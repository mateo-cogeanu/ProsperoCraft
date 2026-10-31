/* SPDX-License-Identifier: GPL-3.0-or-later
 * Console stage 1: real RADV/Zink GL context/readback/destruction, no game/WSI.
 */
#include "../ports/zink/frontend.h"
#include <GL/glcorearb.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void zink_probe_report(const char *, int);
#define CHECK(value, label) do { if (!(value)) { zink_probe_report(label, -1); return -1; } } while (0)
#define LOAD(type, name) type name = (type)ps5zink_get_proc_address(#name); CHECK(name, #name)
int zink_probe_run(void)
{
    for (unsigned cycle = 0; cycle < 3; cycle++) {
        struct ps5zink_config config = {.width=8,.height=8,.major=3,.minor=3,.core=1,.forward=1};
        zink_probe_report("Create real Zink context on the single resident RADV", INT32_MIN);
        struct ps5zink_context *context = ps5zink_create(&config);
        if (!context) { zink_probe_report("Context creation refused", ps5zink_error()); return -1; }
        if (!ps5zink_make_current(context)) { zink_probe_report("Make-current refused; context retained", ps5zink_error()); return -1; }
        LOAD(PFNGLGETSTRINGPROC, glGetString);
        LOAD(PFNGLGETINTEGERVPROC, glGetIntegerv);
        LOAD(PFNGLCLEARCOLORPROC, glClearColor);
        LOAD(PFNGLCLEARPROC, glClear);
        LOAD(PFNGLREADPIXELSPROC, glReadPixels);
        LOAD(PFNGLFINISHPROC, glFinish);
        LOAD(PFNGLGETERRORPROC, glGetError);
        const char *version=(const char*)glGetString(GL_VERSION), *renderer=(const char*)glGetString(GL_RENDERER);
        CHECK(version && renderer && strstr(renderer,"zink"), "Real Zink renderer string");
        int major=0,minor=0;glGetIntegerv(GL_MAJOR_VERSION,&major);glGetIntegerv(GL_MINOR_VERSION,&minor);
        CHECK(major>3 || (major==3 && minor>=3), "Actual GL 3.3+ version");
        char message[768];snprintf(message,sizeof(message),"Cycle%u GL_VERSION=%.192s GL_RENDERER=%.384s",cycle,version,renderer);
        zink_probe_report(message,0);
        unsigned char data[8*8*4+128];memset(data,0xa5,sizeof(data));
        const float r=cycle==0?1:0,g=cycle==1?1:0,b=cycle==2?1:0;
        glClearColor(r,g,b,1);glClear(GL_COLOR_BUFFER_BIT);
        glReadPixels(0,0,8,8,GL_RGBA,GL_UNSIGNED_BYTE,data+64);glFinish();
        CHECK(glGetError()==GL_NO_ERROR,"Real GPU clear/readback completed without GL error");
        for(unsigned i=0;i<64;i++) CHECK(data[i]==0xa5 && data[320+i]==0xa5,"Readback guard bytes");
        for(unsigned i=0;i<64;i++) {
            CHECK(data[64+4*i]==(cycle==0?255:0) && data[65+4*i]==(cycle==1?255:0) &&
                  data[66+4*i]==(cycle==2?255:0) && data[67+4*i]==255,"Actual RGBA pixels");
        }
        zink_probe_report("64 actual RGBA pixels and 128 guard bytes match",0);
        CHECK(ps5zink_make_current(NULL),"Unbind actual GL context");
        zink_probe_report("Destroy context and its final Zink screen/device/instance",INT32_MIN);
        CHECK(ps5zink_destroy(context),"Actual context/screen destruction");
        zink_probe_report("Context/readback/destruction cycle complete",0);
    }
    return 0;
}
