/* SPDX-License-Identifier: GPL-3.0-or-later
 * Physical PS5 USB/Bluetooth HID -> normal SDL keyboard/mouse events.
 * Text translation currently uses US ASCII. Scancodes preserve non-text keys.
 */
#pragma once
#include "ps5_hid.h"
static struct {
 bool initialized;Uint64 retry;
 struct {int handle;SDL_KeyboardID id;bool held[256],blocked[256],primed;unsigned trace_count,delivery_mask;bool trace_read,trace_connected,trace_intercepted,trace_keys;int repeat;Uint64 repeat_at;unsigned leds;} keys[4];
 struct {int handle;SDL_MouseID id;unsigned buttons,blocked;bool primed;} mice[4];
 float x,y;bool position;
} ps5_usb;
/* Record routing outcome once per result/port, never the key or typed text. */
static void PS5_USBKey(Uint64 now,int index,int key,bool down){
 bool posted=SDL_SendKeyboardKey(now,ps5_usb.keys[index].id,0,(SDL_Scancode)key,down);
 unsigned bit=posted?1u:2u;
 if(!(ps5_usb.keys[index].delivery_mask&bit)){
  fprintf(stderr,"PS5_HID keyboard index=%d key_event_posted=%d\n",index,posted);
  ps5_usb.keys[index].delivery_mask|=bit;
 }
}
static char PS5_USBChar(unsigned key,bool shift,bool caps){
 if(key>=4&&key<=29)return (char)((shift!=caps?'A':'a')+key-4);
 if(key>=89&&key<=97)return (char)('1'+key-89);if(key==98)return '0';if(key==99)return '.';
 if(key>=30&&key<=39)return (shift?"!@#$%^&*()":"1234567890")[key-30];
 const unsigned keys[]={44,45,46,47,48,49,51,52,53,54,55,56};const char normal[]=" -=[]\\;'`,./",upper[]=" _+{}|:\"~<>?";
 for(unsigned n=0;n<sizeof(keys)/sizeof(keys[0]);n++)if(key==keys[n])return shift?upper[n]:normal[n];return 0;
}
static void PS5_USBText(SDL_Window *window,int index,int key){
 if(!SDL_TextInputActive(window))return;
 bool *held=ps5_usb.keys[index].held;if(held[224]||held[226]||held[227]||held[228]||held[230]||held[231])return;
 char text[2]={PS5_USBChar((unsigned)key,held[225]||held[229],(ps5_usb.keys[index].leds&2)!=0),0};if(text[0])SDL_SendKeyboardText(text);
}
static void PS5_USBRelease(Uint64 now,SDL_Window *window){
 for(int n=0;n<4;n++){
  for(int key=0;key<256;key++)if(ps5_usb.keys[n].held[key]){PS5_USBKey(now,n,key,false);ps5_usb.keys[n].held[key]=false;}
  for(int b=0;b<5;b++)if(ps5_usb.mice[n].buttons&(1u<<b))SDL_SendMouseButton(now,window,ps5_usb.mice[n].id,(Uint8)(b==1?SDL_BUTTON_RIGHT:b==2?SDL_BUTTON_MIDDLE:b+1),false);
  ps5_usb.mice[n].buttons=0;ps5_usb.mice[n].primed=false;ps5_usb.keys[n].primed=false;ps5_usb.keys[n].repeat=0;
 }if(ps5_usb.position)(void)client_wsi_cursor(false,0,0,0);ps5_usb.position=false;
}
static void PS5_USBClose(SDL_Window *window){
 if(!ps5_usb.initialized)return;PS5_USBRelease(SDL_GetTicksNS(),window);
 for(int n=0;n<4;n++){if(ps5_usb.keys[n].handle>=0)prospero_hid_close(0,ps5_usb.keys[n].handle);if(ps5_usb.mice[n].handle>=0)prospero_hid_close(1,ps5_usb.mice[n].handle);if(ps5_usb.keys[n].id)SDL_RemoveKeyboard(ps5_usb.keys[n].id);if(ps5_usb.mice[n].id)SDL_RemoveMouse(ps5_usb.mice[n].id);}
 SDL_zero(ps5_usb);
}
static void PS5_PumpUSBInput(SDL_Window *window){
 Uint64 now=SDL_GetTicksNS();
 if(!ps5_usb.initialized){for(int n=0;n<4;n++){ps5_usb.keys[n].handle=-1;ps5_usb.mice[n].handle=-1;}ps5_usb.initialized=true;}
 if(ps5_usb.position&&ps5_temp.cursor_ready){ps5_usb.x=ps5_temp.cursor_x;ps5_usb.y=ps5_temp.cursor_y;}
 if(!window||SDL_GetKeyboardFocus()!=window){PS5_USBRelease(now,window);return;}
 if(now>=ps5_usb.retry){
  ps5_usb.retry=now+2000000000ull;
  for(int n=0;n<4;n++){
   if(ps5_usb.keys[n].handle<0){ps5_usb.keys[n].handle=prospero_hid_open(0,n);if(ps5_usb.keys[n].handle>=0){fprintf(stderr,"PS5_INPUT keyboard index%d handle%d\n",n,ps5_usb.keys[n].handle);}}
   if(ps5_usb.mice[n].handle<0){ps5_usb.mice[n].handle=prospero_hid_open(1,n);if(ps5_usb.mice[n].handle>=0){fprintf(stderr,"PS5_INPUT mouse index%d handle%d\n",n,ps5_usb.mice[n].handle);}}
  }
 }
 for(int n=0;n<4;n++){
  struct prospero_keyboard_packet packets[16];int count=ps5_usb.keys[n].handle<0?0:prospero_hid_read(0,ps5_usb.keys[n].handle,packets,16);
  if(ps5_usb.keys[n].handle>=0&&!ps5_usb.keys[n].trace_read){fprintf(stderr,"PS5_HID keyboard index=%d first_read=%d\n",n,count);ps5_usb.keys[n].trace_read=true;}
  if(count<0&&ps5_usb.keys[n].trace_count<12){fprintf(stderr,"PS5_HID keyboard index=%d read_error=0x%x\n",n,(unsigned)count);ps5_usb.keys[n].trace_count++;}
  if(count<0){prospero_hid_close(0,ps5_usb.keys[n].handle);ps5_usb.keys[n].handle=-1;count=1;SDL_zero(packets[0]);}
  if(count>16)count=16;
  for(int i=0;i<count;i++){
   const struct prospero_keyboard_packet *p=&packets[i];bool held[256]={0};if(p->connected&&!ps5_usb.keys[n].id){ps5_usb.keys[n].id=SDL_GetNextObjectID();SDL_AddKeyboard(ps5_usb.keys[n].id,"PS5 physical keyboard");}
   bool has_keys=false;unsigned valid_keys=0;
   for(int k=0;k<16;k++){has_keys|=p->keys[k]!=0;if(p->keys[k]>=4&&p->keys[k]<256)valid_keys++;}
   if(ps5_usb.keys[n].trace_count<12&&(ps5_usb.keys[n].trace_count==0||ps5_usb.keys[n].trace_connected!=(p->connected!=0)||ps5_usb.keys[n].trace_intercepted!=(p->intercepted!=0)||ps5_usb.keys[n].trace_keys!=has_keys)){
    fprintf(stderr,"PS5_HID keyboard index=%d connected=%d intercepted=%d length=%d keys_present=%d valid_slots=%u\n",n,p->connected!=0,p->intercepted!=0,p->length,has_keys,valid_keys);
    ps5_usb.keys[n].trace_count++;
   }
   ps5_usb.keys[n].trace_connected=p->connected!=0;ps5_usb.keys[n].trace_intercepted=p->intercepted!=0;ps5_usb.keys[n].trace_keys=has_keys;
   if(p->connected&&!p->intercepted){for(int bit=0;bit<8;bit++)held[224+bit]=(p->modifiers&(1u<<bit))!=0;for(int k=0;k<16;k++)if(p->keys[k]>=4&&p->keys[k]<256)held[p->keys[k]]=true;ps5_usb.keys[n].leds=p->leds;}
   if(!ps5_usb.keys[n].primed){for(int k=0;k<256;k++)ps5_usb.keys[n].blocked[k]=held[k];ps5_usb.keys[n].primed=true;}
   for(int k=0;k<256;k++){ps5_usb.keys[n].blocked[k]&=held[k];held[k]&=!ps5_usb.keys[n].blocked[k];}
   /* Modifiers precede printable events and text. */
   for(int k=224;k<232;k++)if(held[k]!=ps5_usb.keys[n].held[k])PS5_USBKey(now,n,k,held[k]);
   for(int k=224;k<232;k++)ps5_usb.keys[n].held[k]=held[k];
   if(!p->connected||p->intercepted)ps5_usb.keys[n].primed=false;
   for(int k=4;k<224;k++)if(held[k]!=ps5_usb.keys[n].held[k]){PS5_USBKey(now,n,k,held[k]);ps5_usb.keys[n].held[k]=held[k];if(held[k]){PS5_USBText(window,n,k);ps5_usb.keys[n].repeat=k;ps5_usb.keys[n].repeat_at=now+450000000ull;}}
   if(!p->connected&&ps5_usb.keys[n].id){SDL_RemoveKeyboard(ps5_usb.keys[n].id);ps5_usb.keys[n].id=0;ps5_usb.keys[n].repeat=0;}
  }
  int key=ps5_usb.keys[n].repeat;if(key&&ps5_usb.keys[n].held[key]&&now>=ps5_usb.keys[n].repeat_at&&(SDL_TextInputActive(window)||key==42||key>=79&&key<=82)){
   PS5_USBKey(now,n,key,true);PS5_USBText(window,n,key);ps5_usb.keys[n].repeat_at=now+35000000ull;
  }
  struct prospero_mouse_packet mice[32];count=ps5_usb.mice[n].handle<0?0:prospero_hid_read(1,ps5_usb.mice[n].handle,mice,32);
  if(count<0){prospero_hid_close(1,ps5_usb.mice[n].handle);ps5_usb.mice[n].handle=-1;count=1;SDL_zero(mice[0]);}
  if(count>32)count=32;
  for(int i=0;i<count;i++){
   const struct prospero_mouse_packet *p=&mice[i];if(p->connected&&!ps5_usb.mice[n].id){ps5_usb.mice[n].id=SDL_GetNextObjectID();SDL_AddMouse(ps5_usb.mice[n].id,"PS5 physical mouse");}bool usable=p->connected&&!(p->buttons&0x80000000u);unsigned buttons=usable?(p->buttons&31):0;
   if(!ps5_usb.mice[n].primed){ps5_usb.mice[n].blocked=buttons;ps5_usb.mice[n].primed=true;}ps5_usb.mice[n].blocked&=buttons;buttons&=~ps5_usb.mice[n].blocked;
   for(int b=0;b<5;b++)if((buttons^ps5_usb.mice[n].buttons)&(1u<<b))SDL_SendMouseButton(now,window,ps5_usb.mice[n].id,(Uint8)(b==1?SDL_BUTTON_RIGHT:b==2?SDL_BUTTON_MIDDLE:b+1),(buttons&(1u<<b))!=0);ps5_usb.mice[n].buttons=buttons;
   if(!usable){ps5_usb.mice[n].primed=false;if(!p->connected&&ps5_usb.mice[n].id){SDL_RemoveMouse(ps5_usb.mice[n].id);ps5_usb.mice[n].id=0;}continue;}
   if(p->wheel||p->tilt)SDL_SendMouseWheel(now,window,ps5_usb.mice[n].id,(float)p->tilt,(float)p->wheel,SDL_MOUSEWHEEL_NORMAL);
   if(SDL_GetWindowRelativeMouseMode(window)){if(p->x||p->y)SDL_SendMouseMotion(now,window,ps5_usb.mice[n].id,true,(float)p->x,(float)p->y);ps5_usb.position=false;}
   else {int w=0,h=0;SDL_GetWindowSize(window,&w,&h);if(w>1&&h>1){if(!ps5_usb.position){ps5_usb.x=w*0.5f;ps5_usb.y=h*0.5f;ps5_usb.position=true;}ps5_usb.x=SDL_clamp(ps5_usb.x+p->x,0.0f,(float)w-1);ps5_usb.y=SDL_clamp(ps5_usb.y+p->y,0.0f,(float)h-1);if(p->x||p->y)SDL_SendMouseMotion(now,window,ps5_usb.mice[n].id,false,ps5_usb.x,ps5_usb.y);ps5_temp.cursor_x=ps5_usb.x;ps5_temp.cursor_y=ps5_usb.y;ps5_temp.cursor_ready=true;}}
  }
 }
 /* Visibility can change while SDL dispatches the previous packet (Controlify
  * mode switch). Redraw from retained position even when no new HID data arrives. */
 if(SDL_GetWindowRelativeMouseMode(window)||!SDL_CursorVisible()||ps5_temp.typing)
  (void)client_wsi_cursor(false,0,0,0);
 else if(ps5_usb.position){int w=0,h=0;SDL_GetWindowSize(window,&w,&h);if(w>1&&h>1)(void)client_wsi_cursor(true,ps5_usb.x/(w-1),ps5_usb.y/(h-1),0);}
}
