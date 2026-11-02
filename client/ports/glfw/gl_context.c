/* SPDX-License-Identifier: Zlib
 * Genuine GLFW context hooks backed by the optional real Mesa/Zink frontend.
 * Weak resident references make absence an ordinary API_UNAVAILABLE error.
 */
#include "internal.h"
#include <SDL3/SDL.h>
#include "../zink/frontend.h"
#include "../sdl/ps5_startup_boundary.h"

#ifdef __APPLE__
#define OPTIONAL __attribute__((weak_import))
#else
#define OPTIONAL __attribute__((weak))
#endif
extern struct ps5zink_context *ps5zink_create(const struct ps5zink_config *) OPTIONAL;
extern int ps5zink_make_current(struct ps5zink_context *) OPTIONAL;
extern int ps5zink_destroy(struct ps5zink_context *) OPTIONAL;
extern int ps5zink_resize(struct ps5zink_context *, unsigned, unsigned) OPTIONAL;
extern int ps5zink_swap_buffers(struct ps5zink_context *) OPTIONAL;
extern int ps5zink_swap_interval(struct ps5zink_context *, int) OPTIONAL;
extern void (*ps5zink_get_proc_address(const char *))(void) OPTIONAL;
extern int ps5zink_error(void) OPTIONAL;

int ps5glfw_gl_available(void)
{
    return ps5zink_create && ps5zink_make_current && ps5zink_destroy &&
           ps5zink_resize && ps5zink_swap_buffers && ps5zink_swap_interval &&
           ps5zink_get_proc_address && ps5zink_error;
}
static void report(void)
{ _glfwInputError(GLFW_PLATFORM_ERROR, "PS5 Zink context operation failed (%d)", ps5zink_error()); }
static void make_current(_GLFWwindow *window)
{
    if (!ps5zink_make_current(window ? window->null.ps5_gl_context : NULL)) { report(); return; }
    _glfwPlatformSetTls(&_glfw.contextSlot, window);
}
static void swap(_GLFWwindow *window)
{
    int width, height;
    SDL_GetWindowSizeInPixels(window->null.ps5_window, &width, &height);
    if (width <= 0 || height <= 0) return; /* Minimized window has no drawable. */
    if (!ps5zink_resize(window->null.ps5_gl_context, (unsigned)width, (unsigned)height) ||
        !ps5zink_swap_buffers(window->null.ps5_gl_context)) report();
}
static void interval(int value)
{
    _GLFWwindow *window = _glfwPlatformGetTls(&_glfw.contextSlot);
    if (!window || !ps5zink_swap_interval(window->null.ps5_gl_context, value)) report();
}
static int platform_extension(const char *name)
{ (void)name; return GLFW_FALSE; } /* Generic GLFW checks real GL extensions first. */
static GLFWglproc address(const char *name) { return (GLFWglproc)ps5zink_get_proc_address(name); }
int ps5glfw_gl_destroy(_GLFWwindow *window)
{
    if (!window->null.ps5_gl_context) return GLFW_TRUE;
    if (!ps5zink_destroy(window->null.ps5_gl_context)) { report(); return GLFW_FALSE; }
    window->null.ps5_gl_context = NULL;
    return GLFW_TRUE;
}
static void destroy(_GLFWwindow *window) { (void)ps5glfw_gl_destroy(window); }
extern int32_t ps5glfw_gl_surface(void *, void *, uint64_t *);
int ps5glfw_gl_create(_GLFWwindow *window, const _GLFWctxconfig *ctx, const _GLFWfbconfig *fb)
{
    if (!ps5glfw_gl_available()) {
        _glfwInputError(GLFW_API_UNAVAILABLE, "PS5 Zink resident group is absent");
        return GLFW_FALSE;
    }
    if (ctx->client != GLFW_OPENGL_API || ctx->source != GLFW_NATIVE_CONTEXT_API ||
        ctx->profile != GLFW_OPENGL_CORE_PROFILE || ctx->share || (ctx->noerror && ctx->debug) ||
        ctx->robustness || fb->stereo || fb->samples || !fb->doublebuffer || fb->sRGB) {
        _glfwInputError(GLFW_VERSION_UNAVAILABLE, "PS5 Zink requires an unshared desktop core native context and non-MSAA framebuffer");
        return GLFW_FALSE;
    }
    int width, height;
    SDL_GetWindowSizeInPixels(window->null.ps5_window, &width, &height);
    struct ps5zink_config config = {
        .width = width > 0 ? (unsigned)width : 1,
        .height = height > 0 ? (unsigned)height : 1,
        .major = ctx->major, .minor = ctx->minor, .core = 1,
        .forward = ctx->forward, .debug = ctx->debug, .no_error = ctx->noerror,
        .window = window->null.ps5_window, .create_surface = ps5glfw_gl_surface,
    };
#ifdef PS5_GLFW_HOST_TEST
    /* Actual SDL dummy window plus actual Zink offscreen GL. Host readback
     * tests explicitly do not claim SDL/VideoOut presentation coverage. */
    config.window = NULL; config.create_surface = NULL;
#endif
    PS5_BOUNDARY("Zink frontend create enter");
    window->null.ps5_gl_context = ps5zink_create(&config);
    PS5_BOUNDARY("Zink frontend create returned");
    if (!window->null.ps5_gl_context) { report(); return GLFW_FALSE; }
    window->context.client = GLFW_OPENGL_API;
    window->context.source = GLFW_NATIVE_CONTEXT_API;
    window->context.makeCurrent = make_current;
    window->context.swapBuffers = swap;
    window->context.swapInterval = interval;
    window->context.extensionSupported = platform_extension;
    window->context.getProcAddress = address;
    window->context.destroy = destroy;
    PS5_BOUNDARY("GLFW GL attribute refresh enter");
    int refreshed = _glfwRefreshContextAttribs(window, ctx);
    PS5_BOUNDARY("GLFW GL attribute refresh returned");
    return refreshed;
}
