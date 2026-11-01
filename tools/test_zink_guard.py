#!/usr/bin/env python3
"""Actual frontend guard + existing graphics mutex lease pool under late refusal."""
import os,subprocess,tempfile
from pathlib import Path
from host_toolchain import ROOT,executable

def main():
 cc=executable('clang',env='CC')
 text=(ROOT/'client/ports/zink/frontend.c').read_text()
 body=text.split('/* BEGIN FRONTEND GUARD:')[1].split('/* END FRONTEND GUARD */')[0]
 body=body[body.index('static pthread_mutex_t guard'):].replace('__attribute__((constructor))','')
 with tempfile.TemporaryDirectory(prefix='prospero-zink-guard-')as folder:
  w=Path(folder);(w/'actual_guard.inc').write_text(body)
  (w/'check.c').write_text(r'''
#define _GNU_SOURCE
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <errno.h>
#include <assert.h>
#include <string.h>
static atomic_uint lease_guard;
static int deny,init_calls,lock_error;
static void lock_entries(void){while(atomic_exchange_explicit(&lease_guard,1,memory_order_acquire)){};}
static void unlock_entries(void){atomic_store_explicit(&lease_guard,0,memory_order_release);}
static int host_init(pthread_mutex_t*p,const pthread_mutexattr_t*a){init_calls++;return deny?ENOMEM:pthread_mutex_init(p,a);}
#define pthread_mutex_init host_init
#include "mutex_reserve.inc"
#undef pthread_mutex_init
static int guard_lock(pthread_mutex_t*p){return lock_error?lock_error:clientgpu_mutex_lock(p);}
#define pthread_mutex_init clientgpu_mutex_init
#define pthread_mutex_lock guard_lock
#include "actual_guard.inc"
#undef pthread_mutex_init
#undef pthread_mutex_lock
static unsigned increments;
static void* worker(void*p){(void)p;for(int i=0;i<10000;i++){assert(!frontend_guard_lock());increments++;assert(!clientgpu_mutex_unlock(&guard));}return NULL;}
int main(int argc,char**argv){
 assert(argc==2);assert(guard_init_result==EAGAIN);assert(frontend_guard_lock()==EAGAIN);
 if(!strcmp(argv[1],"unprepared")){
  frontend_guard_init();assert(guard_init_result==ENOMEM);assert(frontend_guard_lock()==ENOMEM);return 0;
 }
 assert(!clientgpu_mutex_preinit());int calls=init_calls;deny=1;
 if(!strcmp(argv[1],"exhausted")){
  pthread_mutex_t leased[256];for(unsigned i=0;i<256;i++)assert(!clientgpu_mutex_init(&leased[i],NULL));
  frontend_guard_init();assert(guard_init_result==ENOMEM);assert(frontend_guard_lock()==ENOMEM);assert(init_calls==calls);return 0;
 }
 // Old statically-initialized owner is not mapped to a reserved native mutex.
 pthread_mutex_t old=PTHREAD_MUTEX_INITIALIZER;assert(mutex_find(&old)==&old);assert(host_init(&old,NULL)==ENOMEM);
 frontend_guard_init();assert(!guard_init_result&&mutex_find(&guard)!=&guard);calls=init_calls;
 pthread_t threads[8];for(unsigned i=0;i<8;i++)assert(!pthread_create(&threads[i],NULL,worker,NULL));for(unsigned i=0;i<8;i++)assert(!pthread_join(threads[i],NULL));assert(increments==80000&&init_calls==calls);
 lock_error=EAGAIN;assert(frontend_guard_lock()==EAGAIN);lock_error=ENOMEM;assert(frontend_guard_lock()==ENOMEM);lock_error=0;assert(!frontend_guard_lock());assert(!clientgpu_mutex_unlock(&guard));
 puts("PASS actual staged frontend guard: real reserved mutex lease,80000contended increments, late native init denied, exact lock/init error propagation");
}
''')
  subprocess.run([cc,'-D_POSIX_C_SOURCE=200809L','-include',str(ROOT/'tools/fixtures/pthread_timedlock_host.h'),'-std=c11','-pthread','-fsanitize=address,undefined','-I'+str(ROOT/'client/gpu'),'-I'+str(w),str(w/'check.c'),'-o',str(w/'check')],check=True)
  for mode in ('normal','unprepared','exhausted'):subprocess.run([w/'check',mode],check=True,timeout=30,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS actual frontend guard reserve exhaustion/unprepared controls; no PS5 causal/pass inference')
if __name__=='__main__':main()
