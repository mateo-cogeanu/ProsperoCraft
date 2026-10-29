/* SPDX-License-Identifier: LGPL-2.0-or-later */
#pragma once
#include <mutex>
#include "ps5_audio_mutex.hpp"
namespace ps5audio {
// Keep at most one drained native output reserved across logical device reloads.
// The process owns this reservation until title exit; no mixer thread is retained.
class PortPool {
 ps5audio::Mutex mutex;int idle=-1;
public:
 int take(){const auto lock=std::lock_guard{mutex};int port=idle;idle=-1;return port;}
 bool keep(int port){const auto lock=std::lock_guard{mutex};if(port<0||idle>=0)return false;idle=port;return true;}
};
}
