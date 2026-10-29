/* SPDX-License-Identifier: Zlib
 * Consumer graphics allocation pairing. Mesa and graphics-native callers use
 * the same resident heap for duplicated strings as for malloc/realloc/free.
 * General libc and JVM references are not rebound.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
extern void *clientgpu___wrap_malloc(size_t);
static char *copy_string(const char *source,size_t length)
{
    if(length==SIZE_MAX){errno=ENOMEM;return NULL;}
    char *copy=clientgpu___wrap_malloc(length+1);
    if(!copy){errno=ENOMEM;return NULL;}
    memcpy(copy,source,length);copy[length]='\0';return copy;
}
char *clientgpu_strdup(const char *source)
{
    return copy_string(source,strlen(source));
}
char *clientgpu_strndup(const char *source,size_t limit)
{
    size_t length=0;
    while(length<limit && source[length])++length;
    return copy_string(source,length);
}
