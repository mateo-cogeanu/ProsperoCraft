#!/usr/bin/env python3
"""Exercise real signal forwarding and the opt-in diagnostic report budget."""
import argparse
from pathlib import Path
import os
import subprocess
import tempfile
from host_toolchain import ROOT, executable


def main():
    if not __debug__:
        raise RuntimeError('Run fault controls without Python optimization')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cc')
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix='prosperocraft-fault-budget-') as folder:
        root = Path(folder)
        source = root / 'test.c'
        source.write_text(r'''
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
int ps5shaderc_fault_begin(void);void ps5shaderc_fault_end(void);
static volatile sig_atomic_t forwarded;
static void prior(int sig){assert(sig==SIGFPE);++forwarded;}
int main(int argc,char**argv){
 assert(argc==2);assert(!setenv("PROSPERO_DIAGNOSTIC_ROOT",argv[1],1));
 struct sigaction action={0};action.sa_handler=prior;sigemptyset(&action.sa_mask);
 assert(!sigaction(SIGFPE,&action,0));assert(ps5shaderc_fault_begin()==4);
 for(int i=0;i<20;++i)assert(!raise(SIGFPE));
 assert(forwarded==20);ps5shaderc_fault_end();assert(!raise(SIGFPE));assert(forwarded==21);
 char path[1024];snprintf(path,sizeof(path),"%s/java25-vm-trace.log",argv[1]);
 FILE*f=fopen(path,"r");assert(f);char line[256];int reports=0;
 while(fgets(line,sizeof(line),f))if(strstr(line,"SHADERC FAULT signal="))++reports;
 fclose(f);assert(reports==2);
 puts("PASS real20signals forwarded despite2report budget; previous handler restored; ASan/UBSan. Context capture disabled only in host policy fixture.");
}
''')
        target = root / 'test'
        subprocess.run([executable('clang', override=a.cc, env='CC'), '-std=c11','-O1','-g',
            '-D_POSIX_C_SOURCE=200809L','-DPS5_SHADERC_CONTEXT_WORDS=0','-DPS5_SHADERC_MAX_REPORTS=2',
            '-fsanitize=address,undefined',str(ROOT / 'client/ports/shaderc/fault.c'),str(source),
            '-o',str(target)], check=True)
        subprocess.run([str(target),str(root)], check=True,
            env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})


if __name__ == '__main__':
    main()
