#!/usr/bin/env python3
"""Genuine pinned LWJGL PS5 JNI env-copy/TLS lifecycle under unit-local libc refusal.

Manual macOS/JDK25 lane with explicit verified upstream source cache. Host scoped
allocator models ownership only; it is not the PS5 graphics heap or title quota.
"""
import argparse,hashlib,json,os,platform,shutil,subprocess
from pathlib import Path
from host_toolchain import ROOT,java_home,executable,jni_flags

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--cc',required=True);p.add_argument('--java-home',type=Path);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
 if platform.system()!='Darwin':raise RuntimeError('Manual macOS native fault lane; explicit sources required')
 cc=executable('clang',override=a.cc);jdk=java_home(a.java_home);w=a.output_dir.resolve();w.mkdir(parents=True,exist_ok=True);source=w/'source';source.mkdir(exist_ok=True)
 pin=json.loads((ROOT/'client/ports/lwjgl/native-sources.json').read_text())
 for row in pin['files']:
  path=a.source_dir/row['file'];assert path.stat().st_size==row['size']and sha(path)==row['sha256'];shutil.copyfile(path,source/row['file'])
 subprocess.run(['git','apply','--unsafe-paths','--directory='+str(source),str(ROOT/'client/ports/lwjgl/0002-native-core-ps5.patch')],check=True)
 shutil.copyfile(ROOT/'client/ports/lwjgl/PS5Config.h',source/'PS5Config.h')
 (w/'EnvCopyCheck.java').write_text(r'''
import java.util.concurrent.atomic.AtomicReference;
public class EnvCopyCheck {
 static native void cycle();static native void foreign();static native long[] stats();
 public static void main(String[]a)throws Exception{
  System.load(a[0]);int count=a[1].equals("old")?1:16;var failed=new AtomicReference<Throwable>();Thread[] threads=new Thread[count];
  for(int i=0;i<count;i++){threads[i]=new Thread(()->{try{cycle();}catch(Throwable e){failed.set(e);}},"JNI env ownership");threads[i].start();}
  for(Thread t:threads)t.join();if(failed.get()!=null)throw new AssertionError(failed.get());
  foreign();
  long deadline=System.nanoTime()+3_000_000_000L;long[] n=stats();while(n[0]!=n[1]&&System.nanoTime()<deadline){Thread.sleep(1);n=stats();}
  if(n[0]!=count*2+8||n[1]!=n[0]||n[2]!=0)throw new AssertionError("unpaired env allocation/free "+java.util.Arrays.toString(n));
  System.out.println("PASS actual LWJGL setupEnvData + PS5 TLS branch on realJDK: "+count+" concurrent Java threads plus8native attached threads,JNI table dispatch,paired native destructor release; allocations="+n[0]+" frees="+n[1]);
 }
}
''')
 (w/'allocator.c').write_text(r'''
#include "common_tools.h"
#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
extern jlong Java_org_lwjgl_system_ThreadLocalUtil_setupEnvData(JNIEnv*,jclass,jint);
typedef struct {uint64_t magic;size_t bytes;} Header;
static atomic_long allocations,releases,live;
void* denied_malloc(size_t n){(void)n;return NULL;}
void* denied_calloc(size_t n,size_t b){(void)n;(void)b;return NULL;}
void denied_free(void*p){assert(!p);}
void* scoped_malloc(size_t n){if(n>SIZE_MAX-sizeof(Header))return NULL;Header*h=malloc(n+sizeof(*h));if(!h)return NULL;h->magic=UINT64_C(0xbadc0ffee1234567);h->bytes=n;atomic_fetch_add(&allocations,1);atomic_fetch_add(&live,1);return h+1;}
void* scoped_calloc(size_t n,size_t b){if(n&&b>SIZE_MAX/n)return NULL;void*p=scoped_malloc(n*b);if(p)memset(p,0,n*b);return p;}
void scoped_free(void*p){if(!p)return;Header*h=(Header*)p-1;assert(h->magic==UINT64_C(0xbadc0ffee1234567));h->magic=0;atomic_fetch_add(&releases,1);atomic_fetch_sub(&live,1);free(h);}
JNIEXPORT void JNICALL Java_EnvCopyCheck_cycle(JNIEnv*e,jclass c){
 JNIEnv original=*e;int version=(*e)->GetVersion(e);
 jlong address=Java_org_lwjgl_system_ThreadLocalUtil_setupEnvData(e,c,sizeof(**e)/sizeof(void*));
 assert(address&&*e!=original);EnvData*data=(EnvData*)(uintptr_t)address;
 assert(data->env==e&&data->envCopy==*e&&data->async==0&&((void**)*e)[2]==data);
 assert((*e)->GetVersion(e)==version);jclass strings=(*e)->FindClass(e,"java/lang/String");assert(strings&&!(*e)->ExceptionCheck(e));(*e)->DeleteLocalRef(e,strings);
 // Actual common_tools pthread TLS destructor owns both allocations on thread exit.
}
static void* foreign_worker(void*p){(void)p;jboolean async=0;JNIEnv*e=getEnv(&async);assert(e&&async==1);jclass strings=(*e)->FindClass(e,"java/lang/String");assert(strings&&!(*e)->ExceptionCheck(e));(*e)->DeleteLocalRef(e,strings);return NULL;}
JNIEXPORT void JNICALL Java_EnvCopyCheck_foreign(JNIEnv*e,jclass c){(void)e;(void)c;pthread_t threads[8];for(int i=0;i<8;i++)assert(!pthread_create(&threads[i],NULL,foreign_worker,NULL));for(int i=0;i<8;i++)assert(!pthread_join(threads[i],NULL));}
JNIEXPORT jlongArray JNICALL Java_EnvCopyCheck_stats(JNIEnv*e,jclass c){(void)c;jlong v[3]={atomic_load(&allocations),atomic_load(&releases),atomic_load(&live)};jlongArray out=(*e)->NewLongArray(e,3);if(!out||(*e)->ExceptionCheck(e))return NULL;(*e)->SetLongArrayRegion(e,out,0,3,v);return out;}
''')
 subprocess.run([jdk/'bin/javac','--release','25','-d',w,w/'EnvCopyCheck.java'],check=True)
 flags=['-std=c11','-O1','-g','-fPIC','-DLWJGL_PS5','-I'+str(source),*jni_flags(jdk),'-fsanitize=address,undefined']
 subprocess.run([cc,*flags,'-c',w/'allocator.c','-o',w/'allocator.o'],check=True)
 asan=subprocess.check_output([cc,'-print-file-name=libclang_rt.asan_osx_dynamic.dylib'],text=True).strip();env=dict(os.environ,DYLD_INSERT_LIBRARIES=asan,ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',UBSAN_OPTIONS='halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0')
 for mode,family in [('old','denied'),('scoped','scoped')]:
  objects=[]
  for name in ('common_tools.c','org_lwjgl_system_ThreadLocalUtil.c'):
   obj=w/(mode+'-'+name+'.o');subprocess.run([cc,*flags,*['-D'+n+'='+family+'_'+n for n in ('malloc','calloc','free')],'-c',source/name,'-o',obj],check=True);objects.append(obj)
  lib=w/('libenv-'+mode+'.dylib');subprocess.run([cc,'-dynamiclib','-fsanitize=address,undefined',*objects,w/'allocator.o','-o',lib],check=True)
  r=subprocess.run([jdk/'bin/java','-Xint','-Xcheck:jni','-Xverify:all','-XX:-CreateCoredumpOnCrash','-XX:ErrorFile='+str(w/(mode+'-hs-error.log')),'--enable-native-access=ALL-UNNAMED','-cp',w,'EnvCopyCheck',lib,mode],env=env,capture_output=True,text=True,timeout=45);text=r.stdout+r.stderr;(w/(mode+'.log')).write_text(text)
  if mode=='old':assert r.returncode!=0 and '[LWJGL] Failed to allocate JNIEnv copy.'in text,text[-5000:]
  else:
   assert r.returncode==0 and 'PASS actual LWJGL setupEnvData'in text,text[-6000:]
   assert not any(x in text for x in ('WARNING in native method','FATAL ERROR in native method','ERROR: AddressSanitizer','runtime error:')),text[-6000:]
  print('PASS genuine env-copy JNI',mode,'negative fault reproduction'if mode=='old'else'paired native TLS teardown')
 (w/'audit.json').write_text(json.dumps({'scope':__doc__,'upstream_commit':pin['commit'],'native_patch_sha256':sha(ROOT/'client/ports/lwjgl/0002-native-core-ps5.patch'),'results':{'old':'Actual fatal allocation message reproduced with unit-local malloc refusal','scoped':'16 concurrent realJDK JNI table copies/TLS records plus8native daemon-attach/callback-env/detach threads;40allocations/40native destructor frees/0live;ASan/UBSan'},'ps5':'NOT TESTED'},indent=2)+'\n')
if __name__=='__main__':main()
