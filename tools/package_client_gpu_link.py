"""Finish consumer GPU/JVM integration using existing runtime embedding outputs."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def finish(runtime,java_home,work,assets,spec,gpu_support,gpu_audit,variant="gpu",version="01.000.004"):
 consumer=ROOT/"client"/variant
 def run(*args,**kw):subprocess.run(list(map(str,args)),check=True,env=dict(os.environ,LLVM_CONFIG=str(LLVM/'llvm-config')),**kw)
 build=runtime/'build/java25';sdk=runtime/'.tools/native-sdk/ps5-payload-sdk';graphics_sdk=ROOT/'.tools/graphics-sdk';native=runtime/'.tools/native-app/tooling/native'
 # Keep the runtime's exact module image/configuration/libraries and all54 pinned
 # original artifacts; replace only consumer fixture bytecode and registry audit.
 java=assets/'java25'
 baseline=runtime/'dist/PPSA99874/assets/java25'
 for path in baseline.iterdir():
  if path.name in {'client','client-probe.jar','ports','dependency-port-audit.json','lwjgl-native-audit.json','resident-libraries-audit.json','classes'}:continue
  dest=java/path.name
  if path.is_dir():shutil.copytree(path,dest,dirs_exist_ok=True)
  else:shutil.copyfile(path,dest)
 shutil.copytree(work/'classes',java/'classes',dirs_exist_ok=True)
 manifest=work/'resident-libraries.json';manifest.write_text(json.dumps(spec['resident_libraries'],indent=2)+'\n')
 run('python3',runtime/'tools/java25_builtin_runtime.py','--management',*(['--imageio','--library-alias','SDL3=ps5sdl','--library-alias','libzstd-jni_dh-1.5.7-12=ps5zstddh','--library-alias','zstd-jni_dh-1.5.7-12=ps5zstddh','--library-alias','sqlitejdbc=ps5sqlitedh'] if variant=='startup' else []),'--external-libraries',manifest)
 shutil.copyfile(build/'builtin-resident-audit.json',java/'resident-libraries-audit.json')
 if variant=='startup':
  shutil.copy2(runtime/'build/java25/boot-image/lib/modules',java/'lib/modules')
  shutil.copy2(runtime/'build/java25/boot-image-audit.json',java/'boot-image-audit.json')
  shutil.copy2(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libnio.so',java/'lib/libnio.so')
  shutil.copy2(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libjava.so',java/'lib/libjava.so')
  shutil.copy2(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libverify.so',java/'lib/libverify.so')
  shutil.copy2(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libnet.so',java/'lib/libnet.so')
  shutil.copy2(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/server/libjvm.so',java/'lib/server/libjvm.so')
  from audit_extended_sync import audit as extended_sync_audit
  (java/'extended-sync-runtime-audit.json').write_text(json.dumps(extended_sync_audit(runtime),indent=2)+'\n')
  from audit_network_scratch import audit as network_scratch_audit
  (java/'network-scratch-runtime-audit.json').write_text(json.dumps(network_scratch_audit(runtime),indent=2)+'\n')
  from audit_core_scratch import audit as core_scratch_audit
  (java/'core-scratch-runtime-audit.json').write_text(json.dumps(core_scratch_audit(runtime),indent=2)+'\n')
  for name in ['awt','lcms']:shutil.copy2(build/'imageio-target'/('lib'+name+'.so'),java/'lib'/('lib'+name+'.so'))
  shutil.copy2(build/'imageio-target/audit.json',java/'imageio-native-audit.json')
  shutil.copytree(runtime/'.tools/java25/openjdk/src/java.desktop/share/legal',java/'legal/java.desktop',dirs_exist_ok=True)
 shutil.copyfile(ROOT/'build/client-ports/lwjgl-native/ps5/audit.json',java/'lwjgl-native-audit.json')
 (java/'gpu-integration-audit.json').write_text(json.dumps(gpu_audit,indent=2)+'\n')
 # Reuse only generated actual objects and wrap flags from runtime embedding.
 from build_runtime_emutls import build as build_runtime_emutls
 (java/'emutls-runtime-audit.json').write_text(json.dumps(build_runtime_emutls(runtime),indent=2)+'\n')
 original=[json.loads(line)for line in (build/'jni-link.rsp').read_text().splitlines()]
 old_objects=json.loads((build/'builtin-link-inputs.json').read_text())
 # The regenerated registry adds the real GPU JNI library. Other input lists
 # match the baseline except for this new group and native core object hashes.
 base_objects=[p for p in original if '/embedded-'in p or p.endswith('/builtin-libraries.o')]
 inputs=[p for p in original if p not in base_objects and p!='--defsym=__cxa_thread_atexit_impl=0']
 flags=[p for p in inputs if p.startswith('-')]
 backends=[p for p in inputs if not p.startswith('-')and not p.endswith('.a')]
 archives=[p for p in inputs if p.endswith('.a')]
 inputs=[*flags,'--wrap=close',*(['--wrap=__cxa_throw','--wrap=_ZNSt3__15mutex4lockEv','--wrap=pthread_mutex_lock'] if variant=='startup' else []),str(build/'embedded-jvm.o'),*old_objects,str(gpu_support),*backends,*archives,'--defsym=__cxa_thread_atexit_impl=clientgpu_ps5___cxa_thread_atexit_impl']
 layout=work/'gpu-probe.ld';s=(build/'jni-probe.ld').read_text();needle='        *(.data.rel.ro .data.rel.ro.*)';assert needle in s
 s=s.replace(needle,'''        PROVIDE_HIDDEN(__client_gl_init_start = .);
        KEEP(*(SORT(.data.rel.ro.clientgl.init_array.*)))
        PROVIDE_HIDDEN(__client_gl_init_end = .);
        PROVIDE_HIDDEN(__client_openal_init_start = .);
        KEEP(*(SORT(.data.rel.ro.clientopenal.init_array.*)))
        PROVIDE_HIDDEN(__client_openal_init_end = .);
        PROVIDE_HIDDEN(__client_shaderc_init_start = .);
        KEEP(*(SORT(.data.rel.ro.clientshaderc.init_array.*)))
        PROVIDE_HIDDEN(__client_shaderc_init_end = .);
        PROVIDE_HIDDEN(__client_ui_init_start = .);
        KEEP(*(SORT(.data.rel.ro.clientui.init_array.*)))
        PROVIDE_HIDDEN(__client_ui_init_end = .);
        PROVIDE_HIDDEN(__client_gpu_init_start = .);
        KEEP(*(SORT(.data.rel.ro.clientgpu.init_array.*)))
        KEEP(*(.data.rel.ro.clientgpu.init_array*))
        PROVIDE_HIDDEN(__client_gpu_init_end = .);
'''+needle);layout.write_text(s)
 aliasmap=work/'gpu-abi-local.map';aliasmap.write_text('{ local: __cxa_thread_atexit_impl; };\n')
 response=work/'combined-link.rsp';response.write_text('\n'.join(json.dumps(p)for p in inputs)+'\n')
 objects=[]
 if variant=='startup':
  from build_launcher_toolkit import build as build_toolkit,package_sources
  objects.extend(build_toolkit(work,runtime,gpu_audit['graphics_bindings']))
  package_sources(java)
  shutil.copytree(ROOT/'assets/launcher-icons',java/'launcher-icons',dirs_exist_ok=True)
  shutil.copyfile(work/'launcher-toolkit-audit.json',java/'launcher-toolkit-audit.json')

 if variant=='startup':
  model_pin=json.loads((ROOT/'client/ports/console-model-runtime.json').read_text())
  model_header=runtime/model_pin['path'];assert hashlib.sha256(model_header.read_bytes()).hexdigest()==model_pin['sha256'],'Runtime model helper pin mismatch'
 # Compile application/UI against the original runtime SDK. Only the isolated
 # graphics dependency/bridge uses the fork headers. Both use the same SDK ABI.
 for name,source in [('main',consumer/'bootstrap.cpp'),('renderer',runtime/'native/renderer/demo_renderer.cpp'),('crt',native/'app_crt.cpp'),('cpp_runtime',native/'app_cpp_runtime.cpp')]:
  obj=work/(name+'.o')
  run(LLVM/'clang++','-DPROSPERO_APP_VERSION="'+version+'"','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include/c++/v1','-isystem',sdk/'target/include','-I'+str(runtime/'native/renderer'),'-I'+str(runtime/'build/native'),'-I'+str(runtime/'src'),'-I'+str(runtime/'native'),'-I'+str(work),'-I'+str(ROOT/'client/native'),'-I'+str(ROOT/'client/launcher/toolkit/src'),'-I'+str(ROOT/'.tools/PS5_Mesa/include'),'-I'+str(runtime/'java25/probe'),'-I'+str(runtime/'java25/platform'),'-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-stack-protector','-fno-plt','-femulated-tls','-fno-exceptions','-fno-rtti','-ffunction-sections','-fdata-sections','-c',source,'-o',obj);objects.append(obj)
 if variant=='startup':
  hardware_audit={'runtime':model_pin,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [consumer/'bootstrap.cpp',ROOT/'client/ports/oshi/hardware_labels.hpp',ROOT/'client/ports/mesa/0010-ps5-device-display-name.patch']},'main_object_sha256':hashlib.sha256((work/'main.o').read_bytes()).hexdigest(),'gpu_property_object':gpu_audit['wsi_diagnostics']['hardware_display'],'console':'Standard PS5 and PS5 Pro pending; fixtures only'}
  (java/'hardware-display-audit.json').write_text(json.dumps(hardware_audit,indent=2)+'\n')
 if variant in {'runtime_shader','startup','native_bootstrap','opengl_bootstrap','stb_bootstrap','freetype_bootstrap','vma_bootstrap','spvc_bootstrap'}:
  # Only this consumer title's C++ allocation operators need the existing
  # graphics heap. Pair new/delete (including aligned/nothrow/sized variants)
  # without changing raw libc, JVM os::malloc or global --wrap policies.
  cpp=work/'cpp_runtime.o';raw_cpp=work/'cpp_runtime-libc.o';shutil.copyfile(cpp,raw_cpp)
  bindings={name:gpu_audit['graphics_bindings'][name]for name in ['malloc','free','posix_memalign']}
  mapping=work/'cpp-allocation-bindings.txt';mapping.write_text(''.join(k+' '+v+'\n'for k,v in sorted(bindings.items())))
  run(LLVM/'llvm-objcopy','--redefine-syms='+str(mapping),cpp)
  audit={'scope':'Consumer application C++ new/delete operators only; unchanged SDK source, JVM allocation and raw libc bindings',
         'source_sha256':hashlib.sha256((native/'app_cpp_runtime.cpp').read_bytes()).hexdigest(),
         'bindings':bindings,'raw_object_sha256':hashlib.sha256(raw_cpp.read_bytes()).hexdigest(),
         'scoped_object_sha256':hashlib.sha256(cpp.read_bytes()).hexdigest(),'console':'pending'}
  (java/'cpp-allocation-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 if variant=='startup':
  sync_source=java/'gpu-sync-source';sync_source.mkdir(exist_ok=True)
  for name in ['present_worker.c','condition_reserve.c','mutex_reserve.inc']:
   shutil.copyfile(ROOT/'client/gpu'/name,sync_source/name)
  shutil.copyfile(ROOT/'client/ports/mesa/0008-videoout-reserved-worker.patch',sync_source/'0008-videoout-reserved-worker.patch')
  diagnostic_sources=java/'startup-diagnostic-source';diagnostic_sources.mkdir(exist_ok=True)
  for path in [ROOT/'client/ports/shaderc/fault.c',ROOT/'client/startup/shader_stage_budget.hpp',ROOT/'client/startup/input_present_trace.hpp',ROOT/'client/ports/openal/ps5_audio_mutex.hpp']:
   shutil.copyfile(path,diagnostic_sources/path.name)
  (java/'startup-diagnostics-audit.json').write_text(json.dumps({'fault_source_sha256':hashlib.sha256((ROOT/'client/ports/shaderc/fault.c').read_bytes()).hexdigest(),'stage_budget_source_sha256':hashlib.sha256((ROOT/'client/startup/shader_stage_budget.hpp').read_bytes()).hexdigest(),'input_present_source_sha256':hashlib.sha256((ROOT/'client/startup/input_present_trace.hpp').read_bytes()).hexdigest(),'audio_mutex_source_sha256':hashlib.sha256((ROOT/'client/ports/openal/ps5_audio_mutex.hpp').read_bytes()).hexdigest(),'bootstrap_source_sha256':hashlib.sha256((ROOT/'client/startup/bootstrap.cpp').read_bytes()).hexdigest(),'main_object_sha256':hashlib.sha256((work/'main.o').read_bytes()).hexdigest(),'policy':'Diagnostic mode:explicit existing1Hz stack/resource observer;256detailed shader stages,failures/unrelated stages retained;atomic fault guard and7signals with legacy4signal API;142cause unproven'},indent=2)+'\n')
  exception_obj=work/'native-exception-trace.o'
  run(LLVM/'clang++','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include/c++/v1','-isystem',sdk/'target/include','-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-exceptions','-fno-rtti','-fno-stack-protector','-c',ROOT/'client/gpu/exception_trace.cpp','-o',exception_obj)
  objects.append(exception_obj)
  mutex_obj=work/'native-mutex-trace.o'
  run(LLVM/'clang++','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include/c++/v1','-isystem',sdk/'target/include','-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-exceptions','-fno-rtti','-fno-stack-protector','-c',ROOT/'client/gpu/mutex_trace.cpp','-o',mutex_obj)
  objects.append(mutex_obj)
  (java/'native-mutex-trace-audit.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'client/gpu/mutex_trace.cpp').read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(mutex_obj.read_bytes()).hexdigest(),'policy':'Diagnostic only;enabled at shaderc entry,256calls max;original lock unchanged,errno preserved;unreturned enter identifies throwing caller'},indent=2)+'\n')

  (java/'native-exception-trace-audit.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/'client/gpu/exception_trace.cpp').read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(exception_obj.read_bytes()).hexdigest(),'policy':'Diagnostic only;128records max,exactSDKsystem_error code,original__cxa_throw forwarded,errno preserved;existingwhatmessage/no demangling or message construction','console':'Pending original exception identification'},indent=2)+'\n')
 stubs=[]
 for name in ['libSceAgc','libSceAgcDriver']:
  # Real native003 import declaration files, never executable implementations.
  stubs.append(ROOT/'build/client-graphics'/(name+'.so'))
 if variant=='startup':
  # System-library import declarations, never executable fallback drivers.
  mouse=work/'libSceMouse.so'
  run(LLVM/'clang','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-fPIC','-fno-stack-protector','-c',ROOT/'client/ports/sdl/ps5_mouse_imports.c','-o',work/'mouse-imports.o')
  run('/opt/homebrew/opt/lld/bin/ld.lld','-shared','-soname','libSceMouse.sprx',work/'mouse-imports.o','-o',mouse)
  stubs.append(mouse)
  # Keep after real objects: --as-needed must see their undefined imports.
  inputs += [str(sdk/'target/lib/libSceKeyboard.so'),str(mouse)]
  response.write_text('\n'.join(json.dumps(p)for p in inputs)+'\n')
 pie=work/('bootstrap-'+version+'-symbols.elf')
 run('bash',sdk/'bin/prospero-lld','-T',layout,'--eh-frame-hdr','--version-script',native/'app-symbols.map','--version-script',aliasmap,'-e','_start','-o',pie,*objects,*stubs,'@'+str(response),'--as-needed',*sorted((sdk/'target/lib').glob('*.so')))
 symbols=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(pie)],text=True);table={line.split()[-1]:int(line.split()[0],16)for line in symbols.splitlines()if len(line.split())==3}
 assert table['__init_array_start']==table['__init_array_end'],'Unstaged automatic constructor'
 assert table['__jvm_init_array_end']>table['__jvm_init_array_start']
 assert table['__client_gpu_init_end']>table['__client_gpu_init_start']
 tool=runtime/'build/native/host/ps5-native-tool';elf=work/'eboot.elf'
 run(tool,'link','--in',pie,'--out',elf,'--stub-dir',sdk/'target/lib',*sum([['--stub',str(p)]for p in stubs],[]),'--module-sdk','0x02000009','--companion-sdk','0x08050001','--file-name','eboot.elf')
 app=work/'PPSA99874';shutil.rmtree(app,ignore_errors=True);(app/'sce_sys').mkdir(parents=True);(app/'sce_module').mkdir()
 run(tool,'self','--sign','--in',elf,'--out',app/'eboot.bin','--magic','0x1D3D154F')
 shutil.copyfile(consumer/'param.json',app/'sce_sys/param.json');shutil.copyfile(runtime/'sce_sys/icon0.png',app/'sce_sys/icon0.png');shutil.copyfile(runtime/'build/native/libc.prx',app/'sce_module/libc.prx')
 shutil.copytree(assets,app/'assets');shutil.copytree(runtime/'dist/PPSA99874/licenses',app/'licenses')
 shutil.copytree(ROOT/'build/client-graphics/PPSA99874/licenses',app/'licenses/graphics',dirs_exist_ok=True)
 for path in [app/'eboot.bin',app/'sce_module/libc.prx']:run(tool,'self','--inspect','--file',path)
 from apply_branding import apply_app
 apply_app(app)
 import zipfile
 dest=ROOT/('dist/client-'+variant);dest.mkdir(exist_ok=True);package=dest/'PPSA99874.zip'
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted(app.rglob('*')):
   if p.is_file():
    info=zipfile.ZipInfo(str(p.relative_to(app.parent)));info.external_attr=0o100777<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 shutil.copyfile(package,runtime/'dist/PPSA99874.zip')
 digest=hashlib.sha256(package.read_bytes()).hexdigest();(dest/'SHA256SUMS').write_text(digest+'  PPSA99874.zip\n')
 print('Client',version,'Java/LWJGL GPU candidate SHA256',digest,'console pending')
