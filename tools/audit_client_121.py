#!/usr/bin/env python3
"""Independently inspect local candidates against accepted204 and original333 inputs.

Requires explicit SDK build outputs and publisher cache; not a portable CI lane
or evidence of physical-console acceptance. Never modifies packages or game JARs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import zipfile

from audit_client_261 import jar_info, jni_mangle
from build_lwjgl333 import publisher_jars
from host_toolchain import ROOT, java_home
from package_client_121 import (APP_VERSIONS, BASE_PACKAGE, HTTP_IMAGE_AUDIT, OSHI6410_JAR, OSHI6410_PIN,
                                TINYFD_CLASSPATH, TINYFD_JAR, TINYFD_SHA256, release121_gate,
                                release_with_http_module, verify_http_image)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(nm, path, external=True):
    flags = ['--defined-only'] + (['--extern-only'] if external else [])
    return set(subprocess.check_output([str(nm), *flags, str(path)], text=True).split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('package', 'baseline-package', 'build-dir', 'lwjgl333-build', 'publisher-cache', 'llvm-nm', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--app-version', choices=APP_VERSIONS, default=APP_VERSIONS[-1])
    parser.add_argument('--java-home', type=Path)
    args = parser.parse_args()
    candidate = args.app_version.split('.')[-1]
    linked_symbols = args.build_dir / f'client121-{candidate}-symbols.elf'
    if sha(args.baseline_package) != BASE_PACKAGE:
        raise ValueError('Not the exact accepted204 package')
    prefix = 'PPSA99874/assets/java25/'
    with zipfile.ZipFile(args.baseline_package) as old, zipfile.ZipFile(args.package) as new:
        names = new.namelist()
        if new.testzip() or len(names) != len(set(names)):
            raise ValueError('ZIP CRC/duplicate failure')
        if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):
            raise ValueError('Unsafe ZIP path')
        retired_icons = {prefix + directory + '/' + stem + suffix
                         for directory, suffixes in (('launcher-icons', ('.svg', '.png')), ('launcher-icon-source', ('.svg',)))
                         for stem in ('flame', 'modrinth') for suffix in suffixes}
        replacement_icons = {prefix + directory + '/' + stem + suffix
                             for directory, suffixes in (('launcher-icons', ('.svg', '.png')), ('launcher-icon-source', ('.svg',)))
                             for stem in ('amethyst', 'compass') for suffix in suffixes}
        if set(old.namelist()) - set(names) != retired_icons or retired_icons & set(names):
            raise ValueError('Unexpected removed/retained logo assets')
        for name in replacement_icons | {prefix + directory + '/attribution.json' for directory in ('launcher-icons', 'launcher-icon-source')}:
            if new.read(name) != (ROOT / 'assets/launcher-icons' / Path(name).name).read_bytes():
                raise ValueError('Replacement icon/attribution mismatch: ' + name)
        if new.read(prefix+'launcher-toolkit/instance_icons.hpp') != (ROOT/'client/launcher/instance_icons.hpp').read_bytes():
            raise ValueError('Bundled picker pixel source is stale')
        changed = [n for n in old.namelist() if n in names and old.read(n) != new.read(n)]
        allowed = {'PPSA99874/eboot.bin', 'PPSA99874/sce_sys/param.json', prefix + 'client-probe.jar',
                   prefix + 'lib/libjava.so', prefix + 'resident-libraries-audit.json',
                   prefix + 'classes/prosperocraft-build.properties', prefix+'log4j2-startup.xml', prefix+'launcher-icons/attribution.json', prefix+'launcher-icon-source/attribution.json', prefix+'launcher-toolkit/instance_icons.hpp'}
        if candidate == '280':
            allowed.update({prefix + 'lib/modules', prefix + 'release'})
            with TemporaryDirectory(prefix='prosperocraft-http-package-') as temporary:
                original = Path(old.extract(prefix + 'lib/modules', Path(temporary) / 'old'))
                expanded = Path(new.extract(prefix + 'lib/modules', Path(temporary) / 'new'))
                http_audit = verify_http_image(java_home(args.java_home), original, expanded)
            if http_audit != json.loads(new.read(prefix + HTTP_IMAGE_AUDIT)):
                raise ValueError('Packaged HTTP module audit differs from image contents')
            if new.read(prefix + 'release').decode() != release_with_http_module(old.read(prefix + 'release').decode()):
                raise ValueError('Packaged Java module declaration differs from expected')
        if any(n not in allowed and not (n.startswith(prefix + 'classes/') and n.endswith('.class')) for n in changed):
            raise ValueError('Unexpected baseline change: ' + repr(changed))
        added = sorted(set(names) - set(old.namelist()))
        older_provider = {prefix + n for n in ('ports/' + OSHI6410_JAR, 'oshi6410-source-pin.json',
                                                'oshi6410-platform-audit.json')} if candidate in ('257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280') else set()
        if candidate == '280':
            older_provider.add(prefix + HTTP_IMAGE_AUDIT)
        for n in added:
            if not (n in older_provider or n in replacement_icons or n.startswith(prefix + 'lwjgl333-source/') or n.startswith(prefix + 'classes/') or n.startswith(prefix+'native-presentation-source/') or n.startswith(prefix+'storage-source/') or n.startswith(prefix+'oshi665-source/') or n.startswith(prefix+'sdl-resolution-source/') or
                    n in {prefix + 'ports/' + TINYFD_JAR, prefix+'native-presentation-audit.json',prefix+'storage-path-audit.json',prefix+'graphics-resolution-audit.json',prefix+'oshi665-platform-audit.json', prefix+'sdl-resolution-audit.json',prefix+'ports/oshi-6.6.5-ps5-platform.jar',prefix + 'lwjgl333-integration-audit.json', prefix + 'ports/lwjgl-3.3.3-ps5-overlay.jar',
                          'PPSA99874/licenses/LWJGL333-PORT.txt'}):
                raise ValueError('Unexpected added file: ' + n)
        tinyfd_bytes = new.read(prefix + 'ports/' + TINYFD_JAR)
        if hashlib.sha256(tinyfd_bytes).hexdigest() != TINYFD_SHA256:
            raise ValueError('Packaged TinyFD differs from the publisher artifact')
        param = json.loads(new.read('PPSA99874/sce_sys/param.json'))
        if param['contentVersion'] != args.app_version or param['downloadDataSize'] != 4096:
            raise ValueError('Wrong identity')
        if new.read(prefix + 'classes/prosperocraft-121.txt') != release121_gate(args.app_version):
            raise ValueError('Wrong per-release gate')
        if new.read(prefix + 'ports/lwjgl-3.3.3-ps5-overlay.jar') != (args.lwjgl333_build / 'lwjgl-3.3.3-ps5-overlay.jar').read_bytes():
            raise ValueError('Wrong overlay')
        if b'checkTiered' not in new.read(prefix + 'classes/ps5probe/JitWarmup25.class'):
            raise ValueError('Tiered warmup helper was not packaged')
        os_audit = json.loads(new.read(prefix + 'oshi665-platform-audit.json'))
        if hashlib.sha256(new.read(prefix + 'ports/oshi-6.6.5-ps5-platform.jar')).hexdigest() != os_audit['output_sha256']:
            raise ValueError('OSHI665 package mismatch')
        for name, digest in os_audit['source_sha256'].items():
            if hashlib.sha256(new.read(prefix + 'oshi665-source/' + name)).hexdigest() != digest:
                raise ValueError('OSHI665 packaged source mismatch')
        if candidate in ('257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280'):
            old_audit = json.loads(new.read(prefix + 'oshi6410-platform-audit.json'))
            source_pin = new.read(prefix + 'oshi6410-source-pin.json')
            if (old_audit['version'] != '6.4.10' or source_pin != OSHI6410_PIN.read_bytes()
                    or old_audit['source_pin_sha256'] != hashlib.sha256(source_pin).hexdigest()
                    or old_audit['source_sha256'] != os_audit['source_sha256']
                    or old_audit['output_sha256'] != hashlib.sha256(new.read(prefix + 'ports/' + OSHI6410_JAR)).hexdigest()):
                raise ValueError('OSHI 6.4.10 package mismatch')
        if new.read(prefix+'log4j2-startup.xml')!=(ROOT/'client/startup/log4j2-startup.xml').read_bytes():raise ValueError('Stale logging configuration')
        storage_audit=json.loads(new.read(prefix+'storage-path-audit.json'))
        for name,digest in storage_audit['source_sha256'].items():
            if hashlib.sha256(new.read(prefix+'storage-source/'+name)).hexdigest()!=digest:raise ValueError('Storage source mismatch')
        for name,digest in storage_audit['runtime']['source_sha256'].items():
            if hashlib.sha256(new.read(prefix+'storage-source/runtime/'+name)).hexdigest()!=digest:raise ValueError('Storage runtime source mismatch')
        presentation_audit=json.loads(new.read(prefix+'native-presentation-audit.json'))
        for name,digest in presentation_audit['runtime']['source_sha256'].items():
            if hashlib.sha256(new.read(prefix+'native-presentation-source/'+name)).hexdigest()!=digest:raise ValueError('Packaged presentation source mismatch')
        graphics_audit = json.loads(new.read(prefix + 'graphics-resolution-audit.json'))
        # Parent JARs, Java image, VM options and original26 resource tokens must
        # remain byte-identical. Exploded updated classes must match their JAR.
        import io
        with zipfile.ZipFile(io.BytesIO(new.read(prefix + 'client-probe.jar'))) as probe:
            if probe.read('prosperocraft-121.txt') != release121_gate(args.app_version):
                raise ValueError('Wrong probe JAR release gate')
            for n in names:
                if n.startswith(prefix + 'classes/'):
                    relative = n[len(prefix + 'classes/'):]
                    if relative in probe.namelist() and new.read(n) != probe.read(relative):
                        raise ValueError('Exploded/JAR class mismatch: ' + relative)
            with zipfile.ZipFile(io.BytesIO(old.read(prefix + 'client-probe.jar'))) as previous:
                for n in previous.namelist():
                    if not n.endswith('.class') and n not in ('prosperocraft-build.properties','prosperocraft-121.txt') and previous.read(n) != probe.read(n):
                        raise ValueError('Existing probe resource changed: ' + n)
        growth = sum(i.file_size for i in new.infolist()) - sum(i.file_size for i in old.infolist())
        if growth > 8 * 1024 * 1024:
            raise ValueError('Exceeds approved provisional8MiB budget; reassess before handoff')
        registry = json.loads(new.read(prefix + 'resident-libraries-audit.json'))
        if registry['library_symbol_prefixes'] != {'lwjgl333': 'lwjgl333_'}:
            raise ValueError('Wrong generation namespace')
    # The final image must contain selected-size routing and the new SDL group.
    linked_text=linked_symbols.read_bytes()
    if b'MESA_DISK_CACHE_DATABASE_NUM_PARTS\0' not in linked_text:
        raise ValueError('Shader cache partition budget missing')
    for option in (b'-XX:+UseCountedLoopSafepoints', b'-XX:LoopStripMiningIter=1000'):
        if option + b'\0' not in linked_text:
            raise ValueError('C2 safepoint polling option missing')
    if b'-XX:+UseParallelGC\0' in linked_text or b'-XX:+UseG1GC\0' in linked_text:
        raise ValueError('Conflicting collector option in ZGC candidate')
    if b'ZGC: reserve requested=' not in linked_text:
        raise ValueError('PS5 ZGC native reservation trace missing')
    if b'ZGC: direct map kernel result=' not in linked_text:
        raise ValueError('ZGC mapping diagnostics missing or stale target object')
    if b'/dev/dmem0\0' not in linked_text:
        raise ValueError('ZGC direct device fallback missing')
    if b'ZGC: native restore failed address=' not in linked_text:
        raise ValueError('ZGC native reservation restoration missing or stale')
    if b'PS5 ZGC direct mapping failed' not in linked_text:
        raise ValueError('PS5 ZGC physical backend missing')
    if b'PS5 first EMFILE descriptor snapshot' not in linked_text:
        raise ValueError('First EMFILE capture is missing')
    for value in (b'PS5_RENDER_SIZE',b'PS5 selected render resolution is malformed or unavailable'):
        if value not in linked_text:raise ValueError('Missing selected-resolution native path')
    native = args.lwjgl333_build / 'ps5/lwjgl333.o'
    if candidate in ('263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280'):
        native_audit = json.loads((native.parent / 'audit.json').read_text())
        adapter = native.parent / 'closures_wx.c.o'
        sizes = subprocess.check_output([str(args.llvm_nm), '-S', str(adapter)], text=True)
        reserve = next((line.split() for line in sizes.splitlines() if line.split() and line.split()[-1] == 'reserve'), None)
        # PS5 x86-64 Reserve has two 8-byte fields, a 4-byte atomic and alignment.
        if (reserve is None or native_audit['closureReserveCount'] != 512 or int(reserve[1], 16) != 512 * 24
                or sha(adapter) != native_audit['objectsSha256'][adapter.name]):
            raise ValueError('Missing actual 512-page callback reserve metadata')
    raw = symbols(args.llvm_nm, native)
    if 'prospero_ffi_reserve_prime' not in raw or 'ffi_closure_alloc' not in raw:
        raise ValueError('Missing generation-owned callback reserve')
    scoped = symbols(args.llvm_nm, args.build_dir / 'registry/embedded-lwjgl333.o')
    if any(n.startswith('Java_') for n in scoped) or 'lwjgl333_Java_org_lwjgl_opengl_GL32C_nglDeleteSync' not in scoped:
        raise ValueError('Generation JNI symbols not isolated')
    # Exact unsupported desktop APIs are disclosed, not redirected to343.
    unsupported = {'org/lwjgl/system/SharedLibraryUtil', 'org/lwjgl/system/libc/LibCErrno',
                   'org/lwjgl/system/libc/LibCLocale', 'org/lwjgl/system/libc/LibCStdio'}
    counts, absent = {}, []
    tinyfd = jar_info(next(p for p in publisher_jars(args.publisher_cache) if p.name == 'lwjgl-tinyfd-3.3.3.jar'))[1]
    tinyfd_jar = args.build_dir / 'PPSA99874/assets/java25/ports' / TINYFD_JAR
    if tinyfd_jar.read_bytes() != tinyfd_bytes or set(jar_info(tinyfd_jar)[1]) != set(tinyfd):
        raise ValueError('TinyFD 3.4.1 and 3.3.3 native declarations differ')
    tinyfd_exports = symbols(args.llvm_nm, args.build_dir / 'registry/embedded-lwjgl_tinyfd.o')
    c = (ROOT / 'client/ports/tinyfd/ps5_dialogs.c').read_text()
    scalar = {'jlong': 'J', 'jint': 'I', 'void': 'V'}
    for owner, method, desc, static in tinyfd:
        name = 'Java_' + jni_mangle(owner) + '_' + jni_mangle(method)
        match = re.search(r'JNIEXPORT\s+(\w+)\s+JNICALL\s+' + re.escape(name) + r'\(([^)]*)\)', c)
        if not match or not static or name not in tinyfd_exports:
            raise ValueError('TinyFD adapter method missing')
        types = [part.strip().split()[0] for part in match[2].split(',')]
        actual = '(' + ''.join(scalar[t] for t in types[2:]) + ')' + scalar[match[1]]
        if types[:2] != ['JNIEnv*', 'jclass'] or actual != desc:
            raise ValueError('TinyFD adapter ABI mismatch: ' + method)
    for jar in publisher_jars(args.publisher_cache):
        covered = 0
        for owner, method, desc, static in jar_info(jar)[1]:
            if any(x in owner for x in ('/windows/', '/linux/', '/macosx/', '/WGL', '/GLX', '/tinyfd/')):
                continue
            if owner in unsupported:
                absent.append([owner, method, desc])
                continue
            short = 'Java_' + jni_mangle(owner) + '_' + jni_mangle(method)
            long = short + '__' + jni_mangle(desc[1:desc.index(')')])
            if short not in raw and long not in raw:
                raise ValueError('Missing matched333 native: ' + repr((owner, method, desc)))
            covered += 1
        counts[jar.name] = covered
    baseline = args.build_dir / 'baseline204'
    manifest = json.loads((baseline / 'manifest.json').read_text())
    linked = [json.loads(line) for line in (args.build_dir / f'link{candidate}.rsp').read_text().splitlines()]
    replaced = {'inputs/062-backend.o', 'inputs/031-embedded-jvm.o', 'inputs/022-renderer.o','inputs/110-graphics-support.o','inputs/104-main.o', 'inputs/044-embedded-ps5sdl.o', 'inputs/032-embedded-java.o', 'inputs/109-builtin-libraries.o'}
    if candidate in ('260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280'):
        replaced.add('inputs/048-embedded-jnidispatch.o')
        pin = json.loads((ROOT / 'client/launcher/jna-loader-runtime.json').read_text())
        jna = args.build_dir / 'registry/embedded-jnidispatch.o'
        expected_group = pin['group_sha256']
        if candidate in ('262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280'):
            provider = json.loads((ROOT / 'client/launcher/jna-provider.json').read_text())
            expected_group = provider['resident_group_sha256']
            undefined = {line.split()[-1] for line in subprocess.check_output(
                [str(args.llvm_nm), '-u', str(jna)], text=True).splitlines() if line.split()}
            if set(provider['bindings']) & undefined or not set(provider['bindings'].values()) <= undefined:
                raise ValueError('JNA allocator/closure ownership imports are incomplete')
        if linked.count(str(jna.resolve())) != 1 or sha(jna) != expected_group:
            raise ValueError('Wrong checked JNA loader object in the link')
        if b'Native library operation failed; error text allocation refused\0' not in linked_symbols.read_bytes():
            raise ValueError('Checked JNA loader error path missing from linked image')
    retained = {}
    for item in manifest['arguments']:
        if item.startswith('inputs/') and item not in replaced:
            file = (baseline / item).resolve()
            if linked.count(str(file)) != manifest['arguments'].count(item):
                raise ValueError('Baseline link input missing/duplicated: ' + item)
            retained[item] = sha(file)
    for row in manifest['files']:
        if sha(baseline / row['path']) != row['sha256']:
            raise ValueError('Retained relink input corrupted: ' + row['path'])
    sync_pin = json.loads((ROOT / 'client/launcher/extra-mutex-runtime.json').read_text())
    hotspot = args.build_dir / 'registry/embedded-jvm.o'
    if linked.count(str(hotspot.resolve())) != 1 or sha(hotspot) != sync_pin['object_sha256']:
        raise ValueError('Wrong HotSpot runtime in the link')
    synchronization_symbols = {'JVM_PS5SetExtraMutexReserveEnabled', '_ZN15PlatformMonitorC2Eb', '_ZN5MutexC2ENS_4RankEPKcbb',
        '_ZN10MethodData27initialize_extra_data_locksEv',
        'JVM_PS5SetExtendedNativeDirectBudgetEnabled'}
    if not synchronization_symbols <= symbols(args.llvm_nm, hotspot, external=False):
        raise ValueError('PS5 synchronization runtime entry points missing')
    emutls_backend = args.build_dir / 'emutls-backend.o'
    build_record = json.loads((args.package.parent / 'build-audit.json').read_text())
    if linked.count(str(emutls_backend.resolve())) != 1 or sha(emutls_backend) != build_record['compilerTlsBackendSha256']:
        raise ValueError('Compiler TLS backend must match the selected runtime ledger')
    fault=args.build_dir/'storage-fault.o'
    if linked.count(str(fault.resolve()))!=1 or sha(fault)!=storage_audit['fault_object_sha256']:raise ValueError('Storage fault object missing or stale')
    fault_symbols=symbols(args.llvm_nm,fault)
    for suffix in ('begin','end','status','extended_status'):
        if 'prospero_storage_fault_'+suffix not in fault_symbols or 'ps5shaderc_fault_'+suffix in fault_symbols:raise ValueError('Fault recorder namespace collision')
    sdl_group = str((args.build_dir / 'registry/embedded-ps5sdl.o').resolve())
    if linked.count(sdl_group) != 1:
        raise ValueError('Missing/duplicate rebuilt SDL group')
    stack_patch = '0008-radv-shader-object-stage-storage.patch'
    patches = graphics_audit['wsi_diagnostics']['source_recipe']['patches']
    if (stack_patch in patches) != (candidate in ('250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280')):
        raise ValueError('Wrong linked RADV shader-stage storage policy')
    graphics = [Path(n) for n in linked if n.endswith('/graphics-support.o')]
    if len(graphics) != 1 or sha(graphics[0]) != graphics_audit['objects_sha256']['graphics-support.o']:
        raise ValueError('Wrong linked graphics inventory')
    presenters=[Path(n) for n in linked if n.endswith('/presenter120.o')]
    if len(presenters)!=1 or sha(presenters[0])!=presentation_audit['build']['output_sha256']:raise ValueError('Missing/wrong native120 presenter')
    linked333 = str((args.build_dir / 'registry/embedded-lwjgl333.o').resolve())
    if linked.count(linked333) != 1:
        raise ValueError('Missing/duplicate333 native group')
    elf = (args.build_dir / 'eboot.elf').read_bytes()
    classpath = re.findall(rb'-Djava\.class\.path=[^\x00]+\x00', elf)
    original_main = (baseline / 'inputs/104-main.o').read_bytes()
    original_classpath = re.findall(rb'-Djava\.class\.path=[^\x00]+\x00', original_main)
    if len(original_classpath) != 1 or classpath != [
            original_classpath[0][:-1] + b':' + TINYFD_CLASSPATH.encode() + b'\0']:
        raise ValueError('Actual JVM classpath must append only the verified TinyFD JAR')
    for token in (b'libraryProgress\0', b'(Ljava/lang/String;JJ)Z\0', b'CIRCLE  Pause and use original library\0',
                  b'Your library only needs to move once.\0'):
        if token not in elf:
            raise ValueError('Missing storage progress UI or JNI registration: ' + repr(token))
    for root in (b'/download0',):
        log = root + b'/java25-jit.log'
        if (b'-Dps5.probe.jitLog=' + log + b'\0' not in elf or
                b'-Xlog:jit+compilation=debug,codecache=info:file=' + log + b':' not in elf):
            raise ValueError('JIT reader/writer path mismatch for ' + root.decode())
    if b'wrapped_open=%llu wrapped_close=%llu failed_open=%llu tracked_live=%u' not in elf:
        raise ValueError('File activity tracking compiled out')
    if b'12288mutex/8192relative/2048absolute' not in elf:
        raise ValueError('Missing extra mutex reserve bootstrap policy')
    if (b'-Dps5.fabric261Observer=true\0' in elf) != (candidate == '254'):
        raise ValueError('Unexpected Fabric 26.1 observer policy')
    if (b'-Dps5.save263Observer=true\0' in elf) != (candidate == '255'):
        raise ValueError('Unexpected 26.3 save observer policy')
    if (b'-Dps5.world2612Observer=true\0' in elf) != (candidate in ('266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280')):
        raise ValueError('Unexpected 26.1.2 world observer policy')
    if b'-Dps5.startupObserver=false\0' not in elf:
        raise ValueError('Unexpected startup snapshot policy')
    if b'PS5_UI presentation requestedHz=120' not in elf or b'fpsMilli=' not in elf:raise ValueError('Missing actual presentation/timing path')
    for option in (b'-Dps5.zip.maxOpenFiles=8', b'-Xmx1536m', b'-XX:CompressedClassSpaceSize=64m',
                   b'-XX:ReservedCodeCacheSize=144m',
                   b'-XX:TieredStopAtLevel=4', b'-XX:CICompilerCount=2', b'-XX:+UseZGC',
                   b'-XX:+SafepointTimeout', b'-XX:SafepointTimeoutDelay=250', b'-XX:-AbortVMOnSafepointTimeout'):
        if option + b'\0' not in elf:
            raise ValueError(f'Retained option missing from actual{candidate} ELF: ' + option.decode())
    worker_trial = candidate == '276'
    tuned_workers = candidate in ('275', '276', '278', '279', '280')
    for option, expected in ((b'-XX:ActiveProcessorCount=4', candidate not in ('275', '278', '279', '280')),
                             (b'-XX:ActiveProcessorCount=6', tuned_workers),
                             (b'-Dmax.bg.threads=3', worker_trial),
                             (b'-Dmax.bg.threads=5', tuned_workers),
                             (b'-Djava.util.concurrent.ForkJoinPool.common.parallelism=3', tuned_workers),
                             (b'PS5_CHUNK_TRIAL workers=3 activeProcessors=4', worker_trial),
                             (b'PS5_CHUNK_TRIAL workers=5 activeProcessors=6', worker_trial)):
        if (option + b'\0' in elf) != expected:
            raise ValueError('Unexpected chunk worker option: ' + option.decode())
    if (b'-XX:ZOldGCThreads=1\0' in elf) != (candidate in ('249', '250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280')):
        raise ValueError('Unexpected ZGC old-generation worker policy')
    if (b'PS5_ZINK using Vulkan pipelines for shaders\n' in elf) != (candidate in ('252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280')):
        raise ValueError('Unexpected Zink shader object opt-out policy')
    if (b'PS5_ZINK pipeline shaders with synchronous compilation\0' in elf) != (candidate in ('253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280')):
        raise ValueError('Unexpected Zink synchronous compilation policy')
    if b'-XX:ConcGCThreads=2\0' not in elf:
        raise ValueError('Missing ZGC concurrent worker budget')
    source = (args.build_dir / 'registry/builtin-libraries.cpp').read_text()
    if 'lwjgl333_prospero_ffi_reserve_prime' not in symbols(args.llvm_nm, linked_symbols, external=False):
        raise ValueError('333 callback reserve not linked')
    if b'PS5 LWJGL333 pre-JVM closure reserve result=' not in elf:
        raise ValueError('Pre-JVM reserve priming missing from actual executable')
    if 'std::strcmp(name,"lwjgl333") == 0' not in source:
        raise ValueError('No scoped builtin handle')
    if candidate in ('261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '278', '279', '280'):
        resident_audit = json.loads((args.build_dir / 'registry/builtin-resident-audit.json').read_text())
        expected = ['jnidispatch', 'ps5glfw', 'ps5openal']
        if resident_audit.get('library_scoped_handles') != expected:
            raise ValueError('Missing explicit native lookup ownership')
        for group in expected:
            if f'std::strcmp(name,"{group}") == 0' not in source:
                raise ValueError('Resident JNI handle still exposes process lookup: ' + group)
    # The exact204 main was compiled from the same bootstrap apart from identity.
    boot = (ROOT / 'client/save_headroom/bootstrap.cpp').read_text()
    if '#define' not in boot or '"8"' not in boot:
        raise ValueError('Missing accepted ZIP budget8')
    audit = {'package_sha256': sha(args.package), 'version': args.app_version, 'title_id': 'PPSA99874',
             'package_bytes': args.package.stat().st_size, 'zip_growth_bytes': args.package.stat().st_size - args.baseline_package.stat().st_size,
             'uncompressed_growth_bytes': growth, 'baseline_changed_files': changed, 'removed_logo_assets': sorted(retired_icons), 'added_files': added,
             'matched_native_declarations': counts, 'unsupported_nonplatform_native_declarations': sorted(absent),
             'tinyfd': 'Original 3.4.1 parent JAR and 3.3.3 instance binding match 11 retained adapter JNI declarations',
             'retained_link_input_sha256': retained,
             'native_symbols': '333 definitions prefixed; original lookup keys retained with scoped handle',
             'result': 'PASS scoped package/static ABI audit; no complete feature or console acceptance', 'console': 'NOT TESTED'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2) + '\n')
    print(f'PASS{candidate} package audit; uncompressed growth', growth, 'bytes; SHA256', audit['package_sha256'])


if __name__ == '__main__':
    main()
