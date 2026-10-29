/* SPDX-License-Identifier: GPL-3.0-or-later
 * Explicit unavailable-desktop-dialog backend for original LWJGL tinyfd JNI.
 * Normal Minecraft menus remain in-game. No shell, blocking console prompt,
 * fabricated file path, accepted dialog or upstream TinyFD version is returned.
 */
#include <jni.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static const char version[]="ProsperoCraft PS5 dialog adapter 1; desktop dialogs unavailable";
static const char needs[]="PS5 native desktop dialog service unavailable";
static const char empty[]="";
static void unavailable(const char* operation){fprintf(stderr,"PS5_DIALOG unavailable operation=%s; returning cancel\n",operation);}
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm,void* reserved){(void)vm;(void)reserved;return JNI_VERSION_1_8;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1getGlobalChar(JNIEnv* env,jclass type,jlong name){(void)env;(void)type;const char* key=(const char*)(uintptr_t)name;if(!key)return 0;if(!strcmp(key,"tinyfd_version"))return (jlong)(uintptr_t)version;if(!strcmp(key,"tinyfd_needs"))return (jlong)(uintptr_t)needs;if(!strcmp(key,"tinyfd_response"))return (jlong)(uintptr_t)empty;return 0;}
JNIEXPORT jint JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1getGlobalInt(JNIEnv* e,jclass c,jlong n){(void)e;(void)c;(void)n;return -1;}
JNIEXPORT jint JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1setGlobalInt(JNIEnv* e,jclass c,jlong n,jint v){(void)e;(void)c;(void)n;(void)v;return -1;}
JNIEXPORT void JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_tinyfd_1beep(JNIEnv* e,jclass c){(void)e;(void)c;unavailable("beep");}
JNIEXPORT jint JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1notifyPopup(JNIEnv* e,jclass c,jlong t,jlong m,jlong i){(void)e;(void)c;(void)t;(void)m;(void)i;unavailable("notifyPopup");return 0;}
JNIEXPORT jint JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1messageBox(JNIEnv* e,jclass c,jlong t,jlong m,jlong d,jlong i,jint v){(void)e;(void)c;(void)t;(void)m;(void)d;(void)i;(void)v;unavailable("messageBox");return 0;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1inputBox(JNIEnv* e,jclass c,jlong t,jlong m,jlong d){(void)e;(void)c;(void)t;(void)m;(void)d;unavailable("inputBox");return 0;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1saveFileDialog(JNIEnv* e,jclass c,jlong t,jlong p,jint n,jlong f,jlong d){(void)e;(void)c;(void)t;(void)p;(void)n;(void)f;(void)d;unavailable("saveFileDialog");return 0;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1openFileDialog(JNIEnv* e,jclass c,jlong t,jlong p,jint n,jlong f,jlong d,jint multi){(void)e;(void)c;(void)t;(void)p;(void)n;(void)f;(void)d;(void)multi;unavailable("openFileDialog");return 0;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1selectFolderDialog(JNIEnv* e,jclass c,jlong t,jlong p){(void)e;(void)c;(void)t;(void)p;unavailable("selectFolderDialog");return 0;}
JNIEXPORT jlong JNICALL Java_org_lwjgl_util_tinyfd_TinyFileDialogs_ntinyfd_1colorChooser(JNIEnv* e,jclass c,jlong t,jlong h,jlong d,jlong r){(void)e;(void)c;(void)t;(void)h;(void)d;(void)r;unavailable("colorChooser");return 0;}
