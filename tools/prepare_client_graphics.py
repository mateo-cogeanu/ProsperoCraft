#!/usr/bin/env python3
"""Build the pinned PS5 RADV/platform dependencies in consumer-only caches.

macOS adapter for upstream build-radv.sh: same source/options, explicit baseline
x86-64 target, local Python environment and real target compiler-rt CPU model.
The passing Java runtime SDK is never modified. Downloaded code stays ignored.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/'client/graphics/sources.json').read_text())
LLVM=Path('/opt/homebrew/opt/llvm/bin')

def run(*args,env=None,cwd=None):
    subprocess.run(list(map(str,args)),env=env,cwd=cwd,check=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def download(row,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists()or sha(path)!=row['sha256']:
        temp=path.with_suffix(path.suffix+'.download')
        urllib.request.urlretrieve(row['url'],temp)
        if sha(temp)!=row['sha256']:raise ValueError('Downloaded source hash: '+path.name)
        temp.replace(path)

def dependency(key,folder):
    row=LOCK[key];path=ROOT/'.tools'/folder
    if not path.exists():run('git','clone','--depth','1',row['repository'],path)
    try:run('git','-C',path,'cat-file','-e',row['commit']+'^{commit}')
    except subprocess.CalledProcessError:run('git','-C',path,'fetch','--depth','1','origin',row['commit'])
    return path

def prepare(runtime):
    work=ROOT/'build';work.mkdir(exist_ok=True)
    driver=dependency('driver','ps5-vulkan');mesa=dependency('mesa','PS5_Mesa');fork=dependency('sdk','PS5_PayloadSDK')
    # Driver and Mesa build directly from verified, clean pinned tracked sources.
    for key,path in [('driver',driver),('mesa',mesa)]:
        current=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        if current!=LOCK[key]['commit']:
            if subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True):raise ValueError('Dirty dependency: '+key)
            run('git','-C',path,'checkout','--detach',LOCK[key]['commit'])
        run('git','-C',path,'diff','--exit-code','HEAD')
    archive=runtime/'.tools/native-sdk.zip';download(LOCK['base_sdk'],archive)
    sdk=ROOT/'.tools/graphics-sdk';source=work/'graphics-sdk-source';stamp=sdk/'.client-graphics-sdk.json'
    record={'base_sha256':LOCK['base_sdk']['sha256'],'fork_commit':LOCK['sdk']['commit'],'adapter':'client-graphics-sdk-v1','clang':subprocess.check_output([str(LLVM/'clang'),'--version'],text=True).splitlines()[0]}
    if not stamp.exists()or json.loads(stamp.read_text())!=record:
        shutil.rmtree(sdk,ignore_errors=True);sdk.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive)as z:z.extractall(sdk.parent)
        # The release extracts to ps5-payload-sdk; never touch the runtime checkout.
        extracted=sdk.parent/'ps5-payload-sdk'
        extracted.rename(sdk)
        shutil.rmtree(source,ignore_errors=True);source.mkdir()
        exported=subprocess.check_output(['git','-C',str(fork),'archive',LOCK['sdk']['commit']])
        import io,tarfile
        with tarfile.open(fileobj=io.BytesIO(exported))as t:t.extractall(source,filter='data')
        common=sdk/'target/include_common'
        if common.is_dir()and not common.is_symlink():shutil.rmtree(common)
        run('make','-s','-C',source/'include','install','DESTDIR='+str(sdk))
        for name in ['prospero-clang','prospero-clang++']:shutil.copyfile(source/'host/bin'/name,sdk/'bin'/name)
        for p in (sdk/'bin').iterdir():
            if p.is_file():p.chmod(0o755)
        # Compile source units explicitly: this pin's make pattern rules pick
        # its general -Werror rule for imported regex on this host. No source edit.
        objects=[];out=work/'graphics-platform';out.mkdir(exist_ok=True)
        for p in [*sorted((source/'platform/src').glob('*.c')),*sorted((source/'platform/src/regex').glob('*.c')),source/'platform/src/dlmalloc/mspace.c']:
            obj=out/('_'.join(p.relative_to(source/'platform/src').parts)+'.o')
            run(LLVM/'clang','-target','x86_64-sie-ps5','-fPIC','-fno-plt','-fno-stack-protector','-femulated-tls','-fvisibility-nodllstorageclass=default','-fdenormal-fp-math=ieee','-isystem',source/'include/freebsd','-I'+str(source/'platform/include'),'-std=c11','-O2',*(['-w']if 'regex'in p.parts or 'dlmalloc'in p.parts else['-Wall','-Wextra','-Werror']),'-c',p,'-o',obj)
            objects.append(obj)
        run(LLVM/'llvm-ar','rcs',sdk/'target/lib/libps5platform.a',*objects)
        shutil.copytree(source/'platform/include/ps5platform',sdk/'target/include/ps5platform',dirs_exist_ok=True)
        stamp.write_text(json.dumps(record,indent=2)+'\n')
    # The cached SDK can be shared by a fresh build directory. Keep its exact
    # fork source/attribution inputs available even when the binary SDK stamp
    # avoids recompilation; current packaging consumes these notices.
    if not source.exists():
        source.mkdir()
        exported=subprocess.check_output(['git','-C',str(fork),'archive',LOCK['sdk']['commit']])
        import io,tarfile
        with tarfile.open(fileobj=io.BytesIO(exported))as t:t.extractall(source,filter='data')
    venv=ROOT/'.tools/graphics-python'
    if not (venv/'bin/meson').exists():
        run('python3','-m','venv',venv)
        run(venv/'bin/pip','install',*LOCK['python_packages'])
    env=dict(os.environ,PATH=str(venv/'bin')+':'+str(LLVM)+':'+os.environ['PATH'],LLVM_CONFIG=str(LLVM/'llvm-config'))
    host=work/'graphics-clc';meson=venv/'bin/meson'
    common=['-Dgallium-drivers=','-Dplatforms=','-Dglx=disabled','-Degl=disabled','-Dgbm=disabled','-Dopengl=false','-Dgles1=disabled','-Dgles2=disabled','-Dbuild-tests=false','-Dvalgrind=disabled','-Dlibunwind=disabled','-Dzstd=disabled','-Dxmlconfig=disabled','-Dtools=']
    if not (host/'build.ninja').exists():
        run(meson,'setup',host,mesa,'-Dbuildtype=release','-Dmesa-clc=enabled','-Dinstall-mesa-clc=true','-Dvulkan-drivers=','-Dllvm=enabled','-Dshared-llvm=enabled',*common,env=dict(env,CC=str(LLVM/'clang'),CXX=str(LLVM/'clang++')))
    run('ninja','-C',host,'-j','6','src/compiler/clc/mesa_clc','src/compiler/spirv/vtn_bindgen2',env=env)
    bins=work/'graphics-clc-bin';bins.mkdir(exist_ok=True)
    for name,path in [('mesa_clc',host/'src/compiler/clc/mesa_clc'),('vtn_bindgen2',host/'src/compiler/spirv/vtn_bindgen2')]:
        dest=bins/name
        if dest.is_symlink()or dest.exists():dest.unlink()
        dest.symlink_to(path)
    env['PATH']=str(bins)+':'+env['PATH']
    cross=work/'graphics-cross.ini';cross.write_text(f"""[binaries]
c = '{sdk}/bin/prospero-clang'
cpp = '{sdk}/bin/prospero-clang++'
ar = '{sdk}/bin/prospero-ar'
strip = '{sdk}/bin/prospero-strip'
pkg-config = '{sdk}/bin/prospero-pkg-config'
[host_machine]
system = 'freebsd'
cpu_family = 'x86_64'
cpu = 'x86_64'
endian = 'little'
[built-in options]
default_library = 'static'
c_args = ['-march=x86-64', '-msse2', '-mno-avx', '-mno-avx2', '-mno-fma']
cpp_args = ['-march=x86-64', '-msse2', '-mno-avx', '-mno-avx2', '-mno-fma']
[properties]
needs_exe_wrapper = true
""")
    target=work/'graphics-radv'
    if not (target/'build.ninja').exists():
        run(meson,'setup',target,mesa,'--cross-file',cross,'-Dvulkan-drivers=amd','-Dradv-winsys=ps5','-Dllvm=disabled','-Damd-use-llvm=false','-Dvideo-codecs=','-Dbuildtype=debugoptimized','-Db_ndebug=true','-Dzlib=enabled','--force-fallback-for=zlib','-Dexpat=disabled','-Dshader-cache=enabled','-Dvulkan-layers=','-Dmesa-clc=system','-Dradv-build-id='+LOCK['mesa']['commit'],*common,env=env)
    run('ninja','-C',target,'-j','6','src/amd/vulkan/libvulkan_radeon.a',env=env)
    for row in LOCK['compiler_rt']['files']:
        download(row,work/('graphics-cpu-model.c'if row['file']=='x86.c'else row['file']))
    license_row=LOCK['compiler_rt']['license'];download(license_row,work/'graphics-LLVM-LICENSE.txt')
    print('READY: pinned native-only graphics dependencies; Java runtime SDK untouched')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',required=True,type=Path);a=p.parse_args();prepare(a.runtime_workspace.resolve())
