#!/usr/bin/env python3
"""Real-JVM333 JNI-table ownership/refusal/foreign-table checks with native sanitizers."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from host_toolchain import ROOT, executable, java_home, jni_flags
from build_lwjgl333 import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--cc')
    args = parser.parse_args()
    jdk, cc = java_home(args.java_home), executable('clang', override=args.cc)
    work = args.output_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = args.build_dir.resolve() / 'native-sources/lwjgl3-f0ec1437a6149dae00eaa27c47268e5e4efb129f/modules/lwjgl/core/src/main/c'
    audit = json.loads((args.build_dir / 'ps5/audit.json').read_text())
    for name in ('common_tools.c', 'org_lwjgl_system_ThreadLocalUtil.c'):
        assert sha(source / name) == audit['sourceUnitsSha256'][name]
    helper = work / 'ownership.c'
    helper.write_text(r'''
#include "common_tools.h"
#include <pthread.h>
#include <assert.h>
#include <stdatomic.h>
#include <string.h>
static _Atomic int allocations,releases,live;
static _Thread_local int fault;
void*checked_malloc(size_t n){if(fault==1)return NULL;void*p=malloc(n);if(p){++allocations;++live;}return p;}
void*checked_calloc(size_t n,size_t size){if(fault==2)return NULL;void*p=calloc(n,size);if(p){++allocations;++live;}return p;}
void checked_free(void*p){if(p){++releases;--live;free(p);}}
int checked_setspecific(pthread_key_t key,const void*data){return fault==3?12:pthread_setspecific(key,data);}
extern jlong Java_org_lwjgl_system_ThreadLocalUtil_nsetupEnvData(JNIEnv*,jclass,jint);
extern jboolean Java_org_lwjgl_system_ThreadLocalUtil_ownsEnvData(JNIEnv*,jclass);
JNIEXPORT void JNICALL Java_Ownership333_cycle(JNIEnv*e,jclass c,jint failure){
 JNIEnv original=*e;jint version=(*e)->GetVersion(e);
 struct JNINativeInterface_ *foreign=malloc(sizeof(**e));assert(foreign);memcpy(foreign,original,sizeof(*foreign));
 foreign->reserved2=(void*)0x1234;foreign->reserved3=(void*)0x5678;
 *e=foreign;
 assert(!Java_org_lwjgl_system_ThreadLocalUtil_ownsEnvData(e,c));
 fault=failure;
 jlong value=Java_org_lwjgl_system_ThreadLocalUtil_nsetupEnvData(e,c,sizeof(**e)/sizeof(void*));
 if(failure){assert(value==0&&*e==foreign&&(*e)->ExceptionCheck(e));fault=0;*e=original;free(foreign);return;}
 assert(value&&*e!=foreign&&Java_org_lwjgl_system_ThreadLocalUtil_ownsEnvData(e,c));
 EnvData*data=(EnvData*)(uintptr_t)value;
 assert(data->env==e&&data->envCopy==*e&&data->async==0&&data->errnum==0);
 assert((*e)->reserved2==data&&(*e)->reserved3==(void*)0x5678);
 assert(foreign->reserved2==(void*)0x1234&&foreign->reserved3==(void*)0x5678);
 assert(Java_org_lwjgl_system_ThreadLocalUtil_nsetupEnvData(e,c,sizeof(**e)/sizeof(void*))==value);
 assert((*e)->GetVersion(e)==version);
 jclass strings=(*e)->FindClass(e,"java/lang/String");assert(strings&&!(*e)->ExceptionCheck(e));(*e)->DeleteLocalRef(e,strings);
 *e=original;free(foreign); //333TLS owns only its333copy and record until native destructor.
}
JNIEXPORT jint JNICALL Java_Ownership333_live(JNIEnv*e,jclass c){(void)e;(void)c;return live;}
JNIEXPORT void JNICALL Java_Ownership333_balanced(JNIEnv*e,jclass c){(void)e;(void)c;assert(live==0&&allocations==releases);}
JNIEXPORT void JNICALL Java_Ownership333_wrongSize(JNIEnv*e,jclass c){
 JNIEnv original=*e;assert(Java_org_lwjgl_system_ThreadLocalUtil_nsetupEnvData(e,c,1)==0);assert(*e==original&&(*e)->ExceptionCheck(e));
}
''')
    java = work / 'Ownership333.java'
    java.write_text(r'''
import java.util.concurrent.atomic.AtomicReference;
public class Ownership333 {
 static native void cycle(int fault);static native int live();static native void balanced();static native void wrongSize();
 public static void main(String[]a)throws Exception{
  System.load(a[0]);try{wrongSize();throw new AssertionError("bad count accepted");}catch(LinkageError expected){}
  var failure=new AtomicReference<Throwable>();Thread[]threads=new Thread[32];
  for(int i=0;i<threads.length;i++){threads[i]=new Thread(()->{try{
   for(int fault=1;fault<=3;fault++)try{cycle(fault);throw new AssertionError("allocation/key refusal accepted");}catch(OutOfMemoryError expected){}
   for(int n=0;n<100;n++)cycle(0);
  }catch(Throwable t){failure.compareAndSet(null,t);}},"333 real JNI ownership");threads[i].start();}
  for(Thread thread:threads)thread.join();if(failure.get()!=null)throw new AssertionError(failure.get());
  long deadline=System.nanoTime()+3_000_000_000L;while(live()!=0&&System.nanoTime()<deadline)Thread.sleep(1);balanced();
  System.out.println("PASS333 actual JNI ownership:32threads/3200foreign-copy cycles, idempotence, foreign-table preservation, malloc/calloc/key refusal rollback, exact-size refusal, paired native destructor frees");
 }
}
''')
    flags = ['-std=c11', '-O1', '-g', '-fPIC', '-DLWJGL_PS5', '-I' + str(source), *jni_flags(jdk), '-fsanitize=address,undefined']
    objects = []
    for name in ('common_tools.c', 'org_lwjgl_system_ThreadLocalUtil.c'):
        obj = work / (name + '.o')
        subprocess.run([cc, *flags, '-Dmalloc=checked_malloc', '-Dcalloc=checked_calloc', '-Dfree=checked_free',
                        '-Dpthread_setspecific=checked_setspecific', '-c', str(source / name), '-o', str(obj)], check=True)
        objects.append(obj)
    library = work / 'libownership333.dylib'
    subprocess.run([cc, *flags, '-dynamiclib', *map(str, objects), str(helper), '-o', str(library)], check=True)
    subprocess.run([str(jdk / 'bin/javac'), str(java)], check=True)
    asan = subprocess.check_output([cc, '-print-file-name=libclang_rt.asan_osx_dynamic.dylib'], text=True).strip()
    env = {**os.environ, 'DYLD_INSERT_LIBRARIES': asan,
           'ASAN_OPTIONS': 'detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',
           'UBSAN_OPTIONS': 'halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0'}
    result = subprocess.run([str(jdk / 'bin/java'), '-Xint', '-Xcheck:jni', '--enable-native-access=ALL-UNNAMED',
                             '-cp', str(work), 'Ownership333', str(library)], env=env, capture_output=True, text=True, timeout=90)
    text = result.stdout + result.stderr
    (work / 'result.log').write_text(text)
    if result.returncode or 'PASS333 actual JNI ownership' not in text or any(s in text for s in ('runtime error:', 'ERROR: AddressSanitizer', 'WARNING in native method')):
        raise RuntimeError(text[-6000:])
    print(text)


if __name__ == '__main__':
    main()
