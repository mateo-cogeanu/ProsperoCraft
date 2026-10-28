#!/usr/bin/env python3
"""Exercise the original snapshot6 loadJNA method with our forced genuine JNI."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
runtime=ROOT.parents[2];w=ROOT/'build/snapshot6-jna119';w.mkdir(exist_ok=True)
cache=ROOT/'build/snapshot118-test/cache';receipt=json.loads((cache/'versions/26.4-snapshot-6/receipt.json').read_text());cp=':'.join([str(ROOT/'build/startup-host-096'),*[str(cache/p)for p in receipt['classpath']]])
(w/'SnapshotJnaCheck.java').write_text(r'''
public final class SnapshotJnaCheck {
 public static void main(String[] a)throws Exception {
  System.clearProperty("jna.noclasspath");System.clearProperty("jna.nounpack");ClientStartup25.configureJna(false);
  if(!System.getProperty("jna.nosys").equals("true")||Boolean.getBoolean("jna.noclasspath"))throw new AssertionError("old snapshot policy changed");
  ClientStartup25.configureJna(true);
  if(Boolean.getBoolean("jna.nosys")||!Boolean.getBoolean("jna.noclasspath")||!Boolean.getBoolean("jna.nounpack"))throw new AssertionError("resident JNA policy");
  Class<?> bootstrap=Class.forName("com.mojang.blaze3d.platform.NativeLibrariesBootstrap");
  if(!bootstrap.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("versions/26.4-snapshot-6/client.jar"))throw new AssertionError("game class replaced");
  var load=bootstrap.getDeclaredMethod("loadJNA");load.setAccessible(true);load.invoke(null);
  String path=System.getProperty("jnidispatch.path","");if(!path.contains("jna-host"))throw new AssertionError("stock native fallback: "+path);
  if(com.sun.jna.Native.POINTER_SIZE!=8)throw new AssertionError("real JNI ABI");
  System.out.println("PASS original snapshot6 loadJNA bootstrap method using genuine newly built dispatch; supported launcher policy avoids extraction; no game patch; host only");
 }
}
''')
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),str(w/'SnapshotJnaCheck.java')],check=True)
subprocess.run([str(JDK/'bin/java'),'--enable-native-access=ALL-UNNAMED','-Djna.boot.library.path='+str(runtime/'build/java25/jna-host'),'-cp',str(w)+':'+cp,'SnapshotJnaCheck'],check=True,timeout=30)
