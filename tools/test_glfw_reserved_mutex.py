#!/usr/bin/env python3
"""Actual patched GLFW mutex API against actual reserved SDL native mutex source."""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1];w=r/'build/glfw-mutex-reserve-host';w.mkdir(exist_ok=True);source=r/'build/glfw-native/host/source/src';assert 'SDL_CreateMutex' in (source/'posix_thread.c').read_text()
fixture=r'''
#include "internal.h"
#include <SDL3/SDL.h>
#include <pthread.h>
#include <assert.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
int prospero_sdl_mutex_preinit(void);
static int denied,init_calls,errors;static long counter;static _GLFWmutex lock;
int test_mutex_init(pthread_mutex_t*m,const pthread_mutexattr_t*a){init_calls++;return denied?ENOMEM:pthread_mutex_init(m,a);}
int test_cond_init(pthread_cond_t*c,const pthread_condattr_t*a){return pthread_cond_init(c,a);}
bool SDL_SetError(const char *fmt,...){(void)fmt;return false;}
void _glfwInputError(int code,const char*fmt,...){(void)fmt;assert(code==GLFW_PLATFORM_ERROR);errors++;}
static void*worker(void*x){(void)x;for(int i=0;i<10000;i++){_glfwPlatformLockMutex(&lock);long next=counter+1;counter=next;_glfwPlatformUnlockMutex(&lock);}return 0;}
int main(void){_GLFWmutex none={0};assert(!_glfwPlatformCreateMutex(&none)&&errors==1&&!none.posix.allocated);assert(!prospero_sdl_mutex_preinit()&&init_calls==256);denied=1;_GLFWmutex all[256]={0};for(int i=0;i<256;i++)assert(_glfwPlatformCreateMutex(&all[i]));assert(!_glfwPlatformCreateMutex(&none)&&errors==2);for(int i=0;i<256;i++){_glfwPlatformDestroyMutex(&all[i]);assert(!all[i].posix.allocated&&!all[i].posix.ps5_sdl_mutex);}assert(_glfwPlatformCreateMutex(&lock));pthread_t threads[8];for(int i=0;i<8;i++)assert(!pthread_create(&threads[i],0,worker,0));for(int i=0;i<8;i++)pthread_join(threads[i],0);assert(counter==80000);_glfwPlatformDestroyMutex(&lock);for(int i=0;i<10000;i++){assert(_glfwPlatformCreateMutex(&lock));_glfwPlatformLockMutex(&lock);_glfwPlatformUnlockMutex(&lock);_glfwPlatformDestroyMutex(&lock);}assert(init_calls==256);puts("PASS actual GLFW reserved SDL mutex:unprepared/exhaustion errors,256leases/destroyzeroing,80000contended increments,10000reusecycles,no pthreadmutexinit afterearlyreserve");}
'''
p=w/'test.c';p.write_text(fixture);flags=['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I'+str(source),'-I/opt/homebrew/include'];subprocess.run([*flags,'-c',str(source/'posix_thread.c'),'-o',str(w/'glfw-thread.o')],check=True)
subprocess.run([*flags,str(p),str(w/'glfw-thread.o'),str(r/'build/sdl-sync-reserve-host/SDL_sysmutex.o'),'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True,timeout=45)
