#!/usr/bin/env python3
"""Actual184 Java GL workload on macOS lavapipe, with modeled launcher barrier.

No native launcher/UI, VideoOut, LoadExec, account or Minecraft behavior is
established by this test. The packaged Java fixture is executed unchanged.
"""
import argparse,json,os,platform,subprocess,hashlib
from pathlib import Path
from host_toolchain import ROOT,java_home,executable,jni_flags

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--graphics-config',type=Path,required=True);p.add_argument('--cc',required=True);p.add_argument('--java-home',type=Path);p.add_argument('--host-vulkan',type=Path,required=True);p.add_argument('--fixture',type=Path,default=ROOT/'client/zink_handoff/ClientStartup25.java');p.add_argument('--output-dir',type=Path,default=ROOT/'build/zink-handoff-host')
 a=p.parse_args()
 if platform.system()!='Darwin':raise RuntimeError('macOS/lavapipe research test only')
 jdk=java_home(a.java_home);cc=executable('clang',override=a.cc);cfg=json.loads(a.graphics_config.read_text())
 frontend=Path(cfg['frontend']);glfw=Path(cfg['glfw-library']);core=Path(cfg['core-library']);opengl=Path(cfg['opengl-library']);work=a.output_dir.resolve();work.mkdir(parents=True,exist_ok=True)
 for file in (frontend,glfw):
  audit=json.loads(file.with_suffix('.json').read_text())if file==frontend else json.loads(file.with_name('audit.json').read_text())
  assert sha(file)==audit['output_sha256']
 lib=work/'libhandoff-host.dylib';subprocess.run([cc,'-dynamiclib',*jni_flags(jdk),str(ROOT/'tools/fixtures/zink_handoff_host.c'),'-o',str(lib)],check=True)
 loader_pin=json.loads((ROOT/'client/ports/sdl/host-loader-source.json').read_text())
 loader_source=ROOT/'.tools/lwjgl-native-src'/loader_pin['file']
 assert sha(loader_source)==loader_pin['sha256'],'Pinned host JNI dynamic-link source mismatch'
 loader=work/'libhost-loader.dylib'
 subprocess.run([cc,'-dynamiclib','-DLWJGL_MACOS','-I'+str(ROOT/'.tools/lwjgl-native-src'),*jni_flags(jdk),str(loader_source),'-o',str(loader)],check=True)
 for name,target in [('ps5zink',frontend),('ps5clientgpu',a.host_vulkan),('libps5clientgpu.so',a.host_vulkan),('libps5glfw.so',glfw),('liblwjgl_opengl.so',opengl)]:
  dest=work/name
  if dest.is_symlink():dest.unlink()
  if dest.exists():raise FileExistsError(dest)
  dest.symlink_to(target.resolve())
 # Only exact locked parent modules; no arbitrary game cache scan.
 lock=json.loads((ROOT/'client/26.3.lock.json').read_text())
 parents=[]
 for row in lock['artifacts']:
  if row['id'].startswith(('org.lwjgl:','org.jspecify:')) and ':natives-' not in row['id']:
   file=Path(cfg['parent-dir'])/row['file'];assert sha(file)==row['sha256'];parents.append(file)
 cp=os.pathsep.join(map(str,[work,ROOT/'build/client-ports/lwjgl-modules/lwjgl-3.4.3-ps5-modules.jar',ROOT/'build/client-ports/lwjgl/lwjgl-3.4.3-ps5-platform.jar',Path(cfg['glfw-binding']),*parents]))
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(work),str(a.fixture.resolve()),str(ROOT/'tools/fixtures/ZinkHandoffHost25.java')],check=True)
 asan=subprocess.check_output([cc,'-print-file-name=libclang_rt.asan_osx_dynamic.dylib'],text=True).strip()
 env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE='true',SDL_VIDEODRIVER='dummy',DYLD_INSERT_LIBRARIES=asan,DYLD_LIBRARY_PATH=str(work)+os.pathsep+str(frontend.parent),MESA_SHADER_CACHE_DIR=str(work/'shader-cache'),ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',UBSAN_OPTIONS='halt_on_error=1')
 command=[jdk/'bin/java','-Xint','-Xcheck:jni','-Xverify:all','--enable-native-access=ALL-UNNAMED','--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED','-Djava.library.path='+str(opengl.parent),'-cp',cp,'ZinkHandoffHost25',lib,core,loader]
 for mode in ('reject','resume','positive'):
  env['ZINK_HANDOFF_HOST_MODE']=mode
  result=subprocess.run(list(map(str,[*command,mode])),env=env,cwd=work,capture_output=True,text=True,timeout=90);text=result.stdout+result.stderr;(work/(mode+'.log')).write_text(text)
  assert result.returncode==0 and 'PASS184'in text,text[-5000:]
  assert not any(s in text for s in ('WARNING in native method','FATAL ERROR in native method','ERROR: AddressSanitizer','runtime error:')),text[-5000:]
  print('PASS184',mode)
 (work/'audit.json').write_text(json.dumps({'fixture_sha256':sha(a.fixture.resolve()),'frontend_sha256':sha(frontend),'glfw_sha256':sha(glfw),'scope':__doc__,'results':['reject','resume','positive'],'ps5':'NOT TESTED'},indent=2)+'\n')
if __name__=='__main__':main()
