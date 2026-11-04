/* SPDX-License-Identifier: MIT */
#include <ffi.h>
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>
static _Atomic int refuse,fail_rx,fail_rw,maps,fail_after;
void*test_mmap(void*a,size_t n,int p,int f,int d,off_t o){int e=atomic_load(&refuse);if(atomic_load(&fail_after)&&atomic_fetch_add(&maps,1)>=atomic_load(&fail_after))e=ENOMEM;if(e){errno=e;return MAP_FAILED;}return mmap(a,n,p,f,d,o);}
int test_mprotect(void*a,size_t n,int p){if((p&PROT_EXEC)?atomic_load(&fail_rx):atomic_load(&fail_rw)){errno=EACCES;return -1;}return mprotect(a,n,p);}
extern int prospero_ffi_reserve_prime(void);
static void add(ffi_cif*c,void*r,void**a,void*d){(void)c;*(ffi_arg*)r=(ffi_arg)(*(int*)a[0]+*(int*)a[1]+(int)(intptr_t)d);}
static void exercise(void){
 ffi_cif cif;ffi_type*types[]={&ffi_type_sint,&ffi_type_sint};assert(ffi_prep_cif(&cif,FFI_DEFAULT_ABI,2,&ffi_type_sint,types)==FFI_OK);
 void*code;ffi_closure*c=ffi_closure_alloc(sizeof(*c),&code);assert(c&&code==c);assert(ffi_prep_closure_loc(c,&cif,add,(void*)3,code)==FFI_OK);assert(((int(*)(int,int))code)(20,22)==45);assert(ffi_prep_closure_loc(c,&cif,add,NULL,code)!=FFI_OK);ffi_closure_free(c);
}
static void*worker(void*unused){(void)unused;for(int i=0;i<200;i++)exercise();return NULL;}
int main(int argc,char**argv){
 (void)argv;
 if(argc>1){atomic_store(&fail_after,3);assert(prospero_ffi_reserve_prime()==ENOMEM);assert(prospero_ffi_reserve_prime()==EBUSY);void*code=(void*)1;atomic_store(&refuse,ENOMEM);assert(!ffi_closure_alloc(sizeof(ffi_closure),&code)&&!code);puts("PASS incomplete bootstrap pool remains unpublished/owned;repeat prime rejected");return 0;}
 void*code=(void*)1;atomic_store(&refuse,ENOMEM);assert(!ffi_closure_alloc(sizeof(ffi_closure),&code)&&!code);atomic_store(&refuse,0);assert(prospero_ffi_reserve_prime()==0);assert(prospero_ffi_reserve_prime()==EBUSY);
 atomic_store(&refuse,EACCES);assert(!ffi_closure_alloc(sizeof(ffi_closure),&code)&&!code&&errno==EACCES);atomic_store(&refuse,ENOMEM);
 ffi_closure*all[64];for(int i=0;i<64;i++){all[i]=ffi_closure_alloc(sizeof(ffi_closure),&code);assert(all[i]&&code==all[i]);}assert(!ffi_closure_alloc(sizeof(ffi_closure),&code)&&!code&&errno==ENOMEM);for(int i=0;i<64;i++)ffi_closure_free(all[i]);
 pthread_t threads[16];for(int i=0;i<16;i++)assert(!pthread_create(&threads[i],NULL,worker,NULL));for(int i=0;i<16;i++)assert(!pthread_join(threads[i],NULL));
 ffi_cif cif;ffi_type*types[]={&ffi_type_sint,&ffi_type_sint};assert(ffi_prep_cif(&cif,FFI_DEFAULT_ABI,2,&ffi_type_sint,types)==FFI_OK);
 ffi_cif bad=cif;bad.abi=(ffi_abi)-1;ffi_closure*c=ffi_closure_alloc(sizeof(*c),&code);assert(ffi_prep_closure_loc(c,&bad,add,NULL,code)!=FFI_OK);ffi_closure_free(c);exercise();
 c=ffi_closure_alloc(sizeof(*c),&code);atomic_store(&fail_rx,1);assert(ffi_prep_closure_loc(c,&cif,add,NULL,code)!=FFI_OK);atomic_store(&fail_rx,0);ffi_closure_free(c);exercise();
 c=ffi_closure_alloc(sizeof(*c),&code);assert(ffi_prep_closure_loc(c,&cif,add,NULL,code)==FFI_OK);atomic_store(&fail_rw,1);ffi_closure_free(c);atomic_store(&fail_rw,0);ffi_closure_free(c); /* retained page, never reused */
 for(int i=0;i<63;i++){all[i]=ffi_closure_alloc(sizeof(*c),&code);assert(all[i]);}assert(!ffi_closure_alloc(sizeof(*c),&code));for(int i=0;i<63;i++)ffi_closure_free(all[i]);
 puts("PASS real libffi reserve:bootstrap64/exhaust/reuse,3200concurrent native closures,ENOMEM-only fallback,unprimed/EACCES rejection,RX failure recovery,RW failure quarantine");
}
