#!/usr/bin/env python3
"""Build pinned genuine OpenAL Soft with loopback/null;stage PS5 constructors."""
from pathlib import Path
import argparse,subprocess,json,hashlib,re,shutil,tarfile,io
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime,host=False,offline=False):
 port=ROOT/'client/ports/openal';pin=json.loads((port/'sources.json').read_text());source=ROOT/'.tools/openal-soft-src'
 if not source.exists():
  if offline:raise FileNotFoundError(source)
  subprocess.run(['git','clone','--depth','1','--branch',pin['tag'],pin['repository'],str(source)],check=True)
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==pin['commit'];subprocess.run(['git','-C',str(source),'diff','--exit-code','HEAD'],check=True)
 out=ROOT/('build/openal-host'if host else'build/openal-ps5');out.mkdir(exist_ok=True)
 # Export a private, coherent source tree: every Device user sees one layout.
 private=out/'source'
 if not private.exists():
  private.mkdir();archive=subprocess.check_output(['git','-C',str(source),'archive','HEAD'])
  with tarfile.open(fileobj=io.BytesIO(archive))as tar:tar.extractall(private,filter='data')
 device=private/'alc/device.h';text=(source/'alc/device.h').read_text()
 assert text.count('std::mutex StateLock;')==1
 device.write_text(text.replace('#include <mutex>','#include <mutex>\n#include "ps5_audio_mutex.hpp"').replace('std::mutex StateLock;','ps5audio::Mutex StateLock;'))
 shutil.copyfile(port/'ps5_audio_mutex.hpp',private/'alc/ps5_audio_mutex.hpp')
 hrtf=private/'core/hrtf.cpp';text=(source/'core/hrtf.cpp').read_text()
 for name in ['LoadedHrtfLock','EnumeratedHrtfLock']:
  assert text.count('auto '+name+' = std::mutex{};')==1
  text=text.replace('auto '+name+' = std::mutex{};','auto '+name+' = ps5audio::Mutex{};')
 hrtf.write_text('#include "ps5_audio_mutex.hpp"\n'+text)
 shutil.copyfile(port/'ps5_audio_mutex.hpp',private/'core/ps5_audio_mutex.hpp')
 helpers=private/'core/helpers.cpp';text=(source/'core/helpers.cpp').read_text();assert text.count('auto gSearchLock = std::mutex{};')==1
 helpers.write_text('#include "ps5_audio_mutex.hpp"\n'+text.replace('auto gSearchLock = std::mutex{};','auto gSearchLock = ps5audio::Mutex{};'))
 cache=out/'CMakeCache.txt'
 if cache.exists() and ('CMAKE_HOME_DIRECTORY:INTERNAL='+str(private))not in cache.read_text():cache.unlink()
 args=['cmake','-S',str(private),'-B',str(out),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DLIBTYPE='+('SHARED'if host else'STATIC'),'-DALSOFT_ENABLE_MODULES=OFF','-DALSOFT_UTILS=OFF','-DALSOFT_EXAMPLES=OFF','-DALSOFT_TESTS=OFF','-DALSOFT_EAX=OFF','-DALSOFT_EMBED_HRTF_DATA=OFF','-DALSOFT_BACKEND_WAVE=OFF','-DALSOFT_INSTALL=OFF','-DALSOFT_CPUEXT_SSE3=OFF','-DALSOFT_CPUEXT_SSE4_1=OFF','-DCMAKE_DISABLE_FIND_PACKAGE_PkgConfig=TRUE','-DCMAKE_DISABLE_FIND_PACKAGE_DBus1=TRUE']
 for b in ['PIPEWIRE','PULSEAUDIO','ALSA','OSS','SOLARIS','SNDIO','WASAPI','DSOUND','WINMM','PORTAUDIO','JACK','COREAUDIO','OBOE','OPENSL','SDL2','SDL3']:args+=['-DALSOFT_BACKEND_'+b+'=OFF']
 if host:args+=['-DCMAKE_SHARED_LINKER_FLAGS=-framework CoreFoundation']
 if not host:
  sdk=ROOT/'.tools/graphics-sdk';toolchain=out/'toolchain.cmake';toolchain.write_text('set(CMAKE_SYSTEM_NAME FreeBSD)\nset(CMAKE_SYSTEM_VERSION 9)\nset(CMAKE_SYSTEM_PROCESSOR x86_64)\nset(CMAKE_CROSSCOMPILING TRUE)\nset(CMAKE_C_COMPILER '+str(LLVM/'clang')+')\nset(CMAKE_CXX_COMPILER '+str(LLVM/'clang++')+')\nset(CMAKE_C_COMPILER_TARGET x86_64-sie-ps5)\nset(CMAKE_CXX_COMPILER_TARGET x86_64-sie-ps5)\nset(CMAKE_AR '+str(LLVM/'llvm-ar')+')\nset(CMAKE_RANLIB '+str(LLVM/'llvm-ranlib')+')\nset(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)\n')
  flags='-isysroot '+str(sdk)+' -isystem '+str(sdk/'target/include')+' -fvisibility-nodllstorageclass=default -march=x86-64 -msse2 -mno-avx -mno-avx2 -mno-fma -fno-stack-protector -femulated-tls -fPIC'
  args+=['-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_C_FLAGS='+flags,'-DCMAKE_CXX_FLAGS=-isystem '+str(sdk/'target/include/c++/v1')+' '+flags+' -fexceptions -frtti']
 subprocess.run(args,check=True);subprocess.run(['cmake','--build',str(out),'--target','OpenAL','-j','4'],check=True)
 if host:return out/'libopenal.dylib'
 raw=out/'openal-raw.o';subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r','--whole-archive',str(out/'libopenal.a'),'--no-whole-archive','-o',str(raw)],check=True)
 bindings=json.loads((ROOT/'build/client-gpu/audit.json').read_text())['graphics_bindings'];mapping=out/'provider-bindings.txt';mapping.write_text(''.join(k+' '+v+'\n'for k,v in sorted(bindings.items())))
 obj=out/'openal.o';subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(mapping),str(raw),str(obj)],check=True)
 sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(obj)],text=True);ctors=sorted(set(re.findall(r'\]\s+(\.(?:init_array|ctors)(?:\.\S+)?)\s',sections)));opts=[]
 for name in ctors:
  suffix=name.rsplit('.',1)[-1];priority=(65535-int(suffix)if name.startswith('.ctors.')else int(suffix))if suffix.isdigit()else 65535
  opts+=['--rename-section',name+'=.data.rel.ro.clientopenal.init_array.'+f'{priority:05d}'+name]
 if opts:subprocess.run([str(LLVM/'llvm-objcopy'),*opts,str(obj)],check=True)
 headers=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base';life=out/'lifecycle.o'
 subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-I'+str(headers),'-I'+str(headers/'freebsd'),'-c',str(port/'lifecycle.c'),'-o',str(life)],check=True)
 audit={'sources':pin,'data_search_mutex':{'original_source_sha256':hashlib.sha256((source/'core/helpers.cpp').read_bytes()).hexdigest(),'private_source_sha256':hashlib.sha256(helpers.read_bytes()).hexdigest(),'policy':'Only data-discovery gSearchLock uses allocation-free mutex;search paths/ownership unchanged'},'hrtf_mutex':{'original_source_sha256':hashlib.sha256((source/'core/hrtf.cpp').read_bytes()).hexdigest(),'patched_source_sha256':hashlib.sha256(hrtf.read_bytes()).hexdigest(),'mutex_header_sha256':hashlib.sha256((port/'ps5_audio_mutex.hpp').read_bytes()).hexdigest(),'policy':'Only LoadedHrtfLock/EnumeratedHrtfLock use allocation-free mutex;HRTF discovery/data unchanged'},'device_state_mutex':{'original_header_sha256':hashlib.sha256((source/'alc/device.h').read_bytes()).hexdigest(),'patched_header_sha256':hashlib.sha256(device.read_bytes()).hexdigest(),'mutex_header_sha256':hashlib.sha256((port/'ps5_audio_mutex.hpp').read_bytes()).hexdigest(),'policy':'All OpenAL native units compiled from same private tree with allocation-free StateLock;other Device locks unchanged'},'objects_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [obj,life]},'constructor_sections':ctors,'bindings':bindings,'scope':'Actual OpenAL Soft with upstream null and loopback backends;no speaker/capture support claim','target':'x86_64-sie-ps5/SSE2;real C++ exceptions/RTTI;no automatic module constructors','lifecycle_sha256':hashlib.sha256((port/'lifecycle.c').read_bytes()).hexdigest(),'console':'pending actual PS5 ALC/AL mixer/cleanup'};(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');return obj,life,audit
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--host',action='store_true');p.add_argument('--offline',action='store_true');a=p.parse_args();print(build(a.runtime_workspace,a.host,a.offline))
