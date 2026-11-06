/* SPDX-License-Identifier: GPL-3.0-or-later
 * Launcher-only compatible rumble. The two-byte ABI/mode follow the pinned
 * PS5_VKHomebrewUI pad.cpp (BlackBearReloaded/Mihawk notices retained there).
 */
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <pthread.h>
extern "C" std::uint64_t sceKernelGetProcessTime();
extern "C" int sceKernelUsleep(std::uint32_t);
namespace prospero_menu {
struct LauncherMotors {std::uint8_t large_motor=0,small_motor=0;};
static_assert(sizeof(LauncherMotors)==2);
extern "C" int scePadSetVibrationMode(int,int);
extern "C" int scePadSetVibration(int,const LauncherMotors*);
// Same native ABI as the consumer SDL trigger adapter; launcher owns its pad
// handle until the worker has reset both sides and joined before handoff.
struct LauncherTriggerCommand {std::int32_t mode=0,reserved=0;std::uint8_t data[48]{};};
struct LauncherTriggerEffect {std::uint8_t mask=3,reserved[7]{};LauncherTriggerCommand left{},right{};};
static_assert(sizeof(LauncherTriggerEffect)==120&&offsetof(LauncherTriggerEffect,right)==64);
extern "C" int scePadSetTriggerEffect(int,const LauncherTriggerEffect*);
inline constexpr unsigned page_trigger_start_zone=2,page_trigger_click_zone=3;
inline constexpr unsigned page_trigger_position(unsigned zone){return (zone*255+9)/10;}
inline unsigned page_trigger_buttons(unsigned previous,unsigned left,unsigned right){
 const auto pressed=[previous](unsigned bit,unsigned travel){
  const auto zone=(previous&bit)?page_trigger_start_zone:page_trigger_click_zone;
  return travel>=page_trigger_position(zone)?bit:0u;
 };
 return pressed(0x100,left)|pressed(0x200,right);
}
inline LauncherTriggerEffect page_trigger_effect(unsigned sides){LauncherTriggerEffect e{};for(unsigned side=0;side<2;side++)if(sides&(1u<<side)){auto& c=side?e.right:e.left;c.mode=2;c.data[0]=page_trigger_start_zone;c.data[1]=page_trigger_click_zone;c.data[2]=4;}return e;}
struct Haptics {
 pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
 pthread_t thread{};int handle=-1;bool started=false,quit=false,allowed=false;
 std::uint64_t last_poll=0,deadline=0,last_cue=0;LauncherMotors requested{};
 unsigned seen=0;bool seeded=false;unsigned trigger_ready=0;
 void control(bool enabled,std::uint64_t now){pthread_mutex_lock(&mutex);allowed=enabled;last_poll=now;if(!enabled){deadline=0;requested={};trigger_ready=0;}pthread_mutex_unlock(&mutex);}
 void observe(unsigned serial,const char* cue,bool enabled,std::uint64_t now){
  if(!seeded){seen=serial;seeded=true;return;}if(serial==seen)return;seen=serial;
  if(!enabled)return;
  LauncherMotors motors{};unsigned duration=0;
  if(!std::strcmp(cue,"move")){motors={0,32};duration=18;}
  else if(!std::strcmp(cue,"confirm")){motors={18,64};duration=45;}
  else if(!std::strcmp(cue,"back")){motors={0,42};duration=28;}
  else if(!std::strcmp(cue,"error")){motors={56,44};duration=70;}
  else if(!std::strcmp(cue,"success")){motors={26,80};duration=85;}
  if(!duration|| (last_cue&&now-last_cue<70))return;last_cue=now;
  pthread_mutex_lock(&mutex);if(allowed){requested=motors;deadline=now+duration;}pthread_mutex_unlock(&mutex);
 }
 void page_ready(unsigned available,unsigned held){pthread_mutex_lock(&mutex);trigger_ready=allowed?(((available&~held)|(trigger_ready&held))&3u):0;pthread_mutex_unlock(&mutex);}

 static void* run(void* context){auto& self=*static_cast<Haptics*>(context);LauncherMotors sent{};bool configured=false,failed=false,trigger_failed=false;unsigned sent_trigger=0;
  for(;;){
   pthread_mutex_lock(&self.mutex);bool quit=self.quit;auto now=sceKernelGetProcessTime()/1000;bool enabled=self.allowed&&now-self.last_poll<=250;LauncherMotors next=enabled&&now<self.deadline?self.requested:LauncherMotors{};unsigned trigger=enabled?self.trigger_ready:0;pthread_mutex_unlock(&self.mutex);
   if(!enabled){configured=false;failed=false;trigger_failed=false;}
   if(quit){LauncherMotors zero{};(void)scePadSetVibration(self.handle,&zero);auto off=page_trigger_effect(0);(void)scePadSetTriggerEffect(self.handle,&off);break;}
   if(enabled&&!configured&&!failed){int rc=scePadSetVibrationMode(self.handle,2);configured=rc>=0;failed=rc<0;if(failed)std::fprintf(stderr,"PS5_UI vibration mode unavailable code=%d;launcher continues\n",rc);}
   if(failed)next={};
   if(next.large_motor!=sent.large_motor||next.small_motor!=sent.small_motor){
    int rc=scePadSetVibration(self.handle,&next);if(rc<0){failed=true;LauncherMotors zero{};(void)scePadSetVibration(self.handle,&zero);next={};std::fprintf(stderr,"PS5_UI vibration unavailable code=%d;launcher continues\n",rc);}sent=next;
   }
   if(trigger_failed)trigger=0;
   if(trigger!=sent_trigger){auto effect=page_trigger_effect(trigger);int rc=scePadSetTriggerEffect(self.handle,&effect);if(rc<0){trigger_failed=true;auto off=page_trigger_effect(0);(void)scePadSetTriggerEffect(self.handle,&off);trigger=0;std::fprintf(stderr,"PS5_UI page trigger unavailable code=%d;launcher continues\n",rc);}sent_trigger=trigger;}
   (void)sceKernelUsleep(5000);
  }return nullptr;
 }
 bool start(int controller){handle=controller;quit=false;allowed=false;deadline=last_poll=last_cue=0;seeded=false;seen=0;trigger_ready=0;
  pthread_attr_t attrs;if(pthread_attr_init(&attrs)!=0)return false;int rc=pthread_attr_setstacksize(&attrs,128*1024);if(!rc)rc=pthread_create(&thread,&attrs,run,this);pthread_attr_destroy(&attrs);started=rc==0;return started;
 }
 void close(){if(!started)return;pthread_mutex_lock(&mutex);quit=true;allowed=false;deadline=0;pthread_mutex_unlock(&mutex);pthread_join(thread,nullptr);started=false;handle=-1;}
};
}
