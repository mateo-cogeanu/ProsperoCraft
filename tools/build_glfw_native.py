#!/usr/bin/env python3
"""Build pinned genuine GLFW with a consumer SDL3 PS5 platform backend."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,tarfile,urllib.request
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime,host=False,offline=False):
 port=ROOT/'client/ports/glfw';pin=json.loads((port/'sources.json').read_text());cache=ROOT/'.tools/glfw-3.4.tar.gz'
 if not cache.exists():
  if offline:raise FileNotFoundError(cache)
  cache.write_bytes(urllib.request.urlopen(pin['upstream']['archive_url'],timeout=60).read())
 assert hashlib.sha256(cache.read_bytes()).hexdigest()==pin['upstream']['archive_sha256']
 out=ROOT/'build/glfw-native'/('host'if host else'ps5');out.mkdir(parents=True,exist_ok=True);source=out/'source';shutil.rmtree(source,ignore_errors=True);source.mkdir()
 with tarfile.open(cache)as tar:
  for m in tar.getmembers():
   m.name='/'.join(m.name.split('/')[1:])
   if m.name:tar.extract(m,source,filter='data')
 p=source/'src/null_init.c';text=p.read_text();assert text.count('*platform = null;')==1;p.write_text(text.replace('*platform = null;','*platform = null;\n    extern void _glfwConfigurePs5(_GLFWplatform*);\n    _glfwConfigurePs5(platform);'))
 p=source/'src/null_platform.h';text=p.read_text().replace('#define GLFW_NULL_CURSOR_STATE','#define GLFW_NULL_CURSOR_STATE void* ps5_cursor;').replace('typedef struct _GLFWwindowNull\n{','typedef struct _GLFWwindowNull\n{\n    void* ps5_window; void* ps5_preedit; void* ps5_ime; int ps5_rect[4];').replace('typedef struct _GLFWmonitorNull\n{','typedef struct _GLFWmonitorNull\n{\n    unsigned ps5_display;');p.write_text(text)
 p=source/'src/input.c';text=p.read_text();text=text.replace('switch (mode)\n    {','if(mode==208903){extern int ps5glfw_ime_get(_GLFWwindow*);return ps5glfw_ime_get(window); }\n    switch (mode)\n    {',1)
 start=text.index('GLFWAPI void glfwSetInputMode(');part=text[start:];part=part.replace('switch (mode)\n    {','if(mode==208903){extern void ps5glfw_ime_set(_GLFWwindow*,int);ps5glfw_ime_set(window,value);return;}\n    switch (mode)\n    {',1);p.write_text(text[:start]+part)
 units=['context','init','input','monitor','platform','vulkan','window','egl_context','osmesa_context','null_init','null_monitor','null_window','null_joystick','posix_thread','cocoa_time'if host else'posix_time']
 paths=[source/'src'/(u+'.c')for u in units]+[port/n for n in ['ps5_platform.c','vulkan_bridge.c','modules.c']]
 flags=['-std=c11','-O2','-fPIC','-I'+str(source/'src'),'-I'+str(ROOT/'.tools/PS5_Mesa/include')]
 if host:compiler='clang';flags+=['-DPS5_GLFW_HOST_TEST','-I/opt/homebrew/include','-fsanitize=address,undefined','-g']
 else:
  compiler=str(LLVM/'clang');sdk=ROOT/'.tools/graphics-sdk';flags+=['-target','x86_64-sie-ps5','-march=x86-64','-mno-avx','-mno-avx2','-mno-fma','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-I'+str(ROOT/'build/sdl-src/include')]
 objects=[]
 for p in paths:
  obj=out/(p.stem+'.o');subprocess.run([compiler,*flags,'-c',str(p),'-o',str(obj)],check=True);objects.append(obj)
 result=out/'glfw.o'
 if host:subprocess.run(['clang','-dynamiclib','-fsanitize=address,undefined',*map(str,objects),'-L/opt/homebrew/lib','-lSDL3','-o',str(out/'libps5glfw.dylib')],check=True)
 else:subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r',*map(str,objects),'-o',str(result)],check=True)
 audit={'upstream':pin['upstream'],'scope':pin['scope'],'target':'host ASan/UBSan with real SDL dummy window; Vulkan creation disabled only in host fixture'if host else'PS5 real SDL Vulkan window','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'local_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in port.iterdir()if p.is_file()},'console':'Pending26.2startup/menu/input/gameplay'}
 (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--host',action='store_true');p.add_argument('--offline',action='store_true');a=p.parse_args();print(build(a.runtime_workspace,a.host,a.offline))
