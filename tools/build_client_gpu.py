#!/usr/bin/env python3
"""Scope the graphics dependency's compatibility providers to its own objects.

This consumer integration keeps the passing JVM allocator/thread/DNS definitions
intact. It does not alter game bytecode, the runtime SDK or downloaded sources.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin');LLD=Path('/opt/homebrew/opt/lld/bin/ld.lld')
def run(*args,**kw):subprocess.run(list(map(str,args)),check=True,**kw)
def build(runtime,java_home,wsi_diagnostics=False):
 out=ROOT/'build/client-gpu';out.mkdir(exist_ok=True);sdk=ROOT/'.tools/graphics-sdk';driver=ROOT/'.tools/ps5-vulkan'
 # The native003 build already supplies a verified recipe with a real target
 # compiler-runtime archive path, independent of Linux host directory layout.
 flags=subprocess.check_output(['bash','-c','source "$1"; radv_link_recipe "$2" "$3" "$4"; printf "%s\\n" "${radv_link_flags[@]}"','radv-flags',str(ROOT/'build/client-graphics/radv-link-host.sh'),str(driver),str(sdk),str(ROOT/'build/graphics-radv/src/amd/vulkan/libvulkan_radeon.a')],env=dict(os.environ,LLVM_CONFIG=str(LLVM/'llvm-config')),text=True).splitlines()
 compatibility={};wraps=[]
 for flag in flags:
  if flag.startswith('--defsym='):
   a,b=flag.removeprefix('--defsym=').split('=');compatibility[a]=b
  if flag.startswith('--wrap='):wraps.append(flag.removeprefix('--wrap='))
 radv_archive=ROOT/'build/graphics-radv/src/amd/vulkan/libvulkan_radeon.a';wsi_audit=None
 if wsi_diagnostics:
  from build_wsi_diagnostics import build as build_wsi
  radv_archive,wsi_audit=build_wsi()
 platform=out/'platform-raw.o';mesa=out/'radv-raw.o'
 run(LLD,'-r','--whole-archive',sdk/'target/lib/libps5platform.a','--no-whole-archive','-o',platform)
 run(LLD,'-r','--whole-archive',radv_archive,'--no-whole-archive','-o',mesa)
 text=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only','--extern-only',str(platform)],text=True)
 definitions={line.split()[-1]for line in text.splitlines()if len(line.split())==3}
 prefix={name:'clientgpu_'+name for name in definitions}
 # All platform-owned globals are isolated, including the wrapped allocator,
 # thread records, TLS destructor state and helpers. Mesa libc references bind
 # to those actual providers; no global --defsym or --wrap policy is changed.
 binding={name:prefix[target]for name,target in compatibility.items()if target in prefix}
 for name in wraps:
  target='__wrap_'+name
  if target in prefix:binding[name]=prefix[target]
 pmap=dict(prefix);pmap.update(binding)
 # SDK platform internals retain their original libc string ownership. Mesa
 # and graphics callers duplicate through the same heap as their scoped free.
 binding.update({'strdup':'clientgpu_strdup','strndup':'clientgpu_strndup'})
 # Real calls underneath its wrappers intentionally keep the original OS/SDK
 # behavior. Core JVM wraps still map these __real_* references in the final link.
 for name in ['fclose','fflush','posix_memalign','malloc_usable_size','pthread_detach']:
  pmap['__real_'+name]=name
 # Mesa and the JVM each include their own zlib. Scope every actual Mesa
 # zlib global, including internal shared globals, without changing either source.
 zobjects=sorted((ROOT/'build/graphics-radv/subprojects/zlib-1.3.1/libz.a.p').glob('*.o'))
 assert zobjects
 ztext=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only','--extern-only',*map(str,zobjects)],text=True)
 zsymbols={line.split()[-1]for line in ztext.splitlines()if len(line.split())==3}
 zmap={name:'clientgpu_zlib_'+name for name in zsymbols}
 binding.update(zmap)
 mesa_sync={name:'clientgpu_'+name.removeprefix('pthread_') for name in ['pthread_cond_init','pthread_cond_destroy','pthread_cond_signal','pthread_cond_broadcast','pthread_cond_wait','pthread_cond_timedwait','pthread_condattr_init','pthread_condattr_setclock','pthread_condattr_destroy']}
 mesa_mutex={name:'clientgpu_'+name.removeprefix('pthread_') for name in ['pthread_mutex_init','pthread_mutex_destroy','pthread_mutex_lock','pthread_mutex_unlock','pthread_mutex_trylock','pthread_mutex_timedlock']}
 for obj,mapping in [(platform,pmap),(mesa,{**binding,**mesa_sync,**mesa_mutex})]:
  path=out/(obj.stem+'-renames.txt');path.write_text(''.join(a+' '+b+'\n'for a,b in sorted(mapping.items())))
  run(LLVM/'llvm-objcopy','--redefine-syms='+str(path),obj)
 # CPU feature detection uses the genuine compiler-rt implementation, initialized
 # with the graphics library after VM creation rather than during title startup.
 cpu=out/'cpu-model.o'
 run(LLVM/'clang','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include','-march=x86-64','-mno-avx','-mno-avx2','-mno-fma','-O2','-I'+str(ROOT/'build'),'-c',ROOT/'build/graphics-cpu-model.c','-o',cpu)
 scoped=out/'libgraphics-platform.a'
 run(LLVM/'llvm-objcopy','--redefine-syms='+str(out/'platform-raw-renames.txt'),sdk/'target/lib/libps5platform.a',scoped)
 strings=out/'graphics-string-alloc.o'
 run(LLVM/'clang','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',ROOT/'client/gpu/string_alloc.c','-o',strings)
 conditions=out/'graphics-condition-reserve.o'
 run(LLVM/'clang','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',ROOT/'client/gpu/condition_reserve.c','-o',conditions)
 worker=out/'graphics-present-worker.o'
 run(LLVM/'clang','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',ROOT/'client/gpu/present_worker.c','-o',worker)
 merged=out/'graphics-support.o'
 core_sdk=runtime/'.tools/native-sdk/ps5-payload-sdk'
 for name in ['libc++.a','libc++abi.a','libunwind.a']:
  assert (core_sdk/'target/lib'/name).read_bytes()==(sdk/'target/lib'/name).read_bytes(),'Shared C++ ABI mismatch'
 run(LLD,'-r','--undefined=clientgpu_ps5_fp_ieee','--undefined=clientgpu_ps5___cxa_thread_atexit_impl',mesa,scoped,cpu,strings,conditions,worker,'--start-group',*[core_sdk/'target/lib'/n for n in ['libc++.a','libc++abi.a','libunwind.a']],'--end-group','-o',merged)
 sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(merged)],text=True)
 names=sorted(set(re.findall(r'\]\s+(\.(?:init_array|ctors)(?:\.\S+)?)\s',sections)))
 assert names,'Expected real native graphics constructors'
 options=[]
 priorities={}
 for name in names:
  suffix=name.rsplit('.',1)[-1]
  priority=(65535-int(suffix)if name.startswith('.ctors.')else int(suffix))if suffix.isdigit()else 65535
  renamed='.data.rel.ro.clientgpu.init_array.'+f'{priority:05d}'+name
  priorities[name]=priority;options+=['--rename-section',name+'='+renamed]
 run(LLVM/'llvm-objcopy',*options,merged)
 assert not re.search(r'\]\s+\.(?:init_array|ctors)(?:\s|\.)',subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(merged)],text=True))
 # The regular resident registry sees only the constructor-free JNI bridge.
 # Its OnLoad explicitly runs the retained graphics constructor array once.
 bridge=out/'gpu-bridge.o';headers=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_include/java.base'
 run(LLVM/'clang',*(['-DPS5_GPU_EARLY_VIDEOOUT=1']if wsi_diagnostics else []),'-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-target','x86_64-sie-ps5','-march=x86-64','-mno-avx','-mno-avx2','-mno-fma','-fvisibility-nodllstorageclass=default','-isysroot',sdk,'-isystem',sdk/'target/include','-I'+str(ROOT/'.tools/PS5_Mesa/include'),'-I'+str(headers),'-I'+str(headers/'freebsd'),'-c',ROOT/'client/gpu/bridge.c','-o',bridge)
 audit={'scope':'Consumer-owned scoped graphics dependency providers; JVM process-wide allocation/thread/DNS behavior retained','provider_definitions':prefix,'graphics_bindings':binding,'constructors':{'sections':names,'normalized_priorities':priorities,'execution':'pthread_once before launcher RADV use or JNI_OnLoad; retained functions, no automatic startup execution'},'callback':'The SDK C++ ABI optional TLS destructor callback resolves to the real scoped platform provider for this combined title','mesa_sync_bindings':mesa_sync,'mesa_mutex_bindings':mesa_mutex,'mutex_reserve_source_sha256':hashlib.sha256((ROOT/'client/gpu/mutex_reserve.inc').read_bytes()).hexdigest(),'present_worker_source_sha256':hashlib.sha256((ROOT/'client/gpu/present_worker.c').read_bytes()).hexdigest(),'condition_reserve_source_sha256':hashlib.sha256((ROOT/'client/gpu/condition_reserve.c').read_bytes()).hexdigest(),'string_allocator_source_sha256':hashlib.sha256((ROOT/'client/gpu/string_alloc.c').read_bytes()).hexdigest(),'objects_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [merged,bridge,strings,conditions,worker]},'console':'pending'}
 if wsi_audit is not None:audit['wsi_diagnostics']=wsi_audit;audit['early_videoout_owner']='Same WSI output initialized after GPU constructors,before original Main;negative result fails JNI_OnLoad;no external handle/handoff'
 (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 print('Built scoped graphics support and resident JNI bridge',out)
 return merged,bridge,audit
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',required=True,type=Path);p.add_argument('--java-home',required=True,type=Path);a=p.parse_args();build(a.runtime_workspace.resolve(),a.java_home)
