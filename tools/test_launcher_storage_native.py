#!/usr/bin/env python3
"""Actual bootstrap storage/report/temp routing with isolated host roots."""
from pathlib import Path
import os,subprocess,tempfile
from host_toolchain import ROOT,executable
SOURCE=r'''
#include "storage_paths.hpp"
#include "ps5_startup_boundary.h"
#include <cassert>
#include <string>
extern "C" char* client_startup_openal_getenv(const char*);
extern "C" int ps5shaderc_fault_begin();
extern "C" void ps5shaderc_fault_end();
int main(int argc,char**argv){
 assert(argc==2);bool expected=std::strcmp(argv[1],"shared")==0;assert(prospero_storage::initialize());assert(prospero_storage::shared==expected);
 const char* root=prospero_storage::report_root();assert(std::strcmp(std::getenv("PROSPERO_DIAGNOSTIC_ROOT"),root)==0);assert(std::strcmp(ps5::log_share::report_root(),root)==0);
 assert(std::strcmp(client_startup_openal_getenv("ALSOFT_LOCAL_PATH"),expected?PROSPERO_SHARED_STORAGE:PROSPERO_LEGACY_STORAGE "/mc-client")==0);
 assert(std::strcmp(std::getenv("TMPDIR"),expected?PROSPERO_SHARED_STORAGE "/tmp":PROSPERO_LEGACY_STORAGE)==0);
 int initial=::open(PROSPERO_REPORT_PATH("java25-startup.log"),O_CREAT|O_WRONLY,0600);assert(initial>=0);assert(::close(initial)==0);PS5_BOUNDARY("routing");
 assert(ps5shaderc_fault_begin()==4);ps5shaderc_fault_end();
 std::string fault=std::string(root)+"/java25-vm-trace.log";struct stat a{};assert(stat(fault.c_str(),&a)==0&&S_ISREG(a.st_mode));
 if(expected){std::string forbidden=std::string(PROSPERO_LEGACY_STORAGE)+"/java25-vm-trace.log";assert(stat(forbidden.c_str(),&a)!=0&&errno==ENOENT);}
 puts("PASS actual native shared/fallback report+tmp selection, report-root hook, SDL breadcrumb, shader-fault file and unchanged OpenAL env adapter routing");
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-storage-native-')as td:
 root=Path(td).resolve();cc=executable('clang',env='CC');cxx=executable('clang++',env='CXX');flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread']
 (root/'main.cpp').write_text(SOURCE)
 for mode in ('shared','fallback'):
  case=root/mode;case.mkdir();primary=case/'data';legacy=case/'legacy';legacy.mkdir()
  if mode=='fallback':primary.write_text('unavailable-directory')
  (case/'log_share.hpp').write_text('#pragma once\nnamespace ps5::log_share {inline const char* selected=nullptr;inline bool configure_root(const char* root){selected=root;return true;}inline const char* report_root(){return selected;}}\n')
  objects=[]
  for name in ('client/ports/shaderc/fault.c','client/startup/openal_trace_env.c'):
   obj=case/(Path(name).stem+'.o');subprocess.run([cc,*flags,'-c',str(ROOT/name),'-o',str(obj)],check=True);objects.append(str(obj))
  binary=case/'check'
  subprocess.run([cxx,'-std=c++20',*flags,'-DPROSPERO_SHARED_STORAGE="'+str(primary)+'"','-DPROSPERO_LEGACY_STORAGE="'+str(legacy)+'"','-I'+str(ROOT/'client/launcher'),'-I'+str(ROOT/'client/ports/sdl'),'-I'+str(case),str(root/'main.cpp'),*objects,'-o',str(binary)],check=True)
  subprocess.run([str(binary),mode],check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
