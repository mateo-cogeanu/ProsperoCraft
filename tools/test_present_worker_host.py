#!/usr/bin/env python3
"""Actual reserved worker with native thread identity/argument/result and late refusal."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <pthread.h>
#include <errno.h>
#include <assert.h>
#include <stdio.h>
#include <stdatomic.h>
static int deny=1,creates;
static int test_create(pthread_t*t,const pthread_attr_t*a,void*(*f)(void*),void*p){creates++;if(deny)return EAGAIN;return pthread_create(t,a,f,p);}
#define pthread_create test_create
'''+ '\n#include "'+str(r/'client/gpu/present_worker.c')+'"\n'+r'''
#undef pthread_create
static _Atomic int entered;
static pthread_t actual;
static int work(void*arg){assert(arg==(void*)0x4321);actual=pthread_self();atomic_store(&entered,1);return 73;}
int main(){pthread_t thread;
 assert(clientgpu_present_worker_start(&thread,work,(void*)0x4321)==2);
 assert(clientgpu_present_worker_preinit()==EAGAIN&&creates==1);
 deny=0;assert(!clientgpu_present_worker_preinit()&&creates==2);
 assert(!clientgpu_present_worker_preinit()&&creates==2);deny=1;
 assert(!atomic_load(&entered));
 assert(clientgpu_present_worker_start(0,work,0)==2);
 assert(clientgpu_present_worker_start(&thread,0,0)==2);
 assert(!clientgpu_present_worker_start(&thread,work,(void*)0x4321));
 assert(clientgpu_present_worker_start(&thread,work,(void*)0x4321)==2);
 void*result=0;assert(!pthread_join(thread,&result));
 assert(atomic_load(&entered)&&pthread_equal(actual,thread)&&result==(void*)73&&creates==2);
 puts("PASS actual native reserved worker: early creation failure propagated, retry/idempotence, no premature callback, late creation denied, same thread/argument/result, single assignment and invalid request rejection;ASan/UBSan");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.c';p.write_text(code);exe=d/'test'
 subprocess.run(['clang','-std=c11','-O2','-pthread','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True,timeout=10)
