#!/usr/bin/env python3
"""Build the vendored kit against the existing consumer graphics ABI."""
import hashlib, json, re, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LLVM=Path('/opt/homebrew/opt/llvm/bin')
KIT=ROOT/'client/launcher/toolkit'
UNITS=['gfx/renderer.cpp','gfx/triangulate.cpp','gfx/draw_list.cpp','gfx/font.cpp','gfx/vk/vk_renderer.cpp','ui/widgets.cpp','ui/theme.cpp','ui/glyphs.cpp','ui/pixel_font.cpp','ui/components/component.cpp','ui/components/button.cpp','ui/components/card.cpp','ui/components/grid.cpp','ui/components/dialog.cpp','ui/components/progress.cpp','ui/components/badge.cpp','ui/components/tooltip.cpp','ui/components/overlay.cpp']

def dispatch(work):
    texts=(KIT/'src/gfx/vk/vk_renderer.cpp').read_text()+(ROOT/'client/launcher/toolkit_surface.hpp').read_text()
    names=sorted(set(re.findall(r'\bvk([A-Z]\w*)\(',texts)))
    instance={'DestroyInstance','EnumeratePhysicalDevices','GetPhysicalDeviceMemoryProperties','GetPhysicalDeviceQueueFamilyProperties','GetPhysicalDeviceProperties','CreateDevice','GetDeviceProcAddr'}
    names=sorted(set(names)|instance)
    out=['#pragma once','#define VK_NO_PROTOTYPES','#include <vulkan/vulkan.h>','extern "C" PFN_vkVoidFunction vk_icdGetInstanceProcAddr(VkInstance,const char*);','namespace prospero_ui_dispatch {']
    out += ['inline PFN_vk'+n+' fn_'+n+'=nullptr;' for n in names]
    out += ['inline bool toolkit_load_global(){fn_CreateInstance=reinterpret_cast<PFN_vkCreateInstance>(vk_icdGetInstanceProcAddr(nullptr,"vkCreateInstance"));return fn_CreateInstance!=nullptr;}','inline bool toolkit_load_instance(VkInstance i){']
    out += ['fn_'+n+'=reinterpret_cast<PFN_vk'+n+'>(vk_icdGetInstanceProcAddr(i,"vk'+n+'"));if(!fn_'+n+')return false;' for n in names if n in instance]
    out += ['return true;}','inline bool toolkit_load_device(VkDevice d){']
    out += ['fn_'+n+'=reinterpret_cast<PFN_vk'+n+'>(fn_GetDeviceProcAddr(d,"vk'+n+'"));if(!fn_'+n+')return false;' for n in names if n not in instance and n!='CreateInstance']
    out += ['return true;}','}','using prospero_ui_dispatch::toolkit_load_global;','using prospero_ui_dispatch::toolkit_load_instance;','using prospero_ui_dispatch::toolkit_load_device;']
    out += ['#define vk'+n+' prospero_ui_dispatch::fn_'+n for n in names]
    (work/'toolkit_dispatch.hpp').write_text('\n'.join(out)+'\n')

def build(work,runtime=None,bindings=None):
    work.mkdir(parents=True,exist_ok=True)
    pin=json.loads((KIT/'upstream.json').read_text())
    for path,sha in pin['sha256'].items():
        assert hashlib.sha256((KIT/path).read_bytes()).hexdigest()==sha, 'Upstream source changed: '+path
    dispatch(work)
    flags=['-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-exceptions','-fno-rtti','-ffunction-sections','-fdata-sections','-I'+str(KIT/'src'),'-I'+str(work),'-I'+str(ROOT/'.tools/PS5_Mesa/include'),'-include',str(work/'toolkit_dispatch.hpp')]
    if runtime:
        sdk=runtime/'.tools/native-sdk/ps5-payload-sdk'
        flags+=['-target','x86_64-sie-ps5','-fPIC','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include/c++/v1'),'-isystem',str(sdk/'target/include'),'-fno-stack-protector','-fno-plt','-femulated-tls']
    objects=[]
    for unit in UNITS:
        obj=work/(unit.replace('/','_')+'.o')
        subprocess.run([str(LLVM/'clang++'),*flags,'-c',str(KIT/'src'/unit),'-o',str(obj)],check=True)
        if runtime:
            sections=subprocess.check_output([str(LLVM/'llvm-readelf'),'-SW',str(obj)],text=True)
            names=sorted(set(re.findall(r'\]\s+(\.(?:init_array|ctors)(?:\.\S+)?)\s',sections)))
            for name in names:
                suffix=name.rsplit('.',1)[-1]
                priority=(65535-int(suffix) if name.startswith('.ctors.') else int(suffix)) if suffix.isdigit() else 65535
                subprocess.run([str(LLVM/'llvm-objcopy'),'--rename-section',name+'=.data.rel.ro.clientui.init_array.'+str(priority).zfill(5)+name,str(obj)],check=True)
        if bindings:
            mapping=work/'toolkit-bindings.txt';mapping.write_text(''.join(k+' '+v+'\n' for k,v in sorted(bindings.items())))
            subprocess.run([str(LLVM/'llvm-objcopy'),'--redefine-syms='+str(mapping),str(obj)],check=True)
        objects.append(obj)
    audit={'revision':pin['revision'],'local_upstream_patches':[],
           'backend':'hui::gfx::VkRenderer','frames_in_flight':1,
           'display':'Existing native VideoOut via completed offscreen RGBA8 readback',
           'objects_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
           'graphics_bindings':bindings or {},'automatic_constructors':False if runtime else 'host platform initialization',
           'audio_backend_linked':False,'sample_application_linked':False,'console':'PENDING exact096'}
    (work/'launcher-toolkit-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return objects

def package_sources(java):
    dest=java/'launcher-toolkit';shutil.copytree(KIT,dest,dirs_exist_ok=True)
    for name in ['toolkit_surface.hpp','toolkit_canvas.hpp','toolkit_effects.hpp','palette.hpp','native_menu.hpp','navigation.hpp','haptics.hpp','branding_logo.hpp','instance_icons.hpp','login_qr.hpp']:
        shutil.copyfile(ROOT/'client/launcher'/name,dest/name)
    for name in ['build_launcher_toolkit.py','prepare_launcher_toolkit.py']:
        shutil.copyfile(ROOT/'tools'/name,dest/name)
