#!/usr/bin/env python3
"""Actual instance persistence, publisher install/cache validation and controller model."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import tempfile,json,subprocess
ROOT=Path(__file__).resolve().parents[1];jdk=java_home()
cp=launcher_classpath()
source=r'''
import java.nio.file.*;import java.util.*;import java.io.*;import java.security.*;import com.google.gson.*;
public class InstanceCheck {
 static Map<String,byte[]> files=new HashMap<>();static int reads=0;static final String META="https://piston-meta.mojang.com/version/26.1.json",JAR="https://piston-data.mojang.com/objects/client.jar",LIB="https://libraries.minecraft.net/example/test.jar",INDEX="https://piston-meta.mojang.com/index.json";
 static byte[] bytes(String s){return s.getBytes(java.nio.charset.StandardCharsets.UTF_8);}static String hash(byte[] b)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-1").digest(b));}
 static String pin(String url,byte[] b)throws Exception{return "{\"url\":\""+url+"\",\"sha1\":\""+hash(b)+"\",\"size\":"+b.length+"}";}
 static void fixture()throws Exception{
  byte[] client=bytes("original client bytes"),library=bytes("original library bytes"),asset=bytes("asset bytes");String sha=hash(asset);files.put(JAR,client);files.put(LIB,library);files.put("https://resources.download.minecraft.net/"+sha.substring(0,2)+"/"+sha,asset);
  byte[] index=bytes("{\"objects\":{\"a\":{\"hash\":\""+sha+"\",\"size\":"+asset.length+"},\"same hash\":{\"hash\":\""+sha+"\",\"size\":"+asset.length+"}}}");files.put(INDEX,index);
  String libraryPin=pin(LIB,library).replace("{","{\"path\":\"example/test.jar\",");
  String meta="{\"id\":\"26.1\",\"type\":\"release\",\"mainClass\":\"net.minecraft.client.main.Main\",\"javaVersion\":{\"majorVersion\":25},\"downloads\":{\"client\":"+pin(JAR,client)+"},\"assetIndex\":"+pin(INDEX,index).replace("{","{\"id\":\"32\",")+",\"libraries\":[{\"name\":\"example:test:1\",\"downloads\":{\"artifact\":"+libraryPin+"}},{\"name\":\"example:test:1:natives-windows\",\"downloads\":{\"artifact\":"+libraryPin+"}}]}";
  files.put(META,bytes(meta));String entry="{\"id\":\"26.1\",\"type\":\"release\",\"url\":\""+META+"\",\"sha1\":\""+hash(files.get(META))+"\"}";files.put(ProsperoInstall.MANIFEST,bytes("{\"versions\":["+entry+"]}"));
 }
 static synchronized InputStream open(String url)throws Exception{reads++;byte[] b=files.get(url);if(b==null)throw new IOException("Unexpected fixture request");return new ByteArrayInputStream(b);}
 interface Action{void run()throws Exception;}static void denied(Action action)throws Exception{try{action.run();throw new AssertionError("accepted invalid input");}catch(IOException|IllegalArgumentException expected){}}
 static void waitFor(ProsperoLauncher model)throws Exception{long end=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<end)Thread.sleep(5);if(model.tick(0)[64].equals("BUSY"))throw new AssertionError("worker stuck");}
 public static void main(String[]args)throws Exception{
  Path root=Path.of(args[0]);fixture();
  byte[] originalManifest=files.get(ProsperoInstall.MANIFEST);String snapUrl=META.replace("26.1","26.4-snapshot-999");byte[] snapMeta=bytes(new String(files.get(META),java.nio.charset.StandardCharsets.UTF_8).replace("26.1","26.4-snapshot-999").replace("\"majorVersion\":25","\"majorVersion\":26"));files.put(snapUrl,snapMeta);
  String snapRow="{\"id\":\"26.4-snapshot-999\",\"type\":\"snapshot\",\"url\":\""+snapUrl+"\",\"sha1\":\""+hash(snapMeta)+"\"}";
  String releases=new String(originalManifest,java.nio.charset.StandardCharsets.UTF_8);files.put(ProsperoInstall.MANIFEST,bytes(releases.replace("[","["+snapRow+",")));
  var snapshotInstaller=new ProsperoInstall(root.resolve("snapshot-cache"),InstanceCheck::open);if(snapshotInstaller.catalog(false,()->false).size()!=1||snapshotInstaller.catalog(true,()->false).size()!=2)throw new AssertionError("snapshot/release filter");
  var snapshotReceipt=snapshotInstaller.install(snapshotInstaller.catalog(true,()->false).get(0),1,(text,done,total)->{},()->false);if(snapshotReceipt.javaMajor!=26||ProsperoLauncher.supported(snapshotReceipt.version))throw new AssertionError("future runtime download/launch guard");files.put(ProsperoInstall.MANIFEST,originalManifest);
var store=new ProsperoLibrary(root.resolve("store"));if(!store.instances().isEmpty())throw new AssertionError("preset instance");
  var first=store.add("Vanilla26.1","26.1",1);var second=store.add("Other world","26.1",2);if(store.game(first).equals(store.game(second)))throw new AssertionError("shared saves");Files.writeString(store.game(first).resolve("keep-world.txt"),"world");store.rename(first,"My world");store.icon(first,5);
  var reopened=new ProsperoLibrary(root.resolve("store"));if(!reopened.instances().get(0).name.equals("My world")||reopened.instances().get(0).icon!=5||!Files.readString(store.game(first).resolve("keep-world.txt")).equals("world"))throw new AssertionError("persistence/world");
  denied(()->store.add("../bad","26.1",1));denied(()->store.add("bad","../../escape",1));denied(()->ProsperoInstall.relative(root,"../escape"));denied(()->ProsperoInstall.safeUrl("https://evil.example/file"));denied(()->ProsperoInstall.safeUrl("http://piston-meta.mojang.com/file"));
  Path oldLibrary=root.resolve("store/library.json");var oldJson=JsonParser.parseString(Files.readString(oldLibrary)).getAsJsonObject();oldJson.getAsJsonObject("settings").remove("showIntro");Files.writeString(oldLibrary,oldJson.toString());if(!new ProsperoLibrary(root.resolve("store")).settings().showIntro)throw new AssertionError("old library notice default");
  for(int resolution=0;resolution<ProsperoLibrary.RESOLUTIONS.length;resolution++){reopened.settings().resolution=resolution;reopened.save();if(new ProsperoLibrary(root.resolve("store")).settings().resolution!=resolution)throw new AssertionError("resolution not retained");}
  var install=new ProsperoInstall(root.resolve("cache"),InstanceCheck::open);var versions=install.catalog(false,()->false);if(versions.size()!=1)throw new AssertionError();var receipt=install.install(versions.get(0),3,(s,d,t)->{},()->false);install.verify(receipt);
  if(!receipt.version.equals("26.1")||!receipt.assetIndex.equals("32")||receipt.classpath.size()!=2||receipt.files.size()!=4||!Files.readString(root.resolve("cache/versions/26.1/client.jar")).equals("original client bytes"))throw new AssertionError("wrong version/classifier/asset dedup");
  int before=reads;install.install(versions.get(0),3,(s,d,t)->{},()->false);if(reads!=before+1)throw new AssertionError("verified cache downloaded again");
  Files.writeString(root.resolve("cache/versions/26.1/client.jar"),"tamper");denied(()->install.verify(receipt));install.install(versions.get(0),2,(s,d,t)->{},()->false);install.verify(install.receipt("26.1"));
  denied(()->install.install(versions.get(0),2,(s,d,t)->{},()->true));
  var corrupt=new ProsperoInstall(root.resolve("corrupt"),url->url.equals(JAR)?new ByteArrayInputStream(bytes("WRONG bytes")):open(url));denied(()->corrupt.install(versions.get(0),1,(s,d,t)->{},()->false));if(Files.exists(root.resolve("corrupt/versions/26.1/receipt.json")))throw new AssertionError("failed install marked ready");
  var interrupted=new java.util.concurrent.atomic.AtomicBoolean();var mid=new ProsperoInstall(root.resolve("mid-cancel"),url->{InputStream original=open(url);return new FilterInputStream(original){public int read(byte[] b,int off,int len)throws IOException{int n=super.read(b,off,len);if(url.equals(JAR))interrupted.set(true);return n;}};});
  denied(()->mid.install(versions.get(0),1,(s,d,t)->{},interrupted::get));try(var paths=Files.walk(root.resolve("mid-cancel"))){if(paths.anyMatch(p->p.toString().endsWith(".part")||p.toString().endsWith("receipt.json")))throw new AssertionError("cancel left unverified file/receipt");}
  var model=new ProsperoLauncher(new ProsperoAuth(),root.resolve("model"),InstanceCheck::open);if(!model.tick(0)[13].equals("1"))throw new AssertionError("not empty");
  if(model.tick(0)!=model.tick(0))throw new AssertionError("idle notice allocates new state");
  if(!model.tick(0)[11].equals("7")||!model.tick(0)[68].equals("ON"))throw new AssertionError("intro default");if(!model.tick(0)[15].equals("1"))throw new AssertionError("OK initial focus");
  model.tick(0x10);model.tick(0x40);if(!model.tick(0)[15].equals("1"))throw new AssertionError("welcome must be horizontal");
  model.tick(0x20);if(!model.tick(0)[15].equals("0")||!model.tick(0)[68].equals("ON"))throw new AssertionError("right should focus, not toggle");
  model.tick(0x4000);if(!model.tick(0)[68].equals("OFF"))throw new AssertionError("checkbox X");model.tick(0x80);model.tick(0x4000);if(!new ProsperoLauncher(new ProsperoAuth(),root.resolve("model"),InstanceCheck::open).tick(0)[11].equals("0"))throw new AssertionError("intro preference");
  var notice=new ProsperoLauncher(new ProsperoAuth(),root.resolve("model"),InstanceCheck::open);
  notice.tick(0x800);for(int i=0;i<4;i++)notice.tick(0x40);notice.tick(0x4000);
  if(!new ProsperoLauncher(new ProsperoAuth(),root.resolve("model"),InstanceCheck::open).tick(0)[11].equals("7"))throw new AssertionError("Settings restore notice");notice.tick(0x4000);
  model.tick(0x800);if(!model.tick(0)[11].equals("2")||!model.tick(0)[28].equals("CONTENT"))throw new AssertionError("R1 auto settings");model.tick(0x4000);if(!model.tick(0)[11].equals("10"))throw new AssertionError("resolution dropdown");model.tick(0x2000);
  model.tick(0x400);model.tick(0x4000);waitFor(model);if(!model.tick(0)[23].equals("26.1"))throw new AssertionError("catalog");model.tick(0x40);model.tick(0x40);model.tick(0x4000);if(!model.tick(0)[11].equals("6"))throw new AssertionError("name keyboard");model.tick(0x4000);model.tick(0x8000);
  model.tick(0x40);model.tick(0x4000);model.tick(0x40);model.tick(0x4000);model.tick(0x40);model.tick(0x4000);waitFor(model);if(!model.tick(0)[13].equals("2")||!model.tick(0)[19].equals("READY"))throw new AssertionError("instance install "+model.tick(0)[2]);
  model.tick(0x4000);waitFor(model);if(!model.tick(0)[10].equals("WAIT")||!model.tick(0)[6].contains("COMING SOON"))throw new AssertionError("unsupported version launched");
  if(!ProsperoLauncher.supported("26.2")||!ProsperoLauncher.supported("26.3")||ProsperoLauncher.supported("26.3-snapshot-1")||ProsperoLauncher.supported("26.1"))throw new AssertionError("compatibility allowlist");
  for(var entry:files.entrySet())if(entry.getKey().equals(META)||entry.getKey().equals(ProsperoInstall.MANIFEST))entry.setValue(bytes(new String(entry.getValue(),java.nio.charset.StandardCharsets.UTF_8).replace("26.1","26.3").replace("example:test:1","org.lwjgl:lwjgl-sdl:3.4.3")));
  // The metadata URL in the manifest also changes; provide the matching fixture.
  files.put(META.replace("26.1","26.3"),files.get(META));
  byte[] metadata=files.get(META);String catalog="{\"versions\":[{\"id\":\"26.3\",\"type\":\"release\",\"url\":\""+META+"\",\"sha1\":\""+hash(metadata)+"\"}]}";files.put(ProsperoInstall.MANIFEST,bytes(catalog));
  Path supportedRoot=root.resolve("supported");var supportedLibrary=new ProsperoLibrary(supportedRoot);var supportedInstance=supportedLibrary.add("Playable","26.3",1);supportedLibrary.settings().showIntro=false;supportedLibrary.save();var supportedInstaller=new ProsperoInstall(supportedRoot.resolve("cache"),InstanceCheck::open);var supportedReceipt=supportedInstaller.install(supportedInstaller.catalog(false,()->false).get(0),1,(t,d,n)->{},()->false);supportedLibrary.ready(supportedInstance,true);
  Files.writeString(supportedLibrary.game(supportedInstance).resolve("keep-world.txt"),"world");
  var supportedModel=new ProsperoLauncher(new ProsperoAuth(),supportedRoot,InstanceCheck::open);supportedModel.tick(0x4000);supportedModel.tick(0x4000);waitFor(supportedModel);if(!supportedModel.tick(0)[10].equals("LAUNCH"))throw new AssertionError("supported launch "+supportedModel.tick(0)[2]);List<String> launch=List.of(supportedModel.arguments(null,null));if(!launch.contains("--demo")||!launch.contains("26.3")||!launch.contains("--graphicsBackend"))throw new AssertionError("supported original demo arguments");if(!launch.get(launch.indexOf("--width")+1).equals("1920")||!launch.get(launch.indexOf("--height")+1).equals("1080"))throw new AssertionError("launch not1080p");
  // Returning is a fresh process/model; every launch gets a new loader.
  for(int cycle=0;cycle<3;cycle++){
   System.setProperty("ps5.launcher.resume","true");supportedLibrary.settings().showIntro=true;supportedLibrary.save();
   var next=new ProsperoLauncher(new ProsperoAuth(),supportedRoot,InstanceCheck::open);
   if(!next.tick(0)[11].equals("0")||!next.tick(0)[68].equals("ON"))throw new AssertionError("return must bypass notice without changing preference");
   next.tick(0x800);if(!next.tick(0)[12].equals("1"))throw new AssertionError("topbar horizontal");next.tick(0x400);
   next.tick(0x4000);next.tick(0x4000);waitFor(next);if(!next.tick(0)[10].equals("LAUNCH"))throw new AssertionError("repeat selection/launch");
   if(!Files.readString(supportedLibrary.game(supportedInstance).resolve("keep-world.txt")).equals("world"))throw new AssertionError("cycle lost world");
  }System.clearProperty("ps5.launcher.resume");
  // Temporary channel requires an unexpired, entitlement-checked Session.
  Path channel=Path.of(args[1]).resolve("prosperocraft-channel.txt");Files.writeString(channel,"temp_gametest");
  supportedLibrary.settings().showIntro=false;supportedLibrary.save();
  var authRequests=new java.util.concurrent.atomic.AtomicInteger();var testAuth=new ProsperoAuth((e,m,t,b,a)->{authRequests.incrementAndGet();throw new ProsperoAuth.Failure("NETWORK");},new ProsperoAuth.Clock(){public long millis(){return System.currentTimeMillis();}public void sleep(long n){}});
  var fullModel=new ProsperoLauncher(testAuth,supportedRoot,InstanceCheck::open);fullModel.tick(0x4000);if(!fullModel.tick(0)[6].equals("PLAY - Sign in"))throw new AssertionError("sign-in play wording");fullModel.tick(0x4000);waitFor(fullModel);
  if(!fullModel.tick(0)[10].equals("WAIT")||!fullModel.tick(0)[11].equals("3")||authRequests.get()!=1)throw new AssertionError("unsigned full game accepted");
  var sessionField=ProsperoLauncher.class.getDeclaredField("session");sessionField.setAccessible(true);
  sessionField.set(fullModel,new ProsperoAuth.Session("OwnedPlayer","0123456789abcdef0123456789abcdef","SECRET_TEST_TOKEN",System.currentTimeMillis()+3600000));
  fullModel.tick(0x400);fullModel.tick(0x400);fullModel.tick(0x4000);
  synchronized(fullModel){fullModel.tick(0x4000);fullModel.tick(0x8);} // Worker cannot prepare until guide is open.
  waitFor(fullModel);if(!fullModel.tick(0)[11].equals("8")||!fullModel.tick(0)[10].equals("WAIT")||!fullModel.tick(0)[95].equals("READY"))throw new AssertionError("guide bypassed tutorial during preparation");
  fullModel.tick(0x2000);if(!fullModel.tick(0)[11].equals("11"))throw new AssertionError("guide lost tutorial");
  fullModel.tick(0x20);fullModel.tick(0x4000);if(!fullModel.tick(0)[94].equals("OFF")||new ProsperoLibrary(supportedRoot).settings().showControls)throw new AssertionError("tutorial preference persistence");fullModel.tick(0x80);fullModel.tick(0x4000);
  if(!fullModel.tick(0)[10].equals("LAUNCH"))throw new AssertionError("tutorial OK");if(!fullModel.tick(0)[6].equals("PLAY"))throw new AssertionError("ready action wording");List<String> fullArgs=List.of(fullModel.arguments(null,null));
  if(fullArgs.contains("--demo")||fullArgs.contains("--disableMultiplayer")||fullArgs.contains("--disableChat")||!fullArgs.get(fullArgs.indexOf("--accessToken")+1).equals("SECRET_TEST_TOKEN")||!fullArgs.get(fullArgs.indexOf("--username")+1).equals("OwnedPlayer")||!fullArgs.get(fullArgs.indexOf("--uuid")+1).equals("0123456789abcdef0123456789abcdef"))throw new AssertionError("full session handoff");
  if(Arrays.toString(fullModel.tick(0)).contains("SECRET_TEST_TOKEN")||fullModel.toString().contains("SECRET_TEST_TOKEN"))throw new AssertionError("UI leaked session token");
  sessionField.set(fullModel,new ProsperoAuth.Session("OwnedPlayer","0123456789abcdef0123456789abcdef","SECRET_EXPIRED",System.currentTimeMillis()-1));denied(()->fullModel.arguments(null,null));
  sessionField.set(fullModel,null);denied(()->fullModel.arguments(null,null));
  Files.writeString(channel,"demo");if(!List.of(supportedModel.arguments(null,null)).contains("--demo"))throw new AssertionError("Demo mode changed");Files.delete(channel);
  if(!Files.readString(supportedLibrary.game(supportedInstance).resolve("keep-world.txt")).equals("world"))throw new AssertionError("full launch lost world");
  System.out.println("PASS Temp_gametest verified session arguments, unsigned/expired/signed-out rejection, full-game flags, UI redaction, Demo isolation and existing world/cache reuse");
  var persisted=new ProsperoLibrary(root.resolve("model"));if(persisted.instances().size()!=1||persisted.instances().get(0).icon!=2||!persisted.instances().get(0).name.endsWith("1"))throw new AssertionError("controller persistence");
  System.out.println("PASS empty/persistent instances, isolated worlds, rename/icons/settings, L1/R1/keyboard/install/play controller flow, unsupported26.1 launch guard and startup-notice persistence, original bytes, pin verification/cache/repair/cancel/failure/traversal/HTTPS/native-classifier rejection");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-instances-')as folder:
 w=Path(folder);(w/'InstanceCheck.java').write_text(source)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'InstanceCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'-cp',str(w)+':'+cp,'InstanceCheck',str(w/'data'),str(w)],check=True,timeout=40)
