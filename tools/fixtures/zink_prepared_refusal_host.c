/* SPDX-License-Identifier: MIT */
#include "frontend.h"
#include <GL/glcorearb.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL prepared-refusal line=%d error=%d\n",__LINE__,ps5zink_error());abort();}}while(0)
int main(void)
{
 CHECK(setenv("MESA_GL_VERSION_OVERRIDE","3.3",1)==0);
 CHECK(ps5zink_prepare_screen());
 struct ps5zink_config c={.width=4,.height=4,.major=4,.minor=6,.core=1,.forward=1};
 CHECK(!ps5zink_create(&c));CHECK(ps5zink_error()==ENOTSUP);
 c.major=3;c.minor=3;
 struct ps5zink_context*ctx=ps5zink_create(&c);CHECK(ctx);CHECK(ps5zink_make_current(ctx));
 PFNGLCLEARCOLORPROC clearColor=(void*)ps5zink_get_proc_address("glClearColor");
 PFNGLCLEARPROC clear=(void*)ps5zink_get_proc_address("glClear");
 PFNGLREADPIXELSPROC read=(void*)ps5zink_get_proc_address("glReadPixels");CHECK(clearColor&&clear&&read);
 unsigned char pixel[4]={0};clearColor(1,0,0,1);clear(GL_COLOR_BUFFER_BIT);read(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
 CHECK(pixel[0]==255&&pixel[1]==0&&pixel[2]==0&&pixel[3]==255);
 CHECK(ps5zink_destroy(ctx));CHECK(!ps5zink_get_current());
 puts("PASS real prepared screen retained after version refusal, retried, rendered and destroyed");return 0;
}
