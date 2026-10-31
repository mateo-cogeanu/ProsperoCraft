"""Shared package mechanics; specialized native/auth/relink assertions stay mandatory."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
from app_identity import ROOT, RESOURCE, current_identity, java_resource


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate manifest key: ' + key)
        result[key] = value
    return result


def load_legacy_manifest(path):
    data = json.loads(Path(path).read_text(), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or set(data) != {'schema', 'kind', 'builds'}:
        raise ValueError('Missing or unknown audit manifest fields')
    if type(data['schema']) is not int or data['schema'] != 1 or data['kind'] != 'legacy-staging':
        raise ValueError('Unsupported audit manifest schema/kind')
    builds = data['builds']
    if not isinstance(builds, list) or not builds or any(type(b) is not int or not 122 <= b <= 150 for b in builds):
        raise ValueError('Invalid legacy build profile')
    if builds != sorted(set(builds)):
        raise ValueError('Duplicate or unordered profiles')
    return data


@contextmanager
def checked_zip(path, expected_sha256=None):
    path = Path(path)
    if expected_sha256 is not None:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
            raise ValueError('Package SHA-256 mismatch')
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate package members')
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name:
                raise ValueError('Unsafe package member: ' + name)
        if package.testzip() is not None:
            raise ValueError('Package CRC failure')
        yield package


def audit_current_identity(package, root=ROOT):
    import io
    identity = current_identity(root)
    prefix = identity['title_id'] + '/'
    with checked_zip(package) as archive:
        param = json.loads(archive.read(prefix + 'sce_sys/param.json'), object_pairs_hook=unique_object)
        if (param['contentVersion'], param['titleId']) != (identity['app_version'], identity['title_id']):
            raise ValueError('Package identity differs from current metadata')
        with zipfile.ZipFile(io.BytesIO(archive.read(prefix + 'assets/java25/client-probe.jar'))) as java:
            if java.namelist().count(RESOURCE) != 1 or java.read(RESOURCE) != java_resource(identity):
                raise ValueError('Java/native package identity mismatch')
        if archive.read(prefix + 'assets/java25/classes/' + RESOURCE) != java_resource(identity):
            raise ValueError('Exploded Java identity mismatch')
        if ('Minecraft Original Client Startup ' + identity['app_version']).encode() not in archive.read(prefix + 'eboot.bin'):
            raise ValueError('Native identity marker missing')
    return identity


def run_legacy(number):
    if __debug__ is False:
        raise RuntimeError('Audit assertions require Python without optimization')
    manifest = load_legacy_manifest(ROOT / 'tests/audits/legacy-builds.json')
    if type(number) is not int or number not in manifest['builds']:
        raise ValueError('Unknown legacy build')
    from legacy_package_audit import audit_legacy
    audit_legacy(number)
