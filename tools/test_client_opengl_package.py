#!/usr/bin/env python3
"""Verify029 real Mesa/OpenGL acceptance package and preserved frozen game/runtime artifacts."""
from pathlib import Path
import argparse,subprocess,json,zipfile,hashlib,io
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin');p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args()
w=ROOT/'build/client-opengl_bootstrap-probe';package=ROOT/'dist/client-opengl_bootstrap/PPSA99874.zip';elf=w/'bootstrap-01.000.029-symbols.elf';sha=lambda b:hashlib.sha256(b).hexdigest()
nm=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(elf)],text=True);symbols={r.split()[-1]:int(r.split()[0],16)for r in nm.splitlines()if len(r.split())==3}
assert symbols['__init_array_start']==symbols['__init_array_end']
for name,count in [('jvm',359),('client_gpu',4),('client_shaderc',5)]:assert (symbols['__'+name+'_init_array_end']-symbols['__'+name+'_init_array_start'])//8==count if name=='jvm'else (symbols['__'+name+'_init_end']-symbols['__'+name+'_init_start'])//8==count
al_ctors=(symbols['__client_openal_init_end']-symbols['__client_openal_init_start'])//8;assert al_ctors>0
for name in ['OSMesaGetProcAddress','OSMesaCreateContextAttribs','OSMesaMakeCurrent','OSMesaDestroyContext','Java_ClientOpenGL25_create','Java_ClientOpenGL25_destroy','Java_org_lwjgl_opengl_GL11C_glClear','ps5_builtin_load_ps5clientgl','ps5_builtin_load_lwjgl_opengl','ffi_call','ffi_call_plan_alloc','ffi_call_plan_invoke','ffi_call_plan_free','ffi_prep_closure_loc','ps5ffi_prep_closure_loc_impl','ffi_closure_alloc','ffi_closure_free','Java_org_lwjgl_system_libffi_LibFFI_FFI_1TYPE_1DOUBLE','Java_org_lwjgl_system_Upcalls_getCallbackHandler','Java_ClientNativeBootstrap25_invokeCallback','alcOpenDevice','alcLoopbackOpenDeviceSOFT','alcRenderSamplesSOFT','alBufferData','alSourcePlay','ps5_builtin_load_ps5openal','ps5_builtin_load_ps5nativeprobe']:assert symbols.get(name),name
with zipfile.ZipFile(package)as z,zipfile.ZipFile(ROOT/'dist/milestones/Client_Continuous_Direct_Scene-01.000.023/PPSA99874-full-local.zip')as old:
 assert z.testzip()is None;pre='PPSA99874/';param=json.loads(z.read(pre+'sce_sys/param.json'));assert param['contentVersion']=='01.000.029'
 for key in ['titleId','contentId','conceptId']:assert param[key]==json.loads(old.read(pre+'sce_sys/param.json'))[key]
 for row in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts']:assert sha(z.read(pre+'assets/java25/client/jars/'+row['file']))==row['sha256'],row['file']
 for name in old.namelist():
  if name.endswith('/lib/modules')or name.endswith('.so'):assert z.read(name)==old.read(name),name
 assert b'-Xmx128m'in z.read(pre+'eboot.bin')and b'Client029 ALL5 PASS'in z.read(pre+'eboot.bin')
 assert sha(z.read(pre+'assets/java25/opengl-licenses/mesa-24.3.4-source.tar.xz'))==json.loads((ROOT/'client/ports/opengl/mesa-sources.json').read_text())['archive']['sha256']
 fixture=z.read(pre+'assets/java25/classes/ClientOpenGL25.class');assert b'OSMesa'in fixture and b'glReadPixels'in fixture and b'softpipe'in fixture and b'net.minecraft.client.main.Main'not in fixture
 assert not any('DispatchHost25'in n or n.endswith(('.pcm','.at9'))for n in z.namelist())
 assert b'OpenGL029 diagnostic'in fixture and b'getCause'in fixture and b'getStackTrace'in fixture
 module=z.read(pre+'assets/java25/ports/lwjgl-3.4.3-ps5-modules.jar');assert sha(module)==json.loads(z.read(pre+'assets/java25/module-platform-audit.json'))['output_sha256']
 with zipfile.ZipFile(io.BytesIO(module))as overlay:
  assert 'org/lwjgl/opengl/GL.class'in overlay.namelist()
  assert not any(n.startswith('net/minecraft/')for n in overlay.namelist())
 assert sha((ROOT/'dist/failures/Client_OpenGL_Provider-01.000.028/PPSA99874-full-local.zip').read_bytes())=='db19d2731496c82f77b6d88276f201517fca2d786e251d94520718986c5f7596'
 groups=json.loads(z.read(pre+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'];assert [x['name']for x in groups]==['ps5clientgpu','ps5clientbridge','lwjgl','ps5sdl','ps5shaderc','ps5openal','ps5nativeprobe','ps5clientgl','lwjgl_opengl']
 for name in ['opengl-provider-audit.json','opengl-jni-audit.json','opengl-licenses/Mesa-COPYING.txt','ffi-audit.json','openal-audit.json','native-bootstrap-licenses/OpenAL-COPYING.txt','native-bootstrap-licenses/libffi-LICENSE.txt']:assert z.read(pre+'assets/java25/'+name)
for file in ['eboot.bin','sce_module/libc.prx']:
 output=subprocess.check_output([str(a.runtime_workspace/'build/native/host/ps5-native-tool'),'self','--inspect','--file',str(w/'PPSA99874'/file)],text=True);assert 'integrity: valid'in output
assert package.read_bytes()==(a.runtime_workspace/'dist/PPSA99874.zip').read_bytes()
for folder,digest in [('Client_Continuous_Direct_Scene-01.000.023','846cd9adea6f9e6b04f80df461424c26b1fec6aa080ed641c35e7cfb16488ea4'),('Client_Original_Startup-01.000.025','1c61c103fc96ac30a4c7acbdb985888a5cf2dfa848dadf90b74903c052097aee')]:
 root='milestones'if folder.startswith('Client_Continuous')else'failures';assert sha((ROOT/'dist'/root/folder/'PPSA99874-full-local.zip').read_bytes())==digest
bootstrap=(ROOT/'client/opengl_bootstrap/bootstrap.cpp').read_text()+(ROOT/'client/bootstrap/acceptance_impl.hpp').read_text();assert 'test_count=5'in bootstrap and 'DestroyJavaVM'in bootstrap and '192.168.'not in bootstrap
assert 'clientgl_optional_context_tls_init'not in symbols
assert not any(n.startswith('_glapi_')for n in symbols)
assert symbols.get('clientgl__glapi_get_proc_address')
assert (w/'classes/ClientOpenGL25.class').read_bytes()==(ROOT/'build/opengl-bootstrap-host-029/ClientOpenGL25.class').read_bytes()
assert sha((ROOT/'dist/milestones/Client_Callbacks_OpenAL-01.000.026/PPSA99874-full-local.zip').read_bytes())=='e158f9fd76ce91f16091b6e9ee2c54a4cbaf11863f08bf77853204b6ef984d82'
gl_ctors=(symbols['__client_gl_init_end']-symbols['__client_gl_init_start'])//8;assert gl_ctors>0
print('PASS029 CRC/signatures/identity,54 original JARs/exact023 runtime image/native libraries,real OSMesa/OpenGL JNI plus preserved native providers,359+4+5+'+str(al_ctors)+'+GL'+str(gl_ctors)+' staged constructors/no auto ctors,9resident groups,dependency overlay,128MiB/five-row fixture/no game or speaker success claim,preserved023/failed025 packages. PS5 pending.SHA256',sha(package.read_bytes()))
