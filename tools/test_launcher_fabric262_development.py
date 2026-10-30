#!/usr/bin/env python3
"""Exercise package-only development access without changing public support policy."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
SOURCE=r'''
import java.nio.file.*;import java.util.*;import java.lang.reflect.*;
public class Fabric262DevelopmentCheck {
 static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
 static void set(ProsperoLauncher m,String name,Object value)throws Exception{var f=ProsperoLauncher.class.getDeclaredField(name);f.setAccessible(true);f.set(m,value);var c=ProsperoLauncher.class.getDeclaredField("cached");c.setAccessible(true);c.set(m,null);}
 public static void main(String[] args)throws Exception{
  boolean dev=Boolean.parseBoolean(args[1]);
  check(ProsperoChannel.fabric262Test()==dev,"exact channel and marker required;properties cannot enable test");
  check(!ProsperoLauncher.supported("26.2","fabric"),"public support stays held in test build");
  check(ProsperoLauncher.launchable("26.2","fabric")==dev,"development permission");
  check(!ProsperoLauncher.launchable("26.1","fabric"),"test scope does not enable unrelated versions");
  for(String v:List.of("26.2","26.3","26.4-snapshot-1","26.4-snapshot-6"))check(ProsperoLauncher.launchable(v,"vanilla"),"vanilla remains available");
  check(ProsperoLauncher.launchable("26.3","fabric"),"Fabric26.3 preserved");
  Path root=Path.of(args[0]);var library=new ProsperoLibrary(root);library.settings().showIntro=false;library.save();
  var instance=library.add("Disposable Fabric test","26.2",1,"fabric");library.ready(instance,true);
  String saved=Files.readString(root.resolve("library.json"));
  var model=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("No network in state inspection");});
  check(model.tick(0)[35].equals(dev?"DEV TEST":"COMING SOON"),"card accurately labeled");
  set(model,"detail",instance);set(model,"page",4);set(model,"row",0);set(model,"top",false);
  String[] state=model.tick(0);
  check(state[6].equals(dev?"DEV TEST - PLAY":"COMING SOON"),"action label");
  check(state[69].equals(dev?"DEVELOPMENT":"PENDING"),"never claims support");
  if(dev)check(state[65].contains("disposable")&&ProsperoChannel.label().equals("DEV FABRIC 26.2"),"development notice and channel");
  set(model,"versions",List.of(new ProsperoInstall.Version("26.2","release","","")));set(model,"dropdownKind",6);
  var choices=ProsperoLauncher.class.getDeclaredMethod("choices");choices.setAccessible(true);
  check(((List<?>)choices.invoke(model)).get(1).toString().contains(dev?"Development test":"Coming soon"),"loader picker");
  check(Files.readString(root.resolve("library.json")).equals(saved)&&instance.loader.equals("fabric"),"loader and library not migrated");
  var current=ProsperoLauncher.class.getDeclaredField("current");current.setAccessible(true);current.set(null,model);
  var receipt=new ProsperoInstall.Receipt();receipt.window="GLFW";set(model,"receipt",receipt);set(model,"fabricLoaderVersion","0.19.5");
  check(ProsperoLauncher.gameMain().equals(ProsperoFabric.MAIN),"genuine Fabric entrypoint retained");
  check(ProsperoLauncher.launchIdentity().equals("PS5_LAUNCH game=26.2 loader=fabric window=GLFW fabric262_test="+dev+" fabric_loader=0.19.5"),"identity excludes instance/account/paths");
  System.out.println("PASS channel/marker scope dev="+dev+";public support held;labels/entrypoint/launch identity/instance retention");
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 work=Path(d);(work/'Fabric262DevelopmentCheck.java').write_text(SOURCE)
 gson=str(ROOT/'.tools/client/gson-2.14.0.jar')
 classes=work/'classes';classes.mkdir()
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',gson,'-d',str(classes),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(work/'Fabric262DevelopmentCheck.java')],check=True)
 for n,(channel,marker,enabled) in enumerate([
  ('temp_gametest',None,False),('temp_gametest','fabric-26.2-test-v1\n',True),
  ('demo','fabric-26.2-test-v1\n',False),('offline','fabric-26.2-test-v1\n',False),
  ('temp_gametest','fabric-26.2-test-v1\nextra',False),('temp_gametest','fabric-26.2-test-v2\n',False),
 ]):
  resources=work/str(n);resources.mkdir();(resources/'prosperocraft-channel.txt').write_text(channel+'\n')
  if marker is not None:(resources/'prosperocraft-development.txt').write_text(marker)
  subprocess.run([str(JDK/'bin/java'),'-Dps5.fabric262.test=true','-cp',str(resources)+':'+str(classes)+':'+gson,'Fabric262DevelopmentCheck',str(work/('data'+str(n))),str(enabled).lower()],check=True)
