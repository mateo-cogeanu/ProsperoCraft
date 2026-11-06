#!/usr/bin/env python3
"""Actual candidate environment policy, preserving defaults and failure ownership."""
import os,subprocess,tempfile
from pathlib import Path
from host_toolchain import ROOT,executable

def main():
 cxx=executable('clang++',env='CXX')
 with tempfile.TemporaryDirectory(prefix='prospero-zink-submit-')as folder:
  w=Path(folder);source=w/'check.cpp';source.write_text(r'''#include <cassert>
#include <string>
#include "submit_policy.hpp"
#include "../../startup/shader_cache_budget.hpp"
static int calls;
static int refusal(const char*,const char*,int){calls++;errno=ENOMEM;return -1;}
int main(){
 unsetenv("MESA_DISK_CACHE_DATABASE_NUM_PARTS");
 assert(prospero_shader_cache::configure(refusal)==ENOMEM&&calls==1);
 assert(!getenv("MESA_DISK_CACHE_DATABASE_NUM_PARTS"));
 assert(!prospero_shader_cache::configure());
 assert(std::string(getenv("MESA_DISK_CACHE_DATABASE_NUM_PARTS"))=="2");
 setenv("MESA_DISK_CACHE_DATABASE_NUM_PARTS","50",1);
 assert(!prospero_shader_cache::configure());
 assert(std::string(getenv("MESA_DISK_CACHE_DATABASE_NUM_PARTS"))=="2");
 calls=0;
 unsetenv("ZINK_DEBUG");assert(!getenv("ZINK_DEBUG"));
 assert(!prospero_zink::enable_flushsync());assert(std::string(getenv("ZINK_DEBUG"))=="flushsync");
 assert(!prospero_zink::enable_flushsync(refusal)&&calls==0);
 setenv("ZINK_DEBUG","nir,validation",1);assert(!prospero_zink::enable_flushsync());assert(std::string(getenv("ZINK_DEBUG"))=="nir,validation,flushsync");
 setenv("ZINK_DEBUG","nir flushsync validation",1);assert(!prospero_zink::enable_flushsync(refusal)&&calls==0);
 setenv("ZINK_DEBUG","notflushsync",1);assert(prospero_zink::enable_flushsync(refusal)==ENOMEM&&calls==1);assert(std::string(getenv("ZINK_DEBUG"))=="notflushsync");
 std::string large(501,'x');setenv("ZINK_DEBUG",large.c_str(),1);assert(prospero_zink::enable_flushsync(refusal)==E2BIG&&calls==1);assert(std::string(getenv("ZINK_DEBUG"))==large);
 std::string edge(500,'x');setenv("ZINK_DEBUG",edge.c_str(),1);assert(!prospero_zink::enable_flushsync());assert(std::string(getenv("ZINK_DEBUG"))==edge+",flushsync");
 unsetenv("GALLIUM_THREAD");assert(!getenv("GALLIUM_THREAD"));
 assert(prospero_zink::enable_synchronous_context(refusal)==ENOMEM&&calls==2);assert(!getenv("GALLIUM_THREAD"));
 setenv("GALLIUM_THREAD","1",1);assert(prospero_zink::enable_synchronous_context(refusal)==ENOMEM&&calls==3);assert(std::string(getenv("GALLIUM_THREAD"))=="1");
 assert(!prospero_zink::enable_synchronous_context());assert(std::string(getenv("GALLIUM_THREAD"))=="0");
 assert(!prospero_zink::enable_synchronous_context(refusal)&&calls==3);
 assert(std::string(getenv("ZINK_DEBUG"))==edge+",flushsync");
 setenv("ZINK_DEBUG","nir,flushsync",1);
 assert(!prospero_zink::disable_shader_objects());
 assert(std::string(getenv("ZINK_DEBUG"))=="nir,flushsync,noshobj");
 assert(!prospero_zink::disable_shader_objects(refusal)&&calls==3);
 setenv("ZINK_DEBUG","notnoshobj",1);
 assert(prospero_zink::disable_shader_objects(refusal)==ENOMEM&&calls==4);
 assert(std::string(getenv("ZINK_DEBUG"))=="notnoshobj");
 unsetenv("GALLIUM_THREAD");unsetenv("ZINK_DEBUG");return 0;
}
''')
  subprocess.run([cxx,'-std=c++20','-D_POSIX_C_SOURCE=200809L','-fsanitize=address,undefined','-I'+str(ROOT/'client/ports/zink'),source,'-o',w/'check'],check=True)
  subprocess.run([w/'check'],check=True,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS actual candidate flushsync, shader-object opt-out and direct-context policy: exact token/idempotence/preserved flags/absent default/bounds/native setter refusal;ASan/UBSan;no PS5 inference')
if __name__=='__main__':main()
