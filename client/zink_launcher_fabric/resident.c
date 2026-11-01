/* SPDX-License-Identifier: GPL-3.0-or-later
 * Only the genuine GL procedure resolver is exported by this resident group.
 * GLFW context operations bind directly to the same scoped frontend object.
 */
#include <jni.h>
extern void prospero_graphics_init(void);
extern void (*clientgpu_ps5zink_get_proc_address(const char *))(void);
__attribute__((visibility("default"))) void (*ps5zink_get_proc_address(const char *name))(void)
{return clientgpu_ps5zink_get_proc_address(name);}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm,void *reserved)
{(void)vm;(void)reserved;prospero_graphics_init();return JNI_VERSION_1_8;}
