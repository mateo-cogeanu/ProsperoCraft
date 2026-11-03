#!/usr/bin/env python3
"""Deterministic121 inventory/generation/hash failures; no publisher downloads."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile

from host_toolchain import ROOT
from prepare_client_121 import validate_metadata
from prepare_client_261 import verified


def reject(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('Invalid121 input accepted')


def main():
    rows = json.loads((ROOT / 'client/1.21.lock.json').read_text())['versions']
    assert [r['id'] for r in rows] == ['1.21', *['1.21.' + str(i) for i in range(1, 12)]]
    for row in rows:
        meta = {'id': row['id'], 'type': 'release', 'javaVersion': {'majorVersion': 21},
                'mainClass': 'net.minecraft.client.main.Main', 'assetIndex': {'id': row['assetIndex']},
                'downloads': {'client': row['client'], 'client_mappings': row['clientMappings']},
                'libraries': row['libraries']}
        validate_metadata(row, json.dumps(meta))
        for field, value in (('id', '1.21-pre1'), ('type', 'snapshot'), ('mainClass', 'FakeMain'),
                             ('javaVersion', {'majorVersion': 25}), ('javaVersion', {'majorVersion': True})):
            bad = {**meta, field: value}
            reject(lambda: validate_metadata(row, json.dumps(bad)))
        changed = copy.deepcopy(meta)
        next(lib for lib in changed['libraries'] if lib['name'].startswith('org.lwjgl:lwjgl:'))['name'] = 'org.lwjgl:lwjgl:3.4.3'
        reject(lambda: validate_metadata(row, json.dumps(changed)))
        reject(lambda: validate_metadata({**row, 'id': '1.20.6'}, json.dumps(meta)))
        reject(lambda: validate_metadata({**row, 'id': '1.21.100'}, json.dumps(meta)))
        assert row['javaMajor'] == 21 and row['window'] == 'GLFW' and row['renderer'] == 'ZINK'
        assert row['ps5DownloadedNativeClassifiers'] == []
    with tempfile.TemporaryDirectory(prefix='121-pins-') as folder:
        path = Path(folder) / 'original.jar'
        data = b'publisher-original-fixture'
        pin = {'url': 'https://piston-data.mojang.com/fixture', 'size': len(data),
               'sha1': hashlib.sha1(data).hexdigest()}
        verified(pin, path, transport=lambda url: data)
        assert path.read_bytes() == data
        reject(lambda: verified({**pin, 'sha1': '0' * 40}, path, offline=True))
        reject(lambda: verified({**pin, 'size': len(data) + 1}, path, offline=True))
        assert path.read_bytes() == data
    print('PASS exact12release inventory; Java21/Main/generation/native/download pins and negative controls; no network/game execution')


if __name__ == '__main__':
    main()
