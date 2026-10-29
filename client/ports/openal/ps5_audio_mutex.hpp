/* SPDX-License-Identifier: LGPL-2.0-or-later
 * Scoped nonrecursive audio locks; no lazy SDK mutex initialization.
 * Acquire/release exclusion with finite spinning then native sleep backoff.
 */
#pragma once
#include <ctime>
namespace ps5audio {
class Mutex {
 unsigned state_=0;
public:
 constexpr Mutex() noexcept=default;
 Mutex(const Mutex&)=delete;Mutex&operator=(const Mutex&)=delete;
 bool try_lock() noexcept {unsigned expected=0;return __atomic_compare_exchange_n(&state_,&expected,1,false,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED);}
 void lock() noexcept {unsigned spins=0;while(!try_lock()){
  if(spins++<64){
#if defined(__x86_64__) || defined(__i386__)
   __asm__ volatile("pause");
#elif defined(__aarch64__)
   __asm__ volatile("yield");
#endif
  }else{const timespec delay{0,50000};nanosleep(&delay,nullptr);spins=0;}
 }}
 void unlock() noexcept {__atomic_store_n(&state_,0,__ATOMIC_RELEASE);}
};
}
