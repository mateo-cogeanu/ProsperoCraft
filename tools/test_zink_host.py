#!/usr/bin/env python3
"""Actual macOS lavapipe/Zink + rebuilt GLFW/LWJGL execution, outside CI lanes.

All native inputs are explicit local build outputs. Original game inputs are
verified against the draft publisher lock. No account, network or target/GPU
acceptance is involved; SDL's dummy window has an offscreen Zink drawable.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

from host_toolchain import ROOT, executable, java_home, jni_flags
from prepare_client_261 import verified, validate_metadata, allowed, artifact_path


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--cc', required=True)
    parser.add_argument('--frontend', type=Path, required=True)
    parser.add_argument('--glfw-library', type=Path, required=True)
    parser.add_argument('--no-zink-glfw', type=Path, required=True)
    parser.add_argument('--core-library', type=Path, required=True)
    parser.add_argument('--opengl-library', type=Path, required=True)
    parser.add_argument('--parent-dir', type=Path, required=True)
    parser.add_argument('--publisher-cache', type=Path, required=True)
    parser.add_argument('--glfw-binding', type=Path, required=True)
    parser.add_argument('--oshi-provider', type=Path, required=True, help='Existing genuine consumer OSHI overlay; host fixture metadata avoids unrelated macOS JNA telemetry')
    parser.add_argument('--check-preparation-refusal', action='store_true', help='Require honest early refusal with a layerless host Vulkan provider')
    parser.add_argument('--prepare-screen', action='store_true', help='Prepare the real screen via a native constructor before the host JVM')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/zink-host-test')
    args = parser.parse_args()
    if args.check_preparation_refusal and not args.prepare_screen: parser.error('--check-preparation-refusal requires --prepare-screen')
    if platform.system() != 'Darwin':
        raise RuntimeError('This host lane currently exercises macOS lavapipe; Linux and PS5 are separate validation')
    jdk, cc = java_home(args.java_home), executable('clang', override=args.cc)
    work = args.output_dir.resolve(); work.mkdir(parents=True, exist_ok=True)
    frontend, glfw, absent = (p.resolve() for p in (args.frontend, args.glfw_library, args.no_zink_glfw))
    native_audit = json.loads(frontend.with_suffix('.json').read_text())
    if sha(frontend) != native_audit['output_sha256']:
        raise ValueError('Frontend output audit mismatch')
    for name in ('frontend.c', 'frontend.h'):
        if sha(ROOT / 'client/ports/zink' / name) != native_audit['source']['recipe']['frontend'][name]:
            raise ValueError('Stale frontend: ' + name)
    for library in (glfw, absent):
        audit = json.loads(library.with_name('audit.json').read_text())
        for name, digest in audit['local_source_sha256'].items():
            if sha(ROOT / 'client/ports/glfw' / name) != digest:
                raise ValueError('Stale GLFW source: ' + name)
    # Real frontend C execution first. The frontend itself and this driver use
    # ASan/UBSan; Mesa and the external lavapipe ICD use their ordinary builds.
    native = work / 'frontend-check'
    subprocess.run([cc, '-std=c11', '-O1', '-g', '-fsanitize=address,undefined',
                    '-I' + str(ROOT / 'client/ports/zink'), '-I' + str(ROOT / '.tools/PS5_Mesa/include'),
                    str(ROOT / 'tools/fixtures/zink_frontend_host.c'), str(frontend),
                    '-Wl,-rpath,' + str(frontend.parent), '-o', str(native)], check=True)
    asan = subprocess.check_output([cc, '-print-file-name=libclang_rt.asan_osx_dynamic.dylib'], text=True).strip()
    if not Path(asan).is_file(): raise FileNotFoundError('Selected compiler ASan runtime unavailable')
    env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE='true', SDL_VIDEODRIVER='dummy',
               ASAN_OPTIONS='detect_leaks=0:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',
               UBSAN_OPTIONS='halt_on_error=1:handle_segv=0:handle_sigbus=0:handle_sigfpe=0',
               MESA_SHADER_CACHE_DIR=str(work / 'shader-cache'))
    def execute(command, name, expected):
        result = subprocess.run(list(map(str, command)), cwd=work, env=env, capture_output=True, text=True, timeout=120)
        text = result.stdout + result.stderr
        (work / (name + '.log')).write_text(text)
        if result.returncode or expected not in text or any(s in text for s in ('ERROR: AddressSanitizer', 'runtime error:', 'WARNING in native method', 'FATAL ERROR in native method')):
            raise RuntimeError(name + ' failed; inspect ' + str(work / (name + '.log')) + '\n' + text[-4000:])
        print('PASS', name, flush=True)
        return text
    execute([native], 'native-context', 'PASS real Zink clear/draw/guard/readback')
    # Use the actual pinned dynamic-link JNI helper for host execution only.
    loader_pin = json.loads((ROOT / 'client/ports/sdl/host-loader-source.json').read_text())
    loader_source = ROOT / '.tools/lwjgl-native-src' / loader_pin['file']
    if sha(loader_source) != loader_pin['sha256']: raise ValueError('Host dynamic-link JNI source mismatch')
    loader = work / 'libhost-loader.dylib'
    subprocess.run([cc, '-dynamiclib', '-DLWJGL_MACOS', '-I' + str(ROOT / '.tools/lwjgl-native-src'),
                    *jni_flags(jdk), str(loader_source), '-o', str(loader)], check=True)
    parent = []
    for row in json.loads((ROOT / 'client/26.3.lock.json').read_text())['artifacts']:
        if row['id'].startswith(('org.lwjgl:', 'org.jspecify:')) and ':natives-' not in row['id']:
            path = args.parent_dir.resolve() / row['file']; verified(row, path, offline=True)
            if sha(path) != row['sha256']: raise ValueError('Parent SHA-256 mismatch')
            parent.append(path)
    oshi = args.oshi_provider.resolve()
    oshi_audit = json.loads(oshi.with_name('audit.json').read_text())
    if sha(oshi) != oshi_audit['output_sha256']: raise ValueError('OSHI output mismatch')
    for name, digest in oshi_audit['source_sha256'].items():
        if sha(ROOT / 'client/ports/oshi' / name) != digest: raise ValueError('Stale OSHI source')
    overlays = [oshi, ROOT / 'build/client-ports/lwjgl-modules/lwjgl-3.4.3-ps5-modules.jar',
                ROOT / 'build/client-ports/lwjgl/lwjgl-3.4.3-ps5-platform.jar', args.glfw_binding.resolve()]
    cp = os.pathsep.join(map(str, [work, *overlays, *parent]))
    subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-cp', cp, '-d', str(work),
                    str(ROOT / 'tools/fixtures/ZinkGlfwHost25.java')], check=True)
    alias = work / 'libps5zink.so'
    if alias.is_symlink(): alias.unlink()
    if alias.exists(): raise ValueError('Refusing to replace a non-symlink host provider alias')
    alias.symlink_to(frontend)
    inserted = [asan]
    if args.prepare_screen:
        prewarm = work / 'libprewarm.dylib'
        subprocess.run([cc, '-dynamiclib', '-fsanitize=address,undefined',
                        '-I' + str(ROOT / 'client/ports/zink'),
                        str(ROOT / 'tools/fixtures/zink_prewarm_host.c'), str(frontend),
                        '-Wl,-rpath,' + str(frontend.parent), '-o', str(prewarm)], check=True)
        # Keep the missing-provider control free of this genuine provider.
        # Positive pre-JVM cases load it only after that separate child exits.
    env['DYLD_INSERT_LIBRARIES'] = os.pathsep.join(inserted)
    env['DYLD_LIBRARY_PATH'] = os.pathsep.join(map(str, [work, frontend.parent]))
    command = [jdk / 'bin/java', '-Xint', '-Xcheck:jni', '-Xverify:all', '--enable-native-access=ALL-UNNAMED',
               '--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED',
               '-Djava.library.path=' + str(args.opengl_library.resolve().parent), '-cp', cp,
               'ZinkGlfwHost25', args.core_library.resolve(), loader]
    execute([*command, absent, 'absent'], 'missing-zink', 'PASS real GLFW missing-Zink refusal')
    if args.prepare_screen:
        env['DYLD_INSERT_LIBRARIES'] = os.pathsep.join([asan, str(prewarm)])
    if args.check_preparation_refusal:
        refused = subprocess.run([str(jdk / 'bin/java'), '-version'], cwd=work,
            env=dict(env, ZINK_DEBUG='flushsync,validation'), capture_output=True, text=True, timeout=40)
        refusal = refused.stdout + refused.stderr
        (work / 'preparation-refusal.log').write_text(refusal)
        if (not refused.returncode or 'HOST_ZINK preparation failed error=19' not in refusal or
            any(token in refusal for token in ('HOST_ZINK pre-JVM screen preparation complete',
                'openjdk version', 'AddressSanitizer', 'runtime error:'))):
            raise AssertionError('Early preparation refusal failed; requires a layerless host provider: ' + refusal[-3000:])
        print('PASS pre-JVM preparation refusal and instance cleanup', flush=True)
    reports = []
    for row in json.loads((ROOT / 'client/26.1.lock.json').read_text())['versions']:
        cache = args.publisher_cache.resolve()
        meta = validate_metadata(row, verified(row['metadata'], cache / (row['id'] + '.json'), offline=True))
        game = cache / (row['id'] + '-client.jar'); verified(row['client'], game, offline=True)
        dependencies = []
        for lib in meta['libraries']:
            name = lib['name']
            if ':natives-' in name or not allowed(lib) or (name.startswith('io.netty:netty-transport-native-') and len(name.split(':')) > 3): continue
            artifact = lib.get('downloads', {}).get('artifact')
            if artifact:
                path = cache / 'libraries' / artifact_path(artifact['path']); verified(artifact, path, offline=True); dependencies.append(path)
        full = list(command); full[full.index('-cp') + 1] = cp + os.pathsep + os.pathsep.join(map(str, [game, *dependencies]))
        text = execute([*full, glfw, 'zink', args.opengl_library.resolve()], row['id'], 'PASS actual GLFW/LWJGL Zink')
        if args.prepare_screen and ('HOST_ZINK pre-JVM screen preparation complete' not in text or 'prepared screen reuse' not in text): raise AssertionError('Missing pre-JVM preparation')
        if text.count('PASS actual GLFW/LWJGL Zink') != 3: raise AssertionError('Missing full context cycles')
        reports.append({'id': row['id'], 'client_sha256': sha(game), 'cycles': 3,
                        'scope': 'Original GlBackend hints and GlDevice capability creation; injected null debug options stop after capability creation; not Main/title/world'})
    (work / 'audit.json').write_text(json.dumps({'host': platform.platform(), 'scope': __doc__,
        'pre_jvm_screen_preparation': args.prepare_screen, 'early_refusal_checked': args.check_preparation_refusal, 'frontend_sha256': sha(frontend), 'glfw_sha256': sha(glfw), 'missing_zink_glfw_sha256': sha(absent),
        'core_sha256': sha(args.core_library), 'opengl_jni_sha256': sha(args.opengl_library),
        'versions': reports, 'native_sanitizers': 'ASan/UBSan frontend, GLFW and test driver; Mesa/lavapipe not instrumented',
        'ps5': 'Not executed; context/presentation/game/save/regression pending'}, indent=2) + '\n')


if __name__ == '__main__': main()
