#!/usr/bin/env python3
"""Build genuine pinned OSHI6.6.5 PS5 CPU overlay; explicit publisher cache only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from host_toolchain import ROOT, java_home
from prepare_client_261 import verified
from build_lwjgl333 import obtain


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--publisher-cache',type=Path,required=True)
    p.add_argument('--cache-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--java-home',type=Path)
    p.add_argument('--fetch-deps',action='store_true')
    a=p.parse_args();jdk=java_home(a.java_home);port=ROOT/'client/ports/oshi665';spec=json.loads((port/'sources.json').read_text());work=a.output_dir.resolve();work.mkdir(parents=True,exist_ok=True);cache=a.cache_dir.resolve();cache.mkdir(parents=True,exist_ok=True)
    archive=obtain(spec['source'],cache/'sources.jar',a.fetch_deps)
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    if sha(port/'LICENSE')!=spec['license_sha256']:raise ValueError('License pin mismatch')
    row=next(r for r in json.loads((ROOT/'client/1.21.lock.json').read_text())['versions'] if r['id']=='1.21.10')
    cp=[]
    for lib in row['libraries']:
        if lib['name'] in ('com.github.oshi:oshi-core:6.6.5','net.java.dev.jna:jna:5.15.0','org.slf4j:slf4j-api:2.0.16'):
            pin=lib['downloads']['artifact'];file=a.publisher_cache.resolve()/'libraries'/pin['path'];verified(pin,file,offline=True);cp.append(file)
    if len(cp)!=3:raise ValueError('Exact OSHI/JNA/SLF4J generation required')
    src=work/'src';shutil.rmtree(src,ignore_errors=True);(src/'oshi').mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:(src/'oshi/SystemInfo.java').write_bytes(z.read('oshi/SystemInfo.java'))
    subprocess.run(['git','apply','--unsafe-paths','--directory='+str(src),str(port/'0001-ps5-cpu-provider.patch')],check=True)
    shutil.copytree(port/'java',src,dirs_exist_ok=True);classes=work/'classes';shutil.rmtree(classes,ignore_errors=True);classes.mkdir()
    subprocess.run([str(jdk/'bin/javac'),'--release','21','-cp',os.pathsep.join(map(str,cp)),'-d',str(classes),*map(str,sorted(src.rglob('*.java')))],check=True)
    jar=work/'oshi-6.6.5-ps5-platform.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(classes.rglob('*.class')):
            info=zipfile.ZipInfo(f.relative_to(classes).as_posix());info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
        z.writestr(zipfile.ZipInfo('META-INF/OSHI-LICENSE.txt'),(port/'LICENSE').read_bytes())
    audit={'version':'6.6.5','output_sha256':sha(jar),'source_sha256':{str(f.relative_to(port)):sha(f) for f in port.rglob('*') if f.is_file()},'original_dependencies_sha256':{f.name:sha(f) for f in cp},'upstream_source':spec['source'],'scope':spec['scope'],'console':'pending1.21.10PS5'}
    (work/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PASS OSHI665 overlay',sha(jar))


if __name__=='__main__':main()
