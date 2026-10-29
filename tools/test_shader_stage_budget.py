#!/usr/bin/env python3
"""Exact log budget under concurrent calls, keeping every failure/unrelated stage."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
code=r'''
#include <atomic>
#include <thread>
#include <vector>
#include <cassert>
#include <cstdio>
#include "shader_stage_budget.hpp"
int main(){ShaderStageBudget b;std::atomic<int>records=0,suppressed=0,notice=0;
 std::vector<std::thread>threads;
 for(int i=0;i<8;i++)threads.emplace_back([&]{for(int j=0;j<10000;j++){auto d=b.admit("shaderc: before compile",INT_MIN);records+=d==b.Record;notice+=d==b.FirstSuppressed;suppressed+=d==b.Suppress;}});
 for(auto&t:threads)t.join();assert(records==256&&notice==1&&suppressed==80000-257&&b.seen==257);
 for(auto*name:{"shaderc: message","compiler: message","glslang: message","Compiler fault recorder installed (expected4)"})assert(b.admit(name,0)==b.Suppress);
 for(int i=0;i<10000;i++){assert(b.admit("shaderc: compilation failed",-1)==b.Record);assert(b.admit("glslang: positive error",12)==b.Record);assert(b.admit("WSI present",INT_MIN)==b.Record);assert(b.admit("native fatal",0)==b.Record);}
 assert(b.admit(nullptr,0)==b.Record&&b.seen==257);
 puts("PASS actual shader stage budget:80000concurrent calls,256details/1notice/saturating counter;every error and unrelated stage preserved;ASan/UBSan");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.cpp';p.write_text(code);exe=d/'test'
 subprocess.run(['clang++','-std=c++17','-O2','-pthread','-fsanitize=address,undefined','-I'+str(r/'client/startup'),str(p),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True,timeout=20)
