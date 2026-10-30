/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include "console_model.hpp"
extern "C" unsigned long long sceKernelGetMainSocId(void);
namespace prospero_menu::hardware {
// Written once on the launcher startup thread, before any UI/JVM worker starts.
// CPU JNI and Vulkan only consume this snapshot; neither queries the hardware.
class Identity {
 ps5::console::SocResult value_{};bool initialized_=false;
public:
 void initialize(ps5::console::SocQuery query) {
  if(initialized_)return;
  value_=ps5::console::read_soc(query);initialized_=true;
 }
 const ps5::console::SocResult& value()const{return value_;}
};
inline Identity snapshot;
inline void initialize(){snapshot.initialize(sceKernelGetMainSocId);}
inline const ps5::console::SocResult& identity(){return snapshot.value();}
}
