/* SPDX-License-Identifier: GPL-3.0-or-later
 * Stage2a: actual GLFW/SDL + kopper presentation; no JVM or launcher handoff.
 */
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <GL/glcorearb.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
extern void zink_probe_report(const char *,int);
#ifndef PS5ZINK_CYCLE_MILLISECONDS
#define PS5ZINK_CYCLE_MILLISECONDS 4000
#endif
static unsigned errors;
static void error(int code,const char *description)
{
    char text[320];snprintf(text,sizeof(text),"GLFW error0x%x:%.256s",code,description?description:"");
    errors++;zink_probe_report(text,-1);
}
static int64_t milliseconds(void)
{
    struct timespec t;
    if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;
    return (int64_t)t.tv_sec*1000+t.tv_nsec/1000000;
}
#define CHECK(value,label) do {if(!(value)){zink_probe_report(label,-1);return -1;}}while(0)
#define LOAD(type,name) type name=(type)glfwGetProcAddress(#name);CHECK(name,#name)
int zink_present_run(void)
{
    glfwSetErrorCallback(error);
    for(unsigned cycle=0;cycle<3;cycle++){
        errors=0;glfwInitHint(GLFW_PLATFORM,GLFW_PLATFORM_NULL);
        zink_probe_report("Initialize real GLFW/SDL display inventory",INT32_MIN);
        CHECK(glfwInit(),"GLFW/SDL initialization");
        const GLFWvidmode *mode=glfwGetVideoMode(glfwGetPrimaryMonitor());
        CHECK(mode&&mode->width>0&&mode->height>0,"Real selected display mode");
        char note[512];snprintf(note,sizeof(note),"Cycle%u selected display %dx%d %dHz (configured inventory; not measured FPS)",cycle,mode->width,mode->height,mode->refreshRate);zink_probe_report(note,0);
        glfwDefaultWindowHints();glfwWindowHint(GLFW_CLIENT_API,GLFW_OPENGL_API);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
        glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT,GLFW_TRUE);
        GLFWwindow *window=glfwCreateWindow(mode->width,mode->height,"ProsperoCraft Zink182",NULL,NULL);
        CHECK(window,"Create actual GLFW Zink window");
        glfwMakeContextCurrent(window);CHECK(glfwGetCurrentContext()==window,"Actual GLFW current context");
        glfwSwapInterval(1);
        LOAD(PFNGLGETSTRINGPROC,glGetString);LOAD(PFNGLGETERRORPROC,glGetError);
        LOAD(PFNGLVIEWPORTPROC,glViewport);LOAD(PFNGLCLEARCOLORPROC,glClearColor);
        LOAD(PFNGLCLEARPROC,glClear);LOAD(PFNGLSCISSORPROC,glScissor);
        LOAD(PFNGLENABLEPROC,glEnable);LOAD(PFNGLDISABLEPROC,glDisable);
        LOAD(PFNGLFINISHPROC,glFinish);LOAD(PFNGLREADPIXELSPROC,glReadPixels);
        const char *version=(const char*)glGetString(GL_VERSION),*renderer=(const char*)glGetString(GL_RENDERER);
        CHECK(version&&renderer&&strstr(renderer,"zink"),"Genuine Zink renderer");
        snprintf(note,sizeof(note),"Cycle%u GL_VERSION=%.128s GL_RENDERER=%.256s",cycle,version,renderer);zink_probe_report(note,0);
        zink_probe_report("First-frame monotonic clock enter",INT32_MIN);
        int64_t start=milliseconds(),now=start;unsigned frames=0;
        CHECK(start>=0,"Monotonic animation clock");
        while(now-start<PS5ZINK_CYCLE_MILLISECONDS){
            int width=0,height=0;
#define FIRST(label) do {if(frames==0)zink_probe_report(label,INT32_MIN);}while(0)
            FIRST("First-frame glfwPollEvents enter");glfwPollEvents();
            FIRST("First-frame glfwPollEvents returned; framebuffer size enter");
            glfwGetFramebufferSize(window,&width,&height);
            FIRST("First-frame framebuffer size returned; viewport enter");
            CHECK(width>=320&&height>=240,"Bounded actual drawable size");
            glViewport(0,0,width,height);glDisable(GL_SCISSOR_TEST);
            FIRST("First-frame viewport/disable returned");
            float phase=(float)(now-start)/(float)PS5ZINK_CYCLE_MILLISECONDS;
            unsigned color=(unsigned)(phase*3);if(color>2)color=2;
            FIRST("First-frame base clear enter");
            glClearColor(color==0?0.7f:0.05f,color==1?0.7f:0.05f,color==2?0.7f:0.05f,1);glClear(GL_COLOR_BUFFER_BIT);
            FIRST("First-frame base clear returned; scissor clear enter");
            glEnable(GL_SCISSOR_TEST);glScissor((int)(phase*(width-width/12)),0,width/12,height);
            glClearColor(1,1,1,1);glClear(GL_COLOR_BUFFER_BIT);glDisable(GL_SCISSOR_TEST);
            FIRST("First-frame scissor clear returned; GL error query enter");
            CHECK(glGetError()==GL_NO_ERROR,"Actual animation GL commands");
            if(frames==0){
                /* Read only one pixel with guards: no full-frame CPU presentation copy. */
                unsigned char pixel[132];memset(pixel,0xa5,sizeof(pixel));
                FIRST("First-frame glReadPixels enter");
                glReadPixels(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel+64);FIRST("First-frame glReadPixels returned; glFinish enter");glFinish();
                FIRST("First-frame glFinish returned");
                CHECK(glGetError()==GL_NO_ERROR&&pixel[64]==255&&pixel[65]==255&&pixel[66]==255&&pixel[67]==255,"Real rendered framebuffer pixel readback");
                for(unsigned i=0;i<64;i++)CHECK(pixel[i]==0xa5&&pixel[68+i]==0xa5,"Single-pixel readback guards");
            }
            FIRST("First-frame glfwSwapBuffers enter");
            glfwSwapBuffers(window);FIRST("First-frame glfwSwapBuffers returned");CHECK(errors==0,"Actual GLFW/kopper swap");
            frames++;now=milliseconds();CHECK(now>=start,"Animation clock progressed");
        }
        CHECK(frames>1,"Multiple real swaps completed");
        glFinish();CHECK(glGetError()==GL_NO_ERROR,"Final GPU work complete");
        snprintf(note,sizeof(note),"Cycle%u completed %u swaps in %lldms; visible animation requires human confirmation",cycle,frames,(long long)(now-start));zink_probe_report(note,0);
        glfwMakeContextCurrent(NULL);CHECK(glfwGetCurrentContext()==NULL&&errors==0,"Unbind GLFW context");
        glfwDestroyWindow(window);CHECK(errors==0,"Destroy context/swapchain/surface/window");
        glfwTerminate();CHECK(errors==0,"Terminate actual GLFW/SDL video subsystem");
        zink_probe_report("Cycle complete: real GLFW/SDL teardown; next cycle must reacquire display",0);
    }
    zink_probe_report("Native presentation cycles complete; full Java launcher handoff remains untested",0);
    return 0;
}
