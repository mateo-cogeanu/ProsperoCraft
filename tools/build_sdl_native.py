#!/usr/bin/env python3
"""Build the pinned public SDL3 PS5 video/input port as a resident dependency."""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];LLVM=Path('/opt/homebrew/opt/llvm/bin')
def build(runtime):
    port=ROOT/'client/ports/sdl';lock=json.loads((port/'sources.json').read_text());cache=ROOT/'.tools/sdl3-src';out=ROOT/'build/sdl3-native';source=ROOT/'build/sdl-src'
    if not cache.exists():subprocess.run(['git','clone','--no-checkout',lock['sdl']['repository'],str(cache)],check=True)
    if subprocess.run(['git','-C',str(cache),'cat-file','-e',lock['sdl']['commit']],capture_output=True).returncode:subprocess.run(['git','-C',str(cache),'fetch','--depth','1','origin',lock['sdl']['commit']],check=True)
    # Only our ignored generated source export is replaced; the cache remains intact.
    shutil.rmtree(source,ignore_errors=True);source.mkdir(parents=True)
    with tempfile.TemporaryFile() as archive:
        subprocess.run(['git','-C',str(cache),'archive',lock['sdl']['commit']],stdout=archive,check=True);archive.seek(0)
        subprocess.run(['tar','-x','-C',str(source)],stdin=archive,check=True)
    subprocess.run(['git','apply','--unsafe-paths','--directory='+str(source),str(port/'0001-register-ps5.patch')],check=True)
    subprocess.run(['git','apply','--unsafe-paths','--directory='+str(source),str(port/'0002-ps5-rwlock.patch')],check=True)
    subprocess.run(['git','apply','--unsafe-paths','--directory='+str(source),str(port/'0003-ps5-native-sync-reserve.patch')],check=True)
    subprocess.run(['git','apply','--unsafe-paths','--directory='+str(source),str(port/'0004-ps5-thread-error-storage.patch')],check=True)
    sdk=ROOT/'.tools/graphics-sdk';out.mkdir(exist_ok=True)
    toolchain=out/'ps5.cmake';toolchain.write_text('set(CMAKE_SYSTEM_NAME FreeBSD)\nset(CMAKE_SYSTEM_VERSION 9)\nset(CMAKE_SYSTEM_PROCESSOR x86_64)\nset(CMAKE_CROSSCOMPILING TRUE)\nset(PS5 TRUE)\nset(CMAKE_C_COMPILER '+str(LLVM/'clang')+')\nset(CMAKE_C_COMPILER_TARGET x86_64-sie-ps5)\nset(CMAKE_AR '+str(LLVM/'llvm-ar')+')\nset(CMAKE_RANLIB '+str(LLVM/'llvm-ranlib')+')\nset(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)\n')
    flags='-isysroot '+str(sdk)+' -isystem '+str(sdk/'target/include')+' -fvisibility-nodllstorageclass=default -march=x86-64 -mno-avx -mno-avx2 -mno-fma -fno-stack-protector'
    args=['cmake','-S',str(source),'-B',str(out),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_C_FLAGS='+flags,'-DSDL_PS5_PORT_DIR='+str(port),'-DSDL_PS5_PLATFORM_DIR='+str(port),'-DSDL_UNIX_CONSOLE_BUILD=ON','-DSDL_STATIC=ON','-DSDL_VULKAN=ON','-DSDL_AUDIO=ON','-DSDL_ALSA=OFF','-DSDL_PULSEAUDIO=OFF','-DSDL_PIPEWIRE=OFF','-DSDL_OSS=OFF','-DSDL_JACK=OFF','-DSDL_SNDIO=OFF','-DSDL_DISKAUDIO=OFF','-DSDL_DUMMYAUDIO=OFF']
    for option in ['SHARED','TEST_LIBRARY','TESTS','EXAMPLES','INSTALL','HAPTIC','SENSOR','CAMERA','GPU','RENDER','OPENGL','OPENGLES','OPENVR','X11','WAYLAND','KMSDRM','RPI','ROCKCHIP','VIVANTE','OFFSCREEN','DUMMYVIDEO','DBUS','IBUS','LIBURING','LIBUDEV','HIDAPI','HIDAPI_LIBUSB','VIRTUAL_JOYSTICK','DEPS_SHARED','DLOPEN_NOTES','DIALOG','TRAY','POWER','ASSEMBLY','AVX','AVX2','AVX512F']:
        args.append('-DSDL_'+option+'=OFF')
    # Static try-compile checks cannot prove target libc export availability.
    # Use SDL's own implementations for APIs absent from the actual link.
    args += ['-DHAVE_WCSNLEN=OFF','-DHAVE_WCSLCPY=OFF','-DHAVE_WCSLCAT=OFF','-DHAVE_NL_LANGINFO=OFF']
    subprocess.run(args,check=True);subprocess.run(['cmake','--build',str(out),'-j','6'],check=True)
    platform=out/'platform-input.o';subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fno-stack-protector','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-I'+str(port),'-c',str(port/'platform-input.c'),'-o',str(platform)],check=True)
    hid=out/'physical-hid.o';subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fno-stack-protector','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-I'+str(port),'-c',str(port/'ps5_hid_native.c'),'-o',str(hid)],check=True)
    events=out/'controlify-events.o';subprocess.run([str(LLVM/'clang'),'-target','x86_64-sie-ps5','-O2','-fPIC','-fno-stack-protector','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-I'+str(source/'include'),'-c',str(port/'ps5_controlify_events.c'),'-o',str(events)],check=True)
    obj=out/'resident-sdl.o';subprocess.run(['/opt/homebrew/opt/lld/bin/ld.lld','-r','--whole-archive',str(out/'libSDL3.a'),'--no-whole-archive',str(platform),str(hid),str(events),'-o',str(obj)],check=True)
    tls_symbols=subprocess.check_output([str(LLVM/'llvm-nm'),str(obj)],text=True)
    assert ' T prospero_sdl_tls_preinit' in tls_symbols,'PS5 TLS guard inactive'
    sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(obj)],text=True);assert '.init_array'not in sections and '.ctors'not in sections,'Unexpected automatic SDL constructors'
    audit={'sdl':lock['sdl'],'reference':lock['reference'],'profile':lock['profile'],'port_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(port.iterdir())if p.is_file()},'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'scope':'Actual SDL3 core/events/PS5 video/Vulkan/joystick driver; primary DualSense actuator-only SDL audio and native joystick gyro; game speaker audio remains OpenAL; native compatible rumble and translated Controlify adaptive-trigger effects;LED/impulse-trigger-rumble/process spawn unsupported; no game modifications','console':'pending'}
    (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');return obj
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args();print(build(a.runtime_workspace))
