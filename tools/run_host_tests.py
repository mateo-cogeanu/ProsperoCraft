#!/usr/bin/env python3
"""Run the explicit, bounded offline host-test lanes; fetch only when requested."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
import hashlib
from host_toolchain import ROOT, dependency, executable, java_home


def fetch_dependencies():
    pins = json.loads((ROOT / 'tests/host-dependencies.json').read_text())
    cache = Path(os.environ.get('PROSPERO_HOST_DEPS', ROOT / '.tools/host-tests')).expanduser().resolve()
    cache.mkdir(parents=True, exist_ok=True)
    for name, row in pins.items():
        if (cache / row['file']).exists():
            dependency(name)  # Corrupt existing inputs must fail, not be silently trusted.
            continue
        with urllib.request.urlopen(row['url'], timeout=45) as response:
            data = response.read(row['size'] + 1)
        if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise RuntimeError(f'Download checksum/size mismatch: {name}')
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as tmp:
            temporary = Path(tmp.name)
            tmp.write(data)
        temporary.replace(cache / row['file'])
        print(f'Verified {name}: {row["sha256"]}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=('fast', 'native'), default='fast')
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--deps-dir', type=Path)
    parser.add_argument('--cc', help='C compiler executable')
    parser.add_argument('--cxx', help='C++ compiler executable')
    parser.add_argument('--fetch-deps', action='store_true', help='Provision the two pinned small host libraries, then run')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise RuntimeError('Host assertions require Python without -O/PYTHONOPTIMIZE.')
    if args.deps_dir:
        os.environ['PROSPERO_HOST_DEPS'] = str(args.deps_dir.resolve())
    home = java_home(args.java_home)
    os.environ['JAVA_HOME'] = str(home)
    if args.fetch_deps:
        fetch_dependencies()
    for name in ('gson', 'fabric-loader'):
        dependency(name)
    if args.lane == 'native':
        os.environ['CC'] = executable('clang', override=args.cc, env='CC')
        os.environ['CXX'] = executable('clang++', override=args.cxx, env='CXX')
    tests = json.loads((ROOT / 'tests/host-lanes.json').read_text())[args.lane]
    if not tests:
        raise RuntimeError('Empty host test lane')
    print(f'JDK: {home}; lane: {args.lane}; {len(tests)} required checks', flush=True)
    start = time.monotonic()
    for test in tests:
        print(f'\n>>> {test}', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'tools' / test)], cwd=ROOT,
                       check=True, timeout=180)
    print(f'PASS {len(tests)} checks in {time.monotonic() - start:.1f}s', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.SubprocessError, OSError) as error:
        print(f'Host checks FAILED: {error}', file=sys.stderr)
        sys.exit(1)
