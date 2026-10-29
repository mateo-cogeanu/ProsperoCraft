#!/usr/bin/env python3
"""Exercise actual PS5 SDL lock backend with allocation-free storage and contention."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1];work=root/'build/sdl-rwlock-host';work.mkdir(exist_ok=True)
fixture=r'''
#include <SDL3/SDL.h>
#include <pthread.h>
#include <assert.h>
#include <stdatomic.h>
#include <time.h>
#include <stdio.h>
bool SDL_SetError(const char *fmt,...){(void)fmt;return false;}
int sceKernelUsleep(uint32_t us){struct timespec t={0,us*1000};nanosleep(&t,0);return 0;}
static SDL_RWLock *lock;
static atomic_int ready,go,readers,writers,maxreaders;
static long left,right;
static void *reader(void *arg){(void)arg;atomic_fetch_add(&ready,1);while(!atomic_load(&go)){}for(int i=0;i<3000;i++){SDL_LockRWLockForReading(lock);int n=atomic_fetch_add(&readers,1)+1;int peak=atomic_load(&maxreaders);while(n>peak&&!atomic_compare_exchange_weak(&maxreaders,&peak,n)){}assert(!atomic_load(&writers));SDL_LockRWLockForReading(lock);assert(left==right);if(i%100==0)sceKernelUsleep(50);SDL_UnlockRWLock(lock);atomic_fetch_sub(&readers,1);SDL_UnlockRWLock(lock);}return 0;}
static void *writer(void *arg){(void)arg;atomic_fetch_add(&ready,1);while(!atomic_load(&go)){}for(int i=0;i<3000;i++){SDL_LockRWLockForWriting(lock);assert(atomic_fetch_add(&writers,1)==0);assert(!atomic_load(&readers));left++;right=left;assert(atomic_fetch_sub(&writers,1)==1);SDL_UnlockRWLock(lock);}return 0;}
int main(void){SDL_RWLock *all[256];for(int i=0;i<256;i++){all[i]=SDL_CreateRWLock();assert(all[i]);for(int j=0;j<i;j++)assert(all[j]!=all[i]);}assert(!SDL_CreateRWLock());for(int i=0;i<256;i++)SDL_DestroyRWLock(all[i]);lock=SDL_CreateRWLock();assert(lock);SDL_LockRWLockForReading(lock);assert(SDL_TryLockRWLockForReading(lock));assert(!SDL_TryLockRWLockForWriting(lock));SDL_UnlockRWLock(lock);assert(!SDL_TryLockRWLockForWriting(lock));SDL_UnlockRWLock(lock);assert(SDL_TryLockRWLockForWriting(lock));assert(!SDL_TryLockRWLockForWriting(lock));assert(!SDL_TryLockRWLockForReading(lock));SDL_UnlockRWLock(lock);assert(SDL_TryLockRWLockForWriting(NULL)&&SDL_TryLockRWLockForReading(NULL));SDL_LockRWLockForReading(NULL);SDL_LockRWLockForWriting(NULL);SDL_UnlockRWLock(NULL);SDL_DestroyRWLock(NULL);pthread_t threads[8];for(int i=0;i<8;i++)assert(!pthread_create(&threads[i],0,i<4?reader:writer,0));while(atomic_load(&ready)!=8){}atomic_store(&go,1);for(int i=0;i<8;i++)pthread_join(threads[i],0);assert(left==12000&&right==left&&atomic_load(&maxreaders)>1);SDL_DestroyRWLock(lock);for(int k=0;k<1000;k++){lock=SDL_CreateRWLock();assert(lock);SDL_LockRWLockForWriting(lock);SDL_UnlockRWLock(lock);SDL_DestroyRWLock(lock);}puts("PASS PS5 SDL actual RWLock: bounded256 lifetime/reuse, recursive+parallel readers, exclusive writers, try/block/NULL semantics, protected data visibility;24000contended operations");}
'''
(work/'test.c').write_text(fixture)
common=['clang','-std=c11','-DPS5_RWLOCK_HOST_TEST','-I/opt/homebrew/include','-fsanitize=address,undefined','-pthread']
subprocess.run([*common,'-c',str(root/'client/ports/sdl/SDL_ps5rwlock.c'),'-o',str(work/'rwlock.o')],check=True)
symbols=subprocess.check_output(['nm','-u',str(work/'rwlock.o')],text=True)
names={line.split()[-1] for line in symbols.splitlines() if line.split()}
assert not names.intersection({'_malloc','_calloc','_realloc','_free'}) and not any(n.startswith('_pthread_rwlock_') for n in names),symbols
subprocess.run([*common,str(work/'test.c'),str(work/'rwlock.o'),'-o',str(work/'test')],check=True)
subprocess.run([str(work/'test')],check=True,timeout=45)
