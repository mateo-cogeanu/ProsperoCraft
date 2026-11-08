#!/usr/bin/env python3
"""Build a separate genuine LWJGL333 PS5 overlay and matched native group.

No implicit game-cache discovery, native implementation stubs or343 output changes.
Source/dependency provisioning requires --fetch-deps; all inputs are verified.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

from host_toolchain import ROOT, executable, java_home, jni_flags, shared_flags, library_name

PORT = ROOT / 'client/ports/lwjgl333'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def obtain(pin, path, fetch=False):
    if not path.exists():
        if not fetch:
            raise FileNotFoundError('Missing pinned input; explicitly use --fetch-deps: ' + str(path))
        request = urllib.request.Request(pin['url'], headers={'User-Agent': 'ProsperoCraft-LWJGL333-build/1'})
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
        if len(data) != pin['size'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
            raise ValueError('Download size/SHA256 mismatch: ' + path.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if path.stat().st_size != pin['size'] or sha(path) != pin['sha256']:
        raise ValueError('Pinned input changed: ' + path.name)
    return path


def publisher_jars(cache, row=None):
    if row is None:
        row = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions'][-1]
    jars = []
    for lib in row['libraries']:
        if lib['name'] not in row['lwjgl']:
            continue
        pin = lib['downloads']['artifact']
        path = cache / 'libraries' / pin['path']
        if path.stat().st_size != pin['size'] or hashlib.sha1(path.read_bytes()).hexdigest() != pin['sha1']:
            raise ValueError('Original333 publisher input mismatch: ' + path.name)
        jars.append(path)
    if len(jars) != len(row['lwjgl']) or len(jars) != len(set(row['lwjgl'])):
        raise ValueError('Expected all exact genuine publisher modules')
    return jars


def build_java(args, pin, jdk, cache, work, *, port=PORT, publisher_row=None):
    group = pin['residentGroup']
    source = work / 'java-sources'
    classes = work / 'classes'
    for directory in (source, classes):
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True)
    units = {
        'lwjgl': ['org/lwjgl/system/' + n + '.java' for n in ('Platform', 'APIUtil', 'Library', 'ThreadLocalUtil')],
        'lwjgl-opengl': ['org/lwjgl/opengl/GL.java'],
        'lwjgl-openal': ['org/lwjgl/openal/ALC.java'],
    }
    for record in pin['javaSources']:
        if record['module'] not in units:
            continue
        archive = obtain(record, cache / record['file'], args.fetch_deps)
        with zipfile.ZipFile(archive) as jar:
            for name in units[record['module']]:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(jar.read(name))
    subprocess.run(['git', 'apply', '--unsafe-paths', '--directory=' + str(source),
                    str(port / '0001-ps5-java-dispatch.patch')], check=True)
    path = source / 'org/lwjgl/system/ps5/PS5Library.java'
    path.parent.mkdir(parents=True)
    shutil.copyfile(port / 'PS5Library.java', path)
    shutil.copytree(port / 'java', source, dirs_exist_ok=True)
    annotations = obtain(pin['compileOnlyAnnotations'], cache / pin['compileOnlyAnnotations']['file'], args.fetch_deps)
    originals = publisher_jars(args.publisher_cache.resolve(), publisher_row)
    subprocess.run([str(jdk / 'bin/javac'), '--release', '8', '-proc:none', '-implicit:none',
                    '-cp', os.pathsep.join(map(str, [*originals, annotations])), '-d', str(classes),
                    *map(str, sorted(source.rglob('*.java')))], check=True)
    emitted = sorted(classes.rglob('*.class'))
    owners = ('org/lwjgl/system/Platform', 'org/lwjgl/system/APIUtil', 'org/lwjgl/system/Library',
              'org/lwjgl/system/ThreadLocalUtil', 'org/lwjgl/system/ps5/PS5Library',
              'org/lwjgl/opengl/GL', 'org/lwjgl/openal/ALC')
    if not emitted or any(not str(f.relative_to(classes)).startswith((*owners, 'prosperocraft/' + group + '/')) for f in emitted):
        raise ValueError('Unexpected Java overlay output')
    output = work / ('lwjgl-' + pin['version'] + '-ps5-overlay.jar')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as jar:
        for file in emitted:
            info = zipfile.ZipInfo(file.relative_to(classes).as_posix())
            info.compress_type = zipfile.ZIP_DEFLATED
            jar.writestr(info, file.read_bytes())
        jar.writestr('META-INF/PS5-PORT-LICENSE.txt', (port / 'LICENSE.md').read_bytes())
    audit = {'version': pin['version'], 'versionStringUnmodified': pin['javaVersionString'],
             'originalJarsSha256': {f.name: sha(f) for f in originals},
             'javaSourceArchives': pin['javaSources'],
             'patchSha256': sha(port / '0001-ps5-java-dispatch.patch'),
             'localSourceSha256': {str(f.relative_to(port)): sha(f) for f in [port / 'PS5Library.java', *sorted((port / 'java').rglob('*.java'))]},
             'classes': [f.relative_to(classes).as_posix() for f in emitted],
             'outputSha256': sha(output), 'gameJarModified': False,
             'scope': 'Separate original-source PS5 platform/dispatch overlay; entire' + group.removeprefix('lwjgl') + ' package owner required',
             'console': 'pending'}
    (work / 'java-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print('Built', group, 'overlay', output, flush=True)
    return output


def build_native(args, pin, jdk, cache, work, *, port=PORT):
    group = pin['residentGroup']
    archive = obtain(pin['sourceArchive'], cache / pin['sourceArchive']['file'], args.fetch_deps)
    extraction = work / 'native-sources'
    shutil.rmtree(extraction, ignore_errors=True)
    extraction.mkdir()
    with tarfile.open(archive) as tar:
        tar.extractall(extraction, filter='data')
    source = extraction / ('lwjgl3-' + pin['commit'])
    for patch in ('0002-ps5-native-ownership.patch', '0003-explicit-libffi-abi-selection.patch'):
        subprocess.run(['git', 'apply', '--unsafe-paths', '--directory=' + str(source), str(port / patch)], check=True)
    core = source / 'modules/lwjgl/core/src/main/c'
    generated = source / 'modules/lwjgl/core/src/generated/c'
    gl = source / 'modules/lwjgl/opengl/src/generated/c'
    stb = source / 'modules/lwjgl/stb/src/generated/c'
    config = ROOT / 'client/ports/lwjgl/PS5Config.h'
    shutil.copyfile(config, core / config.name)
    core_units = [core / n for n in ('common_tools.c', 'org_lwjgl_system_MemoryUtil.c',
                                   'org_lwjgl_system_ThreadLocalUtil.c', 'org_lwjgl_system_Callback.c')]
    core_units += [generated / n for n in ('org_lwjgl_system_JNI.c', 'org_lwjgl_system_MemoryAccessJNI.c',
                   'org_lwjgl_system_jni_JNINativeInterface.c', 'org_lwjgl_system_libc_LibCStdlib.c',
                   'org_lwjgl_system_libc_LibCString.c', 'org_lwjgl_system_libffi_FFICIF.c',
                   'org_lwjgl_system_libffi_FFIClosure.c', 'org_lwjgl_system_libffi_LibFFI.c')]
    units = [*core_units, *sorted(f for f in gl.glob('*.c') if not f.name.startswith(('org_lwjgl_opengl_WGL', 'org_lwjgl_opengl_GLX'))),
             *sorted(stb.glob('*.c')), ROOT / 'client/native/lwjgl_resident.c', port / 'bridge.c']
    if not args.host:
        units.append(ROOT / 'client/ports/libffi/closures_wx.c')
    compiler = executable('clang', override=args.cc)
    flags = ['-std=c11', '-D_GNU_SOURCE', '-O2', '-fPIC', '-DLWJGL_PS5', '-include', 'string.h',
             '-I' + str(core), '-I' + str(args.ffi_include.resolve()),
             '-I' + str(source / 'modules/lwjgl/opengl/src/main/c'),
             '-I' + str(source / 'modules/lwjgl/stb/src/main/c')]
    if args.host:
        # Genuine generated JNI deliberately casts C function addresses to
        # uintptr_t-based signatures. Keep UBSan arithmetic/alignment/etc checks;
        # Clang's function type check cannot model this established C ABI bridge.
        flags += [*jni_flags(jdk), '-g', '-fsanitize=undefined', '-fno-sanitize=function', '-DHAS_FFI_SYSV=1']
    else:
        if args.runtime_workspace is None:
            raise ValueError('Target build requires --runtime-workspace')
        runtime = args.runtime_workspace.resolve()
        sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
        major = getattr(args, 'runtime_major', 25)
        headers = runtime / ('.tools/java' + str(major) + '/openjdk/build/ps5-bootstrap/support/modules_include/java.base')
        for header in (headers / 'jni.h', headers / 'freebsd/jni_md.h'):
            if not header.is_file():
                raise FileNotFoundError('Missing matching target JNI header: ' + str(header))
        flags += ['-target', 'x86_64-sie-ps5', '-march=x86-64', '-msse2', '-mno-avx', '-mno-avx2', '-mno-fma',
                  '-fvisibility-nodllstorageclass=default', '-fno-stack-protector', '-femulated-tls',
                  '-isysroot', str(sdk), '-isystem', str(sdk / 'target/include'),
                  '-I' + str(headers), '-I' + str(headers / 'freebsd'), '-DHAS_FFI_UNIX64=1',
                  '-DPROSPERO_FFI_RESERVE_COUNT=' + str(args.closure_reserve_count)]
    major = getattr(args, 'runtime_major', 25)
    guard = work / 'jni-generation-check.h'
    guard.write_text('#include <jni.h>\n_Static_assert(sizeof(struct JNINativeInterface_) == ' +
                     str({17:234, 21:235, 25:236}[major]) + ' * sizeof(void*), "JNI generation mismatch");\n')
    flags += ['-include', str(guard)]
    output = work / ('host' if args.host else 'ps5')
    output.mkdir(exist_ok=True)
    def compile_unit(unit):
        obj = output / (unit.name + '.o')
        subprocess.run([compiler, *flags, '-c', str(unit), '-o', str(obj)], check=True)
        return obj
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        objects = list(pool.map(compile_unit, units))
    if args.host:
        if args.ffi_library is None:
            raise ValueError('Host link requires --ffi-library matching --ffi-include')
        merged = output / library_name(group)
        subprocess.run([compiler, *shared_flags(), '-fsanitize=undefined', *map(str, objects),
                        str(args.ffi_library.resolve()), '-o', str(merged)], check=True)
    else:
        linker = executable('ld.lld', override=args.lld)
        merged = output / (group + '.o')
        subprocess.run([linker, '-r', *map(str, objects), '-o', str(merged)], check=True)
    audit = {'version': pin['version'], 'source': pin['sourceArchive'], 'sourceCommit': pin['commit'],
             'nativePatchSha256': sha(port / '0002-ps5-native-ownership.patch'),
             'ffiAbiPatchSha256': sha(port / '0003-explicit-libffi-abi-selection.patch'),
             'sharedConfigSha256': sha(config),
             'sourceUnitsSha256': {f.name: sha(f) for f in units},
             'ffiHeadersSha256': {n: sha(args.ffi_include / n) for n in ('ffi.h', 'ffitarget.h')},
             'objectsSha256': {f.name: sha(f) for f in objects}, 'outputSha256': sha(merged),
             'units': len(units), 'target': 'host' if args.host else 'PS5 x86_64/SSE2/emulatedTLS',
             'residentGroup': pin['residentGroup'], 'symbolPrefixRequired': pin['symbolPrefix'],
             'jniRuntimeMajor': getattr(args, 'runtime_major', 25),
             'jniHeadersSha256': {str(f.relative_to(headers)): sha(f) for f in (headers / 'jni.h', headers / 'freebsd/jni_md.h')} if not args.host else {str(f.relative_to(jdk)): sha(f) for f in (jdk / 'include').rglob('jni*.h')},
             'closureReserveCount': 0 if args.host else args.closure_reserve_count,
             'hostSanitizers': 'UBSan except generic C ABI JNI function-pointer casts' if args.host else None,
             'scope': 'Genuine' + group.removeprefix('lwjgl') + ' core/callback/GL/STB; shares existing compatible libffi/provider C APIs; no343 replacement',
             'console': 'pending'}
    (output / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print('Built', group, 'native group', merged, len(units), 'units', flush=True)
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--publisher-cache', type=Path, required=True)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.tools/lwjgl333')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/lwjgl333')
    parser.add_argument('--runtime-workspace', type=Path)
    parser.add_argument('--ffi-include', type=Path)
    parser.add_argument('--ffi-library', type=Path)
    parser.add_argument('--cc')
    parser.add_argument('--lld')
    parser.add_argument('--part', choices=('java', 'native', 'all'), default='all')
    parser.add_argument('--host', action='store_true')
    parser.add_argument('--closure-reserve-count', type=int, choices=(64, 512), default=64)
    parser.add_argument('--fetch-deps', action='store_true')
    args = parser.parse_args()
    pin = json.loads((PORT / 'sources.json').read_text())
    cache, work = args.cache_dir.resolve(), args.output_dir.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    jdk = java_home(args.java_home)
    if args.part in ('java', 'all'):
        build_java(args, pin, jdk, cache, work)
    if args.part in ('native', 'all'):
        if args.ffi_include is None:
            parser.error('--ffi-include is required for native building')
        build_native(args, pin, jdk, cache, work)


if __name__ == '__main__':
    main()
