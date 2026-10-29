#!/usr/bin/env python3
"""VMA's actual RAII lock guards with target hooks: contention, sharing and reuse."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>
#include <cstdio>
#include <chrono>
#include <new>
#include "ps5_mutex.hpp"
#define VMA_STATIC_VULKAN_FUNCTIONS 0
#define VMA_DYNAMIC_VULKAN_FUNCTIONS 0
#define VMA_IMPLEMENTATION
#include "vk_mem_alloc.h"
static_assert(sizeof(VMA_MUTEX)==sizeof(unsigned));
static_assert(sizeof(VMA_RW_MUTEX)==2*sizeof(unsigned));
static void until(auto predicate){auto end=std::chrono::steady_clock::now()+std::chrono::seconds(10);while(!predicate()){assert(std::chrono::steady_clock::now()<end);std::this_thread::yield();}}
int main(){
 VMA_MUTEX mutex;assert(mutex.TryLock());assert(!mutex.TryLock());mutex.Unlock();
 VMA_RW_MUTEX rw;assert(rw.TryLockRead());assert(rw.TryLockRead());assert(!rw.TryLockWrite());rw.UnlockRead();rw.UnlockRead();assert(rw.TryLockWrite());assert(!rw.TryLockRead()&&!rw.TryLockWrite());rw.UnlockWrite();
 {VmaMutexLock lock(mutex);}assert(mutex.TryLock());mutex.Unlock();
 {VmaMutexLockRead lock(rw,true);assert(!rw.TryLockWrite());}
 {VmaMutexLockWrite lock(rw,true);assert(!rw.TryLockRead());}
 // Existing readers drain; waiting writer blocks fresh readers and then enters.
 rw.LockRead();std::atomic<bool>entered=false,release=false;
 std::thread writer([&]{VmaMutexLockWrite lock(rw,true);entered=true;until([&]{return release.load();});});
 until([&]{if(!rw.TryLockRead())return true;rw.UnlockRead();return false;});
 assert(!entered);rw.UnlockRead();until([&]{return entered.load();});assert(!rw.TryLockRead());release=true;writer.join();
 // True parallel shared access, including reads held by another thread.
 rw.LockRead();entered=false;
 std::thread reader([&]{VmaMutexLockRead lock(rw,true);entered=true;});until([&]{return entered.load();});reader.join();rw.UnlockRead();
 long value=0,normal=0;std::atomic<int>writers=0,readers=0;std::vector<std::thread>threads;
 for(int i=0;i<8;i++)threads.emplace_back([&,i]{for(int j=0;j<10000;j++){
  if(i%2){VmaMutexLockWrite lock(rw,true);assert(writers.fetch_add(1)==0&&readers.load()==0);value++;assert(writers.fetch_sub(1)==1);}
  else{VmaMutexLockRead lock(rw,true);readers++;assert(!writers.load());assert(value>=0);readers--;}
  {VmaMutexLock lock(mutex);normal++;}
 }});
 for(auto&t:threads)t.join();assert(value==40000&&normal==80000);
 // Many simultaneously live locks and repeated address reuse need no lease pool.
 std::vector<VMA_RW_MUTEX>many(10000);for(auto&m:many){assert(m.TryLockWrite());m.UnlockWrite();}
 alignas(VMA_RW_MUTEX) unsigned char storage[sizeof(VMA_RW_MUTEX)];
 for(int i=0;i<10000;i++){auto*m=new(storage)VMA_RW_MUTEX;m->LockWrite();m->UnlockWrite();m->~RWMutex();}
 puts("PASS actual pinned VMA RAII guards: mutex exclusion, parallel readers, exclusive writers, try paths, queued-writer admission, 80000 contended operations, 10000 live locks and address reuse; ASan/UBSan");
}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(code);exe=d/'test'
 subprocess.run(['clang++','-std=c++20','-Wno-nullability-completeness','-O2','-pthread','-fsanitize=address,undefined','-I'+str(r/'client/ports/vma'),'-I'+str(r/'.tools/lwjgl-vma-src'),str(p),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True,timeout=40)
