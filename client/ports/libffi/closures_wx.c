/* Project PS5 platform allocation adapter for genuine libffi. MIT license. */
#include <ffi.h>
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>
#include <stdatomic.h>
#include <stdio.h>
#ifndef PROSPERO_FFI_RESERVE_COUNT
#define PROSPERO_FFI_RESERVE_COUNT 0
#endif
#if PROSPERO_FFI_RESERVE_COUNT > 0
/* Explicit consumer pre-JVM reserve; each real page remains independently W->X.
 * Metadata stays writable outside executable pages. No allocator/ABI policy change
 * without the build opt-in; retired/uncertain cleanup never re-enters the pool. */
struct Reserve {void*base;size_t length;_Atomic unsigned state;};
static struct Reserve reserve[PROSPERO_FFI_RESERVE_COUNT];
static atomic_flag reserve_started=ATOMIC_FLAG_INIT;
static _Atomic unsigned fallback_count;
static _Atomic unsigned reserve_ready;
int prospero_ffi_reserve_prime(void){
 if(atomic_flag_test_and_set_explicit(&reserve_started,memory_order_acq_rel))return EBUSY;
 long page=sysconf(_SC_PAGESIZE);if(page<=64)return EINVAL;
 for(unsigned i=0;i<PROSPERO_FFI_RESERVE_COUNT;i++){
  void*p=mmap(NULL,(size_t)page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0);
  if(p==MAP_FAILED)return errno?errno:ENOMEM; /* prior pages remain owned, bounded */
  reserve[i].base=p;reserve[i].length=(size_t)page;
  atomic_store_explicit(&reserve[i].state,1,memory_order_release);
 }
 atomic_store_explicit(&reserve_ready,1,memory_order_release);return 0;
}
static void* reserve_take(size_t length){
 if(!atomic_load_explicit(&reserve_ready,memory_order_acquire))return MAP_FAILED;
 for(unsigned i=0;i<PROSPERO_FFI_RESERVE_COUNT;i++){
  unsigned available=1;
  if(reserve[i].length==length&&atomic_compare_exchange_strong_explicit(&reserve[i].state,&available,2,memory_order_acq_rel,memory_order_acquire)){
   unsigned n=atomic_fetch_add_explicit(&fallback_count,1,memory_order_relaxed);
   if(n<8)fprintf(stderr,"PS5_LIBFFI closure reserve fallback count=%u capacity=%u page=%zu\n",n+1,(unsigned)PROSPERO_FFI_RESERVE_COUNT,length);
   return reserve[i].base;
  }
 }
 return MAP_FAILED;
}
static int reserve_release(void*base){
 for(unsigned i=0;i<PROSPERO_FFI_RESERVE_COUNT;i++)if(reserve[i].base==base){
  if(atomic_load_explicit(&reserve[i].state,memory_order_acquire)!=2)return 1;
  if(mprotect(base,reserve[i].length,PROT_READ|PROT_WRITE)!=0){
   int error=errno;atomic_store_explicit(&reserve[i].state,3,memory_order_release);
   fprintf(stderr,"PS5_LIBFFI closure reserve reset failed errno=%d;page retained\n",error);return 1;
  }
  memset(base,0,reserve[i].length);
  atomic_store_explicit(&reserve[i].state,1,memory_order_release);return 1;
 }
 return 0;
}
#endif
#define MAGIC UINT64_C(0x5053354646495758)
#define OFFSET 64u
struct Header {uint64_t magic;size_t length;int prepared;};
extern ffi_status ps5ffi_prep_closure_loc_impl(ffi_closure*,ffi_cif*,void(*)(ffi_cif*,void*,void**,void*),void*,void*);
static struct Header* header(void*p){return (struct Header*)((char*)p-OFFSET);}
void* ffi_closure_alloc(size_t size,void**code){
 if(!code){errno=EINVAL;return NULL;}*code=NULL;
 long page=sysconf(_SC_PAGESIZE);if(page<=(long)OFFSET||size==0||size>(size_t)page-OFFSET){errno=EINVAL;return NULL;}
 void*base=mmap(NULL,(size_t)page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0);if(base==MAP_FAILED){
  int error=errno;
#if PROSPERO_FFI_RESERVE_COUNT > 0
  if(error==ENOMEM)base=reserve_take((size_t)page);
#endif
  if(base==MAP_FAILED){fprintf(stderr,"PS5_LIBFFI closure allocation failed errno=%d size=%zu page=%ld\n",error,size,page);errno=error;return NULL;}
 }
 struct Header*h=base;h->magic=MAGIC;h->length=(size_t)page;h->prepared=0;void*p=(char*)base+OFFSET;*code=p;return p;
}
void ffi_closure_free(void*p){if(!p)return;struct Header*h=header(p);if(h->magic!=MAGIC)return;
#if PROSPERO_FFI_RESERVE_COUNT > 0
 if(reserve_release(h))return;
#endif
 (void)munmap(h,h->length);}
void* ffi_data_to_code_pointer(void*p){return p;}
int ffi_tramp_is_present(void*p){(void)p;return 0;}
ffi_status ffi_prep_closure_loc(ffi_closure*c,ffi_cif*cif,void(*fun)(ffi_cif*,void*,void**,void*),void*data,void*code){
 if(!c||!cif||!fun||code!=(void*)c)return FFI_BAD_TYPEDEF;
 struct Header*h=header(c);if(h->magic!=MAGIC||h->prepared)return FFI_BAD_TYPEDEF;
 ffi_status result=ps5ffi_prep_closure_loc_impl(c,cif,fun,data,code);if(result!=FFI_OK)return result;
 h->prepared=1;__builtin___clear_cache((char*)c,(char*)c+sizeof(*c));
 if(mprotect(h,h->length,PROT_READ|PROT_EXEC)!=0){h->prepared=0;return FFI_BAD_TYPEDEF;}
 return FFI_OK;
}
