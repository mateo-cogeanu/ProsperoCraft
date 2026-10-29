#!/usr/bin/env python3
"""Exact bounded input-triggered presentation budget; no controller state mutation."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <thread>
#include <vector>
#include <atomic>
#include <cassert>
#include <cstdio>
#include "input_present_trace.hpp"
int main(){InputPresentBudget b;assert(!b.input(0)&&!b.probe(false));assert(b.input(1)==1&&!b.input(1));
 int frames=0;while(b.probe(true))frames++;assert(frames==8&&!b.probe(false));
 for(unsigned i=2;i<=8;i++){assert(b.input(i)==i);assert(b.probe(false));for(int j=0;j<8;j++)assert(b.probe(true));assert(!b.probe(true));}
 for(unsigned i=9;i<100000;i++)assert(!b.input(i));assert(b.changes==8&&!b.probe(true));
 InputPresentBudget parallel;std::atomic<int>changes=0,taken=0;std::vector<std::thread>threads;
 for(int i=0;i<8;i++)threads.emplace_back([&]{changes+=parallel.input(55)!=0;});for(auto&t:threads)t.join();assert(changes==1);threads.clear();
 for(int i=0;i<8;i++)threads.emplace_back([&]{while(parallel.probe(true))taken++;});for(auto&t:threads)t.join();assert(taken==8&&!parallel.probe(false));
 puts("PASS actual input/present diagnostic budget:change dedup,8changesx8frames maximum,saturation,concurrentduplicate inputs/exact shared consumption;ASan/UBSan");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(code);exe=d/'test';subprocess.run(['clang++','-std=c++17','-O2','-pthread','-fsanitize=address,undefined','-I'+str(r/'client/startup'),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True,timeout=20)
