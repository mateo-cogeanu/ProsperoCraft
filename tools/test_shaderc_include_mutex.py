#!/usr/bin/env python3
"""Real pinned CountingIncluder lifetime/concurrency with refused kernel mutexes."""
from pathlib import Path
import subprocess,tempfile,shutil
r=Path(__file__).resolve().parents[1];src=r/'.tools/shaderc-src'
code=r'''
#include <pthread.h>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <thread>
#include <vector>
#include <stdexcept>
#include <cstring>
static std::atomic<int> inits{0},destroys{0},locks{0};
static int refused_init(pthread_mutex_t*,const pthread_mutexattr_t*){++inits;return ENOMEM;}
static int observed_destroy(pthread_mutex_t*){++destroys;return EINVAL;}
static int observed_lock(pthread_mutex_t*){++locks;return EINVAL;}
static int observed_unlock(pthread_mutex_t*){return EINVAL;}
#define pthread_mutex_init refused_init
#define pthread_mutex_destroy observed_destroy
#define pthread_mutex_lock observed_lock
#define pthread_mutex_unlock observed_unlock
#include "libshaderc_util/counting_includer.h"
#undef pthread_mutex_init
#undef pthread_mutex_destroy
#undef pthread_mutex_lock
#undef pthread_mutex_unlock
class Fixture final:public shaderc_util::CountingIncluder {
public:
 int total=0,active=0,max_active=0;bool fail=false;
 glslang::TShader::Includer::IncludeResult* include_delegate(const char*,const char*,IncludeType,size_t)override{
  ++active;if(active>max_active)max_active=active;
  if(fail){--active;throw std::runtime_error("fixture");}
  ++total;--active;return nullptr;
 }
 void release_delegate(glslang::TShader::Includer::IncludeResult*)override{}
};
int main(){
 for(int i=0;i<1000;i++){alignas(Fixture) unsigned char storage[sizeof(Fixture)];memset(storage,0xa5,sizeof(storage));auto*f=new(storage)Fixture;
#ifdef __PROSPERO__
  f->fail=true;try{f->includeLocal("a","b",0);assert(false);}catch(const std::runtime_error&){}f->fail=false;
#endif
  f->includeSystem("a","b",0);assert(f->num_include_directives()>0);f->~Fixture();}
#ifdef __PROSPERO__
 assert(inits==0&&destroys==0&&locks==0);
 Fixture f;std::vector<std::thread> workers;
 for(int t=0;t<8;t++)workers.emplace_back([&]{for(int i=0;i<10000;i++)f.includeLocal("a","b",0);});
 for(auto&t:workers)t.join();assert(f.total==80000&&f.max_active==1&&f.num_include_directives()==80000);
 puts("PASS actual patched CountingIncluder:1000 poisonedstorage/failure/unwind/reuse lifetimes;80000 concurrent includes serialized;zero native mutex init/lock/destroy;ASan/UBSan");
#else
 assert(inits==1000&&destroys==1000&&locks==1000);
 puts("PASS original failure reproduced:1000ignored ENOMEM initializations still lock/destroy poisoned mutex storage");
#endif
}
'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d).resolve()
 for name in ['libshaderc_util/include/libshaderc_util/counting_includer.h','libshaderc_util/include/libshaderc_util/mutex.h']:
  p=w/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/name,p)
 (w/'check.cpp').write_text(code)
 common=['clang++','-std=c++17','-pthread','-fsanitize=address,undefined','-I'+str(w/'libshaderc_util/include'),'-I'+str(src/'third_party/glslang'),'-I'+str(r/'client/ports/shaderc'),str(w/'check.cpp')]
 subprocess.run([*common,'-o',str(w/'old')],check=True);subprocess.run([str(w/'old')],check=True)
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(w),str(r/'client/ports/shaderc/0005-counting-includer-owned-mutex.patch')],check=True)
 subprocess.run([*common,'-D__PROSPERO__','-o',str(w/'new')],check=True);subprocess.run([str(w/'new')],check=True,timeout=30)
