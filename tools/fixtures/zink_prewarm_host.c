/* SPDX-License-Identifier: MIT */
#include "frontend.h"
#include <stdio.h>
#include <stdlib.h>
/* Injected into the genuine Java executable by the explicit host-only test.
 * Dyld runs this before launcher main/JNI_CreateJavaVM; no target shim is built. */
__attribute__((constructor)) static void prepare_before_java(void)
{
 fprintf(stderr,"HOST_ZINK pre-JVM screen preparation enter\n");
 if(!ps5zink_prepare_screen()){fprintf(stderr,"HOST_ZINK preparation failed error=%d\n",ps5zink_error());abort();}
 fprintf(stderr,"HOST_ZINK pre-JVM screen preparation complete\n");
}
