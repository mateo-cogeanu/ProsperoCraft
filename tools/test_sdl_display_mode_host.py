#!/usr/bin/env python3
"""Host inventory regression for actual PS5 SDL mode/surface hook;no GPU claim."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];work=ROOT/'build/sdl-display-mode-host';work.mkdir(exist_ok=True)
s=(ROOT/'client/ports/sdl/SDL_ps5video.c').read_text();query=s[s.index('static bool PS5_QueryDisplay('):s.index('static bool PS5_VideoInit(')];hook=s[s.index('static bool PS5_Vulkan_CreateSurface('):s.index('static void PS5_Vulkan_DestroySurface(')]
preamble=r'''
#define VK_NO_PROTOTYPES
#include <vulkan/vulkan.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
typedef void SDL_VideoDevice;typedef struct {int w,h;}SDL_Window;typedef struct{unsigned format;int w,h;float refresh_rate;}SDL_DisplayMode;
#define SDL_zero(x) memset(&(x),0,sizeof(x))
#define SDL_PIXELFORMAT_BGRA32 1
static bool SDL_SetError(const char*fmt,...){(void)fmt;return false;}
static void SDL_Log(const char*fmt,...){(void)fmt;}
static const char*render_size;static const char*SDL_GetHint(const char*name){assert(!strcmp(name,"PS5_RENDER_SIZE"));return render_size;}
static int bad_alpha,incomplete,creates;static VkExtent2D chosen;
static VkDisplayModePropertiesKHR inventory[]={
 {.displayMode=(VkDisplayModeKHR)1,.parameters={{3840,2160},119880}},
 {.displayMode=(VkDisplayModeKHR)2,.parameters={{1920,1080},119880}},
 {.displayMode=(VkDisplayModeKHR)3,.parameters={{3840,2160},59940}},
 {.displayMode=(VkDisplayModeKHR)4,.parameters={{1920,1080},59940}}};
static VkResult VKAPI_CALL devices(VkInstance i,uint32_t*n,VkPhysicalDevice*p){(void)i;*n=1;p[0]=(VkPhysicalDevice)1;return VK_SUCCESS;}
static VkResult VKAPI_CALL displays(VkPhysicalDevice d,uint32_t*n,VkDisplayPropertiesKHR*p){(void)d;*n=1;p[0]=(VkDisplayPropertiesKHR){.display=(VkDisplayKHR)1,.physicalResolution={3840,2160},.supportedTransforms=VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR};return VK_SUCCESS;}
static VkResult VKAPI_CALL modes(VkPhysicalDevice d,VkDisplayKHR display,uint32_t*n,VkDisplayModePropertiesKHR*p){(void)d;(void)display;*n=4;memcpy(p,inventory,sizeof(inventory));return incomplete?VK_INCOMPLETE:VK_SUCCESS;}
static VkResult VKAPI_CALL planes(VkPhysicalDevice d,uint32_t*n,VkDisplayPlanePropertiesKHR*p){(void)d;*n=1;p[0]=(VkDisplayPlanePropertiesKHR){.currentStackIndex=7};return VK_SUCCESS;}
static VkResult VKAPI_CALL supports(VkPhysicalDevice d,uint32_t plane,uint32_t*n,VkDisplayKHR*p){(void)d;(void)plane;*n=1;p[0]=(VkDisplayKHR)1;return VK_SUCCESS;}
static VkResult VKAPI_CALL caps(VkPhysicalDevice d,VkDisplayModeKHR mode,uint32_t plane,VkDisplayPlaneCapabilitiesKHR*p){(void)d;(void)plane;VkExtent2D e={0};for(int i=0;i<4;i++)if(mode==inventory[i].displayMode)e=inventory[i].parameters.visibleRegion;assert(e.width);*p=(VkDisplayPlaneCapabilitiesKHR){.supportedAlpha=bad_alpha?0:VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR,.minSrcExtent=e,.maxSrcExtent=e,.minDstExtent=e,.maxDstExtent=e};return VK_SUCCESS;}
static VkResult VKAPI_CALL create(VkInstance i,const VkDisplaySurfaceCreateInfoKHR*c,const VkAllocationCallbacks*a,VkSurfaceKHR*p){(void)i;(void)a;assert(c->planeIndex==0&&c->planeStackIndex==7&&c->imageExtent.width>0&&c->imageExtent.height>0&&c->alphaMode==VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR);chosen=c->imageExtent;*p=(VkSurfaceKHR)1;creates++;return VK_SUCCESS;}
static VkResult VKAPI_CALL surface_caps(VkPhysicalDevice d,VkSurfaceKHR s,VkSurfaceCapabilitiesKHR*p){(void)d;(void)s;*p=(VkSurfaceCapabilitiesKHR){.currentExtent={1920,1080},.minImageCount=2,.maxImageCount=3,.supportedUsageFlags=VK_IMAGE_USAGE_TRANSFER_DST_BIT};return VK_SUCCESS;}
static VkResult VKAPI_CALL create_instance(const VkInstanceCreateInfo*c,const VkAllocationCallbacks*a,VkInstance*i){(void)c;(void)a;*i=(VkInstance)1;return VK_SUCCESS;}
static void VKAPI_CALL destroy_instance(VkInstance i,const VkAllocationCallbacks*a){(void)i;(void)a;}
static PFN_vkVoidFunction vkGetInstanceProcAddr(VkInstance instance,const char*name){(void)instance;
#define ENTRY(vk,fn) if(!strcmp(name,"vk"#vk))return (PFN_vkVoidFunction)fn;
ENTRY(CreateInstance,create_instance) ENTRY(DestroyInstance,destroy_instance) ENTRY(EnumeratePhysicalDevices,devices) ENTRY(GetPhysicalDeviceDisplayPropertiesKHR,displays) ENTRY(GetDisplayModePropertiesKHR,modes) ENTRY(GetPhysicalDeviceDisplayPlanePropertiesKHR,planes) ENTRY(GetDisplayPlaneSupportedDisplaysKHR,supports) ENTRY(GetDisplayPlaneCapabilitiesKHR,caps) ENTRY(CreateDisplayPlaneSurfaceKHR,create) ENTRY(GetPhysicalDeviceSurfaceCapabilitiesKHR,surface_caps)
return NULL;}
'''
preamble+='\nstatic int ps5_surface_width=1920,ps5_surface_height=1080;\n#define SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED 1\nstatic void SDL_SendWindowEvent(SDL_Window*w,int event,int width,int height){assert(w&&event==1&&width==(int)chosen.width&&height==(int)chosen.height); }\n'
main=r'''
int main(void){VkExtent2D native={3840,2160};assert(PS5_SelectDisplayMode(inventory,4,native)==1);assert(PS5_SelectDisplayMode(inventory,3,native)==1);assert(PS5_SelectDisplayMode(NULL,0,native)==-1);assert(PS5_SelectDisplayMode(inventory,33,native)==-1);
assert(PS5_SelectDisplayMode(inventory,1,native)==-1);
assert(PS5_SelectRequestedMode(inventory,4,1920,1080)==1);assert(PS5_SelectRequestedMode(inventory,4,3840,2160)==0);assert(PS5_SelectRequestedMode(inventory,4,1366,768)==-1);SDL_Window window={1920,1080};
VkSurfaceKHR surface=VK_NULL_HANDLE;assert(PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface));assert(surface&&chosen.width==1920&&chosen.height==1080&&creates==1);
bad_alpha=1;assert(!PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&!surface&&creates==1);bad_alpha=0;incomplete=1;assert(!PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&!surface&&creates==1);
/* The same hook must use60Hz when the verified inventory offers no120Hz. */
incomplete=0;inventory[1].parameters.refreshRate=0;
assert(PS5_SelectDisplayMode(inventory,4,native)==3);
assert(PS5_SelectRequestedMode(inventory,4,1920,1080)==3);
inventory[1]=inventory[3];assert(PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&creates==2);
/* Never invent modes, choose>120Hz, or depend on enumeration order. */
inventory[1].parameters.refreshRate=144000;assert(PS5_SelectDisplayMode(inventory,4,native)==3);
inventory[1].parameters.refreshRate=120000;assert(PS5_SelectDisplayMode(inventory,4,native)==1);
VkDisplayModePropertiesKHR tmp=inventory[1];inventory[1]=inventory[3];inventory[3]=tmp;
assert(PS5_SelectDisplayMode(inventory,4,native)==3);
assert(PS5_SelectRequestedMode(NULL,0,1920,1080)==-1);
assert(PS5_SelectRequestedMode(inventory,33,1920,1080)==-1);
assert(PS5_SelectRequestedMode(inventory,4,0,1080)==-1);
render_size="3840x2160";SDL_DisplayMode reported;assert(PS5_QueryDisplay(&reported)&&reported.w==3840&&reported.h==2160&&ps5_surface_width==3840&&ps5_surface_height==2160);assert(PS5_SelectConfiguredRenderMode(inventory,4,render_size)==0);
assert(PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&chosen.width==3840&&chosen.height==2160&&ps5_surface_width==3840&&ps5_surface_height==2160);
for(unsigned i=0;i<4;i++){const char*bad[]={"1366x768","-1x1080","3840x2160junk","999999999999x1"};render_size=bad[i];int before=creates;assert(!PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&!surface&&creates==before);}
render_size="1920x1080";assert(PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&chosen.width==1920&&chosen.height==1080);
/* All launcher sizes must reach the real query and surface, with a stale1080p window. */
const char *sizes[]={"1280x720","1600x900","1920x1080","2560x1440","3840x2160"};
const uint32_t widths[]={1280,1600,1920,2560,3840},heights[]={720,900,1080,1440,2160};
for(unsigned i=0;i<5;i++){inventory[0].parameters.visibleRegion=(VkExtent2D){widths[i],heights[i]};render_size=sizes[i];assert(PS5_QueryDisplay(&reported)&&reported.w==(int)widths[i]&&reported.h==(int)heights[i]);assert(PS5_Vulkan_CreateSurface(NULL,&window,(VkInstance)1,NULL,&surface)&&chosen.width==widths[i]&&chosen.height==heights[i]);}
render_size=NULL;assert(PS5_SelectConfiguredRenderMode(inventory,4,render_size)==-2);
puts("PASS explicit user4K/1080p modes override stale logical window;unsupported/malformed fail without silent substitution;legacy controls; actual SDL surface hook:enumerated1080p119.88 preference,59.94 fallback,120Hz ceiling/order/invalid controls,1080p-only fallback,plane/display/alpha/extent/stack propagation,incomplete/unsupported rejection;host inventory fixture only,PS5 GPU pending");}
'''
unit=work/'check.c';unit.write_text(preamble+'\n'+(ROOT/'client/ports/sdl/ps5_display_mode.h').read_text()+'\n'+hook+query+main);binary=work/'check';subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-I'+str(ROOT/'.tools/lwjgl-vma-src'),str(unit),'-o',str(binary)],check=True);subprocess.run([str(binary)],check=True)
