/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#ifndef PROSPERO_APP_VERSION
#define PROSPERO_APP_VERSION "Development"
#endif
#include "demo_renderer.hpp"
#include "palette.hpp"
#include "branding_logo.hpp"
#include "instance_icons.hpp"
#include "login_qr.hpp"
#include "navigation.hpp"
#include "haptics.hpp"
#include "fonts.hpp"
#ifdef PROSPERO_TOOLKIT
#include "toolkit_canvas.hpp"
#endif
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <atomic>
#include <pthread.h>
extern "C" int sceKernelUsleep(std::uint32_t);
extern "C" std::uint64_t sceKernelGetProcessTime();
namespace prospero_menu {
#ifdef PROSPERO_TOOLKIT
using prospero_ui::Canvas;
#else
using ps5::demo::Canvas;
#endif
inline std::uint32_t ink(std::uint32_t rgb){return prospero_palette::raw_ink(prospero_palette::rgb(rgb));}
// Text stays small; only the seven thumbnail slots need larger buffers.
// Inline aggregate storage preserves constructor-free startup and bounded stacks.
struct Fields {
 bool operator==(const Fields&)const noexcept=default;
 std::array<std::array<char,512>,98> text{};
 std::array<std::array<char,8192>,7> images{};
 template<class Char>struct Slot {Char* p;size_t length;Char* data()const noexcept{return p;}size_t size()const noexcept{return length;}Char& operator[](size_t i)const noexcept{return p[i];}};
 Slot<char> operator[](size_t i)noexcept {if(i>=96&&i<=102)return {images[i-96].data(),8192};return {text[i>=103?i-7:i].data(),512};}
 Slot<const char> operator[](size_t i)const noexcept {if(i>=96&&i<=102)return {images[i-96].data(),8192};return {text[i>=103?i-7:i].data(),512};}
};
// Only the native UI thread draws/reads the controller. JNI stays on the JVM
// startup thread. A bounded mailbox exchanges public UI text and button edges.
inline Fields fields{},published{};
inline pthread_mutex_t mailbox=PTHREAD_MUTEX_INITIALIZER;
inline pthread_t ui_thread{};
inline unsigned events[64]{},event_read=0,event_write=0;
inline std::atomic<bool> visible{false},online{false},exit_requested{false},display_done{false},display_ok{false};
inline int controller=-1;inline Haptics haptics;inline bool pad_connected=false;inline unsigned pad_generation=0;
inline unsigned updates=0;
inline Navigation navigation{};inline std::uint64_t pressed_at=0;
inline void publish(const Fields& values) noexcept {
 pthread_mutex_lock(&mailbox);published=values;pthread_mutex_unlock(&mailbox);
}
inline unsigned take_input() noexcept {
 pthread_mutex_lock(&mailbox);unsigned value=0;if(event_read!=event_write){value=events[event_read%64];++event_read;}pthread_mutex_unlock(&mailbox);return value;
}
inline void discard_input() noexcept {
 pthread_mutex_lock(&mailbox);event_read=event_write;pthread_mutex_unlock(&mailbox);
}
inline void push_input(unsigned value) noexcept {
 if(!value)return;pthread_mutex_lock(&mailbox);
 if(event_write-event_read<64)events[event_write++%64]=value;
 pthread_mutex_unlock(&mailbox);
}
inline void label(Canvas& c,int x,int y,const char* text,unsigned size=24,std::uint32_t rgb=0xeaf0e8){c.label(x,y,text,size,ink(rgb));}
// Font-independent controller shapes also work in the fallback renderer.
inline void control_glyph(Canvas& c,int x,int y,std::string_view key,unsigned size,std::uint32_t rgb){
 int d=int(size)+4;auto dot=[&](int px,int py){c.rectangle(x+px,y+py,2,2,static_cast<ps5::demo::Color>(ink(rgb)));};
 auto line=[&](int ax,int ay,int bx,int by){int dx=std::abs(bx-ax),dy=-std::abs(by-ay),sx=ax<bx?1:-1,sy=ay<by?1:-1,err=dx+dy;for(;;){dot(ax,ay);if(ax==bx&&ay==by)break;int e=2*err;if(e>=dy){err+=dy;ax+=sx;}if(e<=dx){err+=dx;ay+=sy;}}};
 if(key=="X"){line(5,5,d-5,d-5);line(d-5,5,5,d-5);}
 else if(key=="TRIANGLE"){line(d/2,3,3,d-3);line(3,d-3,d-3,d-3);line(d-3,d-3,d/2,3);}
 else if(key=="SQUARE"){line(4,4,d-4,4);line(d-4,4,d-4,d-4);line(d-4,d-4,4,d-4);line(4,d-4,4,4);}
 else if(key=="CIRCLE"){int r=d/2-3;for(int yy=-r;yy<=r;yy++)for(int xx=-r;xx<=r;xx++){int a=xx*xx+yy*yy;if(a<=r*r&&a>=(r-2)*(r-2))dot(d/2+xx,d/2+yy);}}
 else {unsigned w=Canvas::text_width(key,size-4)+14;c.rounded(x,y,w,d,6,ink(0x355c48));c.label(x+7,y+4,key,size-4,ink(rgb));}
}
inline void control_label(Canvas& c,int x,int y,std::string_view text,unsigned size=24,std::uint32_t rgb=0xa9c6b2){
 const std::string_view keys[]={"TRIANGLE","CIRCLE","SQUARE","OPTIONS","L1","R1","L2","R2","L3","R3","X"};
 while(!text.empty()){
  std::string_view match;for(auto k:keys)if(text.starts_with(k)&&(text.size()==k.size()||text[k.size()]==' '||text[k.size()]=='/')){match=k;break;}
  if(!match.empty()){control_glyph(c,x,y,match,size,rgb);x+=int(match.size()>2&&match!="TRIANGLE"&&match!="CIRCLE"&&match!="SQUARE"?Canvas::text_width(match,size-4)+22:size+13);text.remove_prefix(match.size());}
  else {size_t n=1;while(n<text.size()&&text[n-1]!=' ')n++;auto part=text.substr(0,n);c.label(x,y,part,size,ink(rgb));x+=int(Canvas::text_width(part,size));text.remove_prefix(n);}
 }
}
inline void wrap(Canvas& c,int x,int y,std::string_view text,unsigned width,int lines=3){
 while(!text.empty()&&lines-->0){std::size_t n=text.size();while(n>0&&Canvas::text_width(text.substr(0,n),24)>width)--n;if(!n)break;
  if(n<text.size()){auto space=text.substr(0,n).find_last_of(' ');if(space!=std::string_view::npos&&space>0)n=space;}
  c.label(x,y,text.substr(0,n),24,ink(0xaac0b6));text.remove_prefix(n);while(!text.empty()&&text.front()==' ')text.remove_prefix(1);y+=34;
 }
}
inline void card(Canvas& c,int x,int y,unsigned w,unsigned h,bool focus=false){c.rounded(x,y,w,h,24,ink(focus?0xa9eab6:0x294138));c.rounded(x+2,y+2,w-4,h-4,22,ink(0x13271f));}
inline void title(Canvas& c,int x,int y,const char* text,unsigned size=30,unsigned width=1000,std::uint32_t color=0xeaf0e8){
 std::string_view value(text);if(Canvas::text_width(value,size)>width){while(!value.empty()&&Canvas::text_width(value,size)+Canvas::text_width("...",size)>width)value.remove_suffix(1);c.label(x,y,value,size,ink(color));c.label(x+Canvas::text_width(value,size),y,"...",size,ink(color));}else label(c,x,y,text,size,color);
}
struct TextOrigin {int x,y;};
inline TextOrigin centered_text(int x,int y,int width,int height,std::string_view text,unsigned size){
#ifdef PROSPERO_TOOLKIT
 const auto& font=*(size>=30?prospero_ui::surface->fonts.semibold.font:prospero_ui::surface->fonts.regular.font);
 std::vector<hui::gfx::GlyphQuad> glyphs; font.layout(text,0,0,float(size),hui::gfx::Align::left,glyphs);
 float left=0,right=0,top=0,bottom=0;bool first=true;
 for(const auto& g:glyphs){if(first){left=g.x0;right=g.x1;top=g.y0;bottom=g.y1;first=false;}else{left=std::min(left,g.x0);right=std::max(right,g.x1);top=std::min(top,g.y0);bottom=std::max(bottom,g.y1);}}
 return {int(std::lround(x+(width-(right-left))/2-left)),int(std::lround(y+(height-(bottom-top))/2-top-font.ascent(float(size))))};
#else
 const auto& font=ui_font::get(size);int pen=0,left=0,right=0,top=0,bottom=0;bool inked=false;
 for(unsigned char ch:text){const auto& glyph=font.glyphs[(ch>=32&&ch<=126?ch:'?')-32];if(glyph.w>0&&glyph.h>0){int l=pen+glyph.x,r=l+glyph.w,t=glyph.y,b=t+glyph.h;if(!inked){left=l;right=r;top=t;bottom=b;inked=true;}else{if(l<left)left=l;if(r>right)right=r;if(t<top)top=t;if(b>bottom)bottom=b;}}pen+=glyph.advance;}
 return {x+(width-(right-left))/2-left,y+(height-(bottom-top))/2-top};
#endif
}
inline int number(int index){return std::atoi(fields[index].data());}
inline void block(Canvas& c,int x,int y,int size,int kind){
#ifdef PROSPERO_TOOLKIT
 c.instance_icon(x,y,size,kind);return;
#endif
 unsigned index=kind>=0&&unsigned(kind)<prospero_icons::count?unsigned(kind):0;
 for(int yy=0;yy<72;yy++)for(int xx=0;xx<72;xx++){auto color=prospero_icons::pixels[index][yy*72+xx];if(color>>24)c.rectangle(x+xx*size/72,y+yy*size/72,(size+71)/72,(size+71)/72,static_cast<ps5::demo::Color>(color));}
}
inline void content_icon(Canvas& c,int x,int y,int size,const char* pixels){
 if(std::strlen(pixels)!=6144){c.rounded(x,y,size,size,8,ink(0x294038));c.rounded(x+size/5,y+size/5,size*3/5,size*3/5,5,ink(0x50675c));return;}
 auto hex=[](char a)->int{return a>='0'&&a<='9'?a-'0':a>='a'&&a<='f'?a-'a'+10:0;};
 for(int yy=0;yy<32;yy++)for(int xx=0;xx<32;xx++){const char* p=pixels+(yy*32+xx)*6;unsigned color=0;for(int n=0;n<6;n++)color=(color<<4)|hex(p[n]);c.rectangle(x+xx*size/32,y+yy*size/32,(size+31)/32,(size+31)/32,static_cast<ps5::demo::Color>(ink(color)));}
}
struct Focus {float x=0,y=0,w=0,h=0;bool initialized=false;};
inline Focus focus{};inline std::uint64_t transition_start=0,last_draw_time=0,component_motion_until=0;inline bool animating=false;
inline std::uint64_t now_ms(){return sceKernelGetProcessTime()/1000;}
inline void selection(Canvas& c,int x,int y,int w,int h){
 const bool reduced=std::strcmp(fields[30].data(),"ON")==0;
 if(!focus.initialized||reduced){focus={float(x),float(y),float(w),float(h),true};}
 #ifdef PROSPERO_TOOLKIT
 static hui::tween::Spring springs[4];float targets[]={float(x),float(y),float(w),float(h)};
 float* values[]={&focus.x,&focus.y,&focus.w,&focus.h};
 for(int i=0;i<4;i++){if(reduced||*values[i]==targets[i])springs[i].snap(targets[i]);springs[i].target=targets[i];springs[i].update(prospero_ui::dt,22);*values[i]=springs[i].value;}
#else
 const float rate=reduced?1.0f:0.34f;focus.x+=(x-focus.x)*rate;focus.y+=(y-focus.y)*rate;focus.w+=(w-focus.w)*rate;focus.h+=(h-focus.h)*rate;
#endif
 auto distance=[](float a,float b){return a>b?a-b:b-a;};if(distance(focus.x,float(x))+distance(focus.y,float(y))+distance(focus.w,float(w))+distance(focus.h,float(h))>1.0f)animating=true;
 else focus={float(x),float(y),float(w),float(h),true};
 const bool press=std::strcmp(fields[30].data(),"ON")!=0&&pressed_at&&now_ms()-pressed_at<110;
 if(press)animating=true;
 const int inset=press?2:0;
#ifdef PROSPERO_TOOLKIT
 c.ring(int(focus.x)+inset,int(focus.y)+inset,int(focus.w)-inset*2,int(focus.h)-inset*2);
#else
 c.rounded(int(focus.x)-4+inset,int(focus.y)-4+inset,unsigned(focus.w)+8-inset*2,unsigned(focus.h)+8-inset*2,22,ink(press?0xe0ffe4:0xa9eab6));
#endif
}
inline void action(Canvas& c,int x,int y,int w,const char* text,bool active,bool primary=false){
#ifdef PROSPERO_TOOLKIT
 const bool press=active&&pressed_at&&now_ms()-pressed_at<110;
 if(active)selection(c,x,y,w,76);c.button(x,y,w,76,text,active,primary,press);if(press)animating=true;
 // Continue refreshing while the component's own focus and press springs settle.
 if(now_ms()<component_motion_until)animating=true;
 return;
#endif
 if(active)selection(c,x,y,w,76);c.rounded(x,y,w,76,18,ink(primary?0xb6f2be:0x244438));label(c,x+28,y+22,text,30,primary?0x102c1b:0xeaf0e8);
}
inline void row_control(Canvas& c,int y,const char* name,const char* value,bool active,bool editable=true,int height=96){
 if(active)selection(c,760,y,1080,height);
#ifdef PROSPERO_TOOLKIT
 c.control(760,y,1080,height,active,std::strcmp(fields[30].data(),"ON")!=0&&pressed_at&&now_ms()-pressed_at<110);
#else
 c.rounded(760,y,1080,height,20,ink(active?0x1e3c30:0x142b24));
#endif
 label(c,792,y+(height-96)/2+16,name,24,0x8fae9d);title(c,792,y+(height-96)/2+47,value,30,960);if(editable){
#ifdef PROSPERO_TOOLKIT
 bool toggle=std::strcmp(name,"REDUCED MOTION")==0||std::strcmp(name,"SHOW SNAPSHOTS")==0||std::strcmp(name,"STARTUP NOTICE")==0;
 if(toggle)c.toggle(std::strcmp(name,"REDUCED MOTION")==0?0:std::strcmp(name,"SHOW SNAPSHOTS")==0?1:2,1728,y+(height-40)/2,std::strcmp(value,"ON")==0,active);
 else
#endif
 label(c,1779,y+43,">",30,0xa9eab6);
 }
}
inline void player_head(Canvas& c,int x,int y,int size){
 // Center the unchanged face in its own theme-colored tile, with no outline.
 const int padding=std::max(10,size/6);
 c.rounded(x-padding,y-padding,size+2*padding,size+2*padding,padding,ink(0x729b83));
 const char* hex=fields[80].data();if(std::strlen(hex)!=384){c.rounded(x,y,size,size,6,ink(0x568b72));label(c,x+size/4,y+size/5,"?",unsigned(size/2),0xeaf0e8);return;}
 for(int py=0;py<8;py++)for(int px=0;px<8;px++){char rgb[7]{};std::memcpy(rgb,hex+(py*8+px)*6,6);c.rectangle(x+px*size/8,y+py*size/8,(size+7)/8,(size+7)/8,static_cast<ps5::demo::Color>(prospero_palette::raw_ink(unsigned(std::strtoul(rgb,nullptr,16)))));}
}
inline void login_qr(Canvas& c,int x,int y,int scale){c.rounded(x,y,prospero_qr::size*scale,prospero_qr::size*scale,0,ink(0xffffff));for(int py=0;py<prospero_qr::size;py++)for(int px=0;px<prospero_qr::size;px++)if(prospero_qr::modules[py*prospero_qr::size+px]=='1')c.rectangle(x+px*scale,y+py*scale,scale,scale,static_cast<ps5::demo::Color>(ink(0x000000)));}
inline void compose(Canvas& c) noexcept {
 animating=false;last_draw_time=now_ms();prospero_palette::selected=std::clamp(number(104),0,5);
#ifdef PROSPERO_TOOLKIT
 c.context(fields,pressed_at);
#endif
 c.gradient(ink(0x0b1815),ink(0x08120f));c.disc(1760,850,380,ink(0x0c211a));
 const int page=number(11),row=number(15),selected=number(9),tab=number(12);const bool top=std::strcmp(fields[28].data(),"TOP")==0;(void)selected;
 float elapsed=float(now_ms()-transition_start)/180.0f;if(elapsed<0)elapsed=0;if(elapsed>1)elapsed=1;
 const int slide=std::strcmp(fields[30].data(),"ON")==0?0:int(16*(1-elapsed)*(1-elapsed));if(slide>0)animating=true;
 c.rounded(40,32,1840,108,24,ink(0x10221c));block(c,66,53,64,0);label(c,149,66,"ProsperoCraft",30);label(c,405,72,"NATIVE JAVA 25",24,0x718d7b);
 const bool signed_in=fields[81][0]&&std::strcmp(fields[5].data(),"Not signed in")!=0;
 const char* tabs[]={"Instances","Settings",signed_in?fields[81].data():"Sign in"};const int tx[]={865,1245,1555},tw[]={350,280,280};
 for(int i=0;i<3;i++){
  const bool current=tab==i,account=i==2&&signed_in;
  const int name_width=tw[i]-(account?68:0);
  if(current&&top)selection(c,tx[i],52,tw[i],68);
  c.rounded(tx[i],52,name_width,68,18,ink(current?0x53885c:0x14251e));
  auto text=centered_text(tx[i],52,name_width,68,tabs[i],i==2?24:30);
  if(account)text.x=std::max(tx[i]+16,text.x);
  title(c,text.x,text.y,tabs[i],i==2?24:30,account?name_width-32:tw[i]-45,current?0xc7f4cf:0xb0c4b5);
  if(current)c.rounded(tx[i]+24,124,tw[i]-48,6,3,ink(0xd0ff9a));
  if(account)player_head(c,tx[i]+tw[i]-51,66,40);
 }
#ifdef PROSPERO_TOOLKIT
 c.begin_content();
#endif
 if(page==0){
  label(c,70,192+slide,"Instances",64);
  [[maybe_unused]] const int count=number(13),start=number(14);
#ifdef PROSPERO_TOOLKIT
   c.library(fields,slide);
#else
   for(int i=0;i<8&&start+i<count;i++){int x=70+(i%4)*450,y=342+(i/4)*272+slide,at=32+i*4;bool active=!top&&selected==start+i;if(active)selection(c,x,y,420,242);c.rounded(x,y,420,242,22,ink(active?0x1f3a2b:0x13291f));if(std::strcmp(fields[at+3].data(),"ADD")==0){c.rounded(x+184,y+118,52,6,3,ink(0xb6f2be));c.rounded(x+207,y+95,6,52,3,ink(0xb6f2be));}else{block(c,x+27,y+26,88,number(at+2));title(c,x+26,y+137,fields[at].data(),30,365);label(c,x+27,y+187,fields[at+1].data(),24,0x92b6a0);label(c,x+235,y+187,fields[at+3].data(),24,0xa7d4ae);}}
#endif
 }else if(page==1||page==5){
  label(c,70,185+slide,page==1?"A world of your own.":"Make it yours.",64);label(c,75,269+slide,page==1?"One instance. Its own settings, worlds and memories.":"Your worlds stay right where they are.",24,0x91ad9b);
  c.rounded(70,338+slide,620,548,28,ink(0x10221c));block(c,275,402+slide,204,page==1?number(24):number(18));title(c,105,690+slide,page==1?fields[22].data():fields[16].data(),42,540);label(c,108,761+slide,"JAVA EDITION / INSTANCE",24,0x8db69a);
  if(page==1){row_control(c,320+slide,"VERSION",fields[23].data(),row==0);row_control(c,430+slide,"LOADER",fields[82].data(),row==1,true);row_control(c,540+slide,"NAME",fields[22].data(),row==2);row_control(c,650+slide,"ICON","Choose instance icon",row==3);action(c,760,774+slide,1080,"CREATE & DOWNLOAD",row==4,true);wrap(c,790,884+slide,fields[70].data(),1000,1);}
  else{row_control(c,310+slide,"INSTANCE NAME",fields[16].data(),row==0);row_control(c,420+slide,"INSTANCE ICON","Choose instance icon",row==1);action(c,760,535+slide,520,"MODS",row==2);action(c,1320,535+slide,520,"SHADERS",row==3);action(c,760,630+slide,520,"RESOURCE PACKS",row==4);action(c,1320,630+slide,520,"DUPLICATE INSTANCE",row==7);action(c,760,725+slide,520,"DONE",row==5,true);action(c,1320,725+slide,520,"DELETE INSTANCE",row==6);}
 }else if(page==14){
  title(c,70,225,fields[82].data(),64,1750);content_icon(c,85,365,96,fields[96].data());title(c,220,385,fields[85].data(),36,1550);wrap(c,85,515,fields[70].data(),1640,3);
  action(c,760,740,520,"CANCEL",row==0,true);action(c,1320,740,520,"UNINSTALL",row==1);
 }else if(page==13){
  title(c,70,185,fields[82].data(),64,1700);title(c,75,275,fields[70].data(),24,1750,0x91ad9b);int first=number(84);for(int n=0;n<7&&first+n<23;n++){int y=340+n*78;action(c,70,y,1770,fields[85+n].data(),row==first+n);}
 }else if(page==12){
  title(c,70,185,fields[82].data(),64,1500);title(c,75,270,fields[70].data(),24,1770,0x91ad9b);
  action(c,70,325,1010,fields[92].data(),row==0,true);char queue[80];std::snprintf(queue,sizeof(queue),"DOWNLOAD ALL (%s)",fields[91].data());action(c,1120,325,720,queue,row==1,true);
  action(c,70,435,330,"PREVIOUS",row==2);action(c,430,435,330,"NEXT",row==3);char count[100];std::snprintf(count,sizeof(count),"%d / %s results",number(84),fields[83].data());if(std::strcmp(fields[82].data(),"Shaders")==0)action(c,800,435,470,fields[95].data(),row==11);else label(c,800,461,count,24,0x91ad9b);action(c,1320,435,520,std::strcmp(fields[103].data(),"INSTALLED")==0?"BROWSE":"INSTALLED",row==10);
  for(int i=0;i<number(93)&&i<4;i++){int y=535+i*92;if(row==i+4)selection(c,70,y,1770,86);
#ifdef PROSPERO_TOOLKIT
   c.control(70,y,1770,86,row==i+4,std::strcmp(fields[30].data(),"ON")!=0&&pressed_at&&now_ms()-pressed_at<110);
#else
   c.rounded(70,y,1770,86,12,ink(row==i+4?0x1e3c30:0x10251d));
#endif
   bool installed=std::strncmp(fields[85+i].data(),"[I]",3)==0,checked=installed||std::strncmp(fields[85+i].data(),"[X]",3)==0;
#ifdef PROSPERO_TOOLKIT
   c.toggle(4+i,82,y+23,checked,row==i+4,true);
#else
   c.rounded(82,y+23,40,40,8,ink(0x8fae9d));c.rounded(85,y+26,34,34,5,ink(0x142e23));if(checked){for(int n=0;n<9;n++)c.rectangle(90+n,y+42+n,5,5,static_cast<ps5::demo::Color>(ink(0xb6f2be)));for(int n=0;n<18;n++)c.rectangle(98+n,y+50-n,5,5,static_cast<ps5::demo::Color>(ink(0xb6f2be)));}
#endif
   content_icon(c,139,y+7,72,fields[96+i].data());const char* text=fields[85+i].data();if(std::strlen(text)>=4)text+=4;bool local_view=std::strcmp(fields[103].data(),"INSTALLED")==0;title(c,235,y+31,text,24,local_view?1210:installed?1350:1570);
   if(local_view){
#ifdef PROSPERO_TOOLKIT
    if(row==20+i)selection(c,1500,y+18,320,51);c.button(1500,y+18,320,51,"UNINSTALL",row==20+i,false,std::strcmp(fields[30].data(),"ON")!=0&&pressed_at&&now_ms()-pressed_at<110);
#else
    if(row==20+i)selection(c,1500,y+18,320,51);c.rounded(1500,y+18,320,51,12,ink(0x284538));label(c,1570,y+31,"UNINSTALL",24);
#endif
   }else if(installed)label(c,1640,y+31,"INSTALLED",18,0xa9eab6);}

 }else if(page==2){
  label(c,70,185+slide,"Settle in.",64);label(c,75,270+slide,"A few thoughtful defaults. You're in control.",24,0x91ad9b);
  c.rounded(70,340+slide,620,548,28,ink(0x10221c));label(c,112,391+slide,"YOUR SETUP",24,0x8fbb9b);label(c,112,459+slide,"Native Java 25",42);wrap(c,114,545+slide,"Choose your game window size. The pointer uses logical coordinates; the native display reports its actual framebuffer size. Video and audio options stay with each instance.",520,5);label(c,114,714+slide,"SQUARE  Change background",24,0xa9eab6);title(c,114,753+slide,fields[76][0]?fields[76].data():"Waves",30,510);label(c,114,804+slide,std::strcmp(fields[79].data(),"OFF")==0?"TRIANGLE  Vibration: OFF":"TRIANGLE  Vibration: ON",24,0xa9eab6);title(c,114,851+slide,fields[67].data(),18,510,0x83a58d);
  const char* themes[]={"Forest","Ocean","Amethyst","Rose","Amber","Graphite"};
  const char* names[]={"GAME RESOLUTION","PARALLEL DOWNLOADS","REDUCED MOTION","SHOW SNAPSHOTS","STARTUP NOTICE","INPUT & CONTROLLER KEYBINDS","COLOR THEME"};
  const char* values[]={fields[25].data(),fields[26].data(),fields[30].data(),fields[27].data(),fields[68].data(),"Configure controls",themes[prospero_palette::selected]};
  for(int i=0;i<7;i++)row_control(c,300+i*96+slide,names[i],values[i],row==i,true,86);
 }else if(page==3){
  label(c,70,185+slide,"Your account. Your adventure.",64);label(c,75,270+slide,"Sign in on your phone. Your password stays with Microsoft.",24,0x91ad9b);
  c.rounded(70,340+slide,1000,548,28,ink(0x10221c));label(c,116,391+slide,"MICROSOFT ACCOUNT",24,0x8fbb9b);title(c,116,447+slide,fields[5].data(),42,750);if(signed_in)player_head(c,929,389+slide,96);
  if(fields[3][0]){login_qr(c,747,514+slide,7);label(c,116,539+slide,"ENTER THIS CODE",24,0x8eaf9a);label(c,115,584+slide,fields[3].data(),64,0xc9f5cd);wrap(c,117,699+slide,"https://www.microsoft.com/link",600,2);}
  else wrap(c,117,547+slide,"Sign in with your Microsoft account to play Minecraft Java. Your saved account reconnects on future launches. You can sign out on this console at any time.",850,5);
  action(c,1140,366+slide,700,signed_in?"SIGN OUT":"SIGN IN WITH MICROSOFT",row==0,true);wrap(c,1167,634+slide,fields[2].data(),620,6);
 }else if(page==4){
  label(c,70,185+slide,std::strcmp(fields[69].data(),"PENDING")==0?"Coming soon.":"Ready when you are.",64);c.rounded(70,330+slide,620,560,28,ink(0x10221c));block(c,245,385+slide,270,number(18));title(c,109,721+slide,fields[16].data(),42,540);label(c,112,794+slide,fields[17].data(),24,0x97bea3);
  title(c,762,352+slide,fields[16].data(),64,1060);label(c,768,441+slide,"JAVA EDITION",24,0x94b69f);
  const char* actions[]={fields[6].data(),"INSTANCE SETTINGS","REPAIR DOWNLOAD","PLAY OFFLINE"};
  int y=505;for(int i=0;i<4;i++){if(i==3&&std::strcmp(fields[71].data(),"OFFLINE")!=0)continue;action(c,760,y+slide,1080,actions[i],row==i,i==0&&std::strcmp(fields[69].data(),"PENDING")!=0);y+=100;}
  if(y<920)wrap(c,790,y+8+slide,fields[65].data(),1000,1);
 }else if(page==10){
  label(c,250,185,fields[82].data(),48);c.rounded(240,265,1440,650,28,ink(0x10251d));int first=number(84),count=number(83);for(int i=0;i<8&&first+i<count;i++){int yy=285+i*72;if(first+i==row)selection(c,265,yy,1390,66);if(number(93)==1||number(93)==2)block(c,285,yy+5,54,first+i);title(c,(number(93)==1||number(93)==2)?365:290,yy+17,fields[85+i].data(),24,1230);}label(c,270,937,"D-PAD  Choose     LEFT / RIGHT  Page     X  Confirm     CIRCLE  Cancel",24,0xa9eab6);
 }else if(page==9){
#ifdef PROSPERO_TOOLKIT
  c.confirm(fields[16].data(),row);
#else
  label(c,70,185+slide,"Delete this instance?",64);c.rounded(70,330+slide,1770,548,28,ink(0x10221c));
  title(c,116,390+slide,fields[16].data(),48,1600);wrap(c,118,490+slide,"Permanently delete this instance, including every world and its settings? This cannot be undone. Shared downloads are kept.",1560,3);
  action(c,116,710+slide,780,"NO",row==0,true);action(c,970,710+slide,780,"YES, DELETE",row==1,std::strcmp(fields[64].data(),"BUSY")!=0);
#endif
 }else if(page==8||page==11){
  const bool essentials=page==11;int section=essentials?0:number(74);
  label(c,70,190,essentials?"Ready to play":"Controller guide",64);
  const char* sections[]={"MOVEMENT & ACTIONS","INVENTORY & MENUS","TEXT KEYBOARD","WORLD SHORTCUTS","TOUCHPAD SHORTCUTS"};
  label(c,78,291,essentials?"THE ESSENTIALS":sections[std::clamp(section,0,4)],30,0xa9eab6);
  const char* basic[]={"Left stick   Move", "Right stick   Look", "X   Jump", "R2   Mine / attack", "L2   Use / place", "OPTIONS   Pause"};
  const char* world[]={"Left stick   Move / L3   Sprint", "Right stick   Look / OPTIONS   Pause", "X   Jump / CIRCLE   Sneak", "R2   Mine or attack / L2   Use or place", "L1 / R1   Change hotbar slot", "TRIANGLE   Inventory"};
  const char* menus[]={"Right stick   Move pointer", "X / R2   Left click / L2   Right click", "R3   Middle click", "SQUARE + click   Quick move", "L1 / R1   Scroll / CIRCLE   Back", "Cursor only   Select / L3   Text keyboard"};
  const char* typing[]={"D-PAD / left stick   Choose a key", "X   Type / R1   Space", "L1 / TRIANGLE   Delete", "R2   Change case / L2   Symbols", "OPTIONS   Enter and close", "CIRCLE / L3   Close / touchpad + R3   Toggle"};
  const char* shortcuts[]={"SQUARE   Swap hands", "D-PAD DOWN   Drop item", "D-PAD UP   Player list", "D-PAD LEFT / RIGHT   Hotbar slot 1 / 9", "R3   Change camera", "Hold touchpad + R3   Pick block"};
  const char* touchpad[]={"Hold touchpad + TRIANGLE   Chat", "Hold touchpad + SQUARE   Command", "Hold touchpad + X   Enter / CIRCLE   Backspace", "Hold touchpad + LEFT   HUD / RIGHT   Screenshot", "Hold touchpad + UP   Debug / DOWN   Advancements", "Hold touchpad + OPTIONS   Fullscreen"};
  const char** lines=essentials?basic:section==0?world:section==1?menus:section==2?typing:section==3?shortcuts:touchpad;
  for(int i=0;i<6;i++){int x=78+(i/3)*900,y=382+(i%3)*122;c.rounded(x-4,y-18,850,96,20,ink(0x10251d));control_label(c,x+26,y+12,lines[i],essentials?30:24);}
  if(essentials){
   control_label(c,78,760,"L3 Text keyboard in menus     OPTIONS Full controls",24,0x94b69f);
   action(c,78,850,330,std::strcmp(fields[95].data(),"READY")==0?"OK":"PREPARING...",row==1,true);
   if(row==0)selection(c,470,850,610,76);c.rounded(470,850,610,76,18,ink(0x142e23));
#ifdef PROSPERO_TOOLKIT
   c.toggle(3,490,868,std::strcmp(fields[94].data(),"OFF")==0,row==0,true);
#else
   label(c,490,871,std::strcmp(fields[94].data(),"OFF")==0?"[X]":"[ ]",30);
#endif
   label(c,555,872,"Don't show again",30);
  }else{char counter[48];std::snprintf(counter,sizeof(counter),"%d / 5",section+1);label(c,1740,850,counter,30,0x94b69f);control_label(c,78,850,"LEFT / RIGHT  Change section",30,0x94b69f);}
 }else if(page==7){
  c.rounded(170,190,1580,745,32,ink(0x142e23));
  label(c,235,240,"Welcome to ProsperoCraft",64);
  wrap(c,240,347,"Your Minecraft Java library, right here on your console. Create an instance, choose an icon and make yourself at home.",1390,3);
  wrap(c,240,468,"Sign in with your Microsoft account, download 26.3, then choose PLAY. Your account, worlds and verified downloads are saved for future launches.",1390,3);
  wrap(c,240,570,"Use the shoulder buttons to explore Instances, Settings and your account. Press OPTIONS for the controller guide. All 26.x releases and snapshots are available to download; versions beyond the current 26.3 support are coming soon.",1390,5);
  action(c,240,773,330,"OK",row==1,true);
  if(row==0)selection(c,680,773,430,76);
  c.rounded(680,773,430,76,18,ink(0x142e23));
#ifdef PROSPERO_TOOLKIT
  c.toggle(3,704,791,std::strcmp(fields[68].data(),"ON")==0,row==0,true);
#else
  c.rounded(704,791,40,40,8,ink(row==0?0xe0ffe4:0x8fae9d));
  c.rounded(707,794,34,34,5,ink(0x142e23));
  if(std::strcmp(fields[68].data(),"ON")==0){
   // A two-stroke tick at TV scale; independent of font glyph support.
   for(int i=0;i<9;++i)c.rectangle(712+i,810+i,5,5,static_cast<ps5::demo::Color>(ink(0xb6f2be)));
   for(int i=0;i<18;++i)c.rectangle(720+i,818-i,5,5,static_cast<ps5::demo::Color>(ink(0xb6f2be)));
  }
#endif
  label(c,766,795,"Show next time",30);
 }else if(page==6){
  label(c,70,185,"Enter text.",64);c.rounded(70,300,1770,116,22,ink(0x183c2a));title(c,103,330,fields[29].data(),42,1650);
  const char* chars=std::strcmp(fields[66].data(),"LOWER")==0?"1234567890qwertyuiopasdfghjkl_zxcvbnm .-":"1234567890QWERTYUIOPASDFGHJKL_ZXCVBNM .-";int chosen=number(31);
  for(int i=0;i<40;i++){int x=80+(i%10)*176,y=465+(i/10)*91;if(i==chosen)selection(c,x,y,152,73);c.rounded(x,y,152,73,16,ink(i==chosen?0x356647:0x172e24));char letter[2]={chars[i],0};label(c,x+61,y+21,letter,30);}
  label(c,100,873,"X  Add     TRIANGLE  Backspace     L2  Case     R2  Space     OPTIONS  Clear     SQUARE  Done",24,0x8daf99);
 }
#ifdef PROSPERO_TOOLKIT
 c.end_content();
#endif
 if(std::strcmp(fields[64].data(),"BUSY")==0){
  if(page==12&&fields[102][0])content_icon(c,78,924,46,fields[102].data());if(page!=3)title(c,page==12&&fields[102][0]?144:78,942,fields[2].data(),24,1230,0xaac8b2);label(c,1450,942,fields[21].data(),24,0xaac8b2);
#ifdef PROSPERO_TOOLKIT
  c.progress(number(20));
#else
  c.rounded(72,982,1770,5,2,ink(0x233c2c));if(number(20)>0)c.rounded(72,982,unsigned(1770*number(20)/1000),5,2,ink(0xa9eab6));
#endif
 }else if(page!=3)title(c,78,949,fields[2].data(),24,1760,0x83a58d);
 control_label(c,76,1020,fields[7].data(),20,0x7d9f89);label(c,1650,1020,PROSPERO_APP_VERSION,24,0x7d9f89);
}
#ifdef PROSPERO_TOOLKIT
inline std::uint64_t toolkit_frame_time=0;
inline void draw(ps5::demo::Canvas& output) noexcept {
 if(prospero_ui::healthy){
  auto time=now_ms();prospero_ui::dt=toolkit_frame_time?std::clamp(float(time-toolkit_frame_time)/1000.0f,0.001f,0.05f):1.0f/60;toolkit_frame_time=time;
  prospero_ui::reduced=std::strcmp(fields[30].data(),"ON")==0;
  prospero_ui::surface->list.clear();Canvas canvas;compose(canvas);
  prospero_ui::healthy=prospero_ui::surface->render();
  if(prospero_ui::healthy){auto* pixels=static_cast<const std::uint32_t*>(prospero_ui::surface->pixels);
   prospero_ui::healthy=output.blit_rgba({pixels,1920*1080});
   return;
  }
 }
 output.clear(ps5::demo::Color::background);output.label(100,350,"Vulkan launcher unavailable. Game launch is blocked.",36,ink(0xeaf0e8));
 output.label(100,430,"Keep open for logs, then close and reinstall the preserved086 candidate.",24,ink(0xa9eab6));
}
#else
inline void draw(ps5::demo::Canvas& output) noexcept {compose(output);}
#endif
inline bool update() noexcept {
 // The second update follows the initial submit/WaitVblank in run_ui_until.
 if(++updates>=2)visible.store(true,std::memory_order_release);
 unsigned pressed=0;PadSample batch[64]{};const int count=scePadRead(controller,batch,64);
 const auto current_time=now_ms();bool connection_changed=false;
 if(count<0||count>64){pad_connected=false;navigation.clear();discard_input();}
 else for(int i=0;i<count;++i){
  pad_connected=batch[i].connected&&!(batch[i].buttons&0x80000000u);
  if(pad_generation!=batch[i].connection_generation){connection_changed=true;haptics.control(false,current_time);pad_generation=batch[i].connection_generation;}
  if(!pad_connected){pressed=0;discard_input();}
  pressed|=navigation.sample(batch[i].buttons,batch[i].lx,batch[i].ly,batch[i].connected,current_time);
 }
 pressed|=navigation.repeat(current_time);
 if(pressed&0x4000)pressed_at=current_time;
 push_input(pressed);
 bool changed=false;
 if(!online.load(std::memory_order_acquire)){
  if(pressed&0x400){std::snprintf(fields[12].data(),512,"%d",(number(12)+2)%3);std::snprintf(fields[28].data(),512,"TOP");changed=true;}
  if(pressed&0x800){std::snprintf(fields[12].data(),512,"%d",(number(12)+1)%3);std::snprintf(fields[28].data(),512,"TOP");changed=true;}
 }else{
  pthread_mutex_lock(&mailbox);changed=fields!=published;
  if(changed){if(std::strcmp(fields[11].data(),published[11].data())!=0){transition_start=now_ms();focus.initialized=false;}fields=published;}
  pthread_mutex_unlock(&mailbox);
 }
 bool vibration=online.load(std::memory_order_acquire)&&pad_connected&&!connection_changed&&current_time-navigation.last_sample<=250&&std::strcmp(fields[79].data(),"ON")==0&&!exit_requested.load();
 haptics.control(vibration,current_time);haptics.observe(unsigned(number(77)),fields[78].data(),vibration,current_time);
 if(changed||(pressed&0x4000)){component_motion_until=now_ms()+700;return true;}
#ifdef PROSPERO_TOOLKIT
 if(!prospero_ui::reduced&&prospero_ui::healthy)return now_ms()-last_draw_time>=33;
#endif
 return animating&&now_ms()-last_draw_time>=16;

}
inline bool stop() noexcept{bool value=exit_requested.load(std::memory_order_acquire);if(value)haptics.control(false,now_ms());return value;}
inline void* ui_main(void*) noexcept {
 pad_connected=false;pad_generation=0;(void)haptics.start(controller);
#ifdef PROSPERO_TOOLKIT
 extern void initialize_toolkit_graphics();initialize_toolkit_graphics();
 #ifndef PROSPERO_TOOLKIT_FONT_DIR
#define PROSPERO_TOOLKIT_FONT_DIR "/app0/assets/java25/launcher-toolkit/assets/fonts"
#endif
 prospero_ui::open(PROSPERO_TOOLKIT_FONT_DIR);
#endif
 const bool closed=ps5::demo::run_ui_until(draw,update,stop,"");
#ifdef PROSPERO_TOOLKIT
 const bool gpu_closed=prospero_ui::close();
#else
 const bool gpu_closed=true;
#endif
 haptics.close();scePadClose(controller);controller=-1;
 std::fprintf(stderr,"PS5_UI handoff display_closed=%d gpu_closed=%d\n",int(closed),int(gpu_closed));
 display_ok.store(closed&&gpu_closed,std::memory_order_release);display_done.store(true,std::memory_order_release);return nullptr;
}
inline bool start_frontend() noexcept {
 visible=false;online=false;exit_requested=false;display_done=false;display_ok=false;
 updates=0;navigation.clear();pressed_at=0;focus={};transition_start=now_ms();animating=false;event_read=event_write=0;fields={};published={};
 const char* boot[]={"Instances","","Opening your library...","","","Not signed in","PLAY DEMO","L1 / R1  Top bar     X  Select","PREPARING","0","WAIT","0"};
 for(int i=0;i<12;++i)std::snprintf(fields[i].data(),512,"%s",boot[i]);
 std::int32_t user=-1;if(sceUserServiceGetInitialUser(&user)<0)return false;controller=scePadOpen(user,0,0,nullptr);if(controller<0)return false;
 pthread_attr_t attrs;
 if(pthread_attr_init(&attrs)!=0){scePadClose(controller);controller=-1;return false;}
 int created=pthread_attr_setstacksize(&attrs,2*1024*1024);
 if(created==0)created=pthread_create(&ui_thread,&attrs,ui_main,nullptr);
 pthread_attr_destroy(&attrs);
 if(created!=0){scePadClose(controller);controller=-1;return false;}
 while(!visible.load(std::memory_order_acquire)&&!display_done.load(std::memory_order_acquire))(void)sceKernelUsleep(1000);
 return visible.load(std::memory_order_acquire)&&!display_done.load(std::memory_order_acquire)
#ifdef PROSPERO_TOOLKIT
 &&prospero_ui::healthy
#endif
 ;
}
inline void show_failure() noexcept {
 Fields text{};
 // Do not touch UI-owned fields: supply a complete independent failure state.
 const char* boot[]={"Your next world.","Starts right here.","Account services could not start. Keep app open for startup logs.","","","Not signed in","STARTUP FAILED","Close and reopen after collecting the startup report","STARTUP FAILED","0","WAIT","0"};
 for(int i=0;i<12;++i)std::snprintf(text[i].data(),512,"%s",boot[i]);publish(text);online.store(true,std::memory_order_release);
}
inline jboolean menu(JNIEnv* env,jclass owner){
 const jmethodID tick=env->GetStaticMethodID(owner,"launcherTick","(I)[Ljava/lang/String;");if(!tick)return false;
 bool launch=false,failed=false;
 while(!launch&&!failed&&!display_done.load(std::memory_order_acquire)){
  auto array=static_cast<jobjectArray>(env->CallStaticObjectMethod(owner,tick,static_cast<jint>(take_input())));
  if(env->ExceptionCheck()||!array){failed=true;break;}
  Fields next{};
  if(env->GetArrayLength(array)!=105){env->DeleteLocalRef(array);failed=true;break;}
  for(int i=0;i<105;++i){auto value=static_cast<jstring>(env->GetObjectArrayElement(array,i));if(!value){failed=true;break;}const char* bytes=env->GetStringUTFChars(value,nullptr);if(!bytes){env->DeleteLocalRef(value);failed=true;break;}std::snprintf(next[i].data(),next[i].size(),"%s",bytes);env->ReleaseStringUTFChars(value,bytes);env->DeleteLocalRef(value);}
  env->DeleteLocalRef(array);if(failed)break;
  publish(next);online.store(true,std::memory_order_release);
  launch=std::strcmp(next[10].data(),"LAUNCH")==0;
  if(!launch)(void)sceKernelUsleep(16000);
 }
 exit_requested.store(true,std::memory_order_release);
 while(!display_done.load(std::memory_order_acquire))(void)sceKernelUsleep(1000);
 pthread_join(ui_thread,nullptr);
 return display_ok.load(std::memory_order_acquire)&&launch&&!failed&&!env->ExceptionCheck();
}
}
