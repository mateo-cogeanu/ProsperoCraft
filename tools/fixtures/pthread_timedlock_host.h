/* Host-only macOS fixture for the native POSIX timed-mutex operation. */
#include <pthread.h>
#include <errno.h>
#include <time.h>
#if defined(__APPLE__) && !defined(pthread_mutex_timedlock)
static int host_pthread_mutex_timedlock(pthread_mutex_t*m,const struct timespec*t)
{
 for(;;){int rc=pthread_mutex_trylock(m);if(rc!=EBUSY)return rc;
  struct timespec now;clock_gettime(CLOCK_REALTIME,&now);
  if(now.tv_sec>t->tv_sec||(now.tv_sec==t->tv_sec&&now.tv_nsec>=t->tv_nsec))return ETIMEDOUT;
  const struct timespec delay={0,50000};nanosleep(&delay,0);
 }
}
#define pthread_mutex_timedlock host_pthread_mutex_timedlock
#endif
