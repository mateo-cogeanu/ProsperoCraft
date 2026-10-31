#!/usr/bin/env python3
"""Actual upstream Knot + intact Minecraft26.3 discovery and preLaunch mod on host."""
from pathlib import Path
import json,subprocess,zipfile,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');w=ROOT/'build/content103-knot';w.mkdir(exist_ok=True)
live=ROOT/'build/content103-live/cache';receipt=json.loads((live/'fabric/26.3/receipt.json').read_text());fabricjar=next(live/e['path'] for e in receipt['files'] if 'fabric-loader-' in e['path'])
gson=next(ROOT.glob('.tools/client/gson-*.jar'));lock=json.loads((ROOT/'client/26.3.lock.json').read_text());gamejar=ROOT/'.tools/client/client-26.3.jar';original=hashlib.sha256(gamejar.read_bytes()).hexdigest()
game=w/'game';shutil.rmtree(game,ignore_errors=True);(game/'mods').mkdir(parents=True)
(w/'PreLaunchCheck.java').write_text('''public class PreLaunchCheck implements net.fabricmc.loader.api.entrypoint.PreLaunchEntrypoint {public void onPreLaunch(){System.setProperty("ps5.test.fabric.preLaunch","ENTERED");throw new IllegalStateException("EXPECTED_HOST_PRELAUNCH_STOP");}}''')
subprocess.run([str(JDK/'bin/javac'),'-cp',str(fabricjar),'-d',str(w),str(w/'PreLaunchCheck.java')],check=True)
with zipfile.ZipFile(game/'mods/prospero-host-prelaunch.jar','w') as z:
 z.writestr('fabric.mod.json',json.dumps({'schemaVersion':1,'id':'prospero_host_check','version':'1.0.0','environment':'client','entrypoints':{'preLaunch':['PreLaunchCheck']}}));z.write(w/'PreLaunchCheck.class','PreLaunchCheck.class')
(w/'KnotCheck.java').write_text(r'''
import java.nio.file.*;import java.net.*;import java.util.*;import java.lang.reflect.*;
public class KnotCheck {
 public static void main(String[]a)throws Exception {
  Path cache=Path.of(a[0]);var fabric=new ProsperoFabric(cache);var receipt=fabric.read("26.3");var urls=new ArrayList<URL>();for(int n=2;n<a.length;n++)urls.add(Path.of(a[n]).toUri().toURL());
  var vanilla=new URLClassLoader(urls.toArray(URL[]::new),KnotCheck.class.getClassLoader());var loader=fabric.loader(receipt,vanilla);Thread.currentThread().setContextClassLoader(loader);ProsperoFabric.configure(loader,Path.of(a[2]),"26.3");if(!java.net.URLConnection.getDefaultUseCaches("jar"))throw new AssertionError("Fabric cached resource policy regressed");
  Class<?> env=loader.loadClass("net.fabricmc.api.EnvType"),knot=loader.loadClass("net.fabricmc.loader.impl.launch.knot.Knot");Object client=env.getField("CLIENT").get(null);Object launcher=knot.getConstructor(env).newInstance(client);
  try{knot.getMethod("init",String[].class).invoke(launcher,(Object)new String[]{"--gameDir",a[1],"--version","26.3","--username","HostProbe","--accessToken","0"});throw new AssertionError("preLaunch did not stop game");}
  catch(InvocationTargetException expected){if(!"ENTERED".equals(System.getProperty("ps5.test.fabric.preLaunch")))throw new AssertionError("Failed before preLaunch",expected.getCause());}
  ClassLoader target=Thread.currentThread().getContextClassLoader();
  if(target.loadClass("org.lwjgl.system.Configuration")!=loader.loadClass("org.lwjgl.system.Configuration"))throw new AssertionError("LWJGL configuration/native owner duplicated into Knot");if(target==loader)throw new AssertionError("Knot target handoff missing");
  System.out.println("PASS actual Fabric Knot26.3 + upstream libraries + intact official game JAR:game discovery/dependency resolution/Mixin initialization/real fixture mod preLaunch/target classloader handoff + shared parent LWJGL configuration/native owner. Deliberate stop before graphics;not PS5 or Vitrail rendering acceptance.");
 }
}
''')
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',str(gson),'-d',str(w),str(ROOT/'client/launcher/java/ProsperoBuild.java'),str(ROOT/'client/launcher/java/ProsperoInstall.java'),str(ROOT/'client/launcher/java/ProsperoDownloads.java'),str(ROOT/'client/launcher/java/ProsperoFabric.java'),str(ROOT/'client/launcher/java/ProsperoDependencies.java'),str(w/'KnotCheck.java')],check=True)
# Client first, then exact upstream non-native libraries. The launcher stays on parent.
artifacts=[ROOT/'.tools/client'/r['file'] for r in lock['artifacts'] if r['file']!='client-26.3.jar']
subprocess.run([str(JDK/'bin/java'),'-Xverify:all','-Djava.awt.headless=true','-cp',str(w)+':'+str(gson),'KnotCheck',str(live),str(game),str(gamejar),*map(str,artifacts)],check=True,timeout=90)
assert hashlib.sha256(gamejar.read_bytes()).hexdigest()==original
