/* SPDX-License-Identifier: Zlib
 * Reserve the one process-lifetime VideoOut flip worker before JVM pressure.
 * Assignment starts the original WSI routine with its original argument.
 * No substitute presentation or successful result on creation failure.
 */
#include <pthread.h>
#include <errno.h>
#include <time.h>
static pthread_t worker;
static int (*entry)(void*);
static void *argument;
static unsigned ready,assigned,started;
static void* dispatch(void *unused)
{
 (void)unused;
 while(!__atomic_load_n(&started,__ATOMIC_ACQUIRE)){
  const struct timespec delay={0,1000000};nanosleep(&delay,0);
 }
 return (void*)(long)entry(argument);
}
int clientgpu_present_worker_preinit(void)
{
 if(ready)return 0;
 int result=pthread_create(&worker,0,dispatch,0);
 if(!result)ready=1;
 return result;
}
/* Mesa C11 thrd_t is the native pthread_t on this POSIX backend. */
int clientgpu_present_worker_start(pthread_t *result,int (*function)(void*),void *data)
{
 if(!ready || !function || !result)return 2; /* thrd_error */
 unsigned expected=0;
 if(!__atomic_compare_exchange_n(&assigned,&expected,1,0,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE))return 2;
 entry=function;argument=data;*result=worker;
 __atomic_store_n(&started,1,__ATOMIC_RELEASE);
 return 0; /* thrd_success; the reserved native thread really exists */
}
