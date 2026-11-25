#!/usr/bin/env python3
"""Exercise real persisted backdrop choices through the existing Settings model."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
source=r'''
import java.nio.file.*;
public class BackgroundCheck {
 public static void main(String[] args)throws Exception {
  Path root=Path.of(args[0]);var library=new ProsperoLibrary(root);library.settings().showIntro=false;
  var instance=library.add("Keep my world","26.3",1);Path world=library.game(instance).resolve("saves/Keep/level.dat");Files.createDirectories(world.getParent());Files.writeString(world,"unchanged");library.save();
  var model=new ProsperoLauncher(new ProsperoAuth(),root,null);model.tick(0x800);
  if(!model.tick(0)[11].equals("2")||!model.tick(0)[75].equals("5"))throw new AssertionError("Settings/default Waves");
  for(int i=0;i<8;i++)model.tick(0x40);
  for(int i=0;i<10;i++){
   int expected=(5+i)%10+1;model.tick(0x4000);int current=Integer.parseInt(model.tick(0)[15]);for(int k=0;k<10;k++){if(current==expected-1)break;model.tick(0x40);current=Integer.parseInt(model.tick(0)[15]);if(current==9&&current!=expected-1){for(int n=0;n<9;n++)model.tick(0x10);current=0;}}var fields=model.tick(0x4000);
   if(!fields[75].equals(""+expected)||!fields[76].equals(ProsperoLauncher.BACKGROUNDS[expected-1]))throw new AssertionError("mode mapping");
   if(new ProsperoLibrary(root).settings().background!=expected)throw new AssertionError("not persistent");
  }
  library=new ProsperoLibrary(root);library.settings().background=7;library.save();if(new ProsperoLibrary(root).settings().background!=7)throw new AssertionError("Waves migration overwrote later choice");library.settings().background=5;library.save();
  Path migration=root.resolve("library.json");String old=Files.readString(migration).replace("\"backgroundDefaultsRevision\": 1","\"backgroundDefaultsRevision\": 0").replace("\"background\": 5","\"background\": 2");Files.writeString(migration,old);if(new ProsperoLibrary(root).settings().background!=5)throw new AssertionError("existing library did not migrate to Waves");
  if(!Files.readString(world).equals("unchanged")||new ProsperoLibrary(root).instances().size()!=1)throw new AssertionError("world changed");
  Path file=root.resolve("library.json");String data=Files.readString(file);Files.writeString(file,data.replace("\"background\": 5","\"background\": 999"));
  if(new ProsperoLibrary(root).settings().background!=5)throw new AssertionError("invalid mode fallback");
  Files.writeString(file,data.replace("\"background\": 5,",""));if(new ProsperoLibrary(root).settings().background!=5)throw new AssertionError("older library default");
  System.out.println("PASS actual Settings Background row selects all10toolkit backgrounds,persists after reopen,defaults old/invalid preferences to Waves,retains instance/world bytes");
 }
}'''
with tempfile.TemporaryDirectory() as d:
 work=Path(d);(work/'BackgroundCheck.java').write_text(source);cp=str(ROOT/'.tools/client/gson-2.14.0.jar')
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(work),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(work/'BackgroundCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(work)+':'+cp,'BackgroundCheck',str(work/'data')],check=True)
