/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "demo_renderer.hpp"
#include "pad.h"
#include "jni_checks.hpp"
#include <cerrno>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <cstdlib>
#include <unistd.h>
extern "C" int ps5shaderc_fault_begin(void);
extern "C" unsigned ps5shaderc_fault_extended_status(unsigned*);
extern "C" void ps5shaderc_fault_end(void);
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
void JNICALL java_stage(JNIEnv*,jclass,jint index){
 const char*points[]={"JAVA: entered run", "JAVA: before Path.of", "JAVA: before writer open", "JAVA: writer opened", "JAVA: basics passed", "JAVA: before RuntimeMXBean", "JAVA: RuntimeMXBean passed", "JAVA: before LWJGL331", "JAVA: LWJGL331 passed", "JAVA: before original Main", "JAVA: before classpath manifest", "JAVA: verified manifest parsed", "JAVA: before game classloader", "JAVA: game classloader ready", "JAVA: original Main class initialized"};
 if(index>=0&&index<15)stage(points[index]);else stage("JAVA: unknown diagnostic stage");
}
void report_exception(JNIEnv*e,jthrowable error,int depth){
 if(!error||depth>2)return;
 jclass type=e->GetObjectClass(error),class_type=e->FindClass("java/lang/Class");
 jmethodID name=class_type?e->GetMethodID(class_type,"getName","()Ljava/lang/String;"):nullptr;
 jstring text=name?static_cast<jstring>(e->CallObjectMethod(type,name)):nullptr;
 const char*utf=text&&!e->ExceptionCheck()?e->GetStringUTFChars(text,nullptr):nullptr;
 const char*allow[]={"java.lang.AssertionError","java.lang.LinkageError","java.lang.UnsatisfiedLinkError","java.lang.NoSuchMethodError","java.lang.NoClassDefFoundError","java.lang.OutOfMemoryError","java.lang.ExceptionInInitializerError","java.lang.IllegalStateException","java.lang.IllegalArgumentException","java.lang.UnsupportedOperationException","java.lang.reflect.InvocationTargetException","java.io.IOException","java.io.FileNotFoundException","java.nio.file.NoSuchFileException","java.nio.file.AccessDeniedException","java.lang.NullPointerException"};
 const char*label="other/unclassified throwable";
 if(utf)for(const char*v:allow)if(std::strcmp(utf,v)==0){label=v;break;}
 if(logfile){std::fprintf(logfile,"JAVA exception class depth%d: %s\n",depth,label);std::fflush(logfile);}
 if(utf)e->ReleaseStringUTFChars(text,utf);
 if(text)e->DeleteLocalRef(text);if(class_type)e->DeleteLocalRef(class_type);
 if(e->ExceptionCheck())e->ExceptionClear();
 jmethodID getter=type?e->GetMethodID(type,"getCause","()Ljava/lang/Throwable;"):nullptr;
 jthrowable cause=getter?static_cast<jthrowable>(e->CallObjectMethod(error,getter)):nullptr;
 if(e->ExceptionCheck())e->ExceptionClear();
 else if(cause&&cause!=error)report_exception(e,cause,depth+1);
 if(cause)e->DeleteLocalRef(cause);if(type)e->DeleteLocalRef(type);
}
int register_stage(JNIEnv*e,jclass klass){
 JNINativeMethod n{const_cast<char*>("nativeStage"),const_cast<char*>("(I)V"),reinterpret_cast<void*>(&java_stage)};
 return e->RegisterNatives(klass,&n,1)==JNI_OK?0:-1722;
}
int print_vm(FILE*,const char*format,va_list args){if(!logfile)return 0;int n=std::vfprintf(logfile,format,args);std::fflush(logfile);return n;}
void exit_vm(int n){if(logfile){std::fprintf(logfile,"VM exit status %d\n",n);std::fflush(logfile);}}
void abort_vm(){stage("VM abort hook");}
void finish(int i,int rc,const char*text){status[i]=rc? -1:1;std::snprintf(details[i],sizeof(details[i]),"%s / code %d",text,rc);if(logfile){std::fprintf(logfile,"CHECK %d result %d: %s\n",i,rc,text);std::fflush(logfile);}}
void run(int i){
 if(i==0){
  if(initialized){finish(i,-1710,"Already initialized; relaunch to repeat");return;}
  logfile=std::fopen("/download0/mc120-java17-bootstrap.log","a");
  if(!logfile){finish(i,errno?errno:-1711,"Cannot create private probe log");return;}
  stage("ProsperoCraft1.20 Java17 bootstrap008; original game entry, no renderer/world");
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
   {const_cast<char*>("-Xint"),nullptr},{const_cast<char*>("-Xms16m"),nullptr},{const_cast<char*>("-Xmx128m"),nullptr},
   {const_cast<char*>("-XX:UseAVX=0"),nullptr},{const_cast<char*>("-XX:UseSSE=2"),nullptr},
   {const_cast<char*>("-XX:+UseSerialGC"),nullptr},{const_cast<char*>("-XX:ActiveProcessorCount=2"),nullptr},
   {const_cast<char*>("-XX:CompressedClassSpaceSize=32m"),nullptr},{const_cast<char*>("-XX:-UsePerfData"),nullptr},
   {const_cast<char*>("-Xshare:off"),nullptr},{const_cast<char*>("-Duser.timezone=UTC"),nullptr},
   {const_cast<char*>("-Dlog4j2.disableJmx=true"),nullptr},
   {const_cast<char*>("-Dsun.nio.fs.chdirAllowed=true"),nullptr},
   {const_cast<char*>("--add-modules=ALL-SYSTEM"),nullptr},
   {const_cast<char*>("-Djava.io.tmpdir=/download0"),nullptr},{const_cast<char*>("-Duser.home=/download0"),nullptr},
   {const_cast<char*>("-Djava.class.path=/app0/assets/java17/classes"),nullptr},
   {const_cast<char*>("-XX:ErrorFile=/download0/java17-hs-error-%p.log"),nullptr},
   {const_cast<char*>("vfprintf"),reinterpret_cast<void*>(&print_vm)},
   {const_cast<char*>("exit"),reinterpret_cast<void*>(&exit_vm)},{const_cast<char*>("abort"),reinterpret_cast<void*>(&abort_vm)}
  };
  JavaVMInitArgs args{};args.version=JNI_VERSION_1_8;args.options=options;args.nOptions=sizeof(options)/sizeof(options[0]);args.ignoreUnrecognized=JNI_FALSE;
  // This diagnostic-only process uses its own title-local fault report.
  if(getenv("PROSPERO_DIAGNOSTIC_ROOT")&&unsetenv("PROSPERO_DIAGNOSTIC_ROOT")!=0){finish(i,-1720,"Cannot select private fault log");return;}
  int handlers=ps5shaderc_fault_begin();unsigned errors=0;
  unsigned owned=ps5shaderc_fault_extended_status(&errors);
  if(logfile){std::fprintf(logfile,"Fault recorder handlers=%d owned=0x%x errors=0x%x anchor=%p\n",handlers,owned,errors,reinterpret_cast<void*>(&run));std::fflush(logfile);}
  if(handlers!=4){ps5shaderc_fault_end();finish(i,-1721,"Incomplete startup fault recorder");return;}
  stage("Entering genuine Java17 JNI_CreateJavaVM");
  int rc=JNI_CreateJavaVM(&vm,reinterpret_cast<void**>(&env),&args);
  ps5shaderc_fault_end();
  if(rc==JNI_OK&&(!vm||!env))rc=-1715;
  if(rc!=JNI_OK){vm=nullptr;env=nullptr;}
  finish(i,rc,"VM creation returned");return;
 }
 if(!vm||!env){finish(i,-1716,"Create the VM first");return;}
 if(i==2){
  static unsigned char bytes[65536];FILE*f=std::fopen("/app0/assets/java17/classes/HelloLts.class","rb");
  size_t n=f?std::fread(bytes,1,sizeof(bytes),f):0;bool bad=!f||std::ferror(f)||!std::feof(f);if(f)std::fclose(f);
  if(bad){finish(i,-1717,"Probe class read failed");return;}
  stage("Installing row3 fault scope and entering JNI consumer checks");
  int handlers=ps5shaderc_fault_begin();
  if(handlers!=4){ps5shaderc_fault_end();finish(i,-1723,"Incomplete row3 fault recorder");return;}
  int rc=ps5_lts_probe::run(env,bytes,n,stage,register_stage);
  if(env->ExceptionCheck()){jthrowable failure=env->ExceptionOccurred();env->ExceptionClear();report_exception(env,failure,0);env->DeleteLocalRef(failure);if(env->ExceptionCheck())env->ExceptionClear();}
  ps5shaderc_fault_end();
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
 c.label(100,65,"Minecraft1.20 / Java17 bootstrap - 01.000.008",54,color(235,243,250));
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
 // Preserve prior bytes and make this unauthenticated probe's diagnostics readable
 // by the FTP service. Never touch account files or another title's storage.
 const char*diagnostics[]={"/download0/mc120-java17-bootstrap.log","/download0/java17-vm-trace.log","/download0/mc120-java17-fault.log"};
 for(const char*path:diagnostics){
  int fd=open(path,O_CREAT|O_WRONLY|O_APPEND,0644);if(fd>=0){(void)fchmod(fd,0644);close(fd);}
 }

 sceUserServiceInitialize(nullptr);int user=-1;
 if(sceUserServiceGetInitialUser(&user)>=0&&scePadInit()>=0)pad=scePadOpen(user,0,0,nullptr);
 ps5::demo::run_ui(draw,update,"Minecraft1.20 Java17 bootstrap ready");
 return 0;
}
