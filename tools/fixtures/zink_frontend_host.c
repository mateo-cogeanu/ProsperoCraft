/* SPDX-License-Identifier: MIT
 * Actual GL/Zink host execution, no game/native-driver substitutes.
 */
#include "frontend.h"
#include <GL/glcorearb.h>
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(value) do { if (!(value)) { fprintf(stderr,"FAIL line %d error %d\n",__LINE__,ps5zink_error()); abort(); } } while (0)
#define LOAD(type, name) type name = (type)ps5zink_get_proc_address(#name); CHECK(name)

static void pixels(void)
{
    LOAD(PFNGLGETSTRINGPROC, glGetString);
    LOAD(PFNGLCLEARCOLORPROC, glClearColor);
    LOAD(PFNGLCLEARPROC, glClear);
    LOAD(PFNGLREADPIXELSPROC, glReadPixels);
    LOAD(PFNGLGETERRORPROC, glGetError);
    unsigned char data[96];
    memset(data, 0xa5, sizeof(data));
    glClearColor(1,0,0,1); glClear(GL_COLOR_BUFFER_BIT);
    glReadPixels(0,0,4,4,GL_RGBA,GL_UNSIGNED_BYTE,data+16);
    for(unsigned i=0;i<16;i++) CHECK(data[i]==0xa5 && data[80+i]==0xa5);
    for(unsigned i=0;i<16;i++) CHECK(data[16+4*i]==255 && data[17+4*i]==0 && data[18+4*i]==0 && data[19+4*i]==255);
    CHECK(glGetError()==GL_NO_ERROR);
    CHECK(strstr((const char*)glGetString(GL_RENDERER),"zink")!=NULL);
}
static void draw(void)
{
    LOAD(PFNGLCREATESHADERPROC, glCreateShader);
    LOAD(PFNGLSHADERSOURCEPROC, glShaderSource);
    LOAD(PFNGLCOMPILESHADERPROC, glCompileShader);
    LOAD(PFNGLGETSHADERIVPROC, glGetShaderiv);
    LOAD(PFNGLGETSHADERINFOLOGPROC, glGetShaderInfoLog);
    LOAD(PFNGLCREATEPROGRAMPROC, glCreateProgram);
    LOAD(PFNGLATTACHSHADERPROC, glAttachShader);
    LOAD(PFNGLLINKPROGRAMPROC, glLinkProgram);
    LOAD(PFNGLGETPROGRAMIVPROC, glGetProgramiv);
    LOAD(PFNGLUSEPROGRAMPROC, glUseProgram);
    LOAD(PFNGLGENVERTEXARRAYSPROC, glGenVertexArrays);
    LOAD(PFNGLBINDVERTEXARRAYPROC, glBindVertexArray);
    LOAD(PFNGLVIEWPORTPROC, glViewport);
    LOAD(PFNGLDRAWARRAYSPROC, glDrawArrays);
    LOAD(PFNGLREADPIXELSPROC, glReadPixels);
    LOAD(PFNGLGETERRORPROC, glGetError);
    LOAD(PFNGLDELETEVERTEXARRAYSPROC, glDeleteVertexArrays);
    LOAD(PFNGLDELETEPROGRAMPROC, glDeleteProgram);
    LOAD(PFNGLDELETESHADERPROC, glDeleteShader);
    const char *vertex="#version 330 core\nconst vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));void main(){gl_Position=vec4(p[gl_VertexID],0,1);}";
    const char *fragment="#version 330 core\nout vec4 color;void main(){color=vec4(0,1,0,1);}";
    GLuint vs=glCreateShader(GL_VERTEX_SHADER),fs=glCreateShader(GL_FRAGMENT_SHADER),program=glCreateProgram(),vao;
    glShaderSource(vs,1,&vertex,NULL); glCompileShader(vs);
    glShaderSource(fs,1,&fragment,NULL); glCompileShader(fs);
    GLint ok=0;
    glGetShaderiv(vs,GL_COMPILE_STATUS,&ok);
    if(!ok){char log[1024];glGetShaderInfoLog(vs,sizeof(log),NULL,log);fprintf(stderr,"%s\n",log);} CHECK(ok);
    glGetShaderiv(fs,GL_COMPILE_STATUS,&ok); CHECK(ok);
    glAttachShader(program,vs);glAttachShader(program,fs);glLinkProgram(program);
    glGetProgramiv(program,GL_LINK_STATUS,&ok);CHECK(ok);
    glGenVertexArrays(1,&vao);glBindVertexArray(vao);glUseProgram(program);glViewport(0,0,4,4);
    glDrawArrays(GL_TRIANGLES,0,3);
    unsigned char data[96];memset(data,0xa5,sizeof(data));
    glReadPixels(0,0,4,4,GL_RGBA,GL_UNSIGNED_BYTE,data+16);
    for(unsigned i=0;i<16;i++)CHECK(data[i]==0xa5&&data[80+i]==0xa5);
    for(unsigned i=0;i<16;i++)CHECK(data[16+4*i]==0&&data[17+4*i]==255&&data[18+4*i]==0&&data[19+4*i]==255);
    glUseProgram(0);glDeleteVertexArrays(1,&vao);glDeleteProgram(program);glDeleteShader(vs);glDeleteShader(fs);
    CHECK(glGetError()==GL_NO_ERROR);
}
struct worker { struct ps5zink_context *context; int blocked; };
static void *thread(void *arg)
{
    struct worker *w=arg;
    CHECK(!ps5zink_get_current());
    if(w->blocked){CHECK(!ps5zink_make_current(w->context));CHECK(ps5zink_error()==EBUSY);CHECK(!ps5zink_destroy(w->context));}
    else {CHECK(ps5zink_make_current(w->context));pixels();draw();CHECK(ps5zink_make_current(NULL));}
    return NULL;
}
static unsigned surface_attempts;
static int32_t refused_surface(void *instance, void *window, uint64_t *surface)
{
    CHECK(instance && window && surface); *surface=0; surface_attempts++;
    return -3; /* Real failure injection, never a successful/faked surface. */
}
int main(void)
{
    CHECK(!ps5zink_create(NULL));CHECK(ps5zink_error()==EINVAL);
    CHECK(!ps5zink_get_proc_address(NULL));CHECK(!ps5zink_swap_buffers(NULL));
    struct ps5zink_config rejected={.width=8,.height=8,.major=3,.minor=3,.core=1,.window=(void*)1,.create_surface=refused_surface};
    struct ps5zink_context *failed=ps5zink_create(&rejected);CHECK(failed);
    CHECK(!ps5zink_make_current(failed));CHECK(surface_attempts==1);CHECK(!ps5zink_get_current());CHECK(ps5zink_destroy(failed));
    for(unsigned cycle=0;cycle<3;cycle++){
        struct ps5zink_config config={.width=8,.height=8,.major=3,.minor=3,.core=1,.forward=1};
        struct ps5zink_context *c=ps5zink_create(&config);CHECK(c);
        CHECK(ps5zink_make_current(c));CHECK(ps5zink_get_current()==c);
        LOAD(PFNGLGETSTRINGPROC, glGetString);
        printf("Actual GL %s / %s\n",glGetString(GL_VERSION),glGetString(GL_RENDERER));fflush(stdout);
        pixels();draw();CHECK(ps5zink_swap_interval(c,0));CHECK(ps5zink_swap_buffers(c));
        CHECK(!ps5zink_resize(c,0,4));CHECK(ps5zink_resize(c,4,4));pixels();
        pthread_t worker;struct worker state={c,1};CHECK(!pthread_create(&worker,NULL,thread,&state));CHECK(!pthread_join(worker,NULL));
        CHECK(ps5zink_get_current()==c);CHECK(ps5zink_make_current(NULL));
        state.blocked=0;CHECK(!pthread_create(&worker,NULL,thread,&state));CHECK(!pthread_join(worker,NULL));
        CHECK(ps5zink_destroy(c));CHECK(!ps5zink_destroy(c));
        puts("PASS real Zink clear/draw/guard/readback, resize, thread ownership/transfer and destroy cycle");fflush(stdout);
    }
    return 0;
}
