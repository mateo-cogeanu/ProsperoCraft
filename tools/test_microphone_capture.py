#!/usr/bin/env python3
"""Actual bounded capture core with controlled AudioIn boundary, ASan/UBSan."""
from pathlib import Path
from host_toolchain import executable
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=r'''
#include "ps5_capture.hpp"
#include <cassert>
#include <thread>
#include <atomic>
#include <cmath>
#include <string_view>
using ps5audio::Capture;
static int user_id=7,init_rc=0,open_rc=9,close_rc=0,input_rc=256,route=3,mute=0,opens=0,closes=0,reads=0,inits=0,users=0;
static bool mute_after=false,route_after=false;
int user(int*p){++users;*p=user_id;return 0;}int init(){++inits;return init_rc;}
int open(int u,unsigned t,unsigned i,unsigned n,unsigned r,unsigned f){assert(u==7&&t==1&&i==0&&n==256&&r==16000&&f==1);++opens;return open_rc;}
int close(int h){assert(h==9);++closes;return close_rc;}
int silent(int h){assert(h==9);return mute;}int reroute(int h){assert(h==9);return route;}
int input(int h,void*p){assert(h==9);++reads;auto* pcm=static_cast<std::int16_t*>(p);for(int i=0;i<256;i++)pcm[i]=i%2?32767:-32768;if(mute_after)mute=1;if(route_after)++route;return input_rc;}
int main(){
 // The actual static callback gate must outlive a destroyed target after join refusal.
 {ps5audio::CaptureWorkerLifetime lifetime;std::atomic<bool> entered{false},release{false},detached{false};
  struct Target{std::atomic<bool>* entered;std::atomic<bool>* release;int calls=0;};auto* target=new Target{&entered,&release};
  lifetime.attach(target,[](void* p,const char*){auto& t=*static_cast<Target*>(p);++t.calls;*t.entered=true;while(!t.release->load())std::this_thread::yield();});
  std::thread producer([&]{lifetime.disconnect("first");});while(!entered)std::this_thread::yield();
  std::thread cleanup([&]{lifetime.detach();detached=true;});
  while(!lifetime.kill.load())std::this_thread::yield();assert(!detached);release=true;producer.join();cleanup.join();assert(detached&&target->calls==1);delete target;
  lifetime.disconnect("late error after target destruction"); // Must not dereference target.
 }
 Capture c;ps5audio::CaptureApi api{user,init,open,input,silent,reroute,close};
 init_rc=-1;assert(!c.open(api)&&opens==0&&inits==1&&std::string_view(c.errorStage)=="init");init_rc=0;open_rc=-2;assert(!c.open(api)&&inits==2&&std::string_view(c.errorStage)=="open");open_rc=9;
 init_rc=-99; // Successful process initialization must survive enumeration/reopen.

 assert(c.open(api)&&c.pump()&&c.available()==768);float samples[768];assert(c.take(samples,768,true));assert(samples[0]==-1.f&&samples[3]>-.334f&&samples[3]<-.333f);assert(!c.take(samples,1,true));assert(c.peak==32768&&c.nonzero==256);
 mute=1;assert(c.pump());assert(c.take(samples,768,true));for(float s:samples)assert(s==0);assert(c.silent_blocks==1);
 mute=0;mute_after=true;assert(c.pump());assert(c.take(samples,768,true));for(float s:samples)assert(s==0);mute_after=false;mute=0;
 route_after=true;assert(c.pump());assert(c.take(samples,768,true));for(float s:samples)assert(s==0);route_after=false;
 for(int n=0;n<100;n++)assert(c.pump());assert(c.available()==Capture::Capacity&&c.dropped>0);c.clear();assert(c.available()==0);
 input_rc=-5;assert(!c.pump()&&c.error==-5&&c.available()==0&&!c.active());input_rc=256;
 assert(c.close()&&c.handle==-1&&!c.active());
 input_rc=100;assert(c.open(api)&&c.active()&&!c.pump()&&c.error==100&&std::string_view(c.errorStage)=="input-short"&&!c.active());input_rc=256;assert(c.close());
 {int before=opens;user_id=-3;assert(!c.open(api)&&c.error==-1&&std::string_view(c.errorStage)=="initial-user-invalid"&&opens==before&&c.handle==-1);user_id=7;}
 {ps5audio::WorkerOwnership w;int joins=0;assert(w.stop([&]{++joins;return 0;})&&joins==0);w.started=true;assert(w.stop([&]{++joins;return 0;})&&joins==1&&!w.started);
  w.started=true;assert(!w.stop([&]{++joins;return 35;})&&joins==2&&w.uncertain&&w.join_error==35&&!w.started);assert(!w.stop([&]{++joins;return 0;})&&joins==2);}Capture uncertain;init_rc=0;assert(uncertain.open(api));init_rc=-99;close_rc=-8;assert(!uncertain.close()&&uncertain.handle==9&&!uncertain.healthy);int before_closes=closes;close_rc=0;assert(!uncertain.close()&&closes==before_closes&&!uncertain.active());assert(!uncertain.open(api));
 for(int n=0;n<200;n++){assert(c.open(api)&&c.pump()&&c.close());}
 assert(c.open(api));std::atomic<bool> done{false};std::thread producer([&]{for(int i=0;i<5000;i++)assert(c.pump());done=true;});std::thread consumer([&]{float out[96];while(!done){unsigned n=std::min(96u,c.available());if(n)assert(c.take(out,n,true));}});producer.join();consumer.join();assert(c.close());
 mute=-7;assert(c.open(api));assert(!c.pump());assert(c.close());
 assert(opens>=202&&closes>=203&&inits==3);
 {Capture early;mute=0;int before_inits=inits,before_opens=opens,before_reads=reads,before_users=users;
  init_rc=-8;assert(!early.initialize(api)&&!early.initialized&&early.error==-8&&inits==before_inits+1);
  init_rc=0;assert(early.initialize(api)&&early.initialized&&inits==before_inits+2);
  init_rc=-99;assert(early.initialize(api)&&inits==before_inits+2);assert(opens==before_opens&&reads==before_reads&&early.handle==-1&&users==before_users);
  assert(early.open(api)&&early.pump());int park_opens=opens,park_closes=closes,park_reads=reads;
  assert(early.park()&&early.prepared()&&early.available()==0&&early.handle==9);
  for(int n=0;n<20;++n){assert(early.open(api)&&!early.prepared()&&early.pump()&&early.park());}
  assert(opens==park_opens&&closes==park_closes&&reads==park_reads+20&&early.prepared());
  assert(early.close()&&!early.prepared()&&early.handle==-1&&inits==before_inits+2);
  assert(!early.park());

 }

}
'''
with tempfile.TemporaryDirectory() as td:
    w=Path(td);(w/'test.cpp').write_text(source)
    subprocess.run([executable('clang++',env='CXX'),'-std=c++20','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-I'+str(ROOT/'client/ports/openal'),str(w/'test.cpp'),'-o',str(w/'test')],check=True)
    subprocess.run([str(w/'test')],check=True,timeout=30)
print('PASS actual capture core init/open/read/partial and short-read failure, invalid-user stage, active-owner state, failed-join pinning, failed-close retained ownership, mute-before/after/route silence, 16→48k interpolation, bounded overflow, 200 restarts and 5000-block producer/consumer; host OS doubles, no PS5 speech claim')
