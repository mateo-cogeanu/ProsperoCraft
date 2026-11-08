#!/usr/bin/env python3
"""Offline controls for the three distinct 1.20 publisher generations."""
import copy
import json

from host_toolchain import ROOT
from verify_client_120 import RELEASES, validate_metadata


def rejects(row, meta):
    try:
        validate_metadata(row, json.dumps(meta))
    except ValueError:
        return
    raise AssertionError('Invalid 1.20 metadata accepted')


def main():
    rows = json.loads((ROOT / 'client/1.20.lock.json').read_text())['versions']
    assert tuple(row['id'] for row in rows) == RELEASES
    for row in rows:
        meta = {'id': row['id'], 'type': 'release', 'mainClass': row['mainClass'],
                'javaVersion': {'majorVersion': row['javaMajor']},
                'assetIndex': {'id': row['assetIndex']}, 'libraries': row['libraries'],
                'downloads': {'client': row['client'], 'client_mappings': row['clientMappings']}}
        validate_metadata(row, json.dumps(meta))
        for field, value in (('id', '1.20-pre1'), ('type', 'snapshot'),
                             ('mainClass', 'FakeMain'), ('assetIndex', {'id': 'wrong'}),
                             ('javaVersion', {'majorVersion': 25}),
                             ('javaVersion', {'majorVersion': True})):
            rejects(row, {**meta, field: value})
        rejects({**row, 'id': '1.20.7'}, meta)
        rejects({**row, 'javaMajor': True}, meta)
        changed = copy.deepcopy(meta)
        changed['downloads']['client']['sha1'] = '0' * 40
        rejects(row, changed)
        # Even a matching modified lock must not admit a different native generation.
        changed = copy.deepcopy(meta)
        lib = next(lib for lib in changed['libraries'] if lib['name'].startswith('org.lwjgl:lwjgl:'))
        lib['name'] = 'org.lwjgl:lwjgl:3.4.3'
        binding = [lib['name'] for lib in changed['libraries']
                   if lib['name'].startswith('org.lwjgl:') and ':natives-' not in lib['name']]
        rejects({**row, 'libraries': changed['libraries'], 'lwjgl': binding}, changed)
        # A coherent but duplicate binding list must also fail.
        changed['libraries'].append(copy.deepcopy(lib))
        binding.append(lib['name'])
        rejects({**row, 'libraries': changed['libraries'], 'lwjgl': binding}, changed)
    print('PASS seven 1.20 releases; Java17/21 and LWJGL331/332/333 boundaries; corruption controls; offline')


if __name__ == '__main__':
    main()
