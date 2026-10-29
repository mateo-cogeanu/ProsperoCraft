#!/usr/bin/env python3
"""Actual mutex tracer forwarding native lock behavior, throws and bounded logging."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=r'''
#include <mutex>
#include <thread>
#include <atomic>
#include <system_error>
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <cassert>
#include <string>
static std::string output;static unsigned opens,closes,forwarded;static bool fail_open,interrupt_write;static int sentinel;
static int test_open(const char*p,int f,...){assert(!strcmp(p,"/download0/java25-startup.log")&&f==(O_WRONLY|O_APPEND));opens++;if(fail_open){errno=EMFILE;return -1;}return 79;}
static ssize_t test_write(int fd,const void*p,size_t n){assert(fd==79);if(interrupt_write){interrupt_write=false;errno=EINTR;return -1;}size_t k=n>5?5:n;output.append((const char*)p,k);return k;}
static int test_close(int fd){assert(fd==79);closes++;errno=EBADF;return 0;}
#define open test_open
#define write test_write
#define close test_close
'''
s+='\n#include "'+str(r/'client/gpu/mutex_trace.cpp')+'"\n'
s+=r'''
#undef open
#undef write
#undef close
extern "C" int __real_pthread_mutex_lock(pthread_mutex_t*p){if((void*)p==&sentinel){errno=E2BIG;return ENOMEM;}return pthread_mutex_lock(p);}
extern "C" void __real__ZNSt3__15mutex4lockEv(void*p){assert(errno==EDOM);forwarded++;if(p==&sentinel)throw std::system_error(12,std::generic_category(),"mutex lock failed");static_cast<std::mutex*>(p)->lock();}
static void call(std::mutex&m){errno=EDOM;__wrap__ZNSt3__15mutex4lockEv(&m);assert(errno==EDOM);m.unlock();}
int main(){std::mutex mutex;call(mutex);assert(forwarded==1&&opens==0);ps5_cpp_mutex_trace_enable();interrupt_write=true;call(mutex);assert(opens==2&&closes==2&&output.find("phase=enter id=0")!=std::string::npos&&output.find("phase=return id=0")!=std::string::npos);errno=EDOM;try{__wrap__ZNSt3__15mutex4lockEv(&sentinel);assert(false);}catch(const std::system_error&e){assert(e.code().value()==12);}assert(output.find("phase=enter id=1")!=std::string::npos&&output.find("phase=return id=1")==std::string::npos);fail_open=true;call(mutex);assert(opens==5&&closes==3);fail_open=false;for(int i=0;i<300;i++)call(mutex);assert(opens==511&&closes==509&&forwarded==304);mutex.lock();std::atomic<bool>started=false,locked=false;std::thread thread([&]{errno=EDOM;started=true;__wrap__ZNSt3__15mutex4lockEv(&mutex);locked=true;mutex.unlock();});while(!started){}assert(!locked);mutex.unlock();thread.join();assert(locked&&forwarded==305&&opens==511);for(int i=0;i<80;i++){errno=EDOM;assert(__wrap_pthread_mutex_lock((pthread_mutex_t*)&sentinel)==ENOMEM&&errno==E2BIG);}assert(opens==575&&closes==573&&output.find("native-error-12")!=std::string::npos);assert(!__wrap_pthread_mutex_lock(mutex.native_handle()));mutex.unlock();puts("PASS actual mutex recorder:64nativefailurecap/unchangedresult+errno, disabled gate,originalnativeblocking/exclusion,unchangedthrow,unreturnedenter,errno,partialwrites/EINTR/openfailure,256callcap while all calls still forwarded");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(s);exe=d/'test';subprocess.run(['clang++','-std=c++20','-fsanitize=address,undefined','-pthread',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
