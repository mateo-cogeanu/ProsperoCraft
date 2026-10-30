#!/usr/bin/env python3
"""Fault-inject the actual directory owner, including failures during enumeration."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=r'''
#include <dirent.h>
#include <cerrno>
#include <cassert>
#include <cstring>
#include <stdexcept>
static int mode=0,opened=0,closed=0,reads=0;
static dirent entry;
static DIR* owned=reinterpret_cast<DIR*>(0x1234);
static DIR* test_opendir(const char* path){assert(!strcmp(path,"fixture"));if(mode==1){errno=EACCES;return nullptr;}++opened;return owned;}
static int test_closedir(DIR* stream){assert(stream==owned);++closed;return 0;}
static dirent* test_readdir(DIR* stream){assert(stream==owned);if(mode==2){errno=EIO;return nullptr;}if(reads++==0){strcpy(entry.d_name,"actual.mhr");return &entry;}return nullptr;}
#define opendir test_opendir
#define closedir test_closedir
#define readdir test_readdir
#include "ps5_directory.hpp"
#undef opendir
#undef closedir
#undef readdir
int main(){
 for(int cycle=0;cycle<1000;cycle++){
  mode=0;reads=0;
  {ps5audio::Directory directory{"fixture"};errno=EBUSY;assert(!strcmp(directory.next()->d_name,"actual.mhr"));errno=EBUSY;assert(directory.next()==nullptr);}
  assert(opened==closed);
  mode=1;try{ps5audio::Directory directory{"fixture"};assert(false);}catch(const std::system_error& e){assert(e.code().value()==EACCES);}assert(opened==closed);
  mode=2;try{ps5audio::Directory directory{"fixture"};directory.next();assert(false);}catch(const std::system_error& e){assert(e.code().value()==EIO);}assert(opened==closed);
  mode=0;try{ps5audio::Directory directory{"fixture"};throw std::bad_alloc{};}catch(const std::bad_alloc&){}assert(opened==closed);
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 w=Path(d);(w/'check.cpp').write_text(source)
 subprocess.run(['clang++','-std=c++17','-fsanitize=address,undefined','-I'+str(ROOT/'client/ports/openal'),str(w/'check.cpp'),'-o',str(w/'check')],check=True)
 subprocess.run([str(w/'check')],check=True)
print('PASS actual directory RAII:1000 EOF/stale-errno/open-denial/read-error/allocation-unwind cycles;no leaked stream;ASan/UBSan')
