/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include "log_share.hpp"
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#ifndef PROSPERO_SHARED_STORAGE
#define PROSPERO_SHARED_STORAGE "/data/ProsperoCraft"
#endif
#ifndef PROSPERO_LEGACY_STORAGE
#define PROSPERO_LEGACY_STORAGE "/download0"
#endif
namespace prospero_storage {
inline bool shared=false;
inline const char* report_root()noexcept{return shared?PROSPERO_SHARED_STORAGE "/reports":PROSPERO_LEGACY_STORAGE "";}
inline const char* base_root()noexcept{return shared?PROSPERO_SHARED_STORAGE "":PROSPERO_LEGACY_STORAGE "/ProsperoCraft";}
inline bool directory(const char* path)noexcept{
 if(::mkdir(path,0700)!=0&&errno!=EEXIST)return false;
 int fd=::open(path,O_RDONLY|O_DIRECTORY|O_NOFOLLOW);if(fd<0)return false;
 struct stat value{};bool ok=::fstat(fd,&value)==0&&S_ISDIR(value.st_mode);if(::close(fd)!=0)ok=false;return ok;
}
inline bool shared_access()noexcept{
 if(!directory(PROSPERO_SHARED_STORAGE "")||!directory(PROSPERO_SHARED_STORAGE "/reports")||!directory(PROSPERO_SHARED_STORAGE "/tmp")||!directory(PROSPERO_SHARED_STORAGE "/reports/mc-client")||!directory(PROSPERO_SHARED_STORAGE "/reports/mc-client/logs"))return false;
 char name[160],renamed[160];std::snprintf(name,sizeof(name),PROSPERO_SHARED_STORAGE "/reports/.native-storage-check-%ld",static_cast<long>(::getpid()));std::snprintf(renamed,sizeof(renamed),"%s-moved",name);
 int fd=::open(name,O_CREAT|O_EXCL|O_RDWR|O_NOFOLLOW,0600);if(fd<0)return false;
 const char content[]="ProsperoCraft";char check[sizeof(content)]{};bool ok=::write(fd,content,sizeof(content))==static_cast<ssize_t>(sizeof(content))&&::lseek(fd,0,SEEK_SET)==0&&::read(fd,check,sizeof(check))==static_cast<ssize_t>(sizeof(check))&&std::memcmp(content,check,sizeof(content))==0;
 if(::close(fd)!=0)ok=false;
 if(ok){ok=::rename(name,renamed)==0;if(ok){ok=::unlink(renamed)==0;return ok;}}
 (void)::unlink(name);return false;
}
inline bool initialize()noexcept{
 shared=shared_access();
 if(!shared&&(!directory(PROSPERO_LEGACY_STORAGE "/mc-client")||!directory(PROSPERO_LEGACY_STORAGE "/mc-client/logs")))return false;
 // Set before core/library constructors and Java's environment snapshot.
 if(::setenv("PROSPERO_DIAGNOSTIC_ROOT",report_root(),1)||::setenv("PROSPERO_STORAGE_BASE",base_root(),1)||::setenv("ALSOFT_LOCAL_PATH",shared?PROSPERO_SHARED_STORAGE "":PROSPERO_LEGACY_STORAGE "/mc-client",1)||::setenv("HOME",base_root(),1)||::setenv("TMPDIR",shared?PROSPERO_SHARED_STORAGE "/tmp":PROSPERO_LEGACY_STORAGE "",1))return false;
 return ps5::log_share::configure_root(report_root());
}
}
#define PROSPERO_REPORT_PATH(name) (prospero_storage::shared?PROSPERO_SHARED_STORAGE "/reports/" name:PROSPERO_LEGACY_STORAGE "/" name)
#define PROSPERO_STORAGE_OPTION(primary,fallback) (prospero_storage::shared?primary:fallback)
