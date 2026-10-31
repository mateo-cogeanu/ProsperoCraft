#!/usr/bin/env python3
"""Exercise actual duplicate data isolation, cancellation, publication failure and UI routing."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];jdk=java_home()
s=r'''
import java.nio.file.*;import java.io.*;import java.util.*;
public class DuplicateCheck{
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 interface Job{void run()throws Exception;}static void denied(Job j)throws Exception{try{j.run();throw new AssertionError("accepted");}catch(IOException expected){}}
 static void set(Object o,String key,Object value)throws Exception{var f=o.getClass().getDeclaredField(key);f.setAccessible(true);f.set(o,value);}
 static Object get(Object o,String key)throws Exception{var f=o.getClass().getDeclaredField(key);f.setAccessible(true);return f.get(o);}
 static Map<String,String> tree(Path root)throws Exception{var map=new TreeMap<String,String>();try(var paths=Files.walk(root)){for(var p:paths.toList())if(Files.isRegularFile(p))map.put(root.relativize(p).toString(),Base64.getEncoder().encodeToString(Files.readAllBytes(p)));}return map;}
 public static void main(String[]a)throws Exception{
  Path base=Path.of(a[0]);var library=new ProsperoLibrary(base.resolve("library"));library.settings().showIntro=false;var original=library.add("Original","26.3",16,"fabric");library.defaultContentInstalled(original);library.ready(original,true);
  Path folder=library.game(original).getParent();for(String name:List.of("game/saves/World/level.dat","game/mods/controlify.jar","game/shaderpacks/shader.zip","game/resourcepacks/§lC418 §rSongs Only.zip","game/config/controlify.json","content-installed.json","content-queue.json")){Path p=folder.resolve(name);Files.createDirectories(p.getParent());Files.writeString(p,"DATA:"+name);}
  byte[] large=new byte[2*1024*1024];new Random(116).nextBytes(large);Files.write(folder.resolve("game/large.bin"),large);Files.createDirectories(folder.resolve("game/empty"));Files.createDirectories(library.root.resolve("cache"));Files.writeString(library.root.resolve("cache/shared"),"shared");Files.writeString(library.root.resolve("account-fixture"),"private");
  var before=tree(folder);long[] progress={0};var copy=library.duplicate(original,(m,d,t)->progress[0]=d,()->false);
  check(!copy.id.equals(original.id)&&copy.name.equals("Original Copy")&&copy.loader.equals("fabric")&&copy.version.equals("26.3")&&copy.icon==16&&copy.ready&&!copy.defaultContentPending,"clone metadata");check(tree(library.game(copy).getParent()).equals(before)&&progress[0]>=large.length&&Files.isDirectory(library.game(copy).resolve("empty")),"clone contents/progress");
  Files.writeString(library.game(copy).resolve("saves/World/level.dat"),"CHANGED COPY");check(tree(folder).equals(before),"copy aliases source bytes");
  var second=library.duplicate(original,(m,d,t)->{},()->false);check(second.name.equals("Original Copy 2"),"unique name");
  int count=library.instances().size();boolean[] cancel={false};denied(()->library.duplicate(original,(m,d,t)->cancel[0]=true,()->cancel[0]));check(library.instances().size()==count&&tree(folder).equals(before),"cancel changed library/source");
  Files.createDirectory(library.root.resolve("library.json.tmp"));denied(()->library.duplicate(original,(m,d,t)->{},()->false));Files.delete(library.root.resolve("library.json.tmp"));check(library.instances().size()==count&&tree(folder).equals(before),"metadata failure rollback");
  Path outside=base.resolve("outside");Files.createDirectories(outside);Files.writeString(outside.resolve("keep"),"KEEP");Files.createSymbolicLink(library.game(original).resolve("link"),outside);denied(()->library.duplicate(original,(m,d,t)->{},()->false));Files.delete(library.game(original).resolve("link"));check(Files.readString(outside.resolve("keep")).equals("KEEP"),"followed source link");
  String orphan=UUID.randomUUID().toString();Path journal=library.root.resolve("pending-copy").resolve(orphan);Files.createDirectories(journal);Files.writeString(journal.resolve("id"),orphan);Path abandoned=library.root.resolve("instances").resolve(orphan);Files.createDirectories(abandoned);Files.writeString(abandoned.resolve("orphan"),"partial");new ProsperoLibrary(library.root);check(!Files.exists(abandoned)&&!Files.exists(journal),"precommit recovery");
  journal=library.root.resolve("pending-copy").resolve(copy.id);Files.createDirectories(journal.resolve("files"));Files.writeString(journal.resolve("id"),copy.id);Files.writeString(journal.resolve("files/partial"),"temporary");new ProsperoLibrary(library.root);check(!Files.exists(journal)&&Files.readString(library.game(copy).resolve("saves/World/level.dat")).equals("CHANGED COPY"),"committed copy lost during recovery");
  journal=library.root.resolve("pending-copy").resolve(copy.id);Files.createDirectories(journal);Files.writeString(journal.resolve("id"),copy.id);Files.move(library.game(copy).getParent(),journal.resolve("files"));new ProsperoLibrary(library.root);check(Files.readString(library.game(copy).resolve("saves/World/level.dat")).equals("CHANGED COPY")&&!Files.exists(journal),"committed staged files not restored");
  check(Files.readString(library.root.resolve("cache/shared")).equals("shared")&&Files.readString(library.root.resolve("account-fixture")).equals("private")&&!Files.exists(library.game(copy).resolve("account-fixture")),"global/account data copied or changed");
  var model=new ProsperoLauncher(new ProsperoAuth(),library.root,url->{throw new AssertionError("duplicate used network");});var modelLibrary=(ProsperoLibrary)get(model,"library");set(model,"detail",modelLibrary.instances().getFirst());set(model,"page",5);set(model,"top",false);set(model,"row",4);model.tick(0x20);check(model.tick(0)[15].equals("7"),"resource to duplicate navigation");model.tick(0x40);check(model.tick(0)[15].equals("6"),"duplicate to delete navigation");model.tick(0x10);check(model.tick(0)[15].equals("7"),"delete to duplicate navigation");model.tick(0x4000);
  long end=System.nanoTime()+10_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);check(model.tick(0)[11].equals("4")&&model.tick(0)[16].startsWith("Original Copy"),"duplicate button/result route");
  check(tree(folder).equals(before),"UI duplicate altered original");System.out.println("PASS actual duplicate:world/mods/config/Unicode packs/receipts/queues/empty dirs,unique identity/name/readiness,independent bytes,progress,cancel/save failure rollback,link rejection,pre/postcommit recovery,shared account/cache preservation,and async UI navigation without network");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-duplicate-')as d:
 w=Path(d);(w/'DuplicateCheck.java').write_text(s);cp=launcher_classpath();subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (r/'client/launcher/java').glob('*.java')],str(w/'DuplicateCheck.java')],check=True);subprocess.run([str(jdk/'bin/java'),'-Xverify:all','-cp',str(w)+':'+cp,'DuplicateCheck',str(w/'data')],check=True,timeout=60)
