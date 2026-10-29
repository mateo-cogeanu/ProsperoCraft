#!/usr/bin/env python3
"""Actual pinned GLFW + real SDL dummy events under ASan/UBSan; no PS5/GPU claim."""
from pathlib import Path
import subprocess,tempfile,os
ROOT=Path(__file__).resolve().parents[1]
source=r'''
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <SDL3/SDL.h>
#include <assert.h>
#include <string.h>
extern void* glfwSetPreeditCallback(GLFWwindow*,void*);
extern void* glfwSetIMEStatusCallback(GLFWwindow*,void*);
extern void glfwSetPreeditCursorRectangle(GLFWwindow*,int,int,int,int);
extern void glfwGetPreeditCursorRectangle(GLFWwindow*,int*,int*,int*,int*);
static int presses,releases,characters,button,scrolls,motions,closed;static unsigned last;
static void onkey(GLFWwindow*w,int key,int scan,int action,int mods){assert(key==GLFW_KEY_W&&scan==SDL_SCANCODE_W);if(action==GLFW_PRESS)presses++;if(action==GLFW_RELEASE)releases++;}
static void onchar(GLFWwindow*w,unsigned c){characters++;last=c;}
static void onbutton(GLFWwindow*w,int b,int a,int m){assert(b==GLFW_MOUSE_BUTTON_RIGHT&&a==GLFW_PRESS);button++;}
static void onscroll(GLFWwindow*w,double x,double y){assert(x==0&&y==2);scrolls++;}
static void onmotion(GLFWwindow*w,double x,double y){assert(x==111&&y==222);motions++;}
static void onclose(GLFWwindow*w){closed++;}
int main(void){
 for(int run=0;run<3;run++){
  glfwInitHint(GLFW_PLATFORM,GLFW_PLATFORM_NULL);assert(glfwInit());int count=0;assert(glfwGetMonitors(&count)&&count>0);const GLFWvidmode* mode=glfwGetVideoMode(glfwGetPrimaryMonitor());assert(mode&&mode->width>0&&mode->height>0);
  glfwWindowHint(GLFW_CLIENT_API,GLFW_NO_API);GLFWwindow* w=glfwCreateWindow(640,480,"Real SDL GLFW test",NULL,NULL);assert(w);assert(!strcmp(glfwGetWindowTitle(w),"Real SDL GLFW test"));int x=0,y=0;glfwGetWindowSize(w,&x,&y);assert(x==640&&y==480);glfwSetWindowUserPointer(w,&count);assert(glfwGetWindowUserPointer(w)==&count);
  glfwPollEvents();glfwSetKeyCallback(w,onkey);glfwSetCharCallback(w,onchar);glfwSetMouseButtonCallback(w,onbutton);glfwSetScrollCallback(w,onscroll);glfwSetCursorPosCallback(w,onmotion);glfwSetWindowCloseCallback(w,onclose);
  SDL_Window* s=SDL_GetKeyboardFocus();if(!s){int n=0;SDL_Window** windows=SDL_GetWindows(&n);assert(n==1);s=windows[0];SDL_free(windows);}SDL_WindowID id=SDL_GetWindowID(s);
  SDL_Event e={0};e.key.type=SDL_EVENT_KEY_DOWN;e.key.windowID=id;e.key.scancode=SDL_SCANCODE_W;e.key.down=true;assert(SDL_PushEvent(&e));glfwPollEvents();assert(glfwGetKey(w,GLFW_KEY_W)==GLFW_PRESS);
  e.key.type=SDL_EVENT_KEY_UP;e.key.down=false;SDL_PushEvent(&e);
  memset(&e,0,sizeof(e));e.text.type=SDL_EVENT_TEXT_INPUT;e.text.windowID=id;e.text.text="A\xc3\xa4\xf0\x9f\x98\x80";SDL_PushEvent(&e);
  memset(&e,0,sizeof(e));e.button.type=SDL_EVENT_MOUSE_BUTTON_DOWN;e.button.windowID=id;e.button.button=SDL_BUTTON_RIGHT;SDL_PushEvent(&e);
  memset(&e,0,sizeof(e));e.wheel.type=SDL_EVENT_MOUSE_WHEEL;e.wheel.windowID=id;e.wheel.y=2;SDL_PushEvent(&e);
  memset(&e,0,sizeof(e));e.motion.type=SDL_EVENT_MOUSE_MOTION;e.motion.windowID=id;e.motion.x=111;e.motion.y=222;SDL_PushEvent(&e);
  glfwPollEvents();assert(glfwGetKey(w,GLFW_KEY_W)==GLFW_RELEASE);assert(presses==run+1&&releases==run+1&&characters==(run+1)*3&&last==0x1f600&&button==run+1&&scrolls==run+1&&motions==run+1);
  assert(!glfwSetPreeditCallback(w,(void*)onchar));assert(glfwSetPreeditCallback(w,NULL)==(void*)onchar);assert(!glfwSetIMEStatusCallback(w,(void*)onclose));assert(glfwSetIMEStatusCallback(w,NULL)==(void*)onclose);
  assert(!glfwGetInputMode(w,208903));glfwSetInputMode(w,208903,0);glfwSetPreeditCursorRectangle(w,1,2,3,4);glfwGetPreeditCursorRectangle(w,&x,&y,NULL,NULL);assert(x==1&&y==2);
  e=(SDL_Event){0};e.window.type=SDL_EVENT_WINDOW_CLOSE_REQUESTED;e.window.windowID=id;SDL_PushEvent(&e);glfwPollEvents();assert(closed==run+1&&glfwWindowShouldClose(w));
  glfwDestroyWindow(w);glfwWindowHint(GLFW_CLIENT_API,GLFW_OPENGL_API);assert(!glfwCreateWindow(320,200,"No invented GL",NULL,NULL));assert(glfwGetError(NULL)==GLFW_API_UNAVAILABLE);glfwTerminate();assert(!(SDL_WasInit(SDL_INIT_VIDEO)&SDL_INIT_VIDEO));
 }
 return 0;
}
'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'test.c').write_text(source);lib=ROOT/'build/glfw-native/host';includes=lib/'source/include'
 subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-I'+str(includes),'-I/opt/homebrew/include',str(w/'test.c'),str(lib/'libps5glfw.dylib'),'-L/opt/homebrew/lib','-lSDL3','-o',str(w/'test')],check=True)
 subprocess.run([str(w/'test')],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'),timeout=30)
print('PASS genuine GLFW core + SDL window/monitor, 3 init/teardown cycles, key state/callbacks, Unicode including emoji, mouse/button/scroll, optional IME ABI/disabled state/rectangle, close callback and explicit OpenGL refusal under ASan/UBSan. Host SDL dummy window only; PS5 and Vulkan pending.')
