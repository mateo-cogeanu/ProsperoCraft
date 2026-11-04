#!/usr/bin/env python3
"""Execute original333 STB PNG callbacks with denied native thread-state setup.

Explicit host333 outputs, original publisher bindings and genuine ffi archive.
Only common_tools allocation/key setters are fault-injected; PNG/ffi stay real.
"""
import argparse
import json
import os
import platform
from pathlib import Path
import subprocess
from host_toolchain import ROOT, java_home, executable, jni_flags
from build_lwjgl333 import publisher_jars, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('build-dir', 'publisher-cache', 'ffi-library', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--cc')
    parser.add_argument('--expect-native-refusal', action='store_true', help='Explicit historical negative control')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        raise RuntimeError('This manual host333 dylib test requires macOS; portable CI and PS5 checks are separate')
    jdk, cc = java_home(args.java_home), executable('clang', override=args.cc)
    build, work = args.build_dir.resolve(), args.output_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    source = build / 'native-sources/lwjgl3-f0ec1437a6149dae00eaa27c47268e5e4efb129f/modules/lwjgl/core/src/main/c'
    audit = json.loads((build / 'host/audit.json').read_text())
    for name, digest in audit['objectsSha256'].items():
        if sha(build / 'host' / name) != digest:
            raise ValueError('Stale host input: ' + name)
    if sha(source / 'common_tools.c') != audit['sourceUnitsSha256']['common_tools.c']:
        raise ValueError('Stale native callback source')
    helper = work / 'faults.c'
    helper.write_text(r'''
#include <jni.h>
#include <pthread.h>
#include <stdlib.h>
#include <errno.h>
static _Thread_local int fault_mode,denied;
void*png_checked_calloc(size_t n,size_t size){if(fault_mode==2){denied++;errno=ENOMEM;return NULL;}return calloc(n,size);}
int png_checked_setspecific(pthread_key_t key,const void*value){if(fault_mode==3){denied++;return ENOMEM;}return pthread_setspecific(key,value);}
JNIEXPORT void JNICALL Java_PngWorker207_fault(JNIEnv*e,jclass c,jint mode){(void)e;(void)c;fault_mode=mode;}
JNIEXPORT jint JNICALL Java_PngWorker207_deniedCalls(JNIEnv*e,jclass c){(void)e;(void)c;return denied;}
''')
    flags = ['-std=c11', '-O1', '-g', '-fPIC', '-DLWJGL_PS5', '-fsanitize=undefined', '-fno-sanitize=function',
             '-I' + str(source), *jni_flags(jdk)]
    common = work / 'common_tools.c.o'
    subprocess.run([cc, *flags, '-Dcalloc=png_checked_calloc', '-Dpthread_setspecific=png_checked_setspecific',
                    '-c', str(source / 'common_tools.c'), '-o', str(common)], check=True)
    library = work / 'liblwjgl333.dylib'
    others = [build / 'host' / n for n in audit['objectsSha256'] if n != common.name]
    subprocess.run([cc, *flags, '-dynamiclib', str(common), *map(str, others), str(helper),
                    str(args.ffi_library.resolve()), '-o', str(library)], check=True)
    cp = os.pathsep.join(map(str, [work, build / 'lwjgl-3.3.3-ps5-overlay.jar', *publisher_jars(args.publisher_cache.resolve())]))
    subprocess.run([str(jdk / 'bin/javac'), '-cp', cp, '-d', str(work), str(ROOT / 'tools/fixtures/PngWorker207.java')], check=True)
    result = subprocess.run([str(jdk / 'bin/java'), '-Xint', '-Xcheck:jni', '--enable-native-access=ALL-UNNAMED',
        '-Djava.library.path='+str(work), '-XX:-CreateCoredumpOnCrash', '-XX:ErrorFile='+str(work/'hs_err.log'),
        '-cp', cp, 'PngWorker207', str(library)], capture_output=True, text=True, timeout=90, cwd=work,
        env=dict(os.environ, UBSAN_OPTIONS='halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0'))
    text = result.stdout + result.stderr
    (work / 'result.log').write_text(text)
    if args.expect_native_refusal:
        if result.returncode == 0 or 'native thread state allocation/key refusal' not in text:
            raise AssertionError('Historical native-refusal control did not reproduce')
        print('PASS historical native state refusal reproduced in original STB PNG callback')
        return
    if result.returncode or 'PASS64 original333 PNG' not in text or 'WARNING in native method' in text or 'runtime error:' in text:
        raise RuntimeError(text[-6000:])
    print(text)


if __name__ == '__main__':
    main()
