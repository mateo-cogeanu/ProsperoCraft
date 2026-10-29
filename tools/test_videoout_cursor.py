#!/usr/bin/env python3
"""Execute the actual WSI cursor patch against deterministic OS/WSI boundaries."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
patch=(root/'client/ports/mesa/0006-videoout-menu-cursor.patch').read_text()
actual='\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+')and not line.startswith('+++'))
pre=r'''
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#define __PROSPERO__ 1
#define PUBLIC
#define PS5_KERNEL_DIRECT_TYPE_CPU 3
#define CLAMP(v,a,b) ((v)<(a)?(a):((v)>(b)?(b):(v)))
#define _mm_clflush(p) ((void)(p))
#define _mm_mfence() ((void)0)
typedef struct {unsigned width,height;} VkExtent2D;
static struct wsi_videoout_output {int lock,handle;struct chain{struct set{struct size{VkExtent2D extent;}*size;}*set;}*current;}videoout_output={.handle=17};
static int videoout_once,allocations,enables,disables,images,positions;
static unsigned last_x,last_y;static void*memory;
static void videoout_output_init_once(void){}
static void call_once(int*p,void(*f)(void)){f();}
static void mtx_lock(int*p){}static void mtx_unlock(int*p){}
static int64_t sceKernelGetDirectMemorySize(void){return 1024*1024;}
static int sceKernelAllocateDirectMemory(int64_t a,int64_t b,size_t n,size_t align,int type,int64_t*out){assert(n==65536&&align==65536);allocations++;*out=0;return 0;}
static int sceKernelMapDirectMemory(void**p,size_t n,int prot,int flags,int64_t physical,size_t align){assert(prot==0x33);memory=calloc(1,n);*p=memory;return 0;}
static int sceKernelReleaseDirectMemory(int64_t p,size_t n){assert(0);return 0;}
int sceVideoOutCursorEnable(int32_t h,int32_t i,const void*p){assert(h==17&&i==0&&p);enables++;return 0;}
int sceVideoOutCursorDisable(int32_t h,int32_t i){disables++;return 0;}
int sceVideoOutCursorSetImageAddress(int32_t h,int32_t i,const void*p){assert(p>=memory&&(const char*)p<(char*)memory+65536);images++;return 0;}
int sceVideoOutCursorSetPosition(int32_t h,int32_t i,uint32_t x,uint32_t y){positions++;last_x=x;last_y=y;return 0;}
'''
post=r'''
int main(void){
 assert(client_wsi_cursor(true,.5,.5,0)<0&&!allocations); /* no swapchain yet */
 struct size size={{1920,1080}};struct set set={&size};struct chain chain={&set};videoout_output.current=&chain;
 assert(!client_wsi_cursor(true,.5,.5,0)&&allocations==1&&enables==1&&last_x==959&&last_y==539);
 uint32_t* arrow=(uint32_t*)memory+4096;
 unsigned soft=0,fill=0,outline=0;
 for(unsigned p=0;p<4096;p++){unsigned a=arrow[p]>>24,c=arrow[p]&255;if(a>0&&a<255)soft++;if(a==255&&c>240)fill++;if(a==255&&c<30)outline++;}
 assert(soft>30&&fill>100&&outline>20); /* smooth vector edges, white fill, thin outline */
 assert(arrow[30*64+16]&&!arrow[28*64+23]); /* stem and open notch outside silhouette */
 int before=images;assert(!client_wsi_cursor(true,2,-1,0)&&images==before&&last_x==1919&&last_y==0);
 const char* chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ._-/:!?@()+=";
 for(const char*p=chars;*p;p++)assert(!client_wsi_cursor(true,.25,.75,*p));
 assert(allocations==1&&enables==1&&images>60);assert(!client_wsi_cursor(false,0,0,0)&&disables==1);
 assert(!client_wsi_cursor(false,0,0,0)&&disables==1);assert(!client_wsi_cursor(true,0,0,0)&&enables==2);
 free(memory);return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='ps5-cursor-')as folder:
 p=Path(folder);(p/'test.c').write_text(pre+actual+post)
 subprocess.run(['clang','-std=c11','-fsanitize=address,undefined',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS actual WSI cursor under ASan/UBSan: no second output, deferred allocation, bounded64KiB, double-buffered glyphs, no unchanged image upload, coordinates, hide/re-enable; OS calls are fixtures, PS5 pending')
