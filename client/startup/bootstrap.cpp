#define PS5_TRACK_FILE_ACTIVITY 1
extern "C" int prospero_haptic_reserve();
extern "C" void prospero_hid_preload(void);
extern "C" int sceAudioOutOpen(int,int,int,unsigned,unsigned,unsigned);
/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "demo_renderer.hpp"
#include "log_share.hpp"
#include "log_retention.hpp"
#include "buffer_bridge.hpp"
#include "client_classpath.hpp"
#include "pad.h"
#include <atomic>
#include <algorithm>
#include <cstdarg>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include "jni.h"
#include "native_trace.hpp"
#include "native_stderr.hpp"
#include "observer_native.hpp"
#define PROSPERO_TOOLKIT 1
#include "../launcher/native_menu.hpp"
extern "C" void prospero_graphics_init(void);
namespace prospero_menu {
using ToolkitInitializer=void(*)();
extern "C" ToolkitInitializer __client_ui_init_start[],__client_ui_init_end[];
static pthread_once_t toolkit_once=PTHREAD_ONCE_INIT;
static void initialize_toolkit_once(){
 prospero_graphics_init();
 for(auto* p=__client_ui_init_start;p!=__client_ui_init_end;++p)if(*p)(*p)();
}
void initialize_toolkit_graphics(){pthread_once(&toolkit_once,initialize_toolkit_once);}
}
#include "session_restart.hpp"
#include "../ports/oshi/native_cpu.hpp"
#include <sys/sysctl.h>
static void notify(const char* text);
extern "C" int sceAudioOutInit();
extern "C" {int client_ps5_audio_early_init_result=INT32_MIN;int client_ps5_audio_early_port=-1;}
using Initializer=void (*)();
extern "C" Initializer __jvm_init_array_start[],__jvm_init_array_end[];
#include <sys/mman.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <unistd.h>
extern "C" std::uint64_t sceKernelGetProcessTime();
extern "C" void JNU_PS5SetDirectScratchEnabled(int);
extern "C" void JNU_PS5SetVerifierSmallReserveEnabled(int);
extern "C" void ps5_emutls_enable_direct(int);
extern "C" int prospero_sdl_mutex_preinit();
extern "C" int clientgpu_condition_preinit();
extern "C" int prospero_sdl_condition_preinit();
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
 ps5::file_activity::open_result(fd,path);
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
extern "C" int __real_close(int);
extern "C" int __wrap_close(int fd){int result=__real_close(fd);int saved=errno;ps5::file_activity::close_result(fd,result);errno=saved;return result;}
#endif
extern "C" int ps5shaderc_fault_begin(void);
extern "C" void ps5shaderc_fault_end(void);
namespace {
bool resume_library=false,return_to_library=false;
// One outer reference survives nested compiler begin/end calls. Restore the
// previous JVM handlers on every normal/Java-exception return from run_test.
struct StartupFaultScope {
 bool active;
 int handlers;
 explicit StartupFaultScope(bool enable):active(enable),handlers(enable?ps5shaderc_fault_begin():0){}
 ~StartupFaultScope(){if(active)ps5shaderc_fault_end();}
};
constexpr int test_count=4;
const char *names[]={"Initialize embedded runtime","Create Java VM for original client","Verify original client artifacts","Launcher and selected downloaded instance"};
int status[test_count]{}; // 0 untested, 1 pass, -1 fail, 2 running
char messages[test_count][104]{};
int pad=-1;
bool initialized=false;
JavaVM *java_vm=nullptr;
JNIEnv *java_env=nullptr;
FILE *startup_log=nullptr;
constexpr const char* build_version=PROSPERO_APP_VERSION;
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

 env->ReleaseStringUTFChars(stage,utf);
}
void native_snapshot(JNIEnv *env,jclass,jlong elapsed,jint phase) {
 if(!startup_observer::append("/download0/process-usage.log",static_cast<long long>(elapsed),phase)) {
  jclass error=env->FindClass("java/io/IOException");
  if(error)env->ThrowNew(error,"Native observer report append failed");
 }
}
jobjectArray cpu_information(JNIEnv *env,jclass) {
 int logical=0;size_t size=sizeof(logical);if(sysctlbyname("hw.ncpu",&logical,&size,nullptr,0)!=0||size!=sizeof(logical))logical=0;
 auto info=prospero_cpu::read(prospero_cpu::cpuid,logical);
 if(!info.valid)return nullptr;
 jclass strings=env->FindClass("java/lang/String");if(!strings)return nullptr;
 jobjectArray result=env->NewObjectArray(8,strings,nullptr);env->DeleteLocalRef(strings);if(!result)return nullptr;
 char family[16],model[16],stepping[16],count[16];std::snprintf(family,sizeof(family),"%u",info.family);std::snprintf(model,sizeof(model),"%u",info.model);std::snprintf(stepping,sizeof(stepping),"%u",info.stepping);std::snprintf(count,sizeof(count),"%d",info.logical);
 const char* values[]={info.brand,info.vendor,info.signature,family,model,stepping,count,info.kernel_count?"kernel.hw.ncpu":"CPUID"};
 for(int n=0;n<8;n++){jstring value=env->NewStringUTF(values[n]);if(!value||env->ExceptionCheck())return nullptr;env->SetObjectArrayElement(result,n,value);env->DeleteLocalRef(value);if(env->ExceptionCheck())return nullptr;}return result;
}
int vm_print(FILE *requested,const char *format,va_list arguments) {
 // HotSpot also invokes this hook for dedicated unified log FILEs. Preserve
 // those destinations so file contents,flush and rotation accounting agree.
 FILE *target=((requested==stdout||requested==stderr)&&startup_log)?startup_log:requested;
 if(!target){errno=EINVAL;return -1;}
 int count=std::vfprintf(target,format,arguments);
 if(std::fflush(target)!=0)return -1;
 return count;
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
void run_test(int i);
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
  char resource_identity[256];std::snprintf(resource_identity,sizeof(resource_identity),"Build: %s\nRun: %s\nNative startup observer;phase0 before stack collection,phase1 after publication;RSS units unspecified\n",build_version,run_id);
  if(!ps5::log_share::write_note("/download0/process-usage.log",resource_identity))log_stage("Native observer identity write failed");
  char native_identity[256];std::snprintf(native_identity,sizeof(native_identity),"Build: %s\nRun: %s\nNative stderr capture\n",build_version,run_id);
  int native_stderr_error=0;
  if(!ps5::log_share::write_note("/download0/probe-native-stderr.log",native_identity))
   native_stderr_error=errno?errno:EIO;
  else native_stderr_error=ps5::native_stderr::begin("/download0/probe-native-stderr.log");
  if(!native_stderr_error)std::fprintf(stderr,"Client083 native stderr stream active before embedded constructors\n");
  else notify("Client083 native stderr capture unavailable;continuing original startup. Inspect startup reports.");
  startup_log=std::fopen("/download0/java25-startup.log","a");
  if(!startup_log) {result(i,errno,"Cannot open persistent startup log");return;}
  std::fprintf(startup_log,"\n=== CLIENT RUN %s BUILD %s ===\n",run_id,build_version);std::fflush(startup_log);
  {
   FILE* prior_vm=std::fopen("/download0/java25-vm-trace.log","rb");
   if(prior_vm){
    static char prior_tail[64*1024];
    if(std::fseek(prior_vm,0,SEEK_END)==0){
     long end=std::ftell(prior_vm);
     if(end>0 && std::fseek(prior_vm,end>(long)sizeof(prior_tail)?end-(long)sizeof(prior_tail):0,SEEK_SET)==0){
      size_t count=std::fread(prior_tail,1,sizeof(prior_tail),prior_vm);
      std::fputs("\nBEGIN PREVIOUS VM TRACE TAIL (up to64KiB;prior run, not current)\n",startup_log);
      std::fwrite(prior_tail,1,count,startup_log);
      std::fputs("\nEND PREVIOUS VM TRACE TAIL\n",startup_log);std::fflush(startup_log);
     }
    }
    std::fclose(prior_vm);
   }
  }
  char capture_status[160];std::snprintf(capture_status,sizeof(capture_status),"Native stderr FILE capture status%d;raw descriptor2 unchanged;diagnostic failure is nonfatal",native_stderr_error);log_stage(capture_status);
  log_stage("Prior startup/VM diagnostic tails retained: max512KiB each before new run");
  const auto file_budget=ps5::file_limits::prepare(8192);
  char file_stage[256];std::snprintf(file_stage,sizeof(file_stage),"PS5_FILE_LIMIT query=%d change=%d errno=%d before=%llu after=%llu hard=%llu",file_budget.query,file_budget.change,file_budget.error,(unsigned long long)file_budget.before,(unsigned long long)file_budget.after,(unsigned long long)file_budget.hard);log_stage(file_stage);
  ps5::file_limits::snapshot(file_stage,sizeof(file_stage));log_stage(file_stage);
  log_stage("Storage /download0: title-local reservation requested4096MiB; actual capacity is unavailable, not zero");
  prospero_hid_preload();
  log_stage("Begin embedded core constructors");
  size_t count=0;
  for(auto *fn=__jvm_init_array_start;fn!=__jvm_init_array_end;++fn) {if(*fn) {(*fn)();++count;}}
  initialized=true;log_stage("Embedded constructors complete");
  int graphics_cond_rc=clientgpu_condition_preinit();
  char graphics_sync_note[128];std::snprintf(graphics_sync_note,sizeof(graphics_sync_note),"PS5 RADV native condition reserve: result=%d capacity128;before JVM",graphics_cond_rc);log_stage(graphics_sync_note);
  if(graphics_cond_rc){result(i,graphics_cond_rc,"Cannot reserve RADV native conditions before JVM");return;}
  int mutex_rc=prospero_sdl_mutex_preinit();
  int condition_rc=mutex_rc?0:prospero_sdl_condition_preinit();
  char sync_note[160];std::snprintf(sync_note,sizeof(sync_note),"PS5 SDL native sync reserve: mutex=%d condition=%d capacities256/128;before JVM",mutex_rc,condition_rc);log_stage(sync_note);
  if(mutex_rc||condition_rc){result(i,mutex_rc?mutex_rc:condition_rc,"Cannot reserve SDL native sync before JVM");return;}

  // Prepare the SDK service on the native startup thread before JVM heap/workers.
  client_ps5_audio_early_init_result=sceAudioOutInit();
  char audio_stage[160];std::snprintf(audio_stage,sizeof(audio_stage),"AudioOut pre-JVM init result=%d (0x%08X);failure is nonfatal",client_ps5_audio_early_init_result,static_cast<unsigned>(client_ps5_audio_early_init_result));log_stage(audio_stage);
  std::fprintf(stderr,"PS5 OpenAL AudioOut pre-JVM init result=%d\n",client_ps5_audio_early_init_result);std::fflush(stderr);
  // Reserve the real output port before JVM heaps and Vulkan allocations.
  // OpenAL claims it and retains one drained port across logical device reloads.
  if(client_ps5_audio_early_init_result>=0||static_cast<unsigned>(client_ps5_audio_early_init_result)==0x8026000eu)
   client_ps5_audio_early_port=sceAudioOutOpen(0xff,0,0,256,48000,1);
  (void)prospero_haptic_reserve();
  std::fprintf(stderr,"PS5 OpenAL AudioOut pre-JVM port result=%d (0x%08X)\n",client_ps5_audio_early_port,static_cast<unsigned>(client_ps5_audio_early_port));std::fflush(stderr);
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
   {const_cast<char *>("-Dps5.zip.maxOpenFiles=64"),nullptr},
   {const_cast<char *>("-Xmixed"),nullptr},
   {const_cast<char *>("-XX:TieredStopAtLevel=1"),nullptr},
   {const_cast<char *>("-XX:CICompilerCount=1"),nullptr},
   {const_cast<char *>("-XX:CompileThresholdScaling=4.0"),nullptr},
   {const_cast<char *>("-XX:CompileCommand=MemLimit,*.*,2M"),nullptr},
   {const_cast<char *>("-XX:ReservedCodeCacheSize=96m"),nullptr},
   {const_cast<char *>("-XX:SweeperThreshold=50.0"),nullptr},
   {const_cast<char *>("-Xlog:jit+compilation=debug,codecache=info:file=/download0/java25-jit.log:uptime,level,tags:filecount=1,filesize=4M"),nullptr},
   {const_cast<char *>("--enable-native-access=ALL-UNNAMED"),nullptr},
   {const_cast<char *>("--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED"),nullptr},
   {const_cast<char *>("-XX:+UseCompactObjectHeaders"),nullptr},
   {const_cast<char *>("-XX:UseAVX=0"),nullptr},
   {const_cast<char *>("-XX:UseSSE=2"),nullptr},
   {const_cast<char *>("-XX:MetaspaceSize=128m"),nullptr},
   {const_cast<char *>("-XX:+ExplicitGCInvokesConcurrent"),nullptr},
   {const_cast<char *>("-Djava.awt.headless=true"),nullptr},
   {const_cast<char *>("-Xms128m"),nullptr},
   {const_cast<char *>("-Xmx1536m"),nullptr},
   {const_cast<char *>("-XX:-UseCompressedOops"),nullptr},
   // 063 world generation hit a real Java heap OOM at256MiB.
   // 064 anonymous384MiBreservationfailed. Runtime0118supports separatelybounded
   // directheap fallback onlywithuncompressedoops;targetvalidationrequired.
   // Bootstrap class metadata needs far less than the default 1 GiB reservation.
   {const_cast<char *>("-XX:CompressedClassSpaceSize=64m"),nullptr},
   {const_cast<char *>("-Xshare:off"),nullptr},
   {const_cast<char *>("-Xlog:gc=info,safepoint=info:file=/download0/java25-gc.log:uptimemillis,level,tags:filecount=1,filesize=4M"),nullptr},
   {const_cast<char *>("-XX:+UseG1GC"),nullptr},
   {const_cast<char *>("-XX:MaxGCPauseMillis=4"),nullptr},
   //120Hz: allow a smaller young minimum and spread mandatory mixed-GC work.
   {const_cast<char *>("-XX:+UnlockExperimentalVMOptions"),nullptr},
   {const_cast<char *>("-XX:G1NewSizePercent=1"),nullptr},
   {const_cast<char *>("-XX:G1MixedGCCountTarget=16"),nullptr},
   //100: isolate class/code cleanup in remark; full-GC unloading remains enabled.
   {const_cast<char *>("-XX:-ClassUnloadingWithConcurrentMark"),nullptr},
   {const_cast<char *>("-XX:ParallelGCThreads=4"),nullptr},
   {const_cast<char *>("-XX:ConcGCThreads=1"),nullptr},
   {const_cast<char *>("-XX:G1ReservePercent=20"),nullptr},
   {const_cast<char *>("-XX:ActiveProcessorCount=4"),nullptr},
   {const_cast<char *>("-XX:-UsePerfData"),nullptr},
   {const_cast<char *>("-XX:ErrorFile=/download0/hs_err_java25.log"),nullptr},
   {const_cast<char *>(CLIENT_CLASSPATH_OPTION),nullptr},
   {const_cast<char *>("-Djava.io.tmpdir=/download0"),nullptr},
   {const_cast<char *>("-Duser.home=/download0"),nullptr},
   {const_cast<char *>("-Duser.dir=/download0/mc-client"),nullptr},
   {const_cast<char *>("-Dlog4j.configurationFile=/app0/assets/java25/log4j2-startup.xml"),nullptr},
   {const_cast<char *>("-Dlog4j2.disableJmx=true"),nullptr},
   // Always resolve relative paths against user.dir. UnixFileSystem then
   // skips its desktop getcwd comparison in the native title sandbox.
   {const_cast<char *>("-Dsun.nio.fs.chdirAllowed=true"),nullptr},
   {const_cast<char *>("-Dsun.nio.fs.ps5Sandbox=true"),nullptr},
   {const_cast<char *>("-Djava.net.preferIPv4Stack=true"),nullptr},
   {const_cast<char *>("-Dio.netty.transport.noNative=true"),nullptr},
   {const_cast<char *>("-Dps5.net.traceBindFailures=true"),nullptr},
   {const_cast<char *>("-Dps5.probe.dependencyTrace=true"),nullptr},
   {const_cast<char *>("-Duser.timezone=UTC"),nullptr},
   {const_cast<char *>("vfprintf"),reinterpret_cast<void *>(&vm_print)},
   {const_cast<char *>("exit"),reinterpret_cast<void *>(&vm_exit)},
   {const_cast<char *>("abort"),reinterpret_cast<void *>(&vm_abort)}
  };
  JavaVMOption resume_option{const_cast<char *>("-Dps5.launcher.resume=true"),nullptr};
  JavaVMInitArgs args{};args.version=JNI_VERSION_24;
  JavaVMOption session_options[sizeof(options)/sizeof(options[0])+1];
  std::copy(std::begin(options),std::end(options),session_options);
  const int option_count=sizeof(options)/sizeof(options[0]);session_options[option_count]=resume_option;
  args.nOptions=option_count+(resume_library?1:0);args.options=session_options;args.ignoreUnrecognized=JNI_FALSE;
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
  result(i,rc,"Real JNI_CreateJavaVM, guarded C1 level1, 512 MiB max heap; uncompressed oops/direct fallback");
 } else if(!java_vm||!java_env) {
  result(i,-1303,"Create the VM first; relaunch to retry");
 } else if(i>=2 && i<=3) {
  const char *fixture=i==2?"ClientInventory25":"ClientStartup25";
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
  JNINativeMethod callbacks[]={{const_cast<char *>("checkpoint"),const_cast<char *>("(Ljava/lang/String;)V"),reinterpret_cast<void *>(&network_checkpoint)},
   {const_cast<char *>("nativeSnapshot"),const_cast<char *>("(JI)V"),reinterpret_cast<void *>(&native_snapshot)},
   {const_cast<char *>("launcherMenu"),const_cast<char *>("()Z"),reinterpret_cast<void *>(&prospero_menu::menu)},
   {const_cast<char *>("cpuInformation"),const_cast<char *>("()[Ljava/lang/String;"),reinterpret_cast<void *>(&cpu_information)}};
  if(java_env->RegisterNatives(klass,callbacks,i==3?4:1)!=JNI_OK || java_env->ExceptionCheck()) {
   java_failure(i,-1317,"network trace binding");java_env->DeleteLocalRef(klass);return;
  }
  jmethodID method=java_env->GetStaticMethodID(klass,"main","([Ljava/lang/String;)V");
  if(!method||java_env->ExceptionCheck()) {java_failure(i,-1305,"main method lookup");java_env->DeleteLocalRef(klass);return;}
  jclass string_class=java_env->FindClass("java/lang/String");
  jobjectArray arguments=string_class?java_env->NewObjectArray(0,string_class,nullptr):nullptr;
  if(!arguments||java_env->ExceptionCheck()) {java_failure(i,-1306,"argument array");if(string_class) java_env->DeleteLocalRef(string_class);java_env->DeleteLocalRef(klass);return;}
  StartupFaultScope startup_faults(i==3);
  if(i==3) {
   char fault_note[128];std::snprintf(fault_note,sizeof(fault_note),"Original startup fault recorder installed handlers%d (expected4)",startup_faults.handlers);log_stage(fault_note);
   if(startup_faults.handlers!=4) {
    java_env->DeleteLocalRef(arguments);java_env->DeleteLocalRef(string_class);java_env->DeleteLocalRef(klass);
    result(i,-1320,"Cannot install complete original-startup fault recorder");return;
   }
  }
  log_stage("Calling Client fixture.main");
  java_env->CallStaticVoidMethod(klass,method,arguments);
  bool failed=java_env->ExceptionCheck();
  if(!failed&&i==3){
   jmethodID normal=java_env->GetStaticMethodID(klass,"normalQuit","()Z");
   return_to_library=normal&&java_env->CallStaticBooleanMethod(klass,normal);
   failed=java_env->ExceptionCheck()||!return_to_library;
  }
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
 char stage[512];std::snprintf(stage,sizeof(stage),"GPU083 %s code=%d: %s",code==INT32_MIN?"RUN":code==0?"PASS":"FAIL",code,name);log_stage(stage);
}
extern "C" int sceKernelSendNotificationRequest(std::uint32_t,void*,std::size_t,int);
extern "C" int sceSystemServiceHideSplashScreen();
static void notify(const char* text) {
 struct Notification {std::uint8_t reserved[45];char message[3075];};
 Notification n{};std::snprintf(n.message,sizeof(n.message),"%s",text);
 (void)sceKernelSendNotificationRequest(0,&n,sizeof(n),0);
}
int main(int argc,char** argv) {
 for(int i=0;i<argc;++i)if(argv[i]&&std::strcmp(argv[i],"--prospero-library")==0)resume_library=true;
 ps5::log_share::write_note("/download0/probe-build.txt","Minecraft Original Client Startup " PROSPERO_APP_VERSION " / PPSA99874\n");
 ps5::log_share::start();
 read_previous_log();
 sceUserServiceInitialize(nullptr);std::int32_t user=-1;
 if(sceUserServiceGetInitialUser(&user)>=0 && scePadInit()>=0) pad=scePadOpen(user,0,0,nullptr);


 if(pad<0){notify("Client083 controller setup failed. Existing logs remain available.");for(;;)(void)sceKernelUsleep(1000000);}
 scePadClose(pad);pad=-1;
 (void)sceSystemServiceHideSplashScreen();
 // Native UI owns VideoOut/controller on its thread before creating Java.
 // Core constructors and early AudioOut init stay on the original startup thread.
 ps5_emutls_enable_direct(1);
 log_stage("PS5 compiler TLS direct fallback enabled after libc/anonymous ENOMEM; shared native-data ledger");
 JNU_PS5SetDirectScratchEnabled(1);
 JNU_PS5SetVerifierSmallReserveEnabled(1);
 log_stage("PS5 verifier variable reserve enabled: 4MiB contiguous 256-byte units after libc refusal");
 log_stage("PS5 core direct scratch fallback enabled: two8MiB/64slot temporary-buffer budgets;normal allocators first");
 run_test(0);
 if(resume_library)log_stage("PS5_SESSION RESUME_LIBRARY fresh process; saved notice preference retained");
 if(status[0]!=1){notify("Client083 runtime initialization failed; inspect logs.");for(;;)(void)sceKernelUsleep(1000000);}
 if(!prospero_menu::start_frontend()){notify("Client083 native launcher display could not start; inspect logs.");for(;;)(void)sceKernelUsleep(1000000);}
 log_stage("Native launcher first frame presented; now creating Java account services, no Minecraft graphics loaded");
 // Downloaded instance receipts replace the legacy bundled artifact scan (2).
 for(int i:{1,3}) {
  char state[200];std::snprintf(state,sizeof(state),"RUN: %s",names[i]);session_status(state);
  run_test(i);
  if(status[i]!=1) {
   if(!prospero_menu::display_done.load())prospero_menu::show_failure();
   char note[240];std::snprintf(note,sizeof(note),"Client083 failed check%d: %.160s. Keep open for logs; close/reopen to retry.",i+1,messages[i]);notify(note);
   for(;;)(void)sceKernelUsleep(1000000);
  }
 }
 // Successful LoadExec replaces this entire session. Never create a second
 // JVM or reopen CPU VideoOut while the old WSI still owns its process handle.
 if(return_to_library){
  log_stage("PS5_SESSION REPLACE_PROCESS clean quit -> native instance library");
  session_status("CLEAN QUIT: replacing process for native library;not a gameplay PASS");
  if(startup_log)std::fflush(startup_log);
  std::fflush(nullptr);
  int rc=prospero_session::restart_library();
  char note[240];std::snprintf(note,sizeof(note),"Client083 library restart failed: LoadExec returned0x%08x. Keep open for logs; close/reopen to retry.",unsigned(rc));
  log_stage(note);session_status(note);notify(note);
 }
 for(;;)(void)sceKernelUsleep(1000000);
}
