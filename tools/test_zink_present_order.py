#!/usr/bin/env python3
"""Actual private-frontend flush callback/order regression; modeled pipe boundary.

Checks the pinned Mesa kopper ordering contract using the real port functions.
This is not a Vulkan/VideoOut presentation test; actual offscreen rendering is
covered separately. The old no-callback port must fail the window cases.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
from host_toolchain import ROOT, executable

def extract(source,start,end):return source[source.index(start):source.index(end,source.index(start))]
PREAMBLE=r'''
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
struct pipe_context {void (*flush_resource)(struct pipe_context*,struct pipe_resource*);};
struct pipe_resource {int id;};
struct gl_context {};
struct st_context {struct gl_context *ctx;struct pipe_context *pipe;};
struct pipe_frontend_drawable {int stamp;};
struct ps5zink_context {struct pipe_frontend_drawable drawable;struct pipe_resource *textures[3];bool window,flushing;};
struct screen {void (*flush_frontbuffer)(struct screen*,struct pipe_context*,struct pipe_resource*,int,int,void*,int,void*);};
static struct {struct screen *screen;} frontend;
#define ST_FLUSH_END_OF_FRAME 1
static int order,prepared,completed,should_present,driver_success;
static void _mesa_glthread_finish(struct gl_context *ctx){(void)ctx;assert(order==0);order=1;}
static void flush_resource(struct pipe_context*p,struct pipe_resource*r){(void)p;assert(order==2&&r&&r->id==7);order=3;prepared++;}
static void st_context_flush(struct st_context *st,int flags,void*fence,void(*before)(void*),void*args){
 (void)st;(void)fence;assert(flags==1&&order==1);
 /* Pending GL vertices must be emitted before drawable flush_resource. */
 order=2;if(before)before(args);
 /* Ending the batch can only generate its presentation signal after marking. */
 assert(!should_present||order==3);order=4;
}
static void flush_frontbuffer(struct screen*s,struct pipe_context*p,struct pipe_resource*r,int a,int b,void*c,int d,void*e){
 (void)s;(void)p;(void)r;(void)a;(void)b;(void)c;(void)d;(void)e;assert(order==4&&prepared==1);order=5;completed++;
}
static bool zink_kopper_check(struct pipe_resource*r){(void)r;return driver_success;}
static void p_atomic_inc(int *n){(*n)++;}
static void st_invalidate_buffers(struct st_context*s){(void)s;assert(order==4||order==5);order=6;}
'''
HARNESS=r'''
int main(void){
 struct pipe_context pipe={flush_resource};struct st_context st={NULL,&pipe};
 struct screen screen={flush_frontbuffer};frontend.screen=&screen;
 struct pipe_resource texture={7};
 for(int window=0;window<2;window++)for(int available=0;available<2;available++)for(int success=0;success<2;success++){
  struct ps5zink_context c={0};c.window=window;c.textures[0]=available?&texture:NULL;
  order=prepared=completed=0;driver_success=success;should_present=window&&available;
  assert(present(&c,&st,0)==(!should_present||success));
  assert(order==6&&!c.flushing&&c.drawable.stamp==1);
  assert(prepared==should_present&&completed==should_present);
 }
 struct ps5zink_context c={0};c.flushing=true;order=0;assert(present(&c,&st,0));assert(order==0);
 return 0;
}
'''

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc');args=p.parse_args()
 cc=executable('clang',override=args.cc,env='CC')
 source=(ROOT/'client/ports/zink/frontend.c').read_text()
 callback=extract(source,'struct present_flush {','static bool flush_front(')
 # The selected code includes both exact prepare_present and present functions.
 old=callback.replace('c->window && texture ? prepare_present : NULL, &flush','NULL, NULL')
 assert old!=callback
 with tempfile.TemporaryDirectory(prefix='zink-present-order-') as directory:
  work=Path(directory)
  for name,code,expected in [('fixed',callback,0),('old-missing-callback',old,None)]:
   path=work/(name+'.c');path.write_text('struct pipe_resource;\n'+PREAMBLE+code+HARNESS)
   binary=work/name
   subprocess.run([cc,'-std=c11','-fsanitize=address,undefined','-g',str(path),'-o',str(binary)],check=True)
   result=subprocess.run([str(binary)],capture_output=True,text=True)
   if expected==0:assert result.returncode==0,result.stderr
   else:assert result.returncode!=0,'Old missing-callback negative control unexpectedly passed'
 print('PASS actual frontend prepare_present/present ordering: GL emission -> flush_resource -> batch flush -> screen presentation; window/offscreen/missing-resource/failure/recursion controls; old port fails; ASan/UBSan. Modeled pipe boundary, not VideoOut.')

if __name__=='__main__':main()
