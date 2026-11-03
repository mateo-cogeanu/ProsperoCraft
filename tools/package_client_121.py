#!/usr/bin/env python3
"""Local205 Vanilla121.11 candidate from exact accepted204 inputs. No releases.

Original343/OpenAL/graphics groups are retained byte for byte from the relink kit.
Only main, libjava's explicit handle hook, lookup table and matched333 are linked anew.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zipfile

from host_toolchain import ROOT, java_home
from build_lwjgl333 import sha

BASE_PACKAGE = '89167d01c7da0ece733b0dd8b7871a05ee38ff5f79ee45b4ce9beefc5d4c14a0'
BASE_RELINK = '4351224b234d2b16a688afc4d31f23f0c6badc30670d034ad065cc629bce9f0f'


def extract(archive, directory, prefix=None):
    with zipfile.ZipFile(archive) as source:
        if source.testzip():
            raise ValueError('Input ZIP CRC failure')
        for info in source.infolist():
            if info.is_dir() or (prefix and not info.filename.startswith(prefix)):
                continue
            path = Path(info.filename)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe input ZIP entry')
            target = directory / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(info))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('runtime-workspace', 'baseline-package', 'baseline-relink', 'base-header', 'llvm-home', 'lld', 'lwjgl333-build'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true', help='Compile/link/convert without signing or a candidate ZIP')
    args = parser.parse_args()
    runtime, llvm, jdk = args.runtime_workspace.resolve(), args.llvm_home.resolve() / 'bin', java_home(args.java_home)
    work, output = args.work_dir.resolve(), args.output_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    package = output / 'PPSA99874.zip'
    if package.exists():
        raise FileExistsError('Preserve existing candidate ZIP; choose a new output directory')
    if sha(args.baseline_package) != BASE_PACKAGE or sha(args.baseline_relink) != BASE_RELINK:
        raise ValueError('Exact accepted204 package/relink inputs required')
    baseline = work / 'baseline204'
    extract(args.baseline_relink, baseline)
    manifest = json.loads((baseline / 'manifest.json').read_text())
    for row in manifest['files']:
        if sha(baseline / row['path']) != row['sha256']:
            raise ValueError('Relink input mismatch: ' + row['path'])
    # Preserve204 bootstrap/VM policy and native consumer adapters exactly.
    source_base = baseline / 'consumer-source'
    for subtree in ('client/startup', 'client/save_headroom', 'client/bootstrap', 'client/native'):
        for original in (source_base / subtree).rglob('*'):
            if original.suffix in ('.c', '.cpp', '.h', '.hpp'):
                current = ROOT / original.relative_to(source_base)
                if not current.is_file() or sha(current) != sha(original):
                    raise ValueError('204 native bootstrap/policy changed: ' + str(current))
    pin = json.loads((ROOT / 'client/ports/lwjgl333/runtime.json').read_text())
    for name, digest in pin['source_sha256'].items():
        if sha(runtime / name) != digest:
            raise ValueError('Wrong runtime namespace integration: ' + name)
    if sha(runtime / '.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava/NativeLibraries.o') != pin['nativeLibrariesObjectSha256']:
        raise ValueError('Target libjava needs the pinned137 build')
    build = args.lwjgl333_build.resolve()
    native = build / 'ps5/lwjgl333.o'
    overlay = build / 'lwjgl-3.3.3-ps5-overlay.jar'
    native_audit = json.loads((native.parent / 'audit.json').read_text())
    java_audit = json.loads((build / 'java-audit.json').read_text())
    if sha(native) != native_audit['outputSha256'] or sha(overlay) != java_audit['outputSha256']:
        raise ValueError('Stale333 native/overlay output')
    for name, key in [('0001-ps5-java-dispatch.patch', 'patchSha256')]:
        if sha(ROOT / 'client/ports/lwjgl333' / name) != java_audit[key]:
            raise ValueError('Rebuild333 overlay after source change')
    for name, key in [('0002-ps5-native-ownership.patch', 'nativePatchSha256'), ('0003-explicit-libffi-abi-selection.patch', 'ffiAbiPatchSha256')]:
        if sha(ROOT / 'client/ports/lwjgl333' / name) != native_audit[key]:
            raise ValueError('Rebuild333 native after source change')
    for name, digest in java_audit['localSourceSha256'].items():
        if sha(ROOT / 'client/ports/lwjgl333' / name) != digest:
            raise ValueError('Stale333 Java helper: ' + name)
    for file in (ROOT / 'client/ports/lwjgl333/bridge.c', ROOT / 'client/native/lwjgl_resident.c'):
        if sha(file) != native_audit['sourceUnitsSha256'][file.name]:
            raise ValueError('Stale333 native helper: ' + file.name)
    if sha(ROOT / 'client/ports/lwjgl/PS5Config.h') != native_audit['sharedConfigSha256']:
        raise ValueError('Stale333 target configuration')
    # Scope native allocator,stdio,etc imports to the existing actual graphics
    # provider. Matched333's own definitions get a separate runtime namespace.
    scoped = work / 'lwjgl333-scoped-imports.o'
    subprocess.run([str(llvm / 'llvm-objcopy'), '--redefine-syms=' + str(baseline / 'provider-bindings.txt'),
                    str(native), str(scoped)], check=True)
    groups = []
    old_groups = {}
    for item in manifest['arguments']:
        match = re.fullmatch(r'inputs/\d+-embedded-([a-z0-9_]+)\.o', item)
        if match:
            old_groups[match[1]] = baseline / item
    core = {'jvm', 'java', 'zip', 'jimage', 'net', 'nio', 'verify', 'management', 'management_ext', 'awt', 'lcms'}
    for name, obj in old_groups.items():
        if name not in core:
            groups.append({'name': name, 'objects': [str(obj)]})
    groups.append({'name': 'lwjgl333', 'objects': [str(scoped)]})
    registry = work / 'registry'
    registry.mkdir(exist_ok=True)
    shutil.copyfile(old_groups['jvm'], registry / 'embedded-jvm.o')
    imageio = registry / 'imageio-target'
    if not imageio.exists():
        imageio.symlink_to(runtime / 'build/java25/imageio-target', target_is_directory=True)
    spec = work / 'resident-libraries.json'
    spec.write_text(json.dumps(groups, indent=2) + '\n')
    command = ['--management-extensions', '--imageio', '--library-symbol-prefix', 'lwjgl333=lwjgl333_',
        '--library-alias', 'SDL3=ps5sdl', '--alias-symbol', 'SDL3:SDL_SetEventFilter=prospero_controlify_SetEventFilter',
        '--alias-symbol', 'SDL3:SDL_GetEventFilter=prospero_controlify_GetEventFilter',
        '--alias-symbol', 'SDL3:SDL_PollEvent=prospero_controlify_PollEvent',
        '--library-alias', 'libzstd-jni_dh-1.5.7-12=ps5zstddh',
        '--library-alias', 'zstd-jni_dh-1.5.7-12=ps5zstddh', '--library-alias', 'sqlitejdbc=ps5sqlitedh',
        '--external-libraries', str(spec)]
    # Select a separate output workspace without changing runtime generator defaults.
    driver = work / 'generate-registry.py'
    driver.write_text('import sys\nfrom pathlib import Path\nsys.path.insert(0,' + repr(str(runtime / 'tools')) + ')\n'
        'import java25_builtin_runtime as generator\ngenerator.WORK=Path(' + repr(str(registry)) + ')\n'
        'sys.argv=["java25_builtin_runtime.py",*' + repr(command) + ']\ngenerator.main()\n')
    subprocess.run(['python3', str(driver)], check=True)
    app = work / 'PPSA99874'
    if app.exists():
        shutil.rmtree(app)
    extract(args.baseline_package, work, prefix='PPSA99874/')
    java = app / 'assets/java25'
    shutil.copyfile(overlay, java / 'ports' / overlay.name)
    shutil.copyfile(runtime / '.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libjava.so', java / 'lib/libjava.so')
    shutil.copyfile(registry / 'builtin-resident-audit.json', java / 'resident-libraries-audit.json')
    (java / 'lwjgl333-integration-audit.json').write_text(json.dumps({'runtime': pin, 'java': java_audit, 'native': native_audit,
        'importsScopedSha256': sha(scoped), 'groupSha256': sha(registry / 'embedded-lwjgl333.o'), 'console': 'NOT RUN'}, indent=2) + '\n')
    # All parent input JARs stay exact204; no official333 publisher JARs are bundled.
    header = args.base_header.read_text()
    cp_value = re.fullmatch(r'#pragma once\n#define CLIENT_CLASSPATH_OPTION "([^"\n]+)"\s*', header)
    if not cp_value or cp_value[1].encode() + b'\0' not in (baseline / 'inputs/104-main.o').read_bytes():
        raise ValueError('Classpath header differs from actual accepted204 main object')
    (work / 'client_classpath.hpp').write_text(header)
    from build_launcher_toolkit import dispatch
    dispatch(work)
    parent = [java / 'ports/lwjgl-3.4.3-ps5-modules.jar', java / 'ports/lwjgl-3.4.3-ps5-platform.jar',
              java / 'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar', *sorted((java / 'client/jars').glob('*.jar')), java / 'client-probe.jar']
    classes = work / 'classes'
    shutil.rmtree(classes, ignore_errors=True)
    classes.mkdir()
    subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-cp', os.pathsep.join(map(str, parent)),
                    '-d', str(classes), str(ROOT / 'client/startup/ClientStartup25.java'),
                    *map(str, sorted((ROOT / 'client/launcher/java').glob('*.java')))], check=True)
    files = list(classes.glob('*.class'))
    names = {f.name for f in files}
    jar = java / 'client-probe.jar'
    temporary = jar.with_suffix('.tmp')
    with zipfile.ZipFile(jar) as original, zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as out:
        for info in original.infolist():
            if info.filename not in names and info.filename not in ('prosperocraft-build.properties', 'prosperocraft-121.txt'):
                out.writestr(info, original.read(info))
        for file in files:
            out.writestr(file.name, file.read_bytes())
        out.writestr('prosperocraft-build.properties', b'app_version=01.000.205\ntitle_id=PPSA99874\n')
        out.writestr('prosperocraft-121.txt', b'vanilla-1.21.11-zink-v1\n')
    temporary.replace(jar)
    for file in files:
        shutil.copyfile(file, java / 'classes' / file.name)
    (java / 'classes/prosperocraft-build.properties').write_text('app_version=01.000.205\ntitle_id=PPSA99874\n')
    (java / 'classes/prosperocraft-121.txt').write_text('vanilla-1.21.11-zink-v1\n')
    param = json.loads((app / 'sce_sys/param.json').read_text())
    param['contentVersion'] = '01.000.205'
    (app / 'sce_sys/param.json').write_text(json.dumps(param, indent=2) + '\n')
    sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
    flags = ['-target', 'x86_64-sie-ps5', '-fvisibility-nodllstorageclass=default', '-isysroot', str(sdk),
             '-isystem', str(sdk / 'target/include/c++/v1'), '-isystem', str(sdk / 'target/include'),
             '-march=x86-64', '-mno-avx', '-mno-avx2', '-mno-fma', '-O2', '-fno-stack-protector',
             '-fno-plt', '-femulated-tls', '-ffunction-sections', '-fdata-sections']
    main_obj = work / 'main205.o'
    subprocess.run([str(llvm / 'clang++'), *flags, '-DPROSPERO_APP_VERSION="01.000.205"', '-std=c++20',
        '-Wall', '-Wextra', '-Werror', '-fno-exceptions', '-fno-rtti',
        *['-I' + str(p) for p in (runtime / 'native/renderer', runtime / 'build/native', runtime / 'src',
          runtime / 'native', work, ROOT / 'client/native', ROOT / 'client/launcher/toolkit/src',
          ROOT / '.tools/PS5_Mesa/include', runtime / 'java25/probe', runtime / 'java25/platform')],
        '-c', str(ROOT / 'client/save_headroom/bootstrap.cpp'), '-o', str(main_obj)], check=True)
    libraries = work / 'libraries'
    libraries.mkdir(exist_ok=True)
    for row in manifest['files']:
        file = baseline / row['path']
        if file.suffix in ('.a', '.so'):
            destination = libraries / file.name.split('-', 1)[1]
            if not destination.exists():
                os.link(file, destination)
    pie = work / 'client121-205-symbols.elf'
    replacements = {'inputs/104-main.o': main_obj, 'inputs/032-embedded-java.o': registry / 'embedded-java.o',
                    'inputs/109-builtin-libraries.o': registry / 'builtin-libraries.o'}
    link = []
    for item in manifest['arguments']:
        if item == '{OUTPUT}':
            link.append(str(pie))
        elif item == '-L{LIBRARY_DIR}':
            link.append('-L' + str(libraries))
        elif item in replacements:
            if item.endswith('-builtin-libraries.o'):
                link.append(str(registry / 'embedded-lwjgl333.o'))
            link.append(str(replacements[item]))
        elif item.startswith('inputs/'):
            link.append(str(baseline / item))
        else:
            link.append(item)
    response = work / 'link205.rsp'
    response.write_text('\n'.join(json.dumps(x) for x in link) + '\n')
    subprocess.run([str(args.lld.absolute()), '@' + str(response)], check=True)
    converter = runtime / 'build/native/host/ps5-native-tool'
    elf = work / 'eboot.elf'
    stubs = [baseline / name for name in ('inputs/029-libSceMouse.so', 'inputs/030-libSceAudioIn.so',
                                        'inputs/027-libSceAgc.so', 'inputs/028-libSceAgcDriver.so')]
    subprocess.run([str(converter), 'link', '--in', str(pie), '--out', str(elf), '--stub-dir', str(sdk / 'target/lib'),
        *sum([['--stub', str(p)] for p in stubs], []), '--module-sdk', '0x02000009', '--companion-sdk', '0x08050001', '--file-name', 'eboot.elf'], check=True)
    if args.check_only:
        print('PASS205 target compile/link/converter; no signed candidate ZIP')
        return
    subprocess.run([str(converter), 'self', '--sign', '--in', str(elf), '--out', str(app / 'eboot.bin'), '--magic', '0x1D3D154F'], check=True)
    subprocess.run([str(converter), 'self', '--inspect', '--file', str(app / 'eboot.bin')], check=True)
    notice = app / 'licenses/LWJGL333-PORT.txt'
    notice.write_text('Matched genuine LWJGL3.3.3+5 PS5 Java platform/dispatch overlay and native JNI group.\n'
        'Upstream: https://github.com/LWJGL/lwjgl3/tree/f0ec1437a6149dae00eaa27c47268e5e4efb129f\n'
        'Port source: https://github.com/mateo-cogeanu/ProsperoCraft/tree/main/client/ports/lwjgl333\n'
        'Original publisher game/library JARs are downloaded, verified and retained intact.\n'
        'Only listed platform/dispatch classes take precedence in the separate333 owner; no game remapping/transformation.\n'
        'Bootstrap integration is GPL-3.0-or-later; LWJGL source/patches BSD-3-Clause; STB individual upstream notices retained.\n')
    shutil.copytree(ROOT / 'client/ports/lwjgl333', java / 'lwjgl333-source', dirs_exist_ok=True)
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(app.rglob('*')):
            if file.is_file():
                info = zipfile.ZipInfo(file.relative_to(work).as_posix())
                info.external_attr = 0o100777 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, file.read_bytes())
    record = {'app_version': '01.000.205', 'title_id': 'PPSA99874', 'package_sha256': sha(package),
        'package_bytes': package.stat().st_size, 'baseline_package_sha256': BASE_PACKAGE, 'baseline_relink_sha256': BASE_RELINK,
        'symbols_sha256': sha(pie), 'eboot_sha256': sha(app / 'eboot.bin'), 'runtime': pin,
        'parentNativeGroupsRetainedSha256': {n: sha(p) for n, p in old_groups.items() if n not in ('java',)},
        'javaRuntimeClassesAndImage': 'exact204 modules retained; native libjava handle hook rebuilt',
        'newGroupSha256': sha(registry / 'embedded-lwjgl333.o'), 'overlaySha256': sha(overlay),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'source_tree': 'modified' if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip() else 'clean',
        'scope': 'Development Vanilla1.21.11 only; original121libraries downloaded;26.x support/resources/options retained; Fabric121blocked',
        'console': 'NOT TESTED', 'releaseStore': 'No action'}
    (output / 'build-audit.json').write_text(json.dumps(record, indent=2) + '\n')
    (output / 'SHA256SUMS').write_text(record['package_sha256'] + '  PPSA99874.zip\n')
    shutil.copyfile(pie, output / pie.name)
    print('LOCAL205', package, 'SHA256', record['package_sha256'])


if __name__ == '__main__':
    main()
