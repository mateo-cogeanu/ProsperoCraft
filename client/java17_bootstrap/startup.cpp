/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "demo_renderer.hpp"
#include "pad.h"
#include "jni_checks.hpp"
#include <cerrno>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
using Initializer=void(*)();
extern "C" Initializer __jvm_init_array_start[],__jvm_init_array_end[];
extern "C" unsigned ps5DemoPresentationTargetHz() noexcept { return 60; }
namespace {
using ps5::demo::Canvas;
JavaVM*vm=nullptr;
JNIEnv*env=nullptr;
FILE*logfile=nullptr;
int selected=0,pending=-1,pad=-1;
unsigned previous=0;
bool initialized=false,attempted=false;
int status[4]{};
char details[4][120]{};
const char*names[]={"Initialize matched Java17 + LWJGL331", "Create real Java17 VM (-Xint)", "Initialize LWJGL331 and original Minecraft1.20 entry", "Destroy Java17 VM"};
unsigned color(unsigned r,unsigned g,unsigned b){return 0xff000000u|r|(g<<8)|(b<<16);}
void stage(const char*text){if(logfile){std::fprintf(logfile,"%s\n",text);std::fflush(logfile);}}
int print_vm(FILE*,const char*format,va_list args){if(!logfile)return 0;int n=std::vfprintf(logfile,format,args);std::fflush(logfile);return n;}
void exit_vm(int n){if(logfile){std::fprintf(logfile,"VM exit status %d\n",n);std::fflush(logfile);}}
void abort_vm(){stage("VM abort hook");}
void finish(int i,int rc,const char*text){status[i]=rc? -1:1;std::snprintf(details[i],sizeof(details[i]),"%s / code %d",text,rc);if(logfile){std::fprintf(logfile,"CHECK %d result %d: %s\n",i,rc,text);std::fflush(logfile);}}
void run(int i){
 if(i==0){
  if(initialized){finish(i,-1710,"Already initialized; relaunch to repeat");return;}
  logfile=std::fopen("/download0/mc120-java17-bootstrap.log","a");
  if(!logfile){finish(i,errno?errno:-1711,"Cannot create private probe log");return;}
  stage("ProsperoCraft1.20 Java17 bootstrap001; original game entry, no renderer/world");
  for(auto*p=__jvm_init_array_start;p!=__jvm_init_array_end;++p)if(*p)(*p)();
  initialized=true;finish(i,0,"Core constructors completed");return;
 }
 if(!initialized){finish(i,-1712,"Run core initialization first");return;}
 if(i==1){
  if(attempted){finish(i,-1713,"VM creation already attempted; relaunch");return;}
  attempted=true;
  FILE*f=std::fopen("/app0/assets/java17/lib/modules","rb");unsigned char magic[4]{};
  size_t n=f?std::fread(magic,1,4,f):0;if(f)std::fclose(f);
  if(n!=4||magic[0]!=0xda||magic[1]!=0xda||magic[2]!=0xfe||magic[3]!=0xca){finish(i,-1714,"Packaged Java17 image preflight failed");return;}
  JavaVMOption options[]={
   {const_cast<char*>("-Xint"),nullptr},{const_cast<char*>("-Xms16m"),nullptr},{const_cast<char*>("-Xmx512m"),nullptr},
   {const_cast<char*>("-XX:UseAVX=0"),nullptr},{const_cast<char*>("-XX:UseSSE=2"),nullptr},
   {const_cast<char*>("-XX:+UseSerialGC"),nullptr},{const_cast<char*>("-XX:ActiveProcessorCount=2"),nullptr},
   {const_cast<char*>("-XX:CompressedClassSpaceSize=32m"),nullptr},{const_cast<char*>("-XX:-UsePerfData"),nullptr},
   {const_cast<char*>("-Xshare:off"),nullptr},{const_cast<char*>("-Duser.timezone=UTC"),nullptr},
   {const_cast<char*>("-Dlog4j2.disableJmx=true"),nullptr},
   {const_cast<char*>("--add-modules=ALL-SYSTEM"),nullptr},
   {const_cast<char*>("-Djava.io.tmpdir=/download0"),nullptr},{const_cast<char*>("-Duser.home=/download0"),nullptr},
   {const_cast<char*>("-Djava.class.path=/app0/assets/java17/classes"),nullptr},
   {const_cast<char*>("-XX:ErrorFile=/download0/java17-hs-error-%p.log"),nullptr},
   {const_cast<char*>("vfprintf"),reinterpret_cast<void*>(&print_vm)},
   {const_cast<char*>("exit"),reinterpret_cast<void*>(&exit_vm)},{const_cast<char*>("abort"),reinterpret_cast<void*>(&abort_vm)}
  };
  JavaVMInitArgs args{};args.version=JNI_VERSION_1_8;args.options=options;args.nOptions=sizeof(options)/sizeof(options[0]);args.ignoreUnrecognized=JNI_FALSE;
  stage("Entering genuine Java17 JNI_CreateJavaVM");
  int rc=JNI_CreateJavaVM(&vm,reinterpret_cast<void**>(&env),&args);
  if(rc==JNI_OK&&(!vm||!env))rc=-1715;
  if(rc!=JNI_OK){vm=nullptr;env=nullptr;}
  finish(i,rc,"VM creation returned");return;
 }
 if(!vm||!env){finish(i,-1716,"Create the VM first");return;}
 if(i==2){
  static unsigned char bytes[65536];FILE*f=std::fopen("/app0/assets/java17/classes/HelloLts.class","rb");
  size_t n=f?std::fread(bytes,1,sizeof(bytes),f):0;bool bad=!f||std::ferror(f)||!std::feof(f);if(f)std::fclose(f);
  if(bad){finish(i,-1717,"Probe class read failed");return;}
  stage("Running original Minecraft1.20 argument/bootstrap and genuine331 JNI");int rc=ps5_lts_probe::run(env,bytes,n);
  if(env->ExceptionCheck()){env->ExceptionDescribe();env->ExceptionClear();}
  finish(i,rc,"Original1.20 entry, exact331 owner, native memory and Java17 modules");return;
 }
 stage("Entering DestroyJavaVM");int rc=vm->DestroyJavaVM();if(rc==JNI_OK){vm=nullptr;env=nullptr;}
 finish(i,rc,"DestroyJavaVM returned; relaunch for another VM");
}
bool update()noexcept{
 if(pending>=0){int i=pending;pending=-1;run(i);return true;}
 if(pad<0)return false;
 PadSample samples[64]{};int count=scePadRead(pad,samples,64);
 if(count<0||count>64)return false;
 bool changed=false;
 for(int i=0;i<count;++i){
  unsigned buttons=samples[i].connected&&!(samples[i].buttons&0x80000000u)?samples[i].buttons:0;
  unsigned pressed=buttons&~previous;previous=buttons;
  if(pressed&0x10){selected=(selected+3)%4;changed=true;}
  if(pressed&0x40){selected=(selected+1)%4;changed=true;}
  if((pressed&0x4000)&&status[selected]==0){status[selected]=2;pending=selected;return true;}
 }
 return changed;
}
void draw(Canvas&c)noexcept{
 c.gradient(color(16,28,42),color(8,13,22));
 c.label(100,65,"Minecraft1.20 / Java17 bootstrap - 01.000.001",54,color(235,243,250));
 c.label(103,151,"BOOT TEST ONLY: original1.20 initialization. No playable menu/world yet.",24,color(157,175,193));
 for(int i=0;i<4;++i){int y=245+i*125;
  if(selected==i)c.rounded(95,y-5,1730,106,20,color(101,170,215));
  c.rounded(100,y,1720,96,18,color(26,38,54));
  c.label(126,y+12,names[i],30,color(235,243,250));
  c.label(126,y+57,details[i][0]?details[i]:"D-pad to select, X to run",20,color(157,175,193));
  c.label(1650,y+26,status[i]==1?"PASS":status[i]<0?"FAIL":status[i]==2?"RUN":"--",24,status[i]==1?color(100,219,160):color(235,191,115));
 }
 c.label(103,837,"Run all four rows in order. This checks startup, not rendering or worlds.",25,color(157,175,193));
 c.label(103,897,"Reports: download0/mc120-java17-bootstrap.log and java17-vm-trace.log",22,color(157,175,193));
 c.label(103,967,"If a stage hangs or crashes: close with PS, reopen, and report the stage.",22,color(157,175,193));
}
}
int main(){
 sceUserServiceInitialize(nullptr);int user=-1;
 if(sceUserServiceGetInitialUser(&user)>=0&&scePadInit()>=0)pad=scePadOpen(user,0,0,nullptr);
 ps5::demo::run_ui(draw,update,"Minecraft1.20 Java17 bootstrap ready");
 return 0;
}
