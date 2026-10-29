/* SPDX-License-Identifier: Zlib
 * VMA custom-lock hooks. State lives inside each VMA object; no lazy SDK
 * pthread allocation, global lease limit, or disabled allocator synchronization.
 * Locks are nonrecursive. Waiting writers prevent new readers; existing
 * readers drain before exclusive access. No FIFO guarantee is provided.
 */
#pragma once
#include <cstdint>
#include <ctime>
namespace prospero_vma {
inline void wait(unsigned& spins) noexcept {
 if(spins++ < 64) {
#if defined(__x86_64__) || defined(__i386__)
  __asm__ volatile("pause");
#elif defined(__aarch64__)
  __asm__ volatile("yield");
#endif
 } else {
  const timespec delay{0,50000};
  nanosleep(&delay,nullptr);spins=0;
 }
}
class Mutex {
 unsigned state_=0;
public:
 Mutex() noexcept=default;
 Mutex(const Mutex&)=delete;Mutex& operator=(const Mutex&)=delete;
 void Lock() noexcept {unsigned spins=0;while(!TryLock())wait(spins);}
 bool TryLock() noexcept {unsigned expected=0;return __atomic_compare_exchange_n(&state_,&expected,1,false,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED);}
 void Unlock() noexcept {__atomic_store_n(&state_,0,__ATOMIC_RELEASE);}
};
class RWMutex {
 static constexpr unsigned writer=0x80000000u;
 unsigned state_=0,waiting_=0;
public:
 RWMutex() noexcept=default;
 RWMutex(const RWMutex&)=delete;RWMutex& operator=(const RWMutex&)=delete;
 bool TryLockRead() noexcept {
  if(__atomic_load_n(&waiting_,__ATOMIC_ACQUIRE))return false;
  unsigned state=__atomic_load_n(&state_,__ATOMIC_RELAXED);
  if(state>=writer-1)return false;
  return __atomic_compare_exchange_n(&state_,&state,state+1,false,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED);
 }
 void LockRead() noexcept {unsigned spins=0;while(!TryLockRead())wait(spins);}
 void UnlockRead() noexcept {__atomic_fetch_sub(&state_,1,__ATOMIC_RELEASE);}
 bool TryLockWrite() noexcept {unsigned expected=0;return __atomic_compare_exchange_n(&state_,&expected,writer,false,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED);}
 void LockWrite() noexcept {
  __atomic_fetch_add(&waiting_,1,__ATOMIC_ACQ_REL);
  unsigned spins=0;while(!TryLockWrite())wait(spins);
  __atomic_fetch_sub(&waiting_,1,__ATOMIC_RELEASE);
 }
 void UnlockWrite() noexcept {__atomic_store_n(&state_,0,__ATOMIC_RELEASE);}
};
}
#define VMA_MUTEX prospero_vma::Mutex
#define VMA_RW_MUTEX prospero_vma::RWMutex
