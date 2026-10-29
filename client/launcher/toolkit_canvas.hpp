/* SPDX-License-Identifier: GPL-3.0-or-later
 * Adapt the existing model's 1080p layout to the upstream SDF kit.
 */
#pragma once
#include "toolkit_surface.hpp"
#include "palette.hpp"
#include "branding_logo.hpp"
#include "instance_icons.hpp"
#include "toolkit_effects.hpp"
#include <array>
#include <atomic>
#include <algorithm>
#include <cstdlib>
#include <cstring>
namespace prospero_ui {
inline Surface* surface=nullptr;
inline std::atomic<bool> healthy{true};
inline bool motion=false,reduced=false;
inline float dt=1.0f/60;
struct MenuControlMotion {hui::tween::Spring focus;hui::ui::Pulse press;int page=-1,x=0,y=0,w=0,h=0;std::uint64_t last_press=0;};
inline std::array<MenuControlMotion,32>* buttons=nullptr;
inline unsigned button_index=0;
inline std::array<std::uint32_t,prospero_icons::count> icon_textures{};
inline hui::gfx::Color themed(std::uint32_t rgb,float alpha=1){return hui::gfx::Color::rgb(prospero_palette::rgb(rgb),alpha);}
inline hui::gfx::Color color(std::uint32_t c){return {float(c&255)/255,float((c>>8)&255)/255,float((c>>16)&255)/255,float((c>>24)&255)/255};}
inline hui::ui::Theme theme(){auto t=hui::ui::default_theme();t.style=hui::ui::SurfaceStyle::glass;t.page=themed(0x081a13);t.surface=themed(0x08251d,0.78f);t.primary=themed(0xb6f2be);t.on_primary=themed(0x102c1b);t.secondary=themed(0x142b24);t.on_secondary=t.text=themed(0xeaf0e8);t.focus=themed(0xa9eab6);t.accent=themed(0x81e6af);t.radius=20;t.radius_card=28;t.shadow_blur=30;t.focus_width=2;t.omega=18;t.damping=0.86f;t.outline=themed(0xb3efd4,0.2f);return t;}
struct Canvas {
 void gradient(std::uint32_t,std::uint32_t){button_index=0;motion=false;}
 template<class F> void context(const F& fields,std::uint64_t press_time){
  auto num=[&](int i){return std::atoi(fields[i].data());};auto& e=*effects;reduced=std::strcmp(fields[30].data(),"ON")==0;e.feedback.clear();
  const int page=num(11),selected=num(9);e.page_changed=page!=e.page;
  if(e.page_changed){e.previous_page=e.page;e.page=page;e.age=0;e.entrance.start(reduced?0.0f:0.48f);e.grid.enter();if(page!=9)e.dialog.close(e.feedback);}
  e.age+=dt;e.clock+=reduced?0.0f:dt;e.entrance.update(dt);e.press.update(dt,10);
  if(press_time&&press_time!=e.last_press){e.last_press=press_time;e.press_page=page;e.press_row=num(15);if(!reduced)e.press.trigger();}
  int icon=page==1?num(24):num(18);if(page==0){int slot=selected-num(14);icon=slot>=0&&slot<8?num(34+slot*4):0;}
  auto accent=icon_color(icon);using hui::gfx::Color;auto green=themed(0x2dbe89);
  Color targets[]={themed(0x031512),themed(0x0b382f),hui::gfx::mix(themed(0x146850),accent,0.25f),hui::gfx::mix(green,accent,0.45f)};
  for(int i=0;i<4;i++){if(!e.ready||reduced)e.palette[i].snap(targets[i]);else e.palette[i].target(targets[i]);e.palette[i].update(dt,3.8f);surface->backdrop.colors[i]=e.palette[i].value();}
  int mode=num(75);if(mode<1||mode>10)mode=5;if(mode!=e.backdrop){surface->previous_backdrop=surface->backdrop;e.backdrop=mode;e.mode_age=0;}e.mode_age+=dt;surface->background_mix=reduced?1:hui::tween::smoothstep(e.mode_age/0.55f);surface->previous_backdrop.time=reduced?0:e.clock*0.32f;surface->backdrop.mode=static_cast<hui::gfx::BackdropMode>(mode);surface->backdrop.params[0]=0.35f;surface->backdrop.params[1]=0.5f;surface->backdrop.params[2]=0.35f;surface->backdrop.time=reduced?0:e.clock*0.32f;surface->glass=true;e.ready=true;
  e.selection=selected;e.model_row=num(15);
 }

 void begin_content(){auto& e=*effects;float t=reduced?1:hui::tween::quint_out(e.entrance.progress());surface->list.push_transform(1,960,540,0,reduced?0:28*(1-t));surface->list.push_opacity(reduced?1:hui::tween::cubic_out(e.entrance.progress()));}
 void end_content(){surface->list.pop_opacity();surface->list.pop_transform();
  if(effects->page!=9&&effects->dialog.visible()){effects->dialog.update(reduced?1:dt);hui::ui::Canvas c{surface->list,surface->fonts,surface->renderer.glass_texture(),effects->clock};effects->dialog.draw(c);}
  surface->list.gradient_rect({0,910,1920,170},0,themed(0x03100c,0),themed(0x03100c,0.92f));
 }

 void rounded(int x,int y,unsigned w,unsigned h,unsigned r,std::uint32_t c){
  auto col=color(c);hui::gfx::Rect rect{float(x),float(y),float(w),float(h)};
  if(w>=250&&h>=64&&col.g<0.45f){
   surface->list.shadow({rect.x,rect.y+12,rect.w,rect.h},float(r),32,themed(0x000000,0.28f));
   surface->list.glass(surface->renderer.glass_texture(),rect,float(r),col.with_alpha(0.74f));
   surface->list.bordered_rect(rect,float(r),themed(0,0),1.2f,themed(0xb6f2d4,0.15f));
  }else surface->list.rounded_rect(rect,float(r),col);
 }
 void rectangle(unsigned x,unsigned y,unsigned w,unsigned h,ps5::demo::Color c){rounded(int(x),int(y),w,h,0,static_cast<std::uint32_t>(c));}
 void disc(int,int,unsigned,std::uint32_t){}
 void label(int x,int y,std::string_view value,unsigned size,std::uint32_t c){auto& face=size>=48?surface->fonts.display:size>=30?surface->fonts.semibold:surface->fonts.regular;hui::ui::text(surface->list,face,value,float(x),float(y)+face.font->ascent(float(size)),float(size),color(c));}
 static unsigned text_width(std::string_view value,unsigned size){auto& face=size>=48?surface->fonts.display:size>=30?surface->fonts.semibold:surface->fonts.regular;return unsigned(face.measure(value,float(size))+0.5f);}
 void ring(int x,int y,int w,int h){auto t=theme();hui::ui::Painter p(surface->list,surface->fonts,t,surface->renderer.glass_texture());p.focus_ring({float(x),float(y),float(w),float(h)},22,reduced?1:0.9f+0.1f*hui::ui::breathe(effects->clock));}
 void toggle(int index,int x,int y,bool on,bool focus=false,bool checkbox=false){
  auto& value=effects->switches[index];value.target=on?1:0;if(reduced)value.snap(value.target);else value.update(dt,20);
  auto t=theme();hui::ui::Painter p(surface->list,surface->fonts,t,surface->renderer.glass_texture());hui::ui::Look look;look.focus=focus?1:0;
  if(checkbox)p.checkbox({float(x),float(y),40,40},value.value,look);else p.toggle({float(x),float(y),76,40},value.value,look);
 }
 void progress(int value){auto& bar=effects->progress;bar.style.theme=theme();bar.style.reduced_motion=reduced;bar.style.sheen=!reduced;bar.style.placement=hui::ui::LabelPlacement::none;bar.style.percent=false;bar.style.height=7;bar.style.mode=value>0?hui::ui::ProgressMode::determinate:hui::ui::ProgressMode::indeterminate;bar.set_bounds({72,979,1770,14});bar.set_value(float(value)/1000,reduced);bar.update(reduced?1:dt);hui::ui::Canvas c{surface->list,surface->fonts,surface->renderer.glass_texture(),effects->clock};bar.draw(c);}
 template<class F> void library(const F& fields,int slide){
  auto num=[&](int i){return std::atoi(fields[i].data());};auto& e=*effects;auto& grid=e.grid;
  int count=std::min(8,std::max(0,num(13)-num(14)));std::string key=fields[14].data();
  for(int i=0;i<count*4;i++)key+=std::string("|")+fields[32+i].data();
  auto t=theme();grid.style.theme=t;grid.style.reduced_motion=reduced;grid.style.columns=4;grid.style.cell_width=420;grid.style.cell_height=242;grid.style.gap_x=30;grid.style.gap_y=30;grid.style.padding=0;grid.style.scroll_thumb=false;grid.style.card.art_aspect=0;grid.style.card.text=hui::ui::CardText::over;grid.style.card.title_size=30;grid.style.card.subtitle_size=24;grid.style.card.text_inset=24;grid.style.card.badge_corner=hui::ui::CardCorner::top_right;grid.style.card.glow=true;grid.style.card.focus_scale=reduced?1:1.025f;grid.style.card.lift=reduced?0:7;grid.style.card.press_scale=reduced?0:0.025f;grid.style.entrance_step=reduced?0:0.05f;
  if(key!=e.items_key){std::vector<hui::ui::CardItem> items;for(int i=0;i<count;i++){int at=32+i*4;hui::ui::CardItem item;item.title=fields[at].data();item.subtitle=fields[at+1].data();item.badge=std::strcmp(fields[at+3].data(),"ADD")==0?"":fields[at+3].data();item.tag=num(at+2);item.accent=icon_color(item.tag);items.push_back(item);}grid.set_items(std::move(items));e.items_key=key;grid.enter();}
  if(grid.bounds().y!=342+slide||grid.bounds().w!=1770)grid.set_bounds({70,float(342+slide),1770,514});
  grid.art=[](hui::ui::Canvas& canvas,const hui::gfx::Rect& art,float radius,const hui::ui::CardItem& item,float focus){
   using hui::gfx::Color;if(item.tag<0){float x=art.x+art.w/2,y=art.y+art.h/2;canvas.list.rounded_rect({x-26,y-3,52,6},3,themed(0xb6f2be));canvas.list.rounded_rect({x-3,y-26,6,52},3,themed(0xb6f2be));return;}auto tint=icon_color(item.tag);canvas.list.gradient_rect(art,radius,hui::gfx::mix(themed(0x133e32),tint,0.22f),themed(0x071e19));
   canvas.list.glow({art.x+art.w-150,art.y+20,100,80},45,75,tint.with_alpha(0.12f+focus*0.12f));
   float x=art.x+26,y=art.y+22-(reduced?0:4*focus),size=98;
   if(item.tag>=0&&unsigned(item.tag)<icon_textures.size()){canvas.list.image(icon_textures[item.tag],{x,y,size,size},{0,0,1,1},themed(0xffffff),0);}
   else{canvas.list.shadow({x,y+9,size,size},20,18,themed(0,0.4f));canvas.list.gradient_rect({x,y,size,size},20,tint,hui::gfx::mix(tint,themed(0x193f2c),0.45f));
    for(int row=0;row<3;row++)for(int col=0;col<4;col++)canvas.list.rounded_rect({x+9+col*21,y+38+row*17,12,12},2,themed((row+col)%3==0?0xcaf4c1:0x183a2c,0.65f));}
  };
  int focus=std::clamp(num(9)-num(14),0,std::max(0,count-1));if(grid.focus()!=focus||e.page_changed)grid.set_focus(focus,reduced||e.page_changed);grid.set_active(std::strcmp(fields[28].data(),"TOP")!=0);grid.update(reduced?1:dt);hui::ui::Canvas c{surface->list,surface->fonts,surface->renderer.glass_texture(),e.clock};grid.draw(c);
 }
 void confirm(const char* name,int row){auto& e=*effects;auto& dialog=e.dialog;dialog.style.theme=theme();dialog.style.reduced_motion=reduced;dialog.style.width=1450;dialog.style.title_size=48;dialog.style.body_size=28;dialog.style.padding=60;dialog.style.centered=false;dialog.style.enter_scale=0.94f;dialog.style.enter_rise=34;dialog.style.frost=0.72f;dialog.style.button_height=76;
  if(e.page_changed||!dialog.is_open()){hui::ui::DialogContent content;content.title="Delete "+std::string(name)+"?";content.body="Permanently delete this instance, all of its worlds and its settings? This cannot be undone. Shared downloads are kept.";content.buttons={{"NO",hui::ui::ButtonKind::secondary,false},{"YES, DELETE",hui::ui::ButtonKind::secondary,true}};content.default_button=0;dialog.open(std::move(content),e.feedback);}
  dialog.set_focus(row);dialog.update(reduced?1:dt);hui::ui::Canvas c{surface->list,surface->fonts,surface->renderer.glass_texture(),e.clock};dialog.draw(c);
 }
 void instance_icon(int x,int y,int size,int kind){unsigned index=kind>=0&&unsigned(kind)<icon_textures.size()?unsigned(kind):0;surface->list.image(icon_textures[index],{float(x),float(y),float(size),float(size)},{0,0,1,1},themed(0xffffff),0);}
 void logo(int x,int y,int size){surface->list.image(surface->logo,{float(x),float(y),float(size),float(size)},{0,0,1,1},themed(0xffffff),0);}
 void control(int x,int y,int w,int h,bool active,bool press_live=false,bool positive=false){
  if(button_index>=buttons->size())return;auto& state=(*buttons)[button_index++];auto& e=*effects;
  if(state.page!=e.page||state.w!=w||state.h!=h){state=MenuControlMotion{};state.page=e.page;state.x=x;state.y=y;state.w=w;state.h=h;}
  state.focus.target=active?1.0f:0.0f;
  if(reduced){state.focus.snap(state.focus.target);state.press.value=0;}
  else{
   if(press_live&&active&&!e.page_changed&&e.last_press&&state.last_press!=e.last_press&&e.press_page==e.page&&e.press_row==e.model_row){state.press.trigger();state.last_press=e.last_press;}
   state.focus.update(dt,22);state.press.update(dt,10);
  }
  float focus=std::clamp(state.focus.value,0.0f,1.0f),press=reduced?0:state.press.value;float inset=2.0f*press;
  hui::gfx::Rect rect{float(x)+inset,float(y)+inset,float(w)-2*inset,float(h)-2*inset};
  auto fill=hui::gfx::mix((positive?hui::gfx::Color::rgb(0x477f4a):themed(0x142b24)),(positive?hui::gfx::Color::rgb(0x62a565):themed(0x1e3c30)),focus);
  fill=hui::gfx::mix(fill,themed(0x325a42),press*0.4f);
  surface->list.shadow({rect.x,rect.y+10,rect.w,rect.h},20,26,themed(0x000000,0.24f));
  surface->list.glass(surface->renderer.glass_texture(),rect,20,fill.with_alpha(0.78f));
  surface->list.bordered_rect(rect,20,positive?fill.with_alpha(0.96f):themed(0,0),1.2f,themed(0xb3efd4,0.13f+focus*0.14f));
  motion=motion||std::abs(state.focus.value-state.focus.target)>0.001f||press>0.001f;
 }
 void button(int x,int y,int w,int h,const char* text,bool active,bool primary,bool press=false){
  control(x,y,w,h,active,press,std::string_view(text)=="DONE");const float size=h<64?24:30;
  auto& face=surface->fonts.semibold;auto clipped=face.font->fit(text,size,float(w-98));
  const bool danger=std::string_view(text)=="DELETE INSTANCE"||std::string_view(text)=="UNINSTALL";
  hui::ui::text(surface->list,face,clipped,float(x+32),float(y)+(h-size)/2+face.font->ascent(size),size,themed(danger?0xf0b4ac:primary?0xc9f5cd:0xeaf0e8));
  label(x+w-48,y+int((h-size)/2),">",unsigned(size),0xa9eab6);
 }

};
inline bool open(const char* fonts){
 if(surface)return healthy;
 surface=new Surface;effects=new Effects;buttons=new std::array<MenuControlMotion,32>;healthy=surface->init(fonts);
 if(healthy){std::array<std::uint32_t,72*72> pixels{};for(unsigned i=0;i<pixels.size();i++)pixels[i]=prospero_menu::logo_pixels[i];surface->logo=surface->renderer.create_texture(72,72,reinterpret_cast<const std::uint8_t*>(pixels.data()));healthy=surface->logo!=0;}
 if(healthy)for(unsigned i=0;i<icon_textures.size();i++){icon_textures[i]=surface->renderer.create_texture(72,72,reinterpret_cast<const std::uint8_t*>(prospero_icons::pixels[i]));if(!icon_textures[i]){healthy=false;break;}}
 std::fprintf(stderr,"PS5_UI Vulkan init=%s stage=%s result=%d\n",healthy?"READY":"FAIL",surface->stage,int(surface->error));
 return healthy;
}
inline bool close(){if(!surface)return healthy;bool result=surface->close();if(result){delete buttons;buttons=nullptr;delete effects;effects=nullptr;delete surface;surface=nullptr;}return healthy&&result;}
}
