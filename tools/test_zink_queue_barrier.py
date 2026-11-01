#!/usr/bin/env python3
"""Manual actual pinned Mesa barrier + consumer reserve test under late init refusal."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from host_toolchain import ROOT,executable

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--cc',required=True);a=p.parse_args();source=a.source_dir.resolve();audit=json.loads((source.parent/'source-audit.json').read_text())
 assert audit['recipe']['mesa']['commit']==json.loads((ROOT/'client/ports/zink/sources.json').read_text())['commit']
 for name,digest in audit['recipe']['patches'].items():assert sha(ROOT/'client/ports/zink'/name)==digest
 for name in ('src/util/u_thread.h','src/util/u_thread.c','src/util/u_queue.c'):assert sha(source/name)==audit['patched_files'][name]
 h=(source/'src/util/u_thread.h').read_text();c=(source/'src/util/u_thread.c').read_text();q=(source/'src/util/u_queue.c').read_text()
 condition='#if defined(HAVE_PTHREAD) && !defined(__APPLE__) && !defined(__HAIKU__) && !defined(PS5_ZINK_FRONTEND)'
 assert condition in h and condition in c
 marker="#else /* If the OS doesn't have its own, implement barriers using a mutex and a condvar */"
 typedef=h.split(marker,1)[1].split('#endif',1)[0];functions=c.split(marker,1)[1].split('#endif',1)[0]
 execute=q[q.index('static void\nutil_queue_finish_execute('):q.index('\nvoid\nutil_queue_destroy(',q.index('static void\nutil_queue_finish_execute('))]
 assert 'util_barrier_destroy'not in execute
 finish=q[q.index('util_queue_finish(struct'):q.index('\nint64_t\n',q.index('util_queue_finish(struct'))]
 assert finish.rfind('util_queue_fence_wait')<finish.index('util_barrier_destroy(&barrier)')<finish.rfind('free(fences)')
 with tempfile.TemporaryDirectory(prefix='zink-barrier-')as folder:
  w=Path(folder);(w/'actual_barrier.inc').write_text(typedef+functions+execute)
  (w/'check.c').write_text(r'''#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdatomic.h>
#include <time.h>
static int deny,init_calls;
static int host_mutex_init(pthread_mutex_t*m,const pthread_mutexattr_t*a){init_calls++;return deny?ENOMEM:pthread_mutex_init(m,a);}
static int host_cond_init(pthread_cond_t*c,const pthread_condattr_t*a){init_calls++;return deny?ENOMEM:pthread_cond_init(c,a);}
static int host_clock(pthread_condattr_t*a,clockid_t c){
#ifdef __APPLE__
 (void)a;return c==CLOCK_MONOTONIC||c==CLOCK_REALTIME?0:EINVAL;
#else
 return pthread_condattr_setclock(a,c);
#endif
}
#define pthread_mutex_init host_mutex_init
#define pthread_cond_init host_cond_init
#define pthread_condattr_setclock host_clock
#include "condition_reserve.c"
#undef pthread_mutex_init
#undef pthread_cond_init
#undef pthread_condattr_setclock
// Only real-time barriers are exercised; Darwin's unused monotonic reserve is
// initialized with host defaults. This test makes no monotonic-clock claim.
typedef pthread_mutex_t mtx_t;typedef pthread_cond_t cnd_t;
#define mtx_plain 0
#define mtx_init(m,t) clientgpu_mutex_init(m,NULL)
#define mtx_destroy clientgpu_mutex_destroy
#define mtx_lock clientgpu_mutex_lock
#define mtx_unlock clientgpu_mutex_unlock
#define cnd_init(c) clientgpu_cond_init(c,NULL)
#define cnd_destroy clientgpu_cond_destroy
#define cnd_wait clientgpu_cond_wait
#define cnd_broadcast clientgpu_cond_broadcast
#include "actual_barrier.inc"
static util_barrier barrier;static unsigned payload[8],participants;
static void* worker(void*value){unsigned id=(unsigned)(uintptr_t)value;
 for(unsigned round=1;round<=16;round++){
  payload[id]=round;util_queue_finish_execute(&barrier,NULL,(int)id);
  for(unsigned i=0;i<participants;i++)assert(payload[i]==round);
  util_queue_finish_execute(&barrier,NULL,(int)id);
 }return NULL;
}
int main(void){
 assert(!clientgpu_mutex_preinit());assert(!clientgpu_condition_preinit());int initial=init_calls;deny=1;
 for(unsigned n=1;n<=8;n*=2){participants=n;
  for(unsigned pass=0;pass<64;pass++){
   pthread_t threads[8];util_barrier_init(&barrier,n);
   for(unsigned i=0;i<n;i++)assert(!pthread_create(&threads[i],NULL,worker,(void*)(uintptr_t)i));
   for(unsigned i=0;i<n;i++)assert(!pthread_join(threads[i],NULL));
   util_barrier_destroy(&barrier);
   for(unsigned i=0;i<mutex_ready;i++)assert(!mutexes[i].owner);
   for(unsigned i=0;i<ready;i++)assert(!entries[i].owner);
  }
 }
 for(unsigned i=0;i<1000;i++){util_barrier_init(&barrier,1);util_barrier_wait(&barrier);util_barrier_destroy(&barrier);}
 assert(init_calls==initial);
 puts("PASS actual patched Mesa portable barrier:1/2/4/8participants,8192generations, memory visibility,1000reuse cycles, balanced reserve leases, late native mutex/condition init denied, ASan/UBSan");
}
''')
  cc=executable('clang',override=a.cc)
  subprocess.run([cc,'-D_POSIX_C_SOURCE=200809L','-include',str(ROOT/'tools/fixtures/pthread_timedlock_host.h'),'-std=c11','-pthread','-fsanitize=address,undefined','-I'+str(ROOT/'client/gpu'),'-I'+str(w),w/'check.c','-o',w/'check'],check=True)
  subprocess.run([w/'check'],check=True,timeout=60,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS genuine source/patch provenance and util_queue_finish destroys barrier after real completion fences; PS5 queue/quit cause remains pending')
if __name__=='__main__':main()
