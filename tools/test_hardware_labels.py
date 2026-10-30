#!/usr/bin/env python3
"""Exercise actual native display labels and intact supported Minecraft CPU entries."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile,zipfile
from build_oshi_platform import build as build6
from build_oshi7_platform import build as build7
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--java-home',type=Path,required=True);a=p.parse_args()
runtime=a.runtime_workspace.resolve();jdk=a.java_home
ports=[build6(jdk,True),build7(jdk,True)]
cpp=r'''
#include "hardware_labels.hpp"
#include "native_cpu.hpp"
#include <cassert>
#include <cstdio>
#include <cstring>
static const char* model="CFI-7019";
static int query(char* out){std::strcpy(out,model);return 0;}
int main(){
 for(const char* text:{"CFI-2015B","CFI-7019","unrecognized"}){
  model=text;auto id=ps5::console::read(query);const char* cpu=prospero_hardware::cpu(id.model);const char* gpu=prospero_hardware::gpu(id.model);
  assert(std::strlen(cpu)<96&&std::strlen(gpu)<256);
  for(const char* s:{cpu,gpu})for(;*s;s++)assert(*s>=32&&*s<=126);
  std::puts(cpu);std::puts(gpu);
 }
 assert(!std::strcmp(prospero_hardware::gpu(ps5::console::Model::unknown),prospero_hardware::gpu(ps5::console::read(nullptr).model)));
 auto before=prospero_cpu::read(prospero_cpu::cpuid,7);(void)prospero_hardware::cpu(ps5::console::Model::pro);auto after=prospero_cpu::read(prospero_cpu::cpuid,7);
 assert(before.logical==after.logical&&before.logical==7&&before.valid==after.valid);
}
'''
java=r'''
import oshi.hardware.HardwareAbstractionLayer;
public class HardwareDebugCheck {
 public static void main(String[] args)throws Exception {
  int before=Runtime.getRuntime().availableProcessors();
  System.setProperty("oshi.ps5","true");System.setProperty("ps5.cpu.brand",args[0]);System.setProperty("ps5.cpu.vendor","AuthenticAMD");System.setProperty("ps5.cpu.signature","00870F10");System.setProperty("ps5.cpu.logical",args[1]);
  Object info;try{info=Class.forName("oshi.SystemInfo").getConstructor().newInstance();}catch(ClassNotFoundException v7){info=Class.forName("oshi.spi.SystemInfoFactory").getMethod("create").invoke(null);}
  var cpu=((HardwareAbstractionLayer)info.getClass().getMethod("getHardware").invoke(info)).getProcessor();
  if(cpu.getLogicalProcessorCount()!=Integer.parseInt(args[1]))throw new AssertionError("changed logical count");
  try{cpu.getPhysicalProcessorCount();throw new AssertionError("fabricated physical topology");}catch(UnsupportedOperationException expected){}
  if(args[2].equals("missing"))System.clearProperty("ps5.cpu.signature");
  if(args[2].equals("malformed"))System.setProperty("ps5.cpu.logical","invalid");
  if(args[2].equals("brand"))System.setProperty("ps5.cpu.brand","bad\nbrand");
  boolean legacy=args[3].equals("26.2-client.jar");
  Class<?> entry=Class.forName(legacy?"com.mojang.blaze3d.platform.GLX":"net.minecraft.client.gui.components.debug.DebugEntrySystemSpecs");
  String actual=(String)entry.getMethod(legacy?"_getCpuInfo":"getCpuInfo").invoke(null);
  String expected=args[2].equals("valid")?args[1]+"x "+args[0]:"<unknown>";
  if(!actual.equals(expected))throw new AssertionError(actual+" != "+expected);
  if(!entry.getProtectionDomain().getCodeSource().getLocation().toString().endsWith(args[3]))throw new AssertionError("replaced game class");
  if(before!=Runtime.getRuntime().availableProcessors())throw new AssertionError("changed JVM processor count");
  System.out.println("PASS "+args[3]+": "+actual);
 }
}'''
with tempfile.TemporaryDirectory(prefix='hardware-display-')as temp:
 w=Path(temp);(w/'check.cpp').write_text('#include <initializer_list>\n'+cpp)
 subprocess.run(['clang++','-arch','x86_64','-std=c++20','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(runtime/'java25/platform'),'-I'+str(ROOT/'client/ports/oshi'),str(w/'check.cpp'),'-o',str(w/'check')],check=True)
 # Compile the exact added RADV statements; compare every other byte including ID/capability/driver sentinels.
 patch=(ROOT/'client/ports/mesa/0010-ps5-device-display-name.patch').read_text()
 added='\n'.join(line[1:]for line in patch.splitlines()if line.startswith('+')and not line.startswith('+++'))
 gpu_test='#include <cstdio>\n#include <cstring>\n#include <cassert>\nstruct Props {unsigned ids[8];char deviceName[256];unsigned char capabilities[1024];char driverInfo[256];};\nstruct Instance {struct {struct {char force_vk_devicename[64];} debug;} drirc;}; Instance storage{};Instance* instance=&storage;\nconst char* answer="GPU fixture";\nconst char* prospero_gpu_display_name(void){return answer;}\nvoid update(Props* p){(void)p;\n'+added+'\n}\nint main(){Props p;std::memset(&p,0xa5,sizeof(p));std::strcpy(p.deviceName,"original");Props expected=p;\n#ifdef RADV_PS5\nstd::snprintf(expected.deviceName,sizeof(expected.deviceName),"%s",answer);\n#endif\nupdate(&p);assert(!std::memcmp(&p,&expected,sizeof(p)));std::strcpy(instance->drirc.debug.force_vk_devicename,"explicit override");expected=p;update(&p);assert(!std::memcmp(&p,&expected,sizeof(p)));}\n'
 (w/'gpu.cpp').write_text(gpu_test)
 for target in [True,False]:
  subprocess.run(['clang++','-std=c++20','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*(['-DRADV_PS5']if target else []),str(w/'gpu.cpp'),'-o',str(w/'gpu')],check=True)
  subprocess.run([str(w/'gpu')],check=True)
 labels=subprocess.check_output([str(w/'check')],text=True).splitlines();assert len(labels)==6
 assert labels==['AMD Zen 2, 8C16T (PS5)','AMD RDNA 2, 36 CUs (PS5)','AMD Zen 2, 8C16T (PS5 Pro)','AMD RDNA 2.x, 60 CUs (PS5 Pro)','AMD CPU (PS5; model unknown)','AMD RDNA (PS5; model unknown)']
 (w/'HardwareDebugCheck.java').write_text(java)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',str(ports[0])+':'+str(ROOT/'.tools/client/oshi-core-6.9.0.jar'),'-d',str(w),str(w/'HardwareDebugCheck.java')],check=True)
 research=[ROOT/'build/version122-research',ROOT/'build/snapshot118-research',ROOT/'.tools/client']
 cases=[(ROOT/'.tools/client/client-26.3.jar',None)]
 cases += [(research[0]/'26.2-client.jar',research[0]/'26.2.json')]
 cases += [(research[1]/(f'26.4-snapshot-{n}-client.jar'),research[1]/(f'26.4-snapshot-{n}.json'))for n in range(1,7)]
 for game,metadata in cases:
  before=hashlib.sha256(game.read_bytes()).hexdigest();seven='snapshot-6' in game.name
  with zipfile.ZipFile(game)as jar:
   device_classes=[n[:-6].replace('/','.')for n in jar.namelist()if n.endswith('/VulkanPhysicalDevice.class')]
  assert len(device_classes)==1
  bytecode=subprocess.check_output([str(jdk/'bin/javap'),'-c','-p','-classpath',str(game),*device_classes],text=True)
  assert 'VkPhysicalDeviceProperties.deviceNameString:'in bytecode and 'VkPhysicalDeviceDriverProperties.driverInfoString:'in bytecode

  dependencies=[]
  if metadata:
   meta=json.loads(metadata.read_text());assert hashlib.sha1(game.read_bytes()).hexdigest()==meta['downloads']['client']['sha1']
   for lib in meta['libraries']:
    artifact=lib.get('downloads',{}).get('artifact')
    if not artifact or ':natives-' in lib['name']:continue
    name=Path(artifact['path']).name
    matches=[directory/name for directory in research if (directory/name).exists()]
    if not matches:continue # optional foreign-host libraries are never needed by this narrow debug call
    dep=matches[0];assert hashlib.sha1(dep.read_bytes()).hexdigest()==artifact['sha1'];dependencies.append(dep)
  else:
   lock=json.loads((ROOT/'client/26.3.lock.json').read_text())
   for row in lock['artifacts']:
    dep=ROOT/'.tools/client'/row['file'];assert hashlib.sha256(dep.read_bytes()).hexdigest()==row['sha256'];dependencies.append(dep)
  cp=':'.join(map(str,[w,ports[1 if seven else 0],game,*[d for d in dependencies if d!=game]]))
  for label in labels[::2]:
   for count in ['16','7']:
    subprocess.run([str(jdk/'bin/java'),'-cp',cp,'HardwareDebugCheck',label,count,'valid',game.name],check=True,timeout=25)
  for mode in ['missing','malformed','brand']:
   subprocess.run([str(jdk/'bin/java'),'-cp',cp,'HardwareDebugCheck',labels[0],'16',mode,game.name],check=True,timeout=25)
  assert hashlib.sha256(game.read_bytes()).hexdigest()==before
 print('PASS native labels/bounds/CPUID invariance and intact26.2/26.3/snapshots1-6 OSHI6/7 F3 entries; counts16/7,partial/invalid input,JVM count unchanged. Host fixtures only; no real Pro detection.')
