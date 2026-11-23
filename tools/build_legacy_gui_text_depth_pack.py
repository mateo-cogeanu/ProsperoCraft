#!/usr/bin/env python3
"""Build an opt-in GUI text depth trial using local Minecraft 1.21.x shaders."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

STOCK_SHADER_SHA256 = '43c638c9fe9654e9cb0114619d6e895f42b07724e4a216b8a04d022808de814a'
SHADERS = ('rendertype_text', 'rendertype_text_intensity')
POSITION = '    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);'
TRIAL = """    vec3 textPosition = Position;
    // Match the 1.21/1.21.1 GUI projection and the base font foreground.
    bool baseGuiForeground = ProjMat[3][3] == 1.0
        && abs(ProjMat[2][2] + 0.0001) < 0.0000001
        && abs(ModelViewMat[3].z + 11000.0) < 0.01
        && abs(Position.z - 0.03) < 0.001;
    if (baseGuiForeground) {
        textPosition.z = 0.25;
    }
    gl_Position = ProjMat * ModelViewMat * vec4(textPosition, 1.0);"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('client_jar', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()

    files = {'pack.mcmeta': json.dumps({'pack': {
        'pack_format': 34,
        'description': 'ProsperoCraft GUI text depth trial for 1.21 and 1.21.1',
    }}) + '\n'}
    with ZipFile(args.client_jar) as client:
        version = json.loads(client.read('version.json'))['id']
        if version not in ('1.21', '1.21.1'):
            parser.error(f'Expected Minecraft 1.21 or 1.21.1, found {version}')
        for shader in SHADERS:
            path = f'assets/minecraft/shaders/core/{shader}.vsh'
            original = client.read(path)
            if hashlib.sha256(original).hexdigest() != STOCK_SHADER_SHA256:
                raise ValueError(f'Unexpected stock shader: {path}')
            text = original.decode()
            if text.count(POSITION) != 1:
                raise ValueError(f'Expected one position calculation: {path}')
            files[path] = text.replace(POSITION, TRIAL)

    with ZipFile(args.output, 'x') as pack:
        for name, contents in files.items():
            pack.writestr(ZipInfo(name), contents, compress_type=ZIP_DEFLATED)


if __name__ == '__main__':
    main()
