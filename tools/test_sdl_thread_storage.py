#!/usr/bin/env python3
"""Actual patched SDL TLS/error code: isolation, allocation failures and cleanup."""
from pathlib import Path
import subprocess,tempfile,re
r=Path(__file__).resolve().parents[1];src=r/'build/sdl-src/src'
with tempfile.TemporaryDirectory() as d:
 w=Path(d)
 thread=(src/'thread/SDL_thread.c').read_text().split('static bool ThreadValid')[0]
 assert 'prospero_sdl_tls_preinit' in thread,'Export patched target SDL first'
 systls=(src/'thread/pthread/SDL_systls.c').read_text()
 error=(src/'SDL_error.c').read_text()
 # Compile the actual complete TLS/error routines, omitting unrelated SDL thread
 # creation. Keep the upstream flexible-array and error structs verbatim.
 h=(src/'thread/SDL_thread_c.h').read_text();h=h[h.index('typedef struct\n{'):h.index('// This is how many TLS entries')]
 eh=(src/'SDL_error_c.h').read_text();eh=eh[eh.index('typedef enum'):eh.index('// Macros to save')]
 prefix='''#include <SDL3/SDL.h>
#include <pthread.h>
#include <assert.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#define __PROSPERO__ 1
#define TLS_ALLOC_CHUNKSIZE 4
#define CHECK_PARAM(x) if(x)
#undef SDL_assert
#define SDL_assert assert
'''+h+eh+'''
void SDL_SYS_InitTLSData(void);
SDL_TLSData *SDL_SYS_GetTLSData(void);
bool SDL_SYS_SetTLSData(SDL_TLSData*);
void SDL_SYS_QuitTLSData(void);
void SDL_Generic_InitTLSData(void);
SDL_TLSData *SDL_Generic_GetTLSData(void);
bool SDL_Generic_SetTLSData(SDL_TLSData*);
void SDL_Generic_QuitTLSData(void);
static _Thread_local int fail_after=-1;
static atomic_int live;
static void *test_realloc(void*p,size_t n){
 if(fail_after==0)return NULL;
 if(fail_after>0)--fail_after;
 void*q=realloc(p,n);if(q&&!p)atomic_fetch_add(&live,1);return q;
}
static void test_free(void*p){if(p)atomic_fetch_sub(&live,1);free(p);}
static void *test_malloc(size_t n){return test_realloc(NULL,n);}
static void test_original(SDL_malloc_func*a,SDL_calloc_func*b,SDL_realloc_func*c,SDL_free_func*d){(void)a;(void)b;*c=test_realloc;*d=test_free;}
static atomic_int accounted;
#define INCREMENT_ALLOCATION_COUNT() atomic_fetch_add(&accounted,1)
#define DECREMENT_ALLOCATION_COUNT() atomic_fetch_sub(&accounted,1)
static struct { SDL_malloc_func malloc_func; SDL_calloc_func calloc_func; SDL_realloc_func realloc_func; SDL_free_func free_func; } s_mem={test_malloc,calloc,test_realloc,test_free};
#define SDL_GetOriginalMemoryFunctions test_original
'''
 def strip(s):return re.sub(r'^#include.*\n','',s,flags=re.M)
 malloc=(src/'stdlib/SDL_malloc.c').read_text();at=malloc.index('/* ProsperoCraft alteration: only SDL TLS bootstrap');malloc=malloc[malloc.rfind('#ifdef',0,at):]

 fixture=r'''
static SDL_TLSID slots[20];
static _Thread_local int destroyed;
static void destructor(void*p){assert(p==(void*)42);destroyed++;}
static void *worker(void*arg){
 long id=(long)arg;
 for(int k=0;k<1000;k++){
  destroyed=0;
  for(int i=0;i<20;i++)assert(SDL_SetTLS(&slots[i],(void*)42,destructor));
  assert(!SDL_SetError("thread %ld cycle %d",id,k));
  char expected[80];snprintf(expected,sizeof expected,"thread %ld cycle %d",id,k);
  assert(!strcmp(SDL_GetError(),expected));
  for(int i=0;i<20;i++)assert(SDL_GetTLS(&slots[i])==(void*)42);
  SDL_CleanupTLS();assert(destroyed==20);assert(!SDL_SYS_GetTLSData());
 }
 return NULL;
}
int main(void){
 assert(!SDL_SYS_SetTLSData(NULL)); /* fail closed before bootstrap */
 assert(!prospero_sdl_tls_preinit());
 for(int n=0;n<3;n++){
  int before=atomic_load(&live);fail_after=n;
  assert(!SDL_SetError("cannot allocate"));
  assert(!SDL_SYS_GetTLSData());assert(!strcmp(SDL_GetError(),""));
  assert(atomic_load(&live)==before);fail_after=-1;
 }
 fail_after=3;assert(!SDL_SetError("string allocation refused"));fail_after=-1;
 assert(SDL_SYS_GetTLSData()&&!strcmp(SDL_GetError(),""));SDL_CleanupTLS();assert(!atomic_load(&live));
 for(int i=0;i<20;i++)assert(SDL_SetTLS(&slots[i],(void*)42,destructor));
 SDL_CleanupTLS();
 assert(!SDL_SetError("ready"));assert(!strcmp(SDL_GetError(),"ready"));
 fail_after=0;assert(!SDL_malloc(64));assert(!strcmp(SDL_GetError(),"Out of memory"));
 assert(!SDL_realloc(NULL,64));assert(!strcmp(SDL_GetError(),"Out of memory"));fail_after=-1;
 assert(!SDL_SetError("ready"));
 SDL_TLSData*old=SDL_SYS_GetTLSData();int before=atomic_load(&live);
 fail_after=0;assert(!SDL_SetTLS(&slots[19],(void*)42,destructor));fail_after=-1;
 assert(SDL_SYS_GetTLSData()==old&&atomic_load(&live)==before);
 assert(!strcmp(SDL_GetError(),"ready"));SDL_CleanupTLS();assert(!atomic_load(&live));
 pthread_t ts[8];for(long i=0;i<8;i++)assert(!pthread_create(&ts[i],NULL,worker,(void*)i));
 for(int i=0;i<8;i++)assert(!pthread_join(ts[i],NULL));
 assert(!atomic_load(&live));assert(SDL_GetAtomicInt(&SDL_tls_allocated)==0);
 SDL_QuitTLSData();assert(SDL_generic_TLS_mutex&&!SDL_generic_TLS);
 assert(!prospero_sdl_tls_preinit());assert(!SDL_SetError("reinit"));
 assert(!strcmp(SDL_GetError(),"reinit"));SDL_QuitTLSData();assert(!atomic_load(&live));assert(!atomic_load(&accounted));
 puts("PASS actual SDL TLS/error code: 4 allocation-failure sites/rollback, retained storage on failed growth, 8 threads/8000lifetimes/160000destructors, error isolation, cleanup/reinit, zero SDK TLS dependency; ASan/UBSan");
}
'''
 # Negative control: the pinned original error/TLS routines recurse when the
 # native set refuses. Bound the observed recursion instead of overflowing the
 # host stack; the same forced refusal is absent from the patched backend.
 def original(name):return subprocess.check_output(['git','-C',str(r/'.tools/sdl3-src'),'show','683181b47cfabd293e3ea409f838915b8297a4fd:src/'+name],text=True)
 refused=r"""
static int refused_setspecific(pthread_key_t key,const void *p){
 (void)key;(void)p;static int attempts;
 if(++attempts==32)_Exit(77);
 return 12;
}
#define pthread_setspecific refused_setspecific
"""
 old=w/'original.c';old.write_text(prefix+'void *SDL_malloc(size_t size)'+original('stdlib/SDL_malloc.c').split('void *SDL_malloc(size_t size)',1)[1]+refused+strip(original('thread/SDL_thread.c').split('static bool ThreadValid')[0])+strip(original('thread/pthread/SDL_systls.c'))+strip(original('SDL_error.c'))+'\nint main(void){SDL_SetError("fixture");return 1;}\n')
 oldexe=w/'original';subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include',str(old),'-L/opt/homebrew/lib','-lSDL3','-o',str(oldexe)],check=True)
 assert subprocess.run([str(oldexe)],timeout=10).returncode==77
 print('PASS pinned original SDL failure reproduced:32 recursive pthread_setspecific refusals while creating one error')
 p=w/'test.c';p.write_text(prefix+malloc+strip(thread)+strip(systls)+strip(error)+fixture)
 exe=w/'test';subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include',str(p),'-L/opt/homebrew/lib','-lSDL3','-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True,timeout=50)
