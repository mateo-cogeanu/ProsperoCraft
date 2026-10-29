#!/usr/bin/env python3
"""Build pinned original LWJGL JNI and VMA implementation with private allocator slots."""
from pathlib import Path
import argparse,json,hashlib,subprocess,urllib.request,shutil
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime,java_home,host=False,offline=False,ps5_locks=False):
 lock=json.loads((ROOT/'client/ports/vma/native-sources.json').read_text());cache=ROOT/'.tools/lwjgl-vma-src';cache.mkdir(exist_ok=True);out=ROOT/('build/lwjgl-vma-host'if host else'build/lwjgl-vma-ps5');out.mkdir(exist_ok=True)
 for row in lock['files']:
  p=cache/row['file'];p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   if offline:raise FileNotFoundError(p)
   p.write_bytes(urllib.request.urlopen(row['url'],timeout=60).read())
  assert p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['file']
 include=out/'include';include.mkdir(exist_ok=True);shutil.copyfile(ROOT/'client/ports/lwjgl/PS5Config.h',include/'PS5Config.h')
 headers=java_home/'include'if host else runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base';sdk=ROOT/'.tools/graphics-sdk'
 flags=['-DLWJGL_MACOS','-fsanitize=undefined','-g']if host else['-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include/c++/v1'),'-isystem',str(sdk/'target/include'),'-march=x86-64','-msse2','-mno-avx','-mno-avx2','-mno-fma','-fno-stack-protector','-femulated-tls','-DLWJGL_PS5','-include',str(include/'PS5Config.h')]
 flags += ['-Dorg_lwjgl_'+n+'=clientvma_org_lwjgl_'+n for n in ['malloc','calloc','realloc','free','aligned_alloc','aligned_free']]
 locks=ROOT/'client/ports/vma/ps5_mutex.hpp'
 if not host or ps5_locks:flags += ['-include',str(locks)]
 objects=[]
 for row in lock['files']:
  if not row['file'].endswith('.cpp'):continue
  obj=out/(row['file']+'.o');subprocess.run(['clang++'if host else str(LLVM/'clang++'),'-std=c++17','-O2','-DNDEBUG','-fno-exceptions','-fno-rtti','-fPIC','-I'+str(include),'-I'+str(cache),'-I'+str(headers),'-I'+str(headers/('darwin'if host else'freebsd')),*flags,'-c',str(cache/row['file']),'-o',str(obj)],check=True);objects.append(obj)
 if host:
  library=out/'liblwjgl_vma.dylib';subprocess.run(['clang++','-dynamiclib','-fsanitize=undefined','-undefined','dynamic_lookup',*map(str,objects),'-o',str(library)],check=True);return library
 raw=out/'lwjgl-vma-raw.o';subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r',*map(str,objects),'-o',str(raw)],check=True)
 merged=out/'lwjgl-vma.o';subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(ROOT/'build/client-gpu/sdl-bindings.txt'),str(raw),str(merged)],check=True)
 sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(merged)],text=True);assert '.tdata'not in sections and '.tbss'not in sections
 names=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only','--extern-only',str(merged)],text=True);exports=[l.split()[-1]for l in names.splitlines()if len(l.split())==3 and l.split()[-1].startswith('Java_org_lwjgl_util_vma_')];assert len(exports)>50
 audit={'sources':lock,'compile_units':len(objects),'jni_exports':len(exports),'object_sha256':hashlib.sha256(merged.read_bytes()).hexdigest(),'allocator':'Private clientvma_org_lwjgl_* slots initialized by original LibVma.setupMalloc;existing scoped graphics C++/thread providers;JVM/core globals unchanged','implementation':'Original VMA3.4.0 and original generated LWJGL3.4.3 JNI;explicit Vulkan function table,no static/dynamic loader lookup','locks':{'hooks':['VMA_MUTEX','VMA_RW_MUTEX'],'source_sha256':hashlib.sha256(locks.read_bytes()).hexdigest(),'policy':'Inline allocation-free nonrecursive mutex/read-write state;acquire/release,writer preference,64spin/50us native sleep contention;no global lease limit'},'tls':'Compiler emulated TLS;no native TLS segments','scope':'Actual allocator/JNI compiled;PS5 GPU allocation/map/flush/transfer/free acceptance pending'};(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PASS target genuine VMA/JNI',len(exports),'exports',audit['object_sha256']);return merged
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--java-home',type=Path,required=True);p.add_argument('--host',action='store_true');p.add_argument('--offline',action='store_true');p.add_argument('--ps5-locks',action='store_true',help='Exercise target custom lock hooks in the host VMA build');a=p.parse_args();print(build(a.runtime_workspace,a.java_home,a.host,a.offline,a.ps5_locks))
