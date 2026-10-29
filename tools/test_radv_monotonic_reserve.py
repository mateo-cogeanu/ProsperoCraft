#!/usr/bin/env python3
"""Actual Mesa monotonic condition wrappers with reserved clocks and late init refusal."""
from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1];w=r/'build/radv-monotonic-host';w.mkdir(exist_ok=True)
# macOS lacks pthread_condattr_setclock. The host fixture implements that native
# API using macOS relative waits, while recording the selected clock per object.
native=r'''
#include <pthread.h>
#include <errno.h>
#include <time.h>
#include <assert.h>
static int deny,calls;static const pthread_cond_t* mono[128];static unsigned monos;
static pthread_condattr_t* current_attr;static clockid_t selected_clock;
int test_attr_init(pthread_condattr_t*a){if(deny)return ENOMEM;int rc=pthread_condattr_init(a);if(!rc){current_attr=a;selected_clock=CLOCK_REALTIME;}return rc;}
int test_attr_clock(pthread_condattr_t*a,clockid_t c){assert(a==current_attr);if(deny)return ENOMEM;if(c!=CLOCK_REALTIME&&c!=CLOCK_MONOTONIC)return EINVAL;selected_clock=c;return 0;}
int test_attr_destroy(pthread_condattr_t*a){assert(a==current_attr);current_attr=0;return pthread_condattr_destroy(a);}
int test_init(pthread_cond_t*c,const pthread_condattr_t*a){calls++;if(deny)return ENOMEM;int rc=pthread_cond_init(c,a);if(!rc&&a&&selected_clock==CLOCK_MONOTONIC){assert(monos<128);mono[monos++]=c;}return rc;}
int test_timedwait(pthread_cond_t*c,pthread_mutex_t*m,const struct timespec*t){int monotonic=0;for(unsigned i=0;i<monos;i++)if(mono[i]==c)monotonic=1;if(!monotonic)return pthread_cond_timedwait(c,m,t);struct timespec now,relative;clock_gettime(CLOCK_MONOTONIC,&now);relative.tv_sec=t->tv_sec-now.tv_sec;relative.tv_nsec=t->tv_nsec-now.tv_nsec;if(relative.tv_nsec<0){relative.tv_nsec+=1000000000;relative.tv_sec--;}if(relative.tv_sec<0)relative=(struct timespec){0};return pthread_cond_timedwait_relative_np(c,m,&relative);}
'''
(w/'native.c').write_text(native)
(w/'native.h').write_text('#include <pthread.h>\n#include <time.h>\nint test_attr_init(pthread_condattr_t*);int test_attr_clock(pthread_condattr_t*,clockid_t);int test_attr_destroy(pthread_condattr_t*);int test_init(pthread_cond_t*,const pthread_condattr_t*);int test_timedwait(pthread_cond_t*,pthread_mutex_t*,const struct timespec*);\n')
flags=['clang','-std=c11','-fsanitize=address,undefined','-pthread','-DHAVE_PTHREAD','-DHAVE_STRUCT_TIMESPEC','-I'+str(r/'.tools/PS5_Mesa/src')]
subprocess.run([*flags,'-include',str(w/'native.h'),'-Dpthread_cond_init=test_init','-Dpthread_condattr_init=test_attr_init','-Dpthread_condattr_setclock=test_attr_clock','-Dpthread_condattr_destroy=test_attr_destroy','-Dpthread_cond_timedwait=test_timedwait','-c',str(r/'client/gpu/condition_reserve.c'),'-o',str(w/'reserve.o')],check=True)
source=(r/'.tools/PS5_Mesa/src/util/cnd_monotonic.c').read_text();body=source[source.index('int\nu_cnd_monotonic_init'):]
# All exported monotonic routines are kept; select the actual POSIX clock branch
# after loading host system headers so platform headers retain their proper ABI.
(w/'mesa.c').write_text('#include "c11/threads.h"\n#include <time.h>\n#include <assert.h>\nint clientgpu_condattr_setclock(pthread_condattr_t*,clockid_t);\nstruct u_cnd_monotonic{pthread_cond_t cond;};\n#undef __APPLE__\n'+body)
rename=['pthread_cond_init','pthread_cond_destroy','pthread_cond_signal','pthread_cond_broadcast','pthread_cond_wait','pthread_cond_timedwait','pthread_condattr_init','pthread_condattr_setclock','pthread_condattr_destroy']
subprocess.run([*flags,*['-D'+n+'=clientgpu_'+n.removeprefix('pthread_')for n in rename],'-c',str(w/'mesa.c'),'-o',str(w/'mesa.o')],check=True)
test=r'''
#include "c11/threads.h"
#include <stdatomic.h>
#include <stdio.h>
struct u_cnd_monotonic{pthread_cond_t cond;};
int clientgpu_cond_timedwait(pthread_cond_t*,pthread_mutex_t*,const struct timespec*);
int clientgpu_condition_preinit(void);int clientgpu_cond_init(pthread_cond_t*,const pthread_condattr_t*);int clientgpu_cond_destroy(pthread_cond_t*);
int clientgpu_condattr_init(pthread_condattr_t*);int clientgpu_condattr_setclock(pthread_condattr_t*,clockid_t);int clientgpu_condattr_destroy(pthread_condattr_t*);
int u_cnd_monotonic_init(struct u_cnd_monotonic*);void u_cnd_monotonic_destroy(struct u_cnd_monotonic*);int u_cnd_monotonic_timedwait(struct u_cnd_monotonic*,mtx_t*,const struct timespec*);int u_cnd_monotonic_wait(struct u_cnd_monotonic*,mtx_t*);int u_cnd_monotonic_signal(struct u_cnd_monotonic*);int u_cnd_monotonic_broadcast(struct u_cnd_monotonic*);
static struct u_cnd_monotonic c;static pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;static atomic_int waiters;static int go,value;
static void*worker(void*x){(void)x;pthread_mutex_lock(&mutex);waiters++;while(!go)assert(u_cnd_monotonic_wait(&c,&mutex)==thrd_success);assert(value==77);pthread_mutex_unlock(&mutex);return 0;}
int main(void){assert(!clientgpu_condition_preinit()&&calls==256&&monos==128);deny=1;struct u_cnd_monotonic all[128],extra;pthread_cond_t real[128];for(int i=0;i<128;i++){assert(u_cnd_monotonic_init(&all[i])==thrd_success);assert(!clientgpu_cond_init(&real[i],NULL));}assert(u_cnd_monotonic_init(&extra)==thrd_error);for(int i=0;i<128;i++){u_cnd_monotonic_destroy(&all[i]);assert(!clientgpu_cond_destroy(&real[i]));}
 pthread_condattr_t attrs[64];for(int i=0;i<64;i++)assert(!clientgpu_condattr_init(&attrs[i]));pthread_condattr_t excess;assert(clientgpu_condattr_init(&excess)==ENOMEM);assert(clientgpu_condattr_setclock(&attrs[0],(clockid_t)-99)==EINVAL);for(int i=0;i<64;i++)assert(!clientgpu_condattr_destroy(&attrs[i]));
 pthread_cond_t realtime;assert(!clientgpu_cond_init(&realtime,NULL));pthread_mutex_lock(&mutex);struct timespec real_deadline;clock_gettime(CLOCK_REALTIME,&real_deadline);assert(clientgpu_cond_timedwait(&realtime,&mutex,&real_deadline)==ETIMEDOUT);pthread_mutex_unlock(&mutex);assert(!clientgpu_cond_destroy(&realtime));
 assert(u_cnd_monotonic_init(&c)==thrd_success);pthread_mutex_lock(&mutex);struct timespec deadline;clock_gettime(CLOCK_MONOTONIC,&deadline);deadline.tv_nsec+=2000000;if(deadline.tv_nsec>=1000000000){deadline.tv_nsec-=1000000000;deadline.tv_sec++;}assert(u_cnd_monotonic_timedwait(&c,&mutex,&deadline)==thrd_timedout);pthread_mutex_unlock(&mutex);
 pthread_t threads[4];for(int i=0;i<4;i++)assert(!pthread_create(&threads[i],0,worker,0));while(waiters<4){}pthread_mutex_lock(&mutex);go=1;value=77;assert(u_cnd_monotonic_broadcast(&c)==thrd_success);pthread_mutex_unlock(&mutex);for(int i=0;i<4;i++)pthread_join(threads[i],0);
 go=0;waiters=0;assert(!pthread_create(&threads[0],0,worker,0));while(!waiters){}pthread_mutex_lock(&mutex);go=1;assert(u_cnd_monotonic_signal(&c)==thrd_success);pthread_mutex_unlock(&mutex);pthread_join(threads[0],0);u_cnd_monotonic_destroy(&c);for(int i=0;i<10000;i++){assert(u_cnd_monotonic_init(&c)==thrd_success);u_cnd_monotonic_destroy(&c);}assert(calls==256&&monos==128);puts("PASS actual Mesa POSIX monotonic wrappers+adapter:128realtime+128monotonic independent bounds,64attrs/invalidclock,monotonic deadline timeout,signal/broadcast/mutexreacquisition/data visibility,10000reuse,nolateinit;nativeclockhostfixtureusesrelativeNP");}
'''
(w/'test.c').write_text(native+'\n'+test)
subprocess.run([*flags,str(w/'test.c'),str(w/'mesa.o'),str(w/'reserve.o'),'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True,timeout=45)
