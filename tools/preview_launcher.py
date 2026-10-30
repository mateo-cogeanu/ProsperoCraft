#!/usr/bin/env python3
"""Render actual native launcher draw code; exercise return/ownership on host fixtures."""
from pathlib import Path
import argparse,subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args();runtime=a.runtime_workspace.resolve()
w=ROOT/'build/launcher-preview';w.mkdir(parents=True,exist_ok=True)
source='''#include <cstdlib>\n#include <cassert>\n#include <vector>\n#include <string>\n#include <fstream>\n#include <thread>\n#include <chrono>\n#include "jni.h"\n#include "pad.h"\n#include "'''+str(runtime/'native/renderer/demo_renderer.cpp')+'''"\n#include "'''+str(ROOT/'client/launcher/native_menu.hpp')+'''"\n'''
source+=r'''
static std::atomic<unsigned> fake_buttons{0},pad_reads{0},flips{0},motor_large{0},motor_small{0};
static void* storage=nullptr;static std::vector<std::string> operations;static int notifications=0,failure=0;static std::string output;
extern "C" {
int prospero_hid_open(int,int){return -1;}
int prospero_hid_read(int,int,void*,int){return 0;}
void prospero_hid_close(int,int){}
bool ps5ObserveOwnedAllocation(const void* p) noexcept{return p!=nullptr;}
size_t sceKernelGetDirectMemorySize(){return 256*1024*1024;}
int sceKernelAllocateDirectMemory(int64_t,int64_t,size_t n,size_t alignment,int,int64_t*physical){assert(!storage);assert(!posix_memalign(&storage,alignment,n));*physical=0;return 0;}
int sceKernelMapDirectMemory(void**p,size_t,int,int,int64_t,size_t){*p=storage;return 0;}
int sceKernelMunmap(void*,size_t){operations.push_back("unmap");return failure==2?-1:0;}
int sceKernelReleaseDirectMemory(int64_t,size_t){operations.push_back("release");if(failure==3)return -1;free(storage);storage=nullptr;return 0;}
int sceKernelSendNotificationRequest(uint32_t,void*,size_t,int){notifications++;return 0;}
uint64_t sceKernelGetProcessTime(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
int sceKernelUsleep(uint32_t us){std::this_thread::sleep_for(std::chrono::microseconds(us));return 0;}
int sceUserServiceGetInitialUser(int32_t* user){*user=1;return 0;}
int scePadOpen(int32_t,int,int,const void*){return 42;}
int scePadClose(int){assert(motor_large.load()==0&&motor_small.load()==0);return 0;}
int scePadSetVibrationMode(int,int mode){assert(mode==2);return 0;}
int scePadSetVibration(int,const prospero_menu::LauncherMotors* motors){motor_large=motors->large_motor;motor_small=motors->small_motor;return 0;}
int scePadRead(int,PadSample* samples,int){samples[0]={};samples[0].connected=1;samples[0].lx=samples[0].ly=128;samples[0].buttons=fake_buttons.load();pad_reads.fetch_add(1);return 1;}
int sceSystemServiceHideSplashScreen(){return 0;}
int sceVideoOutOpen(int32_t,int32_t,int32_t,const void*){return 17;}
int sceVideoOutClose(int32_t){operations.push_back("close");return failure==1?-1:0;}
int sceVideoOutSetFlipRate(int32_t,int32_t){return 0;}
int sceVideoOutWaitVblank(int32_t){return 0;}
int sceVideoOutSubmitFlip(int32_t,int32_t,uint32_t,int64_t){
 flips.fetch_add(1);
 if(!output.empty()){
  std::ofstream f(output,std::ios::binary);f<<"P6\n1920 1080\n255\n";
  for(unsigned y=0;y<1080;y++)for(unsigned x=0;x<1920;x++){auto px=*reinterpret_cast<uint32_t*>(static_cast<char*>(storage)+ps5::demo::tiled_byte_offset(x,y));char rgb[]={char(px&255),char((px>>8)&255),char((px>>16)&255)};f.write(rgb,3);}
  output.clear();
 }return 0;
}
}
namespace ps5::demo {
extern "C" void sceVideoOutSetBufferAttribute2(VideoAttribute*,uint64_t,uint32_t,uint32_t,uint32_t,uint64_t,uint32_t,uint64_t){}
extern "C" int sceVideoOutRegisterBuffers2(int32_t,int32_t,int32_t,VideoBuffer*,int32_t,VideoAttribute*,int32_t,void*){return 0;}
}
static pthread_t jni_owner{};static std::string ui_strings[105];static unsigned java_calls=0;
static void check_jni(){assert(pthread_equal(jni_owner,pthread_self()));}
static jmethodID method_id(JNIEnv*,jclass,const char*,const char*){check_jni();return reinterpret_cast<jmethodID>(1);}
static jobject java_tick(JNIEnv*,jclass,jmethodID,va_list args){check_jni();++java_calls;unsigned buttons=va_arg(args,jint);if(buttons&0x4000)ui_strings[10]="LAUNCH";return reinterpret_cast<jobject>(1);}
static jsize array_length(JNIEnv*,jarray){check_jni();return 105;}
static jobject array_element(JNIEnv*,jobjectArray,jsize index){check_jni();return reinterpret_cast<jobject>(uintptr_t(index+10));}
static const char* utf_chars(JNIEnv*,jstring value,jboolean*){check_jni();return ui_strings[reinterpret_cast<uintptr_t>(value)-10].c_str();}
static void release_chars(JNIEnv*,jstring,const char*){check_jni();}
static void delete_ref(JNIEnv*,jobject){check_jni();}
static jboolean exception_check(JNIEnv*){check_jni();return JNI_FALSE;}
static bool update() noexcept{return false;}static bool stop() noexcept{return true;}
static void animation_check(ps5::demo::Canvas& c) noexcept {
 prospero_menu::fields[30][0]=0;prospero_menu::focus={};
 prospero_menu::animating=false;prospero_menu::selection(c,100,100,400,80);
 prospero_menu::selection(c,800,400,300,80);
 assert(prospero_menu::focus.x>100&&prospero_menu::focus.x<800&&prospero_menu::animating);
 for(int i=0;i<40;i++){prospero_menu::animating=false;prospero_menu::selection(c,800,400,300,80);}
 assert(!prospero_menu::animating&&prospero_menu::focus.x==800);
 prospero_menu::pressed_at=prospero_menu::now_ms();prospero_menu::selection(c,800,400,300,80);assert(prospero_menu::animating);
 snprintf(prospero_menu::fields[30].data(),512,"ON");prospero_menu::animating=false;prospero_menu::selection(c,400,300,600,90);
 assert(!prospero_menu::animating&&prospero_menu::focus.x==400&&prospero_menu::focus.w==600);
 prospero_menu::fields[30][0]=0;prospero_menu::pressed_at=0;
}
int main(int argc,char**argv){assert(argc==2);
 const char* values[]={"Your next world.","Starts right here.","Pick your instance. Make it your world.","","","Not signed in","PLAY DEMO","L1 / R1  Top bar     D-PAD  Navigate     X  Select     CIRCLE  Library","MICROSOFT ACCOUNT","0","WAIT","0"};
 for(int i=0;i<12;i++)snprintf(prospero_menu::fields[i].data(),512,"%s",values[i]);
 snprintf(prospero_menu::fields[13].data(),512,"7");
 const char* names[]={"Vanilla 26.3","Quiet mornings","Amethyst skies","A fresh start","Vanilla 26.2","Weekend world"};
 for(int i=0;i<6;i++){int at=32+i*4;snprintf(prospero_menu::fields[at].data(),512,"%s",names[i]);snprintf(prospero_menu::fields[at+1].data(),512,"%s",i==4?"26.2":"26.3");snprintf(prospero_menu::fields[at+2].data(),512,"%d",i);snprintf(prospero_menu::fields[at+3].data(),512,"READY");}
 snprintf(prospero_menu::fields[56].data(),512,"");snprintf(prospero_menu::fields[58].data(),512,"-1");snprintf(prospero_menu::fields[59].data(),512,"ADD");
 output=std::string(argv[1])+"/home.ppm";
 prospero_menu::focus={};assert(ps5::demo::run_ui_until(prospero_menu::draw,update,stop,"preview"));assert((operations==std::vector<std::string>{"close","unmap","release"})&&!storage);
 snprintf(prospero_menu::fields[11].data(),512,"3");snprintf(prospero_menu::fields[12].data(),512,"2");
 snprintf(prospero_menu::fields[3].data(),512,"ABCD-EFGH");snprintf(prospero_menu::fields[4].data(),512,"https://www.microsoft.com/link");snprintf(prospero_menu::fields[2].data(),512,"Approve sign-in on your phone or computer");
 output=std::string(argv[1])+"/signin.ppm";operations.clear();prospero_menu::focus={};assert(ps5::demo::run_ui_until(prospero_menu::draw,update,stop,"preview"));
 for(const char* scene:{"keybinds","uninstall","shaders","mods-installed","mods-downloading","mods","empty","create","settings","detail","offline","offline-edit","delete","delete-confirm","edit","keyboard","intro","intro-checkbox","intro-unchecked","controls","pending","account-saved","dropdown-version","dropdown-icons","dropdown-resolution","loading-controls","instances","controls-menus","controls-keyboard","controls-shortcuts","controls-touchpad","settings-top"}){
  int page=std::strcmp(scene,"uninstall")==0?14:std::strcmp(scene,"keybinds")==0?13:(std::strncmp(scene,"mods",4)==0||std::strcmp(scene,"shaders")==0)?12:std::strcmp(scene,"account-saved")==0?3:std::strcmp(scene,"instances")==0?0:std::strcmp(scene,"settings-top")==0?2:std::strncmp(scene,"controls-",9)==0?8:std::strcmp(scene,"loading-controls")==0?11:std::strncmp(scene,"delete",6)==0?9:std::strcmp(scene,"offline-edit")==0?5:std::strcmp(scene,"pending")==0?4:std::strcmp(scene,"controls")==0?8:std::strncmp(scene,"intro",5)==0?7:std::strcmp(scene,"empty")==0?0:std::strcmp(scene,"create")==0?1:std::strcmp(scene,"settings")==0?2:(std::strcmp(scene,"detail")==0||std::strcmp(scene,"offline")==0)?4:std::strcmp(scene,"edit")==0?5:6;
  snprintf(prospero_menu::fields[11].data(),512,"%d",page);snprintf(prospero_menu::fields[12].data(),512,"%d",page==2?1:page==3?2:0);snprintf(prospero_menu::fields[13].data(),512,"0");snprintf(prospero_menu::fields[16].data(),512,"Vanilla 26.3");snprintf(prospero_menu::fields[17].data(),512,"26.3");snprintf(prospero_menu::fields[18].data(),512,"1");snprintf(prospero_menu::fields[22].data(),512,"Weekend world");snprintf(prospero_menu::fields[23].data(),512,"26.3");snprintf(prospero_menu::fields[24].data(),512,"2");snprintf(prospero_menu::fields[25].data(),512,"1920 x 1080");snprintf(prospero_menu::fields[26].data(),512,"4");snprintf(prospero_menu::fields[27].data(),512,"ON");snprintf(prospero_menu::fields[29].data(),512,"Weekend world");snprintf(prospero_menu::fields[2].data(),512,"");snprintf(prospero_menu::fields[68].data(),512,"ON");snprintf(prospero_menu::fields[65].data(),512,"26.3 native gameplay baseline");
  snprintf(prospero_menu::fields[73].data(),512,"%s",std::strncmp(scene,"offline",7)==0?"OFFLINE BRANCH":"TEMP GAMETEST");snprintf(prospero_menu::fields[15].data(),512,"0");if(std::strcmp(scene,"delete-confirm")==0)snprintf(prospero_menu::fields[15].data(),512,"1");if(std::strcmp(scene,"offline-edit")==0)snprintf(prospero_menu::fields[15].data(),512,"3");
  snprintf(prospero_menu::fields[71].data(),512,"%s",std::strcmp(scene,"offline")==0?"OFFLINE":"");if(std::strcmp(scene,"offline")==0){snprintf(prospero_menu::fields[72].data(),512,"OwnedPlayer");snprintf(prospero_menu::fields[15].data(),512,"3");}
  if(page==7){snprintf(prospero_menu::fields[15].data(),512,"1");snprintf(prospero_menu::fields[7].data(),512,"D-PAD / STICK LEFT / RIGHT  Choose     X  Select / toggle");}
  if(std::strncmp(scene,"intro-",6)==0)snprintf(prospero_menu::fields[15].data(),512,"0");
  if(std::strcmp(scene,"intro-unchecked")==0)snprintf(prospero_menu::fields[68].data(),512,"OFF");
  if(page==11){snprintf(prospero_menu::fields[94].data(),512,"OFF");snprintf(prospero_menu::fields[95].data(),512,"READY");snprintf(prospero_menu::fields[15].data(),512,"1");}
  if(page==8)snprintf(prospero_menu::fields[7].data(),512,"CIRCLE / OPTIONS  Back");
  if(std::strcmp(scene,"pending")==0){snprintf(prospero_menu::fields[16].data(),512,"Vanilla 26.2");snprintf(prospero_menu::fields[17].data(),512,"26.2");snprintf(prospero_menu::fields[69].data(),512,"PENDING");snprintf(prospero_menu::fields[6].data(),512,"COMING SOON");snprintf(prospero_menu::fields[65].data(),512,"Download available. Launch support is not ready yet.");}
  if(std::strcmp(scene,"account-saved")==0){snprintf(prospero_menu::fields[11].data(),512,"3");snprintf(prospero_menu::fields[12].data(),512,"2");snprintf(prospero_menu::fields[3].data(),512,"");snprintf(prospero_menu::fields[5].data(),512,"OwnedPlayer");snprintf(prospero_menu::fields[81].data(),512,"OwnedPlayer");std::string head;for(int i=0;i<64;i++)head+=(i/8==3&&(i%8==2||i%8==5))?"4870a0":"b78362";snprintf(prospero_menu::fields[80].data(),512,"%s",head.c_str());}
  if(std::strncmp(scene,"dropdown-",9)==0){snprintf(prospero_menu::fields[11].data(),512,"10");snprintf(prospero_menu::fields[73].data(),512,"TEMP GAMETEST");snprintf(prospero_menu::fields[82].data(),512,"%s",std::strcmp(scene,"dropdown-icons")==0?"Choose instance icon":std::strcmp(scene,"dropdown-resolution")==0?"Game resolution":"Choose version");snprintf(prospero_menu::fields[83].data(),512,"8");snprintf(prospero_menu::fields[84].data(),512,"0");snprintf(prospero_menu::fields[93].data(),512,"%s",std::strcmp(scene,"dropdown-icons")==0?"1":"0");const char* icons[]={"ProsperoCraft","Grass","Nether star","Ender pearl","Redstone flame","Planks","Gold","Stone"};const char* versions[]={"26.4-snapshot-5 [Coming soon]","26.4-snapshot-4 [Coming soon]","26.3","26.3-rc-3 [Coming soon]","26.2 [Coming soon]","26.1 [Coming soon]","26.1-snapshot-2 [Coming soon]","26.1-snapshot-1 [Coming soon]"};for(int n=0;n<8;n++)snprintf(prospero_menu::fields[85+n].data(),512,"%s",std::strcmp(scene,"dropdown-icons")==0?icons[n]:versions[n]);if(std::strcmp(scene,"dropdown-resolution")==0){const char* modes[]={"1280 x 720","1600 x 900","1920 x 1080","2560 x 1440","3840 x 2160"};for(int n=0;n<5;n++)snprintf(prospero_menu::fields[85+n].data(),512,"%s",modes[n]);snprintf(prospero_menu::fields[83].data(),512,"5");snprintf(prospero_menu::fields[93].data(),512,"3");}}
  snprintf(prospero_menu::fields[28].data(),512,"CONTENT");snprintf(prospero_menu::fields[12].data(),512,"%d",page==0||page==1?0:page==2?1:page==3?2:0);snprintf(prospero_menu::fields[74].data(),512,"0");
  if(std::strcmp(scene,"empty")==0){snprintf(prospero_menu::fields[13].data(),512,"1");snprintf(prospero_menu::fields[32].data(),512,"");snprintf(prospero_menu::fields[33].data(),512,"");snprintf(prospero_menu::fields[34].data(),512,"-1");snprintf(prospero_menu::fields[35].data(),512,"ADD");}
  if(std::strcmp(scene,"instances")==0){snprintf(prospero_menu::fields[13].data(),512,"3");const char* cards[]={"Vanilla 26.3","Weekend world",""};for(int i=0;i<3;i++){int at=32+i*4;snprintf(prospero_menu::fields[at].data(),512,"%s",cards[i]);snprintf(prospero_menu::fields[at+1].data(),512,"%s",i<2?"26.3":"");snprintf(prospero_menu::fields[at+2].data(),512,"%d",i<2?i+1:-1);snprintf(prospero_menu::fields[at+3].data(),512,"%s",i<2?"READY":"ADD");}}
  if(page==13){snprintf(prospero_menu::fields[82].data(),512,"Controller keybinds");snprintf(prospero_menu::fields[70].data(),512,"USB keyboard/mouse use Minecraft Controls. Controller menu controls stay available.");snprintf(prospero_menu::fields[84].data(),512,"0");const char* bindings[]={"Restore default controller bindings","Left stick Up : W","Left stick Down : S","Left stick Left : A","Left stick Right : D","Cross : Space","Triangle : E"};for(int n=0;n<7;n++)snprintf(prospero_menu::fields[85+n].data(),512,"%s",bindings[n]);snprintf(prospero_menu::fields[15].data(),512,"2");}
  if(page==1)snprintf(prospero_menu::fields[82].data(),512,"Fabric");
  if(page==12){snprintf(prospero_menu::fields[82].data(),512,"Mods");snprintf(prospero_menu::fields[70].data(),512,"Fabric mods for 26.3. Required dependencies included.");snprintf(prospero_menu::fields[92].data(),512,"Search Modrinth...");snprintf(prospero_menu::fields[91].data(),512,"2");snprintf(prospero_menu::fields[93].data(),512,"4");snprintf(prospero_menu::fields[83].data(),512,"184");snprintf(prospero_menu::fields[84].data(),512,"0");const char* hits[]={"[X] Vitrail Shaders / 84500 downloads","[X] Sodium / 10000000 downloads","[ ] Fabric API / 1000000 downloads","[ ] Mod Menu / 900000 downloads","[ ] Example compatible mod / 800000 downloads","[ ] Another compatible mod / 700000 downloads"};for(int n=0;n<6;n++)snprintf(prospero_menu::fields[85+n].data(),512,"%s",hits[n]);snprintf(prospero_menu::fields[15].data(),512,"4");}
  if(page==12)snprintf(prospero_menu::fields[103].data(),512,"BROWSE");
  if(page==12){for(int n=0;n<6;n++){std::string pixels;for(int i=0;i<256;i++)pixels+=(i/16>3&&i/16<12&&i%16>3&&i%16<12)?(n%2?"79b8eb":"87dc62"):"123c29";snprintf(prospero_menu::fields[96+n].data(),8192,"%s",pixels.c_str());}if(std::strcmp(scene,"mods-installed")==0){snprintf(prospero_menu::fields[103].data(),512,"INSTALLED");for(int n=0;n<6;n++)snprintf(prospero_menu::fields[85+n].data(),512,"[I] installed-mod-%d.jar",n+1);}if(std::strcmp(scene,"mods-downloading")==0){snprintf(prospero_menu::fields[64].data(),512,"BUSY");snprintf(prospero_menu::fields[8].data(),512,"CONTENT");snprintf(prospero_menu::fields[2].data(),512,"Downloading Vitrail Shaders");snprintf(prospero_menu::fields[20].data(),512,"450");snprintf(prospero_menu::fields[102].data(),8192,"%s",prospero_menu::fields[96].data());}}

  if(page==14){snprintf(prospero_menu::fields[13].data(),512,"3");snprintf(prospero_menu::fields[32].data(),512,"A quiet morning");snprintf(prospero_menu::fields[33].data(),512,"WORLD");snprintf(prospero_menu::fields[34].data(),512,"Quiet Morning");snprintf(prospero_menu::fields[35].data(),512,"PINNED");snprintf(prospero_menu::fields[36].data(),512,"Building with friends");snprintf(prospero_menu::fields[37].data(),512,"SERVER");snprintf(prospero_menu::fields[38].data(),512,"mc.example.test:25565");snprintf(prospero_menu::fields[39].data(),512,"PINNED");snprintf(prospero_menu::fields[40].data(),512,"A new adventure");snprintf(prospero_menu::fields[41].data(),512,"WORLD");snprintf(prospero_menu::fields[42].data(),512,"New Adventure");snprintf(prospero_menu::fields[43].data(),512,"");}
  if(page==8){int section=std::strcmp(scene,"controls-menus")==0?1:std::strcmp(scene,"controls-keyboard")==0?2:std::strcmp(scene,"controls-shortcuts")==0?3:std::strcmp(scene,"controls-touchpad")==0?4:0;snprintf(prospero_menu::fields[74].data(),512,"%d",section);}
  if(page==12||page==14){const char* names[]={"vitrail","sodium","fabric","modmenu","alpha","jpeg"};for(int n=0;n<6;n++){std::ifstream input(std::string("/Users/mateocogeanu/Documents/ChatGPT/PS5_Homebrew/.tools/github-publish/ps5-minecraft-java/build/content107-icons/")+names[n]+".hex");std::string pixels((std::istreambuf_iterator<char>(input)),std::istreambuf_iterator<char>());if(pixels.size()==6144)snprintf(prospero_menu::fields[96+n].data(),8192,"%s",pixels.c_str());}if(std::strcmp(scene,"mods-installed")==0)snprintf(prospero_menu::fields[15].data(),512,"20");if(std::strcmp(scene,"mods-downloading")==0)snprintf(prospero_menu::fields[102].data(),8192,"%s",prospero_menu::fields[96].data());}
  if(page==14){snprintf(prospero_menu::fields[82].data(),512,"Uninstall this file?");snprintf(prospero_menu::fields[85].data(),512,"vitrail-0.13.0-beta+mc26.3.jar");snprintf(prospero_menu::fields[70].data(),512,"Only this file is removed. Worlds and settings are kept. Mods that depend on it may stop working.");snprintf(prospero_menu::fields[15].data(),512,"0");}
  if(std::strcmp(scene,"shaders")==0){snprintf(prospero_menu::fields[82].data(),512,"Shaders");snprintf(prospero_menu::fields[95].data(),512,"SHADOWS: 50%%");snprintf(prospero_menu::fields[15].data(),512,"11");}
  if(std::strcmp(scene,"settings-top")==0){snprintf(prospero_menu::fields[28].data(),512,"TOP");snprintf(prospero_menu::fields[15].data(),512,"-1");}
  output=std::string(argv[1])+"/"+scene+".ppm";prospero_menu::focus={};assert(ps5::demo::run_ui_until(prospero_menu::draw,update,stop,"preview"));if(std::strcmp(scene,"settings-top")==0){assert(prospero_menu::focus.x==1245&&prospero_menu::focus.y==52&&prospero_menu::focus.w==280&&prospero_menu::focus.h==68);}
 }
 assert(ps5::demo::run_ui_until(animation_check,update,stop,""));
 for(failure=1;failure<=3;failure++){operations.clear();assert(!ps5::demo::run_ui_until(prospero_menu::draw,update,stop,"fixture"));assert(storage);assert(operations.size()==unsigned(failure));free(storage);storage=nullptr;}
 failure=0;operations.clear();unsigned before=flips.load();
 int notifications_before=notifications;assert(prospero_menu::start_frontend());assert(notifications==notifications_before);assert(flips.load()>before); // no JVM exists in this process
 auto await=[&](auto predicate){auto until=std::chrono::steady_clock::now()+std::chrono::seconds(3);while(!predicate()&&std::chrono::steady_clock::now()<until)std::this_thread::sleep_for(std::chrono::milliseconds(1));assert(predicate());};
 // Simulate blocked/unavailable Java initialization. Native drawing/controller
 // polling must remain responsive and preserve ordered button edges.
 unsigned reads=pad_reads.load();fake_buttons=0x40;await([&]{return pad_reads.load()>reads+1;});fake_buttons=0;reads=pad_reads.load();await([&]{return pad_reads.load()>reads+1;});
 fake_buttons=0x4000;reads=pad_reads.load();await([&]{return pad_reads.load()>reads+1;});fake_buttons=0;
 assert(!prospero_menu::online.load());assert(prospero_menu::take_input()==0x40);assert(prospero_menu::take_input()==0x4000);assert(prospero_menu::take_input()==0);
 // A failed Java boot leaves a real, responsive native failure screen.
 prospero_menu::show_failure();reads=pad_reads.load();await([&]{return pad_reads.load()>reads+1;});assert(!prospero_menu::display_done.load());
 prospero_menu::exit_requested=true;pthread_join(prospero_menu::ui_thread,nullptr);
 assert(prospero_menu::display_done.load()&&prospero_menu::display_ok.load());assert(!storage);assert((operations==std::vector<std::string>{"close","unmap","release"}));
 operations.clear();notifications_before=notifications;assert(prospero_menu::start_frontend());assert(notifications==notifications_before);jni_owner=pthread_self();
 for(int i=0;i<105;++i)ui_strings[i]=i<12?values[i]:"";
 JNINativeInterface_ functions{};functions.GetStaticMethodID=method_id;functions.CallStaticObjectMethodV=java_tick;
 functions.GetArrayLength=array_length;functions.GetObjectArrayElement=array_element;functions.GetStringUTFChars=utf_chars;functions.ReleaseStringUTFChars=release_chars;functions.DeleteLocalRef=delete_ref;functions.ExceptionCheck=exception_check;
 JNIEnv environment{&functions};prospero_menu::push_input(0x4000);
 assert(prospero_menu::menu(&environment,reinterpret_cast<jclass>(1))==JNI_TRUE);assert(java_calls>0);
 assert(!storage&&prospero_menu::display_done.load()&&prospero_menu::display_ok.load());
 assert((operations==std::vector<std::string>{"close","unmap","release"}));
 puts("PASS actual JNI bridge via fixture table: callbacks remain on JVM caller thread, input delivered, launch waits for UI close/unmap/release/join");
 puts("PASS native frontend presents before any JVM; remains responsive with blocked account boot, ordered input mailbox, boot failure screen and joined cleanup");
 puts("PASS actual native UI draw/returning renderer fixture; close-before-unmap-before-release, retain remaining ownership on close/unmap/release failures; not PS5 handoff proof");
}
'''
(w/'preview.cpp').write_text(source)
jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
subprocess.run(['clang++','-arch','x86_64','-std=c++20','-O1','-I'+str(runtime/'native/renderer'),'-I'+str(runtime/'build/native'),'-I'+str(runtime/'src'),'-I'+str(jdk/'include'),'-I'+str(jdk/'include/darwin'),str(w/'preview.cpp'),'-o',str(w/'preview')],check=True)
subprocess.run([str(w/'preview'),str(w)],check=True,timeout=30)
from PIL import Image
for name in ['keybinds','uninstall','shaders','mods-installed','mods-downloading','mods','home','signin','empty','create','settings','detail','offline','offline-edit','delete','delete-confirm','edit','keyboard','intro','intro-checkbox','intro-unchecked','controls','pending','account-saved','dropdown-version','dropdown-icons','dropdown-resolution','loading-controls','instances','controls-menus','controls-keyboard','controls-shortcuts','controls-touchpad','settings-top']:
 with Image.open(w/(name+'.ppm'))as picture:picture.save(w/(name+'.png'))
print(w/'home.png')
