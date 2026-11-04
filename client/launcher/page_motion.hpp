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
inline float card_detail_alpha(float progress)noexcept{float t=std::clamp(progress/0.65f,0.f,1.f);return t*t*(3-2*t);}
inline float card_library_alpha(float progress)noexcept{float t=std::clamp(progress/0.55f,0.f,1.f);return 1-t*t*(3-2*t);}
struct SelectionMenu {float x,y,w,h;int visible;static constexpr int pitch=64;float first_y()const noexcept{return y+24;}};
inline SelectionMenu selection_menu(int count,int limit,float label_width,float title_width,bool icons=false)noexcept{int visible=std::clamp(count,0,limit);float w=std::clamp(std::max(label_width+(icons?60:0),title_width)+96.f,600.f,1100.f),h=48.f+visible*SelectionMenu::pitch;return {(1920-w)/2,155+(850-h)/2,w,h,visible};}
inline int selection_menu_hit(const SelectionMenu& menu,int x,int y,float position,int count)noexcept{if(x<menu.x+12||x>=menu.x+menu.w-20||y<menu.first_y()||y>=menu.first_y()+menu.visible*menu.pitch)return -1;int index=int(position+(y-menu.first_y())/menu.pitch);return index>=0&&index<count?index:-1;}
struct IconGrid {float x,y,w,h;static constexpr int columns=8,pitch=128,padding=24;};
inline IconGrid icon_grid(int count)noexcept{int columns=std::clamp(count,1,8),rows=(std::max(0,count)+7)/8;float w=48.f+columns*128,h=48.f+rows*128;return {(1920-w)/2,155+(850-h)/2,w,h};}
inline int icon_grid_hit(const IconGrid& grid,int x,int y,int count)noexcept{float xx=x-grid.x-24,yy=y-grid.y-24;if(xx<0||yy<0||xx>=grid.w-48||yy>=grid.h-48)return -1;int col=int(xx)/128,row=int(yy)/128,index=row*8+col;return index<count&&int(xx)%128>=6&&int(xx)%128<122&&int(yy)%128>=6&&int(yy)%128<122?index:-1;}
struct PageTurn {
 std::uint64_t began=0;int direction=1;bool enabled=false;
 void start(int d,std::uint64_t now,bool reduced)noexcept{direction=d<0?-1:1;began=now;enabled=!reduced;}
 float progress(std::uint64_t now)const noexcept{if(!enabled)return 1;float t=now>=began?std::min(1.f,float(now-began)/280):0;return t*t*(3-2*t);}
 bool moving(std::uint64_t now)const noexcept{return progress(now)<1;}
};
}
