#!/usr/bin/env python3
"""Manual real333 native/binding checks with explicit original publisher cache."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile
import hashlib
import platform

from host_toolchain import ROOT, java_home
from build_lwjgl333 import publisher_jars, sha
from host_toolchain import executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publisher-cache', type=Path, required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--desktop-graphics', action='store_true', help='Additional genuine macOS ARM64 GLFW/OpenGL check; distinct from Zink')
    parser.add_argument('--zink-frontend', type=Path)
    parser.add_argument('--zink-glfw', type=Path)
    parser.add_argument('--no-zink-glfw', type=Path)
    parser.add_argument('--cc')
    parser.add_argument('--original-client', action='store_true', help='Also initialize the verified original1.21.11 GlDevice on Zink')
    parser.add_argument('--oshi-provider', type=Path)
    parser.add_argument('--oshi-audit', type=Path)
    args = parser.parse_args()
    jdk = java_home(args.java_home)
    build, work = args.build_dir.resolve(), args.output_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    native = build / 'host/liblwjgl333.dylib'
    overlay = build / 'lwjgl-3.3.3-ps5-overlay.jar'
    assert sha(native) == json.loads((native.parent / 'audit.json').read_text())['outputSha256']
    assert sha(overlay) == json.loads((build / 'java-audit.json').read_text())['outputSha256']
    jars = publisher_jars(args.publisher_cache.resolve())
    cp = os.pathsep.join(map(str, [work, overlay, *jars]))
    if args.original_client:
        if not args.oshi_provider or not args.oshi_audit:
            parser.error('Original-client mode requires explicit matching --oshi-provider and --oshi-audit')
        oshi_audit = json.loads(args.oshi_audit.read_text())
        if sha(args.oshi_provider) != oshi_audit['output_sha256']:
            raise ValueError('OSHI provider output mismatch')
        for name, digest in oshi_audit['source_sha256'].items():
            if sha(ROOT / 'client/ports/oshi' / name) != digest:
                raise ValueError('OSHI source mismatch: ' + name)
        from prepare_client_261 import verified, allowed
        row = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions'][-1]
        cache = args.publisher_cache.resolve()
        game = cache / row['id'] / 'client.jar'
        verified(row['client'], game, offline=True)
        dependencies = []
        for lib in row['libraries']:
            name = lib['name']
            if ':natives-' in name or not allowed(lib) or (name.startswith('io.netty:netty-transport-native-') and len(name.split(':')) > 3):
                continue
            pin = lib.get('downloads', {}).get('artifact')
            if pin:
                path = cache / 'libraries' / pin['path']
                verified(pin, path, offline=True)
                dependencies.append(path)
        cp += os.pathsep + os.pathsep.join(map(str, [args.oshi_provider.resolve(), game, *dependencies]))
    subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-cp', cp, '-d', str(work),
                    str(ROOT / 'tools/fixtures/Lwjgl333Host25.java'),
                    str(ROOT / 'client/stb_bootstrap/ClientSTB25.java')], check=True)
    command = [str(jdk / 'bin/java'), '-Xint', '-Xcheck:jni', '-Xverify:all',
               '--enable-native-access=ALL-UNNAMED', '-Dorg.lwjgl.util.NoChecks=false',
               '-Djava.library.path=' + str(native.parent),
               '-cp', cp, 'Lwjgl333Host25', str(native)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120,
                            env={**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0'})
    text = result.stdout + result.stderr
    (work / 'result.log').write_text(text)
    if result.returncode or 'PASS genuine333' not in text or any(s in text for s in (
            'WARNING in native method', 'FATAL ERROR in native method', 'runtime error:', 'Unsupported JNI version')):
        raise RuntimeError('333 check failed: ' + text[-6000:])
    (work / 'audit.json').write_text(json.dumps({'scope': __doc__, 'nativeSha256': sha(native),
        'overlaySha256': sha(overlay), 'result': 'PASS core/memory/truthful333 version/callbacks/1600lifetimes/STB3cycles',
        'console': 'NOT RUN; not GL/Zink/window/world/PS5 evidence'}, indent=2) + '\n')
    print(text)
    if args.desktop_graphics:
        if platform.system() != 'Darwin' or platform.machine() != 'arm64':
            raise RuntimeError('Desktop graphics fixture currently requires native macOS ARM64')
        row = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions'][-1]
        pin = next(lib['downloads']['artifact'] for lib in row['libraries']
                   if lib['name'] == 'org.lwjgl:lwjgl-glfw:3.3.3:natives-macos-arm64')
        original = args.publisher_cache / 'libraries' / pin['path']
        if original.stat().st_size != pin['size'] or hashlib.sha1(original.read_bytes()).hexdigest() != pin['sha1']:
            raise ValueError('Original desktop GLFW native input mismatch')
        glfw = work / 'libglfw-original.dylib'
        with zipfile.ZipFile(original) as archive:
            glfw.write_bytes(archive.read('macos/arm64/org/lwjgl/glfw/libglfw.dylib'))
        subprocess.run([str(jdk / 'bin/javac'), '-cp', cp, '-d', str(work),
                        str(ROOT / 'tools/fixtures/Lwjgl333GraphicsHost25.java')], check=True)
        result = subprocess.run([str(jdk / 'bin/java'), '-XstartOnFirstThread', '-Xint', '-Xcheck:jni',
            '--enable-native-access=ALL-UNNAMED', '-Djava.library.path=' + str(native.parent), '-cp', cp,
            'prosperocraft.host333.Lwjgl333GraphicsHost25', str(native), str(glfw)], capture_output=True, text=True, timeout=60,
            env={**os.environ, 'UBSAN_OPTIONS': 'halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0'})
        text = result.stdout + result.stderr
        (work / 'graphics.log').write_text(text)
        if result.returncode or text.count('PASS333 genuine GL cycle') != 3 or any(s in text for s in (
                'WARNING in native method', 'FATAL ERROR in native method', 'runtime error:', 'Unsupported JNI version')):
            raise RuntimeError(text[-6000:])
        print(text)
    selected = [args.zink_frontend, args.zink_glfw, args.no_zink_glfw]
    if any(selected):
        if not all(selected):
            parser.error('Select all three explicit Zink/native GLFW inputs')
        frontend, glfw, absent = [p.resolve() for p in selected]
        if sha(frontend) != json.loads(frontend.with_suffix('.json').read_text())['output_sha256']:
            raise ValueError('Zink frontend audit mismatch')
        for lib in (glfw, absent):
            if sha(lib) != json.loads(lib.with_name('audit.json').read_text())['output_sha256']:
                raise ValueError('GLFW output audit mismatch')
        subprocess.run([str(jdk / 'bin/javac'), '-cp', cp, '-d', str(work),
                        str(ROOT / 'tools/fixtures/Lwjgl333GraphicsHost25.java')], check=True)
        alias = work / 'libps5zink.so'
        if alias.is_symlink():
            alias.unlink()
        if alias.exists():
            raise FileExistsError('Refuse to replace non-symlink host alias')
        alias.symlink_to(frontend)
        cc = executable('clang', override=args.cc)
        asan = subprocess.check_output([cc, '-print-file-name=libclang_rt.asan_osx_dynamic.dylib'], text=True).strip()
        env = {**os.environ, 'DYLD_INSERT_LIBRARIES': asan, 'DYLD_LIBRARY_PATH': str(work) + os.pathsep + str(frontend.parent),
               'LIBGL_ALWAYS_SOFTWARE': 'true', 'SDL_VIDEODRIVER': 'dummy', 'GALLIUM_THREAD': '0', 'ZINK_DEBUG': 'flushsync',
               'ASAN_OPTIONS': 'detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',
               'UBSAN_OPTIONS': 'halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0'}
        for mode, library in (('absent', absent), ('zink', glfw)):
            result = subprocess.run([str(jdk / 'bin/java'), '-Xint', '-Xcheck:jni', '--enable-native-access=ALL-UNNAMED',
                '-Djava.library.path=' + str(native.parent), '-cp', cp, 'prosperocraft.host333.Lwjgl333GraphicsHost25', str(native), str(library), mode,
                *(['original121'] if args.original_client and mode == 'zink' else [])],
                env=env, cwd=work, capture_output=True, text=True, timeout=120)
            text = result.stdout + result.stderr
            (work / (mode + '.log')).write_text(text)
            expected = 'PASS333 actual GLFW missing-Zink refusal' if mode == 'absent' else 'PASS333 genuine GL cycle'
            if result.returncode or expected not in text or (mode == 'zink' and ('renderer=zink' not in text or text.count(expected) != 3)) or any(s in text for s in (
                    'runtime error:', 'ERROR: AddressSanitizer', 'WARNING in native method', 'FATAL ERROR in native method', 'Unsupported JNI version')):
                raise RuntimeError(text[-6000:])
            print(text)


if __name__ == '__main__':
    main()
