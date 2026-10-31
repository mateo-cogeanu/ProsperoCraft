#!/usr/bin/env python3
"""Prove exact legacy source reconstruction and optionally compare target objects."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from elf_equivalence import canonical_object
from host_toolchain import executable
from build_client_openal_relink import export_consumer_bootstrap

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['check_name','version','notification_prefix','vm_result','fixture','stage_format','build_note','ready_note','controller_failure','running_note','failure_format','pass_state','pass_note']


def originals():
    body = (ROOT/'client/bootstrap/acceptance_impl.hpp').read_text().split('\n', 1)[1]
    records = json.loads((ROOT/'tests/bootstrap-migration.json').read_text())
    for variant, record in records.items():
        wrapper = (ROOT/'client'/variant/'bootstrap.cpp').read_text()
        config = dict(re.findall(r' ("(?:\\.|[^"\\])*")' + r', // (\w+)', wrapper))
        config = {field: value for value, field in config.items()}
        assert set(config) == set(FIELDS), variant
        source_body = body.replace('std::snprintf(state,sizeof(state),"%s",acceptance.pass_state)', 'std::snprintf(state,sizeof(state),acceptance.pass_state)')
        source = re.sub(r'acceptance\.(\w+)', lambda m: config[m[1]], source_body)
        prefix = config['notification_prefix']
        source = source.replace('std::strlen('+prefix+')', str(len(json.loads(prefix))))
        assert hashlib.sha256(source.encode()).hexdigest() == record['original_sha256'], variant
        assert json.loads(config['version']) == json.loads((ROOT/'client'/variant/'param.json').read_text())['contentVersion']
        yield variant, source


def target_compare(runtime):
    sdk = runtime/'.tools/native-sdk/ps5-payload-sdk'
    compiler = Path(executable('clang++', env='CXX'))
    headers = runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base'
    for variant, source in originals():
        with tempfile.TemporaryDirectory(prefix='bootstrap-equivalence-') as temporary:
            work = Path(temporary); unit = work/'bootstrap.cpp'; obj = work/'bootstrap.o'
            flags = ['-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include/c++/v1'),'-isystem',str(sdk/'target/include')]
            includes = [ROOT/'client'/variant, ROOT/('build/client-'+variant+'-probe'), ROOT/'client/native', runtime/'native/renderer',runtime/'build/native',runtime/'src',runtime/'native',runtime/'java25/probe',runtime/'java25/platform',headers,headers/'freebsd']
            command = [str(compiler),*flags,*['-I'+str(p) for p in includes],'-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-stack-protector','-fno-plt','-femulated-tls','-fno-exceptions','-fno-rtti','-ffunction-sections','-fdata-sections','-c',str(unit),'-o',str(obj)]
            unit.write_text(source);subprocess.run(command,check=True);before=obj.read_bytes()
            unit.write_text((ROOT/'client'/variant/'bootstrap.cpp').read_text());subprocess.run(command,check=True)
            assert canonical_object(before) == canonical_object(obj.read_bytes()), variant+' target code/data/relocations/symbols differ'
            print('PASS identical target code/data/relocations/symbols (pooled-string numbering normalized):',variant)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--runtime-workspace',type=Path);args=parser.parse_args()
    assert len(list(originals())) == 6
    with tempfile.TemporaryDirectory(prefix='bootstrap-source-export-') as temporary:
        kit=Path(temporary)
        for variant,_ in originals():
            export_consumer_bootstrap(kit,variant)
            for path in [Path(variant)/'bootstrap.cpp',Path('bootstrap/acceptance_config.hpp'),Path('bootstrap/acceptance_impl.hpp')]:
                assert (kit/'consumer-source/client'/path).read_bytes()==(ROOT/'client'/path).read_bytes()
    if args.runtime_workspace:target_compare(args.runtime_workspace.resolve())
    print('PASS six exact source reconstructions: all ordering/JNI/logs/ownership/failure paths preserved')
