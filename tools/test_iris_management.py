#!/usr/bin/env python3
"""Manual original Iris shadow-frustum initializer with forced runtime-owned JNI.

Explicit publisher/mod caches only; no downloads, accounts, JAR edits or rendering.
Outside portable host lanes: requires target runtime Java classes and macOS JNI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from prepare_client_261 import ROOT, verified, validate_metadata, allowed, artifact_path


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['runtime-workspace','mod-cache','publisher-cache','java-home','cc','output-dir']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();mods=a.mod_cache.resolve();runtime=a.runtime_workspace.resolve();cache=a.publisher_cache.resolve()
 iris=json.loads((ROOT/'tests/iris-management-pin.json').read_text());ijar=mods/iris['file'];b=ijar.read_bytes()
 assert len(b)==iris['size']and hashlib.sha256(b).hexdigest()==iris['sha256']and hashlib.sha512(b).hexdigest()==iris['sha512'],'Wrong original Iris'
 sodium=next(x for x in json.loads((ROOT/'tests/sodium-lwjgl-test-pins.json').read_text())['artifacts']if x['game']=='26.1.2');sjar=mods/sodium['file'];sb=sjar.read_bytes();assert hashlib.sha256(sb).hexdigest()==sodium['sha256'],'Wrong original Sodium'
 row=next(x for x in json.loads((ROOT/'client/26.1.lock.json').read_text())['versions']if x['id']=='26.1.2');meta=validate_metadata(row,verified(row['metadata'],cache/'26.1.2.json',offline=True));game=cache/'26.1.2-client.jar';verified(row['client'],game,offline=True)
 jars=[ijar,sjar,game]
 for lib in meta['libraries']:
  name=lib['name']
  if ':natives-'in name or not allowed(lib)or(name.startswith('io.netty:netty-transport-native-')and len(name.split(':'))>3):continue
  artifact=lib.get('downloads',{}).get('artifact')
  if artifact:
   path=cache/'libraries'/artifact_path(artifact['path']);verified(artifact,path,offline=True);jars.append(path)
 subprocess.run(['python3',str(runtime/'tools/test_java25_management_extensions.py'),'--java-home',str(a.java_home.resolve()),'--cc',str(a.cc.resolve()),'--output-dir',str(a.output_dir.resolve()),'--class-path',os.pathsep.join(map(str,jars)),'--initialize-class','net.irisshaders.iris.shadows.frustum.advanced.AdvancedShadowCullingFrustum','--boolean-field','FMA_SUPPORT'],check=True)
 assert ijar.read_bytes()==b and sjar.read_bytes()==sb,'Original mod mutated'
 print('PASS original Iris shadow-frustum clinit and FMA_SUPPORT match real VM false/true through forced genuine runtime JNI; shader loading/rendering/PS5 pending')


if __name__=='__main__':main()
