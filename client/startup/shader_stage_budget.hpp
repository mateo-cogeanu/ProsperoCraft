/* SPDX-License-Identifier: GPL-3.0-or-later
 * Keep finite detailed shader traces so fatal/native checkpoints survive tails.
 * Failure stages and all unrelated stages always remain visible.
 */
#pragma once
#include <cstring>
#include <climits>
struct ShaderStageBudget {
 unsigned seen=0;
 enum Decision { Record, Suppress, FirstSuppressed };
 Decision admit(const char* name,int code) {
  if(code!=INT_MIN && code!=0)return Record;
  bool shader=name && (!std::strncmp(name,"shaderc:",8)||!std::strncmp(name,"compiler:",9)||!std::strncmp(name,"glslang:",8)||!std::strncmp(name,"Compiler fault recorder installed",sizeof("Compiler fault recorder installed")-1));
  if(!shader)return Record;
  unsigned n=__atomic_load_n(&seen,__ATOMIC_RELAXED);
  while(n<=256 && !__atomic_compare_exchange_n(&seen,&n,n+1,false,__ATOMIC_RELAXED,__ATOMIC_RELAXED)){}
  if(n<256)return Record;
  return n==256?FirstSuppressed:Suppress;
 }
};
