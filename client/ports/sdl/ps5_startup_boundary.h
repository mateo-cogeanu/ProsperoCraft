/* SPDX-License-Identifier: Zlib
 * Bounded allocation-free startup breadcrumbs, best-effort diagnostics only.
 * Literal labels contain no accounts, paths from instances, or credentials.
 */
#ifndef PS5_STARTUP_BOUNDARY_H
#define PS5_STARTUP_BOUNDARY_H
#if defined(PS5_GLFW_HOST_TEST) || defined(PS5_RWLOCK_HOST_TEST)
#define PS5_BOUNDARY(label) ((void)0)
#else
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
static unsigned ps5_boundary_count;
static void ps5_startup_boundary(const char *text, unsigned length)
{
    int saved = errno;
    if (__atomic_fetch_add(&ps5_boundary_count, 1, __ATOMIC_RELAXED) < 128) {
        int fd = open("/download0/java25-startup.log", O_WRONLY | O_APPEND);
        if (fd >= 0) {
            unsigned done = 0;
            while (done < length) {
                ssize_t n = write(fd, text + done, length - done);
                if (n > 0) done += (unsigned)n;
                else if (n < 0 && errno == EINTR) continue;
                else break;
            }
            close(fd);
        }
    }
    errno = saved;
}
#define PS5_BOUNDARY(label) ps5_startup_boundary("PS5_STARTUP " label "\n",sizeof("PS5_STARTUP " label "\n")-1)
#endif
#endif
