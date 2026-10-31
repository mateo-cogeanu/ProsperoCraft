#!/usr/bin/env python3
"""Prepare hash-verified original 26.1.x research inputs, never game derivatives.

Default: metadata, client, Java dependencies and asset index for each locked
release. Asset objects require --assets. Downloads stay in the selected cache;
no private/game cache discovery, native binaries or launcher policy changes.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'
HOSTS = {'piston-meta.mojang.com', 'piston-data.mojang.com',
         'libraries.minecraft.net', 'resources.download.minecraft.net'}


def publisher_url(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in HOSTS or
            parsed.username is not None or parsed.password is not None or
            parsed.port is not None or parsed.fragment):
        raise ValueError('Untrusted publisher URL')
    return url


def fetch(url):
    publisher_url(url)
    # Publisher inputs must not silently redirect to another origin.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    with urllib.request.build_opener(NoRedirect).open(url, timeout=30) as response:
        return response.read()


def verified(pin, path, *, offline=False, transport=fetch):
    publisher_url(pin['url'])
    if not re.fullmatch('[0-9a-f]{40}', pin['sha1']):
        raise ValueError('Invalid publisher SHA-1')
    if 'size' in pin and (type(pin['size']) is not int or not 0 <= pin['size'] <= 1024**3):
        raise ValueError('Invalid publisher size')
    def check(data):
        if (hashlib.sha1(data).hexdigest() != pin['sha1'] or
                ('size' in pin and len(data) != pin['size'])):
            raise ValueError('Publisher checksum/size mismatch: ' + path.name)
        return data
    if path.exists():
        return check(path.read_bytes())
    if offline:
        raise FileNotFoundError('Missing verified input; run without --offline: ' + str(path))
    data = check(transport(pin['url']))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.part')
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return data


def allowed(library):
    """Apply ordered publisher rules for the PS5 Linux-library Java selection."""
    result = 'rules' not in library
    for rule in library.get('rules', []):
        os_rule = rule.get('os', {})
        matches = ('features' not in rule and os_rule.get('name', 'linux') == 'linux'
                   and os_rule.get('arch', 'x86_64') in ('x86_64', 'amd64')
                   and 'version' not in os_rule)
        if matches:
            result = rule['action'] == 'allow'
    return result


def artifact_path(value):
    path = PurePosixPath(value)
    if (not value or '\\' in value or '\0' in value or path.is_absolute() or
            '..' in path.parts or ':' in value):
        raise ValueError('Unsafe publisher artifact path')
    return Path(*path.parts)


def validate_metadata(row, data):
    meta = json.loads(data)
    lwjgl = [lib['name'] for lib in meta['libraries']
             if lib['name'].startswith('org.lwjgl:') and ':natives-' not in lib['name']]
    if (meta['id'] != row['id'] or meta['type'] != 'release' or
            meta['javaVersion']['majorVersion'] != 25 or row['javaMajor'] != 25 or
            meta['mainClass'] != 'net.minecraft.client.main.Main' or
            meta['assetIndex']['id'] != row['assetIndex'] or
            meta['downloads']['client'] != row['client'] or lwjgl != row['lwjgl'] or
            not any(name.startswith('org.lwjgl:lwjgl-glfw:') for name in lwjgl) or
            any(name.startswith('org.lwjgl:lwjgl-sdl:') for name in lwjgl)):
        raise ValueError('26.1 assumptions/pins changed; stop before integration: ' + row['id'])
    return meta


def prepare(row, cache, *, offline=False, assets=False):
    if not re.fullmatch(r'26\.1(?:\.\d+)?', row['id']):
        raise ValueError('Only locked 26.1.x release IDs are accepted')
    meta = validate_metadata(row, verified(row['metadata'], cache / (row['id'] + '.json'), offline=offline))
    verified(meta['downloads']['client'], cache / (row['id'] + '-client.jar'), offline=offline)
    for library in meta['libraries']:
        name = library['name']
        if (not allowed(library) or ':natives-' in name or
                (name.startswith('io.netty:netty-transport-native-') and len(name.split(':')) > 3)):
            continue
        artifact = library.get('downloads', {}).get('artifact')
        if artifact:
            verified(artifact, cache / 'libraries' / artifact_path(artifact['path']), offline=offline)
    index = meta['assetIndex']
    data = verified(index, cache / ('assets-' + index['id'] + '.json'), offline=offline)
    if assets:
        for obj in json.loads(data)['objects'].values():
            sha = obj['hash']
            if not re.fullmatch('[0-9a-f]{40}', sha):
                raise ValueError('Invalid asset object hash')
            pin = dict(url='https://resources.download.minecraft.net/' + sha[:2] + '/' + sha,
                       sha1=sha, size=obj['size'])
            verified(pin, cache / 'objects' / sha[:2] / sha, offline=offline)
    print('Verified original', row['id'], '(asset objects ' + ('included' if assets else 'not requested') + ')')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'build/261-research')
    parser.add_argument('--version', action='append', help='Locked release ID; default all')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--assets', action='store_true')
    parser.add_argument('--check-manifest', action='store_true', help='Fetch live manifest and reject changed release inventory/pins')
    args = parser.parse_args()
    rows = json.loads((ROOT / 'client/26.1.lock.json').read_text())['versions']
    if args.check_manifest:
        if args.offline:
            parser.error('--check-manifest requires network; remove --offline')
        data = fetch(MANIFEST)
        found = {v['id']: {'url': v['url'], 'sha1': v['sha1']}
                 for v in json.loads(data)['versions']
                 if v['type'] == 'release' and re.fullmatch(r'26\.1(?:\.\d+)?', v['id'])}
        if found != {row['id']: row['metadata'] for row in rows}:
            raise ValueError('26.1 release inventory/pins changed; review draft lock before integration')
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        (args.cache_dir / 'manifest.json').write_bytes(data)
    selected = set(args.version or [row['id'] for row in rows])
    if selected - {row['id'] for row in rows}:
        parser.error('Unknown version; use an exact ID from client/26.1.lock.json')
    for row in rows:
        if row['id'] in selected:
            prepare(row, args.cache_dir.resolve(), offline=args.offline, assets=args.assets)


if __name__ == '__main__':
    main()
