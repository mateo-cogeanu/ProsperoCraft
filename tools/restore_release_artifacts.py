#!/usr/bin/env python3
"""Restore explicitly selected, checksum-pinned public release copies to dist."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/validation/dist-recovery-2026-11-08.json'


def validate(row):
    path = row['path']
    parts = PurePosixPath(path).parts
    if (not parts or parts[0] != 'dist' or len(parts) < 2 or
            PurePosixPath(path).is_absolute() or '..' in parts or
            '\\' in path or '\0' in path or ':' in path):
        raise ValueError('Recovery destination must be a relative dist path')
    if (not re.fullmatch('[0-9a-f]{64}', row['sha256']) or
            type(row['size']) is not int or row['size'] < 0 or
            not row['url'].startswith('https://github.com/mateo-cogeanu/ProsperoCraft/releases/download/')):
        raise ValueError('Invalid public release pin')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(256 * 1024):
            digest.update(data)
    return digest.hexdigest()


def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'ProsperoCraft-artifact-recovery'})
    return urllib.request.urlopen(request, timeout=60)


def restore(root, row, *, transport=download):
    validate(row)
    root = root.resolve()
    target = root / row['path']
    if target.is_symlink() or not target.resolve().is_relative_to(root / 'dist'):
        raise ValueError('Recovery destination escapes dist')
    if target.exists():
        if target.is_file() and target.stat().st_size == row['size'] and sha(target) == row['sha256']:
            return 'Already verified'
        raise FileExistsError('Existing different file preserved: ' + row['path'])
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.restore-', suffix='.part', delete=False) as output:
            temporary = Path(output.name)
            total = 0
            with transport(row['url']) as response:
                while data := response.read(256 * 1024):
                    total += len(data)
                    if total > row['size']:
                        raise ValueError('Release download exceeds pinned size')
                    output.write(data)
        if temporary.stat().st_size != row['size'] or sha(temporary) != row['sha256']:
            raise ValueError('Release checksum/size mismatch')
        if target.exists() or target.is_symlink():
            raise FileExistsError('Recovery destination appeared during download')
        os.replace(temporary, target)
        return 'Restored and verified'
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', action='append', help='Exact relative path from the recovery manifest')
    parser.add_argument('--list', action='store_true', help='List recoverable paths without downloading')
    args = parser.parse_args()
    rows = json.loads(MANIFEST.read_text())['files']
    by_path = {row['path']: row for row in rows}
    if len(by_path) != len(rows):
        raise ValueError('Duplicate recovery paths')
    for row in rows:
        validate(row)
    if args.list:
        for path in by_path:
            print(path)
    if not args.list and not args.path:
        parser.error('Select --path or --list; no implicit downloads')
    for path in args.path or []:
        if path not in by_path:
            parser.error('Path has no verified public recovery pin: ' + path)
        print(restore(ROOT, by_path[path]) + ': ' + path)


if __name__ == '__main__':
    main()
