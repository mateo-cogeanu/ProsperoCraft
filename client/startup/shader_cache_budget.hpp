/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <cerrno>
#include <cstdlib>

namespace prospero_shader_cache {
inline int configure(int (*setter)(const char*, const char*, int) = ::setenv) {
 // Mesa otherwise uses 50 partitions. Each live cache can retain a database
 // and index handle per partition for the duration of gameplay.
 return setter("MESA_DISK_CACHE_DATABASE_NUM_PARTS", "2", 1) == 0
     ? 0 : (errno ? errno : EIO);
}
}
