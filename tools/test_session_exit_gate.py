#!/usr/bin/env python3
"""Actual native clean-exit arm/status/one-shot ownership gate."""
import os,subprocess,tempfile
from pathlib import Path
from host_toolchain import ROOT,executable

def main():
 with tempfile.TemporaryDirectory(prefix='prospero-exit-gate-')as folder:
  w=Path(folder);source=w/'check.cpp';source.write_text(r'''#include <cassert>
#include <thread>
#include <vector>
#include "session_restart.hpp"
int main(){
 prospero_session::CleanExitGate gate;assert(!gate.take(0));gate.arm();assert(!gate.take(7));assert(!gate.take(0));
 gate.arm();assert(gate.take(0));assert(!gate.take(0));gate.arm();assert(!gate.take(-1));
 for(int n=0;n<100;n++){gate.arm();std::atomic<int> wins{0};std::vector<std::thread> ts;
  for(int i=0;i<8;i++)ts.emplace_back([&]{if(gate.take(0))wins++;});for(auto& t:ts)t.join();assert(wins==1);}
}
''')
  subprocess.run([executable('clang++',env='CXX'),'-std=c++20','-pthread','-fsanitize=address,undefined','-I'+str(ROOT/'client/startup'),source,'-o',w/'check'],check=True)
  subprocess.run([w/'check'],check=True,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS actual native clean-exit gate: unarmed/error refusal, error consumption, exactly one concurrent owner, ASan/UBSan; OS replacement remains console pending')
if __name__=='__main__':main()
