#!/usr/bin/env python3
"""Actual Mesa C11 condition wrapper and native reserve with late init refusal."""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1];w=r/'build/radv-condition-host';w.mkdir(exist_ok=True)
names=['init','destroy','signal','broadcast','wait','timedwait'];flags=['clang','-std=c11','-fsanitize=address,undefined','-pthread','-DHAVE_PTHREAD','-DHAVE_STRUCT_TIMESPEC','-I'+str(r/'.tools/PS5_Mesa/src')]
subprocess.run([*flags,*['-Dpthread_cond_'+n+'=clientgpu_cond_'+n for n in names],'-c',str(r/'.tools/PS5_Mesa/src/c11/impl/threads_posix.c'),'-o',str(w/'mesa-threads.o')],check=True)
(w/'clock-host.h').write_text('#include <pthread.h>\n#include <time.h>\nint test_native_condattr_setclock(pthread_condattr_t*,clockid_t);\n')
subprocess.run([*flags,'-include',str(w/'clock-host.h'),'-Dpthread_condattr_setclock=test_native_condattr_setclock','-Dpthread_cond_init=test_native_cond_init','-c',str(r/'client/gpu/condition_reserve.c'),'-o',str(w/'reserve.o')],check=True)
s=r'''
#include "c11/threads.h"
#include <assert.h>
#include <stdatomic.h>
#include <stdio.h>
int clientgpu_condition_preinit(void);
int clientgpu_cond_signal(pthread_cond_t*);int clientgpu_cond_destroy(pthread_cond_t*);
static int denied,calls;static atomic_int ready,awakened;static int go,value;static cnd_t cond;static mtx_t mutex;
// Host clock stub initializes only the unused monotonic reserve; realtime waits tested here.
int test_native_condattr_setclock(pthread_condattr_t*a,clockid_t c){(void)a;return c==CLOCK_MONOTONIC?0:EINVAL;}
int test_native_cond_init(pthread_cond_t*c,const pthread_condattr_t*a){calls++;return denied?ENOMEM:pthread_cond_init(c,a);}
static int worker(void*x){(void)x;assert(mtx_lock(&mutex)==thrd_success);atomic_fetch_add(&ready,1);while(!go)assert(cnd_wait(&cond,&mutex)==thrd_success);assert(value==42);atomic_fetch_add(&awakened,1);assert(mtx_unlock(&mutex)==thrd_success);return 0;}
int main(void){assert(cnd_init(&cond)==thrd_error&&calls==0);denied=1;assert(clientgpu_condition_preinit()==ENOMEM&&calls==1);denied=0;assert(!clientgpu_condition_preinit()&&calls==257);denied=1;cnd_t all[128],extra;for(int i=0;i<128;i++)assert(cnd_init(&all[i])==thrd_success);assert(cnd_init(&extra)==thrd_error);assert(cnd_init(&all[0])==thrd_error);for(int i=0;i<128;i++)cnd_destroy(&all[i]);assert(cnd_init(&cond)==thrd_success);assert(mtx_init(&mutex,mtx_plain)==thrd_success);assert(mtx_lock(&mutex)==thrd_success);struct timespec t;clock_gettime(CLOCK_REALTIME,&t);t.tv_nsec+=1000000;if(t.tv_nsec>=1000000000){t.tv_nsec-=1000000000;t.tv_sec++;}assert(cnd_timedwait(&cond,&mutex,&t)==thrd_timedout);assert(mtx_unlock(&mutex)==thrd_success);thrd_t threads[4];for(int i=0;i<4;i++)assert(thrd_create(&threads[i],worker,0)==thrd_success);while(atomic_load(&ready)<4){}assert(mtx_lock(&mutex)==thrd_success);value=42;go=1;assert(cnd_broadcast(&cond)==thrd_success);assert(mtx_unlock(&mutex)==thrd_success);for(int i=0;i<4;i++)thrd_join(threads[i],0);assert(awakened==4);
 go=0;atomic_store(&ready,0);assert(thrd_create(&threads[0],worker,0)==thrd_success);while(!ready){}assert(mtx_lock(&mutex)==thrd_success);go=1;assert(cnd_signal(&cond)==thrd_success);assert(mtx_unlock(&mutex)==thrd_success);thrd_join(threads[0],0);cnd_destroy(&cond);mtx_destroy(&mutex);
 for(int i=0;i<10000;i++){assert(cnd_init(&cond)==thrd_success);assert(cnd_signal(&cond)==thrd_success);cnd_destroy(&cond);}assert(calls==257);pthread_cond_t untouched=PTHREAD_COND_INITIALIZER;assert(!clientgpu_cond_signal(&untouched));assert(!clientgpu_cond_destroy(&untouched));puts("PASS actual Mesa C11 + reserved native conditions:preinitfailure/128bounds/duplicate rejection,lateinitrefused,timedwait/signal/broadcast/mutexreacquisition/data visibility,10000reuse,noadditionalnativeinit,ordinary static condition fallback");}
'''
p=w/'test.c';p.write_text(s);subprocess.run([*flags,str(p),str(w/'mesa-threads.o'),str(w/'reserve.o'),str(r/'.tools/PS5_Mesa/src/c11/impl/time.c'),'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True,timeout=45)
