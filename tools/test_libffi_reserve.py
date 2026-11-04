#!/usr/bin/env python3
"""Genuine x86-64 libffi callbacks with denied mmap and bounded W->X reserve.

Explicit pinned source and LLVM tools required. macOS ARM64 needs --x86-64 and
installed Rosetta; this is a manual native lane, not portable CI or PS5 acceptance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess

from host_toolchain import ROOT, executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffi-source-dir', type=Path, required=True)
    parser.add_argument('--llvm-home', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cc')
    parser.add_argument('--x86-64', action='store_true')
    args = parser.parse_args()
    source, work = args.ffi_source_dir.resolve(), args.output_dir.resolve()
    pin = json.loads((ROOT / 'client/ports/libffi/sources.json').read_text())
    if (source / '.ps5-source-commit').read_text().strip() != pin['commit']:
        raise ValueError('Explicit genuine pinned libffi source required')
    if platform.machine().lower() not in ('x86_64', 'amd64') and not (platform.system() == 'Darwin' and args.x86_64):
        raise ValueError('Requires native x86_64 or explicit macOS --x86-64/Rosetta')
    cc = executable('clang', override=args.cc)
    arch = ['-arch', 'x86_64'] if platform.system() == 'Darwin' and args.x86_64 else []
    llvm = args.llvm_home.resolve() / 'bin'
    target = work / 'target'
    target.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CC=shlex.join([cc, *arch]), AR=str(llvm / 'llvm-ar'),
               RANLIB=str(llvm / 'llvm-ranlib'), CFLAGS='-O2 -fPIC')
    command = [str(source / 'configure'), '--disable-shared', '--enable-static',
               '--disable-multi-os-directory', '--disable-docs', '--disable-exec-static-tramp']
    if arch:
        command += ['--host=x86_64-apple-darwin']
    subprocess.run(command, cwd=target, env=env, check=True)
    subprocess.run(['make', '-j4'], cwd=target, env=env, check=True)
    # Rename only the genuine preparation implementation, as the PS5 builder
    # does, then retain the remaining exact upstream static archive objects.
    check = work / 'check'
    check.mkdir(exist_ok=True)
    renamed = check / 'ffi64.o'
    underscore = '_' if platform.system() == 'Darwin' else ''
    subprocess.run([str(llvm / 'llvm-objcopy'), '--redefine-sym',
        underscore + 'ffi_prep_closure_loc=' + underscore + 'ps5ffi_prep_closure_loc_impl',
        str(target / 'src/x86/ffi64.o'), str(renamed)], check=True)
    archive = check / 'libffi-renamed.a'
    archive.write_bytes((target / '.libs/libffi.a').read_bytes())
    subprocess.run([str(llvm / 'llvm-ar'), 'd', str(archive), 'ffi64.o'], check=True)
    subprocess.run([str(llvm / 'llvm-ar'), 'r', str(archive), str(renamed)], check=True)
    adapter, binary = check / 'adapter.o', check / 'test'
    flags = [*arch, '-O1', '-g', '-fsanitize=address,undefined', '-std=c11', '-I' + str(target / 'include')]
    port = ROOT / 'client/ports/libffi'
    subprocess.run([cc, *flags, '-DPROSPERO_FFI_RESERVE_COUNT=64', '-Dmmap=test_mmap', '-Dmprotect=test_mprotect',
                    '-c', str(port / 'closures_wx.c'), '-o', str(adapter)], check=True)
    subprocess.run([cc, *flags, str(port / 'test_reserve.c'), str(adapter), str(archive), '-o', str(binary)], check=True)
    # The64 preallocated pages intentionally remain owned until process exit.
    for mode in (['--partial-prime'], []):
        subprocess.run([str(binary), *mode], env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0'), check=True)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    (work / 'audit.json').write_text(json.dumps({'source_commit': pin['commit'], 'adapter_sha256': sha(port / 'closures_wx.c'),
        'fixture_sha256': sha(port / 'test_reserve.c'), 'original_archive_sha256': sha(target / '.libs/libffi.a'),
        'headers_sha256': {n: sha(target / 'include' / n) for n in ('ffi.h', 'ffitarget.h')},
        'result': 'PASS real x86_64 callbacks/3200concurrent lifetimes;ENOMEM-only reserve64/exhaust/reuse;unprimed/EACCES/RX/RW-failure controls;ASan/UBSan',
        'console': 'pending; no Java/PS5 integration acceptance'}, indent=2) + '\n')


if __name__ == '__main__':
    main()
