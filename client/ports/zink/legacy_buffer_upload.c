/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdatomic.h>
#include <string.h>

typedef void (*GlProc)(void);
typedef void (*BufferDataProc)(unsigned int target, ptrdiff_t size, const void *data, unsigned int usage);

extern GlProc __real_clientgpu_ps5zink_get_proc_address(const char *name);
extern const char *SDL_GetHint(const char *name);

static _Atomic(BufferDataProc) driver_buffer_data;

static void legacy_buffer_data(unsigned int target, ptrdiff_t size, const void *data, unsigned int usage)
{
    enum { GL_ARRAY_BUFFER = 0x8892, GL_DYNAMIC_DRAW = 0x88e8, MAX_UPLOAD = 256 * 1024 };
    BufferDataProc upload = atomic_load_explicit(&driver_buffer_data, memory_order_acquire);

    // Drop the old store before replacing a small immediate vertex upload.
    // Mesa otherwise reuses same-size storage through its discard path.
    if (target == GL_ARRAY_BUFFER && usage == GL_DYNAMIC_DRAW && data && size > 0 && size <= MAX_UPLOAD)
        upload(target, 0, NULL, usage);
    upload(target, size, data, usage);
}

GlProc __wrap_clientgpu_ps5zink_get_proc_address(const char *name)
{
    GlProc address = __real_clientgpu_ps5zink_get_proc_address(name);
    if (!address || !name || strcmp(name, "glBufferData") != 0)
        return address;

    const char *enabled = SDL_GetHint("PS5_LEGACY_GUI_VERTEX_UPLOAD");
    if (!enabled || strcmp(enabled, "1") != 0)
        return address;

    atomic_store_explicit(&driver_buffer_data, (BufferDataProc)address, memory_order_release);
    return (GlProc)legacy_buffer_data;
}
