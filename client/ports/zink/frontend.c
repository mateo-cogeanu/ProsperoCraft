/* SPDX-License-Identifier: MIT
 * Real Mesa GL state tracker on Zink, with private offscreen/kopper drawables.
 * A single shared screen owns the game Vulkan instance/device. A window surface
 * callback reuses the existing display selector with that instance. No EGL/DRI
 * dlopen, OSMesa implementation, replacement GL functions or CPU presenter.
 */
#include "frontend.h"
#include "state_tracker/st_context.h"
#include "state_tracker/st_manager.h"
#include "main/glthread.h"
#include "glapi/glapi/glapi.h"
#include "pipe/p_screen.h"
#include "pipe/p_context.h"
#include "util/u_inlines.h"
#include "util/u_atomic.h"
#include "zink/zink_public.h"
#include "zink/zink_kopper.h"
#include <errno.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>

#define PUBLIC __attribute__((visibility("default")))
struct ps5zink_context {
    struct pipe_frontend_drawable drawable;
    struct st_visual visual;
    struct st_context *st;
    struct pipe_resource *textures[ST_ATTACHMENT_COUNT];
    struct kopper_loader_info loader;
    void *native_window;
    ps5zink_surface_fn create_surface;
    struct ps5zink_context *next;
    unsigned width, height;
    pthread_t owner;
    bool bound, window, flushing;
};
static pthread_mutex_t guard = PTHREAD_MUTEX_INITIALIZER;
static struct pipe_frontend_screen frontend;
static struct ps5zink_context *contexts;
static uint32_t drawable_id;
/* Constant initialized C TLS; compiler emulation on PS5, no C++ wrappers. */
static __thread struct ps5zink_context *current;
static __thread int last_error;

static VkResult surface_callback(VkInstance instance, void *opaque, VkSurfaceKHR *surface)
{
    struct ps5zink_context *c = opaque;
    uint64_t handle = 0;
    *surface = VK_NULL_HANDLE;
    VkResult result = (VkResult)c->create_surface((void *)instance, c->native_window, &handle);
    _Static_assert(sizeof(*surface) == sizeof(handle), "64-bit Vulkan surface ABI required");
    if (result == VK_SUCCESS && !handle) return VK_ERROR_INITIALIZATION_FAILED;
    if (result == VK_SUCCESS) memcpy(surface, &handle, sizeof(handle));
    return result;
}

static int fail(int code) { last_error = code; return 0; }
static int screen_param(struct pipe_frontend_screen *screen, enum st_manager_param param)
{ (void)screen; (void)param; return 0; }
static bool known(struct ps5zink_context *context)
{
    for (struct ps5zink_context *c = contexts; c; c = c->next)
        if (c == context) return true;
    return false;
}
static bool usable(struct ps5zink_context *c)
{ return known(c) && (!c->bound || pthread_equal(c->owner, pthread_self())); }

static struct pipe_resource *allocate(struct ps5zink_context *c, unsigned attachment)
{
    struct pipe_screen *screen = frontend.screen;
    bool depth = attachment == ST_ATTACHMENT_DEPTH_STENCIL;
    struct pipe_resource templ = {0};
    templ.target = PIPE_TEXTURE_2D;
    templ.format = depth ? c->visual.depth_stencil_format : c->visual.color_format;
    templ.width0 = c->width; templ.height0 = c->height;
    templ.depth0 = templ.array_size = 1;
    templ.bind = depth ? PIPE_BIND_DEPTH_STENCIL : PIPE_BIND_RENDER_TARGET | PIPE_BIND_SAMPLER_VIEW;
    if (c->window && !depth) {
        /* Match kopper's real back/front resource relationship. Front readback
         * has its own resource; a single displaytarget is shared underneath. */
        if (attachment == ST_ATTACHMENT_FRONT_LEFT) {
            if (!c->textures[ST_ATTACHMENT_BACK_LEFT])
                c->textures[ST_ATTACHMENT_BACK_LEFT] = allocate(c, ST_ATTACHMENT_BACK_LEFT);
            if (!c->textures[ST_ATTACHMENT_BACK_LEFT]) return NULL;
            return screen->resource_create_drawable(screen, &templ, c->textures[ST_ATTACHMENT_BACK_LEFT]);
        }
        templ.bind |= PIPE_BIND_DISPLAY_TARGET;
        return screen->resource_create_drawable(screen, &templ, &c->loader);
    }
    return screen->resource_create(screen, &templ);
}

static bool validate(struct st_context *st, struct pipe_frontend_drawable *drawable,
                     const enum st_attachment_type *attachments, unsigned count,
                     struct pipe_resource **out, struct pipe_resource **resolve)
{
    (void)st;
    struct ps5zink_context *c = (void *)drawable;
    if (resolve) *resolve = NULL;
    for (unsigned i = 0; i < count; i++) {
        unsigned a = attachments[i];
        if (a >= ST_ATTACHMENT_COUNT || !(c->visual.buffer_mask & (1u << a))) return false;
        if (!c->textures[a]) c->textures[a] = allocate(c, a);
        if (!c->textures[a]) return false;
    }
    for (unsigned i = 0; i < count; i++)
        pipe_resource_reference(&out[i], c->textures[attachments[i]]);
    return true;
}

struct present_flush {
    struct st_context *st;
    struct pipe_resource *texture;
};
/* Match kopper's notify_before_flush_cb: after pending GL vertices are emitted,
 * mark this drawable for presentation before the batch is ended/submitted. */
static void prepare_present(void *opaque)
{
    struct present_flush *flush = opaque;
    flush->st->pipe->flush_resource(flush->st->pipe, flush->texture);
}

static bool present(struct ps5zink_context *c, struct st_context *st, unsigned attachment)
{
    if (c->flushing) return true;
    c->flushing = true;
    _mesa_glthread_finish(st->ctx);
    struct pipe_resource *texture = c->textures[attachment];
    struct present_flush flush = {st, texture};
    st_context_flush(st, ST_FLUSH_END_OF_FRAME, NULL,
                     c->window && texture ? prepare_present : NULL, &flush);
    bool success = true;
    if (c->window && texture) {
        frontend.screen->flush_frontbuffer(frontend.screen, st->pipe, texture, 0, 0, c, 0, NULL);
        success = zink_kopper_check(texture);
    }
    p_atomic_inc(&c->drawable.stamp);
    st_invalidate_buffers(st);
    c->flushing = false;
    return success;
}
static bool flush_front(struct st_context *st, struct pipe_frontend_drawable *drawable,
                        enum st_attachment_type attachment)
{
    if (attachment != ST_ATTACHMENT_FRONT_LEFT) return false;
    return present((void *)drawable, st, attachment);
}
static bool flush_swap(struct st_context *st, struct pipe_frontend_drawable *drawable)
{ (void)st; (void)drawable; return true; }

PUBLIC struct ps5zink_context *ps5zink_create(const struct ps5zink_config *config)
{
    last_error = 0;
    if (!config || !config->width || !config->height || config->width > 16384 ||
        config->height > 16384 || config->major < 3 || config->major > 4 ||
        config->minor < 0 || config->minor > 6 || !config->core ||
        (!!config->window != !!config->create_surface)) {
        fail(EINVAL); return NULL;
    }
    if (pthread_mutex_lock(&guard)) { fail(EBUSY); return NULL; }
    struct ps5zink_context *c = calloc(1, sizeof(*c));
    if (!c) { fail(ENOMEM); goto done; }
    if (!frontend.screen) {
        frontend.screen = zink_create_screen(NULL, NULL);
        frontend.get_param = screen_param;
        if (!frontend.screen) { fail(ENODEV); free(c); c = NULL; goto done; }
    }
    c->width = config->width; c->height = config->height;
    c->window = config->window != NULL;
    c->visual = (struct st_visual) {
        .buffer_mask = ST_ATTACHMENT_FRONT_LEFT_MASK | ST_ATTACHMENT_BACK_LEFT_MASK | ST_ATTACHMENT_DEPTH_STENCIL_MASK,
        .color_format = PIPE_FORMAT_B8G8R8A8_UNORM,
        .depth_stencil_format = PIPE_FORMAT_Z24_UNORM_S8_UINT,
    };
    c->loader.bos.sType = c->window ? VK_STRUCTURE_TYPE_DISPLAY_SURFACE_CREATE_INFO_KHR : 0;
    c->native_window = config->window;
    c->create_surface = config->create_surface;
    c->loader.ps5_window = c->window ? c : NULL;
    c->loader.ps5_create_surface = c->window ? surface_callback : NULL;
    c->loader.initial_swap_interval = 1;
    c->loader.has_alpha = 1;
    c->loader.present_opaque = true;
    c->drawable = (struct pipe_frontend_drawable) {
        .stamp = 1, .ID = ++drawable_id, .fscreen = &frontend, .visual = &c->visual,
        .validate = validate, .flush_front = flush_front, .flush_swapbuffers = flush_swap,
    };
    struct st_context_attribs attributes = {0};
    attributes.profile = API_OPENGL_CORE;
    attributes.major = config->major; attributes.minor = config->minor;
    attributes.visual = c->visual;
    attributes.flags = (config->forward ? ST_CONTEXT_FLAG_FORWARD_COMPATIBLE : 0) |
                       (config->debug ? ST_CONTEXT_FLAG_DEBUG : 0);
    enum st_context_error error;
    c->st = st_api_create_context(&frontend, &attributes, &error, NULL);
    if (!c->st) {
        fail(error == ST_CONTEXT_ERROR_BAD_VERSION ? ENOTSUP : ENOMEM);
        free(c); c = NULL;
        if (!contexts) { st_screen_destroy(&frontend); frontend.screen->destroy(frontend.screen); memset(&frontend, 0, sizeof(frontend)); }
        goto done;
    }
    c->st->frontend_context = c;
    c->next = contexts; contexts = c;
done:
    pthread_mutex_unlock(&guard);
    return c;
}

PUBLIC int ps5zink_make_current(struct ps5zink_context *c)
{
    last_error = 0;
    if (pthread_mutex_lock(&guard)) return fail(EBUSY);
    struct ps5zink_context *previous = current;
    int result = 0;
    if (c && !usable(c)) { fail(EBUSY); goto done; }
    if (c) {
        /* A valid GL context does not imply a usable window surface. Force
         * real drawable allocation before reporting successful make-current. */
        const enum st_attachment_type attachments[] = {ST_ATTACHMENT_BACK_LEFT, ST_ATTACHMENT_DEPTH_STENCIL};
        struct pipe_resource *textures[2] = {NULL, NULL};
        bool ready = validate(c->st, &c->drawable, attachments, 2, textures, NULL);
        for (unsigned i = 0; i < 2; i++) pipe_resource_reference(&textures[i], NULL);
        if (!ready) { fail(ENOMEM); goto done; }
    }
    if (!st_api_make_current(c ? c->st : NULL, c ? &c->drawable : NULL, c ? &c->drawable : NULL)) {
        /* Restore the previous real Mesa binding before retaining its owner. */
        st_api_make_current(previous ? previous->st : NULL,
                            previous ? &previous->drawable : NULL, previous ? &previous->drawable : NULL);
        fail(ENOMEM); goto done;
    }
    if (previous) previous->bound = false;
    current = c;
    if (c) { c->owner = pthread_self(); c->bound = true; }
    result = 1;
done:
    pthread_mutex_unlock(&guard);
    return result;
}
PUBLIC struct ps5zink_context *ps5zink_get_current(void) { return current; }
PUBLIC int ps5zink_destroy(struct ps5zink_context *c)
{
    last_error = 0;
    if (pthread_mutex_lock(&guard)) return fail(EBUSY);
    int result = 0;
    if (!c || !usable(c)) { fail(EBUSY); goto done; }
    if (current == c) {
        if (!st_api_make_current(NULL, NULL, NULL)) { fail(EIO); goto done; }
        current = NULL; c->bound = false;
    }
    _mesa_glthread_finish(c->st->ctx);
    st_context_flush(c->st, ST_FLUSH_WAIT, NULL, NULL, NULL);
    st_api_destroy_drawable(&c->drawable);
    st_destroy_context(c->st);
    for (unsigned i = 0; i < ST_ATTACHMENT_COUNT; i++) pipe_resource_reference(&c->textures[i], NULL);
    struct ps5zink_context **link = &contexts;
    while (*link != c) link = &(*link)->next;
    *link = c->next;
    free(c);
    if (!contexts) { st_screen_destroy(&frontend); frontend.screen->destroy(frontend.screen); memset(&frontend, 0, sizeof(frontend)); }
    result = 1;
done:
    pthread_mutex_unlock(&guard);
    return result;
}
PUBLIC int ps5zink_resize(struct ps5zink_context *c, unsigned width, unsigned height)
{
    last_error = 0;
    if (!width || !height || width > 16384 || height > 16384) return fail(EINVAL);
    if (pthread_mutex_lock(&guard)) return fail(EBUSY);
    int result = 0;
    if (!usable(c)) { fail(EBUSY); goto done; }
    if (c->width != width || c->height != height) {
        _mesa_glthread_finish(c->st->ctx);
        st_context_flush(c->st, ST_FLUSH_WAIT, NULL, NULL, NULL);
        for (unsigned i = 0; i < ST_ATTACHMENT_COUNT; i++) pipe_resource_reference(&c->textures[i], NULL);
        c->width = width; c->height = height;
        p_atomic_inc(&c->drawable.stamp);
        st_invalidate_buffers(c->st);
    }
    result = 1;
done:
    pthread_mutex_unlock(&guard);
    return result;
}
PUBLIC int ps5zink_swap_buffers(struct ps5zink_context *c)
{
    last_error = 0;
    if (!c || current != c) return fail(EINVAL);
    if (!present(c, c->st, ST_ATTACHMENT_BACK_LEFT)) return fail(EIO);
    if (c->textures[ST_ATTACHMENT_FRONT_LEFT]) {
        struct pipe_resource *back = c->textures[ST_ATTACHMENT_BACK_LEFT];
        c->textures[ST_ATTACHMENT_BACK_LEFT] = c->textures[ST_ATTACHMENT_FRONT_LEFT];
        c->textures[ST_ATTACHMENT_FRONT_LEFT] = back;
    }
    return 1;
}
PUBLIC int ps5zink_swap_interval(struct ps5zink_context *c, int interval)
{
    last_error = 0;
    if (!c || current != c || interval < 0) return fail(EINVAL);
    c->loader.initial_swap_interval = 1; /* Physical PS5 remains FIFO. */
    if (c->window && c->textures[ST_ATTACHMENT_BACK_LEFT])
        zink_kopper_set_swap_interval(frontend.screen, c->textures[ST_ATTACHMENT_BACK_LEFT], 1);
    return 1;
}
PUBLIC void (*ps5zink_get_proc_address(const char *name))(void)
{ return name ? _mesa_glapi_get_proc_address(name) : NULL; }
PUBLIC int ps5zink_error(void) { return last_error; }
