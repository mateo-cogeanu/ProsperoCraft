/* SPDX-License-Identifier: GPL-3.0-or-later
 * Explicit retained dependency constructors, invoked by actual resident JNI load.
 * Never run them before the bootstrap has created the VM.
 */
#include <jni.h>
#include <stdint.h>
typedef void (*Initializer)(void);
extern Initializer __client_shaderc_init_start[],__client_shaderc_init_end[];
extern void client_gpu_stage(const char*,int);
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*vm,void*reserved){
 (void)vm;(void)reserved;
 static int initialized;
 if(!initialized){
  for(Initializer*p=__client_shaderc_init_start;p!=__client_shaderc_init_end;++p)if(*p)(*p)();
  initialized=1;client_gpu_stage("Actual shaderc/glslang retained constructors initialized",0);
 }
 return JNI_VERSION_1_8;
}

/* Observational boundary: actual compiler entry is renamed only to forward
 * here, with identical arguments/result and no success substitution. */
extern void* ps5shaderc_real_compiler_initialize(void);
extern void ps5_cpp_mutex_trace_enable(void) __attribute__((weak));
void* shaderc_compiler_initialize(void){
 if(ps5_cpp_mutex_trace_enable)ps5_cpp_mutex_trace_enable();
 client_gpu_stage("ENTER actual native shaderc_compiler_initialize",INT32_MIN);
 void* compiler=ps5shaderc_real_compiler_initialize();
 client_gpu_stage("RETURN actual native shaderc_compiler_initialize",compiler?0:-1);
 return compiler;
}
