#!/usr/bin/env python3
"""Local247 integrates experimental PS5 generational ZGC using exact accepted204 inputs. No releases.

Original343/OpenAL groups are retained byte for byte from the relink kit.
Main, explicit libjava handle hook, SDL, graphics inventory and matched333 are rebuilt.
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
from storage_bootstrap_policy import normalize

BASE_PACKAGE = '89167d01c7da0ece733b0dd8b7871a05ee38ff5f79ee45b4ce9beefc5d4c14a0'
BASE_RELINK = '4351224b234d2b16a688afc4d31f23f0c6badc30670d034ad065cc629bce9f0f'


TINYFD_JAR = 'lwjgl-tinyfd-3.4.1.jar'
TINYFD_SHA256 = '3ffad01103b6cbc8c12c7156691fd87a96f063600a5ff5c9087d321c6736963a'
TINYFD_CLASSPATH = '/app0/assets/java25/ports/' + TINYFD_JAR


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
    parser.add_argument('--presenter-object',type=Path,required=True)
    parser.add_argument('--graphics-build', type=Path, required=True)
    parser.add_argument('--sdl-build',type=Path,required=True)
    parser.add_argument('--oshi665-build',type=Path,required=True)
    parser.add_argument('--hotspot-object', type=Path, required=True)
    parser.add_argument('--tinyfd-jar', type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--app-version', choices=('01.000.247',), default='01.000.247')
    parser.add_argument('--check-only', action='store_true', help='Compile/link/convert without signing or a candidate ZIP')
    args = parser.parse_args()
    if sha(args.tinyfd_jar) != TINYFD_SHA256:
        raise ValueError('Wrong publisher TinyFD 3.4.1 artifact')
    app_version = args.app_version
    candidate = app_version.split('.')[-1]
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
                if not current.is_file():
                    raise ValueError('Missing204 native bootstrap source: ' + str(current))
                body = normalize(str(original.relative_to(source_base)), current.read_text()).encode()
                if str(original.relative_to(source_base)) == 'client/startup/bootstrap.cpp':
                    text, count = re.subn(r'^#ifdef PROSPERO_LWJGL333_CLOSURE_RESERVE\n.*?^#endif\n', '', body.decode(), flags=re.M | re.S)
                    if count != 2:
                        raise ValueError('Expected exactly the two explicit333 reserve bootstrap blocks')
                    body = text.encode()
                if hashlib.sha256(body).hexdigest() != sha(original):
                    raise ValueError('204 native bootstrap/policy changed beyond explicit333 reserve: ' + str(current))
    report_pin=json.loads((ROOT/'client/launcher/report-runtime.json').read_text())
    pin = json.loads((ROOT / 'client/ports/lwjgl333/runtime.json').read_text())
    for name, digest in pin['source_sha256'].items():
        expected=report_pin['source_sha256'].get(name,digest)
        if sha(runtime / name) != expected:
            raise ValueError('Wrong runtime namespace/report integration: ' + name)
    if sha(runtime / '.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava/NativeLibraries.o') != pin['nativeLibrariesObjectSha256']:
        raise ValueError('Target libjava needs the pinned137 build')
    report_pin=json.loads((ROOT/'client/launcher/report-runtime.json').read_text())
    for name,digest in report_pin['source_sha256'].items():
        if sha(runtime/name)!=digest:raise ValueError('Report runtime integration mismatch')
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
    for file in (ROOT / 'client/ports/lwjgl333/bridge.c', ROOT / 'client/native/lwjgl_resident.c', ROOT / 'client/ports/libffi/closures_wx.c'):
        if sha(file) != native_audit['sourceUnitsSha256'][file.name]:
            raise ValueError('Stale333 native helper: ' + file.name)
    if sha(ROOT / 'client/ports/lwjgl/PS5Config.h') != native_audit['sharedConfigSha256']:
        raise ValueError('Stale333 target configuration')
    # Scope native allocator,stdio,etc imports to the existing actual graphics
    # provider. Matched333's own definitions get a separate runtime namespace.
    scoped = work / 'lwjgl333-scoped-imports.o'
    subprocess.run([str(llvm / 'llvm-objcopy'), '--redefine-syms=' + str(baseline / 'provider-bindings.txt'),
                    str(native), str(scoped)], check=True)
    sdl_build=args.sdl_build.resolve();sdl_object=sdl_build/'resident-sdl.o';sdl_audit=json.loads((sdl_build/'audit.json').read_text())
    if sha(sdl_object)!=sdl_audit['object_sha256']:raise ValueError('Stale SDL output')
    for name,digest in sdl_audit['port_sha256'].items():
        if sha(ROOT/'client/ports/sdl'/name)!=digest:raise ValueError('Stale SDL source: '+name)
    sdl_scoped=work/'sdl247-scoped.o'
    subprocess.run([str(llvm/'llvm-objcopy'),'--redefine-syms='+str(baseline/'provider-bindings.txt'),str(sdl_object),str(sdl_scoped)],check=True)
    os_build=args.oshi665_build.resolve();os_overlay=os_build/'oshi-6.6.5-ps5-platform.jar';os_audit=json.loads((os_build/'audit.json').read_text())
    if sha(os_overlay)!=os_audit['output_sha256']:raise ValueError('Stale OSHI665 overlay')
    for name,digest in os_audit['source_sha256'].items():
        if sha(ROOT/'client/ports/oshi665'/name)!=digest:raise ValueError('Stale OSHI665 source: '+name)
    graphics_build = args.graphics_build.resolve()
    graphics_object = graphics_build / 'graphics-support.o'
    graphics_audit = json.loads((graphics_build / 'audit.json').read_text())
    if sha(graphics_object) != graphics_audit['objects_sha256']['graphics-support.o']:
        raise ValueError('Stale graphics output')
    recipe = graphics_audit['wsi_diagnostics']['source_recipe']
    for category, directory in (('patches','zink'),('wsi_patches','mesa'),('wsi_headers','mesa')):
        for name, digest in recipe[category].items():
            if sha(ROOT / 'client/ports' / directory / name) != digest:
                raise ValueError('Stale graphics source: ' + name)
    presenter=args.presenter_object.resolve();presenter_audit=json.loads(presenter.with_suffix('.json').read_text());presentation_pin=json.loads((ROOT/'client/launcher/presentation-runtime.json').read_text())
    if sha(presenter)!=presenter_audit['output_sha256']:raise ValueError('Stale native presenter')
    for name,digest in presentation_pin['source_sha256'].items():
        if sha(runtime/name)!=digest:raise ValueError('Wrong presentation runtime source: '+name)
    for name,digest in presenter_audit['source_sha256'].items():
        if sha(runtime/name)!=digest:raise ValueError('Stale presenter object source: '+name)
    groups = []
    old_groups = {}
    for item in manifest['arguments']:
        match = re.fullmatch(r'inputs/\d+-embedded-([a-z0-9_]+)\.o', item)
        if match:
            old_groups[match[1]] = baseline / item
    core = {'jvm', 'java', 'zip', 'jimage', 'net', 'nio', 'verify', 'management', 'management_ext', 'awt', 'lcms'}
    for name, obj in old_groups.items():
        if name not in core:
            groups.append({'name': name, 'objects': [str(sdl_scoped if name=='ps5sdl' else obj)]})
    groups.append({'name': 'lwjgl333', 'objects': [str(scoped)]})
    registry = work / 'registry'
    registry.mkdir(exist_ok=True)
    sync_pin = json.loads((ROOT / 'client/launcher/extra-mutex-runtime.json').read_text())
    if sha(args.hotspot_object) != sync_pin['object_sha256'] or sha(runtime / sync_pin['patch']) != sync_pin['patch_sha256']:
        raise ValueError('HotSpot object or source does not match the PS5 synchronization pin')
    shutil.copyfile(args.hotspot_object, registry / 'embedded-jvm.o')
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
    # Replace retired logo payloads too, not only the compiled picker pixels.
    shutil.copyfile(ROOT / 'client/launcher/instance_icons.hpp', java / 'launcher-toolkit/instance_icons.hpp')
    icons = ROOT / 'assets/launcher-icons'
    for directory, suffixes in (('launcher-icons', ('.svg', '.png')), ('launcher-icon-source', ('.svg',))):
        destination = java / directory
        for retired in ('flame', 'modrinth'):
            for suffix in suffixes:
                (destination / (retired + suffix)).unlink()
        for replacement in ('amethyst', 'compass'):
            for suffix in suffixes:
                shutil.copyfile(icons / (replacement + suffix), destination / (replacement + suffix))
        shutil.copyfile(icons / 'attribution.json', destination / 'attribution.json')
    shutil.copyfile(ROOT/'client/startup/log4j2-startup.xml',java/'log4j2-startup.xml')
    shutil.copyfile(overlay, java / 'ports' / overlay.name)
    (java/'graphics-resolution-audit.json').write_text(json.dumps(graphics_audit,indent=2)+'\n')
    shutil.copyfile(os_overlay,java/'ports'/os_overlay.name)
    (java/'oshi665-platform-audit.json').write_text(json.dumps(os_audit,indent=2)+'\n')
    (java/'sdl-resolution-audit.json').write_text(json.dumps(sdl_audit,indent=2)+'\n')
    shutil.copyfile(runtime / '.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libjava.so', java / 'lib/libjava.so')
    shutil.copyfile(registry / 'builtin-resident-audit.json', java / 'resident-libraries-audit.json')
    (java / 'lwjgl333-integration-audit.json').write_text(json.dumps({'runtime': pin, 'java': java_audit, 'native': native_audit,
        'importsScopedSha256': sha(scoped), 'groupSha256': sha(registry / 'embedded-lwjgl333.o'), 'console': 'NOT RUN'}, indent=2) + '\n')
    # Restore TinyFD to the parent that owns the other 26.x LWJGL bindings.
    header = args.base_header.read_text()
    cp_value = re.fullmatch(r'#pragma once\n#define CLIENT_CLASSPATH_OPTION "([^"\n]+)"\s*', header)
    if not cp_value or cp_value[1].encode() + b'\0' not in (baseline / 'inputs/104-main.o').read_bytes():
        raise ValueError('Classpath header differs from actual accepted204 main object')
    if 'lwjgl-tinyfd' in cp_value[1]:
        raise ValueError('Unexpected existing TinyFD classpath entry')
    tinyfd = java / 'ports' / TINYFD_JAR
    shutil.copyfile(args.tinyfd_jar, tinyfd)
    (work / 'client_classpath.hpp').write_text(
        header.replace(cp_value[1], cp_value[1] + ':' + TINYFD_CLASSPATH))
    from build_launcher_toolkit import dispatch
    dispatch(work)
    parent = [java / 'ports/lwjgl-3.4.3-ps5-modules.jar', java / 'ports/lwjgl-3.4.3-ps5-platform.jar',
              java / 'ports/lwjgl-glfw-3.4.1-ps5-callback343.jar', tinyfd, *sorted((java / 'client/jars').glob('*.jar')), java / 'client-probe.jar']
    jit_pin = json.loads((ROOT / 'client/launcher/jit-warmup-runtime.json').read_text())
    jit_source = runtime / jit_pin['path']
    if sha(jit_source) != jit_pin['sha256']:
        raise ValueError('Tiered warmup source does not match runtime pin')
    classes = work / 'classes'
    shutil.rmtree(classes, ignore_errors=True)
    classes.mkdir()
    subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-cp', os.pathsep.join(map(str, parent)),
                    '-d', str(classes), str(ROOT / 'client/startup/ClientStartup25.java'), str(jit_source),
                    *map(str, sorted((ROOT / 'client/launcher/java').glob('*.java')))], check=True)
    files = list(classes.rglob('*.class'))
    names = {f.relative_to(classes).as_posix() for f in files}
    jar = java / 'client-probe.jar'
    temporary = jar.with_suffix('.tmp')
    with zipfile.ZipFile(jar) as original, zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as out:
        for info in original.infolist():
            if info.filename not in names and info.filename not in ('prosperocraft-build.properties', 'prosperocraft-121.txt'):
                out.writestr(info, original.read(info))
        for file in files:
            out.writestr(file.relative_to(classes).as_posix(), file.read_bytes())
        out.writestr('prosperocraft-build.properties', ('app_version='+app_version+'\ntitle_id=PPSA99874\n').encode())
        out.writestr('prosperocraft-121.txt', b'vanilla-1.21.9-1.21.11-zink-v3\n')
    temporary.replace(jar)
    for file in files:
        destination = java / 'classes' / file.relative_to(classes)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, destination)
    (java / 'classes/prosperocraft-build.properties').write_text('app_version='+app_version+'\ntitle_id=PPSA99874\n')
    (java / 'classes/prosperocraft-121.txt').write_text('vanilla-1.21.9-1.21.11-zink-v3\n')
    param = json.loads((app / 'sce_sys/param.json').read_text())
    if not int(param.get('attribute3',0))&0x40:raise ValueError('120Hz title declaration missing')
    param['contentVersion'] = app_version
    param['downloadDataSize'] = 4096
    (app / 'sce_sys/param.json').write_text(json.dumps(param, indent=2) + '\n')
    sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
    flags = ['-target', 'x86_64-sie-ps5', '-fvisibility-nodllstorageclass=default', '-isysroot', str(sdk),
             '-isystem', str(sdk / 'target/include/c++/v1'), '-isystem', str(sdk / 'target/include'),
             '-march=x86-64', '-mno-avx', '-mno-avx2', '-mno-fma', '-O2', '-fno-stack-protector',
             '-fno-plt', '-femulated-tls', '-ffunction-sections', '-fdata-sections']
    main_obj = work / ('main'+candidate+'.o')
    subprocess.run([str(llvm / 'clang++'), *flags, '-DPROSPERO_APP_VERSION="'+app_version+'"', '-DPROSPERO_LWJGL333_CLOSURE_RESERVE=1', '-std=c++20',
        '-Wall', '-Wextra', '-Werror', '-fno-exceptions', '-fno-rtti',
        *['-I' + str(p) for p in (runtime / 'native/renderer', runtime / 'build/native', runtime / 'src',
          runtime / 'native', work, ROOT / 'client/native', ROOT / 'client/launcher/toolkit/src',
          ROOT / '.tools/PS5_Mesa/include', runtime / 'java25/probe', runtime / 'java25/platform')],
        '-c', str(ROOT / 'client/save_headroom/bootstrap.cpp'), '-o', str(main_obj)], check=True)
    emutls_backend = work / 'emutls-backend.o'
    subprocess.run([str(llvm / 'clang++'), *flags, '-std=c++20',
        '-Wall', '-Wextra', '-Werror', '-fno-exceptions', '-fno-rtti',
        '-I' + str(runtime / '.tools/java25/openjdk/src/hotspot/share'),
        '-c', str(runtime / 'java25/probe/emutls_alloc.cpp'),
        '-o', str(emutls_backend)], check=True)
    storage_fault=work/'storage-fault.o'
    fault_renames=['-Dps5shaderc_fault_'+suffix+'=prospero_storage_fault_'+suffix for suffix in ('begin','end','status','extended_status')]
    subprocess.run([str(llvm/'clang'),*flags,'-fPIC',*fault_renames,'-c',str(ROOT/'client/ports/shaderc/fault.c'),'-o',str(storage_fault)],check=True)
    libraries = work / 'libraries'
    libraries.mkdir(exist_ok=True)
    for row in manifest['files']:
        file = baseline / row['path']
        if file.suffix in ('.a', '.so'):
            destination = libraries / file.name.split('-', 1)[1]
            if not destination.exists():
                os.link(file, destination)
    pie = work / ('client121-'+candidate+'-symbols.elf')
    replacements = {'inputs/062-backend.o': emutls_backend, 'inputs/031-embedded-jvm.o': registry / 'embedded-jvm.o', 'inputs/022-renderer.o':presenter,'inputs/110-graphics-support.o': graphics_object, 'inputs/104-main.o': main_obj, 'inputs/044-embedded-ps5sdl.o': registry/'embedded-ps5sdl.o', 'inputs/032-embedded-java.o': registry / 'embedded-java.o',
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
    link.append(str(storage_fault))
    response = work / ('link'+candidate+'.rsp')
    response.write_text('\n'.join(json.dumps(x) for x in link) + '\n')
    subprocess.run([str(args.lld.absolute()), '@' + str(response)], check=True)
    converter = runtime / 'build/native/host/ps5-native-tool'
    elf = work / 'eboot.elf'
    stubs = [baseline / name for name in ('inputs/029-libSceMouse.so', 'inputs/030-libSceAudioIn.so',
                                        'inputs/027-libSceAgc.so', 'inputs/028-libSceAgcDriver.so')]
    subprocess.run([str(converter), 'link', '--in', str(pie), '--out', str(elf), '--stub-dir', str(sdk / 'target/lib'),
        *sum([['--stub', str(p)] for p in stubs], []), '--module-sdk', '0x02000009', '--companion-sdk', '0x08050001', '--file-name', 'eboot.elf'], check=True)
    if args.check_only:
        print('PASS247 target compile/link/converter; no signed candidate ZIP')
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
    (java/'native-presentation-audit.json').write_text(json.dumps({'runtime':presentation_pin,'build':presenter_audit},indent=2)+'\n')
    for name in presentation_pin['source_sha256']:
        destination=java/'native-presentation-source'/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(runtime/name,destination)
    storage_sources=('client/launcher/storage_paths.hpp','client/launcher/native_menu.hpp','client/launcher/report-runtime.json','client/ports/shaderc/fault.c','client/ports/openal/startup_boundary.hpp','client/ports/sdl/ps5_startup_boundary.h','client/startup/log4j2-startup.xml','client/startup/file_pressure_report.hpp')
    for name in storage_sources:
        destination=java/'storage-source'/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,destination)
    for name in report_pin['source_sha256']:
        destination=java/'storage-source/runtime'/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(runtime/name,destination)
    (java/'storage-path-audit.json').write_text(json.dumps({'runtime':report_pin,'source_sha256':{name:sha(ROOT/name) for name in storage_sources},'fault_object_sha256':sha(storage_fault),'fault_symbols':'prospero_storage_fault_*; original shaderc group remains retained','default':'download0 for reports and temporary files; verified existing shared catalogs are preserved without further migration','console':'NOT TESTED'},indent=2)+'\n')
    shutil.copytree(ROOT/'client/ports/oshi665',java/'oshi665-source',dirs_exist_ok=True)
    source_sdl=java/'sdl-resolution-source';source_sdl.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'client/ports/mesa/0011-videoout-launcher-resolutions.patch',source_sdl/'0011-videoout-launcher-resolutions.patch')
    for name in ('SDL_ps5video.c','ps5_display_mode.h'):
        shutil.copyfile(ROOT/'client/ports/sdl'/name,source_sdl/name)
    shutil.copytree(ROOT / 'client/ports/lwjgl333', java / 'lwjgl333-source', dirs_exist_ok=True)
    shared_source = java / 'lwjgl333-source/shared-libffi'
    shared_source.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'client/ports/libffi/closures_wx.c', shared_source / 'closures_wx.c')
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(app.rglob('*')):
            if file.is_file():
                info = zipfile.ZipInfo(file.relative_to(work).as_posix())
                info.external_attr = 0o100777 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, file.read_bytes())
    record = {'app_version': app_version, 'title_id': 'PPSA99874', 'package_sha256': sha(package),
        'package_bytes': package.stat().st_size, 'baseline_package_sha256': BASE_PACKAGE, 'baseline_relink_sha256': BASE_RELINK,
        'symbols_sha256': sha(pie), 'eboot_sha256': sha(app / 'eboot.bin'), 'runtime': pin,
        'parentNativeGroupsRetainedSha256': {n: sha(p) for n, p in old_groups.items() if n not in ('jvm','java','ps5sdl')},
        'javaRuntimeClassesAndImage': 'exact204 modules retained; native libjava handle hook rebuilt',
        'compilerTlsBackendSha256': sha(emutls_backend),
        'compilerTlsSourceSha256': sha(runtime / 'java25/probe/emutls_alloc.cpp'),
        'newGroupSha256': sha(registry / 'embedded-lwjgl333.o'), 'overlaySha256': sha(overlay),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'source_tree': 'modified' if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip() else 'clean',
        'scope': 'Select genuine generational ZGC with PS5 direct-memory physical backing and C2 tier4.',
        'tinyfd_sha256': TINYFD_SHA256, 'jitWarmupRuntime': jit_pin, 'extraMutexRuntime': sync_pin,
        'nativePresenterSha256':sha(presenter),'presentationRuntime':presentation_pin,'graphicsSupportSha256':sha(graphics_object),'newSdlGroupSha256':sha(registry/'embedded-ps5sdl.o'),'oshi665Sha256':sha(os_overlay),
        'console': 'NOT TESTED', 'releaseStore': 'No action'}
    (output / 'build-audit.json').write_text(json.dumps(record, indent=2) + '\n')
    (output / 'SHA256SUMS').write_text(record['package_sha256'] + '  PPSA99874.zip\n')
    shutil.copyfile(pie, output / pie.name)
    print('LOCAL247', package, 'SHA256', record['package_sha256'])


if __name__ == '__main__':
    main()
