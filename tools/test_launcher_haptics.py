#!/usr/bin/env python3
"""Exercise the actual motor worker and Java semantic/preference mailbox."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
from host_toolchain import java_home, launcher_classpath, executable
JDK=java_home()
cpp=r'''
#include <atomic>
#include <cassert>
#include <chrono>
#include <thread>
#include <vector>
#include <mutex>
#include "haptics.hpp"
struct Write {int large,small;std::uint64_t time;};
static std::mutex lock;static std::vector<Write> writes;static std::atomic<int> modes{0};static bool fail_mode=false;static std::atomic<bool> fail_trigger{false};static std::atomic<int> trigger_mode{0},trigger_side{-1},trigger_writes{0},trigger_mask{0};
extern "C" std::uint64_t sceKernelGetProcessTime(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
extern "C" int sceKernelUsleep(std::uint32_t us){std::this_thread::sleep_for(std::chrono::microseconds(us));return 0;}
extern "C" int scePadSetVibrationMode(int handle,int mode){assert(handle==42&&mode==2);++modes;return fail_mode?-1:0;}
extern "C" int scePadSetVibration(int handle,const prospero_menu::LauncherMotors* m){assert(handle==42);std::lock_guard guard(lock);writes.push_back({m->large_motor,m->small_motor,sceKernelGetProcessTime()/1000});return 0;}
extern "C" int scePadSetTriggerEffect(int handle,const prospero_menu::LauncherTriggerEffect* e){assert(handle==42&&e->mask==3);int mask=(e->left.mode?1:0)|(e->right.mode?2:0);for(const auto* c:{&e->left,&e->right})if(c->mode)assert(c->mode==2&&c->data[0]==2&&c->data[1]==3&&c->data[2]==2);trigger_mask=mask;trigger_side=mask==1?0:mask==2?1:-1;trigger_mode=mask?2:0;++trigger_writes;return mask&&fail_trigger?-1:0;}

static auto now(){return sceKernelGetProcessTime()/1000;}
static void pause(int ms){std::this_thread::sleep_for(std::chrono::milliseconds(ms));}
static std::vector<Write> snapshot(){std::lock_guard guard(lock);return writes;}
int main(){
 prospero_menu::Haptics h;assert(h.start(42));h.control(true,now());h.observe(0,"",true,now());h.observe(1,"confirm",true,now());
 // No UI polling/rendering for200ms: the motor must still stop on its deadline.
 pause(200);auto events=snapshot();assert(events.size()==2&&events[0].large==18&&events[0].small==64&&events[1].small==0&&events[1].large==0);assert(events[1].time-events[0].time<150);
 h.control(true,now());h.observe(1,"confirm",true,now());pause(30);assert(snapshot().size()==2); // deduplicated
 h.observe(2,"success",true,now());pause(15);h.control(false,now());pause(20);events=snapshot();assert(events.back().small==0&&events.back().large==0); // opt-out/disconnect
 h.observe(3,"error",false,now());h.control(true,now());h.observe(3,"error",true,now());pause(20);assert(snapshot().size()==events.size()); // no replay
 h.control(true,now());h.page_ready(3,0);pause(15);assert(trigger_mask==3); // armed before any press/page change
 h.page_ready(3,1);pause(15);assert(trigger_mask==2);pause(70);assert(trigger_mask==2); // held side remains released
 h.control(true,now());h.page_ready(3,0);pause(15);assert(trigger_mask==3); // neutral rearms
 h.page_ready(2,0);pause(15);assert(trigger_mask==2);h.page_ready(0,0);pause(15);assert(trigger_mask==0);
 h.control(true,now());h.page_ready(3,0);pause(15);assert(trigger_mask==3);pause(300);assert(trigger_mask==0); // stalled UI watchdog
 h.control(false,now());int old_triggers=trigger_writes;h.page_ready(3,0);pause(20);assert(trigger_writes==old_triggers);
 h.control(true,now());fail_trigger=true;h.page_ready(1,0);pause(25);assert(trigger_mode==0);fail_trigger=false;h.control(false,now());pause(15);h.control(true,now());h.page_ready(2,0);pause(15);assert(trigger_mask==2);h.close();assert(trigger_mode==0);assert(!h.started&&h.handle==-1);events=snapshot();assert(events.back().small==0&&events.back().large==0);
 fail_mode=true;prospero_menu::Haptics unavailable;assert(unavailable.start(42));int count=modes.load();unavailable.control(true,now());unavailable.observe(0,"",true,now());unavailable.observe(1,"error",true,now());pause(60);assert(modes==count+1);unavailable.close();
 puts("PASS actual vibration worker:compatible two-byte ABI,independent bounded stop during stalled UI,sequence dedup,opt-out/disconnect cancellation,no stale replay,joined zero-before-close,nonfatal unavailable API;host fixture");
}
'''
java=r'''
import java.nio.file.*;
public class HapticsCheck {
 public static void main(String[] args)throws Exception {
  Path root=Path.of(args[0]);var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;lib.save();var model=new ProsperoLauncher(new ProsperoAuth(),root,null);
  var state=model.tick(0x800);if(!state[79].equals("ON")||!state[78].equals("move"))throw new AssertionError("initial preference/confirm");
  String sequence=state[77];if(!model.tick(0)[77].equals(sequence))throw new AssertionError("idle event");
  state=model.tick(0x40);if(!state[78].equals("move"))throw new AssertionError("focus cue");
  state=model.tick(0x1000);if(!state[79].equals("OFF")||new ProsperoLibrary(root).settings().vibration)throw new AssertionError("disable persistence");
  state=model.tick(0x1000);if(!state[79].equals("ON")||!new ProsperoLibrary(root).settings().vibration)throw new AssertionError("enable persistence");
  if(!model.tick(0x2000)[78].equals("back"))throw new AssertionError("back cue");
  Path file=root.resolve("library.json");Files.writeString(file,Files.readString(file).replace("\"vibration\": true,",""));if(!new ProsperoLibrary(root).settings().vibration)throw new AssertionError("legacy default");
  Path rejected=root.resolve("rejected");var blocked=new ProsperoLibrary(rejected);blocked.settings().showIntro=false;blocked.add("Unsupported","1.21.1",1);blocked.save();var guard=new ProsperoLauncher(new ProsperoAuth(),rejected,null);guard.tick(0x4000);if(!guard.tick(0x4000)[78].equals("error"))throw new AssertionError("unsupported launch error cue");
  Path launching=root.resolve("launching");var ready=new ProsperoLibrary(launching);ready.settings().showIntro=false;var playable=ready.add("Ready","26.3",1);ready.ready(playable,true);ready.save();var click=new ProsperoLauncher(new ProsperoAuth(),launching,null);click.tick(0x4000);if(!click.tick(0x4000)[78].equals("confirm"))throw new AssertionError("Play task-start confirmation");
  System.out.println("PASS actual Java haptic mailbox:focus/confirm/back cues,stable idle sequence,Settings Triangle persistent off/on,older library default;96field contract retained");
 }
}'''
with tempfile.TemporaryDirectory() as d:
 w=Path(d);(w/'test.cpp').write_text(cpp)
 subprocess.run([executable('clang++',env='CXX'),'-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT/'client/launcher'),str(w/'test.cpp'),'-o',str(w/'test')],check=True)
 subprocess.run([str(w/'test')],check=True)
 (w/'HapticsCheck.java').write_text(java);cp=launcher_classpath()
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'HapticsCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(w)+':'+cp,'HapticsCheck',str(w/'data')],check=True)
