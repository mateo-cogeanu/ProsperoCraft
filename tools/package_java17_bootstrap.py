#!/usr/bin/env python3
"""Package a separate local-only original Minecraft1.20/Java17 bootstrap test.

Official publisher inputs stay local. No account, menu/world, release or Store action.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from host_toolchain import ROOT, java_home
from prepare_client_261 import verified, allowed, artifact_path
from verify_client_120 import prepare_assets, validate_metadata
from build_lwjgl333 import sha


def metadata_120(cache, *, offline):
    row = json.loads((ROOT / 'client/1.20.lock.json').read_text())['versions'][0]
    if row['id'] != '1.20' or row['javaMajor'] != 17:
        raise ValueError('Reviewed original 1.20 / Java 17 inputs required')
    data = verified(row['metadata'], cache / '1.20.json', offline=offline)
    return validate_metadata(row, data)


def prepare(cache, output, binding, *, offline=False):
    metadata = metadata_120(cache, offline=offline)
    jars = [cache / '1.20-client.jar']
    verified(metadata['downloads']['client'], jars[0], offline=offline)
    for library in metadata['libraries']:
        if not allowed(library) or ':natives-' in library['name']:
            continue
        pin = library.get('downloads', {}).get('artifact')
        if pin:
            path = cache / 'libraries' / artifact_path(pin['path'])
            verified(pin, path, offline=offline)
            jars.append(path)
    audit = json.loads((binding / 'java-audit.json').read_text())
    native = json.loads((binding / 'ps5/audit.json').read_text())
    overlay = binding / 'lwjgl-3.3.1-ps5-overlay.jar'
    port = ROOT / 'client/ports/lwjgl331'
    if (audit['outputSha256'] != sha(overlay) or native['jniRuntimeMajor'] != 17 or
            native['outputSha256'] != sha(binding / 'ps5/lwjgl331.o') or
            native['nativePatchSha256'] != sha(port / '0002-ps5-native-ownership.patch') or
            audit['patchSha256'] != sha(port / '0001-ps5-java-dispatch.patch') or
            any(sha(port / n) != h for n,h in audit['localSourceSha256'].items())):
        raise ValueError('Matching current17/331 native and overlay audits required')
    for jar in jars:
        if jar.name in audit['originalJarsSha256'] and sha(jar) != audit['originalJarsSha256'][jar.name]:
            raise ValueError('Overlay publisher input mismatch')
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(overlay, output / '000-lwjgl331-ps5-overlay.jar')
    for i,path in enumerate(jars):
        shutil.copy2(path, output / (f'{i+1:03d}-' + path.name))
    names = [p.name for p in sorted(output.glob('*.jar'))]
    (output / 'classpath.list').write_text(''.join(n + '\n' for n in names), encoding='utf-8')
    return {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()}


def graphics_options(bindings, work, llvm, runtime, sdk):
    pins = json.loads((ROOT / 'client/java17_bootstrap/graphics-pins.json').read_text())
    inputs = {}
    for binding in bindings:
        name, sep, path = binding.partition('=')
        if not sep or name not in pins or name in inputs:
            raise ValueError('Expected one path for each pinned graphics input')
        file = Path(path).resolve(strict=True)
        if sha(file) != pins[name]:
            raise ValueError('Graphics input differs from the reviewed build: ' + name)
        inputs[name] = file
    if set(inputs) != set(pins):
        raise ValueError('Missing pinned graphics inputs: ' + ', '.join(sorted(set(pins) - set(inputs))))

    # This LTS application has no Java 25 process-wide allocator/thread wrappers.
    renames = work / 'graphics-imports.txt'
    symbols = ('calloc', 'free', 'malloc', 'pthread_create', 'pthread_join', 'realloc')
    renames.write_text(''.join(f'__real_{name} {name}\n' for name in symbols))
    graphics = work / 'graphics-support.o'
    subprocess.run([str(llvm / 'bin/llvm-objcopy'), '--redefine-syms=' + str(renames),
                    str(inputs['graphics']), str(graphics)], check=True)
    options = ['--staged-constructors', 'client_gpu=.data.rel.ro.clientgpu.init_array',
               '--staged-constructors', 'client_openal=.data.rel.ro.clientopenal.init_array',
               '--thread-atexit-provider', 'clientgpu_ps5___cxa_thread_atexit_impl',
               '--link-object', str(graphics), '--link-object', str(inputs['sdl'])]
    for group in ('ps5clientgpu', 'ps5glfw', 'ps5zink'):
        options += ['--library', f'{group}={inputs[group]}']
    openal, operators = scope_openal_allocator(inputs['ps5openal'], work, llvm, runtime, sdk)
    options += ['--library', f'ps5openal={openal}', '--link-object', str(operators)]
    for name, path in inputs.items():
        if name.endswith('.so'):
            options += ['--import-stub', str(path)]
    return options


def scope_openal_allocator(original, work, llvm, runtime, sdk):
    """Bind OpenAL's C++ new/delete pairs to its existing scoped allocator."""
    llvm_bin = llvm / 'bin'
    source = runtime / '.tools/native-app/tooling/native/app_cpp_runtime.cpp'
    compiled = work / 'openal-operators-original.o'
    subprocess.run([
        str(llvm_bin / 'clang++'), '-target', 'x86_64-sie-ps5',
        '-fvisibility-nodllstorageclass=default', '-isysroot', str(sdk),
        '-isystem', str(sdk / 'target/include/c++/v1'),
        '-isystem', str(sdk / 'target/include'), '-std=c++20', '-O2',
        '-fno-exceptions', '-fno-rtti', '-fno-builtin', '-fno-stack-protector',
        '-fno-plt', '-march=x86-64',
        '-Dmalloc=clientgpu___wrap_malloc', '-Dfree=clientgpu___wrap_free',
        '-Dposix_memalign=clientgpu___wrap_posix_memalign',
        '-c', str(source), '-o', str(compiled),
    ], check=True)
    nm = str(llvm_bin / 'llvm-nm')
    def allocation_symbols(flag, path):
        symbols = subprocess.check_output([nm, flag, '--extern-only', str(path)], text=True)
        return {line.split()[-1] for line in symbols.splitlines()
                if line.split() and line.split()[-1].startswith(('_Zn', '_Zd'))}

    defined = allocation_symbols('--defined-only', compiled)
    required = allocation_symbols('--undefined-only', original)
    if '_ZnamSt11align_val_t' not in required or not required <= defined:
        raise ValueError('OpenAL allocation ABI changed; review paired new/delete')
    renames = work / 'openal-operator-symbols.txt'
    renames.write_text(''.join(f'{name} ps5openal_{name}\n'
                               for name in sorted(defined | {'ps5ObserveOwnedAllocation'})))
    objcopy = str(llvm_bin / 'llvm-objcopy')
    openal = work / 'openal-scoped.o'
    operators = work / 'openal-operators.o'
    for before, after in ((original, openal), (compiled, operators)):
        subprocess.run([objcopy, '--redefine-syms=' + str(renames), str(before), str(after)],
                       check=True)
    if allocation_symbols('--undefined-only', openal):
        raise ValueError('An OpenAL allocation symbol still uses the process allocator')
    return openal, operators


def stage_openal_iostream(work, llvm, sdk):
    # OpenAL pulls the SDK's iostream object into the link. Keep its original
    # priority-100 initializer in the explicit OpenAL range, ahead of OpenAL.
    original = work / 'iostream-original.o'
    with original.open('wb') as output:
        subprocess.run([str(llvm / 'bin/llvm-ar'), 'p', str(sdk / 'target/lib/libc++.a'),
                        'iostream.cpp.o'], stdout=output, check=True)
    sections = subprocess.check_output([str(llvm / 'bin/llvm-readelf'), '-SW', str(original)],
                                       text=True)
    if ' .ctors.65435 ' not in sections:
        raise ValueError('Review the SDK iostream constructor before staging it')
    staged = work / 'iostream-openal.o'
    subprocess.run([str(llvm / 'bin/llvm-objcopy'), '--rename-section',
                    '.ctors.65435=.data.rel.ro.clientopenal.init_array.00100.ctors',
                    str(original), str(staged)], check=True)
    return staged


def scope_lwjgl_allocator(binding, work, llvm, linker):
    """Rebind the generated LWJGL allocation API as one ownership family."""
    native = binding / 'ps5'
    audit = json.loads((native / 'audit.json').read_text())
    units = {
        'org_lwjgl_system_MemoryAccessJNI.c.o',
        'org_lwjgl_system_libc_LibCStdlib.c.o',
    }
    names = ('malloc', 'calloc', 'realloc', 'free', 'posix_memalign')
    renames = {name: 'clientgpu___wrap_' + name for name in names}
    pins = audit['objectsSha256']
    if not units <= pins.keys():
        raise ValueError('Missing reviewed LWJGL allocation units')

    def undefined(path):
        output = subprocess.check_output(
            [str(llvm / 'bin/llvm-nm'), '--undefined-only', str(path)], text=True)
        return {line.split()[-1] for line in output.splitlines() if line.strip()}

    inputs = []
    originals = []
    for name, digest in pins.items():
        if Path(name).name != name or not name.endswith('.c.o'):
            raise ValueError('Invalid audited LWJGL object name: ' + name)
        original = native / name
        if sha(original) != digest:
            raise ValueError('LWJGL object differs from its audit: ' + name)
        originals.append(original)
        if name not in units:
            inputs.append(original)
            continue
        if undefined(original) != renames.keys():
            raise ValueError('Review changed allocation imports in ' + name)
        scoped = work / name
        subprocess.run([str(llvm / 'bin/llvm-objcopy'),
                        *('--redefine-sym=' + name + '=' + target for name, target in renames.items()),
                        str(original), str(scoped)], check=True)
        if undefined(scoped) != set(renames.values()):
            raise ValueError('Incomplete LWJGL allocation rebinding: ' + name)
        inputs.append(scoped)

    original_group = work / 'lwjgl331-original.o'
    subprocess.run([str(linker), '-r', *map(str, originals), '-o', str(original_group)], check=True)
    if sha(original_group) != audit['outputSha256']:
        raise ValueError('Reviewed LWJGL inputs do not reconstruct the original group')
    output = work / 'lwjgl331-scoped.o'
    subprocess.run([str(linker), '-r', *map(str, inputs), '-o', str(output)], check=True)
    return output


def stage_demo_assets(cache, assets, output):
    metadata = metadata_120(cache, offline=True)
    count = prepare_assets(metadata, assets, offline=True, objects=True)
    index = assets / 'indexes' / (metadata['assetIndex']['id'] + '.json')
    game_assets = output / 'game-assets'
    target_index = game_assets / 'indexes' / index.name
    target_index.parent.mkdir(parents=True)
    shutil.copyfile(index, target_index)
    objects = {entry['hash'] for entry in json.loads(index.read_bytes())['objects'].values()}
    for digest in sorted(objects):
        relative = Path('objects') / digest[:2] / digest
        target = game_assets / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(assets / relative, target)
    shutil.copyfile(ROOT / 'client/java17_bootstrap/log4j2-demo.xml', output / 'log4j2-demo.xml')
    return {'indexSha256': sha(target_index), 'verifiedObjects': count}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('runtime-workspace', 'llvm-home', 'lld', 'java-home', 'cache-dir',
                 'lwjgl331-build', 'ffi-core', 'image-dir', 'work-dir'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--graphics-input', action='append', default=[], metavar='NAME=PATH')
    p.add_argument('--offline', action='store_true')
    p.add_argument('--game-assets', type=Path, help='Verified original Minecraft 1.20 asset tree')
    p.add_argument('--prepare-only', action='store_true')
    a = p.parse_args()
    if not a.prepare_only and not a.game_assets:
        p.error('--game-assets is required to package the demo test')
    jdk = java_home(a.java_home, required_major=17)
    work = a.work_dir.resolve()
    if work.exists():
        raise FileExistsError('Preserve existing candidate work; select a fresh directory')
    work.mkdir(parents=True)
    inputs = prepare(a.cache_dir.resolve(), work / 'publisher', a.lwjgl331_build.resolve(), offline=a.offline)
    audit = {'gameJarModified': False, 'scope': 'Local-only original 1.20 demo test',
             'filesSha256': inputs}
    if a.game_assets:
        audit['demoAssets'] = stage_demo_assets(a.cache_dir.resolve(), a.game_assets.resolve(),
                                               work / 'publisher')
    (work / 'publisher-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    if a.prepare_only:
        return
    runtime = a.runtime_workspace.resolve()
    sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
    graphics = graphics_options(a.graphics_input, work, a.llvm_home.resolve(), runtime, sdk)
    iostream = stage_openal_iostream(work, a.llvm_home.resolve(), sdk)
    lwjgl = scope_lwjgl_allocator(a.lwjgl331_build.resolve(), work, a.llvm_home.resolve(), a.lld.absolute())
    fault = work / 'startup-fault.o'
    subprocess.run([str(a.llvm_home.resolve() / 'bin/clang'), '-target','x86_64-sie-ps5',
        '-std=c11','-O2','-fPIC','-femulated-tls','-fno-stack-protector',
        '-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk / 'target/include'),
        '-DPS5_SHADERC_MAX_REPORTS=16', '-DPS5_SHADERC_PROBE_STACK=1',
        '-DPS5_SHADERC_FAULT_LOG="/download0/mc120-java17-fault.log"',
        '-c',str(ROOT / 'client/ports/shaderc/fault.c'),'-o',str(fault)], check=True)
    subprocess.run([sys.executable, str(runtime / 'tools/package_java_lts_probe.py'),
        '--major','17','--probe-dir',str(ROOT / 'client/java17_bootstrap'),
        '--extra-assets',str(work / 'publisher'),'--management','--compiler-tls',
        '--library','lwjgl331=' + str(lwjgl),
        '--link-object',str(a.ffi_core.resolve()),'--link-object',str(fault),'--link-object',str(iostream),'--llvm-home',str(a.llvm_home.resolve()),
        '--lld',str(a.lld.absolute()),'--boot-jdk',str(jdk),'--image-dir',str(a.image_dir.resolve()),
        '--work-dir',str(work / 'package'), *graphics], check=True)


if __name__ == '__main__':
    main()
