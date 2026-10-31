"""Portable host-test discovery. Importing this module performs no I/O or parsing."""
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def executable(name, *, override=None, env=None):
    """Explicit path > named environment override > LLVM_HOME > PATH > Homebrew."""
    selected = override or (os.environ.get(env) if env else None)
    if selected:
        found = shutil.which(str(selected))
        if not found:
            raise RuntimeError(f'{env or name} selects unavailable executable: {selected}')
        return found
    candidates = []
    if os.environ.get('LLVM_HOME'):
        candidates.append(Path(os.environ['LLVM_HOME']) / 'bin' / name)
    found = shutil.which(name)
    if found:
        candidates.append(Path(found))
    if os.environ.get('HOMEBREW_PREFIX'):
        prefix = Path(os.environ['HOMEBREW_PREFIX'])
        candidates.extend([prefix / 'opt/llvm/bin' / name, prefix / 'bin' / name])
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError(f'Missing {name}; install it on PATH or set {env or "LLVM_HOME"}.')


def java_home(override=None):
    """Explicit home > JAVA_HOME > javac on PATH; require a complete JDK 25."""
    selected = override or os.environ.get('JAVA_HOME')
    if selected:
        home = Path(selected).expanduser().resolve()
    else:
        found = shutil.which('javac')
        if not found:
            raise RuntimeError('Missing javac; install JDK 25 on PATH or set JAVA_HOME.')
        javac = Path(found).resolve()
        home = javac.parent.parent
        # Apple's /usr/bin/javac is a launcher, not a JDK installation.
        if platform.system() == 'Darwin' and javac == Path('/usr/bin/javac'):
            home = Path(subprocess.check_output(
                ['/usr/libexec/java_home', '-v', '25'], text=True).strip())
    for name in ('java', 'javac', 'keytool'):
        if not (home / 'bin' / name).is_file():
            raise RuntimeError(f'Incomplete JDK: {home}; missing bin/{name}. Set JAVA_HOME to JDK 25.')
    for name in ('java', 'javac'):
        result = subprocess.run([str(home / 'bin' / name), '-version'],
                                capture_output=True, text=True, check=True)
        version = result.stdout + result.stderr
        match = re.search(r'(?:version\s+"|javac\s+)(\d+)', version)
        if not match or int(match[1]) != 25:
            raise RuntimeError(f'Host tests require JDK 25; {name}: {version.strip()} ({home})')
    return home


def jni_flags(home):
    system = platform.system()
    if system not in ('Darwin', 'Linux'):
        raise RuntimeError(f'JNI host tests support macOS/Linux, got {system}')
    includes = [Path(home) / 'include', Path(home) / 'include' / ('darwin' if system == 'Darwin' else 'linux')]
    for directory, header in zip(includes, ('jni.h', 'jni_md.h')):
        if not (directory / header).is_file():
            raise RuntimeError(f'Missing JNI header: {directory / header}')
    return ['-I' + str(p) for p in includes]


def shared_flags():
    return ['-dynamiclib'] if platform.system() == 'Darwin' else ['-shared', '-fPIC', '-D_GNU_SOURCE']


def library_name(name):
    return 'lib' + name + ('.dylib' if platform.system() == 'Darwin' else '.so')


def dependency(name):
    """Never download implicitly or consult a game/private cache."""
    pins = json.loads((ROOT / 'tests/host-dependencies.json').read_text())
    row = pins[name]
    cache = Path(os.environ.get('PROSPERO_HOST_DEPS', ROOT / '.tools/host-tests')).expanduser().resolve()
    path = cache / row['file']
    if not path.is_file():
        raise RuntimeError(f'Missing host dependency {path}; run python3 {ROOT / "tools/run_host_tests.py"} --fetch-deps')
    data = path.read_bytes()
    if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
        raise RuntimeError(f'Host dependency checksum/size mismatch: {path}; remove it and fetch again.')
    return path


def launcher_classpath():
    return str(dependency('gson'))
