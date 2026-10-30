#!/usr/bin/env python3
"""Run both real input adapters in video-pump order; check Controlify handoff."""
from pathlib import Path
import ast,subprocess,tempfile,shutil
r=Path(__file__).resolve().parents[1]
tree=ast.parse((r/'tools/test_ps5_usb_input.py').read_text());fixture=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='source'for t in n.targets))
fixture=fixture.replace('static struct {float cursor_x,cursor_y;bool cursor_ready,typing;}ps5_temp;','static bool fallback=true,owned,visible=true,cursor_shown;static int hides,shows;')
fixture=fixture.replace('bool SDL_CursorVisible(void){return true;}','bool SDL_CursorVisible(void){return visible;}')
fixture=fixture.replace('int client_wsi_cursor(bool show,float x,float y,int c){assert(x>=0&&x<=1&&y>=0&&y<=1);return 0;}','int client_wsi_cursor(bool show,float x,float y,int c){assert(x>=0&&x<=1&&y>=0&&y<=1);cursor_shown=show;if(show)shows++;else hides++;return 0;}')
fixture=fixture.replace('#include "ps5_usb_input.h"',r'''
#include "platform.h"
const char*SDL_GetHint(const char*n){return NULL;}
bool SDL_GetHintBoolean(const char*n,bool b){return fallback;}
SDL_InitFlags SDL_WasInit(SDL_InitFlags flags){return owned?SDL_INIT_GAMEPAD:0;}
SDL_Gamepad*SDL_GetGamepadFromID(SDL_JoystickID id){return owned&&id==1?(void*)2:NULL;}
bool pad_open(void){return true;}
void pad_poll(struct pad*p){memset(p,0,sizeof(*p));}
uint32_t pad_players(void){return 1;}
int pad_readings(const struct pad_reading**out){static struct pad_reading p={.connected=true,.left_x=128,.left_y=128,.right_x=128,.right_y=128};*out=&p;return 1;}
int client_wsi_keyboard(bool s,int k,int l,int y,const char*p){return 0;}
#include "ps5_temporary_input.h"
#include "ps5_usb_input.h"
''')
fixture=fixture.replace('tick+=16000000;PS5_PumpUSBInput(win);','tick+=16000000;PS5_PumpTemporaryInput(win);PS5_PumpUSBInput(win);')
fixture=fixture[:fixture.index('int main(void)')]+r'''
int main(void){
 focus=win;key(0,0);mouse(0,0,0);pump();pump();
 owned=true;mouse(0,12,2);pump();assert(cursor_shown);
 int after=hides;for(int i=0;i<100;i++){mouse(0,0,0);pump();assert(cursor_shown);}
 assert(hides==after); /* No per-frame hide from inactive fallback. */
 visible=false;mouse(0,1,0);pump();assert(!cursor_shown); /* Respect Controlify hide. */
 visible=true;pump();assert(cursor_shown); /* show immediately without another packet */
 captured=true;pump();assert(!cursor_shown);captured=false;mouse(0,1,0);pump();assert(cursor_shown);
 mouse(1,0,0);pump();assert(buttons[SDL_BUTTON_LEFT]);mouse(0,0,0);pump();assert(!buttons[SDL_BUTTON_LEFT]);
 int before=events;for(int i=0;i<100;i++)pump();assert(events==before); /* no artificial input/mode churn */
 owned=false;pump();pump();owned=true;pump();after=hides;pump();assert(hides==after);
 focus=NULL;pump();focus=win;mouse(0,1,0);pump();assert(cursor_shown);
 PS5_USBClose(win);
 puts("PASS both real PS5 adapters:one-time Controlify handoff,100stationary reports/no hide-show churn,SDL cursor visibility/relative mode,physical clicks,idle silence,reacquisition/focus;ASan/UBSan");
}
'''
with tempfile.TemporaryDirectory(prefix='ps5-cursor-')as d:
 w=Path(d);port=w/'sdl';port.mkdir();(w/'test.c').write_text(fixture)
 for p in (r/'client/ports/sdl').iterdir():
  if p.is_file():shutil.copy2(p,port/p.name)
 # Headers refer to the shared source-only keyboard layout.
 (w/'mesa').mkdir();shutil.copy2(r/'client/ports/mesa/keyboard_layout.h',w/'mesa/keyboard_layout.h')
 common=['clang','-std=c11','-O1','-g','-fsanitize=address,undefined','-I'+str(r/'.tools/sdl3-src/include'),'-I'+str(port),str(w/'test.c')]
 original=subprocess.check_output(['git','-C',str(r),'show','01.000.117:client/ports/sdl/ps5_temporary_input.h'],text=True)
 current=(port/'ps5_temporary_input.h').read_text();(port/'ps5_temporary_input.h').write_text(original)
 subprocess.run([*common,'-o',str(w/'old')],check=True)
 result=subprocess.run([str(w/'old')],capture_output=True,text=True,timeout=10)
 assert result.returncode!=0 and 'hides==after' in result.stderr,result.stderr
 print('PASS117 negative control:inactive fallback reproduces per-frame physical cursor hide/show churn')
 (port/'ps5_temporary_input.h').write_text(current)
 subprocess.run([*common,'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True,timeout=30)
