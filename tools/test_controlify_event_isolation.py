#!/usr/bin/env python3
"""Real SDL global filter/queue + consumer facade, including original refusal."""
from pathlib import Path
import subprocess,tempfile,os
r=Path(__file__).resolve().parents[1]
# Verify the exact unchanged mod callback, rather than relying only on a C model.
import zipfile,hashlib
jar=r/'build/triggers116-test/controlify.jar'
assert hashlib.sha256(jar.read_bytes()).hexdigest()=='bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a'
with tempfile.TemporaryDirectory()as d:
 w=Path(d)
 with zipfile.ZipFile(jar)as z:
  name=next(n for n in z.namelist()if 'sdl-api-' in n and n.endswith('.jar'));(w/'sdl-api.jar').write_bytes(z.read(name))
 (w/'FilterCheck.java').write_text('''import dev.isxander.sdl.SdlEvent;
public class FilterCheck{public static void main(String[]a)throws Exception{
 var cls=Class.forName("dev.isxander.controlify.controllermanager.SDLControllerManager$EventFilter");
 var ctor=cls.getDeclaredConstructor();ctor.setAccessible(true);var filter=ctor.newInstance();
 var method=cls.getDeclaredMethod("filter",Class.forName("dev.isxander.sdl.SdlPointer"),SdlEvent.class);method.setAccessible(true);
 for(int type:new int[]{0x300,0x301,0x303,0x400,0x401,0x402,0x403,0x600,0x605,0x606}){
  boolean accepted=(boolean)method.invoke(filter,null,new SdlEvent(type,0,null));
  if(accepted!=(type==0x605||type==0x606))throw new AssertionError("Unexpected original filter "+type);
 }
 System.out.println("PASS exact unchanged Controlify EventFilter:rejects keyboard/text/mouse;accepts only joystick added/removed");
}}''')
 jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');cp=str(jar)+':'+str(w/'sdl-api.jar')
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),str(w/'FilterCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'-Xverify:all','-cp',str(w)+':'+cp,'FilterCheck'],check=True,timeout=20)
code=r'''
#include <SDL3/SDL.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
int prospero_controlify_events_preinit(void);
void prospero_controlify_SetEventFilter(SDL_EventFilter,void*);
bool prospero_controlify_GetEventFilter(SDL_EventFilter*,void**);
bool prospero_controlify_PollEvent(SDL_Event*);
static int calls;
static bool SDLCALL controller_filter(void *user,SDL_Event*e){assert(user==(void*)42);calls++;return e->type==SDL_EVENT_JOYSTICK_ADDED||e->type==SDL_EVENT_JOYSTICK_REMOVED;}
static bool SDLCALL reject(void*u,SDL_Event*e){return false;}
static void push(Uint32 type,int id){SDL_Event e;SDL_zero(e);e.type=type;if(type==SDL_EVENT_JOYSTICK_ADDED||type==SDL_EVENT_JOYSTICK_REMOVED)e.jdevice.which=id;assert(SDL_PushEvent(&e));}
static void*foreign(void*u){SDL_Event e;assert(!prospero_controlify_PollEvent(&e));assert(strstr(SDL_GetError(),"main thread"));return NULL;}
int main(void){
 assert(SDL_Init(SDL_INIT_EVENTS));SDL_FlushEvents(SDL_EVENT_FIRST,SDL_EVENT_LAST);
 SDL_SetEventFilter(controller_filter,(void*)42);
 SDL_Event key;SDL_zero(key);key.type=SDL_EVENT_KEY_DOWN;assert(!SDL_PushEvent(&key));
 key.type=SDL_EVENT_MOUSE_MOTION;assert(!SDL_PushEvent(&key));
 SDL_SetEventFilter(NULL,NULL);SDL_FlushEvents(SDL_EVENT_FIRST,SDL_EVENT_LAST);
 assert(!prospero_controlify_events_preinit());assert(!prospero_controlify_events_preinit());
 push(SDL_EVENT_KEY_DOWN,0);push(SDL_EVENT_TEXT_INPUT,0);push(SDL_EVENT_MOUSE_MOTION,0);push(SDL_EVENT_MOUSE_BUTTON_DOWN,0);
 prospero_controlify_SetEventFilter(controller_filter,(void*)42);
 SDL_EventFilter f=NULL;void*user=NULL;assert(!SDL_GetEventFilter(&f,&user)&&!f);assert(prospero_controlify_GetEventFilter(&f,&user)&&f==controller_filter&&user==(void*)42);
 push(SDL_EVENT_JOYSTICK_ADDED,7);push(SDL_EVENT_JOYSTICK_REMOVED,7);push(SDL_EVENT_KEY_UP,0);
 SDL_Event e;assert(prospero_controlify_PollEvent(NULL));assert(prospero_controlify_PollEvent(&e)&&e.type==SDL_EVENT_JOYSTICK_ADDED&&e.jdevice.which==7);
 // The main game drains its own copy first, without stealing the mod's event.
 int physical=0,connection=0;while(SDL_PollEvent(&e)){if(e.type==SDL_EVENT_JOYSTICK_ADDED||e.type==SDL_EVENT_JOYSTICK_REMOVED)connection++;else if(e.type==SDL_EVENT_KEY_DOWN||e.type==SDL_EVENT_KEY_UP||e.type==SDL_EVENT_TEXT_INPUT||e.type==SDL_EVENT_MOUSE_MOTION||e.type==SDL_EVENT_MOUSE_BUTTON_DOWN)physical++;}
 assert(physical==5&&connection==2);assert(prospero_controlify_PollEvent(&e)&&e.type==SDL_EVENT_JOYSTICK_REMOVED);assert(!prospero_controlify_PollEvent(&e));
 prospero_controlify_SetEventFilter(reject,NULL);push(SDL_EVENT_JOYSTICK_ADDED,8);assert(!prospero_controlify_PollEvent(NULL));
 prospero_controlify_SetEventFilter(NULL,NULL);push(SDL_EVENT_JOYSTICK_REMOVED,8);assert(prospero_controlify_PollEvent(&e)&&e.jdevice.which==8);assert(!prospero_controlify_PollEvent(&e));
 pthread_t thread;assert(!pthread_create(&thread,NULL,foreign,NULL));pthread_join(thread,NULL);
 for(int i=0;i<256;i++)push(SDL_EVENT_JOYSTICK_ADDED,i+1);
 push(SDL_EVENT_JOYSTICK_REMOVED,1);assert(!prospero_controlify_PollEvent(&e)&&strstr(SDL_GetError(),"overflow"));
 for(int i=0;i<256;i++){assert(prospero_controlify_PollEvent(&e));assert(e.jdevice.which==(unsigned)i+1);}assert(!prospero_controlify_PollEvent(&e));
 for(int cycle=0;cycle<1000;cycle++){push(SDL_EVENT_JOYSTICK_ADDED,1);push(SDL_EVENT_JOYSTICK_REMOVED,1);assert(prospero_controlify_PollEvent(&e)&&e.type==SDL_EVENT_JOYSTICK_ADDED);assert(prospero_controlify_PollEvent(&e)&&e.type==SDL_EVENT_JOYSTICK_REMOVED);}
 SDL_Quit();puts("PASS actual SDL:originalcontrollerfilterdropskeyboard/mouse;aliasfacadepreservesgamefilter/5physicalevents/independentconnectioncopies/order/peek/localfilterchange/foreignthreadrejection/256queuebound+explicitoverflow/1000cycles;ASanUBSan");
}
'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'test.c').write_text(code)
 subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-pthread','-I/opt/homebrew/include',str(w/'test.c'),str(r/'client/ports/sdl/ps5_controlify_events.c'),'-L/opt/homebrew/lib','-lSDL3','-o',str(w/'test')],check=True)
 subprocess.run([str(w/'test')],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'),timeout=40)
