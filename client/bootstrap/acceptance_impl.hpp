// Included once by a variant bootstrap after its constexpr Config.
/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "demo_renderer.hpp"
#include "log_share.hpp"
#include "log_retention.hpp"
#include "buffer_bridge.hpp"
#include "client_classpath.hpp"
#include "pad.h"
#include <atomic>
#include <cstdarg>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include "jni.h"
#include "native_trace.hpp"
static void notify(const char* text);
using Initializer=void (*)();
extern "C" Initializer __jvm_init_array_start[],__jvm_init_array_end[];
#include <sys/mman.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <unistd.h>
extern "C" std::uint64_t sceKernelGetProcessTime();
extern "C" int sceKernelUsleep(std::uint32_t);
// File-open diagnostics specific to this probe; the real platform API is used.
static char native_open_error[192]{};
#ifdef __PROSPERO__
extern "C" int __real_open(const char *,int,...);
extern "C" int __wrap_open(const char *path,int flags,...) {
 mode_t mode=0;
 if(flags&O_CREAT) {va_list args;va_start(args,flags);mode=static_cast<mode_t>(va_arg(args,int));va_end(args);}
 int fd=__real_open(path,flags,mode);
 int error=errno;
 if(fd<0 && ps5_native_trace::enabled.load() &&
    pthread_equal(ps5_native_trace::owner,pthread_self()) &&
    !ps5_vm_trace_io_active() && path && std::strncmp(path,"/download0/",11)==0) {
  // IO guard prevents the trace writer's own open from replacing this result.
  Ps5TraceIOScope guard;
  std::snprintf(native_open_error,sizeof(native_open_error),
    "Native open: flags=0x%X mode=0%o fd=%d errno=%d",flags,static_cast<unsigned>(mode),fd,error);
  ps5_vm_trace(native_open_error);
 }
 errno=error;return fd;
}
#endif
namespace {
constexpr int test_count=5;
const char *names[]={"Initialize embedded runtime","Create Java VM for native acceptance","Verify original client artifacts",acceptance.check_name,"Destroy Java VM"};
int status[test_count]{}; // 0 untested, 1 pass, -1 fail, 2 running
char messages[test_count][104]{};
int pad=-1;
bool initialized=false;
JavaVM *java_vm=nullptr;
JNIEnv *java_env=nullptr;
FILE *startup_log=nullptr;
constexpr const char* build_version=acceptance.version;
char run_id[96]="No client run initialized";
void session_status(const char* state) {
 char note[512];std::snprintf(note,sizeof(note),"Title: PPSA99874\nBuild: %s\nRun: %s\nState: %s\n",build_version,run_id,state);
 ps5::log_share::write_note("/download0/probe-session.txt",note);
}
char exception_detail[1536]{};
char previous_log[7][160]={{},{},{},{},{},{},"No previous startup log."};
struct NativeTraceScope {
 NativeTraceScope() {
#ifdef __PROSPERO__
  ps5_vm_reset_native_call_record();
#endif
  ps5_native_trace::enable();
  ps5_native_trace::quiet();
 }
 ~NativeTraceScope() {ps5_native_trace::disable();}
};
void log_stage(const char *stage) {
#ifdef __PROSPERO__
 ps5_vm_trace(stage);
#endif
 if(startup_log) {std::fprintf(startup_log,"STAGE: %s\n",stage);std::fflush(startup_log);}
}
void network_checkpoint(JNIEnv *env,jclass,jstring stage) {
 const char *utf=env->GetStringUTFChars(stage,nullptr);
 if(!utf) return;
 log_stage(utf);
 if(std::strncmp(utf,acceptance.notification_prefix,std::strlen(acceptance.notification_prefix))==0)notify(utf);
 env->ReleaseStringUTFChars(stage,utf);
}
int vm_print(FILE *,const char *format,va_list arguments) {
 if(!startup_log) return 0;
 int count=std::vfprintf(startup_log,format,arguments);std::fflush(startup_log);return count;
}
void vm_exit(int code) {
 if(startup_log) {std::fprintf(startup_log,"VM EXIT: %d\n",code);std::fflush(startup_log);}
}
void vm_abort() {log_stage("VM ABORT");}
bool read_last_line(const char *path) {
 FILE *file=std::fopen(path,"r");if(!file) return false;
 bool found=false;char line[256]{};
 char recent[7][160]{};
 while(std::fgets(line,sizeof(line),file)) {
  size_t length=std::strlen(line);while(length && (line[length-1]=='\n'||line[length-1]=='\r')) line[--length]='\0';
  if(length) {
   for(int i=0;i<6;++i) std::memcpy(recent[i],recent[i+1],sizeof(recent[i]));
   std::snprintf(recent[6],sizeof(recent[6]),"%.159s",line);found=true;
  }
 }
 if(found) std::memcpy(previous_log,recent,sizeof(previous_log));
 std::fclose(file);return found;
}
void read_previous_log() {
 read_last_line("/download0/java25-startup.log");
 read_last_line("/download0/java25-vm-trace.log");
}

void result(int i,int rc,const char *message) {
 status[i]=rc==0?1:-1;
 std::snprintf(messages[i],sizeof(messages[i]),"%s / code %08X",message,static_cast<unsigned>(rc));
 char state[256];std::snprintf(state,sizeof(state),"%s: %s / code %08X",rc==0?"PASS":"FAIL",names[i],static_cast<unsigned>(rc));session_status(state);
}
void java_failure(int i,int code,const char* phase) {
 // Keep the original exception alive while obtaining its actual Java text.
 jthrowable original=java_env->ExceptionOccurred();
 java_env->ExceptionClear();
 char detail[1536]="Java exception text unavailable";
 if(original) {
  jclass type=java_env->GetObjectClass(original);
  jmethodID method=type?java_env->GetMethodID(type,"toString","()Ljava/lang/String;"):nullptr;
  jstring text=method?static_cast<jstring>(java_env->CallObjectMethod(original,method)):nullptr;
  if(text&&!java_env->ExceptionCheck()) {
   const char* utf=java_env->GetStringUTFChars(text,nullptr);
   if(utf) {std::snprintf(detail,sizeof(detail),"%s",utf);java_env->ReleaseStringUTFChars(text,utf);}
  }
  if(java_env->ExceptionCheck()) java_env->ExceptionClear();
  if(text) java_env->DeleteLocalRef(text);
  if(type) java_env->DeleteLocalRef(type);
  java_env->Throw(original);
  java_env->ExceptionDescribe();java_env->ExceptionClear();
  java_env->DeleteLocalRef(original);
 }
 std::snprintf(exception_detail,sizeof(exception_detail),"%s: %s",phase,detail);
 ps5::log_share::write_note("/download0/probe-exception.txt",exception_detail);
 char message[80];std::snprintf(message,sizeof(message),"%.20s: %.48s",phase,detail);
 if(startup_log) {std::fprintf(startup_log,"CLIENT FAILURE: %s: %s / code %08X\n",phase,detail,static_cast<unsigned>(code));std::fflush(startup_log);}
 result(i,code,message);
}
void skip_vm_dependents() {
 for(int i=2;i<test_count;++i) {
  status[i]=3;
  std::snprintf(messages[i],sizeof(messages[i]),"Not run: VM creation did not succeed.");
 }
}
void run_test(int i) {
 if(i==0) {
  timespec now{};clock_gettime(CLOCK_REALTIME,&now);
  std::snprintf(run_id,sizeof(run_id),"client-%s-%lld-%ld",build_version,static_cast<long long>(now.tv_sec),now.tv_nsec);
  // Explicit initialization starts a new run; menu-only relaunch preserves logs.
  // These are diagnostic files only. No world, save or configuration is touched.
  static char retained_tail[512*1024];
  for(const char* path:{"/download0/java25-startup.log","/download0/java25-vm-trace.log"}) {
   if(!ps5::log_retention::retain_tail(path,retained_tail,sizeof(retained_tail))) {
    result(i,errno,"Cannot retain diagnostic tail; check storage");return;
   }
  }
  ps5::log_share::begin_session(build_version,run_id);
  startup_log=std::fopen("/download0/java25-startup.log","a");
  if(!startup_log) {result(i,errno,"Cannot open persistent startup log");return;}
  std::fprintf(startup_log,"\n=== CLIENT RUN %s BUILD %s ===\n",run_id,build_version);std::fflush(startup_log);
  log_stage("Prior startup/VM diagnostic tails retained: max512KiB each before new run");
  log_stage("Begin embedded core constructors");
  size_t count=0;
  for(auto *fn=__jvm_init_array_start;fn!=__jvm_init_array_end;++fn) {if(*fn) {(*fn)();++count;}}
  initialized=true;log_stage("Embedded constructors complete");
  long page_size=sysconf(_SC_PAGESIZE);
  if(startup_log) {std::fprintf(startup_log,"Runtime constructors: %zu; page size: %ld bytes\n",count,page_size);std::fflush(startup_log);}
  char text[80]{};std::snprintf(text,sizeof(text),"%zu constructors; OS page size: %ld bytes",count,page_size);
  result(i,0,text);
 } else if(!initialized) {
  result(i,-1301,"Initialize runtime first, then relaunch to retry");
 } else if(i==1) {
  // Check the actual read operation; access() may have different sandbox
  // permission behavior. Distinguish preflight errors from JNI returns.
  log_stage("Opening packaged Java core image");
  errno=0;
  FILE *image=std::fopen("/app0/assets/java25/lib/modules","rb");
  if(!image) {
   int error=errno?errno:-1310;
   if(startup_log) {std::fprintf(startup_log,"PREFLIGHT: core image fopen failed, code %08X\n",static_cast<unsigned>(error));std::fflush(startup_log);}
   result(i,error,"Before JVM: core image fopen failed");skip_vm_dependents();read_previous_log();return;
  }
  unsigned char header[4]{};
  size_t read=std::fread(header,1,sizeof(header),image);
  int error=errno;
  std::fclose(image);
  const unsigned char magic[]={0xda,0xda,0xfe,0xca};
  if(read!=sizeof(header)||std::memcmp(header,magic,sizeof(magic))!=0) {
   int code=read!=sizeof(header)?(error?error:-1311):-1312;
   log_stage("Core image read or magic check failed before JNI call");
   result(i,code,"Before JVM: core image read / magic failed");skip_vm_dependents();read_previous_log();return;
  }
#ifdef __PROSPERO__
  // Reuse the runtime's sampling control: preserve last-stage/failure context
  // without synchronous disk writes for every allocation/zeroing checkpoint.
  ps5_vm_set_metadata_interval(4096);
#endif
  log_stage("Runtime ENTER/DONE checkpoint sampling enabled: 1 in 4096");
  log_stage("Core image opened and JIMAGE header verified");
  JavaVMOption options[]={
   {const_cast<char *>("-Xint"),nullptr},
   {const_cast<char *>("--enable-native-access=ALL-UNNAMED"),nullptr},
   {const_cast<char *>("--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED"),nullptr},
   {const_cast<char *>("-XX:+UseCompactObjectHeaders"),nullptr},
   {const_cast<char *>("-XX:UseAVX=0"),nullptr},
   {const_cast<char *>("-XX:UseSSE=2"),nullptr},
   {const_cast<char *>("-Xms16m"),nullptr},
   {const_cast<char *>("-Xmx128m"),nullptr},
   // Keep the proven128MiB reservation:024 failed reserving512MiB before Main.
   // Bootstrap class metadata needs far less than the default 1 GiB reservation.
   {const_cast<char *>("-XX:CompressedClassSpaceSize=64m"),nullptr},
   {const_cast<char *>("-Xshare:off"),nullptr},
   {const_cast<char *>("-XX:+UseSerialGC"),nullptr},
   {const_cast<char *>("-XX:ActiveProcessorCount=2"),nullptr},
   {const_cast<char *>("-XX:-UsePerfData"),nullptr},
   {const_cast<char *>("-XX:ErrorFile=/download0/hs_err_java25.log"),nullptr},
   {const_cast<char *>(CLIENT_CLASSPATH_OPTION),nullptr},
   {const_cast<char *>("-Djava.io.tmpdir=/download0"),nullptr},
   {const_cast<char *>("-Duser.home=/download0"),nullptr},
   {const_cast<char *>("-Dlog4j2.disableJmx=true"),nullptr},
   // Always resolve relative paths against user.dir. UnixFileSystem then
   // skips its desktop getcwd comparison in the native title sandbox.
   {const_cast<char *>("-Dsun.nio.fs.chdirAllowed=true"),nullptr},
   {const_cast<char *>("-Dsun.nio.fs.ps5Sandbox=true"),nullptr},
   {const_cast<char *>("-Djava.net.preferIPv4Stack=false"),nullptr},
   {const_cast<char *>("-Dps5.probe.dependencyTrace=true"),nullptr},
   {const_cast<char *>("-Duser.timezone=UTC"),nullptr},
   {const_cast<char *>("vfprintf"),reinterpret_cast<void *>(&vm_print)},
   {const_cast<char *>("exit"),reinterpret_cast<void *>(&vm_exit)},
   {const_cast<char *>("abort"),reinterpret_cast<void *>(&vm_abort)}
  };
  JavaVMInitArgs args{};args.version=JNI_VERSION_24;
  args.nOptions=sizeof(options)/sizeof(options[0]);args.options=options;args.ignoreUnrecognized=JNI_FALSE;
  // Verify the raw diagnostic write path before entering JVM code. Each
  // VM milestone then appends a line without stdio or JVM allocation.
  int trace_fd=open("/download0/java25-vm-trace.log",O_CREAT|O_WRONLY|O_TRUNC,0600);
  if(trace_fd<0) {result(i,errno,"Before JVM: cannot open checkpoint trace");skip_vm_dependents();return;}
  const char begin[]="APP: entering JNI_CreateJavaVM\n";
  ssize_t traced=write(trace_fd,begin,sizeof(begin)-1);
  int trace_error=errno;close(trace_fd);
  if(traced!=sizeof(begin)-1) {result(i,trace_error?trace_error:-1313,"Before JVM: checkpoint write failed");skip_vm_dependents();return;}
  log_stage("Calling real JNI_CreateJavaVM");
  ps5_native_trace::enable();
  ps5_native_trace::quiet();
  int rc=JNI_CreateJavaVM(&java_vm,reinterpret_cast<void **>(&java_env),&args);
  ps5_native_trace::disable();
  if(startup_log) {std::fprintf(startup_log,"JNI_CreateJavaVM returned %d\n",rc);std::fflush(startup_log);}
  if(rc==JNI_OK && (!java_vm||!java_env)) rc=-1302;
  if(rc!=JNI_OK) {java_vm=nullptr;java_env=nullptr;skip_vm_dependents();read_previous_log();}
  result(i,rc,acceptance.vm_result);
 } else if(!java_vm||!java_env) {
  result(i,-1303,"Create the VM first; relaunch to retry");
 } else if(i>=2 && i<=3) {
  const char *fixture=i==2?"ClientInventory25":acceptance.fixture;
  NativeTraceScope trace_scope;
  log_stage("Reading bundled java.security through native file API");
  FILE *security=std::fopen("/app0/assets/java25/conf/security/java.security","rb");
  if(!security) {result(i,errno?errno:-1318,"Native java.security open failed");return;}
  unsigned char security_header=0;
  size_t security_read=std::fread(&security_header,1,1,security);
  int security_error=std::ferror(security)?errno:0;
  std::fclose(security);
  if(security_read!=1 || security_error || security_header!='#') {
   result(i,security_error?security_error:-1319,"Native java.security read/header failed");return;
  }
  log_stage("Native bundled security configuration read PASS");
  log_stage("Reading packaged Client fixture bytecode directly");
  // Bootstrap bytecode execution independently of desktop class-path file discovery.
  static unsigned char class_bytes[64*1024];
  char class_path[128];std::snprintf(class_path,sizeof(class_path),"/app0/assets/java25/classes/%s.class",fixture);
  FILE* class_file=std::fopen(class_path,"rb");
  if(!class_file) {result(i,errno?errno:-1314,"Client fixture bytecode fopen failed");return;}
  size_t class_size=std::fread(class_bytes,1,sizeof(class_bytes),class_file);
  bool bad_read=std::ferror(class_file)||!std::feof(class_file);
  std::fclose(class_file);
  if(bad_read||class_size<8||class_bytes[0]!=0xca||class_bytes[1]!=0xfe||
     class_bytes[2]!=0xba||class_bytes[3]!=0xbe||class_bytes[6]!=0||class_bytes[7]!=69) {
   result(i,-1315,"Client fixture read / Java 25 format check failed");return;
  }
  log_stage("Obtaining actual system class loader");
  jclass loader_class=java_env->FindClass("java/lang/ClassLoader");
  jmethodID get_loader=loader_class?java_env->GetStaticMethodID(loader_class,"getSystemClassLoader","()Ljava/lang/ClassLoader;"):nullptr;
  jobject loader=get_loader?java_env->CallStaticObjectMethod(loader_class,get_loader):nullptr;
  if(!loader||java_env->ExceptionCheck()) {
   java_failure(i,-1316,"system class loader");
   if(loader_class) java_env->DeleteLocalRef(loader_class);
   if(loader) java_env->DeleteLocalRef(loader);
   return;
  }
  log_stage("Defining Client fixture in the system class loader");
  jclass klass=java_env->DefineClass(fixture,loader,reinterpret_cast<const jbyte*>(class_bytes),static_cast<jsize>(class_size));
  java_env->DeleteLocalRef(loader);java_env->DeleteLocalRef(loader_class);
  if(!klass||java_env->ExceptionCheck()) {java_failure(i,-1304,"DefineClass Client fixture");return;}
  JNINativeMethod callbacks[]={{const_cast<char *>("checkpoint"),const_cast<char *>("(Ljava/lang/String;)V"),reinterpret_cast<void *>(&network_checkpoint)}};
  if(java_env->RegisterNatives(klass,callbacks,1)!=JNI_OK || java_env->ExceptionCheck()) {
   java_failure(i,-1317,"network trace binding");java_env->DeleteLocalRef(klass);return;
  }
  jmethodID method=java_env->GetStaticMethodID(klass,"main","([Ljava/lang/String;)V");
  if(!method||java_env->ExceptionCheck()) {java_failure(i,-1305,"main method lookup");java_env->DeleteLocalRef(klass);return;}
  jclass string_class=java_env->FindClass("java/lang/String");
  jobjectArray arguments=string_class?java_env->NewObjectArray(0,string_class,nullptr):nullptr;
  if(!arguments||java_env->ExceptionCheck()) {java_failure(i,-1306,"argument array");if(string_class) java_env->DeleteLocalRef(string_class);java_env->DeleteLocalRef(klass);return;}
  log_stage("Calling Client fixture.main");
  java_env->CallStaticVoidMethod(klass,method,arguments);
  bool failed=java_env->ExceptionCheck();
  if(failed) java_failure(i,-1307,fixture);
  java_env->DeleteLocalRef(arguments);java_env->DeleteLocalRef(string_class);java_env->DeleteLocalRef(klass);
  log_stage(failed?"Client fixture threw exception":"Client fixture returned normally");
  if(!failed) result(i,0,"Java dependency check PASS");
 } else {
  NativeTraceScope trace_scope;
  log_stage("Calling DestroyJavaVM");
  int rc=java_vm->DestroyJavaVM();
  if(rc==JNI_OK) {java_vm=nullptr;java_env=nullptr;}
  log_stage(rc==JNI_OK?"DestroyJavaVM complete":"DestroyJavaVM returned an error");
  result(i,rc,"Real DestroyJavaVM, application UI stays active");
 }
}

}
extern "C" void client_sdl_diagnostic(const char* text) {log_stage(text);}
extern "C" void client_gpu_stage(const char *name,int code) {
 char stage[512];std::snprintf(stage,sizeof(stage),acceptance.stage_format,code==INT32_MIN?"RUN":code==0?"PASS":"FAIL",code,name);log_stage(stage);
}
extern "C" int sceKernelSendNotificationRequest(std::uint32_t,void*,std::size_t,int);
extern "C" int sceSystemServiceHideSplashScreen();
static void notify(const char* text) {
 struct Notification {std::uint8_t reserved[45];char message[3075];};
 Notification n{};std::snprintf(n.message,sizeof(n.message),"%s",text);
 (void)sceKernelSendNotificationRequest(0,&n,sizeof(n),0);
}
int main() {
 ps5::log_share::write_note("/download0/probe-build.txt",acceptance.build_note);
 ps5::log_share::start();
 read_previous_log();
 sceUserServiceInitialize(nullptr);std::int32_t user=-1;
 if(sceUserServiceGetInitialUser(&user)>=0 && scePadInit()>=0) pad=scePadOpen(user,0,0,nullptr);

 notify(acceptance.ready_note);
 if(pad<0){notify(acceptance.controller_failure);for(;;)(void)sceKernelUsleep(1000000);}
 bool armed=false,start=false;std::uint32_t previous=0;
 while(!start) {
  PadSample batch[64]{};int count=scePadRead(pad,batch,64);
  if(count>=0&&count<=64)for(int i=0;i<count;++i) {
   auto buttons=batch[i].connected&&!(batch[i].buttons&0x80000000u)?batch[i].buttons:0u;
   if(batch[i].connected&&!(batch[i].buttons&0x80000000u)&&!(buttons&0x4000))armed=true;
   if(armed&&((buttons&~previous)&0x4000))start=true;
   previous=buttons;
  }
  (void)sceKernelUsleep(16000);
 }
 scePadClose(pad);pad=-1;
 (void)sceSystemServiceHideSplashScreen();
 notify(acceptance.running_note);
 // Compiler and texture/depth/blend acceptance precede retained SDL display resources.
 // This also avoids repeating manual inputs when compiler startup fails.
 for(int step=0;step<test_count;++step) {
  int i=step;
  if(i){char state[200];std::snprintf(state,sizeof(state),"RUN: %s",names[i]);session_status(state);}
  run_test(i);
  if(status[i]!=1) {
   char note[240];std::snprintf(note,sizeof(note),acceptance.failure_format,i+1,messages[i]);notify(note);
   for(;;)(void)sceKernelUsleep(1000000);
  }
 }
 char state[240];std::snprintf(state,sizeof(state),"%s",acceptance.pass_state);session_status(state);
 notify(acceptance.pass_note);
 for(;;)(void)sceKernelUsleep(1000000);
}
