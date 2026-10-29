#!/usr/bin/env python3
"""Actual bounded startup diagnostic writer: partial writes, EINTR, failure, errno."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
header=root/'client/ports/sdl/ps5_startup_boundary.h'
s=r'''
#include <errno.h>
#include <assert.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
static int opened,closed,calls,fail_open,interrupt_write;static unsigned bytes;
static int test_open(const char*p,int flags,...){assert(!strcmp(p,"/download0/java25-startup.log"));assert(flags==(O_WRONLY|O_APPEND));opened++;if(fail_open){errno=EMFILE;return -1;}return 7;}
static ssize_t test_write(int fd,const void*p,size_t n){assert(fd==7&&p&&n);calls++;if(interrupt_write){interrupt_write=0;errno=EINTR;return -1;}unsigned size=n>3?3:(unsigned)n;bytes+=size;return size;}
static int test_close(int fd){assert(fd==7);closed++;errno=EBADF;return 0;}
#define open test_open
#define write test_write
#define close test_close
'''
s+='\n#include "'+str(header)+'"\n'
s+=r'''
int main(void){errno=ERANGE;interrupt_write=1;PS5_BOUNDARY("fixture");assert(errno==ERANGE&&opened==1&&closed==1&&bytes==strlen("PS5_STARTUP fixture\n")&&calls>1);fail_open=1;PS5_BOUNDARY("fixture");assert(errno==ERANGE&&opened==2&&closed==1);fail_open=0;for(int i=0;i<200;i++)PS5_BOUNDARY("fixture");assert(opened==128&&closed==127);return 0;}
'''
with tempfile.TemporaryDirectory()as d:
 p=Path(d)/'test.c';p.write_text(s);exe=Path(d)/'test';subprocess.run(['clang','-std=c11','-fsanitize=address,undefined',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
print('PASS actual startup boundary writer:128callbound,partialwrites,EINTR,openfailure,pairedclose,errno preserved')
