/* SPDX-License-Identifier: Zlib
 * Consumer diagnostic wrapper: record original native C++ throw before
 * termination/demangling can obscure its cause. Preserve original throw ABI.
 */
#include <typeinfo>
#include <system_error>
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
extern "C" [[noreturn]] void __real___cxa_throw(void*,void*,void(*)(void*));
static unsigned events;
static void record_throw(void* object,const std::type_info* type,const void* caller)
{
 int saved=errno;
 if(__atomic_fetch_add(&events,1,__ATOMIC_RELAXED)<128){
  const char* name=type?type->name():"<null>";
  const char* message="";
  int system_code=0;bool known_system_error=false;
  // Exact SDK libc++ ABI type; never reinterpret arbitrary exception types.
  if(object && !std::strcmp(name,"NSt3__112system_errorE")){
   known_system_error=true;message=static_cast<const std::system_error*>(object)->what();system_code=static_cast<const std::system_error*>(object)->code().value();
  }
  char text[512];
  int n=std::snprintf(text,sizeof(text),"PS5_CPP_THROW caller=%p anchor=%p type=%.240s system_error=%d code=%d message=%.160s\n",caller,(void*)&record_throw,name,known_system_error?1:0,system_code,message);
  if(n>0){
   size_t length=(size_t)n<sizeof(text)?(size_t)n:sizeof(text)-1;
   int fd=open("/download0/java25-startup.log",O_WRONLY|O_APPEND);
   if(fd>=0){size_t done=0;while(done<length){ssize_t count=write(fd,text+done,length-done);if(count>0)done+=(size_t)count;else if(count<0&&errno==EINTR)continue;else break;}close(fd);}
  }
 }
 errno=saved;
}
extern "C" [[noreturn]] void __wrap___cxa_throw(void* object,void* type,void(*destructor)(void*))
{
 record_throw(object,static_cast<const std::type_info*>(type),__builtin_return_address(0));
 __real___cxa_throw(object,type,destructor);
}
