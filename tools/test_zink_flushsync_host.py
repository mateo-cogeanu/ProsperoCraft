#!/usr/bin/env python3
"""Actual macOS Zink GL plus native worker-name interposition; explicit local inputs."""
import argparse,json,os,platform,subprocess
from pathlib import Path
from host_toolchain import ROOT,executable

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',required=True);p.add_argument('--cxx',required=True);p.add_argument('--frontend',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
 if platform.system()!='Darwin':raise RuntimeError('Manual macOS lavapipe lane; no hosted/private cache fallback')
 cc=executable('clang',override=a.cc);cxx=executable('clang++',override=a.cxx);w=a.output_dir.resolve();w.mkdir(parents=True,exist_ok=True);frontend=a.frontend.resolve()
 subprocess.run([cc,'-std=c11','-O1','-g','-fsanitize=address,undefined','-I'+str(ROOT/'client/ports/zink'),'-I'+str(ROOT/'.tools/PS5_Mesa/include'),ROOT/'tools/fixtures/zink_frontend_host.c',frontend,'-Wl,-rpath,'+str(frontend.parent),'-o',w/'real-gl'],check=True)
 (w/'names.c').write_text(r'''
#include <pthread.h>
#include <string.h>
#include <unistd.h>
static int traced_name(const char*name){
 if(name&&(strstr(name,":zfq")||!strncmp(name,"zfq",3))){static const char tag[]="HOST_ZINK_FLUSH_WORKER_CREATED\n";write(2,tag,sizeof(tag)-1);}
 return pthread_setname_np(name);
}
__attribute__((used)) static const struct{const void*replacement;const void*original;} bind __attribute__((section("__DATA,__interpose")))={(const void*)traced_name,(const void*)pthread_setname_np};
''')
 subprocess.run([cc,'-dynamiclib',w/'names.c','-o',w/'names.dylib'],check=True)
 (w/'policy.cpp').write_text('#include "submit_policy.hpp"\n#include <unistd.h>\nint main(int argc,char**argv){if(argc!=3)return 99;if(argv[1][0]==\'1\'&&prospero_zink::enable_flushsync())return 98;execl(argv[2],argv[2],nullptr);return 97;}\n')
 subprocess.run([cxx,'-std=c++20','-I'+str(ROOT/'client/ports/zink'),w/'policy.cpp','-o',w/'policy'],check=True)
 asan=subprocess.check_output([cc,'-print-file-name=libclang_rt.asan_osx_dynamic.dylib'],text=True).strip()
 env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE='true',ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',UBSAN_OPTIONS='halt_on_error=1',DYLD_INSERT_LIBRARIES=asan+':'+str(w/'names.dylib'),MESA_SHADER_CACHE_DIR=str(w/'shader-cache'));env.pop('ZINK_DEBUG',None)
 outcomes={}
 for mode in ('0','1'):
  r=subprocess.run([w/'policy',mode,w/'real-gl'],env=env,capture_output=True,text=True,timeout=120);text=r.stdout+r.stderr;(w/('default.log'if mode=='0'else'flushsync.log')).write_text(text)
  assert r.returncode==0,text[-6000:]
  assert 'ERROR: AddressSanitizer'not in text and 'runtime error:'not in text,text[-6000:]
  count=text.count('HOST_ZINK_FLUSH_WORKER_CREATED');outcomes[mode]=count
  assert (count>0)==(mode=='0'),(mode,count,text[-6000:])
 (w/'audit.json').write_text(json.dumps({'scope':__doc__,'worker_names':outcomes,'actual':'Same genuine frontend clear/draw/guard/readback/thread/lifecycle workload succeeds in both processes; default creates zfq worker, actual candidate policy creates none','ps5':'NOT TESTED'},indent=2)+'\n')
 print('PASS actual candidate flushsync policy + genuine Zink GL: default zfq worker positive control, synchronous path zero zfq workers; native naming interposed only for observation; PS5 pending')
if __name__=='__main__':main()
