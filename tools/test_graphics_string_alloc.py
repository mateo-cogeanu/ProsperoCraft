#!/usr/bin/env python3
"""Actual Mesa XSTRDUP macro with scoped string allocation and libc refusal."""
from pathlib import Path
import subprocess,tempfile,os,signal
r=Path(__file__).resolve().parents[1];mesa=(r/'.tools/PS5_Mesa/src/util/xmlconfig.c').read_text();a=mesa.index('#define XSTRDUP');b=mesa.index('/**',a);macro=mesa[a:b]
s=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
char*clientgpu_strdup(const char*);char*clientgpu_strndup(const char*,size_t);
static int old_path,deny_graphics;static unsigned allocations,frees;
void*clientgpu___wrap_malloc(size_t n){if(deny_graphics)return NULL;void*p=malloc(n);if(p)allocations++;return p;}
static char*route_strdup(const char*s){if(old_path){errno=ENOMEM;return NULL;}return clientgpu_strdup(s);}
#define strdup route_strdup
'''+macro+r'''
static void release(char*p){if(p){frees++;free(p);}}
int main(int argc,char**argv){(void)argv;old_path=argc>1;char*p;XSTRDUP(p,"radv_disable_htile");assert(!strcmp(p,"radv_disable_htile"));release(p);
 p=clientgpu_strdup("");assert(p&&!p[0]);release(p);p=clientgpu_strdup("name \xc2\xa7 pack");assert(p&&!strcmp(p,"name \xc2\xa7 pack"));release(p);
 char bounded[3]={'x','y','z'};p=clientgpu_strndup(bounded,3);assert(p&&!strcmp(p,"xyz"));release(p);p=clientgpu_strndup("abc",0);assert(p&&!p[0]);release(p);p=clientgpu_strndup("abc",SIZE_MAX);assert(p&&!strcmp(p,"abc"));release(p);
 for(int i=0;i<10000;i++){XSTRDUP(p,"radv_driver_option");assert(p&&!strcmp(p,"radv_driver_option"));release(p);}deny_graphics=1;errno=0;assert(!clientgpu_strdup("x")&&errno==ENOMEM);assert(!clientgpu_strndup("x",1)&&errno==ENOMEM);assert(allocations==frees);puts("PASS actual Mesa XSTRDUP through paired graphics string allocator;empty/Unicode/boundednonterminated/zero+SIZE_MAXlimit,10000cycles,failureerrno,completecleanup");}
'''
with tempfile.TemporaryDirectory()as d:
 d=Path(d);p=d/'test.c';p.write_text(s);exe=d/'test';subprocess.run(['clang','-std=c11','-fsanitize=address,undefined',str(p),str(r/'client/gpu/string_alloc.c'),'-o',str(exe)],check=True)
 old=subprocess.run([str(exe),'old-libc-route'],capture_output=True);assert old.returncode==-signal.SIGABRT and b'out of memory' in old.stderr,old.stderr
 subprocess.run([str(exe)],check=True)
print('PASS old libc-duplication refusal reproduces actual Mesa macro abort;new route succeeds with graphics allocator')
