#!/usr/bin/env python3
"""Audit actual148GLFW/TinyFD native exports, routing and packaged source."""
from pathlib import Path
import zipfile,json,hashlib,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
elf=ROOT/'build/client-startup-probe/bootstrap-01.000.148-symbols.elf'
exports=set(line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(elf)],text=True).splitlines()if line.split())
functions=subprocess.check_output(['/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home/bin/javap','-classpath',str(ROOT/'build/version122-research/lwjgl-glfw-3.4.1.jar'),'-c','-p','org.lwjgl.glfw.GLFW$Functions'],text=True)
required=[name for name,kind in re.findall(r'// String (glfw\w+)\n\s+\d+: invokestatic[^\n]+// Method org/lwjgl/system/APIUtil\.(apiGetFunctionAddress\w*)',functions)if kind=='apiGetFunctionAddress']
assert len(required)==118 and set(required)<=exports
for name in ['glfwCreateWindowSurface','glfwVulkanSupported','glfwInitVulkanLoader','glfwGetRequiredInstanceExtensions','glfwSetPreeditCallback','glfwSetIMEStatusCallback','glfwSetPreeditCursorRectangle','ps5_builtin_load_ps5glfw','ps5_builtin_load_lwjgl_tinyfd','Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1getGlobalChar']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 assert package.testzip()is None;prefix='PPSA99874/assets/java25/';audit=json.loads(package.read(prefix+'glfw-audit.json'))
 for name,digest in audit['local_source_sha256'].items():assert hashlib.sha256(package.read(prefix+'glfw-source/'+name)).hexdigest()==digest==hashlib.sha256((ROOT/'client/ports/glfw'/name).read_bytes()).hexdigest()
 scratch=json.loads(package.read(prefix+'core-scratch-runtime-audit.json'));runtime=ROOT.parents[2]
 assert scratch['runtime']==json.loads((ROOT/'client/ports/core-scratch-runtime.json').read_text())
 assert hashlib.sha256(package.read(prefix+'lib/libjava.so')).hexdigest()==scratch['libjava_sha256']
 for name,digest in scratch['objects_sha256'].items():assert hashlib.sha256((runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava'/name).read_bytes()).hexdigest()==digest
 assert hashlib.sha256(package.read(prefix+'lib/libverify.so')).hexdigest()==scratch['libverify_sha256']
 assert hashlib.sha256((runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libverify/check_code.o').read_bytes()).hexdigest()==scratch['verifier_object_sha256']
 assert 'JNU_PS5SetVerifierSmallReserveEnabled' in exports
 assert 'JNU_PS5SetDirectScratchEnabled' in exports
 assert package.read(prefix+'tinyfd-source/ps5_dialogs.c')==(ROOT/'client/ports/tinyfd/ps5_dialogs.c').read_bytes()
 binding=prefix+'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar';binding_audit=json.loads(package.read(prefix+'glfw-binding-audit.json'))
 assert hashlib.sha256(package.read(binding)).hexdigest()==binding_audit['output_sha256']
 assert len(binding_audit['changed_source_units'])==26
 assert package.read(binding)==(ROOT/'build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar').read_bytes()
 assert b'ps5glfw'in package.read(prefix+'classes/ClientStartup25.class') and b'selectedGlfw'in package.read(prefix+'classes/ClientStartup25.class')
sdl=ROOT/'build/sdl3-native/resident-sdl.o'
undefined={line.split()[-1] for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(sdl)],text=True).splitlines() if line.split()}
assert not any(name.startswith('pthread_rwlock_') for name in undefined),undefined
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip') as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/sdl-audit.json'))
 for name in ['SDL_ps5rwlock.c','0002-ps5-rwlock.patch','ps5_startup_boundary.h','SDL_ps5video.c','0003-ps5-native-sync-reserve.patch']:
  assert audit['port_sha256'][name]==hashlib.sha256((ROOT/'client/ports/sdl'/name).read_bytes()).hexdigest()
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip') as package:
 image=package.read('PPSA99874/eboot.bin')
 for marker in [b'BEGIN PREVIOUS VM TRACE TAIL',b'GLFW platform init enter',b'GLFW monitor allocation failed',b'PS5 SDL video driver init enter']:
  assert marker in image,marker
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip') as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/emutls-runtime-audit.json'))
 assert audit['runtime']==json.loads((ROOT/'client/ports/emutls-runtime.json').read_text())
 assert audit['object_sha256']==hashlib.sha256((runtime/'build/java25/emutls-adapter/backend.o').read_bytes()).hexdigest()
 for name,digest in audit['runtime']['source_sha256'].items():assert hashlib.sha256((runtime/name).read_bytes()).hexdigest()==digest
 for name in ['ps5_emutls_enable_direct','ps5_emutls_direct_map','ps5_emutls_direct_unmap']:assert name in exports,name
 names=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(elf)],text=True)
 assert sum(line.endswith('_ZZN17ps5_native_direct5stateEvE5value') for line in names.splitlines())==1,'Native direct ledger must be shared'
for name in ['prospero_sdl_mutex_preinit','prospero_sdl_condition_preinit']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:assert b'PS5 SDL native sync reserve' in package.read('PPSA99874/eboot.bin')
support=ROOT/'build/client-gpu/graphics-support.o'
undefined={line.split()[-1] for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/client-gpu/radv-raw.o')],text=True).splitlines() if line.split()}
assert 'strdup' not in undefined and 'strndup' not in undefined
for name in ['clientgpu_strdup','clientgpu_strndup']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 gpu=json.loads(package.read('PPSA99874/assets/java25/gpu-integration-audit.json'))
 assert gpu['graphics_bindings']['strdup']=='clientgpu_strdup' and gpu['graphics_bindings']['strndup']=='clientgpu_strndup'
 assert gpu['string_allocator_source_sha256']==hashlib.sha256((ROOT/'client/gpu/string_alloc.c').read_bytes()).hexdigest()
glfw_refs={line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/glfw-native/ps5/glfw.o')],text=True).splitlines()if line.split()}
assert not glfw_refs.intersection({'pthread_mutex_init','pthread_mutex_destroy','pthread_mutex_lock','pthread_mutex_unlock'})
assert {'SDL_CreateMutex','SDL_DestroyMutex','SDL_LockMutex','SDL_UnlockMutex'}<=glfw_refs
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/gpu-integration-audit.json'))
 assert audit['condition_reserve_source_sha256']==hashlib.sha256((ROOT/'client/gpu/condition_reserve.c').read_bytes()).hexdigest()
 for name,target in audit['mesa_sync_bindings'].items():
  assert name not in undefined and target in exports,(name,target)
  assert name not in audit['graphics_bindings'],'Condition routing must stay RADV-only'
 assert 'clientgpu_condition_preinit' in exports
 assert b'PS5 RADV native condition reserve' in package.read('PPSA99874/eboot.bin')
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/native-exception-trace-audit.json'))
 assert audit['source_sha256']==hashlib.sha256((ROOT/'client/gpu/exception_trace.cpp').read_bytes()).hexdigest()
 assert audit['object_sha256']==hashlib.sha256((ROOT/'build/client-startup-probe/native-exception-trace.o').read_bytes()).hexdigest()
 assert b'PS5_CPP_THROW caller=' in package.read('PPSA99874/eboot.bin')
 assert '__wrap___cxa_throw' in exports
 response=(ROOT/'build/client-startup-probe/combined-link.rsp').read_text();assert '--wrap=__cxa_throw' in response
symbols={line.split()[-1]:int(line.split()[0],16)for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(elf)],text=True).splitlines()if len(line.split())==3}
address=symbols['_ZNSt3__120__throw_system_errorB8ne180100ENS_10error_codeEPKc']
code=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+160),str(elf)],text=True)
assert '<__wrap___cxa_throw>' in code,'Actual libc++ system_error throw must call recorder'
address=symbols['__wrap___cxa_throw']
code=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+128),str(elf)],text=True)
assert '<__cxa_throw>' in code,'Recorder must forward original ABI'
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/shaderc-audit.json'))
 assert audit['init_mutex_source_sha256']==hashlib.sha256((ROOT/'client/ports/shaderc/ps5_init_mutex.hpp').read_bytes()).hexdigest()
 for name,digest in audit['init_mutex_patch_sha256'].items():assert hashlib.sha256((ROOT/'client/ports/shaderc'/name).read_bytes()).hexdigest()==digest
for unit in ['libshaderc_util/CMakeFiles/shaderc_util.dir/src/compiler.cc.o','third_party/glslang/glslang/CMakeFiles/glslang.dir/MachineIndependent/ShaderLang.cpp.o']:
 refs={line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/shaderc-ps5'/unit)],text=True).splitlines()if line.split()}
 assert {'SDL_CreateMutex','SDL_DestroyMutex','SDL_LockMutex','SDL_UnlockMutex'}<=refs,unit
 assert '_ZNSt3__15mutex4lockEv' not in refs,unit
 names=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm',str(ROOT/'build/shaderc-ps5'/unit)],text=True)
 assert '_ZGVZN12shaderc_util18GlslangInitializer' not in names,'No lazy static mutex guard'
 assert '_ZN18PS5ShaderInitMutexD' not in names,'Initialization locks persist; no destructor registration'
relocations=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-readelf','-r',str(elf)],text=True)
constructors=[]
for line in relocations.splitlines():
 row=line.split()
 if len(row)<4 or row[2]!='R_X86_64_RELATIVE':continue
 address=int(row[0],16)
 if symbols['__client_shaderc_init_start']<=address<symbols['__client_shaderc_init_end']:
  target=int(row[-1],16);constructors.append(next(name for name,value in symbols.items()if value==target))
assert constructors==['_GLOBAL__I_000100','_GLOBAL__sub_I_Scan.cpp','_GLOBAL__sub_I_hlslScanContext.cpp','_GLOBAL__sub_I_doc.cpp'],constructors
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 gpu=json.loads(package.read('PPSA99874/assets/java25/gpu-integration-audit.json'))
 assert len(gpu['mesa_sync_bindings'])==9
 for api in ['pthread_condattr_init','pthread_condattr_setclock','pthread_condattr_destroy']:
  assert api in gpu['mesa_sync_bindings'] and api not in gpu['graphics_bindings']
 assert b'capacities128realtime/128monotonic' in package.read('PPSA99874/eboot.bin')
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/native-mutex-trace-audit.json'))
 assert audit['source_sha256']==hashlib.sha256((ROOT/'client/gpu/mutex_trace.cpp').read_bytes()).hexdigest()
 assert audit['object_sha256']==hashlib.sha256((ROOT/'build/client-startup-probe/native-mutex-trace.o').read_bytes()).hexdigest()
 assert b'PS5_CPP_MUTEX phase=' in package.read('PPSA99874/eboot.bin')
for name in ['ps5_cpp_mutex_trace_enable','__wrap__ZNSt3__15mutex4lockEv']:assert name in exports,name
address=symbols['__wrap__ZNSt3__15mutex4lockEv']
code=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+400),str(elf)],text=True)
assert '<_ZNSt3__15mutex4lockEv>' in code,'Mutex recorder must call actual original lock'
address=symbols['_ZNSt3__111timed_mutex4lockEv']
code=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+300),str(elf)],text=True)
slots=[int(value,16)for value in re.findall(r'# 0x([0-9a-f]+)',code)]
relocations=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-readelf','-r',str(elf)],text=True)
routed='<__wrap_pthread_mutex_lock>' in code
for line in relocations.splitlines():
 row=line.split()
 if len(row)>3 and row[2]=='R_X86_64_RELATIVE' and int(row[0],16)in slots and int(row[-1],16)==symbols['__wrap_pthread_mutex_lock']:routed=True
assert routed,'Actual inlined SDK native mutex GOT calls must route recorder'
assert '__wrap_pthread_mutex_lock' in exports
address=symbols['__wrap_pthread_mutex_lock']
code=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+400),str(elf)],text=True)
assert 'callq' in code,'Native wrapper must forward original native call'
print('PASS actual148 rebuilt runtime127+129 libjava/libverify/object hashes and explicit enablement; all118GLFW exports, callbacks/TinyFD/source/CRC preserved; PS5 SDL allocation-free RWLock source/pin and no pthread_rwlock imports; Fabric validation pending')

# VMA implementation uses supported custom hooks, no SDK lazy mutex state.
vma=ROOT/'build/lwjgl-vma-ps5/lwjgl-vma-raw.o'
refs=set(line.split()[-1]for line in subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(vma)],text=True).splitlines()if line.split())
assert not any('mutex' in n or n.startswith('pthread_') for n in refs),refs
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/vma-audit.json'))
 header=package.read('PPSA99874/assets/java25/vma-source/ps5_mutex.hpp')
 assert header==(ROOT/'client/ports/vma/ps5_mutex.hpp').read_bytes()
 assert audit['locks']['source_sha256']==hashlib.sha256(header).hexdigest()
 assert audit['object_sha256']==hashlib.sha256((vma.parent/'lwjgl-vma.o').read_bytes()).hexdigest()
print('PASS148 actual VMA custom-lock object has no SDK mutex/pthread references;packaged hook source/hash/object audited;PS5 pending')

for name in ['clientgpu_present_worker_preinit','clientgpu_present_worker_start']:assert name in exports,name
with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/gpu-integration-audit.json'))
 assert audit['present_worker_source_sha256']==hashlib.sha256((ROOT/'client/gpu/present_worker.c').read_bytes()).hexdigest()
 assert audit['wsi_diagnostics']['reserved_worker_patch_sha256']==hashlib.sha256((ROOT/'client/ports/mesa/0008-videoout-reserved-worker.patch').read_bytes()).hexdigest()
 assert b'PS5 VideoOut pre-JVM worker reserve' in package.read('PPSA99874/eboot.bin')
boot=(ROOT/'client/startup/bootstrap.cpp').read_text()
assert boot.index('int present_worker_rc=clientgpu_present_worker_preinit()')<boot.index('JNI_CreateJavaVM(&')
patched=(ROOT/'build/wsi-diagnostics/wsi_common_videoout.c').read_text()
assert 'clientgpu_present_worker_start(&out->thread, videoout_flip_thread, NULL)' in patched
assert 'thrd_create(&out->thread' not in patched
print('PASS148 actual WSI flip worker routed to pre-JVM reserved native thread;hashes/startup order/unchanged callback checked;PS5 pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 gpu=json.loads(package.read('PPSA99874/assets/java25/gpu-integration-audit.json'))
 assert gpu['mutex_reserve_source_sha256']==hashlib.sha256((ROOT/'client/gpu/mutex_reserve.inc').read_bytes()).hexdigest()
 assert len(gpu['mesa_mutex_bindings'])==6
 for name,target in gpu['mesa_mutex_bindings'].items():
  assert name not in undefined and target in exports,(name,target)
  assert name not in gpu['graphics_bindings']
print('PASS148 RADV-only six mutex routes;native operations/condition mutex resolution;pre-JVM source and hashes audited')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 for name in ['present_worker.c','condition_reserve.c','mutex_reserve.inc']:
  assert package.read('PPSA99874/assets/java25/gpu-sync-source/'+name)==(ROOT/'client/gpu'/name).read_bytes()
 assert package.read('PPSA99874/assets/java25/gpu-sync-source/0008-videoout-reserved-worker.patch')==(ROOT/'client/ports/mesa/0008-videoout-reserved-worker.patch').read_bytes()

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/network-scratch-runtime-audit.json'))
 assert audit['runtime']==json.loads((ROOT/'client/ports/network-scratch-runtime.json').read_text())
 assert audit['libnet_sha256']==hashlib.sha256(package.read('PPSA99874/assets/java25/lib/libnet.so')).hexdigest()
 for name,digest in audit['objects_sha256'].items():
  obj=ROOT.parents[2]/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libnet'/name
  assert hashlib.sha256(obj.read_bytes()).hexdigest()==digest,name
 assert 'JNU_PS5SetNetworkScratchEnabled' in exports
 assert b'PS5 libnet node scratch enabled' in package.read('PPSA99874/eboot.bin')
code=(ROOT/'client/startup/bootstrap.cpp').read_text();main=code[code.index('int main(int argc,char** argv) {'):]
assert main.index('JNU_PS5SetNetworkScratchEnabled(1)')<main.index('run_test(')
print('PASS148 runtime-owned network scratch pin/rebuilt libnet/object hashes and explicit pre-JVM enablement;PS5 DNS/Fabric pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/extended-sync-runtime-audit.json'))
 assert audit['runtime']==json.loads((ROOT/'client/ports/extended-sync-runtime.json').read_text())
 assert audit['libjvm_sha256']==hashlib.sha256(package.read('PPSA99874/assets/java25/lib/server/libjvm.so')).hexdigest()
 obj=ROOT.parents[2]/'.tools/java25/openjdk/build/ps5-bootstrap/hotspot/variant-server/libjvm/objs/os_posix.o'
 assert audit['os_posix_object_sha256']==hashlib.sha256(obj.read_bytes()).hexdigest()
 assert 'JVM_PS5SetExtendedSyncReserveEnabled' in exports
 assert b'PS5 extended HotSpot sync reserve requested:8192mutex/8192relative/2048absolute' in package.read('PPSA99874/eboot.bin')
assert main.index('JVM_PS5SetExtendedSyncReserveEnabled(1)')<main.index('run_test(')
print('PASS148 runtime-owned extended monitor reserve pin/native object/libjvm hashes and explicit checked pre-JVM policy;actual PS5 prime counts/Fabric pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 shader=json.loads(package.read('PPSA99874/assets/java25/shaderc-audit.json'))
 assert shader['fault_source_sha256']==hashlib.sha256((ROOT/'client/ports/shaderc/fault.c').read_bytes()).hexdigest()
 binary=package.read('PPSA99874/eboot.bin')
 for marker in [b'-Dps5.startupObserver=true',b'SHADER_TRACE detail limit256',b'Native extended signal recorder owned_mask=']:assert marker in binary
 assert 'ps5shaderc_fault_extended_status' in exports
refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/shaderc-ps5/fault.o')],text=True)
assert 'pthread_mutex' not in refs
print('PASS148 diagnostic recorder uses atomic fixed storage,extended signal API,explicit stack/resource sampling and bounded shader stages;PS5 cause remains unproven')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/startup-diagnostics-audit.json'))
 assert audit['stage_budget_source_sha256']==hashlib.sha256((ROOT/'client/startup/shader_stage_budget.hpp').read_bytes()).hexdigest()
 assert audit['main_object_sha256']==hashlib.sha256((ROOT/'build/client-startup-probe/main.o').read_bytes()).hexdigest()
 assert audit['bootstrap_source_sha256']==hashlib.sha256((ROOT/'client/startup/bootstrap.cpp').read_bytes()).hexdigest()
 for name,path in [('fault.c','client/ports/shaderc/fault.c'),('shader_stage_budget.hpp','client/startup/shader_stage_budget.hpp')]:
  assert package.read('PPSA99874/assets/java25/startup-diagnostic-source/'+name)==(ROOT/path).read_bytes()

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/core-scratch-runtime-audit.json'))
 pin=json.loads((ROOT/'client/ports/core-scratch-runtime.json').read_text())
 assert audit['runtime']==pin and 'native_library_scratch' in pin
 obj=ROOT.parents[2]/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava/NativeLibraries.o'
 assert audit['objects_sha256']['NativeLibraries.o']==hashlib.sha256(obj.read_bytes()).hexdigest()
 refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(obj)],text=True)
 assert 'JNU_PS5DirectScratchEnabled' in refs and 'sceKernelAllocateDirectMemory' in refs
 assert b'three8MiB/64slot temporary-buffer budgets including library names' in package.read('PPSA99874/eboot.bin')
print('PASS148 rebuilt runtime NativeLibraries name scratch pin/object/policy/directrefs/libjava verified;PS5 Controlify/compression/world pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/openal-audit.json'))
 boundary=audit['startup_boundaries']
 assert boundary['audio_mutex']['source_sha256']==hashlib.sha256((ROOT/'client/ports/openal/ps5_audio_mutex.hpp').read_bytes()).hexdigest()
 source=(ROOT/'build/openal-startup-boundary-ps5/logging.cpp').read_text()
 assert 'LogCallbackMutex = ps5audio::Mutex{}' in source and 'LogCallbackMutex = std::mutex' not in source
 for name in ['logging.cpp.o','ps5_backend.cpp.o']:
  refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/openal-startup-boundary-ps5'/name)],text=True)
  assert '_ZNSt3__15mutex4lockEv' not in refs and '_ZNSt3__15mutex6unlockEv' not in refs,name
 audit=json.loads(package.read('PPSA99874/assets/java25/startup-diagnostics-audit.json'))
 assert audit['input_present_source_sha256']==hashlib.sha256((ROOT/'client/startup/input_present_trace.hpp').read_bytes()).hexdigest()
 assert audit['audio_mutex_source_sha256']==hashlib.sha256((ROOT/'client/ports/openal/ps5_audio_mutex.hpp').read_bytes()).hexdigest()
 for name in ['client_input_change','client_input_present_trace','client_input_present_note']:assert name in exports
 assert b'INPUT_PRESENT phase=' in package.read('PPSA99874/eboot.bin')
print('PASS148 scoped real OpenAL logging/PS5 state mutex route and bounded input/present checkpoints;PS5 audio and crash cause pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/openal-audit.json'))
 expected=audit['device_state_mutex']
 header=ROOT/'build/openal-ps5/source/alc/device.h'
 assert expected['patched_header_sha256']==hashlib.sha256(header.read_bytes()).hexdigest()
 assert 'ps5audio::Mutex StateLock;' in header.read_text()
 pristine=(ROOT/'.tools/openal-soft-src/alc/device.h').read_text()
 assert header.read_text()==pristine.replace('#include <mutex>','#include <mutex>\n#include "ps5_audio_mutex.hpp"').replace('std::mutex StateLock;','ps5audio::Mutex StateLock;')
 patched=(ROOT/'build/openal-startup-boundary-ps5/alc.cpp.o')
 names=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-n',str(ROOT/'build/client-startup-probe/bootstrap-01.000.148-symbols.elf')],text=True)
 table={l.split()[-1]:int(l.split()[0],16)for l in names.splitlines()if len(l.split())==3}
 start=table['alcGetString'];stop=min(v for v in table.values()if v>start)
 dis=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(stop),str(ROOT/'build/client-startup-probe/bootstrap-01.000.148-symbols.elf')],text=True)
 assert '<__wrap__ZNSt3__15mutex4lockEv>' not in dis,'DeviceStateLock must not route SDK lazy mutex'
 assert expected['mutex_header_sha256']==hashlib.sha256((ROOT/'client/ports/openal/ps5_audio_mutex.hpp').read_bytes()).hexdigest()
print('PASS148 all OpenAL units share privately rebuilt Device layout with allocation-free StateLock;PS5 startup/audio pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/openal-audit.json'))
 hrtf=ROOT/'build/openal-ps5/source/core/hrtf.cpp'
 assert audit['hrtf_mutex']['patched_source_sha256']==hashlib.sha256(hrtf.read_bytes()).hexdigest()
 original=(ROOT/'.tools/openal-soft-src/core/hrtf.cpp').read_text()
 for name in ['LoadedHrtfLock','EnumeratedHrtfLock']:original=original.replace('auto '+name+' = std::mutex{};','auto '+name+' = ps5audio::Mutex{};')
 assert hrtf.read_text()=='#include "ps5_audio_mutex.hpp"\n'+original
 assert hrtf.read_bytes()==(ROOT/'build/openal-host/source/core/hrtf.cpp').read_bytes()
 refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/openal-ps5/CMakeFiles/OpenAL.dir/core/hrtf.cpp.o')],text=True)
 assert '_ZNSt3__15mutex4lockEv' not in refs
print('PASS148 actual HRTF object has noSDKstdmutexlock;exact private source limitedtotwoHRTFlocks;PS5audio pending')

with zipfile.ZipFile(ROOT/'dist/client-startup/PPSA99874.zip')as package:
 audit=json.loads(package.read('PPSA99874/assets/java25/openal-audit.json'))
 original=(ROOT/'.tools/openal-soft-src/core/helpers.cpp').read_text()
 source=ROOT/'build/openal-ps5/source/core/helpers.cpp'
 assert source.read_text()=='#include "ps5_audio_mutex.hpp"\n'+original.replace('auto gSearchLock = std::mutex{};','auto gSearchLock = ps5audio::Mutex{};')
 assert audit['data_search_mutex']['private_source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
 refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(ROOT/'build/openal-startup-boundary-ps5/helpers.cpp.o')],text=True)
 assert '_ZNSt3__15mutex4lockEv' not in refs
print('PASS148 actual SearchDataFiles object has noSDKstdmutexlock;exact private edit/hashes preserve search behavior;PS5 startup/audio pending')
