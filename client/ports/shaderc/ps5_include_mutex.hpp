/* SPDX-License-Identifier: Zlib
 * Per-compilation include serialization; no kernel object, allocation or teardown.
 * Nonrecursive, acquire/release ownership. Destroy only after callers complete.
 */
#pragma once
#include <ctime>
class PS5ShaderIncludeMutex {
 unsigned held_=0;
public:
 constexpr PS5ShaderIncludeMutex() noexcept=default;
 PS5ShaderIncludeMutex(const PS5ShaderIncludeMutex&)=delete;
 PS5ShaderIncludeMutex& operator=(const PS5ShaderIncludeMutex&)=delete;
 void lock() noexcept {
  unsigned attempts=0;
  for(;;){
   unsigned empty=0;
   if(__atomic_compare_exchange_n(&held_,&empty,1,false,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED))return;
   if(++attempts==64){const timespec delay{0,50000};nanosleep(&delay,nullptr);attempts=0;}
#if defined(__x86_64__)
   else __asm__ volatile("pause");
#elif defined(__aarch64__)
   else __asm__ volatile("yield");
#endif
  }
 }
 void unlock() noexcept {__atomic_store_n(&held_,0,__ATOMIC_RELEASE);}
};
