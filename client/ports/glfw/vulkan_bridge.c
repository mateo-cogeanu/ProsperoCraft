/* SPDX-License-Identifier: Zlib */
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>
void ps5glfw_extensions(char** out){
 Uint32 count=0;const char*const* names=SDL_Vulkan_GetInstanceExtensions(&count);
 if(!names||count!=2){SDL_SetError("PS5 GLFW requires the two SDL surface extensions");return;}
 for(Uint32 i=0;i<count;i++)out[i]=(char*)names[i];
}
int ps5glfw_presentation(void* i,void* p,uint32_t q){return SDL_Vulkan_GetPresentationSupport((VkInstance)i,(VkPhysicalDevice)p,q);}
int32_t ps5glfw_surface(void* i,SDL_Window* w,const void* a,uint64_t* out){
 VkSurfaceKHR surface=VK_NULL_HANDLE;
 if(!SDL_Vulkan_CreateSurface(w,(VkInstance)i,(const VkAllocationCallbacks*)a,&surface))return VK_ERROR_INITIALIZATION_FAILED;
 *out=(uint64_t)surface;return VK_SUCCESS;
}

int ps5glfw_vulkan_load(void){
#ifdef PS5_GLFW_HOST_TEST
 return 1;
#else
 return SDL_Vulkan_LoadLibrary(NULL);
#endif
}
void ps5glfw_vulkan_unload(void){
#ifndef PS5_GLFW_HOST_TEST
 SDL_Vulkan_UnloadLibrary();
#endif
}
