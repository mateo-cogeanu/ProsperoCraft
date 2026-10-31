#!/usr/bin/env python3
"""Real pinned OpenAL mixer/backend through a deterministic host AudioOut sink."""
from pathlib import Path
import os,subprocess
from build_openal_startup_boundaries import build
ROOT=Path(__file__).resolve().parents[1]
w=ROOT/'build/openal-ps5-audio-host-test';w.mkdir(exist_ok=True)
(w/'sink.cpp').write_text(r'''
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cmath>
#include <unistd.h>
extern "C" {int client_ps5_audio_early_init_result=(-2147483647-1);int client_ps5_audio_early_port=-1;int client_ps5_audio_secondary_port=-1;}
static std::atomic<int> mode{0},opens{0},closes{0},blocks{0},nonzero{0},init{0},open_attempts{0},waits{0};
static std::atomic<long long> left{0},right{0};static std::atomic<int> primary_pcm{0},secondary_pcm{0};
extern "C" void test_audio_mode(int n){mode=n;if(n==16){client_ps5_audio_early_port=17;client_ps5_audio_secondary_port=18;opens=2;}if(n==15){client_ps5_audio_early_port=17;opens=1;}client_ps5_audio_early_init_result=(n==10||n==14)?0:n==11?static_cast<int>(0x8026000eu):n==12?static_cast<int>(0x80260002u):n==13?-41:(-2147483647-1);}
extern "C" int test_audio_blocks(){return blocks;}
extern "C" int test_audio_nonzero(){return nonzero;}
extern "C" int test_audio_port_pcm(int port){return port==17?primary_pcm.load():secondary_pcm.load();}
extern "C" int test_audio_opens(){return opens;}
extern "C" int test_audio_closes(){return closes;}
extern "C" int test_audio_inits(){return init;}
extern "C" int test_audio_waits(){return waits;}
extern "C" int test_audio_attempts(){return open_attempts;}
extern "C" int sceKernelUsleep(unsigned usec){assert(usec==50000);++waits;return mode==9?-44:0;}
extern "C" double test_audio_balance(){return double(left.load())/double(right.load());}
extern "C" int sceUserServiceGetInitialUser(int* u){*u=1;return 0;}
static std::atomic<int> capture_inits{0};
extern "C" int test_capture_inits(){return capture_inits;}
extern "C" int sceAudioInInit(){return ++capture_inits==1?0:-73;} // second init refuses; not a PS5 error-code claim
extern "C" int sceAudioInOpen(int,unsigned,unsigned,unsigned,unsigned,unsigned){return mode>=100?31:-99;}
extern "C" int sceAudioInInput(int h,void* out){assert(h==31);auto* p=static_cast<std::int16_t*>(out);for(int i=0;i<256;i++)p[i]=i%2?12000:-12000;usleep(16000);return 256;}
extern "C" int sceAudioInClose(int){return 0;}
extern "C" int sceAudioInGetSilentState(int){return 0;}
extern "C" int sceAudioInGetRerouteCount(int){return 0;}
extern "C" int sceAudioOutInit(){int n=++init;if(mode==1)return -41;if((mode==4&&n<=2)||mode==5||mode==6||mode==8||mode==9)return static_cast<int>(0x80260002u);if(mode==7)return static_cast<int>(0x8026000eu);return 0;}
extern "C" int sceAudioOutOpen(int user,int type,int index,unsigned frames,unsigned rate,unsigned format){assert(user==0xff&&type==0&&index==0&&frames==256&&rate==48000&&format==1);++open_attempts;if(mode==2||mode==8||mode==14)return -42;if(mode==16)return static_cast<int>(0x8026000du);if(mode==15&&open_attempts==1)return static_cast<int>(0x8026000du);if((mode==4&&init<=2)||mode==5||mode==9)return static_cast<int>(0x8026000fu);++opens;return 17;}
extern "C" int sceAudioOutOutput(int port,const void* data){assert(port==17||(mode==16&&port==18));if(!data)return 0;auto pcm=(const int16_t*)data;assert((uintptr_t)data%64==0);int n=++blocks;
 if(mode==3 && n>8)return -43;
 for(int i=0;i<256;++i){left+=std::abs(int(pcm[i*2]));right+=std::abs(int(pcm[i*2+1]));if(pcm[i*2]||pcm[i*2+1]){++nonzero;if(port==17)++primary_pcm;else ++secondary_pcm;}}
 usleep(1000);return 0;}
extern "C" int sceAudioOutClose(int port){assert(port==17||(mode==16&&port==18));++closes;return 0;}
''')
subprocess.run(['clang++','-std=c++17','-fsanitize=address,undefined','-fPIC','-c',str(w/'sink.cpp'),'-o',str(w/'sink.o')],check=True)
library,audit=build(host=True,speakers=True,host_objects=[w/'sink.o'])
subprocess.run(['install_name_tool','-id',str(library),str(library)],check=True)
(w/'driver.cpp').write_text(r'''
extern "C" int test_capture_inits();
#define AL_ALEXT_PROTOTYPES
#include <AL/al.h>
#include <AL/alc.h>
#include <AL/alext.h>
#include <cassert>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
extern "C" {void test_audio_mode(int);int test_audio_blocks();int test_audio_nonzero();int test_audio_port_pcm(int);int test_audio_opens();int test_audio_closes();int test_audio_inits();int test_audio_waits();int test_audio_attempts();double test_audio_balance();}
extern "C" void client_ps5_capture_enable(int);
extern "C" void client_ps5_capture_probe(char*,unsigned);
static std::atomic<int> events{0};
static void AL_APIENTRY event_callback(ALenum type,ALuint,ALuint,ALsizei,const ALchar*,void*) noexcept {assert(type==AL_EVENT_TYPE_SOURCE_STATE_CHANGED_SOFT);++events;}
extern "C" int client_ps5_audio_worker_preinit();
extern "C" int client_ps5_audio_event_preinit();
int main(int argc,char**argv){assert(client_ps5_audio_event_preinit()==0);assert(client_ps5_audio_worker_preinit()==0);assert(client_ps5_audio_worker_preinit()==0);int mode=argc>1?atoi(argv[1]):0;test_audio_mode(mode);
 if(mode==16){
  for(int cycle=0;cycle<20;++cycle){
   auto*a=alcOpenDevice(nullptr);auto*b=alcOpenDevice(nullptr);assert(a&&b&&a!=b);
   auto*ca=alcCreateContext(a,nullptr);auto*cb=alcCreateContext(b,nullptr);assert(ca&&cb);
   assert(alcMakeContextCurrent(ca));alEnable(0xdead);assert(alGetError()==AL_INVALID_VALUE);
   assert(alcMakeContextCurrent(cb));assert(alGetError()==AL_NO_ERROR);
   int before_a=test_audio_port_pcm(17),before_b=test_audio_port_pcm(18);
   ALuint buffers[2],sources[2];ALCcontext* contexts[]={ca,cb};
   for(int k=0;k<2;++k){assert(alcMakeContextCurrent(contexts[k]));alGenBuffers(1,&buffers[k]);alGenSources(1,&sources[k]);short pcm[512];for(int i=0;i<512;++i)pcm[i]=((i/16)%2?1:-1)*(k?4000:8000);alBufferData(buffers[k],AL_FORMAT_MONO16,pcm,sizeof(pcm),48000);alSourcei(sources[k],AL_BUFFER,buffers[k]);alSourcei(sources[k],AL_LOOPING,AL_TRUE);alSourcePlay(sources[k]);assert(alGetError()==AL_NO_ERROR);}
   for(int wait=0;wait<1000&&(test_audio_port_pcm(17)<before_a+256||test_audio_port_pcm(18)<before_b+256);++wait)usleep(1000);
   assert(test_audio_port_pcm(17)>=before_a+256&&test_audio_port_pcm(18)>=before_b+256);

   auto*loop=alcLoopbackOpenDeviceSOFT(nullptr);assert(loop);ALCint attrs[]={ALC_FORMAT_CHANNELS_SOFT,ALC_MONO_SOFT,ALC_FORMAT_TYPE_SOFT,ALC_SHORT_SOFT,ALC_FREQUENCY,48000,0};
   auto*cl=alcCreateContext(loop,attrs);assert(cl);alcDestroyContext(cl);assert(alcCloseDevice(loop));
   for(int k=0;k<2;++k){assert(alcMakeContextCurrent(contexts[k]));alSourceStop(sources[k]);alDeleteSources(1,&sources[k]);alDeleteBuffers(1,&buffers[k]);}alcMakeContextCurrent(nullptr);alcDestroyContext(cb);alcDestroyContext(ca);assert(alcCloseDevice(b)&&alcCloseDevice(a));
   assert(test_audio_attempts()==0&&test_audio_opens()==2&&test_audio_closes()==0);
  }
  puts("PASS two independent playback devices +loopback context x20,real late AudioOut refusal avoided via two genuine early ports,context errors isolated,all ports retained without late open");return 0;
 }
 if(mode==100){
  extern void unused();
  assert(alcCaptureOpenDevice(nullptr,48000,AL_FORMAT_MONO_FLOAT32,4096)==nullptr);
  client_ps5_capture_enable(1);
  const char* names=alcGetString(nullptr,ALC_CAPTURE_DEVICE_SPECIFIER);assert(names&&strstr(names,"PS5 system microphone"));
  for(int cycle=0;cycle<20;cycle++){
   auto* capture=alcCaptureOpenDevice(names,48000,AL_FORMAT_MONO_FLOAT32,4096);assert(capture);
   alcCaptureStart(capture);ALCint count=0;for(int n=0;n<100&&!count;n++){usleep(1000);alcGetIntegerv(capture,ALC_CAPTURE_SAMPLES,1,&count);}assert(count>=768);
   float samples[768];alcCaptureSamples(capture,samples,768);assert(alcGetError(capture)==ALC_NO_ERROR);bool nonzero=false;for(float x:samples){assert(std::isfinite(x)&&x>=-1&&x<=1);nonzero|=x!=0;}assert(nonzero);
   alcCaptureStop(capture);assert(alcCaptureCloseDevice(capture));
  }
  assert(test_capture_inits()==1);client_ps5_capture_enable(0);assert(!alcCaptureOpenDevice(nullptr,48000,AL_FORMAT_MONO_FLOAT32,4096));puts("PASS real OpenAL capture path default-off/enable/enumerate/open/start/available/float samples/stop/close x20 with one confirmed init despite repeated-init refusal; host AudioIn source only");return 0;
 }
 if(mode==101){
  auto samples_at_least=[](ALCdevice* d,ALCint n){ALCint count=0;for(int i=0;i<500&&count<n;i++){usleep(1000);alcGetIntegerv(d,ALC_CAPTURE_SAMPLES,1,&count);}return count>=n;};
  client_ps5_capture_enable(1);char result[512];client_ps5_capture_probe(result,sizeof(result));assert(strstr(result,"Input reads completed")&&test_capture_inits()==1); // launcher test initializes AudioIn first, same process
  for(int cycle=0;cycle<3;cycle++){
   // Original SVC2.6.27 order: configured "" then null fallback, no prior enumeration; 960-frame mono float32.
   auto* capture=alcCaptureOpenDevice("",48000,AL_FORMAT_MONO_FLOAT32,960);assert(capture);
   alcCaptureStart(capture);assert(samples_at_least(capture,960));float samples[960];alcCaptureSamples(capture,samples,960);assert(alcGetError(capture)==ALC_NO_ERROR);
   const char* names=alcGetString(nullptr,ALC_CAPTURE_DEVICE_SPECIFIER);assert(names&&strstr(names,"PS5 system microphone")); // listing while live
   assert(samples_at_least(capture,960));ALCint connected=0;alcGetIntegerv(capture,ALC_CONNECTED,1,&connected);assert(connected);
   alcCaptureStop(capture);ALCint left=-1;alcGetIntegerv(capture,ALC_CAPTURE_SAMPLES,1,&left);assert(left==0);alcCaptureSamples(capture,samples,left);assert(alcGetError(capture)==ALC_NO_ERROR);assert(alcCaptureCloseDevice(capture));
  }
  auto* capture=alcCaptureOpenDevice(nullptr,48000,AL_FORMAT_MONO_FLOAT32,960);assert(capture);alcCaptureStart(capture);assert(samples_at_least(capture,960));
  client_ps5_capture_enable(0);ALCint connected=1;for(int i=0;i<500&&connected;i++){usleep(1000);alcGetIntegerv(capture,ALC_CONNECTED,1,&connected);}assert(!connected); // privacy: OFF ends delivery
  ALCint left=-1;alcGetIntegerv(capture,ALC_CAPTURE_SAMPLES,1,&left);assert(left==0);usleep(40000);alcGetIntegerv(capture,ALC_CAPTURE_SAMPLES,1,&left);assert(left==0);
  alcCaptureStop(capture);assert(alcCaptureCloseDevice(capture));assert(!alcCaptureOpenDevice(nullptr,48000,AL_FORMAT_MONO_FLOAT32,960));
  client_ps5_capture_enable(1);capture=alcCaptureOpenDevice(nullptr,48000,AL_FORMAT_MONO_FLOAT32,960);assert(capture&&alcCaptureCloseDevice(capture)); // lease released, reopen works
  assert(test_capture_inits()==1);puts("PASS real OpenAL SVC-order capture: launcher probe then \"\"/null opens without enumeration x3, live enumeration keeps capture, stop drains to0, enable OFF disconnects/drops samples, lease reusable, one init; host AudioIn source only");return 0;
 }
 for(int cycle=0;cycle<(mode==3?1:3);++cycle){
  ALCdevice*d=alcOpenDevice("PS5 Speakers");
  if(mode==1||mode==2||mode==5||mode==8||mode==9||mode==14){assert(!d);assert(test_audio_opens()==0&&test_audio_closes()==0);
   if(mode==5)assert(test_audio_inits()==10&&test_audio_attempts()==10&&test_audio_waits()==9);
   else if(mode==9)assert(test_audio_inits()==1&&test_audio_attempts()==1&&test_audio_waits()==1);
   else assert(test_audio_inits()==(mode==14?0:1)&&test_audio_attempts()==(mode==1?0:1)&&test_audio_waits()==0);
   puts("PASS AudioOut unknown/init/open/permanentbusy/wait failure: real device failure, bounded attempts, no leaked port");return 0;}
  assert(d);assert(!strcmp(alcGetString(d,ALC_ALL_DEVICES_SPECIFIER),"PS5 Speakers"));
  ALCint hrtfs=-1;alcGetIntegerv(d,ALC_NUM_HRTF_SPECIFIERS_SOFT,1,&hrtfs);assert(hrtfs>=0&&alcGetError(d)==ALC_NO_ERROR);
  for(int i=0;i<hrtfs;i++)assert(alcGetStringiSOFT(d,ALC_HRTF_SPECIFIER_SOFT,i));
  ALCcontext*c=alcCreateContext(d,nullptr);assert(c&&alcMakeContextCurrent(c));
  auto debug_control=reinterpret_cast<decltype(&alDebugMessageControlEXT)>(alGetProcAddress("alDebugMessageControlEXT"));assert(debug_control);debug_control(AL_DONT_CARE_EXT,AL_DONT_CARE_EXT,AL_DONT_CARE_EXT,0,nullptr,AL_FALSE);assert(alGetError()==AL_NO_ERROR);
  alEnable(AL_SOURCE_DISTANCE_MODEL);assert(alIsEnabled(AL_SOURCE_DISTANCE_MODEL)&&alGetError()==AL_NO_ERROR);
  ALenum event_type=AL_EVENT_TYPE_SOURCE_STATE_CHANGED_SOFT;alEventCallbackSOFT(event_callback,nullptr);alEventControlSOFT(1,&event_type,AL_TRUE);assert(alGetError()==AL_NO_ERROR);int old_events=events.load();
  ALuint buffer,source;alGenBuffers(1,&buffer);alGenSources(1,&source);
  int16_t samples[4410];for(int i=0;i<4410;++i)samples[i]=(int16_t)(8000*sin(2*3.141592653589793*440*i/44100));
  alBufferData(buffer,AL_FORMAT_MONO16,samples,sizeof(samples),44100);alSourcei(source,AL_BUFFER,buffer);alSourcei(source,AL_LOOPING,AL_TRUE);alSourcePlay(source);assert(alGetError()==AL_NO_ERROR);
  int before=test_audio_nonzero();for(int i=0;i<1000&&test_audio_nonzero()<before+512;++i)usleep(1000);
  assert(test_audio_nonzero()>=before+512);for(int i=0;i<1000&&events.load()==old_events;++i)usleep(1000);assert(events.load()>old_events); // Actual resample/mixer -> stereo PCM,not a fabricated callback.
  if(mode==3){for(int i=0;i<1000&&test_audio_blocks()<=8;++i)usleep(1000);usleep(10000);ALCint connected=1;alcGetIntegerv(d,ALC_CONNECTED,1,&connected);assert(!connected);}
  else {
   alcDevicePauseSOFT(d);int stopped=test_audio_blocks();usleep(10000);assert(test_audio_blocks()==stopped);
   alcDeviceResumeSOFT(d);for(int i=0;i<1000&&test_audio_blocks()==stopped;++i)usleep(1000);assert(test_audio_blocks()>stopped);
   alSourceStop(source);alDeleteSources(1,&source);alDeleteBuffers(1,&buffer);assert(alGetError()==AL_NO_ERROR);
  }
  alcMakeContextCurrent(nullptr);alcDestroyContext(c);assert(alcCloseDevice(d));
  assert(test_audio_opens()==1&&test_audio_closes()==(mode==3?1:0));
 }
 assert(test_audio_inits()==(mode==10||mode==11||mode==15?0:mode==4?3:1));assert(test_audio_waits()==(mode==4?2:0));if(mode==15){assert(test_audio_attempts()==0);ALCdevice* reopened=alcOpenDevice("PS5 Speakers");assert(reopened&&alcCloseDevice(reopened));assert(test_audio_attempts()==0&&test_audio_opens()==1&&test_audio_closes()==0);}assert(test_audio_balance()>0.8&&test_audio_balance()<1.2);
 printf("PASS real OpenAL PS5 backend:3cycles or error-disconnect,pause/resume,44100Hz mono440Hz -> actual48000Hz stereoS16 PCM,portformat/alignment,join/retained-port/init lifetime,nonzero=%d;host AudioOut fixture,not audible PS5 acceptance\n",test_audio_nonzero());
}
''')
source=ROOT/'.tools/openal-soft-src'
subprocess.run(['clang++','-std=c++17','-fsanitize=address,undefined','-I'+str(source/'include'),str(w/'driver.cpp'),str(library),'-Wl,-rpath,'+str(library.parent),'-o',str(w/'check')],check=True)
for mode in [1,2,0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,100,101]:
 result=subprocess.run([str(w/'check'),str(mode)],env=dict(os.environ,ALSOFT_DRIVERS='ps5',ALSOFT_LOGLEVEL='2',ALSOFT_LOCAL_PATH=str(w)),capture_output=True,text=True,timeout=30)
 (w/('mode'+str(mode)+'.log')).write_text(result.stdout+result.stderr)
 if result.returncode:print(result.stdout+result.stderr)
 result.check_returncode();print(result.stdout.strip())
