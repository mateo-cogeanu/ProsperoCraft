#!/usr/bin/env python3
"""Test actual bounded native-port ownership under simulated reopen allocation failure."""
from pathlib import Path
from host_toolchain import executable
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=r'''
#include "ps5_port_pool.hpp"
#include <cassert>
#include <cstdio>
#include <thread>
int main(){ps5audio::PortPool pool;int native_opens=1,native_closes=0;int port=17;
 for(int reload=0;reload<100;reload++){assert(pool.keep(port));port=pool.take();assert(port==17);/* Native open would fail after initial pre-JVM allocation. */}
 assert(native_opens==1&&native_closes==0);assert(pool.keep(port));if(!pool.keep(18))native_closes++;assert(native_closes==1&&pool.take()==17&&pool.take()==-1&&!pool.keep(-1));
 std::thread a([&]{for(int i=0;i<10000;i++){int p=pool.take();if(p>=0)assert(pool.keep(p));}});std::thread b([&]{for(int i=0;i<10000;i++){int p=pool.take();if(p>=0)assert(pool.keep(p));}});assert(pool.keep(19));a.join();b.join();assert(pool.take()==19);
 puts("PASS actual port pool:100 reloads preserve single preallocated port despite later allocation failure;bounded spare ownership,extra close/invalid rejection and concurrent claims");}
'''
with tempfile.TemporaryDirectory(prefix='audio-retain-')as folder:
 w=Path(folder);(w/'test.cpp').write_text(source);subprocess.run([executable('clang++', env='CXX'),'-std=c++20','-fsanitize=address,undefined','-pthread','-I'+str(ROOT/'client/ports/openal'),str(w/'test.cpp'),'-o',str(w/'test')],check=True);subprocess.run([str(w/'test')],check=True)
