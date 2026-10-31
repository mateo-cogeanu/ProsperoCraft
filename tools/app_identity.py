"""Current application identity. Probe and historical versions are independent."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = 'prosperocraft-build.properties'


def current_identity(root=ROOT):
    param = json.loads((root / 'client/startup/param.json').read_text())
    version, title = param['contentVersion'], param['titleId']
    if not isinstance(version, str) or not re.fullmatch(r'\d{2}\.\d{3}\.\d{3}', version):
        raise ValueError('Invalid current contentVersion')
    if not isinstance(title, str) or not re.fullmatch(r'PPSA\d{5}', title):
        raise ValueError('Invalid current titleId')
    return {'app_version': version, 'title_id': title}


def java_resource(identity):
    return ''.join(f'{key}={identity[key]}\n' for key in ('app_version', 'title_id')).encode('ascii')


def write_probe_jar(output, classes, *, identity=None, channel=None, offline_key=None):
    """Package the actual compiled classes and reproducible identity together."""
    import zipfile
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(classes.rglob('*.class')):
            info = zipfile.ZipInfo(path.relative_to(classes).as_posix())
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        if identity is not None:
            content = java_resource(identity)
            info = zipfile.ZipInfo(RESOURCE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
            (classes / RESOURCE).write_bytes(content)
        for name, content in [('prosperocraft-channel.txt', None if channel is None else channel+'\n'), ('offline-import-public-key.der', offline_key)]:
            if content is not None:
                info = zipfile.ZipInfo(name)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, content)


def build_status(package, root=ROOT):
    """Successful compilation is distinct from physical-console acceptance."""
    import hashlib
    import subprocess
    commit = None
    state = 'unavailable'
    if (root / '.git').exists():
        commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        state = 'modified' if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip() else 'clean'
    return {**current_identity(root), 'source_commit': commit, 'source_tree': state,
            'compilation': 'passed', 'console': 'pending',
            'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest()}
