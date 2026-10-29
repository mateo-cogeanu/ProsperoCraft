#!/usr/bin/env python3
"""Actual patched SDL pthread mutex/condition code with init refusal after reservation."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];src=r/'build/sdl-src/src/thread/pthread';w=r/'build/sdl-sync-reserve-host';w.mkdir(exist_ok=True)
# Read actual target-export source, patched by build_sdl_native.
header=r'''
#include <SDL3/SDL.h>
#include <pthread.h>
#include <assert.h>
#include <errno.h>
#define SDL_THREAD_PTHREAD_RECURSIVE_MUTEX 1
#undef SDL_assert
#define SDL_assert assert
struct SDL_Mutex {pthread_mutex_t id;};
int test_mutex_init(pthread_mutex_t*,const pthread_mutexattr_t*);
int test_cond_init(pthread_cond_t*,const pthread_condattr_t*);
#define pthread_mutex_init test_mutex_init
#define pthread_cond_init test_cond_init
'''
(w/'test_header.h').write_text(header)
for name in ['SDL_sysmutex.c','SDL_syscond.c']:
 text=(src/name).read_text();assert 'reserve[' in text,'Run target SDL export first'
 text=text.replace('#include "SDL_internal.h"','#include "test_header.h"').replace('#include "SDL_sysmutex_c.h"','')
 p=w/name;p.write_text(text)
 subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include','-I'+str(w),'-c',str(p),'-o',str(p.with_suffix('.o'))],check=True)
fixture=r'''
#include <SDL3/SDL.h>
#include <pthread.h>
#include <assert.h>
#include <stdatomic.h>
#include <errno.h>
#include <stdio.h>
int prospero_sdl_mutex_preinit(void);int prospero_sdl_condition_preinit(void);
bool SDL_WaitConditionTimeoutNS(SDL_Condition*,SDL_Mutex*,Sint64);
static int deny,mutex_calls,cond_calls;
int test_mutex_init(pthread_mutex_t*m,const pthread_mutexattr_t*a){mutex_calls++;return deny?ENOMEM:pthread_mutex_init(m,a);}
int test_cond_init(pthread_cond_t*c,const pthread_condattr_t*a){cond_calls++;return deny?ENOMEM:pthread_cond_init(c,a);}
bool SDL_SetError(const char *fmt,...){(void)fmt;return false;}
static SDL_Mutex*m;static SDL_Condition*c;static int value,go;static atomic_int ready,awakened;
static void*waiter(void*x){(void)x;SDL_LockMutex(m);atomic_fetch_add(&ready,1);while(!go)assert(SDL_WaitConditionTimeoutNS(c,m,-1));assert(value==42);atomic_fetch_add(&awakened,1);SDL_UnlockMutex(m);return 0;}
static void*tryer(void*x){(void)x;assert(!SDL_TryLockMutex(m));return 0;}
int main(void){assert(!SDL_CreateMutex()&&!SDL_CreateCondition());assert(!prospero_sdl_mutex_preinit()&&!prospero_sdl_condition_preinit());assert(mutex_calls==256&&cond_calls==128);deny=1;SDL_Mutex*ms[256];SDL_Condition*cs[128];for(int i=0;i<256;i++){ms[i]=SDL_CreateMutex();assert(ms[i]);for(int j=0;j<i;j++)assert(ms[i]!=ms[j]);}assert(!SDL_CreateMutex());for(int i=0;i<128;i++){cs[i]=SDL_CreateCondition();assert(cs[i]);for(int j=0;j<i;j++)assert(cs[i]!=cs[j]);}assert(!SDL_CreateCondition());for(int i=0;i<256;i++)SDL_DestroyMutex(ms[i]);for(int i=0;i<128;i++)SDL_DestroyCondition(cs[i]);m=SDL_CreateMutex();c=SDL_CreateCondition();assert(m&&c);SDL_LockMutex(m);SDL_LockMutex(m);assert(SDL_TryLockMutex(m));SDL_UnlockMutex(m);SDL_UnlockMutex(m);pthread_t t;assert(!pthread_create(&t,0,tryer,0));pthread_join(t,0);assert(!SDL_WaitConditionTimeoutNS(c,m,1000000));SDL_UnlockMutex(m);pthread_t threads[4];for(int i=0;i<4;i++)assert(!pthread_create(&threads[i],0,waiter,0));while(atomic_load(&ready)<4){}SDL_LockMutex(m);value=42;go=1;SDL_BroadcastCondition(c);SDL_UnlockMutex(m);for(int i=0;i<4;i++)pthread_join(threads[i],0);assert(awakened==4);
 go=0;atomic_store(&ready,0);assert(!pthread_create(&t,0,waiter,0));while(!atomic_load(&ready)){}SDL_LockMutex(m);go=1;SDL_SignalCondition(c);SDL_UnlockMutex(m);pthread_join(t,0);
 SDL_DestroyMutex(m);SDL_DestroyCondition(c);for(int i=0;i<10000;i++){m=SDL_CreateMutex();c=SDL_CreateCondition();assert(m&&c);SDL_LockMutex(m);SDL_UnlockMutex(m);SDL_DestroyMutex(m);SDL_DestroyCondition(c);}assert(mutex_calls==256&&cond_calls==128);SDL_LockMutex(NULL);SDL_UnlockMutex(NULL);SDL_DestroyMutex(NULL);SDL_DestroyCondition(NULL);assert(SDL_TryLockMutex(NULL));assert(SDL_WaitConditionTimeoutNS(NULL,NULL,0));puts("PASS actual SDL native sync reserves:preinit256mutex/128condition,lateinitrefused,bounds,uniqueleases,recursive/exclusive mutex,conditiontimeout/signal/broadcast/reacquisition/data visibility,10000reusecycles,no additional pthread init calls");}
'''
p=w/'test.c';p.write_text(fixture);exe=w/'test';subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include',str(p),str(w/'SDL_sysmutex.o'),str(w/'SDL_syscond.o'),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True,timeout=45)
