#!/usr/bin/env python3
"""Exercise real reserved workers, exhausted leases and late thread-creation denial."""
import tempfile
from pathlib import Path
from host_toolchain import executable
import subprocess
ROOT=Path(__file__).resolve().parents[1];host_work=tempfile.TemporaryDirectory(prefix='prospero-workers-');out=Path(host_work.name).resolve()
(out/'check.cpp').write_text(r'''
#include <pthread.h>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <cstdlib>
static std::atomic<int> creates{0};static bool deny=false;static int failAt=0;
int test_create(pthread_t* t,const pthread_attr_t* a,void*(*fn)(void*),void* p){int n=++creates;return (deny||n==failAt)?EAGAIN:pthread_create(t,a,fn,p);}
#define pthread_create test_create
#include "ps5_mixer_workers.hpp"
#undef pthread_create
static ps5audio::MixerWorkers pool;
struct Job {std::atomic<bool> ready{false},go{false};std::atomic<int> count{0};};
static void blocked(void* p){auto& job=*static_cast<Job*>(p);job.ready=true;while(!job.go.load())ps5audio::MixerWorkers::pause();++job.count;}
static void quick(void* p){++*static_cast<std::atomic<int>*>(p);}
int main(int argc,char**){
 if(argc>1){if(argc>2)failAt=2;else deny=true;assert(pool.preinit()==EAGAIN);assert(pool.preinit()==EAGAIN);assert(creates==(argc>2?2:1));assert(!pool.assign(quick,nullptr));return 0;}
 assert(!pool.assign(quick,nullptr));assert(pool.preinit()==0);assert(creates==2);deny=true;assert(pool.preinit()==0);assert(creates==2);
 Job a,b;auto* x=pool.assign(blocked,&a);auto* y=pool.assign(blocked,&b);assert(x&&y&&x!=y);assert(!pool.assign(blocked,&a));
 while(!a.ready||!b.ready)ps5audio::MixerWorkers::pause();a.go=true;b.go=true;pool.wait_release(x);pool.wait_release(y);assert(a.count==1&&b.count==1);
 std::atomic<int> completed{0};for(int i=0;i<1000;++i){auto* slot=pool.assign(quick,&completed);assert(slot);pool.wait_release(slot);assert(completed==i+1);}assert(creates==2);
}
''')
subprocess.run([executable('clang++', env='CXX'),'-std=c++17','-O2','-fsanitize=address,undefined','-pthread','-I'+str(ROOT/'client/ports/openal'),str(out/'check.cpp'),'-o',str(out/'check')],check=True)
for args in [[],['fail'],['fail','partial']]:subprocess.run([str(out/'check'),*args],check=True,timeout=20)
print('PASS reserved real workers: initialization/failure/idempotence, two concurrent leases, exhaustion, completion/reuse x1000 with late creation denied; ASan/UBSan')
