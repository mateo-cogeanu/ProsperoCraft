#!/usr/bin/env python3
"""Actual native throw recorder forwarded through host's genuine C++ exception ABI."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=r'''
#include <typeinfo>
#include <system_error>
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <cxxabi.h>
#include <new>
#include <cassert>
#include <string>
static std::string output;static unsigned opens,closes;static bool deny_open,interrupted;
static int test_open(const char* path,int flags,...){assert(!strcmp(path,"/download0/java25-startup.log")&&flags==(O_WRONLY|O_APPEND));opens++;if(deny_open){errno=EMFILE;return -1;}return 71;}
static ssize_t test_write(int fd,const void*p,size_t count){assert(fd==71);if(interrupted){interrupted=false;errno=EINTR;return -1;}size_t n=count>7?7:count;output.append((const char*)p,n);return n;}
static int test_close(int fd){assert(fd==71);closes++;errno=EBADF;return 0;}
#define open test_open
#define write test_write
#define close test_close
'''
s+='\n#include "'+str(r/'client/gpu/exception_trace.cpp')+'"\n'
s+=r'''
#undef open
#undef write
#undef close
extern "C" [[noreturn]] void __real___cxa_throw(void*p,void*t,void(*d)(void*)){assert(errno==EDOM);__cxxabiv1::__cxa_throw(p,(std::type_info*)t,d);}
static int destroyed;
static void destroy_system(void*p){((std::system_error*)p)->~system_error();destroyed++;}
static void send_system(int code){void*p=__cxxabiv1::__cxa_allocate_exception(sizeof(std::system_error));new(p)std::system_error(std::error_code(code,std::generic_category()),"known native failure");errno=EDOM;try{__wrap___cxa_throw(p,(void*)&typeid(std::system_error),destroy_system);}catch(const std::system_error&e){assert(e.code().value()==code&&strstr(e.what(),"known native failure"));return;}assert(false);}
int main(){assert(!strcmp(typeid(std::system_error).name(),"NSt3__112system_errorE"));interrupted=true;send_system(12);assert(destroyed==1&&output.find("type=NSt3__112system_errorE system_error=1 code=12")!=std::string::npos&&opens==1&&closes==1);deny_open=true;send_system(22);assert(destroyed==2&&opens==2&&closes==1);deny_open=false;
 void*p=__cxxabiv1::__cxa_allocate_exception(sizeof(int));new(p)int(42);errno=EDOM;try{__wrap___cxa_throw(p,(void*)&typeid(int),nullptr);}catch(int n){assert(n==42);}assert(output.find("type=i system_error=0 code=0")!=std::string::npos);
 for(int i=0;i<150;i++)send_system(i);assert(opens==128&&closes==127&&destroyed==152);puts("PASS actual throw recorder:originalC++ABI type/code/message/destruction preserved,exactsystem_error/non-systemtypes,errno,partialwrites/EINTR/openfailure,128eventcap");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(s);exe=d/'test';subprocess.run(['clang++','-std=c++20','-fsanitize=address,undefined',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
