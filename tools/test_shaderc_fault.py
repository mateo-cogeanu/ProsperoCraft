#!/usr/bin/env python3
"""Exercise real fault recorder delegation/restoration in isolated host children."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
HARNESS=r'''
#include <signal.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
int ps5shaderc_fault_begin(void);
void ps5shaderc_fault_end(void);
unsigned ps5shaderc_fault_status(unsigned *);
unsigned ps5shaderc_fault_extended_status(unsigned*);
static void* nested_worker(void*unused){(void)unused;for(int i=0;i<1000;i++){if(ps5shaderc_fault_begin()!=4||ps5shaderc_fault_extended_status(0)!=127)_exit(17);ps5shaderc_fault_end();}return 0;}
static void old_one(int sig){_exit(sig==SIGILL?73:75);}
static void old_three(int sig,siginfo_t*info,void*context){_exit(sig==SIGSEGV&&info&&context?74:76);}
int main(int argc,char**argv){
 if(argc!=2)return 1;
 struct sigaction action={0},current;
 action.sa_handler=old_one;sigemptyset(&action.sa_mask);sigaddset(&action.sa_mask,SIGUSR1);
 if(sigaction(SIGILL,&action,0))return 2;
 int mode=atoi(argv[1]);
 if(mode==2||mode==4){action.sa_sigaction=old_three;action.sa_flags=SA_SIGINFO;if(sigaction(SIGSEGV,&action,0))return 3;}
 if(mode>=6&&mode<=8){
  action.sa_handler=old_one;action.sa_flags=0;
  if(sigaction(mode==6?SIGFPE:mode==7?SIGTRAP:SIGSYS,&action,0))return 13;
 }
 if(ps5shaderc_fault_begin()!=4)return 4;
 if(ps5shaderc_fault_extended_status(0)!=127)return 14;
 if(mode==9){pthread_t threads[8];for(int i=0;i<8;i++)if(pthread_create(&threads[i],0,nested_worker,0))return 15;for(int i=0;i<8;i++)if(pthread_join(threads[i],0))return 16;}
 if(mode>=6&&mode<=8)raise(mode==6?SIGFPE:mode==7?SIGTRAP:SIGSYS);
 unsigned errors=99;errno=EDOM;
 if(ps5shaderc_fault_status(&errors)!=15||errors||errno!=EDOM)return 9;
 if(mode==5){
  action.sa_handler=old_one;action.sa_flags=0;
  if(sigaction(SIGILL,&action,0))return 10;
  if(ps5shaderc_fault_status(&errors)!=11||errors)return 11;
  if(sigaction(SIGILL,0,&current)||current.sa_handler!=old_one)return 12;
  ps5shaderc_fault_end();return 0;
 }
 if(mode==3||mode==4){
  if(ps5shaderc_fault_begin()!=4)return 8;
  ps5shaderc_fault_end(); // Compiler scope ends,outer startup scope remains.
  raise(mode==3?SIGILL:SIGSEGV);
 }
 if(mode==1)raise(SIGILL);
 if(mode==2)raise(SIGSEGV);
 if(ps5shaderc_fault_begin()!=4)return 5;
 ps5shaderc_fault_end();
 if(sigaction(SIGILL,0,&current)||current.sa_handler==old_one)return 6;
 ps5shaderc_fault_end();
 if(sigaction(SIGILL,0,&current)||current.sa_handler!=old_one||!sigismember(&current.sa_mask,SIGUSR1))return 7;
 ps5shaderc_fault_end();
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='shaderc-fault-')as folder:
 w=Path(folder);(w/'test.c').write_text(HARNESS);report=w/'report.log'
 # Desktop ucontext layouts differ; test only four guaranteed initial words.
 # Target intentionally records96 raw words using its pinned SDK probe range.
 subprocess.run(['clang','-std=c11','-D_GNU_SOURCE','-Wall','-Wextra','-Werror','-DPS5_SHADERC_CONTEXT_WORDS=4','-DPS5_SHADERC_FAULT_LOG="'+str(report)+'"',str(ROOT/'client/ports/shaderc/fault.c'),str(w/'test.c'),'-pthread','-o',str(w/'test')],check=True)
 subprocess.run([str(w/'test'),'0'],check=True)
 subprocess.run([str(w/'test'),'5'],check=True)
 subprocess.run([str(w/'test'),'9'],check=True)
 for mode,code in [('1',73),('2',74),('3',73),('4',74),('6',75),('7',75),('8',75)]:
  report.unlink(missing_ok=True)
  result=subprocess.run([str(w/'test'),mode]);assert result.returncode==code,result.returncode
  data=report.read_text();assert 'SHADERC FAULT signal='in data and 'SHADERC FAULT address='in data
  assert data.count('SHADERC FAULT context-word=')==4,data
 print('PASS real fault recorder: read-only handler ownership/displacement without reinstallation and errno preservation,8000concurrent nested leases/atomic guard,install/restoration/mask preservation,outer startup scope survives compiler end, SIGILL/FPE/TRAP/SYS one-argument and SIGSEGV SA_SIGINFO delegation with legacy4bit/extended7bit ownership, bounded raw context written before original handler; no recovery. PS5 context capture pending.')
