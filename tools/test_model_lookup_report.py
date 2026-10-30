#!/usr/bin/env python3
"""Compile actual startup lookup-report formatting with real bounded resolver fixtures."""
from pathlib import Path
import argparse,subprocess,tempfile
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args()
s=(r/'client/startup/bootstrap.cpp').read_text();start=s.index(' char model_status[2048];');end=s.index('\n\n sceUserServiceInitialize',start);actual=s[start:end]
code=r'''
#include <cassert>
#include <cstdio>
#include <cstring>
#include <climits>
#include "console_model.hpp"
#define PROSPERO_APP_VERSION "01.000.157"
static char captured[2048];
namespace ps5::log_share {static void write_note(const char*,const char* p){assert(std::strlen(p)<sizeof(captured));std::strcpy(captured,p);}}
static int list(int* p,std::size_t size,std::size_t* n){assert(size==512);*n=512;for(int i=0;i<512;i++)p[i]=100+i;return 0;}
static int query(char* p){std::strcpy(p,"CFI-2014 A01X");return 0;}
static bool hit=false;
static int resolver(int handle,const char* name,void** out){*out=nullptr;if(hit&&handle==611&&!std::strcmp(name,"JC7I7J1bllQ")){*out=reinterpret_cast<void*>(query);return 0;}return INT_MIN;}
static void run(){auto model_query=ps5::console::resolve_loaded_query(resolver,list);auto console_identity=ps5::console::read(model_query.query);
'''+actual+r'''
 assert(std::strstr(captured,"PS5_HARDWARE"));assert(std::strstr(captured,"attempts=514"));
 assert(std::strstr(captured,"PS5_MODEL_LOOKUP handle=1 "));assert(std::strstr(captured,"name_rc=-2147483648"));
 const char* pos=captured;int records=0;while((pos=std::strstr(pos,"PS5_MODEL_LOOKUP"))){records++;pos++;}assert(records==8);
 if(hit)assert(std::strstr(captured,"status=4")&&std::strstr(captured,"resolver_handle=611")&&std::strstr(captured,"by_nid=1"));
 else assert(std::strstr(captured,"status=0")&&std::strstr(captured,"model unknown"));
 assert(!std::strstr(captured,"CFI-")&&!std::strstr(captured,"0x"));
}
int main(){run();hit=true;run();puts("PASS actual native lookup report:514attempts/8records,success/unknown,spaced model,NID path,integer extremes,bounded ASCII/no raw model or pointers");}
'''
with tempfile.TemporaryDirectory(prefix='model-report-')as t:
 w=Path(t);(w/'check.cpp').write_text(code)
 subprocess.run(['clang++','-std=c++20','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(a.runtime_workspace/'java25/platform'),str(w/'check.cpp'),'-o',str(w/'check')],check=True)
 subprocess.run([str(w/'check')],check=True)
