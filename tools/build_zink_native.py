#!/usr/bin/env python3
"""Build a private real GL/Zink frontend and RADV from one pinned Mesa export.

Opt-in component builder; never changes the accepted graphics build, SDK,
launcher gates or app identity. Host execution uses an explicitly supplied
Vulkan ICD wrapper. Target output is a relocatable component, not an app.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tarfile
import urllib.request

from host_toolchain import ROOT, executable


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def export_archive(archive, destination, pin):
    """Extract only pinned regular files/directories and contained symlinks."""
    if archive.stat().st_size != pin['size'] or sha(archive) != pin['sha256']:
        raise ValueError('Mesa archive size/SHA-256 mismatch')
    destination.mkdir(parents=True)
    with tarfile.open(archive) as source:
        members = source.getmembers()
        roots = {Path(m.name).parts[0] for m in members}
        if len(roots) != 1:
            raise ValueError('Mesa archive root mismatch')
        links = []
        for member in members:
            parts = Path(member.name).parts
            if Path(member.name).is_absolute() or '..' in parts:
                raise ValueError('Unsafe archive path')
            relative = Path(*parts[1:])
            path = destination / relative
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                path.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as src, path.open('wb') as dst:
                    shutil.copyfileobj(src, dst)
                path.chmod(member.mode & 0o777)
            elif member.issym():
                links.append((path, member.linkname))
            else:
                raise ValueError('Unexpected archive entry type')
        for path, target in links:
            if not (path.parent / target).resolve().is_relative_to(destination.resolve()):
                raise ValueError('Escaping archive symlink')
            path.symlink_to(target)


def archive_inventory(archive):
    """Original file/link identities, so later exports cannot hide side edits."""
    files, links = {}, {}
    with tarfile.open(archive) as source:
        for member in source:
            name = Path(*Path(member.name).parts[1:]).as_posix()
            if member.isfile():
                with source.extractfile(member) as data:
                    digest = hashlib.sha256()
                    for block in iter(lambda: data.read(1024 * 1024), b''): digest.update(block)
                files[name] = digest.hexdigest()
            elif member.issym(): links[name] = member.linkname
    return {'files': files, 'links': links}


MESON_TARGET = '''
# ProsperoCraft private frontend; no EGL/DRI loader and no second driver.
ps5zink_frontend = static_library('prosperozink_frontend',
  'prospero-zink/frontend.c',
  c_args : host_machine.system() in ['darwin', 'linux'] ? ['-fsanitize=address,undefined'] : [],
  include_directories : [inc_include, inc_src, inc_mesa, inc_gallium, inc_gallium_aux, inc_gallium_drivers],
  dependencies : [idep_nir_headers, idep_mesautil, idep_vulkan_util_headers],
  gnu_symbol_visibility : 'hidden',
)
# This target expresses the full static dependency closure. On PS5 its input
# objects/archives are linked -r, never as this desktop-style shared ELF.
ps5zink_bundle = shared_library('prosperozink',
  link_whole : ps5zink_frontend,
  link_with : [libmesa, libzink, libgallium, libglapi],
  dependencies : [idep_libglsl, idep_nir, idep_vtn, idep_mesautil, idep_vulkan_util, idep_xmlconfig, dep_thread, dep_dl],
  link_args : ps5zink_extra_link + (host_machine.system() in ['darwin', 'linux'] ? ['-fsanitize=address,undefined'] : []),
  install : false,
)
'''
MESON_PREFIX = "\nps5zink_extra_link = []\nif host_machine.system() == 'darwin'\n  ps5zink_extra_link += ['-framework', 'Foundation']\nendif\n"


def prepare_sources(args):
    pins = json.loads((ROOT / 'client/ports/zink/sources.json').read_text())
    graphics = json.loads((ROOT / 'client/graphics/sources.json').read_text())
    if pins['commit'] != graphics['mesa']['commit'] or pins['repository'] != graphics['mesa']['repository']:
        raise ValueError('Zink and RADV must use the same pin')
    archive = args.archive.resolve() if args.archive else ROOT / '.tools/zink' / ('mesa-' + pins['commit'] + '.tar.gz')
    if not archive.exists():
        if args.offline:
            raise FileNotFoundError('Missing Mesa archive; provide --archive or run without --offline')
        archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = archive.with_suffix('.download')
        try:
            urllib.request.urlretrieve(pins['archive']['url'], temporary)
            if temporary.stat().st_size != pins['archive']['size'] or sha(temporary) != pins['archive']['sha256']:
                raise ValueError('Mesa archive download integrity failure')
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
    if archive.stat().st_size != pins['archive']['size'] or sha(archive) != pins['archive']['sha256']:
        raise ValueError('Mesa source archive integrity failure')
    port = ROOT / 'client/ports/zink'
    patches = sorted(port.glob('*.patch'))
    recipe = {'mesa': pins, 'patches': {p.name: sha(p) for p in patches},
              'frontend': {p.name: sha(p) for p in (port / 'frontend.c', port / 'frontend.h')},
              'wsi_patches': {p.name: sha(p) for p in sorted((ROOT / 'client/ports/mesa').glob('*.patch'))},
              'wsi_headers': {p.name: sha(p) for p in sorted((ROOT / 'client/ports/mesa').glob('*.h'))},
              'meson_target': MESON_TARGET}
    source_recipe = {k: v for k, v in recipe.items() if k not in ('frontend', 'meson_target')}
    key = hashlib.sha256(json.dumps(source_recipe, sort_keys=True).encode()).hexdigest()[:16]
    work = args.work_dir.resolve() / key
    source = work / 'source'
    stamp = work / 'source-audit.json'
    if source.exists():
        if not stamp.exists():
            raise ValueError('Incomplete source export; select a new --work-dir')
        record = json.loads(stamp.read_text())
        migrated_inventory = 'original_inventory' not in record
        if migrated_inventory:
            record['original_inventory'] = archive_inventory(archive)
        for name, expected in record['original_inventory']['files'].items():
            if name not in record['patched_files'] and sha(source / name) != expected:
                raise ValueError('Modified original Mesa export; preserve it and choose a new --work-dir: ' + name)
        for name, expected in record['original_inventory']['links'].items():
            if not (source / name).is_symlink() or os.readlink(source / name) != expected:
                raise ValueError('Modified original Mesa link: ' + name)
        for name, expected in record['patched_files'].items():
            if sha(source / name) != expected:
                raise ValueError('Modified generated source; preserve it and choose a new --work-dir: ' + name)
        if migrated_inventory:
            stamp.write_text(json.dumps(record, indent=2) + '\n')
        if record['recipe'] != recipe:
            # Update only verified previous generated overlays; keep the same
            # pinned compiler/driver build for fast frontend iteration.
            root = source / 'meson.build'
            old_suffix = MESON_PREFIX + record['recipe']['meson_target']
            text = root.read_text()
            if not text.endswith(old_suffix):
                raise ValueError('Generated Meson suffix mismatch')
            root.write_text(text[:-len(old_suffix)] + MESON_PREFIX + MESON_TARGET)
            for name in ('frontend.c', 'frontend.h'):
                shutil.copyfile(port / name, source / 'prospero-zink' / name)
            record['recipe'] = recipe
            record['patched_files'] = {name: sha(source / name) for name in record['patched_files']}
            stamp.write_text(json.dumps(record, indent=2) + '\n')
    else:
        export_archive(archive, source, pins['archive'])
        touched = {'meson.build'}
        for patch in patches:
            run('git', 'apply', '--check', patch, cwd=source)
            run('git', 'apply', patch, cwd=source)
            touched.update(line[6:] for line in patch.read_text().splitlines() if line.startswith('+++ b/'))
        for patch in sorted((ROOT / 'client/ports/mesa').glob('*.patch')):
            directory = 'src/amd/vulkan' if patch.name.startswith('0010-') else 'src/vulkan/wsi'
            run('git', 'apply', '--check', '--directory=' + directory, patch, cwd=source)
            run('git', 'apply', '--directory=' + directory, patch, cwd=source)
            touched.update(directory + '/' + line[6:] for line in patch.read_text().splitlines() if line.startswith('+++ b/'))
        for header in sorted((ROOT / 'client/ports/mesa').glob('*.h')):
            name = 'src/vulkan/wsi/' + header.name
            shutil.copyfile(header, source / name)
            touched.add(name)
        private = source / 'prospero-zink'
        private.mkdir()
        for name in ('frontend.c', 'frontend.h'):
            shutil.copyfile(port / name, private / name)
            touched.add('prospero-zink/' + name)
        with (source / 'meson.build').open('a') as out:
            out.write(MESON_PREFIX + MESON_TARGET)
        record = {'recipe': recipe, 'original_inventory': archive_inventory(archive),
                  'patched_files': {name: sha(source / name) for name in sorted(touched)}}
        stamp.write_text(json.dumps(record, indent=2) + '\n')
    return work, source, record


def build(args):
    work, source, record = prepare_sources(args)
    # Share the already pinned zlib source/adapter inputs with the old OSMesa
    # builder, not its GL implementation. Explicitly forbid Meson downloads.
    zlib_rows = json.loads((ROOT / 'client/ports/opengl/mesa-sources.json').read_text())['dependencies']
    package_cache = source / 'subprojects/packagecache'
    package_cache.mkdir(exist_ok=True)
    for row in zlib_rows:
        cached = ROOT / '.tools' / row['file']
        if not cached.exists():
            if args.offline:
                raise FileNotFoundError('Missing pinned zlib input: ' + str(cached))
            urllib.request.urlretrieve(row['url'], cached)
        if cached.stat().st_size != row['size'] or sha(cached) != row['sha256']:
            raise ValueError('Pinned zlib input mismatch: ' + row['file'])
        if (package_cache / row['file']).exists() and sha(package_cache / row['file']) != row['sha256']:
            raise ValueError('Modified zlib package-cache input: ' + row['file'])
        if not (package_cache / row['file']).exists():
            shutil.copyfile(cached, package_cache / row['file'])
    meson = args.meson.resolve()
    if not meson.is_file():
        raise FileNotFoundError('Prepare graphics Meson environment or provide --meson')
    llvm = args.llvm_home.resolve()
    for tool in ('clang', 'clang++', 'llvm-ar', 'llvm-nm'):
        if not (llvm / 'bin' / tool).is_file():
            raise FileNotFoundError('Incomplete --llvm-home: ' + tool)
    ninja = executable('ninja')
    bison = executable('bison', override=args.bison)
    version = subprocess.check_output([bison, '--version'], text=True).splitlines()[0]
    match = re.search(r'\b(\d+)\.(\d+)', version)
    if not match or int(match[1]) < 3:
        raise ValueError('GLSL requires Bison 3+; select --bison explicitly (found ' + version + ')')
    clc = args.clc_dir.resolve()
    env = dict(os.environ, PATH=os.pathsep.join(map(str, [Path(bison).parent, clc, llvm / 'bin', meson.parent])) + os.pathsep + os.environ.get('PATH', ''),
               LLVM_CONFIG=str(llvm / 'bin/llvm-config'))
    target = work / ('host' if args.host else 'ps5')
    native_tools = work / 'native-tools.ini'
    native_tools.write_text('[binaries]\nbison = ' + repr(bison) + '\n')
    common = ['-Dgallium-drivers=zink', '-Dplatforms=', '-Dopengl=true', '-Degl=disabled',
              '-Dglx=disabled', '-Dgbm=disabled', '-Dgles1=disabled', '-Dgles2=disabled',
              '-Dllvm=disabled', '-Damd-use-llvm=false', '-Dbuild-tests=false',
              '-Dvalgrind=disabled', '-Dlibunwind=disabled', '-Dzstd=disabled',
              '-Dxmlconfig=disabled', '-Dtools=', '-Dvideo-codecs=', '-Dexpat=disabled',
              '-Dshader-cache=enabled', '-Dvulkan-layers=', '-Dmesa-clc=system',
              '-Dbuildtype=debugoptimized', '-Db_ndebug=true', '-Ddefault_library=static',
              '--wrap-mode=nodownload',
              '--native-file', str(native_tools)]
    flags = ['-DPS5_ZINK_FRONTEND', '-DPS5_ZINK_STATIC_VULKAN', '-DPS5_ZINK_EMULATED_TLS', '-gline-tables-only']
    if not args.host:
        sdk = args.sdk.resolve()
        cross = work / 'cross.ini'
        flags += ['-march=x86-64', '-msse2', '-mno-avx', '-mno-avx2', '-mno-fma']
        cross.write_text('[binaries]\nbison = ' + repr(bison) + '\n' + '\n'.join(name + ' = ' + repr(str(sdk / 'bin' / tool)) for name, tool in (
            ('c', 'prospero-clang'), ('cpp', 'prospero-clang++'), ('ar', 'prospero-ar'),
            ('strip', 'prospero-strip'), ('pkg-config', 'prospero-pkg-config'))) +
            "\n[host_machine]\nsystem = 'freebsd'\ncpu_family = 'x86_64'\ncpu = 'x86_64'\nendian = 'little'\n" +
            '\n[built-in options]\nc_args = ' + repr(flags) + '\ncpp_args = ' + repr(flags) +
            '\n[properties]\nneeds_exe_wrapper = true\n')
        common += ['--cross-file', str(cross), '-Dvulkan-drivers=amd', '-Dradv-winsys=ps5',
                   '-Dzlib=enabled', '--force-fallback-for=zlib',
                   '-Dradv-build-id=' + record['recipe']['mesa']['commit']]
    else:
        if not args.host_vulkan:
            raise ValueError('--host requires --host-vulkan with an explicit real ICD entry wrapper')
        env.update(CC=str(llvm / 'bin/clang'), CXX=str(llvm / 'bin/clang++'))
        if os.uname().sysname == 'Darwin':
            # MoltenVK's convenience header otherwise defines these *after*
            # vulkan.h's include guard, losing real platform PFN declarations.
            flags += ['-DVK_USE_PLATFORM_MACOS_MVK', '-DVK_USE_PLATFORM_METAL_EXT']
        common += ['-Dvulkan-drivers=', '-Dzlib=enabled', '-Dc_args=' + ' '.join(flags),
                   '-Dcpp_args=' + ' '.join(flags), '-Dc_link_args=' + str(args.host_vulkan.resolve()),
                   '-Dcpp_link_args=' + str(args.host_vulkan.resolve())]
        if args.moltenvk_dir:
            common += ['-Dmoltenvk-dir=' + str(args.moltenvk_dir.resolve())]
    configuration = {'options': common, 'llvm': str(llvm), 'bison': bison, 'sdk': str(args.sdk.resolve())}
    config_stamp = target / 'prospero-config.json'
    if not (target / 'build.ninja').exists():
        run(meson, 'setup', target, source, *common, env=env)
        config_stamp.write_text(json.dumps(configuration, indent=2) + '\n')
    elif not config_stamp.exists() or json.loads(config_stamp.read_text()) != configuration:
        run(meson, 'setup', '--reconfigure', '--clearcache', target, source, *common, env=env)
        config_stamp.write_text(json.dumps(configuration, indent=2) + '\n')
    bundle = 'libprosperozink.dylib' if args.host else 'libprosperozink.so'
    if args.host:
        run(ninja, '-C', target, '-j', args.jobs, bundle, env=env)
        result = target / bundle
    else:
        # Build the exact archive/object dependency closure expressed by Meson,
        # not its shared ELF. RADV and GL use these same utility/compiler objects.
        commands = subprocess.check_output([ninja, '-C', str(target), '-t', 'commands', bundle], text=True, env=env).splitlines()
        inputs = list(dict.fromkeys(token for token in shlex.split(commands[-1]) if token.endswith(('.a', '.o'))))
        inputs = [token for token in inputs if (target / token).exists() or not Path(token).is_absolute()]
        radv = 'src/amd/vulkan/libvulkan_radeon.a'
        run(ninja, '-C', target, '-j', args.jobs, *inputs, radv, env=env)
        result = target / 'zink-radv-unscoped.o'
        lld = Path(executable('ld.lld', override=args.lld))
        # This Mesa pin's RADV archive already embeds NIR/SPIR-V/utilities.
        # Keep that driver whole, then extract only GL/Zink's additional objects
        # through normal archive resolution. Never allow duplicate definitions.
        components = list(dict.fromkeys(inputs))
        roots = ['ps5zink_create', 'ps5zink_make_current', 'ps5zink_get_current',
                 'ps5zink_destroy', 'ps5zink_resize', 'ps5zink_swap_buffers',
                 'ps5zink_swap_interval', 'ps5zink_get_proc_address', 'ps5zink_error']
        run(lld, '-r', *['--undefined=' + name for name in roots], '--whole-archive', radv,
            '--no-whole-archive', '--start-group', *components, '--end-group',
            '-o', result, cwd=target, env=env)
        exports = subprocess.check_output([str(llvm / 'bin/llvm-nm'), '--defined-only', '--extern-only', str(result)], text=True)
        for name in ('ps5zink_create', 'ps5zink_make_current', 'ps5zink_get_proc_address', 'vk_icdGetInstanceProcAddr'):
            if not any(line.split()[-1] == name for line in exports.splitlines() if line.split()):
                raise ValueError('Missing genuine component export: ' + name)
    audit = {'scope': 'Opt-in private GL state-tracker/Zink component; no app/console acceptance',
             'source': record, 'host': args.host, 'output_sha256': sha(result),
             'console': 'Pending context, presentation and original-game tests',
             'integration': 'Unscoped component; existing graphics allocator/sync/constructor scoping and one-copy replacement required before app link'}
    result.with_suffix('.json').write_text(json.dumps(audit, indent=2) + '\n')
    print('Built genuine Zink component:', result, flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--work-dir', type=Path, default=ROOT / 'build/zink-native')
    parser.add_argument('--sdk', type=Path, default=ROOT / '.tools/graphics-sdk')
    parser.add_argument('--meson', type=Path, default=ROOT / '.tools/graphics-python/bin/meson')
    parser.add_argument('--clc-dir', type=Path, default=ROOT / 'build/graphics-clc-bin')
    parser.add_argument('--llvm-home', type=Path, required=True)
    parser.add_argument('--lld', help='ld.lld executable; otherwise use PATH/LLVM_HOME discovery')
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--bison', help='Bison 3+ executable; system Apple Bison 2.3 is unsupported')
    parser.add_argument('--host', action='store_true')
    parser.add_argument('--host-vulkan', type=Path)
    parser.add_argument('--moltenvk-dir', type=Path)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        parser.error('--jobs must be 1..32')
    build(args)


if __name__ == '__main__':
    main()
