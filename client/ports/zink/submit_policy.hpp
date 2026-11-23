/* SPDX-License-Identifier: MIT */
#pragma once
#include <cerrno>
#include <cstdlib>
#include <cstring>
namespace prospero_zink {
// Candidate-only upstream setting, applied once before the first Zink screen.
// Existing diagnostic tokens remain intact. Never print environment contents.
inline int append_driver_option(const char* variable,const char* option,int (*setter)(const char*,const char*,int)){
 const auto length=std::strlen(option);
 const char* current=std::getenv(variable);
 if(current){
  const char* p=current;
  while(*p){while(*p==' '||*p==','||*p=='\t'||*p=='\n')++p;const char* start=p;
   while(*p&&*p!=' '&&*p!=','&&*p!='\t'&&*p!='\n')++p;
   if(static_cast<std::size_t>(p-start)==length&&std::memcmp(start,option,length)==0)return 0;
  }
 }
 char selected[512];std::size_t n=current?std::strlen(current):0;
 if(length>sizeof(selected)-3||n>sizeof(selected)-length-3)return E2BIG;
 if(n){std::memcpy(selected,current,n);selected[n++]=',';}
 std::memcpy(selected+n,option,length+1);
 if(setter(variable,selected,1)!=0)return errno?errno:EIO;
 return 0;
}
inline int enable_debug_option(const char* option,int (*setter)(const char*,const char*,int)){
 return append_driver_option("ZINK_DEBUG",option,setter);
}
inline int disable_radv_hiz(int (*setter)(const char*,const char*,int)=::setenv){
 return append_driver_option("RADV_DEBUG","nohiz",setter);
}
inline int enable_flushsync(int (*setter)(const char*,const char*,int)=::setenv){
 return enable_debug_option("flushsync",setter);
}
inline int disable_shader_objects(int (*setter)(const char*,const char*,int)=::setenv){
 return enable_debug_option("noshobj",setter);
}
inline int disable_background_compilation(int (*setter)(const char*,const char*,int)=::setenv){
 return enable_debug_option("nobgc",setter);
}
// Use Mesa's genuine direct pipe context; no gdrv queue or substitute GL calls.
inline int enable_synchronous_context(int (*setter)(const char*,const char*,int)=::setenv){
 const char* current=std::getenv("GALLIUM_THREAD");
 if(current&&std::strcmp(current,"0")==0)return 0;
 if(setter("GALLIUM_THREAD","0",1)!=0)return errno?errno:EIO;
 return 0;
}

}
