/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
struct InputPresentBudget {
 unsigned last=0,changes=0,remaining=0;
 unsigned input(unsigned mask){
  if(__atomic_exchange_n(&last,mask,__ATOMIC_RELAXED)==mask)return 0;
  unsigned n=__atomic_load_n(&changes,__ATOMIC_RELAXED);
  while(n<8&&!__atomic_compare_exchange_n(&changes,&n,n+1,false,__ATOMIC_RELAXED,__ATOMIC_RELAXED)){}
  if(n>=8)return 0;
  __atomic_store_n(&remaining,8,__ATOMIC_RELEASE);return n+1;
 }
 bool probe(bool consume){
  unsigned n=__atomic_load_n(&remaining,__ATOMIC_ACQUIRE);
  if(!consume)return n!=0;
  while(n&&!__atomic_compare_exchange_n(&remaining,&n,n-1,false,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE)){}
  return n!=0;
 }
};
