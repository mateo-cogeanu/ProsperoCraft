#!/usr/bin/env python3
"""Recompile original GLFW3.4.1bindings against the resident LWJGL3.4.3callback ABI."""
from pathlib import Path
import hashlib,json,subprocess,urllib.request,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
def build(java_home,offline=False):
 pin=json.loads((ROOT/'client/ports/glfw/binding.json').read_text());cache=ROOT/'.tools/client'/pin['file']
 if not cache.exists():
  if offline:raise FileNotFoundError(cache)
  cache.write_bytes(urllib.request.urlopen(pin['url'],timeout=60).read())
 assert hashlib.sha256(cache.read_bytes()).hexdigest()==pin['sha256']
 out=ROOT/'build/client-ports/glfw';src=out/'src';classes=out/'classes';shutil.rmtree(src,ignore_errors=True);shutil.rmtree(classes,ignore_errors=True);src.mkdir(parents=True);classes.mkdir();changed=[]
 with zipfile.ZipFile(cache)as z:
  for name in z.namelist():
   if not name.startswith('org/lwjgl/glfw/')or not name.endswith('.java'):continue
   text=z.read(name).decode();old='new Callback.Descriptor(\n        MethodHandles.lookup(),'
   if old in text:
    interface=Path(name).stem;text=text.replace(old,'new Callback.Descriptor(\n        '+interface+'.class, MethodHandles.lookup(),');changed.append(name)
   target=src/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
 assert len(changed)==26
 lock=json.loads((ROOT/'client/26.3.lock.json').read_text());cp=':'.join(str(ROOT/'.tools/client'/row['file'])for row in lock['artifacts']if row['id'].startswith(('org.lwjgl:','org.jspecify:')))
 subprocess.run([str(java_home/'bin/javac'),'--release','25','-proc:none','-cp',cp,'-d',str(classes),*map(str,sorted(src.rglob('*.java')))],check=True)
 target=out/'lwjgl-glfw-3.4.1-ps5-callback343.jar'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted(classes.rglob('*.class')):z.write(p,p.relative_to(classes))
  z.writestr('META-INF/PS5-PORT.txt','Original LWJGL GLFW3.4.1API recompiled for LWJGL3.4.3 callback descriptor. Only source change: explicit callback interface Class parameter. No game class changes. BSD-3-Clause LWJGL license: https://www.lwjgl.org/license\n')
 audit={'source':pin,'changed_source_units':changed,'adaptation':'Explicit callback interface Class argument required by3.4.3Callback.Descriptor; all GLFW3.4.1Java bindings recompiled against resident3.4.3core','output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'game_jar_modified':False,'console':'Pending26.2launch'};(out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');return target
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--java-home',type=Path,required=True);p.add_argument('--offline',action='store_true');a=p.parse_args();print(build(a.java_home,a.offline))
