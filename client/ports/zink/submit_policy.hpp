/* SPDX-License-Identifier: MIT */
#pragma once
#include <cerrno>
#include <cstdlib>
#include <cstring>
namespace prospero_zink {
// Candidate-only upstream setting, applied once before the first Zink screen.
// Existing diagnostic tokens remain intact. Never print environment contents.
inline int enable_flushsync(int (*setter)(const char*,const char*,int)=::setenv){
 const char* current=std::getenv("ZINK_DEBUG");
 if(current){
  const char* p=current;
  while(*p){while(*p==' '||*p==','||*p=='\t'||*p=='\n')++p;const char* start=p;
   while(*p&&*p!=' '&&*p!=','&&*p!='\t'&&*p!='\n')++p;
   if(p-start==9&&std::memcmp(start,"flushsync",9)==0)return 0;
  }
 }
 char selected[512];std::size_t n=current?std::strlen(current):0;
 if(n>sizeof(selected)-12)return E2BIG;
 if(n){std::memcpy(selected,current,n);selected[n++]=',';}
 std::memcpy(selected+n,"flushsync",10);
 if(setter("ZINK_DEBUG",selected,1)!=0)return errno?errno:EIO;
 return 0;
}
}
