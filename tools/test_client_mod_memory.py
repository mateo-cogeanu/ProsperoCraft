#!/usr/bin/env python3
"""Extract actual bootstrap VM options and exercise ZGC demand growth on a host."""
import subprocess, tempfile
from pathlib import Path
from host_toolchain import ROOT, java_home, executable

source=(ROOT/'client/startup/bootstrap.cpp').read_text()
a=source.index('  JavaVMOption options[]={')
b=source.index('\n  };',a)+len('\n  };')
array=source[a:b]
prefix='''#include <iostream>
struct JavaVMOption {char* optionString;void* extraInfo;};
void vm_print(){} void vm_exit(){} void vm_abort(){}
#define PROSPERO_STORAGE_OPTION(a,b) b
#define PROSPERO_STARTUP_OBSERVER "false"
#define PROSPERO_ZIP_OPEN_BUDGET "8"
#define CLIENT_CLASSPATH_OPTION "-Dfixture.classpath=true"
int main(){
'''
java='''import java.lang.management.*;import com.sun.management.HotSpotDiagnosticMXBean;
public class MemoryCheck {
 public static void main(String[] a){long expected=Long.parseLong(a[0])*1048576,soft=Long.parseLong(a[1])*1048576;
  if(Runtime.getRuntime().maxMemory()!=expected)throw new AssertionError("hard limit");
  var bean=ManagementFactory.getPlatformMXBean(HotSpotDiagnosticMXBean.class);
  if(Long.parseLong(bean.getVMOption("SoftMaxHeapSize").getValue())!=soft)throw new AssertionError("soft target");
  if(a.length>2){byte[][] retained=new byte[6144][];for(int i=0;i<retained.length;i++){retained[i]=new byte[8192];retained[i][0]=(byte)i;}
   for(int i=0;i<retained.length;i++)if(retained[i][0]!=(byte)i)throw new AssertionError("data lost");
   if(Runtime.getRuntime().totalMemory()<=soft)throw new AssertionError("did not grow beyond soft target");
  }else if(Runtime.getRuntime().totalMemory()>256L*1048576)throw new AssertionError("heap precommitted unnecessarily");
  System.out.println("PASS hard ceiling, soft target, lazy commitment and retained allocation integrity");
 }
}'''
with tempfile.TemporaryDirectory(prefix='mod-memory-') as tmp:
    w=Path(tmp);(w/'options.cpp').write_text(prefix+array+'\nfor(auto option:options)std::cout<<option.optionString<<"\\n";\n}\n')
    options={}
    for mode in ('normal', 'large', 'pressure'):
        binary=w/mode
        flags=['-DPROSPERO_ZGC=1','-DPROSPERO_TIERED_PARALLEL=1','-DPROSPERO_CHUNK_WORKERS_5=1']
        if mode != 'normal':flags.append('-DPROSPERO_LARGE_MOD_HEAP=1')
        if mode == 'pressure':flags.append('-DPROSPERO_MOD_MEMORY_PRESSURE=1')
        subprocess.run([executable('clang++'),'-std=c++17',*flags,str(w/'options.cpp'),'-o',str(binary)],check=True)
        options[mode]=subprocess.check_output([str(binary)],text=True).splitlines()
    assert '-Xmx1536m' in options['normal'] and not any(o.startswith('-XX:SoftMaxHeapSize=') for o in options['normal'])
    assert '-Xmx3072m' in options['large'] and '-XX:SoftMaxHeapSize=1536m' in options['large'] and '-Xmx1536m' not in options['large']
    assert '-Xmx3072m' in options['pressure'] and '-XX:SoftMaxHeapSize=2304m' in options['pressure']
    (w/'MemoryCheck.java').write_text(java);jdk=java_home()
    subprocess.run([str(jdk/'bin/javac'),str(w/'MemoryCheck.java')],check=True)
    memory=[o for o in options['pressure'] if o.startswith(('-Xms','-Xmx','-XX:SoftMaxHeapSize=')) or o=='-XX:+UseZGC']
    subprocess.run([str(jdk/'bin/java'),*memory,'-cp',str(w),'MemoryCheck','3072','2304'],check=True,timeout=30)
    subprocess.run([str(jdk/'bin/java'),'-XX:+UseZGC','-Xms16m','-Xmx96m','-XX:SoftMaxHeapSize=32m','-cp',str(w),'MemoryCheck','96','32','allocate'],check=True,timeout=30)
print('PASS actual bootstrap policies and genuine ZGC soft-target growth; host fixture, PS5 memory acceptance pending')
