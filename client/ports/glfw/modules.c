/* SPDX-License-Identifier: Zlib
 * No arbitrary module loading. Vulkan uses glfwInitVulkanLoader with the
 * existing resident ICD; OpenGL context creation is explicitly unavailable.
 */
#include "internal.h"
void* _glfwPlatformLoadModule(const char* path){(void)path;return NULL;}
void _glfwPlatformFreeModule(void* module){(void)module;}
GLFWproc _glfwPlatformGetModuleSymbol(void* module,const char* name){(void)module;(void)name;return NULL;}
int JNI_OnLoad(void* vm,void* reserved){(void)vm;(void)reserved;return 0x00010008;}
