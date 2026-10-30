#!/usr/bin/env python3
"""Actual bounded handoff trace: read-only SDL state, throttle and saturation."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <SDL3/SDL.h>
#include <assert.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
static Uint64 ticks;static int lines,reads;static bool visible=true,relative;
static int trace(const char*fmt,...){char text[512];va_list ap;va_start(ap,fmt);int n=vsnprintf(text,sizeof text,fmt,ap);va_end(ap);if(strchr(text,'\n'))lines++;return n;}
#define fprintf(file,...) trace(__VA_ARGS__)
Uint64 SDL_GetTicksNS(void){return ticks;}
bool SDL_CursorVisible(void){return visible;}
bool SDL_GetWindowRelativeMouseMode(SDL_Window*w){assert(w);return relative;}
SDL_Gamepad*SDL_GetGamepadFromID(SDL_JoystickID id){return id==1?(void*)2:NULL;}
bool SDL_GetGamepadButton(SDL_Gamepad*p,SDL_GamepadButton b){assert(p==(void*)2);reads++;return b==SDL_GAMEPAD_BUTTON_SOUTH;}
Sint16 SDL_GetGamepadAxis(SDL_Gamepad*p,SDL_GamepadAxis a){assert(p==(void*)2);reads++;return a<4?0:32767;}
#include "ps5_input_handoff.h"
int main(void){SDL_Window*w=(void*)1;PS5_TraceInputHandoff(w);assert(!reads&&!lines);
 PS5_TracePhysicalInput(1);PS5_TracePhysicalInput(2);PS5_TraceInputHandoff(w);assert(lines==1&&!ps5_handoff_pending);
 int before=reads;PS5_TracePhysicalInput(1);for(int i=0;i<1000;i++)PS5_TraceInputHandoff(w);assert(lines==1&&reads==before&&ps5_handoff_pending==1);
 ticks=1000000000ull;visible=false;relative=true;PS5_TraceInputHandoff(w);assert(lines==2);
 for(int i=0;i<1000;i++){ticks+=1000000000ull;PS5_TracePhysicalInput(3);PS5_TraceInputHandoff(i%2?w:NULL);}
 assert(lines==16&&ps5_handoff_budget==16);before=reads;PS5_TracePhysicalInput(1);PS5_TraceInputHandoff(w);assert(reads==before);
 puts("PASS actual handoff trace:idle silence,coalescedsources,1secondthrottle,16snapshotcap,nullfocus,realSDLgettercontracts,noinput/modewrites;ASan/UBSan");}
'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'test.c').write_text(code);exe=w/'test'
 subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-I'+str(r/'.tools/sdl3-src/include'),'-I'+str(r/'client/ports/sdl'),str(w/'test.c'),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
