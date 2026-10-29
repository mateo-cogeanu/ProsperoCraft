#!/usr/bin/env python3
"""Exercise real persisted backdrop choices through the existing Settings model."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
source=r'''

import java.nio.file.*;
public class ThemeCheck {
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 public static void main(String[] args)throws Exception {
  Path root=Path.of(args[0]);var library=new ProsperoLibrary(root);library.settings().showIntro=false;
  var instance=library.add("Keep my world","26.3",1);Path world=library.game(instance).resolve("saves/Keep/level.dat");Files.createDirectories(world.getParent());Files.writeString(world,"unchanged");library.save();
  var model=new ProsperoLauncher(new ProsperoAuth(),root,null);model.tick(0x800);model.tick(0x40);for(int i=0;i<6;i++)model.tick(0x40);
  check(model.tick(0)[15].equals("6"),"theme row reachable");
  for(int theme=0;theme<6;theme++){
   model.tick(0x4000);check(model.tick(0)[82].equals("Color theme"),"theme dropdown");int current=Integer.parseInt(model.tick(0)[15]);
   while(current>theme){model.tick(0x10);current--;}while(current<theme){model.tick(0x40);current++;}
   var f=model.tick(0x4000);check(f.length==105&&f[104].equals(""+theme)&&f[11].equals("2")&&f[15].equals("6"),"live selection and return");
   check(new ProsperoLibrary(root).settings().theme==theme,"theme persisted");
  }
  model.tick(0x4000);model.tick(0x10);model.tick(0x2000);check(model.tick(0)[104].equals("5"),"cancel keeps saved theme");
  check(new ProsperoLibrary(root).settings().background==5&&!new ProsperoLibrary(root).settings().snapshots,"unrelated settings");
  Path file=root.resolve("library.json");String saved=Files.readString(file);Files.writeString(file,saved.replace("\"theme\": 5,",""));check(new ProsperoLibrary(root).settings().theme==0,"old library default");
  Files.writeString(file,saved.replace("\"theme\": 5","\"theme\": 999"));check(new ProsperoLibrary(root).settings().theme==0,"invalid theme fallback");
  check(Files.readString(world).equals("unchanged")&&new ProsperoLibrary(root).instances().size()==1,"world preserved");
  System.out.println("PASS all six color themes selected through Settings, live field, save/reopen, cancel, legacy/invalid fallback, instances/world/settings preserved");
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 work=Path(d);(work/'ThemeCheck.java').write_text(source);cp=str(ROOT/'.tools/client/gson-2.14.0.jar')
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(work),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(work/'ThemeCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(work)+':'+cp,'ThemeCheck',str(work/'data')],check=True)
