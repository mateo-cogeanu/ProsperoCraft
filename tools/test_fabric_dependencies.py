#!/usr/bin/env python3
"""Actual upstream predicates plus manifest/nested-module dependency auto downloads."""
import tempfile
from pathlib import Path
from host_toolchain import java_home, launcher_classpath, dependency
import subprocess,json,shutil
ROOT=Path(__file__).resolve().parents[1];JDK=java_home();host_work = tempfile.TemporaryDirectory(prefix='prospero-dependencies-');w=Path(host_work.name).resolve()
loader=dependency('fabric-loader')
source=r'''
import com.google.gson.*;import java.nio.file.*;import java.io.*;import java.util.*;import java.util.zip.*;import java.security.*;
public class DependencyCheck {
 static Map<String,byte[]> network=new HashMap<>();static int reads;
 static byte[] bytes(String s){return s.getBytes(java.nio.charset.StandardCharsets.UTF_8);}
 static byte[] jar(String id,String version,String depends,byte[] nested)throws Exception {var out=new ByteArrayOutputStream();try(var z=new ZipOutputStream(out)){z.putNextEntry(new ZipEntry("fabric.mod.json"));z.write(bytes("{\"id\":\""+id+"\",\"version\":\""+version+"\",\"depends\":"+depends+(nested==null?"":",\"jars\":[{\"file\":\"META-INF/jars/keys.jar\"}]")+"}"));z.closeEntry();if(nested!=null){z.putNextEntry(new ZipEntry("META-INF/jars/keys.jar"));z.write(nested);z.closeEntry();}}return out.toByteArray();}
 static byte[] largeBundledLibrary(byte[] child)throws Exception {
  var out=new ByteArrayOutputStream();
  try(var zip=new ZipOutputStream(out)){
   zip.setLevel(0);
   zip.putNextEntry(new ZipEntry("unrelated.jar"));
   byte[] block=new byte[8192];
   for(int i=0;i<2560;i++)zip.write(block);
   zip.closeEntry();
   zip.putNextEntry(new ZipEntry("META-INF/jars/child.jar"));zip.write(child);zip.closeEntry();
   zip.putNextEntry(new ZipEntry("fabric.mod.json"));
   zip.write(bytes("{\"id\":\"large_library\",\"version\":\"1.0\",\"jars\":[{\"file\":\"META-INF/jars/child.jar\"}]}"));
   zip.closeEntry();
  }
  return out.toByteArray();
 }
 static void version(String project,String version,String filename,byte[] jar,String deps)throws Exception {String url="https://cdn.modrinth.com/data/"+project+"/"+version+"/"+filename;network.put(url,jar);String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-512").digest(jar));String metadata="{\"id\":\""+version+"\",\"project_id\":\""+project+"\",\"game_versions\":[\"26.3\"],\"loaders\":[\"fabric\"],\"dependencies\":"+deps+",\"files\":[{\"filename\":\""+filename+"\",\"url\":\""+url+"\",\"primary\":true,\"size\":"+jar.length+",\"hashes\":{\"sha512\":\""+hash+"\"}}]}";network.put("meta:"+project,bytes("["+metadata+"]"));network.put(ProsperoModrinth.API+"version/"+version,bytes(metadata));}
 static InputStream open(String url)throws Exception{reads++;byte[] b=network.get(url);if(b==null&&url.contains("/project/"))b=network.get("meta:"+url.split("/project/")[1].split("/")[0]);if(b==null)throw new IOException("Unexpected request "+url);return new ByteArrayInputStream(b);}
 static void check(boolean yes,String why){if(!yes)throw new AssertionError(why);}
 public static void main(String[]args)throws Exception {Path root=Path.of(args[0]),game=root.resolve("game");Files.createDirectories(game);Files.writeString(game.resolve("world-marker"),"KEEP");
  Path large=root.resolve("large-bundle.jar");
  byte[] child=jar("bundled_child","1.0","{}",null);
  Files.write(large,jar("large_root","1.0","{}",largeBundledLibrary(child)));
  check(ProsperoDependencies.providedIds(large).containsAll(Set.of("large_root","large_library","bundled_child")),"large nested library or reverse manifest order rejected");
  byte[] unchanged=Files.readAllBytes(large);
  ProsperoDependencies.rootModule(large);
  check(Arrays.equals(unchanged,Files.readAllBytes(large)),"metadata scan changed archive");
  Path oversized=root.resolve("oversized-manifest.jar");
  try(var zip=new ZipOutputStream(Files.newOutputStream(oversized))){
   zip.putNextEntry(new ZipEntry("fabric.mod.json"));zip.write(new byte[128*1024+1]);zip.closeEntry();
  }
  try{ProsperoDependencies.providedIds(oversized);throw new AssertionError("oversized manifest allowed");}
  catch(IOException expected){check(expected.getMessage().contains("manifest"),"wrong manifest bound");}
  Path bomb=root.resolve("scan-budget.jar");
  var bombBytes=new ByteArrayOutputStream();
  try(var zip=new ZipOutputStream(bombBytes)){
   zip.putNextEntry(new ZipEntry("padding"));
   byte[] block=new byte[65536];
   for(int i=0;i<8193;i++)zip.write(block);
   zip.closeEntry();
  }
  Files.write(bomb,jar("scan_budget","1.0","{}",bombBytes.toByteArray()));
  try{ProsperoDependencies.providedIds(bomb);throw new AssertionError("scan budget ignored");}
  catch(IOException expected){check(expected.getMessage().contains("512 MiB"),"wrong scan budget error");}
  try(var versions=new ProsperoDependencies.Versions(Path.of(args[1]),"0.20.1")){
   Path compat=root.resolve("java-compat"),cobble=compat.resolve("mods/cobblemon.jar");Files.createDirectories(cobble.getParent());
   byte[] cobbleBytes=jar("cobblemon","1.8.4+1.21.1","{\"java\":\"21\",\"fabric-api\":\">=0.116.6\"}",null);Files.write(cobble,cobbleBytes);
   var needs=ProsperoDependencies.missing(List.of(cobble),"1.21.1",versions);
   check(needs.size()==1&&needs.getFirst().id().equals("fabric-api"),"scoped Java override removed another dependency");
   for(String gameVersion:List.of("1.21.2","26.3"))try{ProsperoDependencies.missing(List.of(cobble),gameVersion,versions);throw new AssertionError("wrong game Java override");}catch(IOException expected){check(expected.getMessage().contains("requires java"),"wrong scope error");}
   Path other=compat.resolve("other.jar");Files.write(other,jar("other","1.0","{\"java\":\"21\"}",null));
   try{ProsperoDependencies.missing(List.of(other),"1.21.1",versions);throw new AssertionError("global Java spoof");}catch(IOException expected){}
   Path config=compat.resolve("config"),override=config.resolve("fabric_loader_dependencies.json");Files.createDirectories(config);
   String userConfig="{\"version\":1,\"overrides\":{\"other\":{\"+suggests\":{\"optional\":\"*\"}}}}";Files.writeString(override,userConfig);
   var userRule=JsonParser.parseString(userConfig).getAsJsonObject().getAsJsonObject("overrides").get("other");
   ProsperoDependencies.prepareJavaCompatibility(List.of(cobble),compat,"1.21.1");
   String configured=Files.readString(override);
   check(JsonParser.parseString(configured).getAsJsonObject().getAsJsonObject("overrides").get("other").equals(userRule),"user override altered");
   ProsperoDependencies.prepareJavaCompatibility(List.of(cobble),compat,"1.21.1");check(configured.equals(Files.readString(override)),"override not idempotent");
   Class<?> overridesType=versions.loader.loadClass("net.fabricmc.loader.impl.metadata.DependencyOverrides"),versionsType=versions.loader.loadClass("net.fabricmc.loader.impl.metadata.VersionOverrides");
   Object overrides=overridesType.getConstructor(Path.class).newInstance(config);
   var parser=versions.loader.loadClass("net.fabricmc.loader.impl.metadata.ModMetadataParser").getMethod("parseMetadata",InputStream.class,String.class,List.class,versionsType,overridesType,boolean.class);
   String manifest="{\"schemaVersion\":1,\"id\":\"cobblemon\",\"version\":\"1.8.4+1.21.1\",\"depends\":{\"java\":\"21\",\"fabric-api\":\">=0.116.6\"}}";
   Object metadata=parser.invoke(null,new ByteArrayInputStream(bytes(manifest)),"fixture.jar",List.of(),versionsType.getConstructor().newInstance(),overrides,false);
   Class<?> metadataType=versions.loader.loadClass("net.fabricmc.loader.api.metadata.ModMetadata"),depType=versions.loader.loadClass("net.fabricmc.loader.api.metadata.ModDependency"),versionType=versions.loader.loadClass("net.fabricmc.loader.api.Version");
   var dependencies=(Collection<?>)metadataType.getMethod("getDependencies").invoke(metadata);boolean sawJava=false,sawApi=false;
   for(Object dep:dependencies){String id=(String)depType.getMethod("getModId").invoke(dep);if(id.equals("java")){sawJava=true;var match=depType.getMethod("matches",versionType);check((Boolean)match.invoke(dep,versions.parseVersion.invoke(null,"25"))&&(Boolean)match.invoke(dep,versions.parseVersion.invoke(null,"21"))&&!(Boolean)match.invoke(dep,versions.parseVersion.invoke(null,"17"))&&!(Boolean)match.invoke(dep,versions.parseVersion.invoke(null,"26")),"Fabric runtime override range wrong: "+dep+" config="+configured);}if(id.equals("fabric-api"))sawApi=true;}
   check(sawJava&&sawApi,"Fabric parser lost required dependency");
   ProsperoDependencies.prepareJavaCompatibility(List.of(),compat,"1.21.1");
   check(!JsonParser.parseString(Files.readString(override)).getAsJsonObject().getAsJsonObject("overrides").has("cobblemon"),"stale override retained after disable/removal");
   check(!Files.exists(config.resolve(".prosperocraft-cobblemon-java")),"stale ownership retained");
   check(Arrays.equals(cobbleBytes,Files.readAllBytes(cobble)),"Java compatibility modified original mod");
   Files.writeString(override,"{\"version\":1,\"overrides\":{\"cobblemon\":{\"+depends\":{\"java\":\"17\"}}}}");String customJavaRule=Files.readString(override);
   try{ProsperoDependencies.prepareJavaCompatibility(List.of(cobble),compat,"1.21.1");throw new AssertionError("user rule silently replaced");}catch(IOException expected){}
   check(customJavaRule.equals(Files.readString(override)),"custom rule changed");
   Files.delete(override);Path target=root.resolve("untouched-config");Files.writeString(target,"KEEP");Files.createSymbolicLink(override,target);
   try{ProsperoDependencies.prepareJavaCompatibility(List.of(cobble),compat,"1.21.1");throw new AssertionError("override link followed");}catch(IOException expected){}
   check(Files.readString(target).equals("KEEP"),"symlink target changed");
   check(System.getProperty("java.version").startsWith("25"),"global Java property changed");
   System.out.println("PASS scoped Cobblemon Java25 preflight and genuine Fabric metadata override; unrelated requirements/user rules/original bytes preserved, idempotence, removal cleanup and link rejection");
   Path defaults=root.resolve("defaults/game");Files.createDirectories(defaults);var defaultsClient=new ProsperoModrinth(new ProsperoDownloads(DependencyCheck::open));
   version("defaultdep","vDefaultDep","dependency.jar",jar("defaultdep","1.0","{}",null),"[]");version("DOUdJVEm","vControlify","controlify.jar",jar("controlify","1.0","{\"defaultdep\":\"*\"}",null),"[{\"dependency_type\":\"required\",\"project_id\":\"defaultdep\",\"version_id\":null}]");
   defaultsClient.toggle(defaults,new ProsperoModrinth.Selection("userQueued","Keep queued",ProsperoModrinth.Kind.RESOURCE));
   defaultsClient.installDefaults(defaults,"26.3","fabric",versions,(m,d,t)->{},()->false);check(Files.exists(defaults.resolve("mods/controlify.jar"))&&Files.exists(defaults.resolve("mods/dependency.jar"))&&defaultsClient.queue(defaults).size()==1,"defaults missing dependency or changed user queue");
   defaultsClient.installDefaults(defaults,"26.3","fabric",versions,(m,d,t)->{},()->false);check(defaultsClient.installed(defaults).files.size()==2,"duplicate defaults");
   var controlify=defaultsClient.local(defaults,ProsperoModrinth.Kind.MOD).stream().filter(i->i.project().equals("DOUdJVEm")).findFirst().orElseThrow();
   defaultsClient.uninstall(defaults,controlify);
   int afterUninstall=reads;
   defaultsClient.installDefaults(defaults,"26.3","fabric",versions,(m,d,t)->{},()->false);
   check(!Files.exists(defaults.resolve("mods/controlify.jar"))&&reads==afterUninstall,"default setup restored removed Controlify");
   Path custom=root.resolve("manual/game");Files.createDirectories(custom.resolve("mods"));
   Path customJar=custom.resolve("mods/custom-controller.jar");byte[] customMod=jar("controlify","9.0.0","{}",null);Files.write(customJar,customMod);
   defaultsClient.installDefaults(custom,"26.3","fabric",versions,(m,d,t)->{},()->false);
   check(Arrays.equals(customMod,Files.readAllBytes(customJar))&&reads==afterUninstall,"default setup duplicated a manually installed Controlify");
   var manualController=defaultsClient.local(custom,ProsperoModrinth.Kind.MOD).getFirst();
   defaultsClient.toggleEnabled(custom,manualController);int disabledControllerReads=reads;
   defaultsClient.installDefaults(custom,"26.3","fabric",versions,(m,d,t)->{},()->false);
   check(!defaultsClient.hasControlify(custom)&&reads==disabledControllerReads&&!Files.exists(customJar),"disabled Controlify was active or reinstalled");
   defaultsClient.toggleEnabled(custom,defaultsClient.local(custom,ProsperoModrinth.Kind.MOD).getFirst());
   check(defaultsClient.hasControlify(custom),"Controlify reenable not detected");
   defaultsClient.uninstall(custom,defaultsClient.local(custom,ProsperoModrinth.Kind.MOD).getFirst());
   defaultsClient.installDefaults(custom,"26.3","fabric",versions,(m,d,t)->{},()->false);
   check(defaultsClient.local(custom,ProsperoModrinth.Kind.MOD).isEmpty()&&reads==afterUninstall,"manually removed Controlify reappeared");
   check(versions.accepts("0.20.1",List.of(">=0.18.4"))&&versions.accepts("26.3",List.of("~26.3"))&&!versions.accepts("1.0.0",List.of(">=2")),"official version predicates");
   byte[] mod=jar("vitrail","0.13.0-beta","{\"fabric-key-mapping-api-v1\":\"*\",\"minecraft\":\"~26.3\",\"java\":\">=25\"}",null);
   byte[] api=jar("fabric-api","0.165.0+26.3","{\"fabricloader\":\">=0.18\"}",jar("fabric-key-mapping-api-v1","3.0.0","{}",null));
   version("vitrail","vRoot","vitrail.jar",mod,"[]");version("P7dR8mSH","vAPI","fabric-api.jar",api,"[]");
   var client=new ProsperoModrinth(new ProsperoDownloads(DependencyCheck::open));client.toggle(game,new ProsperoModrinth.Selection("vitrail","Vitrail",ProsperoModrinth.Kind.MOD));
   client.downloadAll(game,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
   check(Files.exists(game.resolve("mods/fabric-api.jar"))&&client.installed(game).files.size()==2&&client.queue(game).isEmpty(),"JAR-only required Fabric API not installed");
   check(ProsperoDependencies.missing(List.of(game.resolve("mods/vitrail.jar"),game.resolve("mods/fabric-api.jar")),"26.3",versions).isEmpty(),"nested API module not recognized");
   Path bundled=game.resolve("mods/bundled.jar");Files.write(bundled,jar("bundled","1.0.0","{}",jar("fabric-key-mapping-api-v1","2.0.0","{}",null)));
   var variants=new ArrayList<Path>(List.of(game.resolve("mods/vitrail.jar"),game.resolve("mods/fabric-api.jar"),bundled));check(ProsperoDependencies.missing(variants,"26.3",versions).isEmpty(),"compatible nested provider versions rejected");Files.delete(bundled);
   var disabledAPI=client.local(game,ProsperoModrinth.Kind.MOD).stream().filter(f->f.filename().equals("fabric-api.jar")).findFirst().orElseThrow();
   client.toggleEnabled(game,disabledAPI);int disabledReads=reads;
   try{client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);throw new AssertionError("disabled dependency reinstalled");}
   catch(IOException expected){check(expected.getMessage().contains("disabled mod fabric-key-mapping-api-v1"),"disabled nested dependency not explained");}
   check(reads==disabledReads&&!Files.exists(game.resolve("mods/fabric-api.jar")),"disabled repair used network or restored jar");
   disabledAPI=client.local(game,ProsperoModrinth.Kind.MOD).stream().filter(f->f.filename().equals("fabric-api.jar")).findFirst().orElseThrow();
   client.toggleEnabled(game,disabledAPI);
   var disabledRoot=client.local(game,ProsperoModrinth.Kind.MOD).stream().filter(f->f.filename().equals("vitrail.jar")).findFirst().orElseThrow();
   client.toggleEnabled(game,disabledRoot);
   client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);
   check(reads==disabledReads&&!Files.exists(game.resolve("mods/vitrail.jar")),"disabled root loaded or caused downloads");
   disabledRoot=client.local(game,ProsperoModrinth.Kind.MOD).stream().filter(f->f.filename().equals("vitrail.jar")).findFirst().orElseThrow();
   client.toggleEnabled(game,disabledRoot);
   int before=reads;client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);check(reads==before,"healthy launch used network");
   var entry=client.local(game,ProsperoModrinth.Kind.MOD).stream().filter(i->i.project().equals("P7dR8mSH")).findFirst().orElseThrow();client.uninstall(game,entry);
   try{client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,true);throw new AssertionError("offline missing dependency allowed");}catch(IOException expected){}
   client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);check(Files.exists(game.resolve("mods/fabric-api.jar")),"old instance repair failed");
   Files.delete(game.resolve("mods/fabric-api.jar"));client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);check(Files.exists(game.resolve("mods/fabric-api.jar")),"missing dependency with retained receipt not restored");
   check(Files.readString(game.resolve("world-marker")).equals("KEEP"),"world changed");
   byte[] conflict=jar("other","1.0.0","{\"fabric-key-mapping-api-v1\":\">=99\"}",null);Files.write(game.resolve("mods/conflict.jar"),conflict);
   try{client.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);throw new AssertionError("wrong dependency version accepted");}catch(IOException expected){check(expected.getMessage().contains("fabric-key-mapping-api-v1")&&expected.getMessage().contains(">=99"),"conflict not explained: "+expected.getMessage());}
   check(Arrays.equals(conflict,Files.readAllBytes(game.resolve("mods/conflict.jar"))),"conflict overwritten");Files.delete(game.resolve("mods/conflict.jar"));
   byte[] unknown=jar("unknown","1.0","{\"unmapped-library\":\"*\"}",null);version("unknown","vUnknown","unknown.jar",unknown,"[]");client.toggle(game,new ProsperoModrinth.Selection("unknown","Unknown",ProsperoModrinth.Kind.MOD));
   try{client.downloadAll(game,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("missing unknown dependency allowed");}catch(IOException expected){check(expected.getMessage().contains("unmapped-library"),"missing dependency not named");}
   check(!Files.exists(game.resolve("mods/unknown.jar"))&&client.queue(game).size()==1,"unresolved dependency published or queue lost");


   ProsperoDependencies.verifyVulkan(List.of(game.resolve("mods/vitrail.jar"),game.resolve("mods/fabric-api.jar")));
   Path renamed=root.resolve("renamed-shader.jar");byte[] irisBytes=jar("iris","1.11.7+mc26.3","{}",null);Files.write(renamed,irisBytes);
   try{ProsperoDependencies.verifyVulkan(List.of(renamed));throw new AssertionError("Iris Vulkan launch allowed");}catch(IOException expected){check(expected.getMessage().contains("OpenGL")&&expected.getMessage().contains("Vitrail")&&expected.getMessage().contains("Uninstall"),"Iris launch explanation missing");}
   ProsperoDependencies.verifyGraphics(List.of(renamed),true,"26.3"); // User-authorized original Iris testing on genuine Zink/OpenGL.
   check(Arrays.equals(irisBytes,Files.readAllBytes(renamed)),"Iris guard modified mod");
   Files.write(renamed,jar("shader-wrapper","1.0","{}",irisBytes));
   byte[] nestedIris=Files.readAllBytes(renamed);ProsperoDependencies.verifyGraphics(List.of(renamed),true,"26.3");check(Arrays.equals(nestedIris,Files.readAllBytes(renamed)),"nested Iris testing altered mod");
   try{ProsperoDependencies.verifyVulkan(List.of(renamed));throw new AssertionError("nested Iris launch allowed");}catch(IOException expected){check(expected.getMessage().contains("OpenGL"),"nested Iris not identified");}

   Path launchRoot=root.resolve("launcher-guard");var launchLibrary=new ProsperoLibrary(launchRoot);var launchInstance=launchLibrary.add("Iris test","26.3",0,"fabric");Path launchMods=launchLibrary.game(launchInstance).resolve("mods");Files.createDirectories(launchMods);Files.write(launchMods.resolve("arbitrary-name.jar"),irisBytes);
   var launcher=new ProsperoLauncher(new ProsperoAuth(),launchRoot,url->{throw new AssertionError("guard attempted download");});
   var prepare=ProsperoLauncher.class.getDeclaredMethod("repairDependencies",ProsperoLibrary.Instance.class,int.class,boolean.class);prepare.setAccessible(true);
   for(boolean offline:List.of(false,true))try{prepare.invoke(launcher,launchInstance,0,offline);throw new AssertionError("launcher accepted Iris");}catch(java.lang.reflect.InvocationTargetException expected){check(expected.getCause() instanceof IOException&&expected.getCause().getMessage().contains("OpenGL"),"launcher failed before compatibility explanation");}
   var launched=ProsperoLauncher.class.getDeclaredField("launch");launched.setAccessible(true);check(!launched.getBoolean(launcher)&&Arrays.equals(irisBytes,Files.readAllBytes(launchMods.resolve("arbitrary-name.jar"))),"guard handed off or modified files");
   Files.delete(launchMods.resolve("arbitrary-name.jar"));
   Path vitrailJar=launchMods.resolve("manual-shaders.jar"),sodiumJar=launchMods.resolve("manual-renderer.jar");
   byte[] vitrailBytes=jar("vitrail","0.13.0-beta","{\"sodium\":\"0.9.x\"}",null);
   Files.write(vitrailJar,vitrailBytes);
   for(String bad:List.of("0.9.3-beta.5+mc26.3","0.9.3+mc26.3","0.9.4-beta.1+mc26.3")){
    byte[] sodiumBytes=jar("sodium",bad,"{}",null);Files.write(sodiumJar,sodiumBytes);
    for(boolean offline:List.of(false,true))try{prepare.invoke(launcher,launchInstance,0,offline);throw new AssertionError("launcher accepted conflicting renderer");}
    catch(java.lang.reflect.InvocationTargetException expected){check(expected.getCause() instanceof IOException&&expected.getCause().getMessage().contains("Sodium with 0.9.2"),"missing Vitrail workaround");}
    ProsperoDependencies.verifyGraphics(List.of(vitrailJar,sodiumJar),true,"26.3");
    ProsperoDependencies.verifyGraphics(List.of(vitrailJar,sodiumJar),false,"26.2");
    ProsperoDependencies.verifyGraphics(List.of(sodiumJar),false,"26.3");
    check(!launched.getBoolean(launcher)&&Arrays.equals(sodiumBytes,Files.readAllBytes(sodiumJar)),"Vitrail guard handed off or modified Sodium");
   }
   Files.write(sodiumJar,jar("sodium","0.9.2+mc26.3","{}",null));
   ProsperoDependencies.verifyGraphics(List.of(vitrailJar,sodiumJar),false,"26.3");
   check(Arrays.equals(vitrailBytes,Files.readAllBytes(vitrailJar)),"Vitrail mod modified");
   version("AANobbMI","bAZQdGpg","sodium-092.jar",jar("sodium","0.9.2+mc26.3","{}",null),"[]");
   version("AANobbMI","6etTPjD5","sodium-094.jar",jar("sodium","0.9.4-beta.1+mc26.3","{}",null),"[]");
   version("oSIKhgz3","Q3nKuPKJ","vitrail-013.jar",vitrailBytes,"[{\"project_id\":\"AANobbMI\",\"dependency_type\":\"required\"}]");
   for(boolean reverse:List.of(false,true)){
    Path shaderGame=root.resolve("vitrail-queue-"+reverse+"/game");Files.createDirectories(shaderGame);
    for(String project:reverse?List.of("AANobbMI","oSIKhgz3"):List.of("oSIKhgz3","AANobbMI"))
     client.toggle(shaderGame,new ProsperoModrinth.Selection(project,project,ProsperoModrinth.Kind.MOD));
    client.downloadAll(shaderGame,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
    check(Files.isRegularFile(shaderGame.resolve("mods/sodium-092.jar"))&&!Files.exists(shaderGame.resolve("mods/sodium-094.jar")),"Vitrail queue selected incompatible Sodium");
   }
   Path sodiumOnly=root.resolve("sodium-only/game");Files.createDirectories(sodiumOnly);
   client.toggle(sodiumOnly,new ProsperoModrinth.Selection("AANobbMI","Sodium",ProsperoModrinth.Kind.MOD));
   client.downloadAll(sodiumOnly,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
   check(Files.isRegularFile(sodiumOnly.resolve("mods/sodium-094.jar")),"Sodium-only selection was pinned");
   client.toggle(sodiumOnly,new ProsperoModrinth.Selection("oSIKhgz3","Vitrail",ProsperoModrinth.Kind.MOD));
   try{client.downloadAll(sodiumOnly,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("automatic downgrade allowed");}
   catch(IOException expected){check(expected.getMessage().contains("Automatic downgrades"),"wrong downgrade error");}
   check(Files.isRegularFile(sodiumOnly.resolve("mods/sodium-094.jar"))&&!Files.exists(sodiumOnly.resolve("mods/vitrail-013.jar")),"downgrade modified installed mods");
   version("sodium","oldSodium","sodium-old.jar",jar("sodium","0.9.2","{}",null),"[]");
   version("unused","unusedVersion","unused.jar",jar("unused","1.0","{}",null),"[]");
   version("sodium","newSodium","sodium-new.jar",jar("sodium","0.9.3-beta.1","{}",null),"[{\"project_id\":\"unused\",\"version_id\":\"unusedVersion\",\"dependency_type\":\"required\"}]");
   version("iris","irisVersion","iris.jar",jar("iris","1.11.7","{\"sodium\":\"0.9.x\"}",null),"[{\"project_id\":\"sodium\",\"version_id\":\"oldSodium\",\"dependency_type\":\"required\"}]");
   for(boolean reverse:List.of(false,true)){
    Path fresh=root.resolve("queue-"+reverse+"/game");Files.createDirectories(fresh);
    for(String project:reverse?List.of("sodium","iris"):List.of("iris","sodium"))client.toggle(fresh,new ProsperoModrinth.Selection(project,project,ProsperoModrinth.Kind.MOD));
    client.downloadAll(fresh,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
    check(Files.exists(fresh.resolve("mods/iris.jar"))&&Files.exists(fresh.resolve("mods/sodium-old.jar"))&&!Files.exists(fresh.resolve("mods/sodium-new.jar"))&&!Files.exists(fresh.resolve("mods/unused.jar")),"queue order selected wrong version or retained obsolete dependency");
    check(client.installed(fresh).files.size()==2&&client.queue(fresh).isEmpty(),"wrong dependency receipt or queue");
   }

   Path existing=root.resolve("already-installed/game");Files.createDirectories(existing.resolve("mods"));
   byte[] installedNew=jar("sodium","0.9.3-beta.1","{}",null);Files.write(existing.resolve("mods/sodium-new.jar"),installedNew);
   client.toggle(existing,new ProsperoModrinth.Selection("iris","Iris",ProsperoModrinth.Kind.MOD));
   try{client.downloadAll(existing,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("existing Sodium silently replaced");}catch(IOException expected){check(expected.getMessage().contains("Multiple top-level versions"),"installed conflict not explained");}
   check(Arrays.equals(installedNew,Files.readAllBytes(existing.resolve("mods/sodium-new.jar")))&&!Files.exists(existing.resolve("mods/iris.jar"))&&client.queue(existing).size()==1,"existing conflicting files changed or queue lost");
   version("otherroot","otherVersion","otherroot.jar",jar("otherroot","1.0","{}",null),"[{\"project_id\":\"sodium\",\"version_id\":\"newSodium\",\"dependency_type\":\"required\"}]");
   Path incompatible=root.resolve("incompatible/game");Files.createDirectories(incompatible);
   for(String project:List.of("iris","otherroot"))client.toggle(incompatible,new ProsperoModrinth.Selection(project,project,ProsperoModrinth.Kind.MOD));
   try{client.downloadAll(incompatible,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("incompatible exact dependency pins accepted");}catch(IOException expected){check(expected.getMessage().contains("sodium")&&expected.getMessage().contains("oldSodium")&&expected.getMessage().contains("newSodium"),"conflicting dependency not identified");}
   check(client.local(incompatible,ProsperoModrinth.Kind.MOD).isEmpty()&&client.queue(incompatible).size()==2,"conflict published files or lost queue");

   // The Sift pins GeckoLib's NeoForge release despite offering a Fabric build.
   var siftDeps="[{\"project_id\":\"gecko\",\"version_id\":\"geckoNeo\",\"dependency_type\":\"required\"}]";
   version("sift","siftFabric","sift.jar",jar("sift","2.0.1","{\"geckolib\":\">=5.5.6\",\"minecraft\":\"~26.3\"}",null),siftDeps);
   byte[] geckoFabric=jar("geckolib","5.5.6","{}",null);
   version("gecko","geckoNeo","gecko-neoforge.jar",bytes("wrong loader"),"[]");
   version("gecko","geckoFabric","gecko-fabric.jar",geckoFabric,"[]");
   version("gecko","geckoLatest","gecko-newer.jar",jar("geckolib","5.5.7","{}",null),"[]");
   JsonObject neo=JsonParser.parseString(new String(network.get(ProsperoModrinth.API+"version/geckoNeo"))).getAsJsonObject();
   neo.addProperty("version_number","5.5.6");neo.add("loaders",JsonParser.parseString("[\"neoforge\"]"));
   network.put(ProsperoModrinth.API+"version/geckoNeo",bytes(neo.toString()));
   JsonObject fabric=JsonParser.parseString(new String(network.get(ProsperoModrinth.API+"version/geckoFabric"))).getAsJsonObject();
   fabric.addProperty("version_number","5.5.6");
   network.put(ProsperoModrinth.API+"version/geckoFabric",bytes(fabric.toString()));
   JsonObject newer=JsonParser.parseString(new String(network.get(ProsperoModrinth.API+"version/geckoLatest"))).getAsJsonObject();
   newer.addProperty("version_number","5.5.7");
   network.put("meta:gecko",bytes("["+neo+","+newer+","+fabric+"]"));
   Path sift=root.resolve("cross-loader-pin/game");Files.createDirectories(sift);
   client.toggle(sift,new ProsperoModrinth.Selection("sift","The Sift",ProsperoModrinth.Kind.MOD));
   client.downloadAll(sift,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
   check(client.queue(sift).isEmpty()&&Arrays.equals(geckoFabric,Files.readAllBytes(sift.resolve("mods/gecko-fabric.jar")))
         &&Files.isRegularFile(sift.resolve("mods/sift.jar"))&&!Files.exists(sift.resolve("mods/gecko-newer.jar"))
         &&!Files.exists(sift.resolve("mods/gecko-neoforge.jar")),"same-release Fabric sibling only");
   try{client.version("gecko","geckoNeo",ProsperoModrinth.Kind.MOD,"26.3",()->false);throw new AssertionError("explicit wrong-loader pin accepted");}
   catch(IOException expected){check(expected.getMessage().contains("does not support 26.3 Fabric"),"explicit pin diagnostic");}
   var ambiguous=fabric.deepCopy();ambiguous.addProperty("id","otherFabricBuild");
   var wrongGame=fabric.deepCopy();wrongGame.add("game_versions",JsonParser.parseString("[\"26.2\"]"));
   var wrongProject=fabric.deepCopy();wrongProject.addProperty("project_id","different");
   var server=fabric.deepCopy();server.addProperty("environment","dedicated_server_only");
   Path rejected=root.resolve("invalid-cross-loader-pin/game");Files.createDirectories(rejected);
   client.toggle(rejected,new ProsperoModrinth.Selection("sift","The Sift",ProsperoModrinth.Kind.MOD));
   for(var candidates:List.of("["+newer+","+wrongGame+","+wrongProject+","+server+"]","["+fabric+","+ambiguous+"]")){
    network.put("meta:gecko",bytes(candidates));
    try{client.downloadAll(rejected,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("unverifiable sibling accepted");}
    catch(IOException expected){check(expected.getMessage().contains("Required dependency gecko 5.5.6"),"blocked dependency not identified");}
    check(client.queue(rejected).size()==1&&client.local(rejected,ProsperoModrinth.Kind.MOD).isEmpty(),"rejected dependency changed mods or queue");
   }

   for(boolean sameName:List.of(false,true)){
    Path updateGame=root.resolve("update-"+sameName+"/game");Files.createDirectories(updateGame);Files.writeString(updateGame.resolve("world-marker"),"KEEP");
    byte[] oldLib=jar("library","1.0.0","{}",null),newLib=jar("library","2.0.0","{}",null);
    String oldName="library-old.jar",newName=sameName?oldName:"library-new.jar";
    version("library","libOld",oldName,oldLib,"[]");client.toggle(updateGame,new ProsperoModrinth.Selection("library","Library",ProsperoModrinth.Kind.MOD));client.downloadAll(updateGame,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
    version("library","libNew",newName,newLib,"[]");
    version("requiring","requiringVersion","requiring.jar",jar("requiring","1.0.0","{\"library\":\">=2.0.0\"}",null),"[{\"project_id\":\"library\",\"version_id\":\"libNew\",\"dependency_type\":\"required\"}]");
    client.toggle(updateGame,new ProsperoModrinth.Selection("requiring","Requiring",ProsperoModrinth.Kind.MOD));
    client.downloadAll(updateGame,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
    check(Arrays.equals(newLib,Files.readAllBytes(updateGame.resolve("mods/"+newName)))&&(sameName||!Files.exists(updateGame.resolve("mods/"+oldName)))&&client.installed(updateGame).files.size()==2&&client.installed(updateGame).files.stream().anyMatch(f->f.version().equals("libNew")),"dependency upgrade not committed or duplicate old JAR retained");
    check(Files.readString(updateGame.resolve("world-marker")).equals("KEEP"),"upgrade changed world");
   }
   // Missing manifest-only constraints use the known installed project's newer candidate.
   Path manifestGame=root.resolve("manifest-update/game");Files.createDirectories(manifestGame);
   byte[] oldLibrary=jar("library","1.0.0","{}",null),newLibrary=jar("library","2.0.0","{}",null);
   version("library","libOld","library-old.jar",oldLibrary,"[]");client.toggle(manifestGame,new ProsperoModrinth.Selection("library","Library",ProsperoModrinth.Kind.MOD));client.downloadAll(manifestGame,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
   version("library","libNew","library-new.jar",newLibrary,"[]");
   Files.write(manifestGame.resolve("mods/manual-root.jar"),jar("manualroot","1.0","{\"library\":\">=2\"}",null));
   try{client.repair(manifestGame,"26.3","fabric",versions,(m,d,t)->{},()->false,true);throw new AssertionError("offline outdated mod allowed");}catch(IOException expected){}
   client.repair(manifestGame,"26.3","fabric",versions,(m,d,t)->{},()->false,false);
   check(Files.exists(manifestGame.resolve("mods/library-new.jar"))&&!Files.exists(manifestGame.resolve("mods/library-old.jar")),"pre-Play manifest-only dependency update failed");
   int healthyReads=reads;client.repair(manifestGame,"26.3","fabric",versions,(m,d,t)->{},()->false,false);check(reads==healthyReads,"healthy updated launch used network");
   for(String failure:List.of("hash","cancel","receipt","othermod","modified","downgrade")){
    Path failing=root.resolve("failure-"+failure+"/game");Files.createDirectories(failing);
    version("library","libOld","library-old.jar",oldLibrary,"[]");client.toggle(failing,new ProsperoModrinth.Selection("library","Library",ProsperoModrinth.Kind.MOD));client.downloadAll(failing,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);
    Path receiptPath=ProsperoModrinth.state(failing,"content-installed.json");String priorReceipt=Files.readString(receiptPath);
    byte[] actualOld=oldLibrary;if(failure.equals("modified")){actualOld=jar("library","1.0.0","{\"java\":\">=25\"}",null);Files.write(failing.resolve("mods/library-old.jar"),actualOld);}
    if(failure.equals("othermod"))Files.write(failing.resolve("mods/other.jar"),jar("other","1.0","{\"library\":\"<2\"}",null));
    byte[] desired=failure.equals("downgrade")?jar("library","0.5.0","{}",null):newLibrary;
    version("library","libNew","library-new.jar",desired,"[]");
    version("requiring","requiringVersion","requiring.jar",jar("requiring","1.0","{}",null),"[{\"project_id\":\"library\",\"version_id\":\"libNew\",\"dependency_type\":\"required\"}]");
    client.toggle(failing,new ProsperoModrinth.Selection("requiring","Requiring",ProsperoModrinth.Kind.MOD));
    if(failure.equals("hash"))network.put("https://cdn.modrinth.com/data/library/libNew/library-new.jar",bytes("BAD"));
    if(failure.equals("receipt"))Files.createDirectory(receiptPath.resolveSibling("content-installed.json.tmp"));
    java.util.function.BooleanSupplier stop=()->failure.equals("cancel")&&!Files.exists(failing.resolve("mods/library-old.jar"));
    try{client.downloadAll(failing,"26.3","fabric",(m,d,t)->{},stop,f->{},versions);throw new AssertionError("upgrade failure accepted: "+failure);}catch(IOException expected){}
    check(Arrays.equals(actualOld,Files.readAllBytes(failing.resolve("mods/library-old.jar")))&&!Files.exists(failing.resolve("mods/library-new.jar"))&&!Files.exists(failing.resolve("mods/requiring.jar"))&&Files.readString(receiptPath).equals(priorReceipt)&&client.queue(failing).size()==1,"failed update did not preserve old bytes/receipt/queue: "+failure);
   }
   System.out.println("PASS dependency upgrades with same/different filenames,manifest-only pre-Play repair,offline/healthy behavior,and hash/cancel/receipt-write/other-mod/modified-file/downgrade failures preserve previous state");

   for(String broken:List.of("root","dependency","metadata")){
    Path partial=root.resolve("partial-"+broken+"/game");Files.createDirectories(partial);
    version("shared","sharedV","shared.jar",jar("shared","1.0","{}",null),"[]");
    String shared="[{\"project_id\":\"shared\",\"version_id\":\"sharedV\",\"dependency_type\":\"required\"}]";
    version("brokenroot","brokenV","broken.jar",jar("brokenroot","1.0","{}",null),shared);
    version("dependent","dependentV","dependent.jar",jar("dependent","1.0","{}",null),"[{\"project_id\":\"brokenroot\",\"version_id\":\"brokenV\",\"dependency_type\":\"required\"}]");
    version("otherroot","otherV","other.jar",jar("otherroot","1.0","{}",null),shared);
    version("pack","packV","pack.zip",bytes("PACK"),"[]");
    if(broken.equals("root"))network.put("https://cdn.modrinth.com/data/brokenroot/brokenV/broken.jar",bytes("BAD"));
    if(broken.equals("dependency"))network.put("https://cdn.modrinth.com/data/shared/sharedV/shared.jar",bytes("BAD"));
    if(broken.equals("metadata")){network.remove("meta:brokenroot");network.remove(ProsperoModrinth.API+"version/brokenV");}
    for(String project:List.of("brokenroot","dependent","otherroot","shared"))client.toggle(partial,new ProsperoModrinth.Selection(project,project,ProsperoModrinth.Kind.MOD));
    client.toggle(partial,new ProsperoModrinth.Selection("pack","Pack",ProsperoModrinth.Kind.RESOURCE));
    try{client.downloadAll(partial,"26.3","fabric",(m,d,t)->{},()->false,f->{},versions);throw new AssertionError("partial failure not reported");}catch(IOException expected){check(expected.getMessage().contains("remain queued"),"partial summary missing");}
    check(Files.exists(partial.resolve("resourcepacks/pack.zip"))&&!Files.exists(partial.resolve("mods/broken.jar"))&&!Files.exists(partial.resolve("mods/dependent.jar")),"independent pack blocked or failed dependent installed");
    boolean sharedOk=!broken.equals("dependency");check(Files.exists(partial.resolve("mods/shared.jar"))==sharedOk&&Files.exists(partial.resolve("mods/other.jar"))==sharedOk,"directional dependency failure blocked independent library/root");
    int failed=sharedOk?2:4;check(client.queue(partial).size()==failed&&JsonParser.parseString(Files.readString(ProsperoModrinth.state(partial,"content-download-errors.json"))).getAsJsonArray().size()==failed,"success selections retained or failed roots lost");
   }
   System.out.println("PASS partial queue root/dependency/metadata failures:failed roots/transitive dependents retained with errors;independent packs and healthy shared-library users continue;success selections removed from queue");
  }
  System.out.println("PASS actual upstream Fabric predicates,manifest-only missing API,nested module providers,hash-pinned auto-install,old-instance repair,healthy offline/no-network launch,offline failure,conflicts/unmapped requirements before publication and world/file preservation");
 }
}
'''
(w/'DependencyCheck.java').write_text(source);cp=launcher_classpath()
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'DependencyCheck.java')],check=True)
shutil.rmtree(w/'data',ignore_errors=True)
subprocess.run([str(JDK/'bin/java'),'-Xverify:all','-cp',str(w)+':'+cp,'DependencyCheck',str(w/'data'),str(loader)],check=True)
