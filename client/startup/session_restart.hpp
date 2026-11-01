/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <atomic>
extern "C" int sceSystemServiceLoadExec(const char*,const char*const*);
namespace prospero_session {
class CleanExitGate {
 std::atomic<bool> armed{false};
public:
 void arm(){armed.store(true,std::memory_order_release);}
 bool take(int status){return armed.exchange(false,std::memory_order_acq_rel)&&status==0;}
};
// Success replaces the process and never returns. Any return is failure.
// OS replacement is the ownership barrier for retained WSI/cursor/audio memory,
// native worker threads, the one supported JVM and game classloader statics.
inline int restart_library(){
 const char* arguments[]={"--prospero-library",nullptr};
 return sceSystemServiceLoadExec("/app0/eboot.bin",arguments);
}
}
