/* SPDX-License-Identifier: Zlib
 * ProsperoCraft PS5 SDL reader/writer locks. Allocation-free bounded storage
 * avoids SDK pthread_rwlock_init allocation failure after JVM startup.
 * Concurrent/recursive readers, exclusive writers, try-lock and NULL semantics
 * follow SDL_mutex.h. Fairness/writer preference are not guaranteed by SDL.
 */
#ifdef PS5_RWLOCK_HOST_TEST
#include <SDL3/SDL.h>
#else
#include "SDL_internal.h"
#endif
#include <limits.h>
#include <stdint.h>
extern int sceKernelUsleep(uint32_t);
struct SDL_RWLock { int state; unsigned leased; };
static struct SDL_RWLock locks[256];
static void wait_lock(unsigned *spins)
{
    if (++*spins < 64) {
#if defined(__x86_64__)
        __asm__ volatile("pause");
#elif defined(__aarch64__)
        __asm__ volatile("yield");
#endif
    } else { (void)sceKernelUsleep(50); *spins = 0; }
}
SDL_RWLock *SDL_CreateRWLock(void)
{
    for (unsigned i = 0; i < 256; ++i) {
        unsigned expected = 0;
        if (__atomic_compare_exchange_n(&locks[i].leased, &expected, 1, false,
                                        __ATOMIC_ACQUIRE, __ATOMIC_RELAXED)) {
            __atomic_store_n(&locks[i].state, 0, __ATOMIC_RELAXED);
            return &locks[i];
        }
    }
    SDL_SetError("PS5 SDL reader/writer lock reserve exhausted (256 live locks)");
    return NULL;
}
void SDL_DestroyRWLock(SDL_RWLock *lock)
{
    if (!lock) return;
    /* SDL requires no owners/waiters at destruction; never recycle a held lock. */
    if (__atomic_load_n(&lock->state, __ATOMIC_ACQUIRE) != 0) {
        SDL_SetError("PS5 SDL cannot destroy a held reader/writer lock");
        return;
    }
    __atomic_store_n(&lock->leased, 0, __ATOMIC_RELEASE);
}
bool SDL_TryLockRWLockForReading(SDL_RWLock *lock) SDL_NO_THREAD_SAFETY_ANALYSIS
{
    if (!lock) return true;
    int state = __atomic_load_n(&lock->state, __ATOMIC_RELAXED);
    while (state >= 0 && state < INT_MAX) {
        if (__atomic_compare_exchange_n(&lock->state, &state, state + 1, true,
                                        __ATOMIC_ACQUIRE, __ATOMIC_RELAXED)) return true;
    }
    return false;
}
bool SDL_TryLockRWLockForWriting(SDL_RWLock *lock) SDL_NO_THREAD_SAFETY_ANALYSIS
{
    if (!lock) return true;
    int expected = 0;
    return __atomic_compare_exchange_n(&lock->state, &expected, -1, false,
                                       __ATOMIC_ACQUIRE, __ATOMIC_RELAXED);
}
void SDL_LockRWLockForReading(SDL_RWLock *lock) SDL_NO_THREAD_SAFETY_ANALYSIS
{
    unsigned spins = 0;
    while (!SDL_TryLockRWLockForReading(lock)) wait_lock(&spins);
}
void SDL_LockRWLockForWriting(SDL_RWLock *lock) SDL_NO_THREAD_SAFETY_ANALYSIS
{
    unsigned spins = 0;
    while (!SDL_TryLockRWLockForWriting(lock)) wait_lock(&spins);
}
void SDL_UnlockRWLock(SDL_RWLock *lock) SDL_NO_THREAD_SAFETY_ANALYSIS
{
    if (!lock) return;
    if (__atomic_load_n(&lock->state, __ATOMIC_RELAXED) < 0)
        __atomic_store_n(&lock->state, 0, __ATOMIC_RELEASE);
    else __atomic_fetch_sub(&lock->state, 1, __ATOMIC_RELEASE);
}
