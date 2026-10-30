#!/usr/bin/env python3
"""Exercise the actual adapted HTTP handler and target policy without PS5 access."""
from pathlib import Path
import argparse,subprocess,tempfile
from build_client_crash_capture import scoped_source
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-cache',type=Path,required=True);a=p.parse_args()
text=scoped_source((a.source_cache/'payload/main.c').read_text())
watch=text[text.index('static bool watch_policy('):];watch=watch[:watch.index('\nstatic ',1)]
serve=text[text.index('static void serve(int fd)'):text.index('\nint main(void)')]
fixture=r'''
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>
static int response,called,detached;
static void reply_text(int fd,int status,const char* type,const char* body){response=status;}
static void reply(int fd,int status,const char* type,const char* body,size_t n){response=status;}
static void api_status(int fd){called=1;}
static void api_memory(int fd,const char*q){called=2;}
static void api_crashes(int fd){called=3;}
static void api_crash(int fd,const char*id,bool remove){assert(!remove);called=4;}
static char* read_file(const char*p,size_t*n,size_t limit){*n=0;return NULL;}
static void detach_all(int timeout){assert(timeout==5000);detached++;}
static int traced_count(void){return 0;}
static const char dashboard_html[]="fixture",dashboard_html_end[]={0};
#define LOG_PATH "fixture"
'''
driver=r'''
static void request(const char* method,const char* target,int expected,int api){
 int fd[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,fd));char request[512];
 int n=snprintf(request,sizeof(request),"%s %s HTTP/1.0\r\n\r\n",method,target);assert(write(fd[0],request,n)==n);
 shutdown(fd[0],SHUT_WR);response=called=0;serve(fd[1]);close(fd[0]);assert(response==expected&&called==api);
}
int main(void){
 assert(watch_policy("PPSA99874"));
 for(const char**s=(const char*[]){"PPSA00000","NPXS00000","all","none","PPSA998740","",NULL};*s;s++)assert(!watch_policy(*s));
 request("GET","/api/status",0,1);request("GET","/api/memory",0,2);request("GET","/api/crashes",0,3);request("GET","/api/crash/fixture",0,4);
 request("DELETE","/api/crash/fixture",405,0);request("POST","/api/test/fault?pid=1",405,0);request("GET","/api/test/fault?pid=1",404,0);
 request("GET","/api/errors",404,0);request("POST","/api/status",405,0);request("POST","/api/quit",200,0);assert(detached==1);
 puts("PASS actual adapted capture handler:target-only policy;GET status/memory/crash;no DELETE/test-fault/error-history;quit detaches;ASan/UBSan");
}
'''
with tempfile.TemporaryDirectory() as d:
 w=Path(d);(w/'check.c').write_text(fixture+watch+serve+driver)
 subprocess.run(['clang','-std=gnu11','-fsanitize=address,undefined','-Wno-unused-function',str(w/'check.c'),'-o',str(w/'check')],check=True)
 subprocess.run([str(w/'check')],check=True)
