#!/usr/bin/env python3
"""Verify033 real FreeType font acceptance package and preserved frozen game/runtime artifacts."""
from pathlib import Path
import argparse,subprocess,json,zipfile,hashlib,re
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin');p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args()
w=ROOT/'build/client-freetype_bootstrap-probe';package=ROOT/'dist/client-freetype_bootstrap/PPSA99874.zip';elf=w/'bootstrap-01.000.033-symbols.elf';sha=lambda b:hashlib.sha256(b).hexdigest()
nm=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(elf)],text=True);symbols={r.split()[-1]:int(r.split()[0],16)for r in nm.splitlines()if len(r.split())==3}
assert symbols['__init_array_start']==symbols['__init_array_end']
for name,count in [('jvm',359),('client_gpu',4),('client_shaderc',5)]:assert (symbols['__'+name+'_init_array_end']-symbols['__'+name+'_init_array_start'])//8==count if name=='jvm'else (symbols['__'+name+'_init_end']-symbols['__'+name+'_init_start'])//8==count
al_ctors=(symbols['__client_openal_init_end']-symbols['__client_openal_init_start'])//8;assert al_ctors>0
for name in ['ps5_builtin_load_freetype','FT_Init_FreeType','FT_Load_Char','FT_Done_Face','FT_Done_FreeType','ffi_call','ffi_call_plan_alloc','ffi_call_plan_invoke','ffi_call_plan_free','ffi_prep_closure_loc','ps5ffi_prep_closure_loc_impl','ffi_closure_alloc','ffi_closure_free','Java_org_lwjgl_system_libffi_LibFFI_FFI_1TYPE_1DOUBLE','Java_org_lwjgl_system_Upcalls_getCallbackHandler','Java_ClientNativeBootstrap25_invokeCallback','alcOpenDevice','alcLoopbackOpenDeviceSOFT','alcRenderSamplesSOFT','alBufferData','alSourcePlay','ps5_builtin_load_ps5openal','ps5_builtin_load_ps5nativeprobe']:assert symbols.get(name),name
with zipfile.ZipFile(package)as z,zipfile.ZipFile(ROOT/'dist/milestones/Client_Continuous_Direct_Scene-01.000.023/PPSA99874-full-local.zip')as old:
 assert z.testzip()is None;pre='PPSA99874/';param=json.loads(z.read(pre+'sce_sys/param.json'));assert param['contentVersion']=='01.000.033'
 for key in ['titleId','contentId','conceptId']:assert param[key]==json.loads(old.read(pre+'sce_sys/param.json'))[key]
 for row in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts']:assert sha(z.read(pre+'assets/java25/client/jars/'+row['file']))==row['sha256'],row['file']
 for name in old.namelist():
  if name.endswith('/lib/modules')or name.endswith('.so'):assert z.read(name)==old.read(name),name
 assert b'-Xmx128m'in z.read(pre+'eboot.bin')and b'Client033 ALL5 PASS'in z.read(pre+'eboot.bin')
 fixture=z.read(pre+'assets/java25/classes/ClientFreeType25.class');assert b'FT_Init_FreeType'in fixture and b'FT_Load_Char'in fixture and b'FT_Done_FreeType'in fixture and b'exact nine glyph rasterization fingerprint'in fixture and b'net.minecraft.client.main.Main'not in fixture
 assert (w/'classes/ClientFreeType25.class').read_bytes()==(ROOT/'build/freetype-bootstrap-host-033/ClientFreeType25.class').read_bytes()
 assert z.read(pre+'eboot.bin')==(w/'PPSA99874/eboot.bin').read_bytes()
 assert not any('DispatchHost25'in n or n.endswith(('.pcm','.at9'))for n in z.namelist())
 # All original Java FreeType function-table lookups must have real target exports.
 with zipfile.ZipFile(ROOT/'.tools/client/lwjgl-freetype-3.4.3.jar')as original_ft:
  required={name.decode()for name in re.findall(rb'(?:FT|FTC)_[A-Za-z0-9_]+',original_ft.read('org/lwjgl/util/freetype/FreeType$Functions.class'))}
 assert len(required)==211 and not(required-symbols.keys()),sorted(required-symbols.keys())
 module=z.read(pre+'assets/java25/ports/lwjgl-3.4.3-ps5-modules.jar');assert sha(module)==json.loads(z.read(pre+'assets/java25/module-platform-audit.json'))['output_sha256']
 groups=json.loads(z.read(pre+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'];assert [x['name']for x in groups]==['ps5clientgpu','ps5clientbridge','lwjgl','ps5sdl','ps5shaderc','ps5openal','ps5nativeprobe','freetype']
 pin=json.loads((ROOT/'client/ports/freetype/sources.json').read_text());assert sha(z.read(pre+'assets/java25/font-probe/Abel-Regular.ttf'))==pin['files'][1]['sha256']
 font_audit=json.loads(z.read(pre+'assets/java25/freetype-audit.json'));assert font_audit['exports']>=200 and font_audit['object_sha256']==sha((ROOT/'build/freetype-ps5/freetype.o').read_bytes())
 assert groups[-1]['objects_sha256']==[font_audit['object_sha256']]
 for name in ['freetype-audit.json','freetype-licenses/LICENSE.TXT','freetype-licenses/docs/FTL.TXT','font-probe/OFL.txt','ffi-audit.json','openal-audit.json','native-bootstrap-licenses/OpenAL-COPYING.txt','native-bootstrap-licenses/libffi-LICENSE.txt']:assert z.read(pre+'assets/java25/'+name)
for file in ['eboot.bin','sce_module/libc.prx']:
 output=subprocess.check_output([str(a.runtime_workspace/'build/native/host/ps5-native-tool'),'self','--inspect','--file',str(w/'PPSA99874'/file)],text=True);assert 'integrity: valid'in output
assert package.read_bytes()==(a.runtime_workspace/'dist/PPSA99874.zip').read_bytes()
for folder,digest in [('Client_Continuous_Direct_Scene-01.000.023','846cd9adea6f9e6b04f80df461424c26b1fec6aa080ed641c35e7cfb16488ea4'),('Client_Original_Startup-01.000.025','1c61c103fc96ac30a4c7acbdb985888a5cf2dfa848dadf90b74903c052097aee')]:
 root='milestones'if folder.startswith('Client_Continuous')else'failures';assert sha((ROOT/'dist'/root/folder/'PPSA99874-full-local.zip').read_bytes())==digest
assert sha((ROOT/'dist/milestones/Client_OpenGL_Provider-01.000.029/PPSA99874-full-local.zip').read_bytes())=='ed0cc6f49528b44b6d131c800e3c6359d01e009ae52524b7e96262a71491b685'
assert sha((ROOT/'dist/failures/Client_Original_Startup-01.000.030/PPSA99874-full-local.zip').read_bytes())=='1eb5bc45080aa65b9d38817db58e4984ff58668f491598322783c83c41cc8ce1'
assert sha((ROOT/'dist/failures/Client_Original_Startup-01.000.032/PPSA99874-full-local.zip').read_bytes())=='5d6fb33084876e0d0b08e5b020c6de196b98508d31b983a6f33cd9028635e434'
assert sha((ROOT/'dist/milestones/Client_STB_Codecs-01.000.031/PPSA99874-full-local.zip').read_bytes())=='061d1ab8b40fcd90cf5e3854ee6d5220a7410685ddb69634faaf688db92cb42c'
bootstrap=(ROOT/'client/freetype_bootstrap/bootstrap.cpp').read_text()+(ROOT/'client/bootstrap/acceptance_impl.hpp').read_text();assert 'test_count=5'in bootstrap and 'DestroyJavaVM'in bootstrap and '192.168.'not in bootstrap
print('PASS033 CRC/signatures/identity,54 original JARs/exact023 runtime image/native libraries,real FreeType glyph rasterization and original LWJGL downcalls plus existing native providers,359+4+5+'+str(al_ctors)+' staged constructors/no auto ctors,8resident groups,dependency overlay,128MiB/five-row fixture/no game or speaker success claim,preserved023/failed025 packages. PS5 pending.SHA256',sha(package.read_bytes()))
