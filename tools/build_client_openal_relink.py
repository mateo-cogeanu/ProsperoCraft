#!/usr/bin/env python3
"""Preserve exact native link inputs and OpenAL source for a frozen LGPL-linked app."""
from pathlib import Path
import argparse,json,subprocess,shutil,hashlib,zipfile,tarfile,io
ROOT=Path(__file__).resolve().parents[1]
def export_consumer_bootstrap(kit,variant):
 # Every local include needed by the thin wrapper travels with corresponding source.
 if variant not in {p.name for p in (ROOT/'client').iterdir() if p.is_dir() and (p/'bootstrap.cpp').is_file()}:raise ValueError('Unknown bootstrap variant')
 shutil.copytree(ROOT/'client/bootstrap',kit/'consumer-source/client/bootstrap',dirs_exist_ok=True)
 shutil.copytree(ROOT/'client'/variant,kit/'consumer-source/client'/variant,dirs_exist_ok=True)

def build(runtime,output,variant="native_bootstrap",version="01.000.026",tested_source="4191ea21b7206367fd0749762f4fff89cf6f9e43"):
 number=version.rsplit(".",1)[-1]
 output.mkdir(parents=True,exist_ok=True);work=ROOT/('build/client-'+variant+'-probe');sdk=runtime/'.tools/native-sdk/ps5-payload-sdk';native=runtime/'.tools/native-app/tooling/native';kit=output/'relink-kit';kit.mkdir(exist_ok=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={};entries=[]
 def keep(p):
  p=Path(p).resolve()
  if str(p)in files:return files[str(p)]
  rel='inputs/'+f'{len(files):03d}-'+p.name;target=kit/rel;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);files[str(p)]=rel;entries.append({'path':rel,'sha256':sha(target),'bytes':target.stat().st_size});return rel
 flags=[json.loads(line)for line in (work/'combined-link.rsp').read_text().splitlines()]
 # Reproduce the SDK driver's actual ld.lld arguments without a host-specific SDK wrapper.
 args=['-m','elf_x86_64','-pie','--eh-frame-hdr','-z','max-page-size=0x4000','-mllvm','-emulated-tls','-T',keep(work/'gpu-probe.ld'),'--eh-frame-hdr','--version-script',keep(native/'app-symbols.map'),'--version-script',keep(work/'gpu-abi-local.map'),'-e','_start','-o','{OUTPUT}']
 # Toolkit objects precede the application objects in the actual startup link.
 # Preserve the audited build order and reject stale/mismatched inputs.
 toolkit_audit=work/'launcher-toolkit-audit.json'
 if variant=='startup' and toolkit_audit.exists():
  for name,digest in json.loads(toolkit_audit.read_text())['objects_sha256'].items():
   obj=work/name
   assert sha(obj)==digest,'Toolkit relink input mismatch: '+name
   args.append(keep(obj))
 for name in ['main.o','renderer.o','crt.o','cpp_runtime.o',*(['native-exception-trace.o','native-mutex-trace.o']if variant=='startup' else [])]:args.append(keep(work/name))
 args+=[keep(ROOT/'build/client-graphics/libSceAgc.so'),keep(ROOT/'build/client-graphics/libSceAgcDriver.so')]
 if variant=='startup' and (work/'libSceMouse.so').exists():args.append(keep(work/'libSceMouse.so'))
 for token in flags:args.append(token if token.startswith('-')else keep(token))
 # All libraries are preserved explicitly; discard the build-machine search path.
 args=[token for token in args if not token.startswith('-L')]
 args.insert(0,'-L{LIBRARY_DIR}')
 args+=['--as-needed',*[keep(p)for p in sorted((sdk/'target/lib').glob('*.so'))],'--hash-style=gnu']
 openal_group=keep(runtime/'build/java25/embedded-ps5openal.o');life=keep(ROOT/'build/openal-ps5/lifecycle.o')
 manifest={'app_version':version,'tested_source_commit':tested_source,'original_elf_sha256':sha(work/('bootstrap-'+version+'-symbols.elf')),'arguments':args,'openal_group':openal_group,'openal_lifecycle':life,'files':entries,'llvm':'22.1.7','scope':'Exact relocatable native application/runtime/dependency objects and SDK import declarations;no game JARs or asset objects. Use a compatible scoped OpenAL object from build_openal_native.py for replacement.'}
 (kit/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 shutil.copyfile(ROOT/'tools/relink_client_openal.py',kit/'relink.py')
 shutil.copyfile(ROOT/'tools/build_client_openal_replacement.py',kit/'build_openal_replacement.py')
 shutil.copyfile(ROOT/'build/openal-ps5/provider-bindings.txt',kit/'provider-bindings.txt')
 sourcepin=json.loads((ROOT/'client/ports/openal/sources.json').read_text());data=subprocess.check_output(['git','-C',str(ROOT/'.tools/openal-soft-src'),'archive','--format=tar',sourcepin['commit']]);(kit/'openal-soft-1.25.2-source.tar').write_bytes(data)
 for path in ['client/ports/openal/sources.json','client/ports/openal/lifecycle.c','tools/build_openal_native.py']:
  dest=kit/'consumer-source'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dest)
 export_consumer_bootstrap(kit,variant)
 # Include the exact build-time target headers for rebuilding the LGPL library.
 with tarfile.open(kit/'ps5-sdk-headers.tar','w')as tar:tar.add(ROOT/'.tools/graphics-sdk/target/include',arcname='target/include')
 if variant=='startup':
  # Preserve the actual modified library, not just the historical pristine026 recipe.
  for path in ['client/startup/openal_trace_env.c','client/ports/openal/startup_boundary.hpp','client/ports/openal/ps5_directory.hpp','tools/build_openal_startup_boundaries.py']:
   dest=kit/'consumer-source'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dest)
  with tarfile.open(fileobj=io.BytesIO(data))as tar:tar.extractall(kit/'openal-startup-source',filter='data')
  for unit in ['alc/alc.cpp','core/helpers.cpp']:
   shutil.copyfile(ROOT/'build/openal-startup-boundary-ps5'/Path(unit).name,kit/'openal-startup-source'/unit)
  shutil.copyfile(ROOT/'client/ports/openal/startup_boundary.hpp',kit/'openal-startup-source/alc/startup_boundary.hpp')
  # Header inclusion is local to the patched ALC translation unit.
  patched=kit/'openal-startup-source/alc/alc.cpp'
  patched.write_text('#include "startup_boundary.hpp"\n'+patched.read_text())
  if json.loads((ROOT/'build/openal-startup-boundary-ps5/audit.json').read_text()).get('speaker_backend'):
   for name in ['ps5_backend.cpp','ps5_backend.h','ps5_port_pool.hpp','ps5_audio_mutex.hpp','ps5_mixer_workers.hpp']:
    shutil.copyfile(ROOT/'client/ports/openal'/name,kit/'openal-startup-source/alc/backends'/name)
    dest=kit/'consumer-source/client/ports/openal'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'client/ports/openal'/name,dest)
   cmake=kit/'openal-startup-source/CMakeLists.txt'
   cmake.write_text(cmake.read_text()+'\ntarget_sources(OpenAL PRIVATE alc/backends/ps5_backend.cpp)\ntarget_include_directories(OpenAL PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/alc/backends")\n')
   patched.write_text(patched.read_text().replace('#include "ps5_backend.h"','#include "backends/ps5_backend.h"'))
   for name in ['alc/device.h','alc/context.hpp','al/debug.cpp','core/context.h','al/event.cpp']:
    shutil.copyfile(ROOT/'build/openal-ps5/source'/name,kit/'openal-startup-source'/name)
   shutil.copyfile(ROOT/'client/ports/openal/ps5_mixer_workers.hpp',kit/'openal-startup-source/core/ps5_mixer_workers.hpp')
   shutil.copyfile(ROOT/'client/ports/openal/ps5_audio_mutex.hpp',kit/'openal-startup-source/alc/ps5_audio_mutex.hpp')
   shutil.copyfile(ROOT/'build/openal-ps5/source/core/hrtf.cpp',kit/'openal-startup-source/core/hrtf.cpp')
   shutil.copyfile(ROOT/'client/ports/openal/ps5_audio_mutex.hpp',kit/'openal-startup-source/core/ps5_audio_mutex.hpp')
   shutil.copyfile(ROOT/'client/ports/openal/ps5_directory.hpp',kit/'openal-startup-source/core/ps5_directory.hpp')
   logging=kit/'openal-startup-source/core/logging.cpp'
   logging.write_text('#include "ps5_audio_mutex.hpp"\n'+(ROOT/'build/openal-startup-boundary-ps5/logging.cpp').read_text())
  shutil.copyfile(work/'startup-openal.o',kit/'accepted-startup-openal.o')
  records=kit/'build-record';records.mkdir(exist_ok=True)
  for name in ['config.h','version.h','CMakeCache.txt','toolchain.cmake']:
   path=ROOT/'build/openal-ps5'/name
   if path.exists():
    content=path.read_text().replace(str(ROOT),'{CONSUMER_ROOT}').replace(str(runtime),'{RUNTIME_ROOT}')
    (records/name).write_text(content)
  commands=subprocess.check_output(['ninja','-C',str(ROOT/'build/openal-ps5'),'-t','commands','OpenAL'],text=True)
  (records/'original-commands.txt').write_text(commands.replace(str(ROOT),'{CONSUMER_ROOT}').replace(str(runtime),'{RUNTIME_ROOT}'))
  for name in ['audit.json','alc.cpp','helpers.cpp']:
   shutil.copyfile(ROOT/'build/openal-startup-boundary-ps5'/name,records/name)
  shutil.copyfile(ROOT/'client/ports/openal/startup_boundary.hpp',records/'startup_boundary.hpp')
  manifest['openal_extra_objects']=[keep(work/'startup-openal-trace-env.o')]
  manifest['startup_source']='openal-startup-source'
  manifest['scope']+=' Startup includes modified alc/helpers, bounded scopes and separate getenv shim; replacement OpenAL is combined with that exact shim.'
  (kit/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (kit/'README.txt').write_text('''Client026 OpenAL corresponding-source/relink kit\n\nUnzip this kit. Python3 and LLVM/LLD22.1.7 are needed.\nRun: python3 relink.py --lld /path/to/ld.lld --output rebuilt-symbols.elf\nThis reproduces the tested native ELF from the included exact link objects.\nAll manifest input SHA256s are checked;the unmodified relink must match the recorded ELF.\n\nTo replace the LGPL OpenAL library:extract openal-soft-1.25.2-source.tar,edit it,\nand build a compatible PS5 OpenAL object using build_openal_replacement.py:\npython3 build_openal_replacement.py --source /path/to/edited/source --build-dir /path/to/build --llvm-bin /path/to/llvm/bin --lld /path/to/ld.lld\nThis helper accepts an edited source tree without a pristine-check restriction.\nThe recipe needs the pinned project SDK/scoped graphics provider bindings;the SDK\nheaders are included. The full frozen consumer source and pins are in the release\ntag at https://github.com/mateo-cogeanu/ProsperoCraft.\nBuild-time staging renames .ctors to retained .data.rel.ro.clientopenal.init_array.*\nand binds libc/thread references to the same real scoped graphics providers.\nThe compatible replacement object must preserve the public OpenAL ABI and this\nconstructor contract. Invoke relink.py --openal-object /path/to/new/openal.o.\nThe helper combines it with the included lifecycle object,renames JNI_OnLoad,\nand substitutes only the embedded OpenAL group. All other native inputs stay intact.\n\nConvert the resulting ELF to eboot.bin using the pinned PS5 native packaging tool\nfrom https://github.com/mateo-cogeanu/ps5-java25-homebrew and the frozen packaging\nsource. This remains normal homebrew packaging;no private signing key is needed.\nUse the public app-only ZIP and its provision helper to add your exact original\nclient/Java JARs. No game JARs are in this kit. Source edits/relinks invalidate\nthe console validation of the original026 artifact.\n\nThe original OpenAL COPYING,LICENSE-pffft,BSD-3Clause and bundled MIT/BSD license\nfiles are in the source tar. OpenAL Soft is LGPL-2.0-or-later. Relink objects\nretain their upstream licenses;runtime/dependency pins and notices are in the\nfrozen source and app. This kit does not grant rights to unrelated game data.\n'''.replace('026',number))
 archive=output/('client'+number+'-openal-source-relink.zip')
 if variant=='startup':
  with (kit/'README.txt').open('a')as readme:readme.write('''\nSTARTUP VARIANT ADDENDUM\nThe accepted library differs from pristine upstream: openal-startup-source/\ncontains the exact startup alc.cpp and helpers.cpp changes, plus the local scope header.
If this build enables PS5 speakers, it also includes ps5_backend.cpp/.h and the
CMake recipe to build that backend into OpenAL.\nconsumer-source/client/startup/openal_trace_env.c supplies the explicit game-data\npath and trace setting. Its exact object is retained and automatically linked\nwhen --openal-object replaces the library. To retain the accepted private getenv\nbinding, build from openal-startup-source using build_openal_replacement.py, then:\nllvm-objcopy --redefine-sym getenv=client_startup_openal_getenv /path/to/build/openal.o\npython3 relink.py --lld /path/to/ld.lld --objcopy /path/to/llvm-objcopy --openal-object /path/to/build/openal.o --output modified-symbols.elf\nYou may edit the sources and shim; an edited shim requires updating its manifest\ninput/hash. There is no pristine-source restriction on replacement builds.\naccepted-startup-openal.o is the exact already-staged library before lifecycle/\nshim grouping; it also exercises the replacement path against the accepted ELF.\nNo game assets are included. Provision BOTH JARs and all asset objects using\nprovision_client_menu.py and the release manifest before installing.\nMenu confirmation does not establish world gameplay, real speaker output or stability.\n''')
 if variant=='startup' and (work/'assets/java25/launcher-dependencies.json').exists():
  # Native launcher releases install directly; historical pre-provisioning
  # instructions apply only to earlier game-containing startup packages.
  readme=kit/'README.txt';text=readme.read_text()
  text=text.replace('Use the public app-only ZIP and its provision helper to add your exact original\nclient/Java JARs. No game JARs are in this kit.',
                    'Install the public launcher ZIP directly. Its native instance downloader fetches\noriginal game JARs and assets on the console. No game JARs are in this kit.')
  text=text.replace('No game assets are included. Provision BOTH JARs and all asset objects using\nprovision_client_menu.py and the release manifest before installing.\nMenu confirmation does not establish world gameplay, real speaker output or stability.',
                    'No game assets are included. This launcher release needs no desktop provisioning.\nIts on-console downloader verifies original publisher artifacts. Relink/build checks\ndo not establish console lifecycle, speaker output, gameplay or stability.')
  readme.write_text(text)
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted(kit.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(kit))
 return kit,archive
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variant',default='native_bootstrap');p.add_argument('--version',default='01.000.026');p.add_argument('--tested-source',default='4191ea21b7206367fd0749762f4fff89cf6f9e43');a=p.parse_args();print(build(a.runtime_workspace,a.output,a.variant,a.version,a.tested_source))
