/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "log_share.hpp"
#include "pad.h"
#include "../ports/oshi/hardware_labels.hpp"
#include "../launcher/hardware_identity.hpp"
#include "../startup/input_present_trace.hpp"
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <ctime>
#include <sys/stat.h>
#ifndef PS5ZINK_PROBE_VERSION
#error Probe version must come from the exact package param.json
#endif
extern "C" int zink_present_run(void);
extern "C" int ps5shaderc_fault_begin(void);
extern "C" unsigned ps5shaderc_fault_extended_status(unsigned *);
extern "C" void ps5shaderc_fault_end(void);
extern "C" int prospero_sdl_mutex_preinit(void);
extern "C" int prospero_sdl_condition_preinit(void);
extern "C" int prospero_sdl_tls_preinit(void);
extern "C" int clientgpu_present_worker_preinit(void);
extern "C" int sceKernelUsleep(std::uint32_t);
extern "C" int sceSystemServiceHideSplashScreen();
extern "C" int sceKernelSendNotificationRequest(std::uint32_t,void*,std::size_t,int);
namespace {
FILE *report;
char run_id[128]="No Zink run initialized";
struct Notification {std::uint8_t reserved[45];char message[3075];};
void notify(const char *text){Notification n{};std::snprintf(n.message,sizeof(n.message),"%s",text);(void)sceKernelSendNotificationRequest(0,&n,sizeof(n),0);}
bool directory(const char *path){if(mkdir(path,0777)==0)return true;if(errno!=EEXIST)return false;struct stat s{};return stat(path,&s)==0&&S_ISDIR(s.st_mode);}
}
extern "C" void zink_probe_report(const char *stage,int code)
{
 if(report){std::fprintf(report,"ZINK183 Run:%s %s result=%d: %.768s\n",run_id,code==INT32_MIN?"RUN":code==0?"PASS":"FAIL",code,stage);std::fflush(report);}
 char status[1280];std::snprintf(status,sizeof(status),"ProsperoCraft Zink presentation %s / PPSA99874\nRun: %s\n%s result=%d: %.768s\nNative GLFW/SDL presentation only; no JVM or game.\n",PS5ZINK_PROBE_VERSION,run_id,code==INT32_MIN?"RUNNING":code==0?"PROGRESS":"FAILED",code,stage);
 ps5::log_share::write_note("/download0/probe-session.txt",status);
}
extern "C" void client_sdl_diagnostic(const char *text){static unsigned count;if(__atomic_fetch_add(&count,1,__ATOMIC_RELAXED)<128)zink_probe_report(text,INT32_MIN);}
extern "C" void client_input_change(unsigned mask){char text[64];std::snprintf(text,sizeof(text),"Native input mask0x%x",mask);client_sdl_diagnostic(text);}
extern "C" void client_gpu_stage(const char *stage,int code){zink_probe_report(stage,code);}
static InputPresentBudget input_budget;
extern "C" int client_input_present_trace(int consume){return input_budget.probe(consume!=0);}
extern "C" void client_input_present_note(const char *phase,unsigned index,long long value)
{
 int saved=errno;char text[192];std::snprintf(text,sizeof(text),"INPUT_PRESENT phase=%.48s image=%u value=%lld",phase,index,value);zink_probe_report(text,INT32_MIN);errno=saved;
}
extern "C" const char *prospero_gpu_display_name(void){return prospero_hardware::gpu(prospero_menu::hardware::identity().model);}
int main()
{
 ps5::log_share::write_note("/download0/probe-build.txt","ProsperoCraft Zink presentation " PS5ZINK_PROBE_VERSION " / PPSA99874\nNative GLFW/SDL kopper presentation probe; no JVM/game.\n");
 ps5::log_share::start();
 notify("Zink183 ready: press X once for animated RGB/bar presentation checks; keep open for logs on port8765.");
 sceUserServiceInitialize(nullptr);std::int32_t user=-1;int pad=-1;
 if(sceUserServiceGetInitialUser(&user)>=0&&scePadInit()>=0)pad=scePadOpen(user,0,0,nullptr);
 if(pad<0){notify("Zink183 controller init failed; existing reports preserved.");for(;;)(void)sceKernelUsleep(1000000);}
 bool start=false,armed=false;std::uint32_t previous=0;
 while(!start){
  PadSample batch[64]{};int count=scePadRead(pad,batch,64);
  if(count>=0&&count<=64){
   for(int i=0;i<count;i++){
    auto buttons=batch[i].connected&&!(batch[i].buttons&0x80000000u)?batch[i].buttons:0u;
    if(batch[i].connected&&!(batch[i].buttons&0x80000000u)&&!(buttons&0x4000))armed=true;
    if(armed&&((buttons&~previous)&0x4000))start=true;
    previous=buttons;
   }
  }
  (void)sceKernelUsleep(16000);
 }
 scePadClose(pad);
 ps5::log_share::archive_report("/download0/java25-vm-trace.log","/download0/previous-zink-driver.log");
 timespec time{};(void)clock_gettime(CLOCK_MONOTONIC,&time);
 std::snprintf(run_id,sizeof(run_id),"zink-%s-%lld-%ld",PS5ZINK_PROBE_VERSION,static_cast<long long>(std::time(nullptr)),time.tv_nsec);
 ps5::log_share::begin_session(PS5ZINK_PROBE_VERSION,run_id);
 report=std::fopen("/download0/java25-startup.log","a");
 (void)std::freopen("/download0/java25-vm-trace.log","w",stderr);std::setvbuf(stderr,nullptr,_IONBF,0);
 std::fprintf(stderr,"Build:%s Run:%s native Zink presentation stage2a\n",PS5ZINK_PROBE_VERSION,run_id);
 (void)sceSystemServiceHideSplashScreen();
 int handlers=ps5shaderc_fault_begin();
 unsigned signal_errors=0;unsigned owned=ps5shaderc_fault_extended_status(&signal_errors);
 char signal_note[192];std::snprintf(signal_note,sizeof(signal_note),"Existing native signal recorder handlers%d owned0x%x queryErrors0x%x anchor_zink_present_run=%p",handlers,owned,signal_errors,reinterpret_cast<void*>(&zink_present_run));
 zink_probe_report(signal_note,handlers==4&&owned==0x7f&&!signal_errors?0:-1);
 prospero_menu::hardware::initialize();
 int worker=clientgpu_present_worker_preinit();
 zink_probe_report("Existing genuine WSI worker reservation",worker);
 bool cache=directory("/download0/ProsperoCraft")&&directory("/download0/ProsperoCraft/cache")&&directory("/download0/ProsperoCraft/cache/zink")&&setenv("MESA_SHADER_CACHE_DIR","/download0/ProsperoCraft/cache/zink",1)==0;
 zink_probe_report("App-data shader-cache directory/policy",cache?0:-1);
 int mutex=prospero_sdl_mutex_preinit();
 int condition=mutex==0?prospero_sdl_condition_preinit():-1;
 int tls=mutex==0&&condition==0?prospero_sdl_tls_preinit():-1;
 zink_probe_report("Existing SDL mutex/condition/TLS bootstrap",mutex?mutex:condition?condition:tls);
 int result=handlers==4&&owned==0x7f&&!signal_errors&&cache&&worker==0&&mutex==0&&condition==0&&tls==0?zink_present_run():-1;
 ps5shaderc_fault_end();
 if(!result){
  zink_probe_report("AUTOMATED STAGE2A PASS: three animated presentation cycles and GLFW/SDL teardown/reinit",0);
  notify("Zink183 stage2a checks PASS: confirm three RGB/moving-bar cycles. No launcher/game result. Keep open for current-run reports.");
 }else notify("Zink183 stage2a FAILED. Keep open for current-run reports; after a crash reopen without pressing X.");
 for(;;)(void)sceKernelUsleep(1000000);
}
