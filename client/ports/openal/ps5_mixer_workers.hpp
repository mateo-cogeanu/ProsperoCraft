/* SPDX-License-Identifier: LGPL-2.0-or-later
 * Two process-lifetime mixer workers, reserved before JVM/native heap pressure.
 * Jobs retain their lease until completion is observed; idle workers never touch
 * a device. No thread creation/allocation in assign, wait or release.
 */
#pragma once
#include <pthread.h>
#include <atomic>
#include <cerrno>
#include <ctime>
namespace ps5audio {
struct MixerWorkers {
 struct Slot {
  std::atomic<bool> leased{false};
  std::atomic<unsigned> state{0}; // 0=idle/completed,1=job ready,2=running
  void (*run)(void*)=nullptr;void* context=nullptr;pthread_t thread{};
 };
 Slot slots[2];
 std::atomic<int> initialized{0}; // 0=not initialized,1=initializing,2=ready,-errno=failure
 static void pause() noexcept {const timespec delay{0,1000000};nanosleep(&delay,nullptr);}
 static void* loop(void* opaque) noexcept {
  auto& slot=*static_cast<Slot*>(opaque);
  for(;;){
   if(slot.state.load(std::memory_order_acquire)!=1){pause();continue;}
   slot.state.store(2,std::memory_order_relaxed);
   slot.run(slot.context);
   slot.state.store(0,std::memory_order_release);
  }
 }
 int preinit() noexcept {
  int expected=0;
  if(!initialized.compare_exchange_strong(expected,1,std::memory_order_acq_rel)){
   while((expected=initialized.load(std::memory_order_acquire))==1)pause();
   return expected==2?0:-expected;
  }
  pthread_attr_t attr;int rc=pthread_attr_init(&attr);
  if(rc){initialized.store(-rc,std::memory_order_release);return rc;}
  rc=pthread_attr_setstacksize(&attr,256*1024);
  if(!rc)for(auto& slot:slots){rc=pthread_create(&slot.thread,&attr,loop,&slot);if(rc)break;}
  pthread_attr_destroy(&attr);
  // On partial failure any already-created worker stays idle for process lifetime.
  initialized.store(rc?-rc:2,std::memory_order_release);return rc;
 }
 Slot* assign(void (*run)(void*),void* context) noexcept {
  if(initialized.load(std::memory_order_acquire)!=2)return nullptr;
  for(auto& slot:slots){bool expected=false;
   if(slot.leased.compare_exchange_strong(expected,true,std::memory_order_acq_rel)){
    slot.run=run;slot.context=context;slot.state.store(1,std::memory_order_release);return &slot;
   }
  }
  return nullptr;
 }
 void wait_release(Slot* slot) noexcept {
  if(!slot)return;
  while(slot->state.load(std::memory_order_acquire)!=0)pause();
  slot->run=nullptr;slot->context=nullptr;slot->leased.store(false,std::memory_order_release);
 }
};
}
