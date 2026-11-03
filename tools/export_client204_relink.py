#!/usr/bin/env python3
"""Export the exact accepted 204 native link with inherited OpenAL source rights.

This exports existing inputs; it never rebuilds or changes the tested app.
Run both relink routes from the exported kit before binary publication.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-workspace', type=Path, required=True)
    parser.add_argument('--baseline-kit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime_workspace.resolve()
    output = args.output.resolve()
    kit = output / 'relink-kit'
    if kit.exists():
        raise FileExistsError('Preserve existing export; select a fresh output directory')
    audit = json.loads((ROOT / 'dist/candidates/save-headroom-204/build-audit.json').read_text())
    assert sha(args.baseline_kit) == audit['baseline179_relink_sha256']
    work = ROOT / 'build/save-headroom204'
    base = ROOT / 'build/client-startup-probe'
    sdk = runtime / '.tools/native-sdk/ps5-payload-sdk'
    kit.mkdir(parents=True)
    with zipfile.ZipFile(args.baseline_kit) as archive:
        archive.extractall(kit)
    manifest = json.loads((kit / 'manifest.json').read_text())
    files = manifest['files']
    for row in files:
        assert sha(kit / row['path']) == row['sha256'], row['path']
    known = {(row['sha256'], Path(row['path']).name.split('-', 1)[1]): row['path'] for row in files}

    def keep(path):
        path = path.resolve()
        digest = sha(path)
        key = (digest, path.name)
        if key in known:
            return known[key]
        name = f'inputs/{len(files):03d}-{path.name}'
        shutil.copyfile(path, kit / name)
        files.append({'path': name, 'sha256': digest, 'bytes': path.stat().st_size})
        known[key] = name
        return name

    # Match package_save_headroom.py and the SDK driver's actual argument order.
    link = ['-L{LIBRARY_DIR}', '-m', 'elf_x86_64', '-pie', '--eh-frame-hdr',
            '-z', 'max-page-size=0x4000', '-mllvm', '-emulated-tls',
            '-T', keep(work / 'gpu-probe.ld'), '--eh-frame-hdr',
            '--version-script', keep(runtime / '.tools/native-app/tooling/native/app-symbols.map'),
            '--version-script', keep(base / 'gpu-abi-local.map'), '-e', '_start', '-o', '{OUTPUT}',
            keep(work / 'main.o')]
    toolkit = json.loads((work / 'launcher-toolkit-audit.json').read_text())
    for name, digest in toolkit['objects_sha256'].items():
        assert sha(work / name) == digest
        link.append(keep(work / name))
    for name in ('renderer.o', 'crt.o', 'cpp_runtime.o', 'native-exception-trace.o', 'native-mutex-trace.o'):
        link.append(keep(base / name))
    for path in [base / 'libSceMouse.so', base / 'libSceAudioIn.so',
                 ROOT / 'build/client-graphics/libSceAgc.so', ROOT / 'build/client-graphics/libSceAgcDriver.so']:
        link.append(keep(path))
    response = [json.loads(line) for line in (work / 'combined-link.rsp').read_text().splitlines()]
    for token in response:
        if token.startswith('-L'):
            continue
        link.append(token if token.startswith('-') else keep(Path(token)))
    assert manifest['openal_group'] in link, 'Inherited OpenAL group differs from exact 204 link'
    link += ['--as-needed', *[keep(path) for path in sorted((sdk / 'target/lib').glob('*.so'))], '--hash-style=gnu']
    manifest.update(app_version=audit['app_version'], tested_source_commit=audit['source_commit'],
                    original_elf_sha256=audit['symbols_elf_sha256'], arguments=link)
    (kit / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    # Replace inherited consumer source with the exact clean build source snapshot.
    shutil.rmtree(kit / 'consumer-source')
    consumer = kit / 'consumer-source'
    consumer.mkdir()
    data = subprocess.check_output(['git', '-C', str(ROOT), 'archive', audit['source_commit']])
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(consumer, filter='data')
    runtime_checkout = runtime / '.tools/github-publish/ps5-java25-homebrew'
    data = subprocess.check_output(['git', '-C', str(runtime_checkout), 'archive', audit['save_headroom']['commit']])
    current = kit / 'runtime-source/current'
    current.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(current, filter='data')
    (kit / 'SOURCE-PROVENANCE.json').write_text(json.dumps({
        'consumer_repository': 'https://github.com/mateo-cogeanu/ProsperoCraft',
        'consumer_commit': audit['source_commit'],
        'runtime_repository': audit['save_headroom']['repository'],
        'runtime_commit': audit['save_headroom']['commit'],
        'inherited_openal_kit_sha256': audit['baseline179_relink_sha256'],
        'scope': 'Exact 204 consumer source and current reusable runtime source; inherited OpenAL source, replacement helper and original notices retained. No official game/mod JARs or asset objects.'
    }, indent=2) + '\n')
    (kit / 'README-204.txt').write_text(
        'Exact accepted ProsperoCraft 01.000.204 corresponding-source/relink export.\n'
        'README.txt documents the inherited OpenAL replacement procedure.\n'
        'consumer-source is the clean exact 204 build commit; runtime-source/current\n'
        'is its current reusable runtime source. Older runtime source is retained\n'
        'for inherited inputs. manifest.json records the exact 204 link.\n'
        'Run python3 relink.py --lld /path/to/ld.lld --output rebuilt.elf\n'
        'For a replacement, add --objcopy /path/to/llvm-objcopy\n'
        '--openal-object accepted-startup-openal.o (or a compatible edited build).\n'
        'Edited/relinked artifacts do not inherit console acceptance.\n')
    target = output / 'client204-openal-source-relink.zip'
    if target.exists():
        raise FileExistsError(target)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(kit.rglob('*')):
            if path.is_file():
                archive.write(path, str(path.relative_to(kit)))
    print(target, sha(target))


if __name__ == '__main__':
    main()
