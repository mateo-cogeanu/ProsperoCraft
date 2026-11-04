#!/usr/bin/env python3
"""Actual pinned OSHI665/original121.10 CPU path; no fabricated system metrics."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from host_toolchain import ROOT, java_home
from prepare_client_121 import validate_metadata
from prepare_client_261 import verified, allowed
from build_lwjgl333 import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('publisher-cache','provider-dir','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--java-home',type=Path);a=p.parse_args();jdk=java_home(a.java_home);cache=a.publisher_cache.resolve();work=a.output_dir.resolve();work.mkdir(parents=True,exist_ok=True)
    overlay=a.provider_dir.resolve()/'oshi-6.6.5-ps5-platform.jar';audit=json.loads((a.provider_dir/'audit.json').read_text());assert sha(overlay)==audit['output_sha256']
    for n,digest in audit['source_sha256'].items():assert sha(ROOT/'client/ports/oshi665'/n)==digest
    row=next(r for r in json.loads((ROOT/'client/1.21.lock.json').read_text())['versions'] if r['id']=='1.21.10');meta=validate_metadata(row,verified(row['metadata'],cache/'1.21.10/metadata.json',offline=True));game=cache/'1.21.10/client.jar';verified(row['client'],game,offline=True);files=[overlay,game]
    for lib in meta['libraries']:
        if ':natives-' in lib['name'] or not allowed(lib) or (lib['name'].startswith('io.netty:netty-transport-native-') and len(lib['name'].split(':'))>3):continue
        pin=lib.get('downloads',{}).get('artifact')
        if pin:
            file=cache/'libraries'/pin['path'];verified(pin,file,offline=True);files.append(file)
    source=work/'Oshi665Check.java';source.write_text(r'''
package prosperocraft.host208;
import oshi.*;
public class Oshi665Check{
 public static void main(String[]a)throws Exception{
  String os=System.getProperty("os.name");
  if(a[0].equals("desktop")){if(SystemInfo.getCurrentPlatform()!=PlatformEnum.getValue(com.sun.jna.Platform.getOSType()))throw new AssertionError();System.out.println("PASS original desktop factory selection");return;}
  System.setProperty("oshi.ps5","true");if(SystemInfo.getCurrentPlatform()!=PlatformEnum.UNKNOWN)throw new AssertionError("platform spoof");
  if(a[0].equals("valid")){
   System.setProperty("ps5.cpu.brand","Fixture CPU");System.setProperty("ps5.cpu.vendor","Fixture");System.setProperty("ps5.cpu.signature","00870F10");System.setProperty("ps5.cpu.logical","8");
   var cpu=new SystemInfo().getHardware().getProcessor();if(cpu.getLogicalProcessorCount()!=8||!cpu.getProcessorIdentifier().getName().equals("Fixture CPU"))throw new AssertionError();
   try{cpu.getMaxFreq();throw new AssertionError("fake frequency");}catch(UnsupportedOperationException expected){}
   try{new SystemInfo().getHardware().getMemory();throw new AssertionError("fake memory");}catch(UnsupportedOperationException expected){}
   try{new SystemInfo().getOperatingSystem();throw new AssertionError("unported native metrics");}catch(UnsupportedOperationException expected){}
  }
  if(!oshi.hardware.CentralProcessor.class.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("oshi-core-6.6.5.jar"))throw new AssertionError("wrong OSHI owner");
  Class<?> original=Class.forName("com.mojang.blaze3d.platform.GLX");if(!original.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("client.jar"))throw new AssertionError("game replaced");
  String text=(String)original.getMethod("_getCpuInfo").invoke(null);if(!text.equals(a[0].equals("valid")?"8x Fixture CPU":"<unknown>"))throw new AssertionError(text);
  if(!os.equals(System.getProperty("os.name")))throw new AssertionError("os.name changed");System.out.println("PASS original12110 GLX CPU entry "+a[0]);
 }
}
''')
    cp=os.pathsep.join(map(str,[work,*files]));subprocess.run([str(jdk/'bin/javac'),'--release','21','-cp',cp,'-d',str(work),str(source)],check=True)
    for mode in ('valid','missing','desktop'):
        log=work/(mode+'-class-init.log');result=subprocess.run([str(jdk/'bin/java'),'-Xlog:class+init=info:file='+str(log),'-cp',cp,'prosperocraft.host208.Oshi665Check',mode],capture_output=True,text=True,timeout=40)
        (work/(mode+'.log')).write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError((result.stdout+result.stderr)[-3000:])
        if mode!='desktop' and "Initializing 'com/sun/jna/Native'" in log.read_text():raise AssertionError('PS5 CPU initialized desktop JNA dispatch')
        print(result.stdout)
    print('PASS original665 dependencies/12110 game intact;CPU-only PS5 route,unsupported metrics,missing identity,desktop control,no JNA init or OS spoof')


if __name__=='__main__':main()
