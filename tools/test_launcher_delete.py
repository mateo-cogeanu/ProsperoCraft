#!/usr/bin/env python3
"""Exercise actual delete/undo/confirmation logic, failure rollback and move recovery."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
JDK=java_home()
source=r'''
import java.nio.file.*;import java.util.*;import java.io.*;
public class DeleteCheck {
 static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
 static void set(Object o,String n,Object v)throws Exception{var f=o.getClass().getDeclaredField(n);f.setAccessible(true);f.set(o,v);}
 interface Job{void run()throws Exception;}static void reject(Job j)throws Exception{try{j.run();throw new AssertionError("accepted");}catch(IOException expected){}}
 public static void main(String[]args)throws Exception{
  Path base=Path.of(args[0]);var lib=new ProsperoLibrary(base.resolve("library"));lib.settings().showIntro=false;var first=lib.add("First","26.3",1);var second=lib.add("Second","26.3",2);
  Path world=lib.game(first).resolve("saves/My World/level.dat");Files.createDirectories(world.getParent());Files.writeString(world,"world");Files.createDirectories(lib.root.resolve("cache"));Files.writeString(lib.root.resolve("cache/keep"),"cache");Files.writeString(lib.root.resolve("account-fixture"),"private");
  lib.toggleFavorite(first,new ProsperoDestinations.Entry("WORLD","My World","My World"));
  Files.createDirectory(lib.root.resolve("library.json.tmp"));reject(()->lib.delete(first));Files.delete(lib.root.resolve("library.json.tmp"));check(lib.instances().size()==2&&Files.readString(world).equals("world")&&lib.favorites().size()==1,"rollback lost data");
  new ProsperoLibrary(lib.root);check(lib.delete(first),"cleanup failed");check(!Files.exists(world)&&lib.instances().size()==1&&lib.favorites().isEmpty(),"permanent deletion/pins");
  try(var paths=Files.walk(lib.root.resolve("pending-delete"))){check(paths.count()==1,"retained deleted bytes");}
  check(Files.readString(lib.root.resolve("cache/keep")).equals("cache")&&Files.readString(lib.root.resolve("account-fixture")).equals("private")&&Files.isDirectory(lib.game(second)),"unrelated data");
  // Crash before metadata commit restores live bytes. After commit, purge finishes.
  Path journal=lib.root.resolve("pending-delete/interrupted");Files.createDirectories(journal);Files.writeString(journal.resolve("id"),second.id);Files.writeString(lib.game(second).resolve("keep"),"keep");Files.move(lib.game(second).getParent(),journal.resolve("files"));var recovered=new ProsperoLibrary(lib.root);check(Files.readString(recovered.game(second).resolve("keep")).equals("keep"),"precommit recovery");
  Path committed=lib.root.resolve("pending-delete/committed");Files.createDirectories(committed.resolve("files"));Files.writeString(committed.resolve("id"),first.id);Files.writeString(committed.resolve("files/removed"),"delete");new ProsperoLibrary(lib.root);check(!Files.exists(committed),"postcommit purge");
  Path outside=base.resolve("outside");Files.createDirectories(outside);Files.writeString(outside.resolve("keep"),"keep");var link=recovered.add("Link","26.3",1);Files.delete(recovered.game(link));Files.delete(recovered.game(link).getParent());Files.createSymbolicLink(recovered.game(link).getParent(),outside);reject(()->recovered.delete(link));check(Files.readString(outside.resolve("keep")).equals("keep"),"followed link");
  // Yes/No model confirmation, default No, no undo binding after restart.
  Path root=base.resolve("model");var store=new ProsperoLibrary(root);store.settings().showIntro=false;var entry=store.add("Delete me","26.3",1);
  var model=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});set(model,"page",5);set(model,"detail",getInstance(model));set(model,"row",6);
  model.tick(0x4000);check(model.tick(0)[11].equals("9")&&model.tick(0)[15].equals("0"),"default no");model.tick(0x4000);check(model.tick(0)[11].equals("5")&&Files.isDirectory(store.game(entry)),"No deleted data");model.tick(0x4000);model.tick(0x20);model.tick(0x4000);check(model.tick(0)[11].equals("0")&&!Files.exists(store.game(entry)),"Yes failed");var restart=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});restart.tick(0x1000);check(new ProsperoLibrary(root).instances().isEmpty()&&!restart.tick(0)[74].equals("UNDO"),"undo exists");
  System.out.println("PASS permanent deletion: Yes/No default No, no undo, world/pin purge, shared data retained, rollback/journal recovery, symlink protection");
 }
 static ProsperoLibrary.Instance getInstance(Object m)throws Exception{var f=m.getClass().getDeclaredField("library");f.setAccessible(true);return ((ProsperoLibrary)f.get(m)).instances().get(0);}
}'''
with tempfile.TemporaryDirectory(prefix='prospero-delete-') as folder:
 w=Path(folder);(w/'DeleteCheck.java').write_text(source);cp=launcher_classpath()
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'DeleteCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(w)+':'+cp,'DeleteCheck',str(w/'data'),str(w)],check=True,timeout=40)
