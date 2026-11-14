#!/usr/bin/env python3
"""Build the PS5 companion mod against pinned publisher and Fabric inputs."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

from host_toolchain import ROOT, java_home

SOURCE = ROOT / 'client/ports/controlify263-keyboard'
MOD = 'prosperocraft-controlify-keyboard.jar'
CONTROLIFY = 'bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a'
MIXIN = '03f0065023bfc3045d71bfb99872451d9ad5a0800a5a0dac34ab8c7d5c134f5d'
MINECRAFT = '4508d006323f24fa02876310c192d739af56516eb259000ac50f0909a68c9a2d'


def source_files():
    return sorted(path for path in SOURCE.rglob('*') if path.is_file())


def build(jdk, controlify, mixin, minecraft, output):
    for path, expected in ((controlify, CONTROLIFY), (mixin, MIXIN), (minecraft, MINECRAFT)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Incorrect pinned input: {path.name}')
    files = source_files()
    with tempfile.TemporaryDirectory(prefix='prospero-controlify-') as directory:
        classes = Path(directory)
        subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-proc:none',
                        '-cp', os.pathsep.join(map(str, (controlify, mixin, minecraft))),
                        '-d', str(classes), *(str(path) for path in files if path.suffix == '.java')],
                       check=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as jar:
            for path in sorted(classes.rglob('*.class')):
                jar.writestr(zipfile.ZipInfo(path.relative_to(classes).as_posix()), path.read_bytes())
            for path in files:
                if path.suffix == '.json':
                    jar.writestr(zipfile.ZipInfo(path.name), path.read_bytes())
            jar.writestr(zipfile.ZipInfo('LICENSE'), (ROOT / 'LICENSE').read_bytes())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('controlify-jar', 'mixin-jar', 'minecraft-jar', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--java-home', type=Path)
    args = parser.parse_args()
    build(java_home(args.java_home), args.controlify_jar, args.mixin_jar, args.minecraft_jar, args.output)
