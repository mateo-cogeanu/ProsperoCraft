#!/usr/bin/env python3
"""Manual actual packaged LWJGL vs original publisher OpenAL loader boundaries.

No native calls/initialization, accounts, downloads or original JAR changes.
Explicit package/publisher inputs are required; outside portable host lanes.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from host_toolchain import ROOT,java_home
from prepare_client_261 import verified,validate_metadata,artifact_path

JAVA=r'''
import java.net.*;import java.nio.file.*;
public class BindingOwners {
 public static void main(String[]args)throws Exception{
  URL[] full=new URL[args.length-1];for(int i=1;i<args.length;i++)full[i-1]=Path.of(args[i]).toUri().toURL();
  URL[] child={Path.of(args[0]).toUri().toURL()};
  try(var parent=new URLClassLoader(full,ClassLoader.getPlatformClassLoader());var loader=new ProsperoGameLoader(child,parent)){
   ProsperoBindings.verify(parent);
   for(String name:new String[]{"org.lwjgl.openal.ALC","org.lwjgl.openal.ALC10","org.lwjgl.openal.AL","org.lwjgl.openal.AL10"})if(Class.forName(name,false,loader).getClassLoader()!=parent)throw new AssertionError("split packaged binding");
   System.out.println("PASS real packaged parent binding preflight and shared OpenAL owners");
  }
  URL[] incomplete=java.util.Arrays.stream(full).filter(url->!url.toString().endsWith("/lwjgl-openal-3.4.3.jar")).toArray(URL[]::new);
  try(var parent=new URLClassLoader(incomplete,ClassLoader.getPlatformClassLoader());var old=new URLClassLoader(child,parent);var loader=new ProsperoGameLoader(child,parent)){
   if(Class.forName("org.lwjgl.openal.ALC",false,old).getClassLoader()!=parent||Class.forName("org.lwjgl.openal.ALC10",false,old).getClassLoader()!=old)throw new AssertionError("did not reproduce old split");
   try{Class.forName("org.lwjgl.openal.ALC10",false,loader);throw new AssertionError("fell back to incompatible child binding");}catch(ClassNotFoundException expected){}
   try{ProsperoBindings.verify(parent);throw new AssertionError("missing parent accepted");}catch(ClassNotFoundException expected){}
   System.out.println("PASS old genuine split-loader reproduction; new missing-parent refusal with original child JAR present");
  }
 }
}
'''

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['package-app','publisher-cache','java-home']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();jdk=java_home(a.java_home);java=a.package_app.resolve()/'assets/java25';cache=a.publisher_cache.resolve()
 audit=json.loads((java/'zink-classpath-audit.json').read_text());paths=[]
 import hashlib
 for key,digest in audit['jars_sha256'].items():
  file=java/key;assert hashlib.sha256(file.read_bytes()).hexdigest()==digest;paths.append(file)
 row=next(x for x in json.loads((ROOT/'client/26.1.lock.json').read_text())['versions']if x['id']=='26.1.2');meta=validate_metadata(row,verified(row['metadata'],cache/'26.1.2.json',offline=True));lib=next(x['downloads']['artifact']for x in meta['libraries']if x['name'].startswith('org.lwjgl:lwjgl-openal:')and':natives-'not in x['name']);original=cache/'libraries'/artifact_path(lib['path']);before=verified(lib,original,offline=True)
 with tempfile.TemporaryDirectory(prefix='binding-owners-')as tmp:
  work=Path(tmp);source=work/'BindingOwners.java';source.write_text(JAVA)
  subprocess.run([str(jdk/'bin/javac'),'--release','25','-d',str(work),str(source),str(ROOT/'client/launcher/java/ProsperoGameLoader.java'),str(ROOT/'client/launcher/java/ProsperoBindings.java')],check=True)
  subprocess.run([str(jdk/'bin/java'),'-Xverify:all','-cp',str(work),'BindingOwners',str(original),*map(str,paths)],check=True,timeout=30)
 assert original.read_bytes()==before
 print('PASS genuine binding loader boundary; no native/API/render/PS5 acceptance inferred')

if __name__=='__main__':main()
