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
from verify_client_120 import validate_metadata
from build_lwjgl333 import sha


def prepare(cache, output, binding, *, offline=False):
    row = json.loads((ROOT / 'client/1.20.lock.json').read_text())['versions'][0]
    if row['id'] != '1.20' or row['javaMajor'] != 17:
        raise ValueError('Reviewed original1.20/Java17 inputs required')
    metadata = validate_metadata(row, verified(row['metadata'], cache / '1.20.json', offline=offline))
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
    return {p.name: sha(p) for p in sorted(output.glob('*.jar'))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('runtime-workspace', 'llvm-home', 'lld', 'java-home', 'cache-dir',
                 'lwjgl331-build', 'ffi-core', 'image-dir', 'work-dir'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--offline', action='store_true')
    p.add_argument('--prepare-only', action='store_true')
    a = p.parse_args()
    jdk = java_home(a.java_home, required_major=17)
    work = a.work_dir.resolve()
    if work.exists():
        raise FileExistsError('Preserve existing candidate work; select a fresh directory')
    work.mkdir(parents=True)
    inputs = prepare(a.cache_dir.resolve(), work / 'publisher', a.lwjgl331_build.resolve(), offline=a.offline)
    (work / 'publisher-audit.json').write_text(json.dumps({'gameJarModified':False,
        'scope':'Local-only original1.20 entry/331 JNI; no rendering or world acceptance',
        'filesSha256':inputs}, indent=2) + '\n')
    if a.prepare_only:
        return
    runtime = a.runtime_workspace.resolve()
    sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
    fault = work / 'startup-fault.o'
    subprocess.run([str(a.llvm_home.resolve() / 'bin/clang'), '-target','x86_64-sie-ps5',
        '-std=c11','-O2','-fPIC','-femulated-tls','-fno-stack-protector',
        '-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk / 'target/include'),
        '-DPS5_SHADERC_MAX_REPORTS=16',
        '-DPS5_SHADERC_FAULT_LOG="/download0/mc120-java17-fault.log"',
        '-c',str(ROOT / 'client/ports/shaderc/fault.c'),'-o',str(fault)], check=True)
    subprocess.run([sys.executable, str(runtime / 'tools/package_java_lts_probe.py'),
        '--major','17','--probe-dir',str(ROOT / 'client/java17_bootstrap'),
        '--extra-assets',str(work / 'publisher'),'--management',
        '--library','lwjgl331=' + str(a.lwjgl331_build.resolve() / 'ps5/lwjgl331.o'),
        '--link-object',str(a.ffi_core.resolve()),'--link-object',str(fault),'--llvm-home',str(a.llvm_home.resolve()),
        '--lld',str(a.lld.absolute()),'--boot-jdk',str(jdk),'--image-dir',str(a.image_dir.resolve()),
        '--work-dir',str(work / 'package')], check=True)


if __name__ == '__main__':
    main()
