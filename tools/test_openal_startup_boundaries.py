#!/usr/bin/env python3
"""Exercise the real bounded scope helper and private pinned native ALC unit."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
from build_openal_startup_boundaries import build

ROOT=Path(__file__).resolve().parents[1]
library,audit=build(host=True)
with tempfile.TemporaryDirectory(prefix='openal-boundaries-')as temp:
 root=Path(temp)
 (root/'bounds.cpp').write_text(r'''
#include "startup_boundary.hpp"
#include <cassert>
#include <stdexcept>
#include <thread>
void run(){for(int i=0;i<100;i++){errno=EBUSY;{client_openal_boundary::Scope scope{"controlled",nullptr};assert(errno==EBUSY);}assert(errno==EBUSY);}}
int main(){try{client_openal_boundary::Scope s{"unwind",nullptr,0x1994,1,reinterpret_cast<void*>(0x1234)};throw std::runtime_error("control");}catch(const std::runtime_error&){}std::thread a{run},b{run},c{run};run();a.join();b.join();c.join();assert(client_openal_boundary::issued.load()==128);}
''')
 subprocess.run(['clang++','-std=c++17','-pthread','-fsanitize=address,undefined','-I'+str(ROOT/'client/ports/openal'),str(root/'bounds.cpp'),'-o',str(root/'bounds')],check=True)
 result=subprocess.run([str(root/'bounds')],capture_output=True,text=True,check=True,timeout=20)
 records=re.findall(r'PS5 OpenAL boundary id=(\d+) phase=(enter|scope-exit) api=(\S+)',result.stderr)
 assert len(records)==256
 for i in range(1,129):assert sorted(phase for n,phase,_ in records if int(n)==i)==['enter','scope-exit']
 assert 'api=unwind'in result.stderr and 'runtime error:'not in result.stderr
 assert 'param=0x1994 size=1 output=0x1234'in result.stderr
 (root/'calls.c').write_text(r'''
#include <dlfcn.h>
#include <stdio.h>
#include <assert.h>
#include <AL/alc.h>
int main(int argc,char **argv){
 void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);assert(lib);
 ALCdevice *(*openDevice)(const ALCchar*)=dlsym(lib,"alcOpenDevice");
 ALCenum (*getError)(ALCdevice*)=dlsym(lib,"alcGetError");
 const ALCchar *(*getString)(ALCdevice*,ALCenum)=dlsym(lib,"alcGetString");
 void (*getInteger)(ALCdevice*,ALCenum,ALCsizei,ALCint*)=dlsym(lib,"alcGetIntegerv");
 ALCcontext *(*createContext)(ALCdevice*,const ALCint*)=dlsym(lib,"alcCreateContext");
 ALCboolean (*makeCurrent)(ALCcontext*)=dlsym(lib,"alcMakeContextCurrent");
 void (*destroyContext)(ALCcontext*)=dlsym(lib,"alcDestroyContext");
 ALCboolean (*closeDevice)(ALCdevice*)=dlsym(lib,"alcCloseDevice");
 assert(openDevice&&getError&&getString&&getInteger&&createContext&&makeCurrent&&destroyContext&&closeDevice);
 ALCdevice *device=openDevice(NULL);assert(device);
 printf("open=1 error=%d name=%s\n",getError(device),getString(device,ALC_DEVICE_SPECIFIER));
 ALCint major=0;getInteger(device,ALC_MAJOR_VERSION,1,&major);printf("major=%d\n",major);
 ALCcontext *ctx=createContext(device,NULL);assert(ctx);printf("context=1 current=%d error=%d\n",makeCurrent(ctx),getError(device));
 makeCurrent(NULL);destroyContext(ctx);printf("close=%d\n",closeDevice(device));
}
''')
 subprocess.run(['clang','-I'+str(ROOT/'.tools/openal-soft-src/include'),str(root/'calls.c'),'-o',str(root/'calls')],check=True)
 results=[]
 for lib in [ROOT/'build/openal-host/libopenal.dylib',library]:
  env=dict(os.environ,ALSOFT_LOGLEVEL='0');env.pop('ALSOFT_LOGFILE',None)
  result=subprocess.run([str(root/'calls'),str(lib)],capture_output=True,text=True,check=True,timeout=30);results.append(result)
 assert results[0].stdout==results[1].stdout
 assert 'PS5 OpenAL boundary'not in results[0].stderr
 for name in audit['functions']:
  assert 'phase=enter api='+name in results[1].stderr and 'phase=scope-exit api='+name in results[1].stderr,name
 print(results[1].stdout.strip())
 (root/'hrtf.c').write_text(r'''
#include <dlfcn.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <sys/resource.h>
#include <AL/alc.h>
#include <AL/alext.h>
int main(int argc,char**argv){
 struct rlimit limit={0,0};setrlimit(RLIMIT_CORE,&limit);
 void *lib=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);assert(lib);
 ALCdevice *(*openDevice)(const ALCchar*)=dlsym(lib,"alcOpenDevice");
 ALCenum (*getError)(ALCdevice*)=dlsym(lib,"alcGetError");
 void (*getInteger)(ALCdevice*,ALCenum,ALCsizei,ALCint*)=dlsym(lib,"alcGetIntegerv");
 ALCcontext *(*createContext)(ALCdevice*,const ALCint*)=dlsym(lib,"alcCreateContext");
 void (*destroyContext)(ALCcontext*)=dlsym(lib,"alcDestroyContext");
 ALCboolean (*closeDevice)(ALCdevice*)=dlsym(lib,"alcCloseDevice");
 assert(openDevice&&getError&&getInteger&&createContext&&destroyContext&&closeDevice);
 ALCdevice *d=openDevice(NULL);assert(d);assert(chdir(argv[2])==0);
 int missing=strncmp(argv[3],"missing",7)==0;if(missing)assert(rmdir(argv[2])==0);
 ALCint n=-7;fprintf(stderr,"BEFORE HRTF count query\n");
 getInteger(d,ALC_NUM_HRTF_SPECIFIERS_SOFT,1,&n);printf("count=%d error=%d\n",n,getError(d));
 if(strcmp(argv[3],"missing")==0){ALCcontext *ctx=createContext(d,NULL);assert(ctx);destroyContext(ctx);puts("context=1");}
 assert(closeDevice(d));return 0;
}
''')
 subprocess.run(['clang','-I'+str(ROOT/'.tools/openal-soft-src/include'),str(root/'hrtf.c'),'-o',str(root/'hrtf')],check=True)
 env=dict(os.environ,ALSOFT_LOGLEVEL='3',HOME=str(root/'home'),XDG_DATA_HOME=str(root/'data'),XDG_DATA_DIRS=str(root/'system'))
 env.pop('ALSOFT_LOGFILE',None);env.pop('ALSOFT_LOCAL_PATH',None)
 outcomes=[]
 for index,lib in enumerate([ROOT/'build/openal-host/libopenal.dylib',library]):
  missing=root/f'missing{index}';missing.mkdir()
  result=subprocess.run([str(root/'hrtf'),str(lib),str(missing),'missing'],env=env,capture_output=True,text=True,timeout=30)
  outcomes.append(result)
 assert outcomes[0].returncode==-6 and 'current_path'in outcomes[0].stderr and 'filesystem_error'in outcomes[0].stderr
 assert outcomes[1].returncode==0 and 'count=0 error=0'in outcomes[1].stdout and 'context=1'in outcomes[1].stdout
 assert 'Skipping app-local data search: current_path failed'in outcomes[1].stderr
 assert 'api=alcGetIntegerv'in outcomes[1].stderr and 'param=0x1994 size=1'in outcomes[1].stderr
 valid=root/'valid';valid.mkdir();(valid/'enumeration-control.mhr').write_bytes(b'Enumeration filename fixture only;not HRTF decoding or mixing')
 valid_results=[]
 for lib in [ROOT/'build/openal-host/libopenal.dylib',library]:
  result=subprocess.run([str(root/'hrtf'),str(lib),str(valid),'valid'],env=env,capture_output=True,text=True,check=True,timeout=30)
  valid_results.append(result.stdout)
 assert valid_results[0]==valid_results[1] and 'count=1 error=0'in valid_results[1]
 explicit_env=dict(env,ALSOFT_LOCAL_PATH=str(valid))
 for index,lib in enumerate([ROOT/'build/openal-host/libopenal.dylib',library]):
  missing=root/f'explicit-missing{index}';missing.mkdir()
  result=subprocess.run([str(root/'hrtf'),str(lib),str(missing),'missing-enumerate'],env=explicit_env,capture_output=True,text=True,check=True,timeout=30)
  assert 'count=1 error=0'in result.stdout
  if index:
   assert 'App-local data search explicit path selected'in result.stderr
   assert 'Data directory iteration scope complete'in result.stderr
   assert 'App-local data search current_path begin'not in result.stderr
 # Preserve the upstream filename/type/case/symlink policy and sorted results.
 (valid/'second.MHR').write_bytes(b'filename fixture')
 (valid/'ignored.txt').write_text('not an HRTF')
 (valid/'directory.mhr').mkdir()
 (valid/'linked.mhr').symlink_to(valid/'enumeration-control.mhr')
 (valid/'directory-link.mhr').symlink_to(valid/'directory.mhr',target_is_directory=True)
 for lib in [ROOT/'build/openal-host/libopenal.dylib',library]:
  result=subprocess.run([str(root/'hrtf'),str(lib),str(valid),'valid'],env=env,capture_output=True,text=True,check=True,timeout=30)
  assert 'count=3 error=0'in result.stdout
 print('PASS original/private discovery agree on case-insensitive extension,regular-file symlink inclusion and directory/other-extension exclusion')
 print('PASS actual explicit local-data path:original and private OpenAL enumerate1filename/error0 even with currentdirectory removed;private path skips current_path and records real filesystem stages. No HRTF decoding/mixing or PS5 pass.')
 print('PASS actual HRTF count regression:original pinned library aborts on missing cwd;private repair returns0/error0 and creates context;valid local .mhr filename enumeration remains1 on both. Fixture does not validate HRTF decoding/mixing or PS5 cause.')
 print('PASS actual private pinned OpenAL ALC unit:all5body scope pairs,baseline device/error/name/version/context/current/close results unchanged;actual helper128scope cap,4threads,exception unwinding,errno under ASan/UBSan. PS5 behavior pending.')
