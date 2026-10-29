/* SPDX-License-Identifier: Zlib
 * RADV-only native mutex leases; initialize before JVM pressure. Native pthread
 * operations remain responsible for blocking, ownership and condition waiting.
 * Concurrent destruction/use is outside the pthread lifetime contract.
 */
static struct {pthread_mutex_t native;pthread_mutex_t *owner;} mutexes[320];
static unsigned mutex_ready;
int clientgpu_mutex_preinit(void)
{
 while(mutex_ready<256){int rc=pthread_mutex_init(&mutexes[mutex_ready].native,NULL);if(rc)return rc;mutex_ready++;}
 pthread_mutexattr_t attr;int rc=pthread_mutexattr_init(&attr);if(rc)return rc;
 rc=pthread_mutexattr_settype(&attr,PTHREAD_MUTEX_RECURSIVE);
 if(!rc)while(mutex_ready<320){rc=pthread_mutex_init(&mutexes[mutex_ready].native,&attr);if(rc)break;mutex_ready++;}
 int cleanup=pthread_mutexattr_destroy(&attr);return rc?rc:cleanup;
}
static pthread_mutex_t* mutex_find(pthread_mutex_t*owner)
{
 for(unsigned i=0;i<mutex_ready;i++)if(mutexes[i].owner==owner)return &mutexes[i].native;
 return owner;
}
static pthread_mutex_t* mutex_resolve(pthread_mutex_t*owner)
{
 lock_entries();pthread_mutex_t*native=mutex_find(owner);unlock_entries();return native;
}
int clientgpu_mutex_init(pthread_mutex_t*owner,const pthread_mutexattr_t*attr)
{
 int type=PTHREAD_MUTEX_NORMAL;
 if(attr){int rc=pthread_mutexattr_gettype(attr,&type);if(rc)return rc;}
 // Foreign attribute policies (e.g. process sharing) retain their native path.
 if(attr && type!=PTHREAD_MUTEX_RECURSIVE)return pthread_mutex_init(owner,attr);
 lock_entries();
 if(mutex_find(owner)!=owner){unlock_entries();return EBUSY;}
 unsigned first=type==PTHREAD_MUTEX_RECURSIVE?256:0,last=first?320:256;
 for(unsigned i=first;i<last&&i<mutex_ready;i++)if(!mutexes[i].owner){mutexes[i].owner=owner;unlock_entries();return 0;}
 unlock_entries();return ENOMEM;
}
int clientgpu_mutex_destroy(pthread_mutex_t*owner)
{
 lock_entries();for(unsigned i=0;i<mutex_ready;i++)if(mutexes[i].owner==owner){
  // A leased mutex must be unlocked before destruction, as required by pthread.
  int rc=pthread_mutex_trylock(&mutexes[i].native);
  if(rc){unlock_entries();return rc;}
  pthread_mutex_unlock(&mutexes[i].native);mutexes[i].owner=NULL;unlock_entries();return 0;
 }
 unlock_entries();return pthread_mutex_destroy(owner);
}
int clientgpu_mutex_lock(pthread_mutex_t*owner){return pthread_mutex_lock(mutex_resolve(owner));}
int clientgpu_mutex_trylock(pthread_mutex_t*owner){return pthread_mutex_trylock(mutex_resolve(owner));}
int clientgpu_mutex_unlock(pthread_mutex_t*owner){return pthread_mutex_unlock(mutex_resolve(owner));}
int clientgpu_mutex_timedlock(pthread_mutex_t*owner,const struct timespec*deadline){return pthread_mutex_timedlock(mutex_resolve(owner),deadline);}
