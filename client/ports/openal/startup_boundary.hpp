/* SPDX-License-Identifier: MIT */
#pragma once
#include <atomic>
#include <cerrno>
#include <cstdio>
namespace client_openal_boundary {
inline std::atomic<unsigned> issued{0};
inline void disable() noexcept {issued.store(128,std::memory_order_relaxed);}
inline unsigned reserve() {
 unsigned count=issued.load(std::memory_order_relaxed);
 while(count<128)if(issued.compare_exchange_weak(count,count+1,std::memory_order_relaxed))return count+1;
 return 0;
}
inline void record(unsigned id,const char *phase,const char *api,const void *handle,int param,int size,const void *output) {
 int saved=errno;
 std::fprintf(stderr,"PS5 OpenAL boundary id=%u phase=%s api=%s handle=%p param=0x%x size=%d output=%p\n",id,phase,api,handle,static_cast<unsigned>(param),size,output);
 std::fflush(stderr);errno=saved;
}
struct Scope {
 unsigned id;const char *api;const void *handle;int param,size;const void *output;
 Scope(const char *name,const void *value,int query=0,int count=0,const void *destination=nullptr):id(reserve()),api(name),handle(value),param(query),size(count),output(destination){if(id)record(id,"enter",api,handle,param,size,output);}
 ~Scope(){if(id)record(id,"scope-exit",api,handle,param,size,output);}
};
}
