/* SPDX-License-Identifier: BSD-3-Clause */
#include "common_tools.h"

/* Constant-time shutdown flag, analogous to current upstream's native upcalls.
 * No allocator, VM policy or game callback replacement. */
JNIEXPORT void JNICALL Java_prosperocraft_lwjgl331_Bootstrap_beginShutdown(JNIEnv* env, jclass cls) {
    UNUSED_PARAMS(env, cls)
    ps5_lwjgl331_begin_shutdown();
}
JNIEXPORT jint JNICALL Java_prosperocraft_lwjgl331_Bootstrap_nativeInterfaceSize(JNIEnv* env, jclass cls) {
    UNUSED_PARAM(cls)
    return sizeof(**env) / sizeof(void*);
}

JNIEXPORT jint JNICALL Java_prosperocraft_lwjgl331_Bootstrap_nativeGetVersion(JNIEnv* env, jclass cls) {
    UNUSED_PARAM(cls)
    return (*env)->GetVersion(env);
}
