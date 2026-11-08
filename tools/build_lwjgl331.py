#!/usr/bin/env python3
"""Build the isolated, genuine LWJGL 3.3.1 group for original Vanilla 1.20."""
import argparse
import json
from pathlib import Path

from host_toolchain import ROOT, java_home
from build_lwjgl333 import build_java, build_native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publisher-cache', required=True, type=Path)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.tools/lwjgl331')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/lwjgl331')
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--runtime-workspace', type=Path)
    parser.add_argument('--ffi-include', type=Path)
    parser.add_argument('--ffi-library', type=Path)
    parser.add_argument('--cc')
    parser.add_argument('--lld')
    parser.add_argument('--part', choices=('java', 'native', 'all'), default='all')
    parser.add_argument('--host', action='store_true')
    parser.add_argument('--closure-reserve-count', type=int, choices=(64, 512), default=512)
    parser.add_argument('--fetch-deps', action='store_true')
    args = parser.parse_args()
    port = ROOT / 'client/ports/lwjgl331'
    pin = json.loads((port / 'sources.json').read_text())
    row = json.loads((ROOT / 'client/1.20.lock.json').read_text())['versions'][0]
    if (row['id'] != '1.20' or pin['version'] != '3.3.1' or
            pin['residentGroup'] != 'lwjgl331' or len(row['lwjgl']) != 7 or
            any(not name.endswith(':3.3.1') for name in row['lwjgl'])):
        raise ValueError('Unexpected 1.20 binding generation')
    cache, work = args.cache_dir.resolve(), args.output_dir.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    jdk = java_home(args.java_home)
    if args.part in ('java', 'all'):
        build_java(args, pin, jdk, cache, work, port=port, publisher_row=row)
    if args.part in ('native', 'all'):
        if args.ffi_include is None:
            parser.error('--ffi-include is required for native building')
        build_native(args, pin, jdk, cache, work, port=port)


if __name__ == '__main__':
    main()
