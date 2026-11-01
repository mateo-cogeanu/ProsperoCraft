/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
static void checkpoint(JNIEnv*e,jclass c,jstring text){(void)c;const char*s=(*e)->GetStringUTFChars(e,text,0);if(s){puts(s);(*e)->ReleaseStringUTFChars(e,text,s);}}
static jboolean menu(JNIEnv*e,jclass c){(void)e;(void)c;const char*mode=getenv("ZINK_HANDOFF_HOST_MODE");return mode&&mode[0]=='p';}
static void snapshot(JNIEnv*e,jclass c,jlong a,jint b){(void)e;(void)c;(void)a;(void)b;}
static jobjectArray cpu(JNIEnv*e,jclass c){(void)e;(void)c;return 0;}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*vm,void*reserved){(void)reserved;JNIEnv*e=0;if((*vm)->GetEnv(vm,(void**)&e,JNI_VERSION_1_8)!=0)return JNI_ERR;jclass c=(*e)->FindClass(e,"ClientStartup25");if(!c)return JNI_ERR;
 JNINativeMethod methods[]={{"checkpoint","(Ljava/lang/String;)V",(void*)checkpoint},{"launcherMenu","()Z",(void*)menu},{"nativeSnapshot","(JI)V",(void*)snapshot},{"cpuInformation","()[Ljava/lang/String;",(void*)cpu}};
 return (*e)->RegisterNatives(e,c,methods,4)==0?JNI_VERSION_1_8:JNI_ERR;
}
