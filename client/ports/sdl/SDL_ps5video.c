/*
 * Dusklight for the PlayStation 5 - SDL3's video driver for the console.
 *
 * The console has one output and no windows: this gives SDL one display and
 * lets it keep its window bookkeeping (size, flags, events) for a window that
 * is the whole screen. Nothing is drawn through SDL; the title's renderer
 * presents through VK_KHR_display on its own.
 *
 * Altered for the PS5 Java probe: actual Vulkan display query and static ICD
 * surface/presentation hooks replace preset dimensions and external surfaces.
 *
 * SPDX-License-Identifier: Zlib
 */
#include "SDL_internal.h"

#ifdef SDL_VIDEO_DRIVER_PS5

#include "video/SDL_sysvideo.h"
#include "events/SDL_events_c.h"
#include "events/SDL_keyboard_c.h"
#include "events/SDL_mouse_c.h"
#include "ps5_input_handoff.h"
#include "ps5_temporary_input.h"
#include "ps5_usb_input.h"
#include "ps5_relative_mouse.h"
#include "ps5_startup_boundary.h"

/* Use the same public resident loader as LWJGL. Minecraft checks pointer identity.
 * The public entry delegates to the real static ICD;all returned commands stay real. */
#include "video/SDL_vulkan_internal.h"
#include "ps5_display_mode.h"
extern PFN_vkVoidFunction vkGetInstanceProcAddr(VkInstance,const char*);
static bool PS5_Vulkan_LoadLibrary(SDL_VideoDevice *_this,const char *path)
{
    if(path && *path)return SDL_SetError("PS5 uses its statically resident Vulkan ICD; explicit library path unsupported");
    PFN_vkVoidFunction enumerate=vkGetInstanceProcAddr(VK_NULL_HANDLE,"vkEnumerateInstanceExtensionProperties");
    if(!enumerate)return SDL_SetError("Resident ICD missing extension enumeration");
    _this->vulkan_config.vkGetInstanceProcAddr=(SDL_FunctionPointer)vkGetInstanceProcAddr;
    _this->vulkan_config.vkEnumerateInstanceExtensionProperties=(SDL_FunctionPointer)enumerate;
    _this->vulkan_config.loader_handle=NULL; /* A genuine static provider, no fabricated dlopen handle. */
    _this->vulkan_config.loader_path[0]=0;
    return true;
}
static void PS5_Vulkan_UnloadLibrary(SDL_VideoDevice *_this)
{
    _this->vulkan_config.vkGetInstanceProcAddr=NULL;
    _this->vulkan_config.vkEnumerateInstanceExtensionProperties=NULL;
}
static char const *const *PS5_Vulkan_GetInstanceExtensions(SDL_VideoDevice *_this,Uint32 *count)
{
    static const char *const extensions[]={VK_KHR_SURFACE_EXTENSION_NAME,VK_KHR_DISPLAY_EXTENSION_NAME};
    *count=SDL_arraysize(extensions);return extensions;
}
static int ps5_surface_width=1920,ps5_surface_height=1080;
static bool PS5_Vulkan_CreateSurface(SDL_VideoDevice *_this,SDL_Window *window,VkInstance instance,const VkAllocationCallbacks *allocator,VkSurfaceKHR *surface)
{
    (void)_this;*surface=VK_NULL_HANDLE;
#define LOAD(name) PFN_vk##name name=(PFN_vk##name)vkGetInstanceProcAddr(instance,"vk"#name)
    LOAD(EnumeratePhysicalDevices);LOAD(GetPhysicalDeviceDisplayPropertiesKHR);LOAD(GetDisplayModePropertiesKHR);
    LOAD(GetPhysicalDeviceDisplayPlanePropertiesKHR);LOAD(GetDisplayPlaneSupportedDisplaysKHR);LOAD(GetDisplayPlaneCapabilitiesKHR);LOAD(CreateDisplayPlaneSurfaceKHR);LOAD(GetPhysicalDeviceSurfaceCapabilitiesKHR);
#undef LOAD
    if(!EnumeratePhysicalDevices||!GetPhysicalDeviceDisplayPropertiesKHR||!GetDisplayModePropertiesKHR||!GetPhysicalDeviceDisplayPlanePropertiesKHR||!GetDisplayPlaneSupportedDisplaysKHR||!GetDisplayPlaneCapabilitiesKHR||!CreateDisplayPlaneSurfaceKHR)return SDL_SetError("PS5 Vulkan display entry points missing");
    uint32_t count=16;VkPhysicalDevice devices[16];
    if(EnumeratePhysicalDevices(instance,&count,devices)!=VK_SUCCESS||!count||count>16)return SDL_SetError("PS5 Vulkan physical-device inventory failed");
    VkDisplayPropertiesKHR displays[16];count=16;
    if(GetPhysicalDeviceDisplayPropertiesKHR(devices[0],&count,displays)!=VK_SUCCESS||!count||count>16)return SDL_SetError("PS5 Vulkan display inventory failed");
    VkDisplayModePropertiesKHR modes[32];count=32;
    if(GetDisplayModePropertiesKHR(devices[0],displays[0].display,&count,modes)!=VK_SUCCESS||!count||count>32)return SDL_SetError("PS5 Vulkan mode inventory failed");
    int selected=PS5_SelectDisplayMode(modes,count,displays[0].physicalResolution);
    if(selected<0)return SDL_SetError("PS5 Vulkan no usable enumerated mode");
    /* Prefer the requested real display mode when the driver enumerates it.
     * Retain a usable physical mode otherwise; logical size remains independent. */
    if(window){int requested=PS5_SelectRequestedMode(modes,count,(uint32_t)window->w,(uint32_t)window->h);if(requested>=0)selected=requested;}
    SDL_Log("PS5 Vulkan surface creation: requested %dx%d selected %ux%u %.3fHz",window?window->w:0,window?window->h:0,modes[selected].parameters.visibleRegion.width,modes[selected].parameters.visibleRegion.height,modes[selected].parameters.refreshRate/1000.0);
    VkDisplayPlanePropertiesKHR planes[32];uint32_t plane_count=32;
    if(GetPhysicalDeviceDisplayPlanePropertiesKHR(devices[0],&plane_count,planes)!=VK_SUCCESS||!plane_count||plane_count>32)return SDL_SetError("PS5 Vulkan plane inventory failed");
    for(uint32_t plane=0;plane<plane_count;plane++){
        VkDisplayKHR supported[16];uint32_t supported_count=16;
        if(GetDisplayPlaneSupportedDisplaysKHR(devices[0],plane,&supported_count,supported)!=VK_SUCCESS||supported_count>16)continue;
        bool match=false;for(uint32_t i=0;i<supported_count;i++)if(supported[i]==displays[0].display)match=true;
        if(!match)continue;
        VkDisplayPlaneCapabilitiesKHR caps;
        if(GetDisplayPlaneCapabilitiesKHR(devices[0],modes[selected].displayMode,plane,&caps)!=VK_SUCCESS||!(caps.supportedAlpha&VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR)||!(displays[0].supportedTransforms&VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR))continue;
        VkExtent2D extent=modes[selected].parameters.visibleRegion;
        if(extent.width<caps.minSrcExtent.width||extent.width>caps.maxSrcExtent.width||extent.height<caps.minSrcExtent.height||extent.height>caps.maxSrcExtent.height||extent.width<caps.minDstExtent.width||extent.width>caps.maxDstExtent.width||extent.height<caps.minDstExtent.height||extent.height>caps.maxDstExtent.height)continue;
        VkDisplaySurfaceCreateInfoKHR ci={.sType=VK_STRUCTURE_TYPE_DISPLAY_SURFACE_CREATE_INFO_KHR,.displayMode=modes[selected].displayMode,.planeIndex=plane,.planeStackIndex=planes[plane].currentStackIndex,.transform=VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR,.globalAlpha=1.0f,.alphaMode=VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR,.imageExtent=extent};
        VkResult result=CreateDisplayPlaneSurfaceKHR(instance,&ci,allocator,surface);
        if(result==VK_SUCCESS){ps5_surface_width=(int)extent.width;ps5_surface_height=(int)extent.height;if(window)SDL_SendWindowEvent(window,SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED,ps5_surface_width,ps5_surface_height);}
        SDL_Log("PS5 Vulkan surface: %ux%u %.3fHz plane%u result%d",extent.width,extent.height,modes[selected].parameters.refreshRate/1000.0,plane,result);
        if(result!=VK_SUCCESS)return SDL_SetError("PS5 Vulkan display surface failed:%d",result);
        if(GetPhysicalDeviceSurfaceCapabilitiesKHR){VkSurfaceCapabilitiesKHR actual;result=GetPhysicalDeviceSurfaceCapabilitiesKHR(devices[0],*surface,&actual);if(result==VK_SUCCESS)SDL_Log("PS5 Vulkan surface caps: extent%ux%u images%u-%u usage0x%x",actual.currentExtent.width,actual.currentExtent.height,actual.minImageCount,actual.maxImageCount,actual.supportedUsageFlags);}
        return true;
    }
    return SDL_SetError("PS5 Vulkan no compatible display plane");
}
static void PS5_Vulkan_DestroySurface(SDL_VideoDevice *_this,VkInstance instance,VkSurfaceKHR surface,const VkAllocationCallbacks *allocator)
{
    SDL_Vulkan_DestroySurface_Internal((void*)_this->vulkan_config.vkGetInstanceProcAddr,instance,surface,allocator);
}
static bool PS5_Vulkan_GetPresentationSupport(SDL_VideoDevice *_this,VkInstance instance,VkPhysicalDevice physical,Uint32 family)
{
    VkSurfaceKHR surface=VK_NULL_HANDLE;VkBool32 supported=VK_FALSE;
    if(!PS5_Vulkan_CreateSurface(_this,NULL,instance,NULL,&surface))return false;
    PFN_vkGetPhysicalDeviceSurfaceSupportKHR query=(PFN_vkGetPhysicalDeviceSurfaceSupportKHR)vkGetInstanceProcAddr(instance,"vkGetPhysicalDeviceSurfaceSupportKHR");
    VkResult result=query?query(physical,family,surface,&supported):VK_ERROR_EXTENSION_NOT_PRESENT;
    PS5_Vulkan_DestroySurface(_this,instance,surface,NULL);
    if(result!=VK_SUCCESS)return SDL_SetError("PS5 Vulkan presentation query failed: %d",result);
    return supported==VK_TRUE;
}
static bool PS5_QueryDisplay(SDL_DisplayMode *mode)
{
    const char *extensions[]={VK_KHR_SURFACE_EXTENSION_NAME,VK_KHR_DISPLAY_EXTENSION_NAME};
    VkApplicationInfo app={.sType=VK_STRUCTURE_TYPE_APPLICATION_INFO,.pApplicationName="SDL PS5 display query",.apiVersion=VK_API_VERSION_1_1};
    VkInstanceCreateInfo ci={.sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,.pApplicationInfo=&app,.enabledExtensionCount=2,.ppEnabledExtensionNames=extensions};
    PFN_vkCreateInstance create=(PFN_vkCreateInstance)vkGetInstanceProcAddr(VK_NULL_HANDLE,"vkCreateInstance");VkInstance instance=VK_NULL_HANDLE;
    VkResult result=create?create(&ci,NULL,&instance):VK_ERROR_INITIALIZATION_FAILED;
    if(result!=VK_SUCCESS)return SDL_SetError("SDL PS5 display instance failed: %d",result);
#define LOAD(name) PFN_vk##name name=(PFN_vk##name)vkGetInstanceProcAddr(instance,"vk"#name)
    LOAD(DestroyInstance);LOAD(EnumeratePhysicalDevices);LOAD(GetPhysicalDeviceDisplayPropertiesKHR);LOAD(GetDisplayModePropertiesKHR);
#undef LOAD
    bool ok=false;uint32_t count=16;VkPhysicalDevice devices[16];
    if(!DestroyInstance||!EnumeratePhysicalDevices||!GetPhysicalDeviceDisplayPropertiesKHR||!GetDisplayModePropertiesKHR)goto done;
    if(EnumeratePhysicalDevices(instance,&count,devices)!=VK_SUCCESS||count<1||count>16)goto done;
    VkDisplayPropertiesKHR displays[16];count=16;
    if(GetPhysicalDeviceDisplayPropertiesKHR(devices[0],&count,displays)!=VK_SUCCESS||count<1||count>16)goto done;
    VkDisplayModePropertiesKHR modes[32];count=32;
    if(GetDisplayModePropertiesKHR(devices[0],displays[0].display,&count,modes)!=VK_SUCCESS||count<1||count>32)goto done;
    int selected=PS5_SelectDisplayMode(modes,count,displays[0].physicalResolution);
    if(selected<0)goto done;
    SDL_Log("PS5 SDL display: selected enumerated %ux%u %.3fHz (advertised native %ux%u)",modes[selected].parameters.visibleRegion.width,modes[selected].parameters.visibleRegion.height,modes[selected].parameters.refreshRate/1000.0,displays[0].physicalResolution.width,displays[0].physicalResolution.height);
    SDL_zero(*mode);mode->format=SDL_PIXELFORMAT_BGRA32;mode->w=(int)modes[selected].parameters.visibleRegion.width;mode->h=(int)modes[selected].parameters.visibleRegion.height;mode->refresh_rate=modes[selected].parameters.refreshRate/1000.0f;ok=true;
done:
    if(DestroyInstance)DestroyInstance(instance,NULL);
    if(!ok)return SDL_SetError("SDL PS5 display inventory/mode query failed");
    return true;
}

static bool PS5_VideoInit(SDL_VideoDevice *_this)
{
    PS5_BOUNDARY("PS5 SDL video driver init enter");
    SDL_DisplayMode mode;
    if(!PS5_QueryDisplay(&mode))return false;
    PS5_BOUNDARY("PS5 SDL display query returned success");
    SDL_GetMouse()->SetRelativeMouseMode=PS5_SetRelativeMouseMode;
    PS5_BOUNDARY("PS5 SDL add display enter");
    bool added=SDL_AddBasicVideoDisplay(&mode)!=0;
    PS5_BOUNDARY("PS5 SDL add display returned");
    return added;
}

static void PS5_VideoQuit(SDL_VideoDevice *_this)
{
    PS5_TempRelease(SDL_GetKeyboardFocus(),SDL_GetTicksNS());
    PS5_USBClose(SDL_GetKeyboardFocus());
}

static void PS5_PumpEvents(SDL_VideoDevice *_this)
{
    PS5_PumpTemporaryInput(SDL_GetKeyboardFocus());
    PS5_PumpUSBInput(SDL_GetKeyboardFocus());
    PS5_TraceInputHandoff(SDL_GetKeyboardFocus());
}

static bool PS5_CreateWindow(SDL_VideoDevice *_this, SDL_Window *window, SDL_PropertiesID props)
{
    /* Logical input/window coordinates are independent of the real scanout.
     * GetWindowSizeInPixels reports the actual Vulkan surface extent below. */
    window->min_w=320;window->min_h=240;window->max_w=7680;window->max_h=4320;
    /* The window is the screen, and always has the pad's focus */
    SDL_SetKeyboardFocus(window);
    return true;
}

static bool PS5_SetWindowPosition(SDL_VideoDevice *_this, SDL_Window *window)
{
    return true;
}

static void PS5_SetWindowSize(SDL_VideoDevice *_this, SDL_Window *window)
{
    SDL_SendWindowEvent(window,SDL_EVENT_WINDOW_RESIZED,window->pending.w,window->pending.h);
}

static void PS5_GetWindowSizeInPixels(SDL_VideoDevice *_this,SDL_Window *window,int *w,int *h)
{
    (void)_this;(void)window;*w=ps5_surface_width;*h=ps5_surface_height;
}

static SDL_FullscreenResult PS5_SetWindowFullscreen(SDL_VideoDevice *_this, SDL_Window *window, SDL_VideoDisplay *display, SDL_FullscreenOp fullscreen)
{
    return SDL_FULLSCREEN_SUCCEEDED;
}

static void PS5_DeleteDevice(SDL_VideoDevice *device)
{
    SDL_free(device);
}

static SDL_VideoDevice *PS5_CreateDevice(void)
{
    SDL_VideoDevice *device = (SDL_VideoDevice *)SDL_calloc(1, sizeof(SDL_VideoDevice));
    if (!device) {
        return NULL;
    }
    device->Vulkan_LoadLibrary=PS5_Vulkan_LoadLibrary;
    device->Vulkan_UnloadLibrary=PS5_Vulkan_UnloadLibrary;
    device->Vulkan_GetInstanceExtensions=PS5_Vulkan_GetInstanceExtensions;
    device->Vulkan_CreateSurface=PS5_Vulkan_CreateSurface;
    device->Vulkan_DestroySurface=PS5_Vulkan_DestroySurface;
    device->Vulkan_GetPresentationSupport=PS5_Vulkan_GetPresentationSupport;
    device->VideoInit = PS5_VideoInit;
    device->VideoQuit = PS5_VideoQuit;
    device->PumpEvents = PS5_PumpEvents;
    device->CreateSDLWindow = PS5_CreateWindow;
    device->SetWindowPosition = PS5_SetWindowPosition;
    device->SetWindowSize = PS5_SetWindowSize;
    device->GetWindowSizeInPixels=PS5_GetWindowSizeInPixels;
    device->SetWindowFullscreen = PS5_SetWindowFullscreen;
    device->free = PS5_DeleteDevice;
    device->device_caps = VIDEO_DEVICE_CAPS_FULLSCREEN_ONLY;
    return device;
}

VideoBootStrap PS5_bootstrap = {
    "ps5", "PlayStation 5 video driver",
    PS5_CreateDevice,
    NULL, // no ShowMessageBox implementation
    false
};

#endif // SDL_VIDEO_DRIVER_PS5
