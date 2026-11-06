/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once

#include "file_activity.hpp"

#include <atomic>
#include <cerrno>
#include <unistd.h>

namespace prospero_file_pressure {
inline std::atomic<int> report_fd{-1};
inline std::atomic_flag captured = ATOMIC_FLAG_INIT;

inline void arm(int fd) {
 report_fd.store(fd, std::memory_order_release);
}

inline void write_report(int fd, const char* data, size_t size) {
 while(size != 0) {
  ssize_t count = ::write(fd, data, size);
  if(count < 0 && errno == EINTR) continue;
  if(count <= 0) return;
  data += count;
  size -= static_cast<size_t>(count);
 }
}

inline void on_open_failure(int error) {
 if(error != EMFILE) return;
 int fd = report_fd.load(std::memory_order_acquire);
 if(fd < 0 || captured.test_and_set(std::memory_order_relaxed)) return;

 // The stderr report is already open. Snapshot before more files close,
 // and release the tracking lock before writing to disk.
 int saved = errno;
 static char report[80 * 1024];
 int length = ps5::file_activity::snapshot(report, sizeof(report), 512);
 constexpr char marker[] = "\n=== PS5 first EMFILE descriptor snapshot ===\n";
 write_report(fd, marker, sizeof(marker) - 1);
 if(length > 0) write_report(fd, report, static_cast<size_t>(length));
 errno = saved;
}
}
