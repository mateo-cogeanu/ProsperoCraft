/* SPDX-License-Identifier: LGPL-2.0-or-later */
#pragma once
#include <array>
#include <atomic>
#include <cstdint>
#include <algorithm>
#include <mutex>
#include "ps5_audio_mutex.hpp"
namespace ps5audio {
// OS boundary is injected for actual-code host failure/lifecycle tests.
struct CaptureApi {
 int (*initialUser)(int*);int (*init)();int (*open)(int,unsigned,unsigned,unsigned,unsigned,unsigned);
 int (*input)(int,void*);int (*silent)(int);int (*reroute)(int);int (*close)(int);
};
struct Capture {
 static constexpr unsigned Grain=256,InputRate=16000,Rate=48000,Capacity=16384;
 ps5audio::Mutex mutex;CaptureApi api{};int handle=-1,route=-1,error=0;
 const char* errorStage="none";bool initialized=false;
 bool healthy=false,close_uncertain=false;float previous=0;bool previous_valid=false;
 std::array<float,Capacity> ring{};unsigned read=0,count=0;
 std::uint64_t blocks=0,nonzero=0,silent_blocks=0,dropped=0;int peak=0;
 alignas(64) std::array<std::int16_t,Grain> pcm{};
 // Service preparation only: no user lookup, port open, read or capture opt-in.
 // Startup calls this before JVM/game pressure. Failed init remains retryable.
 bool initializeLocked(){
  if(initialized)return true;errorStage="init";error=api.init();if(error<0)return false;
  initialized=true;error=0;errorStage="none";return true;
 }
 bool initialize(CaptureApi calls){
  const auto lock=std::lock_guard{mutex};if(initialized)return true;api=calls;return initializeLocked();
 }
 bool open(CaptureApi calls){
  const auto lock=std::lock_guard{mutex};if(handle>=0){errorStage="owned-port";return false;}api=calls;
  int user=-1;errorStage="initial-user";error=api.initialUser(&user);if(error<0)return false;
  if(user<0){errorStage="initial-user-invalid";error=-1;return false;} // No user identifier in diagnostics.
  // AudioIn is process-lifetime. Enumeration/test/open share this owner: once
  // initialization actually succeeds, do not initialize it again per port.
  if(!initializeLocked())return false;
  errorStage="open";
  handle=api.open(user,1,0,Grain,InputRate,1); // PS5 General, index0, S16 mono profile.
  if(handle<0){error=handle;return false;}
  errorStage="reroute";route=api.reroute(handle);if(route<0){error=route;closeLocked();return false;}
  healthy=true;error=0;errorStage="none";read=count=0;previous_valid=false;blocks=nonzero=silent_blocks=dropped=0;peak=0;return true;
 }
 bool closeLocked(){if(handle<0)return true;if(close_uncertain)return false;int rc=api.close(handle);if(rc<0){error=rc;errorStage="close";healthy=false;close_uncertain=true;return false;}handle=-1;healthy=false;read=count=0;previous_valid=false;return true;}
 bool close(){const auto lock=std::lock_guard{mutex};return closeLocked();}
 // One producer. Caller joins it before close. Silence queries before AND after
 // input conservatively discard the complete block during mute/route changes.
 bool pump(){
  if(handle<0||!healthy)return false;int before=api.silent(handle),route_before=api.reroute(handle);
  int result=api.input(handle,pcm.data());int after=api.silent(handle),route_after=api.reroute(handle);
  const auto lock=std::lock_guard{mutex};
  if(result!=int(Grain)||before<0||after<0||route_before<0||route_after<0){errorStage=result<0?"input":result!=int(Grain)?"input-short":before<0?"silent-before":after<0?"silent-after":route_before<0?"reroute-before":"reroute-after";error=result!=int(Grain)?result:before<0?before:after<0?after:route_before<0?route_before:route_after;healthy=false;read=count=0;return false;}
  bool silent=before!=0||after!=0||route_before!=route_after||route_after!=route;
  if(route_after!=route){route=route_after;read=count=0;}++blocks;
  if(silent){++silent_blocks;std::fill(pcm.begin(),pcm.end(),0);previous_valid=false;read=count=0;}
  for(auto sample:pcm){int magnitude=sample<0?-int(sample):int(sample);if(magnitude){++nonzero;peak=std::max(peak,magnitude);}float current=float(sample)/32768.f;if(!previous_valid){previous=current;previous_valid=true;}
   // Exact rational 16->48k interpolation, bounded history; no rate drift.
   for(int step=1;step<=3;step++){if(count==Capacity){read=(read+1)%Capacity;--count;++dropped;}ring[(read+count)%Capacity]=previous+(current-previous)*(float(step)/3.f);++count;}previous=current;
  }
  return true;
 }
 // Device exists and is owned by a live, healthy capture (not a pinned cleanup).
 bool active(){const auto lock=std::lock_guard{mutex};return handle>=0&&healthy&&!close_uncertain;}
 unsigned available(){const auto lock=std::lock_guard{mutex};return count;}
 bool take(void* output,unsigned frames,bool floating){
  const auto lock=std::lock_guard{mutex};if(frames>count)return false;
  for(unsigned i=0;i<frames;i++){float value=ring[read];if(floating)static_cast<float*>(output)[i]=value;else static_cast<std::int16_t*>(output)[i]=std::int16_t(std::clamp(value*32768.f,-32768.f,32767.f));read=(read+1)%Capacity;}count-=frames;return true;
 }
 void clear(){const auto lock=std::lock_guard{mutex};read=count=0;previous_valid=false;}
};
// Static-lifetime callback gate. A producer must never retain a backend pointer:
// even failed join cannot prevent OpenAL from destroying its backend/device.
// Detach waits for an in-flight callback before its target can be destroyed.
struct CaptureWorkerLifetime {
 std::atomic<bool> kill{true};
 Mutex callback_mutex;void* target=nullptr;void (*callback)(void*,const char*)=nullptr;
 void attach(void* value,void (*notify)(void*,const char*)){
  const auto lock=std::lock_guard{callback_mutex};target=value;callback=notify;kill.store(false,std::memory_order_release);
 }
 void detach(){
  kill.store(true,std::memory_order_release);const auto lock=std::lock_guard{callback_mutex};target=nullptr;callback=nullptr;
 }
 void disconnect(const char* message){
  const auto lock=std::lock_guard{callback_mutex};if(target&&callback&&!kill.load(std::memory_order_acquire))callback(target,message);
 }
};
// Producer-thread ownership. A failed join means the producer may still be
// inside pump(): the port must never be closed or reused (lease stays pinned
// until app restart). The thread handle is not joined twice.
struct WorkerOwnership {
 bool started=false,uncertain=false;int join_error=0;
 template<class Join> bool stop(Join&& join){if(started){started=false;int rc=join();if(rc){join_error=rc;uncertain=true;}}return !uncertain;}
};
}
