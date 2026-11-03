#!/usr/bin/env python3
"""Verify original locked1.21 release inputs; no derivatives or launcher gating.

Downloaded artifacts/assets remain in an explicitly selected ignored research cache.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re

from host_toolchain import ROOT
from prepare_client_261 import (MANIFEST, fetch, verified, allowed, artifact_path)


def validate_metadata(row, data):
    meta = json.loads(data)
    lwjgl = [lib['name'] for lib in meta['libraries'] if lib['name'].startswith('org.lwjgl:') and ':natives-' not in lib['name']]
    if (not re.fullmatch(r'1\.21(?:\.\d{1,2})?', row['id']) or
        meta['id'] != row['id'] or meta['type'] != 'release' or
        type(meta['javaVersion']['majorVersion']) is not int or meta['javaVersion']['majorVersion'] != 21 or
        row['javaMajor'] != 21 or meta['mainClass'] != 'net.minecraft.client.main.Main' or
        meta['assetIndex']['id'] != row['assetIndex'] or meta['downloads']['client'] != row['client'] or
        meta['downloads']['client_mappings'] != row['clientMappings'] or lwjgl != row['lwjgl'] or
        len(lwjgl) != 8 or any(not n.endswith(':3.3.3') for n in lwjgl) or
        meta['libraries'] != row['libraries']):
        raise ValueError('1.21 publisher pins/generation changed; integration review required: ' + row['id'])
    return meta


def prepare(row, cache, *, offline=False, assets=False):
    folder = cache / row['id']
    meta = validate_metadata(row, verified(row['metadata'], folder / 'metadata.json', offline=offline))
    verified(row['client'], folder / 'client.jar', offline=offline)
    verified(row['clientMappings'], folder / 'client-mappings.txt', offline=offline)
    for lib in meta['libraries']:
        name = lib['name']
        if not allowed(lib) or ':natives-' in name or (name.startswith('io.netty:netty-transport-native-') and len(name.split(':')) > 3):
            continue
        pin = lib.get('downloads', {}).get('artifact')
        if pin:
            verified(pin, cache / 'libraries' / artifact_path(pin['path']), offline=offline)
    index = meta['assetIndex']
    data = verified(index, cache / 'assets/indexes' / (index['id'] + '.json'), offline=offline)
    if assets:
        pins = {}
        for obj in json.loads(data)['objects'].values():
            sha = obj['hash']
            if not re.fullmatch('[a-f0-9]{40}', sha):
                raise ValueError('Invalid asset object hash')
            pins[sha] = {'url': 'https://resources.download.minecraft.net/' + sha[:2] + '/' + sha,
                         'sha1': sha, 'size': obj['size']}
        def one(item):
            sha, pin = item
            verified(pin, cache / 'assets/objects' / sha[:2] / sha, offline=offline)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(one, pins.items()))
    print('Verified original', row['id'], '(assets ' + ('included' if assets else 'index only') + ')', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--version', action='append')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--assets', action='store_true')
    parser.add_argument('--check-manifest', action='store_true')
    args = parser.parse_args()
    rows = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions']
    if args.check_manifest:
        if args.offline:
            parser.error('--check-manifest requires network')
        found = {v['id']: {'url': v['url'], 'sha1': v['sha1']} for v in json.loads(fetch(MANIFEST))['versions']
                 if v['type'] == 'release' and re.fullmatch(r'1\.21(?:\.\d+)?', v['id'])}
        if found != {r['id']: r['metadata'] for r in rows}:
            raise ValueError('Publisher release inventory changed; review lock before integration')
    selected = set(args.version or [r['id'] for r in rows])
    if selected - {r['id'] for r in rows}:
        parser.error('Unknown release; select an exact locked id')
    for row in rows:
        if row['id'] in selected:
            prepare(row, args.cache_dir.resolve(), offline=args.offline, assets=args.assets)


if __name__ == '__main__':
    main()
