#!/usr/bin/env python3
"""Package local native stage-2a Zink presentation probe; no release or Store action.

Reuses pinned native CRT, PS5 RADV link recipe, SDK and converter from native003.
The one combined GL/Zink/RADV object replaces the old RADV archive. No JVM,
OpenAL, game JAR or asset object is included. Preserve existing packages.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from host_toolchain import ROOT


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def package(args):
    runtime, component = args.runtime_workspace.resolve(), args.component.resolve()
    sdk, driver, llvm = ROOT / '.tools/graphics-sdk', ROOT / '.tools/ps5-vulkan', args.llvm_home.resolve()
    pin = json.loads((ROOT / 'client/graphics/sources.json').read_text())
    audit = json.loads(component.with_suffix('.json').read_text())
    if audit['host'] or sha(component) != audit['output_sha256'] or audit['source']['recipe']['mesa']['commit'] != pin['mesa']['commit']:
        raise ValueError('Wrong/stale combined PS5 component')
    for name, digest in audit['source']['recipe']['frontend'].items():
        if sha(ROOT / 'client/ports/zink' / name) != digest: raise ValueError('Stale frontend source')
    for category, directory in (('patches', 'zink'), ('wsi_patches', 'mesa'), ('wsi_headers', 'mesa')):
        for name, digest in audit['source']['recipe'][category].items():
            if sha(ROOT / 'client/ports' / directory / name) != digest: raise ValueError('Stale Mesa/WSI port input')
    if subprocess.check_output(['git', '-C', str(driver), 'rev-parse', 'HEAD'], text=True).strip() != pin['driver']['commit']:
        raise ValueError('Wrong driver CRT/recipe pin')
    subprocess.run(['git', '-C', str(driver), 'diff', '--exit-code', 'HEAD'], check=True)
    sdk_stamp=json.loads((sdk / '.client-graphics-sdk.json').read_text())
    if sdk_stamp['fork_commit'] != pin['sdk']['commit'] or sdk_stamp['base_sha256'] != pin['base_sdk']['sha256']:
        raise ValueError('Wrong SDK fork')
    param = json.loads((ROOT / 'client/zink_present/param.json').read_text())
    version, title = param['contentVersion'], param['titleId']
    if version != '01.000.181' or title != 'PPSA99874': raise ValueError('Review exact probe identity before packaging')
    work, output = ROOT / 'build/zink-present-181', args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / (title + '.zip')
    if archive.exists(): raise FileExistsError('Preserve existing candidate bytes; select a new --output-dir before rebuilding')
    work.mkdir(exist_ok=True)
    dependency_audits={}
    for name, obj, audit_path, source_directory, input_key in (
        ('sdl',ROOT / 'build/sdl3-native/resident-sdl.o',ROOT / 'build/sdl3-native/audit.json','sdl','port_sha256'),
        ('glfw',ROOT / 'build/glfw-native/ps5/glfw.o',ROOT / 'build/glfw-native/ps5/audit.json','glfw','local_source_sha256'),
    ):
        info=json.loads(audit_path.read_text())
        for file,digest in info[input_key].items():
            if sha(ROOT / 'client/ports' / source_directory / file)!=digest:raise ValueError('Stale '+name+' source: '+file)
        if name=='sdl' and sha(obj)!=info['object_sha256']:raise ValueError('SDL object mismatch')
        if name=='glfw' and sha(ROOT / 'client/ports/zink/frontend.h')!=info['zink_frontend_header_sha256']:raise ValueError('GLFW frontend header mismatch')
        renamed=work / (name+'.o')
        subprocess.run([str(llvm / 'bin/llvm-objcopy'),'--redefine-sym','JNI_OnLoad=ps5_zinkprobe_'+name+'_JNI_OnLoad',str(obj),str(renamed)],check=True)
        dependency_audits[name]={'object_sha256':sha(obj),'linked_object_sha256':sha(renamed),'jni_policy':'Genuine initializer privately renamed per component; no JVM or initializer calls in this native title','audit':info}

    env = dict(os.environ, LLVM_CONFIG=str(llvm / 'bin/llvm-config'), PATH=str(llvm / 'bin') + os.pathsep + os.environ.get('PATH', ''))
    def run(*command, **kwargs): subprocess.run(list(map(str, command)), check=True, env=env, **kwargs)
    flags = ['-target','x86_64-sie-ps5','-isysroot',str(sdk),'-fvisibility-nodllstorageclass=default',
             '-fno-stack-protector','-fno-plt','-femulated-tls','-march=x86-64','-msse2',
             '-mno-avx','-mno-avx2','-mno-fma','-fdenormal-fp-math=ieee','-O2',
             '-gline-tables-only','-ffunction-sections','-fdata-sections']
    objects = []
    for name, source, cxx, extra in (
        ('bootstrap',ROOT / 'client/zink_present/bootstrap.cpp',True,
         ['-I'+str(runtime / 'java25/probe'),'-I'+str(runtime / 'java25/platform'),'-I'+str(runtime / 'src'),'-DPS5ZINK_PROBE_VERSION="'+version+'"']),
        ('probe',ROOT / 'client/zink_present/present.c',False,['-I'+str(ROOT / '.tools/PS5_Mesa/include'),'-I'+str(ROOT / 'build/glfw-native/ps5/source/include')]),
        ('loader',ROOT / 'client/vulkan/loader.c',False,['-I'+str(ROOT / '.tools/PS5_Mesa/include')]),
        ('present_worker',ROOT / 'client/gpu/present_worker.c',False,[]),
        ('crt',driver / 'tooling/native/app_crt.cpp',True,[]),
        ('cpp_runtime',driver / 'tooling/native/app_cpp_runtime.cpp',True,[]),
        ('cpu_model',ROOT / 'build/graphics-cpu-model.c',False,['-I'+str(ROOT / 'build')]),
    ):
        obj = work / (name + '.o')
        run(llvm / 'bin' / ('clang++' if cxx else 'clang'), *flags,
            *(['-std=c++20','-fno-exceptions','-fno-rtti','-isystem',str(sdk / 'target/include/c++/v1')] if cxx else ['-std=c11']),
            '-isystem',str(sdk / 'target/include'),'-Wall','-Wextra','-Werror',*extra,'-c',source,'-o',obj)
        objects.append(obj)
    cpu_pin = next(row for row in pin['compiler_rt']['files'] if row['file'] == 'x86.c')
    if sha(ROOT / 'build/graphics-cpu-model.c') != cpu_pin['sha256']: raise ValueError('CPU model source pin mismatch')
    run(llvm / 'bin/llvm-ar','x',sdk / 'target/lib/libc.a','emutls.o',cwd=work)
    builtins = work / 'libgraphics-builtins.a';run(llvm / 'bin/llvm-ar','rcs',builtins,work / 'emutls.o')
    recipe, count = re.subn(r'    builtins=".*?\n','    builtins="'+str(builtins)+'"\n',(driver / 'tools/radv-link.sh').read_text(),count=1)
    if count != 1: raise ValueError('Driver builtins recipe changed')
    recipe_file = work / 'radv-link-host.sh';recipe_file.write_text(recipe)
    stubs=[]
    for name, source in (('libSceAgc','agc_canary_link_stub.c'),('libSceAgcDriver','agc_driver_canary_link_stub.c')):
        obj, so = work / (name+'.o'), work / (name+'.so')
        run(llvm / 'bin/clang',*flags,'-isystem',str(sdk / 'target/include'),'-c',driver / 'vendor/ps5/sdk/stubs' / source,'-o',obj)
        run('bash',sdk / 'bin/prospero-lld','--shared','-soname',name+'.prx','-o',so,obj);stubs.append(so)
    mouse_obj,mouse=work / 'mouse-imports.o',work / 'libSceMouse.so'
    run(llvm / 'bin/clang',*flags,'-fPIC','-c',ROOT / 'client/ports/sdl/ps5_mouse_imports.c','-o',mouse_obj)
    run('bash',sdk / 'bin/prospero-lld','--shared','-soname','libSceMouse.sprx','-o',mouse,mouse_obj)
    stubs.append(mouse)
    (work / 'native-only.map').write_text('{ local: *; };\n')
    linker = work / 'link.sh'
    linker.write_text('''#!/bin/bash
set -euo pipefail
source "$1"
radv_link_recipe "$2" "$3" "$4"
shift 4
"$1/bin/prospero-lld" "${radv_linker_script[@]}" --gc-sections --eh-frame-hdr "${radv_link_flags[@]}" \\
 --version-script "$2/tooling/native/app-symbols.map" --version-script "$3/native-only.map" --exclude-libs=ALL -e _start -o "$3/llvm-pie.elf" \\
 "$3/crt.o" "$3/cpp_runtime.o" "$3/bootstrap.o" "$3/probe.o" "$3/loader.o" "$3/cpu_model.o" "$3/present_worker.o" "$3/sdl.o" "$3/glfw.o" \\
 "$3/libSceAgc.so" "$3/libSceAgcDriver.so" "$3/libSceMouse.so" "${radv_link_inputs[@]}" --as-needed "$1"/target/lib/*.so
''')
    run('bash',linker,recipe_file,driver,sdk,component,sdk,driver,work)
    definitions = subprocess.check_output([str(llvm / 'bin/llvm-nm'),'--defined-only',str(work / 'llvm-pie.elf')], text=True)
    names=[line.split()[-1] for line in definitions.splitlines() if len(line.split()) >= 3]
    required=['ps5zink_create','ps5zink_destroy','_mesa_glapi_get_proc_address','vk_icdGetInstanceProcAddr','radv_CreateInstance','radv_CreateDevice','nir_shader_create','glfwCreateWindow','SDL_CreateWindow','prospero_sdl_tls_preinit']
    for name in required:
        if names.count(name) != 1: raise ValueError('Single-copy audit failed: ' + name)
    if any(name.startswith(('Java_', 'alcOpenDevice')) for name in names): raise ValueError('Unexpected Java/OpenAL payload in native-only probe')
    converter=runtime / 'build/native/host/ps5-native-tool'
    run(converter,'link','--in',work / 'llvm-pie.elf','--out',work / 'eboot.elf','--stub-dir',sdk / 'target/lib',
        *sum([['--stub',str(s)] for s in stubs],[]),'--module-sdk','0x02000009','--companion-sdk','0x08050001','--file-name','eboot.elf')
    if args.check_only:
        print('PASS native compile/link, single-copy audit and converter; no candidate ZIP created')
        return
    app=work / title
    if app.exists(): shutil.rmtree(app)
    (app / 'sce_sys').mkdir(parents=True);(app / 'sce_module').mkdir()
    run(converter,'self','--sign','--in',work / 'eboot.elf','--out',app / 'eboot.bin','--magic','0x1D3D154F')
    shutil.copyfile(ROOT / 'client/zink_present/param.json',app / 'sce_sys/param.json')
    shutil.copyfile(runtime / 'sce_sys/icon0.png',app / 'sce_sys/icon0.png')
    shutil.copyfile(runtime / 'build/native/libc.prx',app / 'sce_module/libc.prx')
    from apply_branding import apply_app
    apply_app(app)
    licenses=app / 'licenses';licenses.mkdir(exist_ok=True)
    for source,name in ((ROOT / 'LICENSE','ProsperoCraft-GPL-3.0-or-later.txt'),(driver / 'LICENSE','PS5-Vulkan-GPL-3.0.txt'),
                        (ROOT / 'build/graphics-sdk-source/LICENSE','PS5-PayloadSDK-GPL-3.0.txt'),
                        (ROOT / 'client/ports/zink/LICENSE.txt','Mesa-Zink-MIT.txt'),(ROOT / 'build/graphics-LLVM-LICENSE.txt','LLVM-LICENSE.txt')):
        shutil.copyfile(source,licenses / name)
    shutil.copytree(ROOT / '.tools/PS5_Mesa/licenses',licenses / 'Mesa')
    shutil.copyfile(ROOT / 'build/sdl-src/LICENSE.txt',licenses / 'SDL-Zlib.txt')
    shutil.copyfile(ROOT / 'client/ports/glfw/LICENSE.md',licenses / 'GLFW-Zlib.txt')
    for name in ('Zlib.txt','MIT.txt'):shutil.copyfile(ROOT / 'client/ports/sdl' / name,licenses / ('SDL-reference-'+name))
    # Existing upstream native003 notices cover this exact Mesa tree, including
    # its Zink files. The known source pins remain explicit in the package.
    notices=ROOT / 'build/client-graphics/PPSA99874/licenses/UPSTREAM-NOTICES.txt'
    if not notices.is_file(): raise FileNotFoundError('Prepare native graphics notices with package_client_graphics.py first')
    shutil.copyfile(notices,licenses / 'UPSTREAM-NOTICES.txt')
    (licenses / 'SOURCES.txt').write_text('ProsperoCraft native Zink stage2a only; GPL-3.0-or-later project/native CRT; MIT Mesa/Zink and original component licenses.\nSources and port patches: https://github.com/mateo-cogeanu/ProsperoCraft\nMesa: '+pin['mesa']['repository']+'@'+pin['mesa']['commit']+'\nNo JVM, game JAR, asset object or OpenAL is linked. Genuine GLFW/SDL video is included; SDL audio is not initialized. No OpenAL relink obligation is created by this native-only package.\n')
    commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    record={'app_version':version,'title_id':title,'source_commit':commit,
            'source_tree':'modified' if subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True).strip() else 'clean',
            'scope':'Native console stage2a only:3 animated GLFW/SDL kopper cycles with teardown/reinit; human visible result and launcher/JVM/game pending',
            'combined_object_sha256':sha(component),'mesa':audit['source']['recipe']['mesa'],
            'consumer_sources_sha256':{name:sha(ROOT / name) for name in (
                'client/zink_present/bootstrap.cpp','client/zink_present/present.c','client/zink_present/param.json',
                'client/vulkan/loader.c','client/gpu/present_worker.c','client/launcher/hardware_identity.hpp',
                'client/ports/oshi/hardware_labels.hpp','client/startup/input_present_trace.hpp',
                'tools/package_zink_present_probe.py','tools/build_zink_native.py')},
            'frontend_sources_sha256':audit['source']['recipe']['frontend'],
            'driver_crt_pin':pin['driver'],
            'patches':audit['source']['recipe']['patches'],'wsi_patches':audit['source']['recipe']['wsi_patches'],
            'objects_sha256':{p.name:sha(p) for p in objects},'sdk_pins':pin['sdk'],'native_dependencies':dependency_audits,
            'symbols_elf_sha256':sha(work / 'llvm-pie.elf'),'single_copy_exports':required,
            'runtime':'JVM not linked; runtime workspace supplies native converter, clean-room libc and log/pad headers',
            'runtime_inputs_sha256':{name:sha(runtime / name) for name in ('java25/probe/log_share.hpp','java25/platform/console_model.hpp','src/pad.h','build/native/libc.prx')},
            'console':'NOT TESTED','release_store':'No action'}
    assets=app / 'assets';assets.mkdir();(assets / 'zink-audit.json').write_text(json.dumps(record,indent=2)+'\n')
    for path in (app / 'eboot.bin',app / 'sce_module/libc.prx'):run(converter,'self','--inspect','--file',path)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output_zip:
        for path in sorted(app.rglob('*')):
            if path.is_file():
                if path.suffix.lower()=='.jar' or '/objects/' in str(path): raise ValueError('Forbidden publisher payload')
                info=zipfile.ZipInfo(path.relative_to(work).as_posix());info.external_attr=0o100777<<16;info.compress_type=zipfile.ZIP_DEFLATED
                output_zip.writestr(info,path.read_bytes())
    record['package_sha256']=sha(archive)
    (output / 'build-audit.json').write_text(json.dumps(record,indent=2)+'\n')
    (output / 'SHA256SUMS').write_text(record['package_sha256']+'  '+archive.name+'\n')
    shutil.copyfile(work / 'llvm-pie.elf',output / 'zink-present181-symbols.elf')
    print('LOCAL CANDIDATE',archive,'SHA256',record['package_sha256'],flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-workspace',type=Path,required=True)
    parser.add_argument('--component',type=Path,required=True)
    parser.add_argument('--llvm-home',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,default=ROOT / 'dist/candidates/zink-present-181')
    parser.add_argument('--check-only',action='store_true',help='Compile/link/audit/convert without creating a candidate ZIP')
    package(parser.parse_args())


if __name__=='__main__':main()
