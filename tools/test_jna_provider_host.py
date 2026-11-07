#!/usr/bin/env python3
"""Original JNA JNI and real SDL/libffi under controlled allocator refusal.

Requires explicit runtime-generated JNA source, publisher JAR and host natives.
This exercises the provider boundary, not the PS5 allocator implementation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from host_toolchain import ROOT, executable, java_home, jni_flags, shared_flags, library_name

PROVIDER = r'''
#include <jni.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <ffi.h>
static _Atomic int mode;
static _Atomic long allocated, released, closure_count;
void *clientgpu___wrap_malloc(size_t n){
 if(mode==1||mode==3)return NULL;
 void *p=malloc(n);if(p)allocated++;return p;
}
void *clientgpu___wrap_calloc(size_t n,size_t size){
 if(mode==1||mode==3)return NULL;
 void *p=calloc(n,size);if(p)allocated++;return p;
}
void clientgpu___wrap_free(void *p){if(p)released++;free(p);}
void *lwjgl333_ffi_closure_alloc(size_t n,void **code){
 void *p=ffi_closure_alloc(n,code);if(p)closure_count++;return p;
}
void lwjgl333_ffi_closure_free(void *p){if(p)closure_count--;ffi_closure_free(p);}
ffi_status lwjgl333_ffi_prep_closure_loc(ffi_closure *c,ffi_cif *cif,
 void(*fn)(ffi_cif*,void*,void**,void*),void *data,void *code){
 return ffi_prep_closure_loc(c,cif,fn,data,code);
}
JNIEXPORT void JNICALL Java_JnaProviderProbe_mode(JNIEnv *e,jclass c,jint value){mode=value;}
JNIEXPORT jlong JNICALL Java_JnaProviderProbe_allocated(JNIEnv *e,jclass c){return allocated;}
JNIEXPORT jlong JNICALL Java_JnaProviderProbe_released(JNIEnv *e,jclass c){return released;}
JNIEXPORT jlong JNICALL Java_JnaProviderProbe_closures(JNIEnv *e,jclass c){return closure_count;}
'''

JAVA = r'''
import com.sun.jna.*;
public class JnaProviderProbe {
 static native void mode(int value);
 static native long allocated();
 static native long released();
 static native long closures();
 interface Plus extends Callback {int apply(int value);}
 public static class DirectSDL {public static native int SDL_GetVersion();}
 static void check(boolean value,String reason){if(!value)throw new AssertionError(reason);}
 public static void main(String[] args)throws Exception {
  check(Native.POINTER_SIZE==8,"real JNA bootstrap");
  mode(1);
  try {NativeLibrary.getInstance(args[0]);throw new AssertionError("raw refusal accepted");}
  catch(OutOfMemoryError expected){check(expected.getMessage().contains("C string"),"original string refusal");}
  mode(2);
  NativeLibrary library=NativeLibrary.getInstance(args[0]);
  int version=library.getFunction("SDL_GetVersion").invokeInt(new Object[0]);
  check(version>=3000000&&version<4000000,"real SDL version");
  Native.register(DirectSDL.class,library);
  check(DirectSDL.SDL_GetVersion()==version,"real JNA direct registration");
  long a=allocated(),f=released();
  for(int i=0;i<1000;i++)try(Memory memory=new Memory(64)){
   memory.clear();memory.setLong(0,i);memory.setString(16,"DualSense");
   check(memory.getLong(0)==i&&memory.getString(16).equals("DualSense"),"memory/string");
  }
  check(allocated()-a==1000&&released()-f==1000,"paired native buffer lifetime");
  Plus plus=value->value+3;
  long before=closures();
  Pointer fn=CallbackReference.getFunctionPointer(plus);
  check(closures()==before+1,"selected real closure allocator");
  check(Function.getFunction(fn).invokeInt(new Object[]{39})==42,"actual native callback");
  Native.unregister(DirectSDL.class);
  var dispose=CallbackReference.class.getDeclaredMethod("disposeAll");dispose.setAccessible(true);dispose.invoke(null);
  check(closures()==before,"paired callback release");
  mode(3);
  try {new Memory(64);throw new AssertionError("provider refusal accepted");}
  catch(OutOfMemoryError expected){}
  mode(0);
  System.out.println("PASS original JNA: reproduced C-string refusal; supplied provider opens real SDL "+version+
   ", direct registration, 1000 paired buffers, real libffi callback/release and provider-refusal control");
 }
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-workspace', type=Path, required=True)
    parser.add_argument('--jna-jar', type=Path, required=True)
    parser.add_argument('--sdl-library', type=Path, required=True)
    parser.add_argument('--ffi-include', type=Path, required=True)
    parser.add_argument('--ffi-library', type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--cc')
    args = parser.parse_args()
    jdk, cc = java_home(args.java_home), executable('clang', override=args.cc)
    build = args.runtime_workspace.resolve() / 'build/java25/jna-host'
    audit = json.loads((build / 'audit.json').read_text())
    assert audit['host'] and audit['patches_sha256'], 'Checked pinned runtime JNA host build required'
    source = build / 'source/native'
    for name, digest in audit['native_sources_sha256'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    row = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions'][-1]
    pin = next(lib['downloads']['artifact'] for lib in row['libraries']
               if lib['name'] == 'net.java.dev.jna:jna:5.17.0')
    jar = args.jna_jar.resolve()
    assert jar.stat().st_size == pin['size'] and hashlib.sha1(jar.read_bytes()).hexdigest() == pin['sha1']
    bindings = json.loads((ROOT / 'client/launcher/jna-provider.json').read_text())['bindings']
    with tempfile.TemporaryDirectory(prefix='jna-provider-host-') as folder:
        work = Path(folder)
        flags = ['-O2', '-fPIC', '-fno-strict-aliasing', '-DNO_JAWT',
                 '-DJNA_JNI_VERSION="' + audit['native_version'] + '"',
                 '-DCHECKSUM="' + audit['native_api_checksum'] + '"',
                 '-I' + str(build / 'headers'), '-I' + str(args.ffi_include.resolve()), *jni_flags(jdk)]
        objects = []
        for unit in ('dispatch', 'callback'):
            obj = work / (unit + '.o')
            subprocess.run([cc, *flags, *['-D' + a + '=' + b for a, b in bindings.items()],
                            '-c', str(source / (unit + '.c')), '-o', str(obj)], check=True)
            objects.append(obj)
        provider = work / 'provider.c'
        provider.write_text(PROVIDER)
        obj = work / 'provider.o'
        subprocess.run([cc, *flags, '-c', str(provider), '-o', str(obj)], check=True)
        strings = work / 'strings.o'
        subprocess.run([cc, *flags, '-c', str(ROOT / 'client/gpu/string_alloc.c'), '-o', str(strings)], check=True)
        lib = work / library_name('jnidispatch')
        subprocess.run([cc, *shared_flags(), *map(str, objects), str(obj), str(strings),
                        str(args.ffi_library.resolve()), '-o', str(lib)], check=True)
        java = work / 'JnaProviderProbe.java'
        java.write_text(JAVA)
        subprocess.run([str(jdk / 'bin/javac'), '-cp', str(jar), '-d', str(work), str(java)], check=True)
        subprocess.run([str(jdk / 'bin/java'), '-Xcheck:jni', '--enable-native-access=ALL-UNNAMED',
                        '-Djna.boot.library.path=' + str(work), '-Djna.nosys=true',
                        '-Djna.noclasspath=true', '-Djna.nounpack=true',
                        '-cp', os.pathsep.join([str(work), str(jar)]),
                        'JnaProviderProbe', str(args.sdl_library.resolve())], check=True, timeout=60)


if __name__ == '__main__':
    main()
