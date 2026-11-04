/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
namespace prospero_menu {
struct Glide {
 float from=0,target=0;std::uint64_t began=0;unsigned duration=180;
 float value(std::uint64_t now)const noexcept {float t=now>=began?std::min(1.f,float(now-began)/duration):0;float e=t*t*(3-2*t);return from+(target-from)*e;}
 bool moving(std::uint64_t now)const noexcept{return from!=target&&now<began+duration;}
 void snap(float v)noexcept{from=target=v;began=0;}
 void to(float v,std::uint64_t now,bool reduced=false)noexcept{if(reduced){snap(v);return;}if(v==target)return;from=value(now);target=v;began=now;}
};
struct CardRect {float x,y,w,h;};
inline CardRect opening_card_rect(int slot,float progress)noexcept{slot=std::clamp(slot,0,7);float t=std::clamp(progress,0.f,1.f);CardRect from{float(70+slot%4*450),float(342+slot/4*272),420,242};return {from.x*(1-t),from.y+(155-from.y)*t,from.w+(1920-from.w)*t,from.h+(850-from.h)*t};}
struct PageTurn {
 std::uint64_t began=0;int direction=1;bool enabled=false;
 void start(int d,std::uint64_t now,bool reduced)noexcept{direction=d<0?-1:1;began=now;enabled=!reduced;}
 float progress(std::uint64_t now)const noexcept{if(!enabled)return 1;float t=now>=began?std::min(1.f,float(now-began)/280):0;return t*t*(3-2*t);}
 bool moving(std::uint64_t now)const noexcept{return progress(now)<1;}
};
}
