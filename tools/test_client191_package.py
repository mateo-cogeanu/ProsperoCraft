#!/usr/bin/env python3
"""Independent exact191 package/JVM/resident/constructor audit; not console proof."""
import argparse,hashlib,json,subprocess,zipfile,io,struct
from pathlib import Path
from host_toolchain import ROOT

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--llvm-home',type=Path,required=True);p.add_argument('--package-dir',type=Path,default=ROOT/'dist/candidates/zink-jvm-191');p.add_argument('--baseline-package',type=Path,required=True)
 a=p.parse_args();folder=a.package_dir.resolve();r=json.loads((folder/'build-audit.json').read_text());archive=folder/'PPSA99874.zip'
 previous=json.loads((ROOT/'docs/validation/client187-zink-launcher-2026-11-01.json').read_text())['build']
 for name in ('client/startup/bootstrap.cpp','client/startup/ClientStartup25.java','client/startup/session_restart.hpp','client/launcher/java/ProsperoSession.java'):
  assert sha(ROOT/name)==previous['source_sha256'][name], 'Quit behavior must remain unchanged: '+name
 assert r['app_version']=='01.000.191' and r['source_tree']=='clean' and r['console']=='NOT TESTED'
 assert sha(archive)==r['package_sha256'] and sha(a.baseline_package)==r['baseline179_sha256']
 for name,digest in r['source_sha256'].items():assert sha(ROOT/name)==digest,name
 symbols=folder/'zink-jvm191-symbols.elf';assert sha(symbols)==r['symbols_elf_sha256']
 option='-Djava.class.path='+':'.join(r['classpath']['paths'])
 assert option.encode()+b'\0' in symbols.read_bytes(),'Effective classpath is not embedded in exactELF'
 nm=a.llvm_home/'bin/llvm-nm';text=subprocess.check_output([str(nm),'--defined-only',str(symbols)],text=True);counts={};values={}
 for line in text.splitlines():
  row=line.split()
  if len(row)==3:counts[row[-1]]=counts.get(row[-1],0)+1;values[row[-1]]=int(row[0],16)
 for name in r['one_copy_symbols']:assert counts[name]==1,name
 elf=symbols.read_bytes()
 assert b'ZINK_DEBUG' in elf and b'flushsync' in elf and b'PS5_ZINK flushsync setup failed' in elf
 wrapper=(ROOT/'client/zink_fabric_sync/bootstrap.cpp').read_text()
 assert wrapper.index('enable_flushsync()')<wrapper.index('return prospero_zink_main(argc,argv)')
 assert b'PS5_ZINK guard_init result=' in elf
 for label in (b'screen create enter',b'state tracker context create enter',b'drawable validate enter',b'GLFW GL attribute refresh enter'):
  assert label in elf,label
 start,end=values['__client_gpu_init_start'],values['__client_gpu_init_end']
 phoff=struct.unpack_from('<Q',elf,32)[0];entsize,num=struct.unpack_from('<HH',elf,54)
 staged=None
 for i in range(num):
  kind,flags,offset,address,physical,filesize,memsize,alignment=struct.unpack_from('<IIQQQQQQ',elf,phoff+i*entsize)
  if kind==1 and address<=start and end<=address+filesize:staged=elf[offset+start-address:offset+end-address]
 assert staged is not None and len(staged)%8==0
 # PIE constructor slots are populated by real R_X86_64_RELATIVE relocations.
 initializers=list(struct.unpack('<'+'Q'*(len(staged)//8),staged))
 shoff=struct.unpack_from('<Q',elf,40)[0];shsize,shnum=struct.unpack_from('<HH',elf,58)
 for i in range(shnum):
  section=struct.unpack_from('<IIQQQQIIQQ',elf,shoff+i*shsize)
  if section[1]!=4:continue
  for offset in range(section[4],section[4]+section[5],section[9]):
   target,info,addend=struct.unpack_from('<QQq',elf,offset)
   if start<=target<end:
    assert info==8 and (target-start)%8==0,'Unexpected constructor relocation'
    initializers[(target-start)//8]=addend
 assert values['frontend_guard_init'] in initializers,'Frontend guard initializer missing from actual staged ELF constructor array'
 assert values['__init_array_start']==values['__init_array_end']
 for start,end in [('__jvm_init_array_start','__jvm_init_array_end'),('__client_gpu_init_start','__client_gpu_init_end'),('__client_ui_init_start','__client_ui_init_end')]:assert values[end]>values[start]
 assert counts['ps5zink_get_proc_address']==1 and counts['ps5_ps5zink_JNI_OnLoad']==1
 assert counts['OSMesaCreateContextAttribs']==1 and any(name.startswith('clientgl_')for name in counts)
 with zipfile.ZipFile(archive)as z,zipfile.ZipFile(a.baseline_package)as old:
  names=z.namelist();assert all(name.startswith('PPSA99874/')and '..'not in Path(name).parts for name in names)
  param=json.loads(z.read('PPSA99874/sce_sys/param.json'));assert param['contentVersion']=='01.000.191'and param['titleId']=='PPSA99874'
  prefix='PPSA99874/assets/java25/'
  embedded=json.loads(z.read(prefix+'zink-handoff-audit.json'))
  for key,value in embedded.items():assert r[key]==value,key
  registry=json.loads(z.read(prefix+'resident-libraries-audit.json'))
  assert registry==r['registry']
  groups={entry['name']for entry in registry['external_resident_libraries']}
  assert {'ps5zink','ps5clientgpu','ps5glfw','lwjgl_opengl','ps5clientgl','ps5openal'}<=groups
  assert registry['library_aliases']['SDL3']=='ps5sdl'
  with zipfile.ZipFile(io.BytesIO(z.read(prefix+'client-probe.jar')))as jar:
   assert jar.read('ClientStartup25.class')==z.read(prefix+'classes/ClientStartup25.class')
   assert b'Original selected Minecraft Main entry' in jar.read('ClientStartup25.class')
   assert b'STAGE2B PASS' not in jar.read('ClientStartup25.class')
   assert jar.read('prosperocraft-channel.txt').strip()==b'temp_gametest'
   assert jar.read('prosperocraft-zink.txt')==b'all-loaders-26.1-zink-v2\n'
   assert b'all-loaders-26.1-zink-v2' in jar.read('ProsperoGraphics.class')
   assert b'DEV TEST - PLAY' in jar.read('ProsperoLauncher.class')
   assert b'ZINK' in jar.read('ProsperoInstall.class')
   assert b'libps5clientgpu.so' in jar.read('ClientStartup25.class')
   assert b'ps5.opengl.provider' in jar.read('ClientStartup25.class')
   assert jar.read('prosperocraft-build.properties')==b'app_version=01.000.191\ntitle_id=PPSA99874\n'
   assert not any(name.startswith('ZinkHandoffHost')for name in jar.namelist())
  with zipfile.ZipFile(io.BytesIO(z.read(prefix+'ports/lwjgl-3.4.3-ps5-modules.jar')))as modules:
   assert b'libps5zink.so' in modules.read('org/lwjgl/opengl/GL.class')
  assert json.loads(z.read(prefix+'zink-classpath-audit.json'))==r['classpath']
  for name,digest in r['classpath']['jars_sha256'].items():assert hashlib.sha256(z.read(prefix+name)).hexdigest()==digest,name
  assert r['classpath']['required_classes']['org.lwjgl.glfw.GLFW']=='ports/lwjgl-glfw-3.4.1-ps5-callback343.jar'
  assert 'PPSA99874/licenses/Mesa-Zink-MIT.txt' in names and 'PPSA99874/licenses/ZINK-SOURCES.txt' in names
  assert hashlib.sha256(z.read(prefix+'classes/ClientStartup25.class')).hexdigest()==r['fixture_class_sha256']
  assert 'PPSA99874/assets/java25/lib/modules'in names
  assert hashlib.sha256(z.read('PPSA99874/eboot.bin')).hexdigest()==r['eboot_sha256']
  # All original parent dependency JARs remain byte-identical to accepted179;
  # the only changed JARs are our diagnostic and the scoped module overlay.
  allowed={prefix+'client-probe.jar',prefix+'ports/lwjgl-3.4.3-ps5-modules.jar'}
  assert {name for name in names if name.endswith('.jar')}=={name for name in old.namelist()if name.endswith('.jar')}
  for name in names:
   assert '/objects/'not in name
   if name.endswith('.jar')and name not in allowed:assert z.read(name)==old.read(name),name
  assert z.read('PPSA99874/sce_module/libc.prx')==old.read('PPSA99874/sce_module/libc.prx')
 converter=a.runtime_workspace/'build/native/host/ps5-native-tool'
 for name in ('eboot.bin','sce_module/libc.prx'):subprocess.run([str(converter),'self','--inspect','--file',str(ROOT/'build/zink-jvm191/PPSA99874'/name)],check=True,stdout=subprocess.DEVNULL)
 assert 'PROSPERO_ZINK_HANDOFF_TEST' not in (ROOT/'client/zink_fabric_sync/bootstrap.cpp').read_text()
 print('PASS191normalLauncherOriginalMain/buildGate/fullAccountChannel/exactZIP/identity/classes/JAR/onecopyRADV+GL/stagedconstructors/residentgroups/029preservation/signatures; no new original game JAR/assets; console pending')
if __name__=='__main__':main()
