#!/usr/bin/env python3
"""Real launcher remap UI/persistence, schema migration, SDL hint and cached Fabric guard."""
from pathlib import Path
import json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');w=ROOT/'build/input105-model';w.mkdir(exist_ok=True)
cp=':'.join(str(ROOT/'.tools/client'/r['file'])for r in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts'])
source=r'''
import java.nio.file.*;import java.util.*;import java.net.*;import com.google.gson.*;
public class Input105 {
 static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
 static void set(ProsperoLauncher m,String name,Object v)throws Exception{var f=ProsperoLauncher.class.getDeclaredField(name);f.setAccessible(true);f.set(m,v);var c=ProsperoLauncher.class.getDeclaredField("cached");c.setAccessible(true);c.set(m,null);}
 public static void main(String[]a)throws Exception{
  Path root=Path.of(a[0]);var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;lib.save();
  var old=JsonParser.parseString(Files.readString(root.resolve("library.json"))).getAsJsonObject();old.getAsJsonObject("settings").remove("controllerKeys");Files.writeString(root.resolve("library.json"),old.toString());check(Arrays.equals(new ProsperoLibrary(root).settings().controllerKeys,ProsperoInput.DEFAULT),"legacy binding migration");
  var model=new ProsperoLauncher(new ProsperoAuth(),root,u->{throw new java.io.IOException();});set(model,"page",2);set(model,"tab",1);set(model,"row",6);model.tick(0x4000);check(model.tick(0)[11].equals("13")&&model.tick(0)[83].equals("23"),"input settings route");
  model.tick(0x40);check(model.tick(0)[85].contains("Restore"),"reset first");model.tick(0x4000);check(model.tick(0)[11].equals("10")&&model.tick(0)[82].contains("key"),"binding dropdown");
  int chosen=ProsperoInput.CODES.indexOf(12);set(model,"row",chosen);model.tick(0x4000);check(model.tick(0)[11].equals("13"),"binding return");check(new ProsperoLibrary(root).settings().controllerKeys[8]==12,"mapped I not saved");
  set(model,"row",21);model.tick(0x4000);set(model,"row",ProsperoInput.CODES.indexOf(515));model.tick(0x4000);check(new ProsperoLibrary(root).settings().controllerKeys[28]==515,"trigger mouse mapping");
  set(model,"row",0);model.tick(0x4000);check(Arrays.equals(new ProsperoLibrary(root).settings().controllerKeys,ProsperoInput.DEFAULT),"reset not saved");
  model.tick(0x2000);check(model.tick(0)[11].equals("2")&&model.tick(0)[15].equals("6"),"back loses route");
  int[] invalid=ProsperoInput.DEFAULT.clone();invalid[0]=4;try{ProsperoInput.validate(invalid);throw new AssertionError("menu navigation remapped");}catch(IllegalArgumentException expected){}
  try(var loader=new java.net.URLClassLoader(new URL[0])){URLConnection.setDefaultUseCaches("jar",false);ProsperoFabric.configure(loader,root.resolve("client.jar"),"26.3");check(URLConnection.getDefaultUseCaches("jar"),"uncached Fabric regression");}
  check(ProsperoInput.hint(ProsperoInput.DEFAULT).split(",").length==30,"hint serialization");
  System.out.println("PASS real remap screen/dropdown/save/reopen/reset/menu-control protection/old-library migration/30-slot SDL hint;cached Fabric resource policy restored");
 }
}'''
(w/'Input105.java').write_text(source)
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'Input105.java')],check=True)
data=w/'data';shutil.rmtree(data,ignore_errors=True);data.mkdir()
subprocess.run([str(JDK/'bin/java'),'-Xverify:all','-cp',str(w)+':'+cp,'Input105',str(data)],check=True,timeout=30)
