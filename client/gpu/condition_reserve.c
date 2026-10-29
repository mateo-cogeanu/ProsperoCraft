/* SPDX-License-Identifier: Zlib
 * RADV-only pthread condition leases, reserved before JVM memory pressure.
 * Native condition operations and the caller's native mutex are retained.
 * Objects created outside this adapter (including static initializers) keep
 * their ordinary pthread path. Destroy requires no active waiters/operations.
 */
#include <pthread.h>
#include <errno.h>
#include <stddef.h>
#include <time.h>
static struct { pthread_cond_t native; pthread_cond_t *owner; } entries[128];
static unsigned ready,guard;
static void lock_entries(void){while(__atomic_exchange_n(&guard,1,__ATOMIC_ACQUIRE)){
#if defined(__x86_64__)
 __asm__ volatile("pause");
#elif defined(__aarch64__)
 __asm__ volatile("yield");
#endif
}}
static void unlock_entries(void){__atomic_store_n(&guard,0,__ATOMIC_RELEASE);}
int clientgpu_condition_preinit(void)
{
 while(ready<128){int rc=pthread_cond_init(&entries[ready].native,NULL);if(rc)return rc;++ready;}
 return 0;
}
static pthread_cond_t* resolve(pthread_cond_t *owner)
{
 pthread_cond_t *native=owner;lock_entries();
 for(unsigned i=0;i<ready;i++)if(entries[i].owner==owner){native=&entries[i].native;break;}
 unlock_entries();return native;
}
int clientgpu_cond_init(pthread_cond_t *owner,const pthread_condattr_t *attr)
{
 /* Mesa C11 uses default attributes. Preserve non-default semantics natively. */
 if(attr)return pthread_cond_init(owner,attr);
 lock_entries();
 for(unsigned i=0;i<ready;i++)if(entries[i].owner==owner){unlock_entries();return EBUSY;}
 for(unsigned i=0;i<ready;i++)if(!entries[i].owner){entries[i].owner=owner;unlock_entries();return 0;}
 unlock_entries();return ENOMEM;
}
int clientgpu_cond_destroy(pthread_cond_t *owner)
{
 lock_entries();for(unsigned i=0;i<ready;i++)if(entries[i].owner==owner){entries[i].owner=NULL;unlock_entries();return 0;}
 unlock_entries();return pthread_cond_destroy(owner);
}
int clientgpu_cond_signal(pthread_cond_t *owner){return pthread_cond_signal(resolve(owner));}
int clientgpu_cond_broadcast(pthread_cond_t *owner){return pthread_cond_broadcast(resolve(owner));}
int clientgpu_cond_wait(pthread_cond_t *owner,pthread_mutex_t *mutex){return pthread_cond_wait(resolve(owner),mutex);}
int clientgpu_cond_timedwait(pthread_cond_t *owner,pthread_mutex_t *mutex,const struct timespec *time){return pthread_cond_timedwait(resolve(owner),mutex,time);}
