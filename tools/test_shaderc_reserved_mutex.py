#!/usr/bin/env python3
"""Actual shaderc initialization lifecycle with reserved SDL mutexes under late-init refusal."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];w=r/'build/shaderc-mutex-host';w.mkdir(exist_ok=True)
# Apply the exact consumer patch to pristine pinned initializer sources.
src=r/'.tools/shaderc-src'
for n in ['libshaderc_util/include/libshaderc_util/compiler.h','libshaderc_util/src/compiler.cc']:
 p=w/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((src/n).read_bytes())
subprocess.run(['git','apply','--unsafe-paths','--directory='+str(w),str(r/'client/ports/shaderc/0003-reserved-init-mutex.patch')],check=True)
s=(w/'libshaderc_util/src/compiler.cc').read_text();a=s.index('unsigned int GlslangInitializer::initialize_count_');b=s.index('\nvoid Compiler::',a);actual=s[a:b]
code=r'''
#include <SDL3/SDL.h>
#include <pthread.h>
#include <atomic>
#include <thread>
#include <vector>
#include <mutex>
#include <type_traits>
#include <cassert>
#include <cerrno>
#include <cstdio>
#include "ps5_init_mutex.hpp"
static_assert(std::is_trivially_destructible_v<PS5ShaderInitMutex>);
static int deny,calls;static std::atomic<int> initializes,finalizes,active;static long counter;
extern "C" int prospero_sdl_mutex_preinit(void);
extern "C" int test_mutex_init(pthread_mutex_t*m,const pthread_mutexattr_t*a){calls++;return deny?ENOMEM:pthread_mutex_init(m,a);}
extern "C" bool SDL_SetError(const char*fmt,...){(void)fmt;return false;}
extern "C" void client_gpu_stage(const char*,int){assert(false);}
namespace glslang {bool InitializeProcess(){assert(active.fetch_add(1)==0);initializes++;return true;}void FinalizeProcess(){assert(active.fetch_sub(1)==1);finalizes++;}}
namespace shaderc_util {class GlslangInitializer {public:GlslangInitializer();~GlslangInitializer();private:static unsigned int initialize_count_;static PS5ShaderInitMutex* glslang_mutex_;};
'''+actual+r'''
}
int main(){assert(!prospero_sdl_mutex_preinit()&&calls==256);deny=1;
 {PS5ShaderInitMutex mutex;std::vector<std::thread> threads;for(int i=0;i<8;i++)threads.emplace_back([&]{for(int j=0;j<10000;j++){std::lock_guard<PS5ShaderInitMutex> lock(mutex);counter++;}});for(auto&t:threads)t.join();assert(counter==80000);}
 {shaderc_util::GlslangInitializer seed;assert(active==1&&initializes==1);std::vector<std::thread> threads;for(int i=0;i<8;i++)threads.emplace_back([]{for(int j=0;j<1000;j++){shaderc_util::GlslangInitializer next;assert(active==1);}});for(auto&t:threads)t.join();assert(finalizes==0);}assert(finalizes==1&&!active);
 for(int i=0;i<1000;i++){shaderc_util::GlslangInitializer next;assert(active==1);}assert(finalizes==1001&&initializes==1001&&!active&&calls==256);puts("PASS actual patched shaderc GlslangInitializer lifecycle + reserved native SDL:refcount/firstcall serialization,8000concurrent compiler lifetimes,1000finalize/reinitialize cycles,80000contended lock increments,no late pthreadmutexinit");}
'''
p=w/'test.cpp';p.write_text(code);subprocess.run(['clang++','-std=c++20','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include','-I'+str(r/'client/ports/shaderc'),str(p),str(r/'build/sdl-sync-reserve-host/SDL_sysmutex.o'),'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True,timeout=45)
