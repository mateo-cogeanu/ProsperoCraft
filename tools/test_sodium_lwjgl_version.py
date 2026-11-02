#!/usr/bin/env python3
"""Manual original Sodium property/real LWJGL identity check; not rendering or ABI acceptance.

Requires explicit pinned original mod cache and real platform core/SLF4J JARs.
No game/mod transformations, test doubles, accounts, native execution or downloads.
Outside portable host lanes because these inputs are separately provisioned.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from host_toolchain import ROOT, java_home

SOURCE = r'''
public final class SodiumVersionCheck {
 public static void main(String[] args)throws Exception {
  boolean optOut=Boolean.parseBoolean(args[0]);
  if(optOut)System.setProperty("sodium.checks.issue2561","false");
  Class<?> checks=Class.forName("net.caffeinemc.mods.sodium.client.compatibility.checks.BugChecks");
  for(String name:new String[]{"ISSUE_899","ISSUE_1486","ISSUE_2048","ISSUE_2561","ISSUE_2637"}){
   var field=checks.getDeclaredField(name);field.setAccessible(true);
   if(field.getBoolean(null)!=( !optOut||!name.equals("ISSUE_2561")))throw new AssertionError(name);
  }
  String version=org.lwjgl.Version.getVersion();
  if(!version.startsWith("3.4.3"))throw new AssertionError("Untruthful or wrong LWJGL: "+version);
  Class<?> pre=Class.forName("net.caffeinemc.mods.sodium.client.compatibility.checks.PreLaunchChecks");
  var compatible=pre.getDeclaredMethod("isUsingKnownCompatibleLwjglVersion");compatible.setAccessible(true);
  if((boolean)compatible.invoke(null))throw new AssertionError("Mismatch hidden");
  if(optOut)pre.getMethod("checkEnvironment").invoke(null);
  System.out.println("PASS original Sodium "+(optOut?"upstream single-check opt-out returns":"default version check remains enabled")+"; real LWJGL "+version+"; other four checks enabled");
 }
}
'''


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--java-home',type=Path,required=True)
 p.add_argument('--mod-cache',type=Path,required=True)
 p.add_argument('--core-jar',type=Path,required=True)
 p.add_argument('--slf4j-jar',type=Path,required=True)
 a=p.parse_args();jdk=java_home(a.java_home)
 lock=json.loads((ROOT/'client/26.3.lock.json').read_text())
 slf=next(x for x in lock['artifacts']if x['file']==a.slf4j_jar.name)
 assert hashlib.sha256(a.slf4j_jar.read_bytes()).hexdigest()==slf['sha256'],'Unverified SLF4J'
 audit=json.loads((a.core_jar.parent/'audit.json').read_text())
 assert hashlib.sha256(a.core_jar.read_bytes()).hexdigest()==audit['output_sha256'],'Unverified platform core'
 with tempfile.TemporaryDirectory(prefix='sodium-version-')as tmp:
  w=Path(tmp);source=w/'SodiumVersionCheck.java';source.write_text(SOURCE)
  subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',str(a.core_jar),'-d',str(w),str(source)],check=True)
  for pin in json.loads((ROOT/'tests/sodium-lwjgl-test-pins.json').read_text())['artifacts']:
   jar=a.mod_cache/pin['file'];data=jar.read_bytes()
   assert len(data)==pin['size'] and hashlib.sha256(data).hexdigest()==pin['sha256'] and hashlib.sha512(data).hexdigest()==pin['sha512'],'Wrong original Sodium'
   cp=os.pathsep.join(map(str,[w,jar,a.core_jar,a.slf4j_jar]))
   for mode in ['false','true']:
    subprocess.run([str(jdk/'bin/java'),'-cp',cp,'SodiumVersionCheck',mode],check=True,timeout=30)
   assert jar.read_bytes()==data,'Original mod changed'
   print('PASS',pin['game'],pin['version'],pin['sha256'],flush=True)
 print('PASS three original Sodium artifacts: truthful LWJGL3.4.3, defaults/other checks retained, explicit single-check property honored; native ABI/GL/Iris/game/PS5 compatibility pending')


if __name__=='__main__':main()
