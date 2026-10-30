#!/usr/bin/env python3
"""Build pinned shaderc/glslang/SPIRV-Tools on host or PS5; stage target constructors."""
from pathlib import Path
import argparse,subprocess,json,hashlib,re,tarfile,io,shutil
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime,host=False,offline=False):
    port=ROOT/'client/ports/shaderc';lock=json.loads((port/'sources.json').read_text());source=ROOT/'.tools/shaderc-src'
    rows=[(source,lock['shaderc'])]+[(source/'third_party'/row['name'],row)for row in lock['dependencies']]
    for path,row in rows:
        if not path.exists():
            if offline:raise FileNotFoundError('Missing compiler source: '+str(path))
            path.mkdir(parents=True);subprocess.run(['git','init','-q',str(path)],check=True)
        if subprocess.run(['git','-C',str(path),'cat-file','-e',row['commit']],capture_output=True).returncode:
            if offline:raise FileNotFoundError('Missing pinned compiler revision')
            subprocess.run(['git','-C',str(path),'fetch','--depth','1',row['repository'],row['commit']],check=True)
        revision=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        if revision!=row['commit']:subprocess.run(['git','-C',str(path),'checkout','--detach',row['commit']],check=True)
        subprocess.run(['git','-C',str(path),'diff','--exit-code','HEAD'],check=True)
    out=ROOT/('build/shaderc-host'if host else'build/shaderc-ps5');out.mkdir(exist_ok=True)
    # Export the pinned shaderc tree; target-only observational patch never edits
    # upstream caches or the original dependency/Java artifacts.
    configured_source=source
    patch=port/'0001-compile-checkpoints.patch'
    if not host:
        configured_source=out/'source';shutil.rmtree(configured_source,ignore_errors=True);configured_source.mkdir()
        archive=subprocess.check_output(['git','-C',str(source),'archive','HEAD'])
        with tarfile.open(fileobj=io.BytesIO(archive))as contents:contents.extractall(configured_source,filter='data')
        for path,row in rows[1:]:
            target=configured_source/'third_party'/row['name']
            if target.exists():shutil.rmtree(target)
            if row['name']=='glslang':
                target.mkdir()
                archive=subprocess.check_output(['git','-C',str(path),'archive','HEAD'])
                with tarfile.open(fileobj=io.BytesIO(archive))as contents:contents.extractall(target,filter='data')
                subprocess.run(['git','apply','--unsafe-paths','--directory='+str(target),str(port/'0002-parser-checkpoints.patch')],check=True)
                subprocess.run(['git','apply','--unsafe-paths','--directory='+str(target),str(port/'0004-glslang-reserved-init-mutex.patch')],check=True)
            else:target.symlink_to(path.resolve(),target_is_directory=True)
        subprocess.run(['git','apply','--unsafe-paths','--directory='+str(configured_source),str(patch)],check=True)
        subprocess.run(['git','apply','--unsafe-paths','--directory='+str(configured_source),str(port/'0003-reserved-init-mutex.patch')],check=True)
        subprocess.run(['git','apply','--unsafe-paths','--directory='+str(configured_source),str(port/'0005-counting-includer-owned-mutex.patch')],check=True)
    cache=out/'CMakeCache.txt'
    if cache.exists():
        home=re.search(r'^CMAKE_HOME_DIRECTORY:INTERNAL=(.+)$',cache.read_text(),re.M)
        if home and Path(home[1]).resolve()!=configured_source.resolve():cache.unlink()
    args=['cmake','-S',str(configured_source),'-B',str(out),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DSHADERC_SKIP_TESTS=ON','-DSHADERC_SKIP_EXAMPLES=ON','-DSHADERC_SKIP_EXECUTABLES=ON','-DSHADERC_SKIP_COPYRIGHT_CHECK=ON','-DSHADERC_SKIP_INSTALL=OFF','-DSHADERC_ENABLE_WERROR_COMPILE=OFF','-DENABLE_GLSLANG_BINARIES=OFF','-DENABLE_HLSL=ON','-DSPIRV_SKIP_EXECUTABLES=ON','-DSPIRV_SKIP_TESTS=ON','-DDISABLE_EXCEPTIONS=ON','-DCMAKE_POSITION_INDEPENDENT_CODE=ON']
    if not host:
        sdk=ROOT/'.tools/graphics-sdk';toolchain=out/'toolchain.cmake'
        toolchain.write_text('set(CMAKE_SYSTEM_NAME FreeBSD)\nset(CMAKE_SYSTEM_VERSION 9)\nset(CMAKE_SYSTEM_PROCESSOR x86_64)\nset(CMAKE_CROSSCOMPILING TRUE)\nset(CMAKE_C_COMPILER '+str(LLVM/'clang')+')\nset(CMAKE_CXX_COMPILER '+str(LLVM/'clang++')+')\nset(CMAKE_C_COMPILER_TARGET x86_64-sie-ps5)\nset(CMAKE_CXX_COMPILER_TARGET x86_64-sie-ps5)\nset(CMAKE_AR '+str(LLVM/'llvm-ar')+')\nset(CMAKE_RANLIB '+str(LLVM/'llvm-ranlib')+')\nset(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)\n')
        flags='-isysroot '+str(sdk)+' -isystem '+str(sdk/'target/include')+' -fvisibility-nodllstorageclass=default -march=x86-64 -msse2 -mno-avx -mno-avx2 -mno-fma -fno-stack-protector -femulated-tls'
        args+=['-DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON','-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_C_FLAGS='+flags,'-DCMAKE_CXX_FLAGS=-I'+str(port)+' -I'+str(ROOT/'build/sdl-src/include')+' -isystem '+str(sdk/'target/include/c++/v1')+' -DPS5_SHADERC_CHECKPOINTS '+flags]
    subprocess.run(args,check=True);subprocess.run(['cmake','--build',str(out),'--target','shaderc_shared'if host else'shaderc_combined','-j','4'if host else'6'],check=True)
    if host:return out/'libshaderc/libshaderc_shared.dylib'
    raw=out/'compiler-raw.o';obj=out/'compiler.o'
    # Shaderc newly needs libc++ iostream initialization. Extract the exact
    # shared SDK member so its real constructor can be staged, not auto-run.
    subprocess.run([str(LLVM/'llvm-ar'),'x',str(sdk/'target/lib/libc++.a'),'iostream.cpp.o'],cwd=out,check=True)
    subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r','--whole-archive',str(out/'libshaderc/libshaderc_combined.a'),'--no-whole-archive',str(out/'iostream.cpp.o'),'-o',str(raw)],check=True)
    # The actual SDK compatibility providers have already been scoped for RADV.
    # Only rename compiler references to real definitions present in that object.
    gpu=json.loads((ROOT/'build/client-gpu/audit.json').read_text());names=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(ROOT/'build/client-gpu/graphics-support.o')],text=True);defined={line.split()[-1]for line in names.splitlines()if len(line.split())==3}
    bindings={k:v for k,v in gpu['graphics_bindings'].items()if v in defined};bindings['shaderc_compiler_initialize']='ps5shaderc_real_compiler_initialize';mapping=out/'provider-bindings.txt';mapping.write_text(''.join(k+' '+v+'\n'for k,v in sorted(bindings.items())))
    subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(mapping),str(raw),str(obj)],check=True)
    sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(obj)],text=True);initializers=sorted(set(re.findall(r'\]\s+(\.(?:init_array|ctors)(?:\.\S+)?)\s',sections)));options=[]
    for name in initializers:
        suffix=name.rsplit('.',1)[-1];priority=(65535-int(suffix)if name.startswith('.ctors.')else int(suffix))if suffix.isdigit()else 65535
        options+=['--rename-section',name+'=.data.rel.ro.clientshaderc.init_array.'+f'{priority:05d}'+name]
    if options:subprocess.run([str(LLVM/'llvm-objcopy'),*options,str(obj)],check=True)
    headers=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base';lifecycle=out/'lifecycle-raw.o'
    subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-I'+str(headers),'-I'+str(headers/'freebsd'),'-c',str(port/'lifecycle.c'),'-o',str(lifecycle)],check=True)
    fault=out/'fault.o'
    subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-c',str(port/'fault.c'),'-o',str(fault)],check=True)
    combined=out/'lifecycle.o'
    subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r',str(lifecycle),str(fault),'-o',str(combined)],check=True)
    lifecycle=combined
    audit={'include_mutex':{'header_sha256':hashlib.sha256((port/'ps5_include_mutex.hpp').read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256((port/'0005-counting-includer-owned-mutex.patch').read_bytes()).hexdigest(),'policy':'CountingIncluder per-compilation in-object atomic exclusion;no kernel init/destroy;RAII include delegation','console':'Pending160'},'init_mutex_source_sha256':hashlib.sha256((port/'ps5_init_mutex.hpp').read_bytes()).hexdigest(),'init_mutex_patch_sha256':{name:hashlib.sha256((port/name).read_bytes()).hexdigest()for name in ['0003-reserved-init-mutex.patch','0004-glslang-reserved-init-mutex.patch']},'sources':lock,'diagnostic_patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'parser_patch_sha256':hashlib.sha256((port/'0002-parser-checkpoints.patch').read_bytes()).hexdigest(),'fault_source_sha256':hashlib.sha256((port/'fault.c').read_bytes()).hexdigest(),'constructor_sections':initializers,'lifecycle':'Explicit resident JNI_OnLoad initializes retained compiler constructors once after VM; no module teardown claim','objects_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [obj,lifecycle]},'bindings':bindings,'console':'pending'};(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');return obj,lifecycle,audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runtime-workspace',required=True,type=Path);p.add_argument('--host',action='store_true');p.add_argument('--offline',action='store_true');a=p.parse_args();build(a.runtime_workspace,a.host,a.offline);print('PASS pinned shaderc dependency build; host'if a.host else'PASS pinned PS5 shaderc dependency build and explicit constructor staging; console pending')
