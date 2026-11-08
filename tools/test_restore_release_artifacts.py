#!/usr/bin/env python3
"""Offline actual-file recovery controls; no release/game downloads."""
import hashlib
import io
from pathlib import Path
import tempfile

from restore_release_artifacts import restore


def rejects(action, error=ValueError):
    try:
        action()
    except error:
        return
    raise AssertionError('Invalid recovery accepted')


def main():
    data = b'exact original release fixture'
    row = {'path': 'dist/releases/fixture/PPSA99874.zip', 'size': len(data),
           'sha256': hashlib.sha256(data).hexdigest(),
           'url': 'https://github.com/mateo-cogeanu/ProsperoCraft/releases/download/fixture/PPSA99874.zip'}
    with tempfile.TemporaryDirectory(prefix='prospero-recovery-') as folder:
        root = Path(folder)
        target = root / row['path']
        for body in (b'truncated', b'x' * len(data), data + b'too large'):
            rejects(lambda: restore(root, row, transport=lambda url: io.BytesIO(body)))
            assert not target.exists() and not list(target.parent.glob('*.part'))
        assert restore(root, row, transport=lambda url: io.BytesIO(data)) == 'Restored and verified'
        assert target.read_bytes() == data
        def no_network(url):
            raise AssertionError('Healthy existing file caused network request')
        assert restore(root, row, transport=no_network) == 'Already verified'
        target.write_bytes(b'different existing bytes')
        rejects(lambda: restore(root, row, transport=no_network), FileExistsError)
        assert target.read_bytes() == b'different existing bytes'
        for path in ('../outside', 'dist/../../outside', '/dist/outside', 'dist\\escape', 'docs/outside'):
            rejects(lambda: restore(root, {**row, 'path': path}, transport=no_network))
        rejects(lambda: restore(root, {**row, 'size': True}, transport=no_network))
        rejects(lambda: restore(root, {**row, 'url': 'https://example.com/file'}, transport=no_network))
        target.unlink()
        external = root / 'private'
        external.mkdir()
        target.parent.rmdir()
        target.parent.symlink_to(external, target_is_directory=True)
        rejects(lambda: restore(root, row, transport=no_network))
        assert not list(external.iterdir())
    print('PASS exact recovery/idempotence, existing-file preservation, truncation/corruption/oversize cleanup, path/symlink/URL refusal; offline')


if __name__ == '__main__':
    main()
