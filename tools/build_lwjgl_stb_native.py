#!/usr/bin/env python3
"""Build pinned original LWJGL STB JNI;actual codecs and generated JNI with isolated allocator pointers."""
from pathlib import Path
import argparse,json,hashlib,subprocess,urllib.request,concurrent.futures,shutil
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime,java_home,host=False,offline=False):
 # Canonicalize a shared verified source cache so its __FILE__ assertion strings
 # do not change when the same dependency is reached through a checkout symlink.
 lock=json.loads((ROOT/'client/ports/stb/native-sources.json').read_text());cache=(ROOT/'.tools/lwjgl-stb-src').resolve();cache.mkdir(exist_ok=True);out=ROOT/('build/lwjgl-stb-host'if host else'build/lwjgl-stb-ps5');out.mkdir(exist_ok=True)
 for row in lock['files']:
  p=cache/row['file']
  if not p.exists():
   if offline:raise FileNotFoundError(p)
   p.write_bytes(urllib.request.urlopen(row['url'],timeout=60).read())
  data=p.read_bytes();assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['sha256'],row['file']
 # A private header copy adapts only native platform macros;upstream cache is intact.
 include=out/'include';include.mkdir(exist_ok=True)
 shutil.copyfile(ROOT/'client/ports/lwjgl/PS5Config.h',include/'PS5Config.h')
 headers=java_home/'include'if host else runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base';sdk=runtime/'.tools/native-sdk/ps5-payload-sdk'
 flags=['-DLWJGL_MACOS','-fsanitize=undefined','-g']if host else['-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-march=x86-64','-msse2','-mno-avx','-mno-avx2','-mno-fma','-fno-stack-protector','-femulated-tls','-DLWJGL_PS5','-include',str(include/'PS5Config.h')]
 flags += ['-Dorg_lwjgl_'+name+'=clientstb_org_lwjgl_'+name for name in ['malloc','calloc','realloc','free','aligned_alloc','aligned_free']]
 def compile(row):
  obj=out/(row['file']+'.o');subprocess.run(['clang'if host else str(LLVM/'clang'),'-std=c11','-O2','-fPIC','-I'+str(include),'-I'+str(cache),'-I'+str(headers),'-I'+str(headers/('darwin'if host else'freebsd')),*flags,'-c',str(cache/row['file']),'-o',str(obj)],check=True);return obj
 units=[row for row in lock['files']if row['file'].startswith('org_lwjgl_')and row['file'].endswith('.c')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:objects=list(pool.map(compile,units))
 if host:
  library=out/'liblwjgl_stb.dylib';subprocess.run(['clang','-dynamiclib','-fsanitize=undefined','-undefined','dynamic_lookup',*map(str,objects),'-o',str(library)],check=True);return library
 merged=out/'lwjgl-stb.o';subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r',*map(str,objects),'-o',str(merged)],check=True)
 sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(merged)],text=True)
 assert '.tdata'not in sections and '.tbss'not in sections,'Unexpected native TLS sections in PS5 STB'
 nm=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only','--extern-only',str(merged)],text=True);exports=[line.split()[-1]for line in nm.splitlines()if len(line.split())==3 and line.split()[-1].startswith('Java_org_lwjgl_stb_')];assert exports
 audit={'sources':lock,'tls':'Compiler-managed emulated TLS;no native TLS segment','allocator':'Private clientstb_org_lwjgl_* pointer variables initialized by original LibSTB.setupMalloc;core globals unchanged','compile_units':len(units),'jni_exports':len(exports),'object_sha256':hashlib.sha256(merged.read_bytes()).hexdigest(),'scope':'Genuine original generated JNI dispatch;actual original embedded STB codecs/algorithms with private allocator pointers;PS5 behavior pending','console':'component only;PS5 acceptance pending'};(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PASS target STB JNI compile/link:',len(units),'units,',len(exports),'real exports;PS5 acceptance pending');return merged
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--java-home',type=Path,required=True);p.add_argument('--host',action='store_true');p.add_argument('--offline',action='store_true');a=p.parse_args();print(build(a.runtime_workspace,a.java_home,a.host,a.offline))
