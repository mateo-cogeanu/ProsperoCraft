#!/usr/bin/env python3
"""Verify original 1.20.x publisher metadata; does not enable launcher support."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re

from host_toolchain import ROOT
from prepare_client_261 import verified


RELEASES = ('1.20', *(f'1.20.{i}' for i in range(1, 7)))
MODULES = ('lwjgl-glfw', 'lwjgl-jemalloc', 'lwjgl-openal', 'lwjgl-opengl',
           'lwjgl-stb', 'lwjgl-tinyfd', 'lwjgl')


def validate_metadata(row, data):
    version = row['id']
    if version not in RELEASES:
        raise ValueError('Unknown 1.20 release')
    group = RELEASES.index(version)
    java = 17 if group < 5 else 21
    binding = '3.3.1' if group < 2 else '3.3.2' if group < 5 else '3.3.3'
    modules = (*MODULES, 'lwjgl-freetype') if group >= 5 else MODULES
    expected = {f'org.lwjgl:{module}:{binding}' for module in modules}
    meta = json.loads(data)
    libraries = [lib['name'] for lib in meta['libraries']
                 if lib['name'].startswith('org.lwjgl:') and ':natives-' not in lib['name']]
    if (meta['id'] != version or meta['type'] != 'release' or
            type(row['javaMajor']) is not int or row['javaMajor'] != java or
            type(meta['javaVersion']['majorVersion']) is not int or
            meta['javaVersion']['majorVersion'] != java or
            row['mainClass'] != 'net.minecraft.client.main.Main' or
            meta['mainClass'] != row['mainClass'] or
            meta['assetIndex']['id'] != row['assetIndex'] or
            meta['downloads']['client'] != row['client'] or
            meta['downloads']['client_mappings'] != row['clientMappings'] or
            libraries != row['lwjgl'] or len(libraries) != len(expected) or
            set(libraries) != expected or meta['libraries'] != row['libraries']):
        raise ValueError('1.20 publisher generation/pins changed; review required: ' + version)
    return meta


def prepare_assets(metadata, directory, *, offline=False, objects=False):
    """Stage the publisher's index and optionally its original asset objects."""
    index = metadata['assetIndex']
    if not re.fullmatch(r'[0-9]+', index['id']):
        raise ValueError('Invalid 1.20 asset index ID')
    data = verified(index, directory / 'indexes' / (index['id'] + '.json'),
                    offline=offline)
    unique = {}
    for item in json.loads(data)['objects'].values():
        digest, size = item['hash'], item['size']
        if (not re.fullmatch('[0-9a-f]{40}', digest) or type(size) is not int
                or not 0 <= size <= 1024**3 or unique.setdefault(digest, size) != size):
            raise ValueError('Invalid or conflicting 1.20 asset object pin')
    if objects:
        def stage(entry):
            digest, size = entry
            prefix = digest[:2]
            pin = {'url': f'https://resources.download.minecraft.net/{prefix}/{digest}',
                   'sha1': digest, 'size': size}
            verified(pin, directory / 'objects' / prefix / digest, offline=offline)

        with ThreadPoolExecutor(max_workers=8) as pool:
            for _ in pool.map(stage, unique.items()):
                pass
    return len(unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', required=True, type=Path)
    parser.add_argument('--version', choices=RELEASES, action='append')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--assets-dir', type=Path, help='Verify and stage the original asset index')
    parser.add_argument('--asset-objects', action='store_true', help='Also stage all indexed asset objects')
    args = parser.parse_args()
    if args.asset_objects and not args.assets_dir:
        parser.error('--asset-objects requires --assets-dir')
    rows = json.loads((ROOT / 'client/1.20.lock.json').read_text())['versions']
    if tuple(row['id'] for row in rows) != RELEASES:
        raise ValueError('Invalid release inventory/order')
    for row in rows:
        if not args.version or row['id'] in args.version:
            data = verified(row['metadata'], args.cache_dir.resolve() / (row['id'] + '.json'),
                            offline=args.offline)
            metadata = validate_metadata(row, data)
            print('Verified metadata:', row['id'], 'Java', row['javaMajor'], row['lwjgl'][0])
            if args.assets_dir:
                count = prepare_assets(metadata, args.assets_dir.resolve(), offline=args.offline,
                                       objects=args.asset_objects)
                print('Verified asset index:', metadata['assetIndex']['id'], 'unique objects:', count,
                      '(objects staged)' if args.asset_objects else '(index only)')


if __name__ == '__main__':
    main()
