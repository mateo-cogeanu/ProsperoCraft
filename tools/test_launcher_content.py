#!/usr/bin/env python3
"""Actual content transport, dependency resolution, queues, Fabric receipts and UI."""
import tempfile
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];JDK=java_home()
host_work = tempfile.TemporaryDirectory(prefix='prospero-content-');w=Path(host_work.name).resolve()
cp=launcher_classpath()
source=r'''
import com.google.gson.*;import java.nio.file.*;import java.io.*;import java.util.*;import java.security.*;
public class ContentCheck {
 static Map<String,byte[]> bodies=new HashMap<>();static int searches;
 static byte[] bytes(String s){return s.getBytes(java.nio.charset.StandardCharsets.UTF_8);}
 static String hash(byte[] b)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-512").digest(b));}
 static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
 interface Job{void run()throws Exception;}static void denied(Job job)throws Exception{try{job.run();throw new AssertionError("unexpected success");}catch(IOException|IllegalArgumentException expected){}}
 static void set(Object o,String field,Object v)throws Exception{var f=o.getClass().getDeclaredField(field);f.setAccessible(true);f.set(o,v);var c=o.getClass().getDeclaredField("cached");c.setAccessible(true);c.set(o,null);}
 static String version(String id,String project,String loader,String filename,String dep)throws Exception{
  byte[] b;
  if(filename.endsWith(".jar")){var out=new ByteArrayOutputStream();try(var jar=new java.util.zip.ZipOutputStream(out)){jar.putNextEntry(new java.util.zip.ZipEntry("fabric.mod.json"));jar.write(bytes("{\"schemaVersion\":1,\"id\":\""+project+"\",\"version\":\"1.0.0\"}"));jar.closeEntry();}b=out.toByteArray();}else b=bytes("original download "+project);String url="https://cdn.modrinth.com/data/"+project+"/"+java.net.URLEncoder.encode(filename,java.nio.charset.StandardCharsets.UTF_8).replace("+","%20");bodies.put(url,b);
  return "{\"id\":\""+id+"\",\"project_id\":\""+project+"\",\"game_versions\":[\"26.3\"],\"loaders\":[\""+loader+"\"],\"files\":[{\"primary\":true,\"filename\":\""+filename+"\",\"url\":\""+url+"\",\"size\":"+b.length+",\"hashes\":{\"sha512\":\""+hash(b)+"\"}}],\"dependencies\":["+dep+"]}";
 }
 static String required(String id){return "{\"dependency_type\":\"required\",\"project_id\":\""+id+"\",\"version_id\":null}";}
 static InputStream open(String url)throws Exception {
  if(url.startsWith(ProsperoModrinth.API+"search?")){searches++;String decoded=java.net.URLDecoder.decode(url,java.nio.charset.StandardCharsets.UTF_8);check(decoded.contains("index=downloads")&&decoded.contains("versions:26.3")&&decoded.contains("categories:fabric")&&(decoded.contains("offset=6")||decoded.contains("offset=0")),"search compatibility/sort/paging");return new ByteArrayInputStream(bytes("{\"total_hits\":9,\"hits\":[{\"project_id\":\"modA\",\"title\":\"Vitrail fixture\",\"description\":\"native Vulkan\",\"downloads\":100}]}"));}
  if(url.contains("/project/")){String project=url.substring(url.indexOf("/project/")+9).split("/")[0];byte[] b=bodies.get("version:"+project);if(b==null)throw new IOException("No fixture version");return new ByteArrayInputStream(bytes("["+new String(b,java.nio.charset.StandardCharsets.UTF_8)+"]"));}
  byte[] b=bodies.get(url);if(b==null)throw new IOException("Unexpected request "+url);return new ByteArrayInputStream(b);
 }
 public static void main(String[] args)throws Exception {
  Path root=Path.of(args[0]).toRealPath();Path game=root.resolve("instances/test/game");Files.createDirectories(game);Files.writeString(game.resolve("world-preserved"),"KEEP");var api=new ProsperoModrinth(new ProsperoDownloads(ContentCheck::open));
  bodies.put("version:modA",bytes(version("vA","modA","fabric","mod-a.jar",required("depB"))));bodies.put("version:depB",bytes(version("vB","depB","fabric","dep-b.jar","")));
  bodies.put("version:shaderA",bytes(version("vS","shaderA","iris","pack.zip","")));bodies.put("version:resourceA",bytes(version("vR","resourceA","minecraft","resources.zip","")));
  var search=api.search(ProsperoModrinth.Kind.MOD,"26.3","fabric","Vitrail",6,()->false);check(search.hits().size()==1&&search.total()==9,"search parse");check(api.search(ProsperoModrinth.Kind.MOD,"26.3","vanilla","",0,()->false).hits().isEmpty()&&searches==1,"vanilla mods network");
  api.toggle(game,new ProsperoModrinth.Selection("modA","A",ProsperoModrinth.Kind.MOD));api.toggle(game,new ProsperoModrinth.Selection("shaderA","Pack",ProsperoModrinth.Kind.SHADER));api.toggle(game,new ProsperoModrinth.Selection("resourceA","Textures",ProsperoModrinth.Kind.RESOURCE));check(new ProsperoModrinth().queue(game).size()==3,"persistent queue");
  Path vanillaGame=root.resolve("vanilla/game");Files.createDirectories(vanillaGame);api.toggle(vanillaGame,new ProsperoModrinth.Selection("modA","A",ProsperoModrinth.Kind.MOD));denied(()->api.downloadAll(vanillaGame,"26.3","vanilla",(s,d,t)->{},()->false));
  byte[] good=bodies.get("https://cdn.modrinth.com/data/depB/dep-b.jar");bodies.put("https://cdn.modrinth.com/data/depB/dep-b.jar",bytes("tamper"));denied(()->api.downloadAll(game,"26.3","fabric",(s,d,t)->{},()->false));check(!Files.exists(game.resolve("mods/mod-a.jar"))&&api.queue(game).size()==1&&Files.exists(game.resolve("shaderpacks/pack.zip"))&&Files.exists(game.resolve("resourcepacks/resources.zip")),"independent packs blocked or failed root removed from queue");bodies.put("https://cdn.modrinth.com/data/depB/dep-b.jar",good);
  denied(()->api.downloadAll(game,"26.3","fabric",(s,d,t)->{},()->true));check(api.queue(game).size()==1,"cancel cleared queue");
  api.toggle(game,new ProsperoModrinth.Selection("shaderA","Pack",ProsperoModrinth.Kind.SHADER));api.toggle(game,new ProsperoModrinth.Selection("resourceA","Textures",ProsperoModrinth.Kind.RESOURCE));
  Set<ProsperoModrinth.Kind> currentKinds=new HashSet<>();api.downloadAll(game,"26.3","fabric",(s,d,t)->{},()->false,f->currentKinds.add(f.kind()));check(currentKinds.size()==3,"current-download observer category coverage");check(api.queue(game).isEmpty()&&api.installed(game).files.size()==4,"dependencies/queue receipt");for(String path:List.of("mods/mod-a.jar","mods/dep-b.jar","shaderpacks/pack.zip","resourcepacks/resources.zip"))check(Files.isRegularFile(game.resolve(path)),"wrong content path "+path);
  check(Files.readString(game.resolve("world-preserved")).equals("KEEP"),"world changed");
  api.toggle(game,new ProsperoModrinth.Selection("modA","A",ProsperoModrinth.Kind.MOD));api.downloadAll(game,"26.3","fabric",(s,d,t)->{},()->false);check(api.installed(game).files.size()==4,"duplicate install");
  var bad=JsonParser.parseString(new String(bodies.get("version:modA"))).getAsJsonObject();bad.add("game_versions",JsonParser.parseString("[\"26.2\"]"));bodies.put("version:modA",bytes(bad.toString()));denied(()->api.version("modA","",ProsperoModrinth.Kind.MOD,"26.3",()->false));
  denied(()->ProsperoDownloads.safe("https://cdn.modrinth.com.evil.invalid/file"));denied(()->ProsperoDownloads.safe("http://cdn.modrinth.com/file"));denied(()->ProsperoDownloads.safe("https://u@cdn.modrinth.com/file"));denied(()->ProsperoDownloads.safe("https://api.modrinth.com:443/file"));
  bad.getAsJsonArray("files").get(0).getAsJsonObject().addProperty("filename","../escape.jar");denied(()->api.file(bad,ProsperoModrinth.Kind.MOD));
  Path linked=root.resolve("linked");Files.createSymbolicLink(linked,game);denied(()->ProsperoDownloads.noLinks(linked.resolve("mods/a.jar")));
  Path modelRoot=root.resolve("library");var lib=new ProsperoLibrary(modelRoot);var vanilla=lib.add("Vanilla","26.3",1);var fabric=lib.add("Fabric","26.3",16,"fabric");lib.settings().showIntro=false;lib.save();check(new ProsperoLibrary(modelRoot).instances().get(1).loader.equals("fabric"),"loader not persistent");
  var old=JsonParser.parseString(Files.readString(modelRoot.resolve("library.json"))).getAsJsonObject();old.getAsJsonArray("instances").get(0).getAsJsonObject().remove("loader");Files.writeString(modelRoot.resolve("library.json"),old.toString());check(new ProsperoLibrary(modelRoot).instances().get(0).loader.equals("vanilla"),"old library migration");denied(()->lib.add("NeoForge","26.3",1,"neoforge"));
  var model=new ProsperoLauncher(new ProsperoAuth(),modelRoot,url->{throw new IOException("fixture offline");});set(model,"page",1);set(model,"row",1);model.tick(0x4000);check(model.tick(0)[11].equals("10")&&model.tick(0)[83].equals("3"),"loader dropdown");model.tick(0x40);model.tick(0x4000);check(model.tick(0)[82].equals("Fabric"),"Fabric choice");model.tick(0x4000);model.tick(0x40);model.tick(0x4000);check(model.tick(0)[11].equals("10")&&model.tick(0)[2].contains("coming soon"),"NeoForge enabled");model.tick(0x2000);
  set(model,"modrinth",api);set(model,"detail",fabric);set(model,"page",5);set(model,"row",2);model.tick(0x4000);
  long end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);
  check(model.tick(0)[11].equals("12")&&model.tick(0)[93].equals("1"),"Mods browser route");set(model,"row",4);model.tick(0x4000);check(model.tick(0)[85].startsWith("[X]")&&model.tick(0)[91].equals("1"),"checkbox queue state");check(api.queue(lib.game(fabric)).size()==1&&api.queue(lib.game(vanilla)).isEmpty(),"instance queue leaked");
  set(model,"row",0);model.tick(0x4000);check(model.tick(0)[11].equals("6"),"search keyboard route");set(model,"keyboard","Vitrail");model.tick(0x8000);end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);check(model.tick(0)[11].equals("12")&&model.tick(0)[92].equals("Vitrail"),"search confirm");model.tick(0x2000);check(model.tick(0)[11].equals("5")&&model.tick(0)[15].equals("2"),"browser back route");
  check(new ProsperoModrinth(api.download).local(game,ProsperoModrinth.Kind.MOD).size()==2,"installed list after reopen");
  check(api.local(game,ProsperoModrinth.Kind.SHADER).size()==1&&api.local(game,ProsperoModrinth.Kind.RESOURCE).size()==1,"pack inventory");
  Files.writeString(game.resolve("mods/manual.jar"),"manual");Files.createSymbolicLink(game.resolve("mods/linked.jar"),root.resolve("outside.jar"));
  check(api.local(game,ProsperoModrinth.Kind.MOD).size()==3,"manual file missing or symlink listed");
  Path pack=game.resolve("vitrail/pack.txt");Files.createDirectories(pack.getParent());String settings="pack=BSL.zip\nenabled=true\nshadowdistance=128\nrenderscale=100\nshadowmapscale=100\ncustom=keep\n";Files.writeString(pack,settings);
  check(ProsperoShaderSettings.toggle(game)==50&&ProsperoShaderSettings.scale(game)==50,"half shadows");
  check(Files.readString(pack).equals(settings.replace("shadowmapscale=100","shadowmapscale=50")),"other settings changed");
  check(Files.readString(pack.resolveSibling("pack.before-prospero106.txt")).equals(settings),"shadow backup");check(ProsperoShaderSettings.toggle(game)==100&&Files.readString(pack).equals(settings),"full shadows restore");
  Files.createDirectories(lib.game(fabric).resolve("mods"));Files.writeString(lib.game(fabric).resolve("mods/manual.jar"),"original");
  set(model,"page",12);set(model,"row",3);model.tick(0x20);check(model.tick(0)[15].equals("10"),"Installed horizontal navigation");model.tick(0x4000);
  end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);
  check(model.tick(0)[103].equals("INSTALLED")&&model.tick(0)[93].equals("1")&&model.tick(0)[85].contains("manual.jar"),"Installed UI actual folder");
  model.tick(0x4000);end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);check(model.tick(0)[103].equals("BROWSE"),"return Browse");
  set(model,"contentKind",ProsperoModrinth.Kind.SHADER);set(model,"row",3);model.tick(0x20);check(model.tick(0)[15].equals("11"),"shadow horizontal navigation");model.tick(0x4000);check(model.tick(0)[95].equals("SHADOWS: 50%")&&ProsperoShaderSettings.scale(lib.game(fabric))==50,"shadow UI persist");model.tick(0x20);check(model.tick(0)[15].equals("10"),"shadow to Installed");
  set(model,"contentKind",ProsperoModrinth.Kind.MOD);set(model,"contentInstalled",true);set(model,"localContent",api.local(lib.game(fabric),ProsperoModrinth.Kind.MOD));set(model,"contentOffset",0);set(model,"page",12);set(model,"row",4);
  model.tick(0x20);check(model.tick(0)[15].equals("20"),"Uninstall button right");model.tick(0x4000);check(model.tick(0)[11].equals("14"),"Uninstall confirmation missing");model.tick(0x2000);check(Files.exists(lib.game(fabric).resolve("mods/manual.jar")),"Cancel removed file");
  set(model,"row",20);model.tick(0x4000);model.tick(0x20);model.tick(0x4000);end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);check(!Files.exists(lib.game(fabric).resolve("mods/manual.jar"))&&model.tick(0)[11].equals("12"),"UI uninstall failed");
  var packItem=api.local(game,ProsperoModrinth.Kind.SHADER).getFirst();check(api.uninstall(game,packItem)&&!Files.exists(game.resolve("shaderpacks/pack.zip")),"shader uninstall");check(api.installed(game).files.stream().noneMatch(f->f.kind()==ProsperoModrinth.Kind.SHADER),"stale receipt after uninstall");
  var resource=api.local(game,ProsperoModrinth.Kind.RESOURCE).getFirst();api.uninstall(game,resource);check(!Files.exists(game.resolve("resourcepacks/resources.zip"))&&Files.exists(game.resolve("mods/mod-a.jar"))&&Files.readString(game.resolve("world-preserved")).equals("KEEP"),"uninstall changed other category/world");
  denied(()->api.uninstall(game,new ProsperoModrinth.Local("escape","../outside.jar","",ProsperoModrinth.Kind.MOD)));denied(()->api.uninstall(game,new ProsperoModrinth.Local("link","linked.jar","",ProsperoModrinth.Kind.MOD)));
  Path receiptPath=game.getParent().resolve("content-installed.json"),tmp=receiptPath.resolveSibling("content-installed.json.tmp");Files.createDirectory(tmp);var manual=api.local(game,ProsperoModrinth.Kind.MOD).stream().filter(f->f.filename().equals("manual.jar")).findFirst().orElseThrow();denied(()->api.uninstall(game,manual));check(Files.readString(game.resolve("mods/manual.jar")).equals("manual"),"failed metadata did not roll back exact file");Files.delete(tmp);
  check(ProsperoModrinth.validFilename("§lC418 §rSongs Only.zip",ProsperoModrinth.Kind.RESOURCE)&&ProsperoModrinth.validFilename("日本語 [Pack]!.zip",ProsperoModrinth.Kind.RESOURCE),"safe Unicode filenames");
  for(String name:List.of("../pack.zip","sub/pack.zip","sub\\pack.zip",".hidden.zip","C:pack.zip","bad\u0000.zip","bad\n.zip","bad\u202e.zip","é".repeat(89)+".zip"))check(!ProsperoModrinth.validFilename(name,ProsperoModrinth.Kind.RESOURCE),"unsafe filename accepted");
  Path unicodeGame=root.resolve("unicode/game");Files.createDirectories(unicodeGame);bodies.put("version:unicode",bytes(version("vUnicode","unicode","minecraft","§lC418 §rSongs Only.zip","")));api.toggle(unicodeGame,new ProsperoModrinth.Selection("unicode","C418",ProsperoModrinth.Kind.RESOURCE));api.downloadAll(unicodeGame,"26.3","fabric",(m,d,t)->{},()->false);check(Files.exists(unicodeGame.resolve("resourcepacks/§lC418 §rSongs Only.zip"))&&new ProsperoModrinth().installed(unicodeGame).files.size()==1,"Unicode receipt roundtrip");api.uninstall(unicodeGame,api.local(unicodeGame,ProsperoModrinth.Kind.RESOURCE).getFirst());check(!Files.exists(unicodeGame.resolve("resourcepacks/§lC418 §rSongs Only.zip")),"Unicode uninstall");
  check(!vanilla.defaultContentPending&&fabric.defaultContentPending,"new instance default policy");lib.defaultContentInstalled(fabric);check(!new ProsperoLibrary(modelRoot).instances().get(1).defaultContentPending,"default completion not persisted");
  var migrated=JsonParser.parseString(Files.readString(modelRoot.resolve("library.json"))).getAsJsonObject();for(var entry:migrated.getAsJsonArray("instances"))entry.getAsJsonObject().remove("defaultContentPending");Files.writeString(modelRoot.resolve("library.json"),migrated.toString());check(!new ProsperoLibrary(modelRoot).instances().get(1).defaultContentPending,"existing instance forced to defaults");
  check(ProsperoModrinth.defaultMods("vanilla").isEmpty()&&ProsperoModrinth.defaultMods("fabric").getFirst().project().equals("DOUdJVEm")&&ProsperoModrinth.defaultMods("neoforge").getFirst().project().equals("DOUdJVEm"),"Fabric/futureNeoForge default plan");
  System.out.println("PASS real content pipeline: exact filters/sort/paging; persistent multi-category queue; recursive required dependencies; all hashes before publication; failure/cancel retention; instance folders; duplicate guard; wrong-version/path/host/link rejection; vanilla migration and loader dropdown/disabled NeoForge");
 }
}
'''
(w/'ContentCheck.java').write_text(source)
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'ContentCheck.java')],check=True)
data=w/'data'
import shutil
shutil.rmtree(data,ignore_errors=True);data.mkdir()
subprocess.run([str(JDK/'bin/java'),'-Xcheck:jni','-Xverify:all','-cp',str(w)+':'+cp,'ContentCheck',str(data)],check=True,timeout=60)
