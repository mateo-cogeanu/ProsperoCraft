/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <algorithm>
#include <cstdint>
#include "../ports/sdl/ps5_hid.h"
namespace prospero_menu {
// Commands share the bounded UI mailbox. Expected page prevents stale clicks
// from activating a different screen after an asynchronous transition.
inline unsigned pointer_command(int page,int kind,int target,bool click){return 0x10000000u|(unsigned(page)<<20)|(unsigned(kind)<<16)|(click?0x8000:0)|unsigned(target);}
struct DesktopHit {int kind=-1,target=0;};
inline DesktopHit desktop_hit(int page,int x,int y,int first,int count,int slide=0,bool offline=false,bool installed=false,bool shader=false){
 auto box=[&](int a,int b,int w,int h){return x>=a&&x<a+w&&y>=b&&y<b+h;};
 bool modal=page==6||(page>=7&&page<=11)||page==14;
 if(!modal){int tx[]={865,1245,1555},tw[]={350,280,280};for(int i=0;i<3;i++)if(box(tx[i],52,tw[i],68))return {0,i};}
 if(page==0){for(int i=0;i<8&&first+i<count;i++)if(box(70+i%4*450,342+i/4*272+slide,420,242))return {1,first+i};}
 if(page==6){for(int i=0;i<40;i++)if(box(80+i%10*176,465+i/10*91,152,73))return {2,i};for(int i=0;i<5;i++)if(box(70+i*360,855,330,76))return {4,i};return {};}
 if(page==10){for(int i=0;i<8&&first+i<count;i++)if(box(265,285+i*72,1390,66))return {3,first+i};return {};}
 if(page==13){for(int i=0;i<7&&first+i<23;i++)if(box(70,340+i*78,1770,76))return {3,first+i};return {};}
 if(page>=1&&page<=5)y-=slide;
 if(page==1){for(int i=0;i<4;i++)if(box(760,320+i*110,1080,96))return {3,i};if(box(760,774,1080,76))return {3,4};}
 if(page==8){if(box(78,825,700,76))return {4,5};if(box(1050,825,700,76))return {4,6};}
 if(page==2&&box(110,705+slide,530,76))return {4,7};if(page==2&&box(110,795+slide,530,76))return {4,8};
 if(page==2){for(int i=0;i<7;i++)if(box(760,300+i*96,1080,86))return {3,i};}
 if(page==3&&box(1140,366,700,76))return {3,0};
 if(page==4){for(int i=0;i<(offline?4:3);i++)if(box(760,505+i*100,1080,76))return {3,i};}
 if(page==5){if(box(760,310,1080,96))return {3,0};if(box(760,420,1080,96))return {3,1};int rows[]={2,3,4,7,5,6};for(int i=0;i<6;i++)if(box(760+i%2*560,535+i/2*95,520,76))return {3,rows[i]};}
 if(page==7){if(box(240,773,330,76))return {3,1};if(box(680,773,430,76))return {3,0};}
 if(page==11){if(box(78,850,330,76))return {3,1};if(box(470,850,610,76))return {3,0};}
 if(page==14){if(box(760,740,520,76))return {3,0};if(box(1320,740,520,76))return {3,1};}
 if(page==12){if(box(70,325,1010,76))return {3,0};if(box(1120,325,720,76))return {3,1};if(box(70,435,330,76))return {3,2};if(box(430,435,330,76))return {3,3};if(shader&&box(800,435,470,76))return {3,11};if(box(1320,435,520,76))return {3,10};for(int i=0;i<count&&i<4;i++)if(box(70,535+i*92,1770,86))return {3,installed&&x>=1500?20+i:4+i};}
 return {};
}
inline char desktop_char(unsigned k,bool shift,bool caps){
 if(k>=4&&k<=29)return char((shift!=caps?'A':'a')+k-4);
 if(k>=30&&k<=39)return (shift?"!@#$%^&*()":"1234567890")[k-30];
 if(k>=89&&k<=97)return char('1'+k-89);if(k==98)return '0';if(k==99)return '.';
 const unsigned keys[]={44,45,46,47,48,49,51,52,53,54,55,56};const char normal[]=" -=[]\\;'`,./",upper[]=" _+{}|:\"~<>?";
 for(unsigned i=0;i<12;i++)if(k==keys[i])return shift?upper[i]:normal[i];return 0;
}
struct DesktopInput {
 struct Keyboard {int handle=-1;bool primed=false,held[256]{},blocked[256]{};int repeat=0;std::uint64_t at=0;};
 struct Mouse {int handle=-1;bool primed=false;unsigned held=0,blocked=0;};
 Keyboard keys[4];Mouse mice[4];float x=960,y=540;bool cursor=false;std::uint64_t retry=0;
 void close(){for(auto& k:keys){if(k.handle>=0)prospero_hid_close(0,k.handle);k=Keyboard{};}for(auto& m:mice){if(m.handle>=0)prospero_hid_close(1,m.handle);m=Mouse{};}cursor=false;}
 template<class Emit,class Point>bool poll(std::uint64_t now,Emit emit,Point point){
  bool changed=false;
  if(now>=retry){retry=now+2000;for(int i=0;i<4;i++){if(keys[i].handle<0)keys[i].handle=prospero_hid_open(0,i);if(mice[i].handle<0)mice[i].handle=prospero_hid_open(1,i);}}
  for(auto& k:keys){if(k.handle<0)continue;prospero_keyboard_packet packets[16]{};int n=prospero_hid_read(0,k.handle,packets,16);if(n<0||n>16){prospero_hid_close(0,k.handle);k=Keyboard{};continue;}
   auto key=[&](int code,unsigned mods,unsigned leds){unsigned b=code==82?0x10:code==81?0x40:code==80?0x80:code==79?0x20:code==41?0x2000:code==58?8:0;if(b)emit(b);else if(code==40||code==88)emit(0x20000000u|1);else if(code==42||code==76)emit(0x20000000u|2);else if(code==43)emit(0x20000000u|((mods&0x22)?4:3));else if(!(mods&0xdd)){char c=desktop_char(code,mods&0x22,leds&2);if(c)emit(0x30000000u|unsigned(c));}};
   unsigned mods=0,leds=0;
   for(int i=0;i<n;i++){auto& p=packets[i];bool held[256]{};mods=p.modifiers;leds=p.leds;if(p.connected&&!p.intercepted)for(auto code:p.keys)if(code>=4&&code<224)held[code]=true;
    if(!k.primed){for(int j=0;j<256;j++)k.blocked[j]=held[j];k.primed=true;}
    for(int j=4;j<224;j++){k.blocked[j]&=held[j];held[j]&=!k.blocked[j];if(held[j]&&!k.held[j]){key(j,mods,leds);k.repeat=j;k.at=now+450;changed=true;}k.held[j]=held[j];}
    if(!p.connected||p.intercepted){k.primed=false;k.repeat=0;}
   }
   // Repeat only on a fresh packet: no stale held action after read loss.
   if(n&&k.repeat&&k.held[k.repeat]&&now>=k.at){int c=k.repeat;if(c!=40&&c!=88&&c!=41&&c!=58&&c!=43){key(c,mods,leds);changed=true;}k.at=now+55;}
  }
  for(auto& m:mice){if(m.handle<0)continue;prospero_mouse_packet packets[16]{};int n=prospero_hid_read(1,m.handle,packets,16);if(n<0||n>16){prospero_hid_close(1,m.handle);m=Mouse{};continue;}
   for(int i=0;i<n;i++){auto& p=packets[i];if(!p.connected){m.primed=false;m.held=0;continue;}unsigned b=p.buttons&3;if(!m.primed){m.blocked=b;m.primed=true;}m.blocked&=b;b&=~m.blocked;
    if(p.x||p.y||b!=m.held||p.wheel){x=std::clamp(x+p.x,0.f,1919.f);y=std::clamp(y+p.y,0.f,1079.f);cursor=true;changed=true;point(int(x),int(y),(b&1)&&!(m.held&1));if((b&2)&&!(m.held&2))emit(0x2000);if(p.wheel)emit(p.wheel>0?0x10:0x40);}m.held=b;
   }
  }return changed;
 }
};
}
