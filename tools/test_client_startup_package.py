#!/usr/bin/env python3
"""Verify actual original-client startup package and all publisher asset objects."""
from pathlib import Path
import argparse,json,zipfile,hashlib,subprocess,struct,tarfile,io,tempfile
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args();runtime=a.runtime_workspace
work=ROOT/'build/client-startup-probe';package=ROOT/'dist/client-startup/PPSA99874.zip';sha=lambda data:hashlib.sha256(data).hexdigest()
@lru_cache(maxsize=None)
def archived_failure_hashes(archive):
 record=json.loads(archive.with_name(archive.name.removesuffix('.tar.zst')+'.json').read_text())
 with archive.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==record['archive_sha256']
 proc=subprocess.Popen(['zstd','-d','--long=30','-q','-c',str(archive)],stdout=subprocess.PIPE);actual={}
 try:
  with tarfile.open(fileobj=proc.stdout,mode='r|')as contents:
   for member in contents:
    if member.isfile():actual[member.name]=hashlib.file_digest(contents.extractfile(member),'sha256').hexdigest();assert actual[member.name]==record['files'][member.name]['sha256']
 finally:proc.stdout.close()
 assert proc.wait()==0 and set(actual)==set(record['files']);return actual
def failure_hash(path):
 if path.exists():return sha(path.read_bytes())
 name=path.relative_to(ROOT/'dist').as_posix()
 for manifest in sorted((ROOT/'dist/archives').glob('failed-client-builds*.json')):
  record=json.loads(manifest.read_text())
  if name in record['files']:
   return archived_failure_hashes(manifest.with_name(manifest.stem+'.tar.zst'))[name]
 raise FileNotFoundError('No preserved failed package: '+name)
def without_build_id(blob):
 assert blob[:6]==b'\x7fELF\x02\x01'
 result=bytearray(blob);offset=struct.unpack_from('<Q',blob,40)[0]
 entry_size,count,names_index=struct.unpack_from('<HHH',blob,58)
 row=struct.unpack_from('<IIQQQQIIQQ',blob,offset+names_index*entry_size)
 names=blob[row[4]:row[4]+row[5]];found=0
 for i in range(count):
  row=struct.unpack_from('<IIQQQQIIQQ',blob,offset+i*entry_size)
  if names[row[0]:].split(b'\0')[0]==b'.note.gnu.build-id':
   start,size=row[4],row[5];assert size==32
   assert struct.unpack_from('<III',blob,start)==(4,16,3) and blob[start+12:start+16]==b'GNU\0'
   result[start+16:start+32]=bytes(16);found+=1
 assert found==1
 return bytes(result)
elf=work/'bootstrap-01.000.146-symbols.elf';text=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(elf)],text=True);symbols={l.split()[-1]:int(l.split()[0],16)for l in text.splitlines()if len(l.split())==3}
assert symbols.get('client_ps5_audio_early_init_result') and symbols.get('client_ps5_audio_early_port')
imports=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(elf)],text=True)
for jna in ['Java_com_sun_jna_Native_getLastError','Java_com_sun_jna_Native_setLastError','Java_com_sun_jna_Native_sizeof','Java_com_sun_jna_Native_initIDs','ps5_builtin_load_jnidispatch']:assert symbols.get(jna),jna
for api in ['sceKeyboardInit','sceKeyboardOpen','sceKeyboardRead','sceKeyboardClose','sceMouseInit','sceMouseOpen','sceMouseRead','sceMouseClose','scePadSetVibration','scePadSetVibrationMode']:assert api in imports

assert symbols.get('prospero_graphics_init')
assert (symbols['__client_ui_init_end']-symbols['__client_ui_init_start'])//8==1
for marker in ['VkRenderer','PushButton','GridView','Dialog','prospero_ui']:
 assert marker in text,marker

assert symbols['__init_array_start']==symbols['__init_array_end'];assert (symbols['__client_openal_init_end']-symbols['__client_openal_init_start'])//8==15;assert (symbols['__jvm_init_array_end']-symbols['__jvm_init_array_start'])//8==359;assert (symbols['__client_gpu_init_end']-symbols['__client_gpu_init_start'])//8==4;assert (symbols['__client_shaderc_init_end']-symbols['__client_shaderc_init_start'])//8==4
assert (symbols['__client_gl_init_end']-symbols['__client_gl_init_start'])//8==1
for name in ['OSMesaGetProcAddress','OSMesaCreateContextAttribs','ps5_builtin_load_ps5clientgl','ps5_builtin_load_lwjgl_opengl','ffi_prep_closure_loc','ffi_call_plan_alloc','alcLoopbackOpenDeviceSOFT','alcRenderSamplesSOFT','ps5_builtin_load_ps5openal','JNI_CreateJavaVM','ps5_builtin_load_ps5sdl','ps5_builtin_load_ps5shaderc','ps5_builtin_load_ps5clientgpu','radv_CreateInstance','ps5_builtin_load_lwjgl_stb','Java_org_lwjgl_stb_LibSTB_setupMalloc','Java_org_lwjgl_stb_STBImage_nstbi_1load_1from_1memory__JIJJJI','clientstb_org_lwjgl_malloc','ps5_builtin_load_freetype','FT_Init_FreeType','FT_Load_Char','FT_Done_FreeType','ps5_builtin_load_lwjgl_vma','Java_org_lwjgl_util_vma_Vma_nvmaCreateAllocator','ps5_builtin_load_ps5spvc','spvc_context_create','spvc_compiler_compile']:assert symbols.get(name),name
for name in ['Java_ProsperoContentImages_nativeDecode','prospero_content_thumbnail','WebPDecodeRGBAInto','ps5_builtin_load_ps5contentimages','prospero_hid_preload','prospero_hid_open','prospero_hid_read','prospero_hid_close','ps5_builtin_load_awt','ps5_builtin_load_lcms','Java_sun_java2d_Disposer_initIDs','Java_java_awt_image_BufferedImage_initIDs','Java_java_awt_image_ColorModel_initIDs','Java_sun_java2d_cmm_lcms_LCMS_loadProfileNative','Java_sun_java2d_cmm_lcms_LCMS_colorConvert']:assert symbols.get(name),name
with zipfile.ZipFile(package)as registry_zip:
 registry=json.loads(registry_zip.read('PPSA99874/assets/java25/resident-libraries-audit.json'))
 assert registry['library_aliases']=={'SDL3':'ps5sdl','libzstd-jni_dh-1.5.7-12':'ps5zstddh','zstd-jni_dh-1.5.7-12':'ps5zstddh','sqlitejdbc':'ps5sqlitedh'}
 binary=registry_zip.read('PPSA99874/eboot.bin');assert b'libSDL3.so' in binary and b'JNI_OnLoad_SDL3' in binary
with zipfile.ZipFile(package)as z,zipfile.ZipFile(ROOT/'dist/milestones/Client_Continuous_Direct_Scene-01.000.023/PPSA99874-full-local.zip')as baseline:
 pin=json.loads(z.read('PPSA99874/assets/java25/launcher-toolkit/upstream.json'))
 assert pin['revision']=='2188642afbcc8d84d36149124f3d9e39dc1b1a05' and pin['patches']==[]
 for name,digest in pin['sha256'].items():
  assert sha(z.read('PPSA99874/assets/java25/launcher-toolkit/'+name))==digest,name
 for name in ['toolkit_surface.hpp','toolkit_canvas.hpp','toolkit_effects.hpp','native_menu.hpp','navigation.hpp','haptics.hpp']:
  assert z.read('PPSA99874/assets/java25/launcher-toolkit/'+name)==(ROOT/'client/launcher'/name).read_bytes()
 assert not any('/assets/audio/' in n for n in z.namelist())
 imageio=json.loads(z.read('PPSA99874/assets/java25/imageio-native-audit.json'))
 assert imageio['host'] is False and imageio['groups']['awt']['compile_units']==4 and imageio['groups']['lcms']['compile_units']>20
 for name in ['awt','lcms']:
  assert sha(z.read('PPSA99874/assets/java25/lib/lib'+name+'.so'))==sha((runtime/'build/java25/imageio-target'/('lib'+name+'.so')).read_bytes())
  assert imageio['groups'][name]['output_sha256']==sha((runtime/'build/java25/imageio-target'/('lib'+name+'.o')).read_bytes())
 assert z.testzip()is None;prefix='PPSA99874/';param=json.loads(z.read(prefix+'sce_sys/param.json'));assert param['attribute3']&0x40;old=json.loads(baseline.read(prefix+'sce_sys/param.json'));assert param['contentVersion']=='01.000.146';assert param['downloadDataSize']==4096
 assert param['localizedParameters']['en-US']['titleName']=='ProsperoCraft'
 assert z.read(prefix+'sce_sys/icon0.png')==(ROOT/'assets/branding/icon0.png').read_bytes()
 from apply_branding import presentation_assets,validate_background
 for name,pixels in presentation_assets().items():
  assert z.read(prefix+'sce_sys/'+name)==pixels;validate_background(pixels)
 assert prefix+'sce_sys/prosperocraft_title.png'not in z.namelist()
 for k in ['titleId','contentId','conceptId']:assert param[k]==old[k]
 assert b'-Xmx1536m'in z.read(prefix+'eboot.bin') and b'Minecraft Original Client Startup 01.000.146'in z.read(prefix+'eboot.bin')
 for flag in [b'-Xmixed',b'-XX:TieredStopAtLevel=1',b'-XX:CICompilerCount=1',b'-XX:CompileThresholdScaling=4.0',b'-XX:CompileCommand=MemLimit,*.*,2M',b'-XX:ReservedCodeCacheSize=96m',b'-XX:MetaspaceSize=128m',b'-XX:+ExplicitGCInvokesConcurrent',b'-Djava.awt.headless=true',b'java25-jit.log']:
  assert flag in z.read(prefix+'eboot.bin'),flag
 assert b'-XX:+UseG1GC' in z.read(prefix+'eboot.bin') and b'-XX:NewRatio=' not in z.read(prefix+'eboot.bin')
 assert b'-XX:ParallelGCThreads=4' in z.read(prefix+'eboot.bin') and b'-XX:ConcGCThreads=1' in z.read(prefix+'eboot.bin')
 assert '"-Xint"' not in (ROOT/'client/startup/bootstrap.cpp').read_text()
 assert b'JIT_WARMUP_OK' in z.read(prefix+'assets/java25/classes/ps5probe/JitWarmup25.class')
 assert b'ps5probe/JitWarmup25' in z.read(prefix+'assets/java25/classes/ClientStartup25.class')
 assert b'gameMain'in z.read(prefix+'assets/java25/classes/ClientStartup25.class') and b'configureGameLaunch'in z.read(prefix+'assets/java25/classes/ClientStartup25.class')
 fixture=z.read(prefix+'assets/java25/classes/ClientStartup25.class');assert b'java/lang/reflect/Method'in fixture and b'launchArguments'in fixture and b'--demo'in fixture and b'--disableMultiplayer'in fixture
 observer=z.read(prefix+'assets/java25/classes/ClientStartup25$StartupObserver.class')
 assert b'PS5 STARTUP SNAPSHOT' in observer and b'getAllStackTraces' in observer and b'heapUsed=' in observer
 assert all(marker in observer for marker in (b'PS5 MAIN TRANSITION',b'getStackTrace',b'isLanguageApply',b'unchangedFromTransition='))
 assert observer==(ROOT/'build/startup-host-096/ClientStartup25$StartupObserver.class').read_bytes()
 assert b'PS5 startup observer unavailable;continuing original Main' in fixture
 with zipfile.ZipFile(io.BytesIO(z.read(prefix+'assets/java25/client-probe.jar'))) as launch_jar:
  assert launch_jar.read('ClientStartup25.class')==fixture
  for entry in ['ProsperoAuth.class','ProsperoAuth$Net.class','ProsperoAuth$Endpoint.class','ProsperoAccountStore.class','ProsperoAccountStore$SignInRequired.class','ProsperoLauncher.class']:
   assert launch_jar.read(entry)==z.read(prefix+'assets/java25/classes/'+entry)
   assert launch_jar.read(entry)==(ROOT/'build/startup-host-096'/entry).read_bytes()
  auth=launch_jar.read('ProsperoAuth.class');endpoints=launch_jar.read('ProsperoAuth$Endpoint.class');account=launch_jar.read('ProsperoAccountStore.class')
  assert b'f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3' in auth and b'00000000402b5328' not in auth
  assert b'XboxLive.signin offline_access' in auth and b'service::user.auth.xboxlive.com::MBI_SSL' not in auth
  for path in [b'consumers/oauth2/v2.0/devicecode',b'consumers/oauth2/v2.0/token']:assert path in endpoints
  assert b'login.live.com' not in endpoints
  assert b'ProsperoCraft account v2' in account and b'f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3' in account
  assert b'PLAY' in launch_jar.read('ProsperoLauncher.class')
  assert b'net.minecraft.client.main.Main' in launch_jar.read('ProsperoLauncher.class')
  assert b'net.fabricmc.loader.impl.launch.knot.KnotClient' in launch_jar.read('ProsperoFabric.class')
  for name in ['ProsperoDownloads.class','ProsperoFabric.class','ProsperoModrinth.class']:assert name in launch_jar.namelist()
  assert b'fabric.systemLibraries' in launch_jar.read('ProsperoFabric.class')
  assert b'setDefaultUseCaches' in launch_jar.read('ProsperoFabric.class')
  assert b'PS5_CONTROLLER_BINDINGS' in fixture
  assert b'controllerKeys' in launch_jar.read('ProsperoLibrary$Settings.class')
  assert b'Mouse middle' in launch_jar.read('ProsperoInput.class')
  assert b'PS5 physical keyboard' in z.read(prefix+'eboot.bin') and b'PS5 physical mouse' in z.read(prefix+'eboot.bin')
  assert b'launcherMenu' in fixture and b'ProsperoLauncher' in fixture
  assert b'ProsperoCraft native launcher visible before Java and Minecraft graphics' not in z.read(prefix+'eboot.bin')
  assert b'ProsperoCraft: preparing your launcher.' not in z.read(prefix+'eboot.bin')
  assert b'COMING SOON' in launch_jar.read('ProsperoLauncher.class')
  channel=launch_jar.read('prosperocraft-channel.txt').decode().strip();assert channel=='temp_gametest'
  if channel=='offline':assert launch_jar.read('offline-import-public-key.der')==(ROOT/'client/launcher/offline-import-public-key.der').read_bytes()
  else:assert 'offline-import-public-key.der' not in launch_jar.namelist()
  assert b'DELETE INSTANCE' in z.read(prefix+'eboot.bin')
  assert b'ProsperoChannel' in launch_jar.read('ProsperoLauncher.class')
  assert b'ProsperoOfflineAccount' in launch_jar.read('ProsperoLauncher.class')
  assert b'SHA256withRSA' in launch_jar.read('ProsperoOfflineAccount.class')
  assert b'Welcome to ProsperoCraft' in z.read(prefix+'eboot.bin')
  assert b'resolutionLabel' in launch_jar.read('ProsperoLauncher.class')
  assert b'RESOLUTIONS' in launch_jar.read('ProsperoLauncher.class')
  assert b'RESOLUTIONS' in launch_jar.read('ProsperoLibrary.class')
  assert launch_jar.read('ClientStartup25$StartupObserver.class')==observer
 cpu_overlay=z.read(prefix+'assets/java25/ports/oshi-6.9.0-ps5-platform.jar')
 assert cpu_overlay==(ROOT/'build/client-ports/oshi/oshi-6.9.0-ps5-platform.jar').read_bytes()
 cpu_audit=json.loads(z.read(prefix+'assets/java25/oshi-platform-audit.json'));assert cpu_audit['output_sha256']==sha(cpu_overlay)
 cpu7=z.read(prefix+'assets/java25/ports/oshi-7.7.2-ps5-provider.jar')
 assert cpu7==(ROOT/'build/client-ports/oshi7/oshi-7.7.2-ps5-provider.jar').read_bytes()
 assert json.loads(z.read(prefix+'assets/java25/oshi7-platform-audit.json'))['output_sha256']==sha(cpu7)
 assert z.read(prefix+'assets/java25/oshi7-licenses/LICENSE')==(ROOT/'client/ports/oshi7/LICENSE').read_bytes()
 with zipfile.ZipFile(io.BytesIO(cpu7)) as provider:
  assert provider.read('META-INF/services/oshi.spi.SystemInfoProvider')==b'oshi.ps5.Ps5SystemInfoProvider\n'
  assert all(not n.startswith(('net/minecraft/','com/mojang/','oshi/ffm/','oshi/spi/')) for n in provider.namelist())

 assert b'cpuInformation' in fixture and b'ps5.cpu.' in fixture and b'prepareCpuInformation' in fixture and b'oshi.ps5' in fixture
 with zipfile.ZipFile(io.BytesIO(cpu_overlay)) as cpu_jar:assert all(not n.startswith(('net/minecraft/','com/mojang/')) for n in cpu_jar.namelist())
 jna=json.loads(z.read(prefix+'assets/java25/jna-audit.json'));assert jna['commit']=='1a91122853f6ab6f1fb2a4a284a6cf2ed8af0a4d' and jna['native_version']=='7.0.4' and len(jna['jni_exports'])==69
 assert jna['output_sha256']==sha((runtime/'build/java25/jna-target/jnidispatch.o').read_bytes())
 assert z.read(prefix+'assets/java25/jna-licenses/AL2.0')==(runtime/'build/java25/jna-target/source/AL2.0').read_bytes()
 assert z.read(prefix+'licenses/ProsperoCraft-LICENSE-GPL-3.0.txt')==(ROOT/'LICENSE').read_bytes()
 assert z.read(prefix+'licenses/ProsperoCraft-NOTICE.txt')==(ROOT/'NOTICE').read_bytes()
 assert b'-Xlog:gc=info,safepoint=info:file=/download0/java25-gc.log:uptimemillis,level,tags:filecount=1,filesize=4M'in z.read(prefix+'eboot.bin')
 for route in (b'/gc.log',b'/gc-rotated.log',b'/previous-gc.log',b'/previous-gc-rotated.log'):assert route in z.read(prefix+'eboot.bin')
 assert b'PS5_TEMPORARY_CONTROLS' in fixture and b'ps5.temporaryControls' in fixture
 assert b'inactivityFpsLimit' in fixture and b'minimized' in fixture and b'options.before-menu063.txt' in fixture
 sdl_audit=json.loads(z.read(prefix+'assets/java25/sdl-audit.json'))
 for name in ['SDL_ps5video.c','ps5_display_mode.h','ps5_temporary_input.h','ps5_relative_mouse.h','platform-input.c']:
  assert sdl_audit['port_sha256'][name]==sha((ROOT/'client/ports/sdl'/name).read_bytes()),name
 assert b'-Xmx256m' not in z.read(prefix+'eboot.bin')
 assert b'heap maxMiB='in fixture
 assert b'PS5_SESSION REPLACE_PROCESS' in z.read(prefix+'eboot.bin')
 assert b'/app0/eboot.bin' in z.read(prefix+'eboot.bin')
 assert b'normalQuit' in fixture
 assert b'ProsperoSession' in fixture
 for entry in ['ProsperoSession.class','ProsperoSession$Evidence.class']:
  assert z.read(prefix+'assets/java25/classes/'+entry)==(ROOT/'build/startup-host-096'/entry).read_bytes()
 assert b'--prospero-library' in z.read(prefix+'eboot.bin')
 assert b'Original game main returned;inspect exceptions.log' not in fixture
 bootstrap=(ROOT/'client/startup/bootstrap.cpp').read_text();assert bootstrap.index('client_ps5_audio_early_init_result=sceAudioOutInit()')<bootstrap.index('JNI_CreateJavaVM(&');assert 'test_count=4'in bootstrap and 'for(int i:{1,3})'in bootstrap and 'ClientContinuousSDL25'not in bootstrap
 assert not any(n.endswith(('.pcm','.at9'))for n in z.namelist())
 lock=json.loads((ROOT/'client/26.3.lock.json').read_text())
 dependencies=json.loads(z.read(prefix+'assets/java25/launcher-dependencies.json'))
 assert all(row['id'].startswith(('org.lwjgl:','com.google.code.gson:')) for row in dependencies)
 for row in dependencies:assert sha(z.read(prefix+'assets/java25/client/jars/'+row['file']))==row['sha256'],row['file']
 assert not any('/game-assets/' in name or name.endswith('/client-26.3.jar') for name in z.namelist())
 assert 'PPSA99874/assets/java25/client/client-inventory.properties' not in z.namelist()
 for row in lock['artifacts']:
  if row not in dependencies:assert prefix+'assets/java25/client/jars/'+row['file'] not in z.namelist()
 for entry in (ROOT/'build/startup-host-096').glob('Prospero*.class'):
  assert z.read(prefix+'assets/java25/classes/'+entry.name)==entry.read_bytes(),entry.name
 for name in [b'ProsperoInstall',b'ProsperoLibrary',b'selectedWork',b'gameLoader']:assert name in fixture or name in z.read(prefix+'assets/java25/classes/ProsperoLauncher.class')

 for name in baseline.namelist():
  if name.endswith('/lib/modules'):assert z.read(name)==(runtime/'build/java25/boot-image/lib/modules').read_bytes(),name
  elif name.endswith(('/libjava.so','/libverify.so','/libnet.so')):assert z.read(name)==(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base'/Path(name).name).read_bytes(),name
  elif name.endswith('/libnio.so'):assert z.read(name)==(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libnio.so').read_bytes(),name
  elif name in [prefix+'assets/java25/lib/libawt.so',prefix+'assets/java25/lib/liblcms.so']:assert z.read(name)==(runtime/'build/java25/imageio-target'/Path(name).name).read_bytes()
  elif name.endswith('.so') and not name.endswith('/server/libjvm.so'):assert without_build_id(z.read(name))==without_build_id(baseline.read(name)),name
 assert z.read(prefix+'assets/java25/lib/server/libjvm.so')==(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/server/libjvm.so').read_bytes()
 assert b'-Dps5.zip.maxOpenFiles=64' in z.read(prefix+'eboot.bin')
 assert b'-XX:-UseCompressedOops' in z.read(prefix+'eboot.bin')
 assert b'PS5 uncompressed heap direct reservation' in z.read(prefix+'eboot.bin')
 assert not any('/game-assets/' in name for name in z.namelist())
 assert z.read(prefix+'assets/java25/log4j2-startup.xml')==(ROOT/'client/startup/log4j2-startup.xml').read_bytes()
 al_boundary=json.loads(z.read(prefix+'assets/java25/openal-audit.json'))['startup_boundaries']
 assert al_boundary['original_archive_unchanged']is True
 assert al_boundary['replaced_members']==['alc.cpp.o','helpers.cpp.o','logging.cpp.o']
 for field,file in [('source_sha256','ps5_backend.cpp'),('header_sha256','ps5_backend.h')]:assert al_boundary['speaker_backend'][field]==sha((ROOT/'client/ports/openal'/file).read_bytes())
 assert al_boundary['speaker_backend']['object_sha256']==sha((ROOT/'build/openal-startup-boundary-ps5/ps5_backend.cpp.o').read_bytes())
 assert b'PS5 OpenAL AudioOut' in z.read(prefix+'eboot.bin') and b'PS5 Speakers' in z.read(prefix+'eboot.bin')
 assert b'audio-enabled-067.txt' in fixture and b'options.before-audio067.txt' in fixture
 assert b'PS5 startup observer disabled for performance run' in fixture
 assert b'AudioOut pre-JVM init result=' in z.read(prefix+'eboot.bin')
 assert b'-XX:MaxGCPauseMillis=4' in z.read(prefix+'eboot.bin')
 assert b'-XX:-ClassUnloadingWithConcurrentMark' in z.read(prefix+'eboot.bin') and b'-XX:-ClassUnloading\x00' not in z.read(prefix+'eboot.bin')
 for flag in [b'-XX:+UnlockExperimentalVMOptions',b'-XX:G1NewSizePercent=1',b'-XX:G1MixedGCCountTarget=16']:assert flag in z.read(prefix+'eboot.bin')
 assert b'PS5_OPTIONS_BEFORE_MAIN' in fixture and b'distancePolicy=preserve-existing/no-new-cap' in fixture
 assert b'PS5 retained histogram sample=' in z.read(prefix+'eboot.bin') and b'PS5 histogram: remaining' in z.read(prefix+'eboot.bin')
 assert b'prepareAudio' in fixture and b'soundCategory_master:0.5' in fixture
 dynamic=subprocess.check_output([str(LLVM/'llvm-readelf'),'--dynamic',str(elf)],text=True)
 assert 'Shared library: [libSceAudioOut.sprx]' in dynamic
 undefined=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(elf)],text=True)
 for api in ['sceAudioOutInit','sceAudioOutOpen','sceAudioOutOutput','sceAudioOutClose']:assert any(line.split()[-1]==api for line in undefined.splitlines())
 assert al_boundary['cwd_discovery_repair']['unit_object_sha256']==sha((ROOT/'build/openal-startup-boundary-ps5/helpers.cpp.o').read_bytes())
 assert al_boundary['header_sha256']==sha((ROOT/'client/ports/openal/startup_boundary.hpp').read_bytes())
 assert al_boundary['original_archive_sha256']==sha((ROOT/'build/openal-ps5/libopenal.a').read_bytes())
 assert al_boundary['private_archive_sha256']==sha((ROOT/'build/openal-startup-boundary-ps5/libopenal-boundary.a').read_bytes())
 assert al_boundary['output_sha256']==sha((ROOT/'build/openal-startup-boundary-ps5/openal.o').read_bytes())
 assert b'PS5 OpenAL boundary id='in z.read(prefix+'eboot.bin')
 al_trace=json.loads(z.read(prefix+'assets/java25/openal-audit.json'))['startup_trace']
 assert al_trace['backend_selection_changed']is True
 assert al_trace['local_data_directory_default']=='/download0/mc-client' and al_trace['explicit_local_path_honored']is True
 assert b'ALSOFT_LOCAL_PATH'in z.read(prefix+'eboot.bin')
 assert al_trace['source_sha256']==sha((ROOT/'client/startup/openal_trace_env.c').read_bytes())
 assert al_trace['private_object_sha256']==sha((work/'startup-openal.o').read_bytes())
 assert al_trace['shim_object_sha256']==sha((work/'startup-openal-trace-env.o').read_bytes())
 assert al_trace['original_object_sha256']==sha((ROOT/'build/openal-ps5/openal.o').read_bytes())
 trace_refs=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(work/'startup-openal.o')],text=True)
 assert 'client_startup_openal_getenv'in trace_refs and not any(line.split()[-1]=='getenv'for line in trace_refs.splitlines())
 assert symbols.get('client_startup_openal_getenv')
 groups=json.loads(z.read(prefix+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'];assert [g['name']for g in groups]==['ps5clientgpu','ps5clientbridge','lwjgl','ps5sdl','ps5glfw','lwjgl_tinyfd','ps5shaderc','jnidispatch','ps5openal','ps5nativeprobe','ps5clientgl','lwjgl_opengl','ps5contentimages','lwjgl_stb','freetype','lwjgl_vma','ps5spvc','ps5zstddh','ps5sqlitedh']
 cpp=json.loads(z.read(prefix+'assets/java25/cpp-allocation-audit.json'));assert cpp['scoped_object_sha256']==sha((work/'cpp_runtime.o').read_bytes())
 sdl=json.loads(z.read(prefix+'assets/java25/sdl-audit.json'));assert sdl['port_sha256']['ps5_display_mode.h']==sha((ROOT/'client/ports/sdl/ps5_display_mode.h').read_bytes());assert sdl['port_sha256']['SDL_ps5video.c']==sha((ROOT/'client/ports/sdl/SDL_ps5video.c').read_bytes());assert sdl['scoped_object_sha256']==sha((work/'resident-sdl.o').read_bytes())
 gpu=json.loads(z.read(prefix+'assets/java25/gpu-integration-audit.json'));assert gpu['vulkan_binding']['loader_object_sha256']==sha((work/'vulkan-loader.o').read_bytes())
 wsi=gpu['wsi_diagnostics'];assert wsi['original_archive_unchanged'] is True
 assert wsi['patch_sha256']==sha((ROOT/'client/ports/mesa/0001-videoout-checkpoints.patch').read_bytes())
 assert wsi['retry_patch_sha256']==sha((ROOT/'client/ports/mesa/0002-videoout-open-retry.patch').read_bytes())
 assert wsi['resources_patch_sha256']==sha((ROOT/'client/ports/mesa/0003-videoout-resources.patch').read_bytes())
 assert wsi['early_owner_patch_sha256']==sha((ROOT/'client/ports/mesa/0004-videoout-early-owner.patch').read_bytes())
 assert gpu['early_videoout_owner'].startswith('Same WSI output')
 assert symbols.get('client_wsi_videoout_prepare')
 bridge_refs=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(ROOT/'build/client-gpu/gpu-bridge.o')],text=True)
 assert 'client_wsi_videoout_prepare' in bridge_refs
 assert b'Client083 native stderr stream active before embedded constructors' in z.read(prefix+'eboot.bin')
 assert b'diagnostic failure is nonfatal' in z.read(prefix+'eboot.bin')
 main_refs=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(work/'main.o')],text=True)
 assert 'dup2' not in main_refs and 'fdopen' in main_refs
 assert b'/native-stderr.log' in z.read(prefix+'eboot.bin')
 assert b'/previous-native-stderr.log' in z.read(prefix+'eboot.bin')
 assert b'Original startup fault recorder installed handlers' in z.read(prefix+'eboot.bin')
 assert symbols.get('ps5shaderc_fault_begin') and symbols.get('ps5shaderc_fault_end') and symbols.get('ps5shaderc_fault_status')
 assert b'fault_owned_mask=' in z.read(prefix+'eboot.bin') and b'flexible_rc=' in z.read(prefix+'eboot.bin')
 assert b'nativeSnapshot' in fixture
 assert b'direct_total=' in z.read(prefix+'eboot.bin') and b'rlimit_%s_rc=' in z.read(prefix+'eboot.bin')
 assert b'Early WSI output initialization' in z.read(prefix+'eboot.bin')
 assert symbols.get('client_wsi_keyboard')
 assert wsi['keyboard_patch_sha256']==sha((ROOT/'client/ports/mesa/0007-videoout-keyboard-overlay.patch').read_bytes())
 for name,digest in wsi['keyboard_headers_sha256'].items():assert digest==sha((ROOT/'client/ports/mesa'/name).read_bytes())
 assert wsi['cursor_patch_sha256']==sha((ROOT/'client/ports/mesa/0006-videoout-menu-cursor.patch').read_bytes())
 assert wsi['present_progress_patch_sha256']==sha((ROOT/'client/ports/mesa/0005-videoout-present-progress.patch').read_bytes())
 for marker in [b'WSI present%u enqueue',b'WSI flip%u fence begin',b'WSI flip%u fence result',b'WSI flip%u submit',b'WSI flip thread create']:assert marker in z.read(prefix+'eboot.bin')
 assert b'WSI resources %s' in z.read(prefix+'eboot.bin')
 assert b'WSI VideoOut open attempt' in z.read(prefix+'eboot.bin')
 assert wsi['original_archive_sha256']==sha((ROOT/'build/graphics-radv/src/amd/vulkan/libvulkan_radeon.a').read_bytes())
 assert wsi['private_archive_sha256']==sha((ROOT/'build/wsi-diagnostics/libvulkan_radeon-diagnostic.a').read_bytes())
 assert wsi['object_sha256']==sha((ROOT/'build/wsi-diagnostics/wsi_common_videoout.c.o').read_bytes())
 assert b'WSI create requested' in z.read(prefix+'eboot.bin') and b'WSI failure' in z.read(prefix+'eboot.bin')
 allocation=json.loads(z.read(prefix+'assets/java25/lwjgl-allocation-audit.json'));assert allocation['runtime_global_allocator_modified']is False
 assert set(allocation['bindings'])=={'malloc','calloc','realloc','free','posix_memalign','aligned_alloc'}
 assert len(allocation['objects_sha256'])==2
 for unit,digest in allocation['objects_sha256'].items():
  obj=work/unit;assert sha(obj.read_bytes())==digest
  undefined=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(obj)],text=True);references={line.split()[-1] for line in undefined.splitlines() if line.split()}
  assert not references.intersection(allocation['bindings']),references
  for name in ['malloc','calloc','realloc','free']:assert allocation['bindings'][name] in references
  for name,target in allocation['bindings'].items():assert target==gpu['graphics_bindings'][name]
 assert b'verifyNativeAllocation' in fixture and b'grow8MiB' in fixture
 audit=json.loads(z.read(prefix+'assets/java25/dependency-port-audit.json'));assert audit['activated_for_game']is True
for file in ['eboot.bin','sce_module/libc.prx']:
 report=subprocess.check_output([str(runtime/'build/native/host/ps5-native-tool'),'self','--inspect','--file',str(work/'PPSA99874'/file)],text=True);assert 'integrity: valid'in report
assert package.read_bytes()==(runtime/'dist/PPSA99874.zip').read_bytes()
for folder,digest in [('Client_Continuous_Direct_Scene-01.000.023','846cd9adea6f9e6b04f80df461424c26b1fec6aa080ed641c35e7cfb16488ea4'),('Client_Visible_Perspective_Scene-01.000.022','9d49135a4dcbd66e93ef496e442c7845964e08aa6664c9dc26546a94196e450e')]:assert sha((ROOT/'dist/milestones'/folder/'PPSA99874-full-local.zip').read_bytes())==digest
with zipfile.ZipFile(package)as z:
 assert z.read('PPSA99874/assets/java25/ports/lwjgl-3.4.3-ps5-modules.jar')==(ROOT/'build/client-ports/lwjgl-modules/lwjgl-3.4.3-ps5-modules.jar').read_bytes()
 validation=json.loads((ROOT/'Client_OpenGL_Provider/validation.json').read_text())
 current_gl=json.loads(z.read('PPSA99874/assets/java25/opengl-provider-audit.json'));old_gl=validation['opengl_provider_audit']
 assert current_gl['renames']=={**old_gl['renames'],'strdup':'clientgpu_strdup','strndup':'clientgpu_strndup'}
 for key,value in old_gl.items():
  if key not in ['renames','objects_sha256']:assert current_gl[key]==value,key
 for name,digest in current_gl['objects_sha256'].items():
  assert sha((ROOT/'build/osmesa-ps5'/name).read_bytes())==digest
  if name!='osmesa-resident.o':assert digest==old_gl['objects_sha256'][name]
 # Reproduce the frozen object's exact bytes from the same raw object with its
 # old binding map; only the two intended string routes differ in the new one.
 with tempfile.TemporaryDirectory()as directory:
  directory=Path(directory);mapping=directory/'old.map';mapping.write_text(''.join(k+' '+v+'\n'for k,v in sorted(old_gl['renames'].items())))
  original=directory/'old.o';subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(mapping),str(ROOT/'build/osmesa-ps5/osmesa-raw.o'),str(original)],check=True)
  options=[]
  for name in old_gl['constructor_sections']:
   suffix=name.rsplit('.',1)[-1];priority=(65535-int(suffix)if name.startswith('.ctors.')else int(suffix))if suffix.isdigit()else 65535
   options+=['--rename-section',name+'=.data.rel.ro.clientgl.init_array.'+f'{priority:05d}'+name]
  if options:subprocess.run([str(LLVM/'llvm-objcopy'),*options,str(original)],check=True)
  assert sha(original.read_bytes())==old_gl['objects_sha256']['osmesa-resident.o']
 assert json.loads(z.read('PPSA99874/assets/java25/opengl-jni-audit.json'))['object_sha256']==validation['opengl_jni_audit']['object_sha256']
 assert sha(z.read('PPSA99874/assets/java25/ports/lwjgl-3.4.3-ps5-modules.jar'))==validation['module_platform_audit']['output_sha256']
 assert (work/'classes/ClientStartup25.class').read_bytes()==(ROOT/'build/startup-host-096/ClientStartup25.class').read_bytes()
 assert b'OSMesa'in z.read('PPSA99874/assets/java25/classes/ClientStartup25.class')
 assert b'ps5clientgl'in z.read('PPSA99874/assets/java25/classes/ClientStartup25.class')
 assert sha((ROOT/'dist/milestones/Client_OpenGL_Provider-01.000.029/PPSA99874-full-local.zip').read_bytes())=='ed0cc6f49528b44b6d131c800e3c6359d01e009ae52524b7e96262a71491b685'
 stb_validation=json.loads((ROOT/'Client_STB_Codecs/validation.json').read_text())
 with zipfile.ZipFile(ROOT/'dist/milestones/Client_STB_Codecs-01.000.031/PPSA99874-full-local.zip')as stb_baseline:
  assert z.read(prefix+'assets/java25/stb-audit.json')==stb_baseline.read(prefix+'assets/java25/stb-audit.json')
  assert next(g for g in groups if g['name']=='lwjgl_stb')==json.loads(stb_baseline.read(prefix+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'][-1]
 with zipfile.ZipFile(ROOT/'dist/milestones/Client_OpenGL_Provider-01.000.029/PPSA99874-full-local.zip')as gl_baseline:
  prior_groups=json.loads(gl_baseline.read(prefix+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'][-2:]
  for group in prior_groups:
   if group['name']=='ps5clientgl':
    assert group['objects_sha256'][0]==old_gl['objects_sha256']['osmesa-resident.o']
    group['objects_sha256'][0]=current_gl['objects_sha256']['osmesa-resident.o']
  assert [g for g in groups if g['name']in ['ps5clientgl','lwjgl_opengl']]==prior_groups
 assert sha((ROOT/'build/lwjgl-stb-ps5/lwjgl-stb.o').read_bytes())==json.loads(z.read(prefix+'assets/java25/stb-audit.json'))['object_sha256']
 assert sha((ROOT/'dist/milestones/Client_STB_Codecs-01.000.031/PPSA99874-full-local.zip').read_bytes())==stb_validation['tested_full_package_sha256']
 assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.030/PPSA99874-full-local.zip')=='1eb5bc45080aa65b9d38817db58e4984ff58668f491598322783c83c41cc8ce1'
 with zipfile.ZipFile(ROOT/'dist/milestones/Client_FreeType_Fonts-01.000.033/PPSA99874-full-local.zip')as font_baseline:
  assert z.read(prefix+'assets/java25/freetype-audit.json')==font_baseline.read(prefix+'assets/java25/freetype-audit.json')
  assert next(g for g in groups if g['name']=='freetype')==json.loads(font_baseline.read(prefix+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'][-1]
 assert sha((ROOT/'dist/milestones/Client_FreeType_Fonts-01.000.033/PPSA99874-full-local.zip').read_bytes())=='e7666f17dedda986507f9ba19fa11183bf89baf07971044659dcee2416022afc'
 assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.032/PPSA99874-full-local.zip')=='5d6fb33084876e0d0b08e5b020c6de196b98508d31b983a6f33cd9028635e434'
 for milestone,version,group,audit in [('Client_VMA_Allocator','01.000.035','lwjgl_vma','vma'),('Client_SPIRV_Cross','01.000.036','ps5spvc','spvc')]:
  record=json.loads((ROOT/milestone/'validation.json').read_text());frozen=ROOT/'dist/milestones'/(milestone+'-'+version)/'PPSA99874-full-local.zip'
  assert sha(frozen.read_bytes())==record['tested_full_package_sha256']
  with zipfile.ZipFile(frozen)as accepted:
   current_audit=json.loads(z.read(prefix+'assets/java25/'+audit+'-audit.json'))
   expected_audit=json.loads(accepted.read(prefix+'assets/java25/'+audit+'-audit.json'))
   expected_group=json.loads(accepted.read(prefix+'assets/java25/resident-libraries-audit.json'))['external_resident_libraries'][-1]
   if audit=='vma':
    # Keep frozen035 bytes/hash intact; only development uses custom lock hooks.
    current_hash=sha((ROOT/'build/lwjgl-vma-ps5/lwjgl-vma.o').read_bytes())
    expected_audit['object_sha256']=current_hash
    expected_audit['locks']=current_audit['locks']
    assert current_audit['locks']['hooks']==['VMA_MUTEX','VMA_RW_MUTEX']
    header=z.read(prefix+'assets/java25/vma-source/ps5_mutex.hpp')
    assert header==(ROOT/'client/ports/vma/ps5_mutex.hpp').read_bytes()
    assert current_audit['locks']['source_sha256']==sha(header)
    expected_group['objects_sha256']=[current_hash]
   assert current_audit==expected_audit
   assert next(g for g in groups if g['name']==group)==expected_group
 assert b'ps5spvc'in fixture and b'SPVC_LIBRARY_NAME'in fixture
 assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.034/PPSA99874-full-local.zip')=='ee306f748fc37c171eec6edb1afaf5dfe59d12ef0cb57b56feb56bf8b3ba4a79'
 assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.037/PPSA99874-full-local.zip')=='ca7fb7e5b5c5c0bdcbd3ee92d5f58ed160652a50f107bf5f470a967a208f9ff0'
 assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.038/PPSA99874-full-local.zip')=='9f9a871285686b43e6abe12df66552a20f6022133646ac2452eb270dfcef93f5'
 assert b'ps5openal'in z.read('PPSA99874/assets/java25/classes/ClientStartup25.class')
 assert sha((ROOT/'dist/milestones/Client_Callbacks_OpenAL-01.000.026/PPSA99874-full-local.zip').read_bytes())=='e158f9fd76ce91f16091b6e9ee2c54a4cbaf11863f08bf77853204b6ef984d82'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.039/PPSA99874-full-local.zip')=='a034ae37f7d5c40026f0c7163b812aaeda6fb7811936b516ed1bd87baaad13a6'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.040/PPSA99874-full-local.zip')=='3950044b662911773ad5d262174b873d7bd48ab44e3e532086880430f94265b5'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.041/PPSA99874-full-local.zip')=='c252c4ce4f454025c6f0930e5c2e2395ff778a3cbe86f7cc71599a94f15fd98c'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.042/PPSA99874-full-local.zip')=='0bfa7f9d36b1882e36b9d53f79e4f025b197cf2ec1a022cc0aa8202c56a7c280'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.043/PPSA99874-full-local.zip')=='80094940d09e25479fae0dbb6106a6d65b11ffe3c6582ac234b6dae38fd2afe3'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.044/PPSA99874-full-local.zip')=='3a940fa1e3280b8f665f065ce5af50a00b1b9d2884b608a5a123f41666670443'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.045/PPSA99874-full-local.zip')=='df6978569980e567cf2ce269f29e2854dfebb7fc4df75d29709991a8e9aeeffd'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.046/PPSA99874-full-local.zip')=='c4c8a11e8fb54dcf2e1fbb91759261aacb940ec1c85485a40ab225b138afbdb9'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.053/PPSA99874-full-local.zip')=='cea95dcd5ef98f851a1f66e023a6e3323914d589df29cff6452f3f858cb1e65d'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.052/PPSA99874-full-local.zip')=='096b371c3927f0125922c591eb8c3033a206068ee6c2c3e39376736cd84f5a2e'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.051/PPSA99874-full-local.zip')=='a4108d61b82c8dae40f8f5babe99dce772dfb45790e21e110d57233f096cf80d'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.047/PPSA99874-full-local.zip')=='52cc98ea6b779f8bdf9b8a2b185a555f5e9bba5a970e33e55fd1bde3907f54f3'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.048/PPSA99874-full-local.zip')=='ede64e69349767fa6dcf425155e5b00210eb20ce48408c6c5c36c7e59179dca4'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.049/PPSA99874-full-local.zip')=='b8edd18c63a6572c483c7c6e203e772bf48c974c50b56a1199fe7d2151d11b40'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.050/PPSA99874-full-local.zip')=='ffc3b7d47132e7c426b42e1215033fd6649ca36f4a9c5c589bf44e59d935062f'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.055/PPSA99874-full-local.zip')=='33b22e7241dcaf2bd003badd4f7f5fbdbd2781bb51b229918de0e87a687e939c'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.056/PPSA99874-full-local.zip')=='587ca6053d121d6cfd5d49d695adc61ff5edb73c03c111e420a5f3ddf74794e1'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.057/PPSA99874-full-local.zip')=='8e7b84a3af448df8bc35f4660829ed9771191860fe075646d0b24badb20e4168'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.058/PPSA99874-full-local.zip')=='cd41f2fd2e98d455a1501e6e5b281894f8e5dba07396093e0cc501abec5a3cef'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.059/PPSA99874-full-local.zip')=='53ce7cc8ff6c83ebec57044951bc44707cbce1322c6188d5e3585745c4857c09'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.060/PPSA99874-full-local.zip')=='899252e805cff1031446cdcceaf6e44c331545601599d7e5b4e04c737502873c'
assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.061/PPSA99874-full-local.zip')=='d1a338b5e7c3d542bf5d4be974e3780c8ea3260ccd812939ea290dd755629429'


assert failure_hash(ROOT/'dist/failures/Client_Original_Startup-01.000.054/PPSA99874-full-local.zip')=='4f42a513d81e89777275368e0d5ad36178d0472827998e5a1a59260f7ac6cbbc'

accepted=ROOT/'dist/accepted/Client_Menu-01.000.062/PPSA99874-full-local.zip'
with accepted.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='26f31cc26bc960d3c7e35205c0280e8b83bc6e475a17b8383c778583cf952b88'

controls063=ROOT/'dist/accepted/Client_Controls-01.000.063/PPSA99874-full-local.zip'
with controls063.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='a1c62a8a6ccc8554c77ea3166633545fd08da6ca2b8e1ebffaf0c843677545f0'

with (ROOT/'dist/failures/Client_Original_Startup-01.000.064/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='87b09e6d64b86f2f0741b12405abf10e165256e2551b34d19fe2ac8ffac3f4c9'

with (ROOT/'dist/accepted/Client_World-01.000.065/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='a85c900937525c04cbae29c1a3f3018e3341e07f0ae6a85a14c733564ad3461a'

with (ROOT/'dist/accepted/Client_Controls-01.000.081/PPSA99874-full-local.zip').open('rb') as preserved:
 assert hashlib.file_digest(preserved,'sha256').hexdigest()=='3455e3fa1121eaaf6ae404ba7b4aa8ba9297f352ae46a76f5535f36fcdf182ad'
with (ROOT/'dist/accepted/Client_Playable-01.000.066/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='0b549873222b155fd21b4a441535390660598096f3f32c27081a963d00ea7802'

with (ROOT/'dist/accepted/Client_Audio-01.000.067/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='95f0af47359b48493afab6e9af23e81de1097796332c4b32e64d03123030397f'

with (ROOT/'dist/accepted/Client_GC-01.000.068/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='24e65f1020e97437b4ce0316e53f41aa1c56b8732bd9768663f2208ac7531efb'

with (ROOT/'dist/accepted/Client_Heap-01.000.069/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='59b20b2434071485c5211ff6b61bd1ccff3010ee71d6b219c0bd66f02a90fd11'

with (ROOT/'dist/accepted/Client_Distance-01.000.070/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='4ce1749199623943a695feb628d30bcafd9088f77e44b65b882d2b327af2d56c'

with (ROOT/'dist/accepted/Client_Retention-01.000.071/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='ea3fb4a81dc2401d0a4a3007e8c14790c42031aa8b717ce287c6ddf29ede9d2c'

with (ROOT/'dist/accepted/Client_G1-01.000.072/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='cd17b96dd9fcc5fb3cedb60b819dffbadcb37c4ebcd4b1ab83bf76d47b547f83'

with (ROOT/'dist/accepted/Client_Audio_Recovery-01.000.073/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='b88028c2c4d11b0a90332f04c20ee899eb7ced0434f09622d37d767a9d85f084'

with (ROOT/'dist/accepted/Client_Smooth_Audio-01.000.074/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='acba867efee8c503e4516a20ec4f2af69009a8ebcc647b370bd260dabed03326'

with (ROOT/'dist/accepted/Client_Launcher-01.000.075/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='660cbfba4095bd98e66d0afc2d32d0b054f6c43a738a4dfba8fe9cca441fabd6'

with (ROOT/'dist/accepted/Client_Branding-01.000.076/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='dcafb141baa6c9464108cb853e083575dc65eb1d560ca6dcae13cf1381330a9b'

with (ROOT/'dist/accepted/Client_Native_First-01.000.077/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='7cee18c872119b502d2d78427819ae5ad5f9715dada6289c2e75d969f08029eb'

with (ROOT/'dist/accepted/Client_Auth_Errors-01.000.078/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='fa13a7468de6735c478931cf9539d59c9f9358fe5035953c185ab8df6591755c'

with (ROOT/'dist/accepted/Client_Instances-01.000.079/PPSA99874-full-local.zip').open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()=='ee4238389de4c454d7b19173fa2613a4515d9c6e685ee083e3e70772b3deb6bf'

print('PASS146 actual package/CRC/signatures,launcher-only dependencies/zero bundled game JARs or asset objects,exact0126coreimage/rebuilt0125libnio+0130libnet/unchanged023otherlibrarybytes except verifiedGNUbuildIDs plus rebuilt0131HotSpot,359+4+4+15+1staged constructors/19real resident groups/actual036 SPIRV-Cross+139 custom-lock VMA+033 FreeType+031 STB+029 OSMesa/OpenGL+026 libffi+OpenAL+module overlay/paired C++ allocator/actual Main invocation bytecode/workdir/log config and preserved022/023 packages. Menu confirmation recorded separately;gameplay/stability validation pending. SHA256',sha(package.read_bytes()))

with (ROOT/'dist/published/ProsperoCraft-01.000.082/PPSA99874.zip').open('rb') as frozen082:
 assert hashlib.file_digest(frozen082,'sha256').hexdigest()=='ab49cad8977736be2be72230743232a270dba9bd17fa70a66b64a93c48230820'
