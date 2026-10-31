/* SPDX-License-Identifier: MIT
 * Private Mesa frontend ABI. This is not an EGL implementation or loader.
 */
#ifndef PROSPERO_ZINK_FRONTEND_H
#define PROSPERO_ZINK_FRONTEND_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
struct ps5zink_context;
/* Stable opaque ABI keeps GLFW's private minimal Vulkan types separate from
 * Mesa's real Vulkan headers. The adapter copies a 64-bit surface handle. */
typedef int32_t (*ps5zink_surface_fn)(void *, void *, uint64_t *);
struct ps5zink_config {
    unsigned width, height;
    int major, minor, core, forward, debug;
    void *window;
    ps5zink_surface_fn create_surface;
};
struct ps5zink_context *ps5zink_create(const struct ps5zink_config *);
int ps5zink_make_current(struct ps5zink_context *);
struct ps5zink_context *ps5zink_get_current(void);
int ps5zink_destroy(struct ps5zink_context *);
int ps5zink_resize(struct ps5zink_context *, unsigned, unsigned);
int ps5zink_swap_buffers(struct ps5zink_context *);
int ps5zink_swap_interval(struct ps5zink_context *, int);
void (*ps5zink_get_proc_address(const char *))(void);
int ps5zink_error(void);
#ifdef __cplusplus
}
#endif
#endif
