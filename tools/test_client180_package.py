#!/usr/bin/env python3
"""Independent local stage-1 package/symbol/source audit; never a PS5 pass."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from host_toolchain import ROOT


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-workspace',type=Path,required=True)
    parser.add_argument('--package-dir',type=Path,default=ROOT / 'dist/candidates/zink-context-180')
    parser.add_argument('--llvm-home',type=Path,required=True)
    args=parser.parse_args();directory=args.package_dir.resolve()
    record=json.loads((directory / 'build-audit.json').read_text())
    package=directory / 'PPSA99874.zip'
    assert sha(package)==record['package_sha256']
    assert record['app_version']=='01.000.180' and record['console']=='NOT TESTED'
    assert record['scope'].startswith('Native console stage1 only')
    with zipfile.ZipFile(package) as archive:
        names=archive.namelist()
        assert names and all(name.startswith('PPSA99874/') and '..' not in Path(name).parts for name in names)
        assert all(not name.lower().endswith(('.jar','.so','.elf')) and '/objects/' not in name for name in names)
        param=json.loads(archive.read('PPSA99874/sce_sys/param.json'))
        assert param==json.loads((ROOT / 'client/zink_probe/param.json').read_text())
        embedded=json.loads(archive.read('PPSA99874/assets/zink-audit.json'))
        for key in embedded:assert embedded[key]==record[key],key
        assert embedded['mesa']['commit']==json.loads((ROOT / 'client/graphics/sources.json').read_text())['mesa']['commit']
        for name,expected in embedded['patches'].items():assert sha(ROOT / 'client/ports/zink' / name)==expected
        for name,expected in embedded['wsi_patches'].items():assert sha(ROOT / 'client/ports/mesa' / name)==expected
        for name,expected in embedded['consumer_sources_sha256'].items():assert sha(ROOT / name)==expected
        for name,expected in embedded['frontend_sources_sha256'].items():assert sha(ROOT / 'client/ports/zink' / name)==expected
        for required in ('Mesa-Zink-MIT.txt','ProsperoCraft-GPL-3.0-or-later.txt','UPSTREAM-NOTICES.txt','SOURCES.txt'):
            assert 'PPSA99874/licenses/'+required in names
        assert b'/zink/' in archive.read('PPSA99874/licenses/UPSTREAM-NOTICES.txt')
        for name in ('eboot.bin','sce_module/libc.prx'):
            built=ROOT / 'build/zink-probe-180/PPSA99874' / name
            assert hashlib.sha256(archive.read('PPSA99874/'+name)).hexdigest()==sha(built)
    symbols=directory / 'zink-context180-symbols.elf'
    assert sha(symbols)==record['symbols_elf_sha256']
    nm=args.llvm_home.resolve() / 'bin/llvm-nm'
    defined=subprocess.check_output([str(nm),'--defined-only',str(symbols)],text=True)
    exports=[line.split()[-1]for line in defined.splitlines()if len(line.split())>=3]
    for name in record['single_copy_exports']:assert exports.count(name)==1,name
    assert not any(name.startswith(('Java_','SDL_','alcOpenDevice'))for name in exports)
    assert 'ps5zink_create' in exports and 'ps5zink_destroy' in exports
    assert b'No Zink run initialized' in symbols.read_bytes() and b'zink-%s-%lld-%ld' in symbols.read_bytes()
    converter=args.runtime_workspace.resolve() / 'build/native/host/ps5-native-tool'
    for name in ('eboot.bin','sce_module/libc.prx'):
        path=ROOT / 'build/zink-probe-180/PPSA99874' / name
        subprocess.run([str(converter),'self','--inspect','--file',str(path)],check=True,stdout=subprocess.DEVNULL)
    print('PASS exact native180ZIP/digest/identity/notices/pins/one-copy RADV+Mesa exports/run identity; no game/JNI/SDL/audio payload; signatures inspect successfully. Console pending.')


if __name__=='__main__':main()
