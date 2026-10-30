#!/usr/bin/env python3
"""Check the unchanged accepted167 release and its shipped launch policy."""
from pathlib import Path
import hashlib,json,zipfile,io,tempfile,subprocess
r=Path(__file__).resolve().parents[1];out=r/'dist/releases/client167';candidate=r/'dist/candidates/ProsperoCraft-Launcher-01.000.167'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((r/'docs/validation/client167-console-acceptance-2026-10-30.json').read_text())
assert sha(out/'PPSA99874.zip')==sha(candidate/'PPSA99874.zip')==record['package_sha256']
with zipfile.ZipFile(out/'PPSA99874.zip') as z:
 assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(names))
 assert all(n.startswith('PPSA99874/')and '..'not in n.split('/')for n in names)
 assert z.read('PPSA99874/sce_sys/param.json')==(r/'sce_sys/param.json').read_bytes()
 p=json.loads(z.read('PPSA99874/sce_sys/param.json'));assert p['titleId']=='PPSA99874'and p['contentVersion']=='01.000.167'and p['downloadDataSize']==4096
 assert z.read('PPSA99874/sce_sys/icon0.png')==(r/'assets/branding/icon0.png').read_bytes()
 assert not any('/instances/'in n or '/account/'in n or '/game-assets/objects/'in n or n.endswith(('client-26.3.jar','.log','.DS_Store'))for n in names)
 for pin in json.loads(z.read('PPSA99874/assets/java25/launcher-dependencies.json')):
  assert pin['id'].startswith(('org.lwjgl:','com.google.code.gson:'))
  assert hashlib.sha256(z.read('PPSA99874/assets/java25/client/jars/'+pin['file'])).hexdigest()==pin['sha256']
 assert z.read('PPSA99874/licenses/ProsperoCraft-NOTICE.txt')==(r/'NOTICE').read_bytes()
 with zipfile.ZipFile(io.BytesIO(z.read('PPSA99874/assets/java25/client-probe.jar')))as jar:
  assert jar.read('prosperocraft-channel.txt')==b'temp_gametest\n';assert 'prosperocraft-development.txt'not in jar.namelist()
 with tempfile.TemporaryDirectory(prefix='release167-policy-')as td:
  w=Path(td);(w/'launcher.jar').write_bytes(z.read('PPSA99874/assets/java25/client-probe.jar'))
  gson=next(n for n in names if '/client/jars/gson-'in n and n.endswith('.jar'));(w/'gson.jar').write_bytes(z.read(gson))
  (w/'Release167Check.java').write_text('''import java.nio.file.*;public class Release167Check{public static void main(String[]a)throws Exception{if(!ProsperoLauncher.supported("26.2","fabric")||ProsperoLauncher.developmentTest("26.2","fabric")||ProsperoChannel.fabric262Test())throw new AssertionError("Fabric26.2 not supported");Path root=Path.of(a[0]);var l=new ProsperoLibrary(root);if(l.settings().snapshots)throw new AssertionError("snapshot default");l.settings().snapshots=true;l.save();if(!new ProsperoLibrary(root).settings().snapshots)throw new AssertionError("saved choice");System.out.println("PASS actual shipped167 classes: Fabric26.2 supported, no development gate, snapshots default off and saved explicit choice retained");}}''')
  j=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home/bin');cp=str(w/'launcher.jar')+':'+str(w/'gson.jar')
  subprocess.run([str(j/'javac'),'--release','25','-cp',cp,'-d',str(w),str(w/'Release167Check.java')],check=True)
  subprocess.run([str(j/'java'),'-cp',str(w)+':'+cp,'Release167Check',str(w/'data')],check=True)
with zipfile.ZipFile(out/'client167-openal-source-relink.zip')as z:
 assert z.testzip() is None;m=json.loads(z.read('manifest.json'));assert m['app_version']=='01.000.167'and m['tested_source_commit']==record['candidate_source_commit']
 assert m['original_elf_sha256']==sha(candidate/'bootstrap-symbols.elf')
 for row in m['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
 for name in ['relink.py','build_openal_replacement.py','openal-startup-source/COPYING','openal-startup-source/alc/backends/ps5_backend.cpp']:assert name in z.namelist()
 for name in ['client167-release-relink.log','client167-release-replacement.log']:assert m['original_elf_sha256']in(r/'build'/name).read_text()
for line in(out/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split();assert sha(out/name)==digest
print('PASS exact accepted167 ZIP, release identity/privacy/pins/notices, corresponding-source object hashes, matching normal/replacement native relinks and all release checksums')
