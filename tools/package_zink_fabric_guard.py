#!/usr/bin/env python3
"""Build isolated189: normal launcher/accounts/instances -> original Vanilla26.1 Main via Zink.

Requires explicit accepted179 package/build inputs and exact183 component. Never
changes the current179 identity or overwrites existing candidate packages.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from host_toolchain import ROOT, java_home


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('runtime-workspace','baseline-package','baseline-relink','baseline-workdir','component','llvm-home','lld'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--java-home',type=Path,required=True)
 p.add_argument('--output-dir',type=Path,default=ROOT/'dist/candidates/zink-jvm-189')
 p.add_argument('--check-only',action='store_true')
 a=p.parse_args();runtime=a.runtime_workspace.resolve();base=a.baseline_workdir.resolve();llvm=a.llvm_home.resolve();jdk=java_home(a.java_home)
 work=ROOT/'build/zink-jvm189';work.mkdir(exist_ok=True);output=a.output_dir.resolve();output.mkdir(parents=True,exist_ok=True)
 archive=output/'PPSA99874.zip'
 if archive.exists():raise FileExistsError('Preserve existing189ZIP; select another --output-dir for any revised build')
 baseline_pin=json.loads((ROOT/'docs/validation/client179-store-publication-2026-10-31.json').read_text())
 if sha(a.baseline_package)!=baseline_pin['package_sha256']:raise ValueError('Wrong accepted179ZIP')
 relink_digest='3d6913b1f9d678faf1fc40bf3cf6771e5fba2c3742e0987aa2c503771a16929c'
 if sha(a.baseline_relink)!=relink_digest:raise ValueError('Wrong accepted179relinkkit')
 with zipfile.ZipFile(a.baseline_relink)as relink_zip:relink_manifest=json.loads(relink_zip.read('manifest.json'))
 baseline_native_hashes={row['sha256']for row in relink_manifest['files']}
 def baseline_native(file):
  if sha(file)not in baseline_native_hashes:raise ValueError('Unverified179link input: '+str(file))
 app=work/'PPSA99874'
 if app.exists():shutil.rmtree(app)
 with zipfile.ZipFile(a.baseline_package)as z:
  for name in z.namelist():
   if not name.startswith('PPSA99874/') or '..'in Path(name).parts:raise ValueError('Unsafe179package entry')
  z.extractall(work)
 java=app/'assets/java25';spec=json.loads((base/'resident-libraries.json').read_text())
 old_audit=json.loads((java/'resident-libraries-audit.json').read_text())
 expected={r['name']:r['objects_sha256']for r in old_audit['external_resident_libraries']}
 for group in spec:
  if [sha(Path(x))for x in group['objects']]!=expected[group['name']]:raise ValueError('Stale179native inputs: '+group['name'])
 env=dict(os.environ,LLVM_CONFIG=str(llvm/'bin/llvm-config'),PATH=str(llvm/'bin')+os.pathsep+os.environ.get('PATH',''))
 def run(*cmd,**kwargs):subprocess.run(list(map(str,cmd)),env=env,check=True,**kwargs)
 import build_client_gpu
 build_client_gpu.LLVM=llvm/'bin';build_client_gpu.LLD=a.lld.absolute()
 gpu,bridge,gpu_audit=build_client_gpu.build(runtime,jdk,True,zink_component=a.component,output_dir=work/'gpu')
 sdk=runtime/'.tools/native-sdk/ps5-payload-sdk';graphics_sdk=ROOT/'.tools/graphics-sdk'
 headers=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base'
 flags=['-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-march=x86-64','-mno-avx','-mno-avx2','-mno-fma','-O2','-fno-stack-protector','-fno-plt','-femulated-tls','-ffunction-sections','-fdata-sections']
 bindings=work/'graphics-bindings.txt';bindings.write_text(''.join(k+' '+v+'\n'for k,v in sorted(gpu_audit['graphics_bindings'].items())))
 import build_glfw_native
 build_glfw_native.LLVM=llvm/'bin'
 raw_glfw=build_glfw_native.build(runtime,offline=True,output_dir=work/'glfw',lld=a.lld.absolute())
 scoped_glfw=work/'resident-glfw.o';run(llvm/'bin/llvm-objcopy','--redefine-syms='+str(bindings),raw_glfw,scoped_glfw)
 resolver=work/'zink-resolver.o'
 run(llvm/'bin/clang',*flags,'-I'+str(headers),'-I'+str(headers/'freebsd'),'-c',ROOT/'client/zink_fabric_guard/resident.c','-o',resolver)
 for group in spec:
  if group['name']=='ps5glfw':group['objects']=[str(scoped_glfw)]
  if group['name']=='ps5clientgpu':group['objects']=[str(bridge),group['objects'][1]]
 spec.append({'name':'ps5zink','objects':[str(resolver)]})
 manifest=work/'resident-libraries.json';manifest.write_text(json.dumps(spec,indent=2)+'\n')
 run('python3',runtime/'tools/java25_builtin_runtime.py','--management','--imageio','--library-alias','SDL3=ps5sdl','--alias-symbol','SDL3:SDL_SetEventFilter=prospero_controlify_SetEventFilter','--alias-symbol','SDL3:SDL_GetEventFilter=prospero_controlify_GetEventFilter','--alias-symbol','SDL3:SDL_PollEvent=prospero_controlify_PollEvent','--library-alias','libzstd-jni_dh-1.5.7-12=ps5zstddh','--library-alias','zstd-jni_dh-1.5.7-12=ps5zstddh','--library-alias','sqlitejdbc=ps5sqlitedh','--external-libraries',manifest)
 buildroot=runtime/'build/java25'
 shutil.copyfile(buildroot/'builtin-resident-audit.json',java/'resident-libraries-audit.json')
 # The module overlay contains the opt-in genuine Zink resolver. Original parent
 # dependency JARs and default029 dispatch remain intact.
 from build_lwjgl_module_platform import build as build_modules
 overlay=build_modules(jdk,offline=True);shutil.copyfile(overlay,java/'ports'/overlay.name)
 shutil.copyfile(overlay.parent/'audit.json',java/'module-platform-audit.json')
 classpath=[java/'ports/lwjgl-3.4.3-ps5-modules.jar',java/'ports/lwjgl-3.4.3-ps5-platform.jar',java/'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar',*sorted((java/'client/jars').glob('*.jar'))]
 classes=work/'classes'
 if classes.exists():shutil.rmtree(classes)
 classes.mkdir()
 classpath.append(java/'client-probe.jar')
 sources=[ROOT/'client/startup/ClientStartup25.java',*sorted((ROOT/'client/launcher/java').glob('*.java'))]
 run(jdk/'bin/javac','--release','25','-cp',os.pathsep.join(map(str,classpath)),'-d',classes,*sources)
 class_names={f.name for f in classes.glob('*.class')}
 jar=java/'client-probe.jar';temporary=jar.with_suffix('.tmp')
 with zipfile.ZipFile(jar)as source,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED)as dest:
  for info in source.infolist():
   if info.filename in class_names or info.filename in ('prosperocraft-build.properties','prosperocraft-zink.txt'):continue
   dest.writestr(info,source.read(info.filename))
  for file in classes.glob('*.class'):dest.writestr(file.name,file.read_bytes())
  dest.writestr('prosperocraft-zink.txt',b'all-loaders-26.1-zink-v2\n')
  dest.writestr('prosperocraft-build.properties',b'app_version=01.000.189\ntitle_id=PPSA99874\n')
 temporary.replace(jar)
 for stale in (java/'classes').glob('ClientStartup25*.class'):stale.unlink()
 for file in classes.glob('*.class'):shutil.copyfile(file,java/'classes'/file.name)
 (java/'classes/prosperocraft-build.properties').write_text('app_version=01.000.189\ntitle_id=PPSA99874\n')
 shutil.copyfile(ROOT/'client/zink_fabric_guard/param.json',app/'sce_sys/param.json')
 # Use the exact full startup classpath but adapt only the generated header path.
 from zink_jvm_classpath import fix_header,verify_app_classpath
 old_header=(base/'client_classpath.hpp').read_text()
 fixed_header=fix_header(old_header)
 (work/'client_classpath.hpp').write_text(fixed_header)
 classpath_audit=verify_app_classpath(app,fixed_header,jdk,work/'classpath-check')
 (java/'zink-classpath-audit.json').write_text(json.dumps(classpath_audit,indent=2)+'\n')
 # Existing toolkit constructors and real native presenter are rebuilt from
 # canonical source with the same scoped graphics bindings.
 import build_launcher_toolkit
 build_launcher_toolkit.LLVM=llvm/'bin'
 toolkit=build_launcher_toolkit.build(work,runtime,gpu_audit['graphics_bindings'])
 main_obj=work/'main.o'
 run(llvm/'bin/clang++','-isystem',sdk/'target/include/c++/v1',*flags,'-DPROSPERO_APP_VERSION="01.000.189"','-std=c++20','-Wall','-Wextra','-Werror','-fno-exceptions','-fno-rtti',
  *['-I'+str(path)for path in (runtime/'native/renderer',runtime/'build/native',runtime/'src',runtime/'native',work,ROOT/'client/native',ROOT/'client/launcher/toolkit/src',ROOT/'.tools/PS5_Mesa/include',runtime/'java25/probe',runtime/'java25/platform')],'-c',ROOT/'client/zink_fabric_guard/bootstrap.cpp','-o',main_obj)
 inputs=[json.loads(line)for line in (base/'combined-link.rsp').read_text().splitlines()]
 regenerated={str(buildroot/name)for name in ('embedded-ps5clientgpu.o','embedded-ps5glfw.o','builtin-libraries.o')}
 for item in inputs:
  if not item.startswith('-') and item not in regenerated:baseline_native(Path(item))
 old_gpu=str(ROOT/'build/client-gpu/graphics-support.o')
 if inputs.count(old_gpu)!=1:raise ValueError('Baseline response lacks exactly one graphics-support replacement')
 inputs=[str(gpu)if item==old_gpu else item for item in inputs]
 for item in json.loads((buildroot/'builtin-link-inputs.json').read_text()):
  if item not in inputs:inputs.insert(inputs.index(str(buildroot/'builtin-libraries.o')),item)
 # Registry output paths are explicit in the baseline response and have just
 # been regenerated from verified native inputs + the new genuine resolver.
 response=work/'combined-link.rsp';response.write_text('\n'.join(json.dumps(x)for x in inputs)+'\n')
 layout=work/'gpu-probe.ld';shutil.copyfile(base/'gpu-probe.ld',layout)
 pie=work/'zink-jvm189-symbols.elf'
 additional=[base/name for name in ('renderer.o','crt.o','cpp_runtime.o','native-exception-trace.o','native-mutex-trace.o')]
 for file in additional:baseline_native(file)
 baseline_native(layout);baseline_native(base/'gpu-abi-local.map')
 stubs=[base/name for name in ('libSceMouse.so','libSceAudioIn.so')]+[ROOT/'build/client-graphics'/name for name in ('libSceAgc.so','libSceAgcDriver.so')]
 run('bash',sdk/'bin/prospero-lld','-T',layout,'--eh-frame-hdr','--version-script',runtime/'.tools/native-app/tooling/native/app-symbols.map','--version-script',base/'gpu-abi-local.map','-e','_start','-o',pie,main_obj,*toolkit,*additional,*stubs,'@'+str(response),'--as-needed',*sorted((sdk/'target/lib').glob('*.so')))
 text=subprocess.check_output([str(llvm/'bin/llvm-nm'),'--defined-only',str(pie)],text=True)
 symbols={};counts={}
 for line in text.splitlines():
  row=line.split()
  if len(row)==3:symbols[row[-1]]=int(row[0],16);counts[row[-1]]=counts.get(row[-1],0)+1
 required=['radv_CreateInstance','radv_CreateDevice','nir_shader_create','clientgpu_ps5zink_create','clientgpu_ps5zink_get_proc_address']
 for name in required:
  if counts.get(name)!=1:raise ValueError('One-copy failure: '+name)
 if symbols['__init_array_start']!=symbols['__init_array_end']:raise ValueError('Unexpected automatic constructors')
 for start,end in [('__jvm_init_array_start','__jvm_init_array_end'),('__client_gpu_init_start','__client_gpu_init_end'),('__client_ui_init_start','__client_ui_init_end')]:
  if symbols[end]<=symbols[start]:raise ValueError('Missing real staged constructors: '+start)
 converter=runtime/'build/native/host/ps5-native-tool';elf=work/'eboot.elf'
 run(converter,'link','--in',pie,'--out',elf,'--stub-dir',sdk/'target/lib',*sum([['--stub',str(x)]for x in stubs],[]),'--module-sdk','0x02000009','--companion-sdk','0x08050001','--file-name','eboot.elf')
 if a.check_only:print('PASS189actual scoped GL/Zink/RADV/JVM/launcher compile/link/registry/constructors/onecopy/converter; noZIP');return
 run(converter,'self','--sign','--in',elf,'--out',app/'eboot.bin','--magic','0x1D3D154F')
 from apply_branding import apply_app
 apply_app(app)
 shutil.copyfile(ROOT/'client/ports/zink/LICENSE.txt',app/'licenses/Mesa-Zink-MIT.txt')
 (app/'licenses/ZINK-SOURCES.txt').write_text('Private Zink frontend/port and normal launcher sources: https://github.com/mateo-cogeanu/ProsperoCraft\nPinned upstream Mesa: https://github.com/mihawk-99/PS5_Mesa@1ba9874f478657ccf6da72ce55f0260164cc0bd0\nOriginal component licenses and graphics upstream notices retained. No original Minecraft JAR or asset objects included.\n')
 # Retain accepted179 OpenAL corresponding source/relink material. No modified
 # OpenAL binary is introduced; the package is a local, unpublished candidate.
 for file in ('frontend.c','frontend.h','README.md','LICENSE.txt','sources.json'):
  dest=java/'zink-source';dest.mkdir(exist_ok=True);shutil.copyfile(ROOT/'client/ports/zink'/file,dest/file)
 for file in (ROOT/'client/ports/zink').glob('*.patch'):shutil.copyfile(file,java/'zink-source'/file.name)
 record={'app_version':'01.000.189','title_id':'PPSA99874','baseline179_sha256':sha(a.baseline_package),'baseline179_relink_sha256':sha(a.baseline_relink),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_tree':'modified'if subprocess.check_output(['git','status','--porcelain'],text=True).strip()else'clean',
  'classpath':classpath_audit,'scope':'Normal full-game launcher/account/instance downloader; opt-in Vanilla/Fabric26.1.x original Main via Zink; known quit failure retained;26.2+ retain Vulkan; physical title/world/lifecycle pending',
  'gpu':gpu_audit,'one_copy_symbols':required,'symbols_elf_sha256':sha(pie),'eboot_sha256':sha(app/'eboot.bin'),
  'source_sha256':{name:sha(ROOT/name)for name in (*[str(f.relative_to(ROOT))for f in sorted((ROOT/'client/launcher/java').glob('*.java'))],'client/startup/bootstrap.cpp','client/zink_fabric_guard/bootstrap.cpp','client/startup/ClientStartup25.java','client/zink_fabric_guard/resident.c','client/zink_fabric_guard/param.json','tools/build_client_gpu.py','tools/build_glfw_native.py','tools/package_zink_fabric_guard.py','client/ports/lwjgl/0004-opengl-ps5-dispatch.patch','client/startup/session_restart.hpp','client/launcher/native_menu.hpp','client/launcher/toolkit_surface.hpp','client/ports/zink/frontend.c','client/ports/zink/frontend.h')},
  'fixture_class_sha256':sha(java/'classes/ClientStartup25.class'),'scoped_glfw_sha256':sha(scoped_glfw),'resolver_sha256':sha(resolver),'runtime_jvm_sha256':sha(buildroot/'embedded-jvm.o'),
  'inherited_link_objects_sha256':{x.name:sha(x)for x in additional},'registry':json.loads((java/'resident-libraries-audit.json').read_text()),'console':'NOT TESTED','release_store':'No action'}
 (java/'zink-handoff-audit.json').write_text(json.dumps(record,indent=2)+'\n')
 for file in (app/'eboot.bin',app/'sce_module/libc.prx'):run(converter,'self','--inspect','--file',file)
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  for file in sorted(app.rglob('*')):
   if file.is_file():
    if '/objects/'in str(file):raise ValueError('No publisher asset objects')
    info=zipfile.ZipInfo(file.relative_to(work).as_posix());info.external_attr=0o100777<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,file.read_bytes())
 record['package_sha256']=sha(archive);(output/'build-audit.json').write_text(json.dumps(record,indent=2)+'\n');(output/'SHA256SUMS').write_text(record['package_sha256']+'  PPSA99874.zip\n');shutil.copyfile(pie,output/pie.name)
 print('LOCAL189',archive,'SHA256',record['package_sha256'])

if __name__=='__main__':main()
