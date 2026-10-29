/* SPDX-License-Identifier: Zlib
 * Shader compiler initialization locks backed by reserved native SDL mutexes.
 * Constant initialization; no SDK lazy mutex allocation after JVM startup.
 */
#pragma once
#include <cstdlib>
#include <SDL3/SDL.h>
extern "C" void client_gpu_stage(const char*,int);
class PS5ShaderInitMutex {
 SDL_Mutex* value_;
 SDL_Mutex* get(){
  SDL_Mutex* value=__atomic_load_n(&value_,__ATOMIC_ACQUIRE);
  if(value)return value;
  SDL_Mutex* next=SDL_CreateMutex();
  if(!next){client_gpu_stage("Shader compiler native mutex reserve exhausted",-1);std::abort();}
  SDL_Mutex* expected=nullptr;
  if(!__atomic_compare_exchange_n(&value_,&expected,next,false,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE)){
   SDL_DestroyMutex(next);return expected;
  }
  return next;
 }
public:
 constexpr PS5ShaderInitMutex() noexcept:value_(nullptr){}
 PS5ShaderInitMutex(const PS5ShaderInitMutex&)=delete;
 PS5ShaderInitMutex& operator=(const PS5ShaderInitMutex&)=delete;
 // The three initialization locks persist until process exit. A trivial
 // destructor keeps static initialization free of SDK lazy guard/destructor paths.
 ~PS5ShaderInitMutex()=default;
 void lock(){SDL_LockMutex(get());}
 void unlock(){SDL_UnlockMutex(__atomic_load_n(&value_,__ATOMIC_ACQUIRE));}
};
