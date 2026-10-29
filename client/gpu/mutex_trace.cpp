/* SPDX-License-Identifier: Zlib
 * Bounded native std::mutex diagnostics after shader compiler initialization.
 * Forward original locking unchanged; a throw naturally omits the return record.
 */
#include <cstdio>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
static unsigned enabled,events;
extern "C" void ps5_cpp_mutex_trace_enable(void){__atomic_store_n(&enabled,1,__ATOMIC_RELEASE);}
extern "C" void __real__ZNSt3__15mutex4lockEv(void*);
static void note(const char* phase,unsigned id,const void* caller,const void* mutex)
{
 int saved=errno;char text[256];int n=std::snprintf(text,sizeof(text),"PS5_CPP_MUTEX phase=%s id=%u caller=%p anchor=%p mutex=%p\n",phase,id,caller,(void*)&note,mutex);
 if(n>0){size_t length=(size_t)n<sizeof(text)?(size_t)n:sizeof(text)-1;int fd=open("/download0/java25-startup.log",O_WRONLY|O_APPEND);if(fd>=0){size_t done=0;while(done<length){ssize_t count=write(fd,text+done,length-done);if(count>0)done+=(size_t)count;else if(count<0&&errno==EINTR)continue;else break;}close(fd);}}
 errno=saved;
}
extern "C" void __wrap__ZNSt3__15mutex4lockEv(void* mutex)
{
 bool record=__atomic_load_n(&enabled,__ATOMIC_ACQUIRE)!=0;
 unsigned id=record?__atomic_fetch_add(&events,1,__ATOMIC_RELAXED):256;
 record=record&&id<256;const void*caller=__builtin_return_address(0);
 if(record)note("enter",id,caller,mutex);
 __real__ZNSt3__15mutex4lockEv(mutex);
 if(record)note("return",id,caller,mutex);
}
// Some SDK C++ methods inline their native lock instead of calling mutex::lock.
// Record failed native calls too, with a separate bound independent of chatter.
#include <pthread.h>
extern "C" int __real_pthread_mutex_lock(pthread_mutex_t*);
static unsigned native_failures;
extern "C" int __wrap_pthread_mutex_lock(pthread_mutex_t* mutex)
{
 const void* caller=__builtin_return_address(0);
 int rc=__real_pthread_mutex_lock(mutex);
 if(rc && __atomic_load_n(&enabled,__ATOMIC_ACQUIRE) &&
    __atomic_fetch_add(&native_failures,1,__ATOMIC_RELAXED)<64){
  char phase[64];int saved=errno;
  std::snprintf(phase,sizeof(phase),"native-error-%d",rc);
  note(phase,0,caller,mutex);errno=saved;
 }
 return rc;
}
