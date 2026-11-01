/* SPDX-License-Identifier: GPL-3.0-or-later
 * Host-only canonical-name boundary forwarding to real native libraries.
 * Matches PS5 registry basename policy; never compiled into the PS5 title.
 */
#include <jni.h>
#include <dlfcn.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
extern jlong Java_org_lwjgl_system_ps5_PS5Library_nOpen(JNIEnv*,jclass,jstring);
extern jlong Java_org_lwjgl_system_ps5_PS5Library_nFind(JNIEnv*,jclass,jlong,jstring);
extern jint Java_org_lwjgl_system_ps5_PS5Library_nClose(JNIEnv*,jclass,jlong);
void *__dlopen(const char *path,int flags){
 if(!path)return NULL;
 const char *slash=strrchr(path,'/'),*name=slash?slash+1:path;
 const char *known[]={"libps5clientgpu.so","libps5glfw.so","libps5zink.so","liblwjgl_opengl.so"};
 for(unsigned i=0;i<sizeof(known)/sizeof(known[0]);i++)if(strcmp(name,known[i])==0)return dlopen(name,flags);
 fprintf(stderr,"STRICT_RESIDENT rejected noncanonical/unknown name\n");return NULL;
}
void *__dlsym(void *handle,const char *name){return dlsym(handle,name);}
int __dlclose(void *handle){return dlclose(handle);}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*vm,void*unused){
 (void)unused;JNIEnv*e=NULL;if((*vm)->GetEnv(vm,(void**)&e,JNI_VERSION_1_8)!=0)return JNI_ERR;
 jclass c=(*e)->FindClass(e,"org/lwjgl/system/ps5/PS5Library");if(!c)return JNI_ERR;
 JNINativeMethod methods[]={
  {"nOpen","(Ljava/lang/String;)J",(void*)Java_org_lwjgl_system_ps5_PS5Library_nOpen},
  {"nFind","(JLjava/lang/String;)J",(void*)Java_org_lwjgl_system_ps5_PS5Library_nFind},
  {"nClose","(J)I",(void*)Java_org_lwjgl_system_ps5_PS5Library_nClose}};
 return (*e)->RegisterNatives(e,c,methods,3)==0?JNI_VERSION_1_8:JNI_ERR;
}
