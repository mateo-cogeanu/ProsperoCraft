#!/usr/bin/env python3
"""Independent local stage-2a package/symbol/source audit; never a PS5 pass."""
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
    parser.add_argument('--package-dir',type=Path,default=ROOT / 'dist/candidates/zink-present-183')
    parser.add_argument('--llvm-home',type=Path,required=True)
    args=parser.parse_args();directory=args.package_dir.resolve()
    record=json.loads((directory / 'build-audit.json').read_text())
    package=directory / 'PPSA99874.zip'
    assert sha(package)==record['package_sha256']
    assert record['app_version']=='01.000.183' and record['console']=='NOT TESTED'
    assert record['scope'].startswith('Native console stage2a only')
    with zipfile.ZipFile(package) as archive:
        names=archive.namelist()
        assert names and all(name.startswith('PPSA99874/') and '..' not in Path(name).parts for name in names)
        assert all(not name.lower().endswith(('.jar','.so','.elf')) and '/objects/' not in name for name in names)
        param=json.loads(archive.read('PPSA99874/sce_sys/param.json'))
        expected_param=json.loads((ROOT / 'client/zink_present_fix/param.json').read_text())
        branding=json.loads((ROOT / 'assets/branding/branding.json').read_text())
        for localized in expected_param['localizedParameters'].values():
            if isinstance(localized,dict) and 'titleName' in localized:localized['titleName']=branding['name']
        assert param==expected_param
        embedded=json.loads(archive.read('PPSA99874/assets/zink-audit.json'))
        for key in embedded:assert embedded[key]==record[key],key
        assert embedded['mesa']['commit']==json.loads((ROOT / 'client/graphics/sources.json').read_text())['mesa']['commit']
        for name,expected in embedded['patches'].items():assert sha(ROOT / 'client/ports/zink' / name)==expected
        for name,expected in embedded['wsi_patches'].items():assert sha(ROOT / 'client/ports/mesa' / name)==expected
        for name,expected in embedded['consumer_sources_sha256'].items():assert sha(ROOT / name)==expected
        for name,expected in embedded['frontend_sources_sha256'].items():assert sha(ROOT / 'client/ports/zink' / name)==expected
        for required in ('Mesa-Zink-MIT.txt','ProsperoCraft-GPL-3.0-or-later.txt','UPSTREAM-NOTICES.txt','SOURCES.txt','SDL-Zlib.txt','GLFW-Zlib.txt'):
            assert 'PPSA99874/licenses/'+required in names
        assert b'/zink/' in archive.read('PPSA99874/licenses/UPSTREAM-NOTICES.txt')
        for name in ('eboot.bin','sce_module/libc.prx'):
            built=ROOT / 'build/zink-present-183/PPSA99874' / name
            assert hashlib.sha256(archive.read('PPSA99874/'+name)).hexdigest()==sha(built)
    symbols=directory / 'zink-present183-symbols.elf'
    assert sha(symbols)==record['symbols_elf_sha256']
    nm=args.llvm_home.resolve() / 'bin/llvm-nm'
    defined=subprocess.check_output([str(nm),'--defined-only',str(symbols)],text=True)
    exports=[line.split()[-1]for line in defined.splitlines()if len(line.split())>=3]
    for name in record['single_copy_exports']:assert exports.count(name)==1,name
    assert not any(name.startswith(('Java_','alcOpenDevice'))for name in exports)
    assert 'ps5shaderc_fault_begin' in exports and 'ps5shaderc_fault_extended_status' in exports
    assert b'First-frame glfwPollEvents enter' in symbols.read_bytes()
    assert 'glfwCreateWindow' in exports and 'SDL_CreateWindow' in exports
    assert record['source_tree']=='clean'
    for name,dep in record['native_dependencies'].items():
        assert sha(ROOT / 'build/zink-present-183' / (name+'.o'))==dep['linked_object_sha256']
    assert 'ps5zink_create' in exports and 'ps5zink_destroy' in exports
    assert b'No Zink run initialized' in symbols.read_bytes() and b'zink-%s-%lld-%ld' in symbols.read_bytes()
    converter=args.runtime_workspace.resolve() / 'build/native/host/ps5-native-tool'
    for name in ('eboot.bin','sce_module/libc.prx'):
        path=ROOT / 'build/zink-present-183/PPSA99874' / name
        subprocess.run([str(converter),'self','--inspect','--file',str(path)],check=True,stdout=subprocess.DEVNULL)
    print('PASS exact native183ZIP/digest/identity/notices/pins/one-copy RADV+Mesa exports/run identity; no game/Java/OpenAL payload; signatures inspect successfully. Console pending.')


if __name__=='__main__':main()
