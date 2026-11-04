#!/usr/bin/env python3
"""Export retained212 link inputs and matching source; never rebuild the app."""
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
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runtime, output = args.runtime_workspace.resolve(), args.output.resolve()
    work = ROOT / 'build/client121-212'
    candidate = ROOT / 'dist/candidates/client121-212-final'
    audit = json.loads((candidate / 'build-audit.json').read_text())
    assert audit['source_tree'] == 'clean' and audit['app_version'] == '01.000.212'
    assert sha(candidate / 'PPSA99874.zip') == audit['package_sha256']
    baseline = ROOT / 'dist/releases/client204/client204-openal-source-relink.zip'
    assert sha(baseline) == audit['baseline_relink_sha256']
    kit = output / 'relink-kit'
    if kit.exists():
        raise FileExistsError('Preserve previous export; choose a fresh directory')
    kit.mkdir(parents=True)
    with zipfile.ZipFile(baseline) as archive:
        if archive.testzip():
            raise ValueError('Baseline kit CRC failure')
        for item in archive.infolist():
            if Path(item.filename).is_absolute() or '..' in Path(item.filename).parts:
                raise ValueError('Unsafe archive path')
        archive.extractall(kit)
    manifest = json.loads((kit / 'manifest.json').read_text())
    files = manifest['files']
    for row in files:
        assert sha(kit / row['path']) == row['sha256'], row['path']
    known = {(row['sha256'], Path(row['path']).name.split('-', 1)[1]): row['path'] for row in files}
    baseline_inputs = (work / 'baseline204').resolve()

    def keep(path):
        path = path.resolve()
        digest = sha(path)
        if path.is_relative_to(baseline_inputs):
            relative = path.relative_to(baseline_inputs).as_posix()
            assert sha(kit / relative) == digest
            return relative
        key = (digest, path.name)
        if key not in known:
            name = f'inputs/{len(files):03d}-{path.name}'
            shutil.copyfile(path, kit / name)
            files.append({'path': name, 'sha256': digest, 'bytes': path.stat().st_size})
            known[key] = name
        return known[key]

    link = []
    for token in map(json.loads, (work / 'link212.rsp').read_text().splitlines()):
        if token.startswith('-L'):
            link.append('-L{LIBRARY_DIR}')
        elif token == str(work / 'client121-212-symbols.elf'):
            link.append('{OUTPUT}')
        elif Path(token).is_absolute():
            link.append(keep(Path(token)))
        else:
            link.append(token)
    assert manifest['openal_group'] in link and '{OUTPUT}' in link
    assert sha(work / 'client121-212-symbols.elf') == audit['symbols_sha256']
    manifest.update(app_version=audit['app_version'], tested_source_commit=audit['source_commit'],
                    original_elf_sha256=audit['symbols_sha256'], arguments=link)
    (kit / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    shutil.rmtree(kit / 'consumer-source')
    consumer = kit / 'consumer-source'
    consumer.mkdir()
    data = subprocess.check_output(['git', '-C', str(ROOT), 'archive', audit['source_commit']])
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(consumer, filter='data')
    pin = audit['presentationRuntime']
    current = kit / 'runtime-source/presentation212'
    current.mkdir(parents=True)
    checkout = runtime / '.tools/github-publish/ps5-java25-homebrew'
    data = subprocess.check_output(['git', '-C', str(checkout), 'archive', pin['commit']])
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(current, filter='data')
    for name, digest in pin['source_sha256'].items():
        assert sha(current / 'Development' / name) == digest
    (kit / 'SOURCE-PROVENANCE.json').write_text(json.dumps({
        'consumer_repository': 'https://github.com/mateo-cogeanu/ProsperoCraft',
        'consumer_commit': audit['source_commit'],
        'runtime_repository': pin['repository'], 'runtime_commit': pin['commit'],
        'runtime_source_path': 'runtime-source/presentation212/Development',
        'inherited_openal_kit_sha256': audit['baseline_relink_sha256'],
        'scope': 'Exact212 consumer source and presentation runtime; inherited runtime/OpenAL source, replacement helper and notices retained. No official game/mod JARs or asset objects.'
    }, indent=2) + '\n')
    (kit / 'README-212.txt').write_text(
        'Exact ProsperoCraft01.000.212 corresponding source and native relink inputs.\n'
        'README.txt retains the OpenAL replacement procedure and upstream rights.\n'
        'consumer-source is the clean tested212 source; runtime-source/presentation212\n'
        'is its presentation runtime. Older sources remain for inherited native inputs.\n'
        'manifest.json is the actual212 link argument order and hashes.\n'
        'Run python3 relink.py --lld /path/to/ld.lld --output rebuilt.elf\n'
        'Replacement: add --objcopy /path/to/llvm-objcopy\n'
        '--openal-object accepted-startup-openal.o (or a compatible modified build).\n'
        'Modified builds do not inherit physical-console acceptance.\n')
    target = output / 'client212-openal-source-relink.zip'
    if target.exists():
        raise FileExistsError(target)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(kit.rglob('*')):
            if file.is_file():
                archive.write(file, file.relative_to(kit).as_posix())
    print(target, sha(target))


if __name__ == '__main__':
    main()
