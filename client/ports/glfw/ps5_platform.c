/* SPDX-License-Identifier: Zlib
 * ProsperoCraft SDL3 backend for genuine GLFW3.4. This is an altered platform
 * implementation, not GLFW's headless monitor/window implementation.
 */
#include "internal.h"
#include <SDL3/SDL.h>
extern void ps5glfw_extensions(char**);
extern int ps5glfw_vulkan_load(void);
extern void ps5glfw_vulkan_unload(void);
extern int ps5glfw_presentation(void*,void*,uint32_t);
extern int32_t ps5glfw_surface(void*,SDL_Window*,const void*,uint64_t*);
#include <string.h>
#include "../sdl/ps5_startup_boundary.h"

static SDL_Window* native(_GLFWwindow* w){return (SDL_Window*)w->null.ps5_window;}
static void error(void){_glfwInputError(GLFW_PLATFORM_ERROR,"PS5 SDL: %s",SDL_GetError());}
static int init(void){
 PS5_BOUNDARY("GLFW platform init enter");
 PS5_BOUNDARY("SDL video/events init enter");
 if(!SDL_InitSubSystem(SDL_INIT_VIDEO|SDL_INIT_EVENTS)){error();return GLFW_FALSE;}
 PS5_BOUNDARY("SDL video/events init returned success");
 PS5_BOUNDARY("GLFW Vulkan load enter");
 if(!ps5glfw_vulkan_load()){error();SDL_QuitSubSystem(SDL_INIT_VIDEO|SDL_INIT_EVENTS);return GLFW_FALSE;}
 PS5_BOUNDARY("GLFW Vulkan load returned success");
 PS5_BOUNDARY("SDL display enumeration enter");
 int count=0;SDL_DisplayID* displays=SDL_GetDisplays(&count);
 PS5_BOUNDARY("SDL display enumeration returned");
 if(!displays||!count){SDL_free(displays);error();ps5glfw_vulkan_unload();SDL_QuitSubSystem(SDL_INIT_VIDEO|SDL_INIT_EVENTS);return GLFW_FALSE;}
 for(int i=0;i<count;i++){
  PS5_BOUNDARY("GLFW monitor allocation enter");
  _GLFWmonitor* monitor=_glfw_calloc(1,sizeof(*monitor));
  if(!monitor){PS5_BOUNDARY("GLFW monitor allocation failed");SDL_free(displays);ps5glfw_vulkan_unload();SDL_QuitSubSystem(SDL_INIT_VIDEO|SDL_INIT_EVENTS);return GLFW_FALSE;}
  const char* display_name=SDL_GetDisplayName(displays[i]);
  if(!display_name)display_name="PS5 display";
  strncpy(monitor->name,display_name,sizeof(monitor->name)-1);
  PS5_BOUNDARY("GLFW monitor allocation returned");
  monitor->null.ps5_display=displays[i];_glfwInputMonitor(monitor,GLFW_CONNECTED,_GLFW_INSERT_LAST);
 }
 PS5_BOUNDARY("GLFW platform init complete");
 SDL_free(displays);return GLFW_TRUE;
}
static void terminate(void){ps5glfw_vulkan_unload();SDL_free(_glfw.null.clipboardString);_glfw.null.clipboardString=NULL;SDL_QuitSubSystem(SDL_INIT_VIDEO|SDL_INIT_EVENTS);}
static GLFWbool mode(_GLFWmonitor* m,GLFWvidmode* out){
 const SDL_DisplayMode* value=SDL_GetCurrentDisplayMode(m->null.ps5_display);
 if(!value){error();return GLFW_FALSE;}
 *out=(GLFWvidmode){value->w,value->h,8,8,8,(int)(value->refresh_rate+0.5f)};return GLFW_TRUE;
}
static GLFWvidmode* modes(_GLFWmonitor* m,int* count){
 GLFWvidmode* result=_glfw_calloc(1,sizeof(*result));if(!result){*count=0;return NULL;}if(!mode(m,result)){_glfw_free(result);*count=0;return NULL;}*count=1;return result;
}
static void monitorPos(_GLFWmonitor* m,int* x,int* y){SDL_Rect r={0};if(!SDL_GetDisplayBounds(m->null.ps5_display,&r))error();if(x)*x=r.x;if(y)*y=r.y;}
static void workarea(_GLFWmonitor* m,int* x,int* y,int* width,int* height){SDL_Rect r={0};if(!SDL_GetDisplayUsableBounds(m->null.ps5_display,&r))error();if(x)*x=r.x;if(y)*y=r.y;if(width)*width=r.w;if(height)*height=r.h;}
static void monitorScale(_GLFWmonitor* m,float* x,float* y){float s=SDL_GetDisplayContentScale(m->null.ps5_display);if(s<=0)s=1;if(x)*x=s;if(y)*y=s;}
static GLFWbool gammaGet(_GLFWmonitor* m,GLFWgammaramp* r){(void)m;(void)r;_glfwInputError(GLFW_FEATURE_UNAVAILABLE,"PS5 display gamma control is unavailable");return GLFW_FALSE;}
static void gammaSet(_GLFWmonitor* m,const GLFWgammaramp* r){(void)gammaGet(m,(GLFWgammaramp*)r);}
static void size(_GLFWwindow* w,int* x,int* y){SDL_GetWindowSize(native(w),x,y);}
static void pixels(_GLFWwindow* w,int* x,int* y){SDL_GetWindowSizeInPixels(native(w),x,y);}
static GLFWbool create(_GLFWwindow* w,const _GLFWwndconfig* cfg,const _GLFWctxconfig* ctx,const _GLFWfbconfig* fb){
 (void)fb;if(ctx->client!=GLFW_NO_API){_glfwInputError(GLFW_API_UNAVAILABLE,"PS5 GLFW backend requires Vulkan/GLFW_NO_API");return GLFW_FALSE;}
 SDL_WindowFlags flags=SDL_WINDOW_VULKAN|(cfg->visible?0:SDL_WINDOW_HIDDEN)|(cfg->resizable?SDL_WINDOW_RESIZABLE:0)|(w->monitor?SDL_WINDOW_FULLSCREEN:0);
#ifdef PS5_GLFW_HOST_TEST
 flags&=~SDL_WINDOW_VULKAN; /* Real SDL dummy window for host event/lifecycle tests only. */
#endif
 PS5_BOUNDARY("SDL window create enter");
 SDL_Window* s=SDL_CreateWindow(cfg->title,cfg->width,cfg->height,flags);if(!s){error();return GLFW_FALSE;}
 PS5_BOUNDARY("SDL window create returned success");
 w->null.ps5_window=s;w->null.width=cfg->width;w->null.height=cfg->height;w->null.opacity=1;
 if(w->monitor)_glfwInputMonitorWindow(w->monitor,w);
 SDL_StartTextInput(s);return GLFW_TRUE;
}
static void destroy(_GLFWwindow* w){if(w->monitor)_glfwInputMonitorWindow(w->monitor,NULL);if(native(w)){SDL_StopTextInput(native(w));SDL_DestroyWindow(native(w));w->null.ps5_window=NULL;}}
static void title(_GLFWwindow* w,const char* s){if(!SDL_SetWindowTitle(native(w),s))error();}
static void icon(_GLFWwindow* w,int n,const GLFWimage* images){if(n<=0)return;SDL_Surface* s=SDL_CreateSurfaceFrom(images[0].width,images[0].height,SDL_PIXELFORMAT_RGBA32,images[0].pixels,images[0].width*4);if(s){SDL_SetWindowIcon(native(w),s);SDL_DestroySurface(s);}}
static void pos(_GLFWwindow* w,int* x,int* y){SDL_GetWindowPosition(native(w),x,y);}
static void setPos(_GLFWwindow* w,int x,int y){if(!SDL_SetWindowPosition(native(w),x,y))error();}
static void setSize(_GLFWwindow* w,int x,int y){if(!SDL_SetWindowSize(native(w),x,y))error();}
static void limits(_GLFWwindow* w,int minx,int miny,int maxx,int maxy){SDL_SetWindowMinimumSize(native(w),minx==GLFW_DONT_CARE?0:minx,miny==GLFW_DONT_CARE?0:miny);SDL_SetWindowMaximumSize(native(w),maxx==GLFW_DONT_CARE?0:maxx,maxy==GLFW_DONT_CARE?0:maxy);}
static void aspect(_GLFWwindow* w,int n,int d){float a=n==GLFW_DONT_CARE?0:(float)n/d;SDL_SetWindowAspectRatio(native(w),a,a);}
static void windowScale(_GLFWwindow* w,float* x,float* y){float s=SDL_GetWindowDisplayScale(native(w));if(s<=0)s=1;if(x)*x=s;if(y)*y=s;}
static void frame(_GLFWwindow* w,int* l,int* t,int* r,int* b){SDL_GetWindowBordersSize(native(w),t,l,b,r);}
#define WINDOW_OP(name,call) static void name(_GLFWwindow* w){if(!call(native(w)))error();}
WINDOW_OP(show,SDL_ShowWindow) WINDOW_OP(hide,SDL_HideWindow) WINDOW_OP(focus,SDL_RaiseWindow)
WINDOW_OP(iconify,SDL_MinimizeWindow) WINDOW_OP(restore,SDL_RestoreWindow) WINDOW_OP(maximize,SDL_MaximizeWindow)
static void attention(_GLFWwindow* w){SDL_FlashWindow(native(w),SDL_FLASH_BRIEFLY);}
static void setMonitor(_GLFWwindow* w,_GLFWmonitor* m,int x,int y,int width,int height,int hz){
 (void)hz;if(!SDL_SetWindowFullscreen(native(w),m!=NULL)){error();return;}
 if(w->monitor)_glfwInputMonitorWindow(w->monitor,NULL);_glfwInputWindowMonitor(w,m);if(m)_glfwInputMonitorWindow(m,w);else{setPos(w,x,y);setSize(w,width,height);}
}
#define WINDOW_FLAG(name,flag,negate) static GLFWbool name(_GLFWwindow* w){return negate?!((SDL_GetWindowFlags(native(w)))&flag):!!((SDL_GetWindowFlags(native(w)))&flag);}
WINDOW_FLAG(focused,SDL_WINDOW_INPUT_FOCUS,0) WINDOW_FLAG(iconified,SDL_WINDOW_MINIMIZED,0) WINDOW_FLAG(visible,SDL_WINDOW_HIDDEN,1)
WINDOW_FLAG(maximized,SDL_WINDOW_MAXIMIZED,0) WINDOW_FLAG(hovered,SDL_WINDOW_MOUSE_FOCUS,0) WINDOW_FLAG(transparent,SDL_WINDOW_TRANSPARENT,0)
static float opacity(_GLFWwindow* w){return SDL_GetWindowOpacity(native(w));}
static void setOpacity(_GLFWwindow* w,float a){if(!SDL_SetWindowOpacity(native(w),a))error();}
static void resizable(_GLFWwindow* w,GLFWbool b){SDL_SetWindowResizable(native(w),b);}
static void decorated(_GLFWwindow* w,GLFWbool b){SDL_SetWindowBordered(native(w),b);}
static void floating(_GLFWwindow* w,GLFWbool b){SDL_SetWindowAlwaysOnTop(native(w),b);}
static void passthrough(_GLFWwindow* w,GLFWbool b){(void)w;if(b)_glfwInputError(GLFW_FEATURE_UNAVAILABLE,"Mouse passthrough is unavailable");}
static int mods(SDL_Keymod m){return ((m&SDL_KMOD_SHIFT)?GLFW_MOD_SHIFT:0)|((m&SDL_KMOD_CTRL)?GLFW_MOD_CONTROL:0)|((m&SDL_KMOD_ALT)?GLFW_MOD_ALT:0)|((m&SDL_KMOD_GUI)?GLFW_MOD_SUPER:0)|((m&SDL_KMOD_CAPS)?GLFW_MOD_CAPS_LOCK:0)|((m&SDL_KMOD_NUM)?GLFW_MOD_NUM_LOCK:0);}
static int key(SDL_Scancode s){
 if(s>=SDL_SCANCODE_A&&s<=SDL_SCANCODE_Z)return GLFW_KEY_A+s-SDL_SCANCODE_A;
 if(s>=SDL_SCANCODE_1&&s<=SDL_SCANCODE_9)return GLFW_KEY_1+s-SDL_SCANCODE_1;
 if(s==SDL_SCANCODE_0)return GLFW_KEY_0;
 if(s>=SDL_SCANCODE_F1&&s<=SDL_SCANCODE_F12)return GLFW_KEY_F1+s-SDL_SCANCODE_F1;
 if(s>=SDL_SCANCODE_F13&&s<=SDL_SCANCODE_F24)return GLFW_KEY_F13+s-SDL_SCANCODE_F13;
 if(s>=SDL_SCANCODE_KP_1&&s<=SDL_SCANCODE_KP_9)return GLFW_KEY_KP_1+s-SDL_SCANCODE_KP_1;
 switch(s){
#define KEY(s,g) case SDL_SCANCODE_##s:return GLFW_KEY_##g;
 KEY(RETURN,ENTER) KEY(ESCAPE,ESCAPE) KEY(BACKSPACE,BACKSPACE) KEY(TAB,TAB) KEY(SPACE,SPACE)
 KEY(RIGHT,RIGHT) KEY(LEFT,LEFT) KEY(UP,UP) KEY(DOWN,DOWN) KEY(INSERT,INSERT) KEY(DELETE,DELETE)
 KEY(HOME,HOME) KEY(END,END) KEY(PAGEUP,PAGE_UP) KEY(PAGEDOWN,PAGE_DOWN)
 KEY(LSHIFT,LEFT_SHIFT) KEY(RSHIFT,RIGHT_SHIFT) KEY(LCTRL,LEFT_CONTROL) KEY(RCTRL,RIGHT_CONTROL)
 KEY(LALT,LEFT_ALT) KEY(RALT,RIGHT_ALT) KEY(LGUI,LEFT_SUPER) KEY(RGUI,RIGHT_SUPER)
 KEY(CAPSLOCK,CAPS_LOCK) KEY(NUMLOCKCLEAR,NUM_LOCK) KEY(SCROLLLOCK,SCROLL_LOCK)
 KEY(PRINTSCREEN,PRINT_SCREEN) KEY(PAUSE,PAUSE) KEY(APPLICATION,MENU)
 KEY(KP_0,KP_0) KEY(KP_ENTER,KP_ENTER) KEY(KP_PERIOD,KP_DECIMAL) KEY(KP_DIVIDE,KP_DIVIDE)
 KEY(KP_MULTIPLY,KP_MULTIPLY) KEY(KP_MINUS,KP_SUBTRACT) KEY(KP_PLUS,KP_ADD) KEY(KP_EQUALS,KP_EQUAL)
#undef KEY
 default:{SDL_Keycode c=SDL_GetKeyFromScancode(s,SDL_KMOD_NONE,false);return c>=32&&c<=126?(int)c:GLFW_KEY_UNKNOWN;}
 }
}
static int scancode(int k){for(int i=0;i<SDL_SCANCODE_COUNT;i++)if(key((SDL_Scancode)i)==k)return i;return -1;}
static const char* keyName(int s){return SDL_GetScancodeName((SDL_Scancode)s);}
static void cursorPos(_GLFWwindow* w,double* x,double* y){if(x)*x=w->virtualCursorPosX;if(y)*y=w->virtualCursorPosY;}
static void warp(_GLFWwindow* w,double x,double y){SDL_WarpMouseInWindow(native(w),(float)x,(float)y);}
static void cursorMode(_GLFWwindow* w,int mode){
 if(!SDL_SetWindowRelativeMouseMode(native(w),mode==GLFW_CURSOR_DISABLED))error();
 if(mode==GLFW_CURSOR_NORMAL)SDL_ShowCursor();else SDL_HideCursor();
 if(!SDL_SetWindowMouseGrab(native(w),mode==GLFW_CURSOR_CAPTURED))error();
}
static void raw(_GLFWwindow* w,GLFWbool b){(void)w;(void)b;}
static GLFWbool rawSupported(void){return GLFW_TRUE;}
static GLFWbool makeCursor(_GLFWcursor* c,const GLFWimage* image,int x,int y){SDL_Surface* s=SDL_CreateSurfaceFrom(image->width,image->height,SDL_PIXELFORMAT_RGBA32,image->pixels,image->width*4);if(s){c->ps5_cursor=SDL_CreateColorCursor(s,x,y);SDL_DestroySurface(s);}return c->ps5_cursor!=NULL;}
static GLFWbool standardCursor(_GLFWcursor* c,int shape){SDL_SystemCursor s=SDL_SYSTEM_CURSOR_DEFAULT;switch(shape){case GLFW_IBEAM_CURSOR:s=SDL_SYSTEM_CURSOR_TEXT;break;case GLFW_CROSSHAIR_CURSOR:s=SDL_SYSTEM_CURSOR_CROSSHAIR;break;case GLFW_POINTING_HAND_CURSOR:s=SDL_SYSTEM_CURSOR_POINTER;break;case GLFW_RESIZE_EW_CURSOR:s=SDL_SYSTEM_CURSOR_EW_RESIZE;break;case GLFW_RESIZE_NS_CURSOR:s=SDL_SYSTEM_CURSOR_NS_RESIZE;break;}c->ps5_cursor=SDL_CreateSystemCursor(s);return c->ps5_cursor!=NULL;}
static void freeCursor(_GLFWcursor* c){if(c->ps5_cursor)SDL_DestroyCursor(c->ps5_cursor);}
static void setCursor(_GLFWwindow* w,_GLFWcursor* c){(void)w;SDL_SetCursor(c?c->ps5_cursor:NULL);}
static void clipboardSet(const char* text){if(!SDL_SetClipboardText(text))error();}
static const char* clipboardGet(void){SDL_free(_glfw.null.clipboardString);_glfw.null.clipboardString=SDL_GetClipboardText();return _glfw.null.clipboardString;}
static _GLFWwindow* find(SDL_WindowID id){for(_GLFWwindow* w=_glfw.windowListHead;w;w=w->next)if(native(w)&&SDL_GetWindowID(native(w))==id)return w;return NULL;}
static void dispatch(const SDL_Event* e){
 if(e->type==SDL_EVENT_QUIT){for(_GLFWwindow* w=_glfw.windowListHead;w;){_GLFWwindow* next=w->next;_glfwInputWindowCloseRequest(w);w=next;}return;}
 _GLFWwindow* w=find(e->window.windowID);if(!w)return;
 switch(e->type){
 case SDL_EVENT_KEY_DOWN:case SDL_EVENT_KEY_UP:_glfwInputKey(w,key(e->key.scancode),e->key.scancode,e->type==SDL_EVENT_KEY_UP?GLFW_RELEASE:GLFW_PRESS,mods(e->key.mod));break;
 case SDL_EVENT_TEXT_INPUT:{const char* text=e->text.text;while(text&&*text){Uint32 c=SDL_StepUTF8(&text,NULL);if(c)_glfwInputChar(w,c,mods(SDL_GetModState()),GLFW_TRUE);}break;}
 case SDL_EVENT_MOUSE_MOTION:_glfwInputCursorPos(w,w->cursorMode==GLFW_CURSOR_DISABLED?w->virtualCursorPosX+e->motion.xrel:e->motion.x,w->cursorMode==GLFW_CURSOR_DISABLED?w->virtualCursorPosY+e->motion.yrel:e->motion.y);break;
 case SDL_EVENT_MOUSE_BUTTON_DOWN:case SDL_EVENT_MOUSE_BUTTON_UP:{int b=e->button.button==SDL_BUTTON_LEFT?GLFW_MOUSE_BUTTON_LEFT:e->button.button==SDL_BUTTON_RIGHT?GLFW_MOUSE_BUTTON_RIGHT:e->button.button==SDL_BUTTON_MIDDLE?GLFW_MOUSE_BUTTON_MIDDLE:e->button.button-1;_glfwInputMouseClick(w,b,e->type==SDL_EVENT_MOUSE_BUTTON_DOWN?GLFW_PRESS:GLFW_RELEASE,mods(SDL_GetModState()));break;}
 case SDL_EVENT_MOUSE_WHEEL:{double sign=e->wheel.direction==SDL_MOUSEWHEEL_FLIPPED?-1:1;_glfwInputScroll(w,e->wheel.x*sign,e->wheel.y*sign);break;}
 case SDL_EVENT_WINDOW_FOCUS_GAINED:case SDL_EVENT_WINDOW_FOCUS_LOST:_glfwInputWindowFocus(w,e->type==SDL_EVENT_WINDOW_FOCUS_GAINED);break;
 case SDL_EVENT_WINDOW_MOUSE_ENTER:case SDL_EVENT_WINDOW_MOUSE_LEAVE:_glfwInputCursorEnter(w,e->type==SDL_EVENT_WINDOW_MOUSE_ENTER);break;
 case SDL_EVENT_WINDOW_CLOSE_REQUESTED:_glfwInputWindowCloseRequest(w);break;
 case SDL_EVENT_WINDOW_MINIMIZED:case SDL_EVENT_WINDOW_RESTORED:_glfwInputWindowIconify(w,e->type==SDL_EVENT_WINDOW_MINIMIZED);break;
 case SDL_EVENT_WINDOW_MOVED:_glfwInputWindowPos(w,e->window.data1,e->window.data2);break;
 case SDL_EVENT_WINDOW_RESIZED:_glfwInputWindowSize(w,e->window.data1,e->window.data2);break;
 case SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED:_glfwInputFramebufferSize(w,e->window.data1,e->window.data2);break;
 case SDL_EVENT_DROP_FILE:{const char* names[]={e->drop.data};_glfwInputDrop(w,1,names);break;}
 }
}
static void poll(void){SDL_Event e;while(SDL_PollEvent(&e))dispatch(&e);}
static void wait(void){SDL_Event e;if(SDL_WaitEvent(&e))dispatch(&e);poll();}
static void waitTimeout(double t){SDL_Event e;int ms=t>2147483?2147483000:(int)(t*1000);if(SDL_WaitEventTimeout(&e,ms))dispatch(&e);poll();}
static void post(void){SDL_Event e={0};e.type=SDL_EVENT_USER;SDL_PushEvent(&e);}
static void extensions(char** out){ps5glfw_extensions(out);}
static GLFWbool present(VkInstance i,VkPhysicalDevice p,uint32_t q){return ps5glfw_presentation(i,p,q);}
static VkResult surface(VkInstance i,_GLFWwindow* w,const VkAllocationCallbacks* a,VkSurfaceKHR* out){return ps5glfw_surface(i,native(w),a,out);}
void _glfwConfigurePs5(_GLFWplatform* p){
 p->init=init;p->terminate=terminate;p->getMonitorPos=monitorPos;p->getMonitorWorkarea=workarea;p->getMonitorContentScale=monitorScale;p->getVideoModes=modes;p->getVideoMode=mode;p->getGammaRamp=gammaGet;p->setGammaRamp=gammaSet;
 p->createWindow=create;p->destroyWindow=destroy;p->setWindowTitle=title;p->setWindowIcon=icon;p->getWindowPos=pos;p->setWindowPos=setPos;p->getWindowSize=size;p->setWindowSize=setSize;p->setWindowSizeLimits=limits;p->setWindowAspectRatio=aspect;p->getFramebufferSize=pixels;p->getWindowFrameSize=frame;p->getWindowContentScale=windowScale;
 p->showWindow=show;p->hideWindow=hide;p->focusWindow=focus;p->iconifyWindow=iconify;p->restoreWindow=restore;p->maximizeWindow=maximize;p->requestWindowAttention=attention;p->setWindowMonitor=setMonitor;
 p->windowFocused=focused;p->windowIconified=iconified;p->windowVisible=visible;p->windowMaximized=maximized;p->windowHovered=hovered;p->framebufferTransparent=transparent;p->getWindowOpacity=opacity;p->setWindowOpacity=setOpacity;p->setWindowResizable=resizable;p->setWindowDecorated=decorated;p->setWindowFloating=floating;p->setWindowMousePassthrough=passthrough;
 p->getCursorPos=cursorPos;p->setCursorPos=warp;p->setCursorMode=cursorMode;p->setRawMouseMotion=raw;p->rawMouseMotionSupported=rawSupported;p->getKeyScancode=scancode;p->getScancodeName=keyName;p->createCursor=makeCursor;p->createStandardCursor=standardCursor;p->destroyCursor=freeCursor;p->setCursor=setCursor;p->setClipboardString=clipboardSet;p->getClipboardString=clipboardGet;
 p->pollEvents=poll;p->waitEvents=wait;p->waitEventsTimeout=waitTimeout;p->postEmptyEvent=post;p->getRequiredInstanceExtensions=extensions;p->getPhysicalDevicePresentationSupport=present;p->createWindowSurface=surface;
}

/* Minecraft's optional GLFW IME extension. PS5 has no native composition
 * service. Keep callback/rectangle ABI and ordinary Unicode text, but report
 * IME disabled rather than inventing a platform composition state. */
int ps5glfw_ime_get(_GLFWwindow* w){(void)w;return GLFW_FALSE;}
void ps5glfw_ime_set(_GLFWwindow* w,int value){(void)w;if(value)_glfwInputError(GLFW_FEATURE_UNAVAILABLE,"Native IME composition is unavailable on PS5");}
void* glfwSetPreeditCallback(GLFWwindow* handle,void* callback){_GLFWwindow* w=(_GLFWwindow*)handle;void* old=w->null.ps5_preedit;w->null.ps5_preedit=callback;return old;}
void* glfwSetIMEStatusCallback(GLFWwindow* handle,void* callback){_GLFWwindow* w=(_GLFWwindow*)handle;void* old=w->null.ps5_ime;w->null.ps5_ime=callback;return old;}
void glfwSetPreeditCursorRectangle(GLFWwindow* handle,int x,int y,int width,int height){_GLFWwindow* w=(_GLFWwindow*)handle;int values[]={x,y,width,height};memcpy(w->null.ps5_rect,values,sizeof(values));SDL_Rect r={x,y,width,height};SDL_SetTextInputArea(native(w),&r,0);}
void glfwGetPreeditCursorRectangle(GLFWwindow* handle,int* x,int* y,int* width,int* height){_GLFWwindow* w=(_GLFWwindow*)handle;if(x)*x=w->null.ps5_rect[0];if(y)*y=w->null.ps5_rect[1];if(width)*width=w->null.ps5_rect[2];if(height)*height=w->null.ps5_rect[3];}
void glfwResetPreeditText(GLFWwindow* handle){_GLFWwindow* w=(_GLFWwindow*)handle;SDL_ClearComposition(native(w));}
