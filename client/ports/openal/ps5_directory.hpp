/* SPDX-License-Identifier: LGPL-2.0-or-later
 * Scoped POSIX directory calls are rebound to the consumer's resident provider.
 * libc++'s out-of-line directory_iterator calls the title's refused opendir.
 * The stream closes on normal completion, read failure and result allocation failure.
 */
#pragma once
#include <cerrno>
#include <dirent.h>
#include <system_error>
namespace ps5audio {
class Directory {
 DIR* stream;
public:
 explicit Directory(const char* path):stream{::opendir(path)} {
  if(!stream)throw std::system_error{errno,std::generic_category(),"OpenAL opendir"};
 }
 ~Directory(){::closedir(stream);}
 Directory(const Directory&)=delete;
 Directory& operator=(const Directory&)=delete;
 dirent* next(){
  errno=0;
  auto* entry=::readdir(stream);
  if(!entry&&errno)throw std::system_error{errno,std::generic_category(),"OpenAL readdir"};
  return entry;
 }
};
}
