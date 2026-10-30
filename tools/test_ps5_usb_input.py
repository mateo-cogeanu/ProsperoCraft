#!/usr/bin/env python3
"""Actual USB SDL adapter with OS packet/SDL event boundaries under sanitizers."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];w=ROOT/'build/usb105-test';w.mkdir(exist_ok=True)
source=r'''
#include <SDL3/SDL.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include "ps5_hid.h"
static SDL_Window *win=(SDL_Window*)(uintptr_t)1,*focus;
static Uint64 tick=1;static bool captured,textactive;static int keyboard_count,mouse_count,removed,events,wheels,motions,texts,closes;static float mx,my;static char typed[10];
static bool keys[256],buttons[6];
static struct {float cursor_x,cursor_y;bool cursor_ready,typing;}ps5_temp;
static struct prospero_keyboard_packet keypack[16];static int keycount;
static struct prospero_mouse_packet mousepack[32];static int mousecount;
Uint64 SDL_GetTicksNS(void){return tick;}
SDL_Window* SDL_GetKeyboardFocus(void){return focus;}
bool SDL_GetWindowRelativeMouseMode(SDL_Window*w){return captured;}
bool SDL_TextInputActive(SDL_Window*w){return textactive;}
bool SDL_CursorVisible(void){return true;}
Uint32 SDL_GetNextObjectID(void){static Uint32 n;return ++n;}
void SDL_AddKeyboard(SDL_KeyboardID id,const char*name){keyboard_count++;}
void SDL_AddMouse(SDL_MouseID id,const char*name){mouse_count++;}
void SDL_RemoveKeyboard(SDL_KeyboardID id){assert(id);removed++;}
void SDL_RemoveMouse(SDL_MouseID id){assert(id);removed++;}
bool SDL_SendKeyboardKey(Uint64 t,SDL_KeyboardID id,int raw,SDL_Scancode key,bool down){assert(id&&key<256);keys[key]=down;events++;return true;}
void SDL_SendMouseButton(Uint64 t,SDL_Window*w,SDL_MouseID id,Uint8 button,bool down){assert(id&&button>=1&&button<=5);buttons[button]=down;events++;}
void SDL_SendMouseMotion(Uint64 t,SDL_Window*w,SDL_MouseID id,bool relative,float x,float y){assert(id&&relative==captured);mx=x;my=y;motions++;}
void SDL_SendMouseWheel(Uint64 t,SDL_Window*w,SDL_MouseID id,float x,float y,SDL_MouseWheelDirection d){assert(id&&y==2);wheels++;}
void SDL_SendKeyboardText(const char*s){texts++;snprintf(typed,sizeof(typed),"%s",s);}
bool SDL_GetWindowSize(SDL_Window*w,int*x,int*y){*x=1920;*y=1080;return true;}
void SDL_Log(const char*f,...){(void)f;}
int client_wsi_cursor(bool show,float x,float y,int c){assert(x>=0&&x<=1&&y>=0&&y<=1);return 0;}
void prospero_hid_preload(void){}
int prospero_hid_open(int mouse,int index){return index==0?(mouse?20:10):-1;}
int prospero_hid_read(int mouse,int handle,void*p,int n){if(mouse){int count=mousecount;if(count>0)memcpy(p,mousepack,(size_t)count*sizeof(mousepack[0]));mousecount=0;return count;}int count=keycount;if(count>0)memcpy(p,keypack,(size_t)count*sizeof(keypack[0]));keycount=0;return count;}
void prospero_hid_close(int mouse,int handle){assert(handle==10||handle==20);closes++;}
static void PS5_TracePhysicalInput(unsigned source){assert(source==1||source==2);}
#include "ps5_usb_input.h"
static void pump(void){tick+=16000000;PS5_PumpUSBInput(win);}
static void key(unsigned code,unsigned modifiers){memset(keypack,0,sizeof(keypack));keypack[0].connected=1;keypack[0].keys[0]=(uint16_t)code;keypack[0].modifiers=modifiers;keycount=1;}
static void mouse(unsigned held,int x,int y){memset(mousepack,0,sizeof(mousepack));mousepack[0].connected=1;mousepack[0].buttons=held;mousepack[0].x=x;mousepack[0].y=y;mousecount=1;}
int main(void){
 focus=win;key(0,0);mouse(0,0,0);pump();assert(keyboard_count==1&&mouse_count==1&&!events);
 key(4,2);textactive=true;pump();assert(keys[4]&&keys[225]&&texts==1&&!strcmp(typed,"A"));key(0,0);pump();assert(!keys[4]&&!keys[225]);
 key(5,0);keypack[1]=keypack[0];keypack[1].keys[0]=0;keycount=2;int old=events;pump();assert(events==old+2&&!keys[5]);
 key(6,0);keypack[0].leds=2;pump();assert(!strcmp(typed,"C"));key(0,0);pump();
 captured=true;mouse(3,12,-5);pump();assert(buttons[SDL_BUTTON_LEFT]&&buttons[SDL_BUTTON_RIGHT]&&mx==12&&my==-5);mouse(0,0,0);mousepack[0].wheel=2;pump();assert(!buttons[1]&&!buttons[3]&&wheels==1);
 captured=false;mouse(1,100,50);mousepack[1]=mousepack[0];mousepack[1].buttons=0;mousecount=2;old=events;pump();assert(events==old+2&&!buttons[1]&&mx>=0&&mx<1920&&my>=0&&my<1080);
 key(26,0);mouse(1,0,0);pump();assert(keys[26]&&buttons[1]);focus=NULL;pump();assert(!keys[26]&&!buttons[1]);
 focus=win;key(26,0);mouse(1,0,0);pump();assert(!keys[26]&&!buttons[1]);key(0,0);mouse(0,0,0);pump();key(26,0);pump();assert(keys[26]);
 key(0,0);keypack[0].intercepted=1;pump();assert(!keys[26]);key(26,0);pump();assert(!keys[26]);key(0,0);pump();
 key(7,0);pump();keycount=-1;pump();assert(!keys[7]&&closes==1);tick+=3000000000ull;key(0,0);pump();
 for(int i=0;i<1000;i++){key(4,0);pump();key(0,0);pump();}assert(ps5_usb.keys[0].trace_count<=12&&ps5_usb.keys[0].delivery_mask<=3);
 PS5_USBClose(win);assert(closes==3&&removed>=2);
 puts("PASS actual USB packet adapter: device discovery,modifiers/US text/caps,short taps,mouse buttons/relative and menu motion/wheel,focus loss/held-input rearm/interception/read failure/close under ASan+UBSan;PS5 hardware pending");
}
'''
(w/'test.c').write_text(source)
subprocess.run(['clang','-std=c11','-O1','-g','-fsanitize=address,undefined','-I'+str(ROOT/'.tools/sdl3-src/include'),'-I'+str(ROOT/'client/ports/sdl'),str(w/'test.c'),'-o',str(w/'test')],check=True)
subprocess.run([str(w/'test')],check=True,timeout=30)
