#!/usr/bin/env python3
"""Audit temporary game-test artifact and preserved channel artifacts, matching toolkit sources and isolation."""
import hashlib, io, json, subprocess, zipfile
from pathlib import Path
from build_launcher_toolkit import ROOT,LLVM,KIT

sha=lambda b:hashlib.sha256(b).hexdigest()
classes={};binaries={}
for channel in ('temp_gametest',):
    folder=ROOT/('dist/client-startup-'+channel)
    package=folder/'PPSA99874.zip'
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        prefix='PPSA99874/';java=prefix+'assets/java25/'
        param=json.loads(z.read(prefix+'sce_sys/param.json'))
        assert param['attribute3']&0x40
        assert param['contentVersion']=='01.000.141' and param['titleId']=='PPSA99874' and param['downloadDataSize']==4096
        with zipfile.ZipFile(io.BytesIO(z.read(java+'client-probe.jar'))) as jar:
            assert jar.read('prosperocraft-channel.txt').decode().strip()==channel
            assert ('offline-import-public-key.der' in jar.namelist())==(channel=='offline')
            if channel=='offline':assert jar.read('offline-import-public-key.der')==(ROOT/'client/launcher/offline-import-public-key.der').read_bytes()
            classes[channel]={n:sha(jar.read(n)) for n in jar.namelist() if n.endswith('.class')}
        assert not any(n.endswith(('/offline-account.json','.pem','.key','.p12')) or '/game-assets/' in n or '/assets/audio/' in n for n in z.namelist())
        pin=json.loads(z.read(java+'launcher-toolkit/upstream.json'))
        assert pin==json.loads((KIT/'upstream.json').read_text())
        for name,digest in pin['sha256'].items():assert sha(z.read(java+'launcher-toolkit/'+name))==digest
        for name in ('toolkit_surface.hpp','toolkit_canvas.hpp','toolkit_effects.hpp','palette.hpp','native_menu.hpp','navigation.hpp','haptics.hpp'):
            assert z.read(java+'launcher-toolkit/'+name)==(ROOT/'client/launcher'/name).read_bytes()
        audit=json.loads(z.read(java+'launcher-toolkit-audit.json'))
        assert audit['backend']=='hui::gfx::VkRenderer' and audit['frames_in_flight']==1 and audit['automatic_constructors'] is False
        assert not audit['audio_backend_linked'] and not audit['sample_application_linked']
        assert z.read(prefix+'licenses/ProsperoCraft-NOTICE.txt')==(ROOT/'NOTICE').read_bytes()
        for name in ('LICENSE','THIRD_PARTY_NOTICES.md','assets/fonts/Inter-LICENSE.txt'):
            assert z.read(java+'launcher-toolkit/'+name)==(KIT/name).read_bytes()
        binaries[channel]=sha(z.read(prefix+'eboot.bin'))
        assert z.read(java+'ports/oshi-6.9.0-ps5-platform.jar')==(ROOT/'build/client-ports/oshi/oshi-6.9.0-ps5-platform.jar').read_bytes()
        assert z.read(java+'ports/oshi-7.7.2-ps5-provider.jar')==(ROOT/'build/client-ports/oshi7/oshi-7.7.2-ps5-provider.jar').read_bytes()
    assert json.loads((folder/'channel.json').read_text())['package_sha256']==sha(package.read_bytes())
    symbols=subprocess.check_output([str(LLVM/'llvm-nm'),'--defined-only',str(folder/'bootstrap-symbols.elf')],text=True)
    table={l.split()[-1]:int(l.split()[0],16) for l in symbols.splitlines() if len(l.split())==3}
    assert table['__init_array_start']==table['__init_array_end']
    assert table['__client_ui_init_end']-table['__client_ui_init_start']==8
    for marker in ('VkRenderer','PushButton','GridView','Dialog','blit_rgba'):assert marker in symbols
for version in ('085','086','087','088','089'):
    record_path=next((ROOT/'docs/validation').glob('client'+version+'-*-2026-10-27.json'))
    record=json.loads(record_path.read_text())
    for channel,row in record['channels'].items():
        package=ROOT/('dist/candidates/ProsperoCraft-'+channel.capitalize()+'-01.000.'+version)/'PPSA99874.zip'
        assert sha(package.read_bytes())==row['package_sha256'],str(package)
record=json.loads((ROOT/'docs/validation/client084-offline-build-2026-10-27.json').read_text())
assert sha((ROOT/'dist/candidates/ProsperoCraft-01.000.084/PPSA99874.zip').read_bytes())=='a1e6774ba8bebe1faac0d9c36c4ff7cc17da1cf5622c2f9519bffc50eec57822'
work=ROOT/'build/client-startup-probe'
audit=json.loads((work/'launcher-toolkit-audit.json').read_text())
for name,digest in audit['objects_sha256'].items():
    obj=work/name;assert sha(obj.read_bytes())==digest
    refs=subprocess.check_output([str(LLVM/'llvm-nm'),'--undefined-only',str(obj)],text=True)
    assert not {l.split()[-1] for l in refs.splitlines() if l.split()}.intersection({'malloc','calloc','realloc','free','posix_memalign'})
print('PASS Temp_gametest141 package/CRC/identity/key exclusion and retention,toolkit pin/source/font/license hashes,real linked renderer/components/blit,explicit glyph constructor and no automatic constructors,paired C++ allocation,OSHI retained;console pending')
