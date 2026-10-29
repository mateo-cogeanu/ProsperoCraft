#!/usr/bin/env python3
"""Exercise loader-specific launch gating and preservation of existing instances."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
source=r'''
import java.nio.file.*;import java.util.*;import java.lang.reflect.*;
public class Fabric262PendingCheck {
 static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
 static void set(ProsperoLauncher m,String name,Object value)throws Exception{var f=ProsperoLauncher.class.getDeclaredField(name);f.setAccessible(true);f.set(m,value);var c=ProsperoLauncher.class.getDeclaredField("cached");c.setAccessible(true);c.set(m,null);}
 static Object call(ProsperoLauncher m,String name)throws Exception{var f=ProsperoLauncher.class.getDeclaredMethod(name);f.setAccessible(true);return f.invoke(m);}
 public static void main(String[] args)throws Exception{
  check(ProsperoLauncher.supported("26.2")&&ProsperoLauncher.supported("26.2","vanilla")&&!ProsperoLauncher.supported("26.2","fabric"),"only Fabric26.2 held");
  for(String v:List.of("26.3","26.4-snapshot-1","26.4-snapshot-6"))check(ProsperoLauncher.supported(v,"vanilla")&&ProsperoLauncher.supported(v,"fabric"),"working versions preserved");
  Path root=Path.of(args[0]);var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;lib.save();
  var fabric=lib.add("My Fabric world","26.2",1,"fabric");lib.ready(fabric,true);var vanilla=lib.add("My Vanilla world","26.2",1,"vanilla");lib.ready(vanilla,true);
  Path world=lib.game(fabric).resolve("saves/Keep/level.dat"),mod=lib.game(fabric).resolve("mods/keep.jar"),cache=root.resolve("cache/keep.jar");
  for(Path p:List.of(world,mod,cache)){Files.createDirectories(p.getParent());Files.writeString(p,"preserved fixture");}
  String saved=Files.readString(root.resolve("library.json"));
  var model=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("Gate must precede account/download/verification network: "+url);});
  var cards=model.tick(0);check(cards[35].equals("COMING SOON")&&cards[39].equals("READY"),"existing Fabric and Vanilla cards differ");
  set(model,"detail",fabric);set(model,"page",4);set(model,"row",0);set(model,"top",false);
  var state=model.tick(0);check(state[6].equals("COMING SOON")&&state[69].equals("PENDING"),"detail held even if ready");
  state=model.tick(0x4000);check(state[10].equals("WAIT")&&state[2].contains("Fabric for Minecraft 26.2 is coming soon")&&state[64].equals("IDLE"),"X does not launch or install");
  var receipt=new ProsperoInstall.Receipt();receipt.version="26.2";receipt.window="GLFW";receipt.javaMajor=25;
  var prepare=ProsperoLauncher.class.getDeclaredMethod("prepareLaunch",ProsperoLibrary.Instance.class,ProsperoInstall.Receipt.class);prepare.setAccessible(true);prepare.invoke(model,fabric,receipt);check(model.tick(0)[10].equals("WAIT"),"final launch preparation also guarded");
  set(model,"detail",vanilla);check(!model.tick(0)[6].equals("COMING SOON")&&model.tick(0)[69].equals("SUPPORTED"),"Vanilla detail stays playable");
  set(model,"versions",List.of(new ProsperoInstall.Version("26.2","release","", ""),new ProsperoInstall.Version("26.3","release","", "")));set(model,"dropdownKind",6);
  check(((List<?>)call(model,"choices")).get(1).toString().contains("Coming soon"),"Fabric choice marked for26.2");
  set(model,"versionChoice",1);check(((List<?>)call(model,"choices")).get(1).equals("Fabric"),"Fabric26.3 choice unchanged");
  set(model,"versionChoice",0);set(model,"dropdownKind",0);set(model,"draftLoader",1);
  check(((List<?>)call(model,"choices")).get(0).toString().contains("Coming soon"),"Fabric version picker held");
  set(model,"draftLoader",0);check(!((List<?>)call(model,"choices")).get(0).toString().contains("Coming soon"),"Vanilla version picker available");
  check(Files.readString(root.resolve("library.json")).equals(saved),"no settings/instances migration");
  for(Path p:List.of(world,mod,cache))check(Files.readString(p).equals("preserved fixture"),"world/mod/download preserved");
  var reopened=new ProsperoLibrary(root);check(reopened.instances().size()==2&&reopened.instances().get(0).ready,"ready receipts retained after reopen");
  System.out.println("PASS Fabric26.2 cards/detail/launch-preparation/creation labels held;Vanilla26.2 and working Fabric versions available;instances/world/mod/cache/settings preserved");
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 work=Path(d);(work/'Fabric262PendingCheck.java').write_text(source);cp=str(ROOT/'.tools/client/gson-2.14.0.jar')
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(work),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(work/'Fabric262PendingCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(work)+':'+cp,'Fabric262PendingCheck',str(work/'data')],check=True)
