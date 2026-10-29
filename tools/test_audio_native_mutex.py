#!/usr/bin/env python3
"""Actual scoped audio mutex with standard C++ lock guards and native contention."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <mutex>
#include <thread>
#include <vector>
#include <atomic>
#include <type_traits>
#include <cassert>
#include <cstdio>
#include "ps5_audio_mutex.hpp"
static_assert(std::is_trivially_destructible_v<ps5audio::Mutex>);
int main(){ps5audio::Mutex mutex;assert(mutex.try_lock());assert(!mutex.try_lock());mutex.unlock();long value=0;
 std::vector<std::thread>threads;for(int i=0;i<8;i++)threads.emplace_back([&]{for(int j=0;j<10000;j++){std::lock_guard lock(mutex);value++;}});
 for(auto&t:threads)t.join();assert(value==80000);
 std::unique_lock first(mutex);std::atomic<bool>started=false,entered=false;
 std::thread other([&]{started=true;std::unique_lock second(mutex);entered=true;});while(!started){}assert(!entered);first.unlock();other.join();assert(entered);
 puts("PASS actual audio inline mutex:standard guard/unique-lock,try behavior,80000contended increments/blocking/data visibility,trivial lifetime;ASan/UBSan");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(code);exe=d/'test';subprocess.run(['clang++','-std=c++17','-O2','-pthread','-fsanitize=address,undefined','-I'+str(r/'client/ports/openal'),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True,timeout=30)
