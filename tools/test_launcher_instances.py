#!/usr/bin/env python3
"""Actual instance persistence, publisher install/cache validation and controller model."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath, dependency
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
 static void checkStreaming(boolean value){if(!value)throw new AssertionError("No progress reported before file EOF");}
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
  Path streamingCache=root.resolve("streaming-cache");var streamed=new java.util.concurrent.atomic.AtomicBoolean();var sawProgress=new java.util.concurrent.atomic.AtomicBoolean();
  var streaming=new ProsperoInstall(streamingCache,url->{if(!url.equals(JAR))return open(url);byte[] body=files.get(url);return new ByteArrayInputStream(body){public synchronized int read(byte[] b,int off,int len){if(pos>0&&pos<body.length&&sawProgress.get())streamed.set(true);return super.read(b,off,Math.min(len,4));}};});
  streaming.install(versions.get(0),1,(t,d,n)->{if(d>0&&d<n){sawProgress.set(true);try{Thread.sleep(110);}catch(InterruptedException stopped){Thread.currentThread().interrupt();}}},()->false);
  checkStreaming(streamed.get());streaming.verify(streaming.receipt("26.1"));
  // Missing receipt recovery reuses original publisher metadata and never requests
  // healthy payloads, including offline. Worlds/mods live outside this cache.
  Path receiptPath=root.resolve("cache/versions/26.1/receipt.json"),metaPath=root.resolve("cache/versions/26.1/metadata.json");
  Files.delete(receiptPath);int refreshReads=reads;
  var refreshed=install.ensure("26.1",3,(t,d,n)->{if(d<0||d>n)throw new AssertionError("refresh progress bounds");},()->false,true);
  install.verify(refreshed);if(reads!=refreshReads)throw new AssertionError("offline receipt recovery made requests");
  Files.writeString(receiptPath,"{invalid");install.ensure("26.1",2,(t,d,n)->{},()->false,true);
  if(reads!=refreshReads)throw new AssertionError("malformed receipt redownloaded payloads");
  Files.writeString(metaPath,"corrupt");Files.delete(receiptPath);
  denied(()->install.ensure("26.1",2,(t,d,n)->{},()->false,true));
  if(Files.exists(receiptPath)||reads!=refreshReads)throw new AssertionError("offline metadata refusal published receipt/network");
  install.ensure("26.1",2,(t,d,n)->{},()->false,false);
  if(reads!=refreshReads+1)throw new AssertionError("metadata recovery fetched healthy payloads");
  String assetHash=hash(bytes("asset bytes"));Path assetPath=root.resolve("cache/assets/objects/"+assetHash.substring(0,2)+"/"+assetHash);
  Files.delete(assetPath);refreshReads=reads;install.refresh("26.1",3,(t,d,n)->{},()->false,false);
  if(reads!=refreshReads+1||!Files.readString(assetPath).equals("asset bytes"))throw new AssertionError("missing asset not selectively restored");
  Files.writeString(root.resolve("cache/versions/26.1/client.jar"),"original client BYTEs");
  refreshReads=reads;install.ensure("26.1",2,(t,d,n)->{},()->false,false);
  if(reads!=refreshReads+1||!Files.readString(root.resolve("cache/versions/26.1/client.jar")).equals("original client bytes"))throw new AssertionError("damaged code not selectively repaired");
  Files.writeString(assetPath,"ASSET BYTES");refreshReads=reads;install.refresh("26.1",2,(t,d,n)->{},()->false,false);
  if(reads!=refreshReads||!Files.readString(assetPath).equals("ASSET BYTES"))throw new AssertionError("quick check unexpectedly read all asset contents");
  install.install(versions.get(0),2,(t,d,n)->{},()->false);
  if(!Files.readString(assetPath).equals("asset bytes"))throw new AssertionError("full checksum repair missed same-size corruption");
  Files.delete(receiptPath);denied(()->install.refresh("26.1",2,(t,d,n)->{},()->true,false));
  if(Files.exists(receiptPath))throw new AssertionError("cancelled refresh published receipt");
  install.refresh("26.1",2,(t,d,n)->{},()->false,true);
  if(!Files.readString(store.game(first).resolve("keep-world.txt")).equals("world"))throw new AssertionError("refresh changed world");
  System.out.println("PASS fast offline/malformed receipt recovery, selective metadata/code/asset downloads, cancellation and full checksum repair escape hatch");
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
  var recoveryMenu=new ProsperoLauncher(new ProsperoAuth(),supportedRoot,InstanceCheck::open,()->{});
  recoveryMenu.tick(0x4000);recoveryMenu.tick(0x40);recoveryMenu.tick(0x40);recoveryMenu.tick(0x4000);
  if(!recoveryMenu.tick(0)[11].equals("10")||!recoveryMenu.tick(0)[85].contains("Quick refresh")||!recoveryMenu.tick(0)[86].contains("Full repair"))throw new AssertionError("recovery selector missing");
  recoveryMenu.tick(0x2000);if(!recoveryMenu.tick(0)[11].equals("4")||!recoveryMenu.tick(0)[15].equals("2"))throw new AssertionError("recovery cancel lost instance focus");
  recoveryMenu.tick(0x4000);int menuReads=reads;recoveryMenu.tick(0x4000);waitFor(recoveryMenu);
  if(!recoveryMenu.tick(0)[2].contains("Launch cache refreshed")||!recoveryMenu.tick(0)[11].equals("4")||reads!=menuReads)throw new AssertionError("quick menu not local/in-place");
  recoveryMenu.tick(0x4000);recoveryMenu.tick(0x40);recoveryMenu.tick(0x4000);waitFor(recoveryMenu);
  if(!recoveryMenu.tick(0)[2].contains("Download complete")||reads!=menuReads+2)throw new AssertionError("full repair route lost: "+recoveryMenu.tick(0)[2]+" requests="+(reads-menuReads));
  Files.delete(supportedRoot.resolve("cache/versions/26.3/receipt.json"));int automaticReads=reads;

  var preparations=new java.util.concurrent.atomic.AtomicInteger();
  var legacy=JsonParser.parseString(Files.readString(supportedRoot.resolve("library.json"))).getAsJsonObject();legacy.getAsJsonObject("settings").addProperty("microphoneEnabled",false);Files.writeString(supportedRoot.resolve("library.json"),legacy.toString());
  var supportedModel=new ProsperoLauncher(new ProsperoAuth(),supportedRoot,InstanceCheck::open,()->{preparations.incrementAndGet();});supportedModel.tick(0x4000);supportedModel.tick(0x4000);waitFor(supportedModel);if(!supportedModel.tick(0)[10].equals("LAUNCH"))throw new AssertionError("supported launch "+supportedModel.tick(0)[2]);if(preparations.get()!=1)throw new AssertionError("automatic mic preparation ignored legacyfalse");if(reads!=automaticReads||!Files.isRegularFile(supportedRoot.resolve("cache/versions/26.3/receipt.json")))throw new AssertionError("Play failed local automatic recovery");List<String> launch=List.of(supportedModel.arguments(null,null));if(!launch.contains("--demo")||!launch.contains("26.3")||!launch.contains("--graphicsBackend"))throw new AssertionError("supported original demo arguments");if(!launch.get(launch.indexOf("--width")+1).equals("1920")||!launch.get(launch.indexOf("--height")+1).equals("1080"))throw new AssertionError("launch not1080p");
  // Returning is a fresh process/model; every launch gets a new loader.
  for(int cycle=0;cycle<3;cycle++){
   System.setProperty("ps5.launcher.resume","true");supportedLibrary.settings().showIntro=true;supportedLibrary.save();
   var next=new ProsperoLauncher(new ProsperoAuth(),supportedRoot,InstanceCheck::open,()->{preparations.incrementAndGet();});
   if(!next.tick(0)[11].equals("0")||!next.tick(0)[68].equals("ON"))throw new AssertionError("return must bypass notice without changing preference");
   next.tick(0x800);if(!next.tick(0)[12].equals("1"))throw new AssertionError("topbar horizontal");next.tick(0x400);
   next.tick(0x4000);next.tick(0x4000);waitFor(next);if(!next.tick(0)[10].equals("LAUNCH"))throw new AssertionError("repeat selection/launch");
   if(!Files.readString(supportedLibrary.game(supportedInstance).resolve("keep-world.txt")).equals("world"))throw new AssertionError("cycle lost world");
  }if(preparations.get()!=4)throw new AssertionError("mic not prepared on every relaunch");System.clearProperty("ps5.launcher.resume");
  // Temporary channel requires an unexpired, entitlement-checked Session.
  Path channel=Path.of(args[1]).resolve("prosperocraft-channel.txt");Files.writeString(channel,"temp_gametest");
  supportedLibrary.settings().showIntro=false;supportedLibrary.save();
  var authRequests=new java.util.concurrent.atomic.AtomicInteger();var testAuth=new ProsperoAuth((e,m,t,b,a)->{authRequests.incrementAndGet();throw new ProsperoAuth.Failure("NETWORK");},new ProsperoAuth.Clock(){public long millis(){return System.currentTimeMillis();}public void sleep(long n){}});
  var fullModel=new ProsperoLauncher(testAuth,supportedRoot,InstanceCheck::open,()->{preparations.incrementAndGet();});fullModel.tick(0x4000);if(!fullModel.tick(0)[6].equals("PLAY - Sign in"))throw new AssertionError("sign-in play wording");fullModel.tick(0x4000);waitFor(fullModel);
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
  // Normal full-game Zink candidate uses only an exact build resource; no auth bypass.
  Path zinkResource=Path.of(args[1]).resolve("prosperocraft-zink.txt");
  Files.writeString(channel,"temp_gametest");Files.writeString(zinkResource,"invalid\n");
  if(ProsperoLauncher.launchable("26.1","vanilla"))throw new AssertionError("invalid build gate");
  Files.writeString(zinkResource,"vanilla-26.1-zink-v1\n");
  Path binding=Path.of(args[1]).resolve("adapted-glfw.jar");try(var jar=new java.util.jar.JarOutputStream(Files.newOutputStream(binding))){}
  System.setProperty("ps5.glfw.binding",binding.toString());
  for(String version:List.of("26.1","26.1.1","26.1.2")){
   if(ProsperoLauncher.supported(version)||!ProsperoLauncher.developmentTest(version,"vanilla")||ProsperoLauncher.launchable(version,"fabric"))throw new AssertionError("Zink Vanilla-only development gate");
   fixture();byte[] meta=bytes(new String(files.get(META),java.nio.charset.StandardCharsets.UTF_8).replace("26.1",version));files.put(META,meta);
   Path zr=root.resolve("zink-"+version);var zi=new ProsperoInstall(zr.resolve("cache"),InstanceCheck::open);
   var receiptZ=zi.install(new ProsperoInstall.Version(version,"release",META,hash(meta)),1,(t,d,n)->{},()->false);
   if(!"ZINK".equals(receiptZ.renderer)||!"GLFW".equals(receiptZ.window))throw new AssertionError("receipt renderer");
   System.setProperty("ps5.glfw.binding",binding+".missing");denied(()->zi.loader(receiptZ));System.setProperty("ps5.glfw.binding",binding.toString());
   try(var loaded=zi.loader(receiptZ)){if(!loaded.getURLs()[0].equals(binding.toUri().toURL()))throw new AssertionError("adapted binding priority");}
   var zl=new ProsperoLibrary(zr);var instanceZ=zl.add("Vanilla Zink",version,1);zl.settings().showIntro=false;zl.settings().showControls=false;zl.ready(instanceZ,true);zl.save();
   var zm=new ProsperoLauncher(testAuth,zr,InstanceCheck::open,()->{preparations.incrementAndGet();});zm.tick(0x4000);
   if(!zm.tick(0)[6].equals("PLAY - Sign in")||!zm.tick(0)[69].equals("SUPPORTED")||!zm.tick(0)[35].isEmpty()||zm.tick(0)[65].contains("Development"))throw new AssertionError("normal Vanilla labels");
   sessionField.set(zm,new ProsperoAuth.Session("OwnedPlayer","0123456789abcdef0123456789abcdef","SECRET_ZINK",System.currentTimeMillis()+3600000));
   zm.tick(0x4000);waitFor(zm);if(!zm.tick(0)[6].equals("PLAY"))throw new AssertionError("signed-in normal Play");if(!zm.tick(0)[10].equals("LAUNCH"))throw new AssertionError("normal Zink launcher did not prepare: "+zm.tick(0)[2]);
   List<String> zargs=List.of(zm.arguments(null,null));if(zargs.contains("--graphicsBackend")||zargs.contains("--demo")||!zargs.contains(version)||!zargs.contains("SECRET_ZINK"))throw new AssertionError("original GL/full account arguments");
   var modelLibraryField=ProsperoLauncher.class.getDeclaredField("library");modelLibraryField.setAccessible(true);var modelLibrary=(ProsperoLibrary)modelLibraryField.get(zm);
   var currentField=ProsperoLauncher.class.getDeclaredField("current");currentField.setAccessible(true);currentField.set(null,zm);
   for(int resolution=0;resolution<ProsperoLibrary.RESOLUTIONS.length;resolution++){modelLibrary.settings().resolution=resolution;var selectedArgs=List.of(zm.arguments(null,null));int[] size=ProsperoLibrary.RESOLUTIONS[resolution];if(!selectedArgs.get(selectedArgs.indexOf("--width")+1).equals(""+size[0])||!selectedArgs.get(selectedArgs.indexOf("--height")+1).equals(""+size[1])||!ProsperoLauncher.selectedRenderSize().equals(size[0]+"x"+size[1]))throw new AssertionError("Zink ignored selected render size");}
   sessionField.set(zm,null);denied(()->zm.arguments(null,null));
   if(!Files.readString(zr.resolve("cache/versions/"+version+"/client.jar")).equals("original client bytes"))throw new AssertionError("rewrote game");
  }
  Files.writeString(zinkResource,"all-loaders-26.1-zink-v2\n");
  Path sodiumResource=Path.of(args[1]).resolve("prosperocraft-sodium-lwjgl-test.txt");
  System.clearProperty("sodium.checks.issue2561");
  if(ProsperoGraphics.configureSodiumLwjglTest("26.1.2","fabric")||System.getProperty("sodium.checks.issue2561")!=null)throw new AssertionError("default Sodium check changed");
  Files.writeString(sodiumResource,"invalid\n");
  if(ProsperoGraphics.configureSodiumLwjglTest("26.1.2","fabric"))throw new AssertionError("invalid Sodium resource");
  Files.writeString(sodiumResource,"sodium-lwjgl-version-test-v1\n");
  for(String version:List.of("26.1","26.1.1","26.1.2","26.2")){
   if(ProsperoGraphics.configureSodiumLwjglTest(version,"vanilla"))throw new AssertionError("Vanilla Sodium scope");
   if(!ProsperoGraphics.configureSodiumLwjglTest(version,"fabric")||!"false".equals(System.getProperty("sodium.checks.issue2561")))throw new AssertionError("candidate Fabric Sodium opt-out");
   System.clearProperty("sodium.checks.issue2561");
  }
  for(String version:List.of("26.3","26.4-snapshot-1"))if(ProsperoGraphics.configureSodiumLwjglTest(version,"fabric"))throw new AssertionError("Vulkan Sodium scope");
  Files.writeString(channel,"demo");if(ProsperoGraphics.configureSodiumLwjglTest("26.1.2","fabric")||ProsperoGraphics.configureSodiumLwjglTest("26.2","fabric"))throw new AssertionError("release Sodium scope");Files.writeString(channel,"temp_gametest");
  System.setProperty("sodium.checks.issue899","true");System.setProperty("sodium.checks.issue2561","true");Files.delete(sodiumResource);
  if(ProsperoGraphics.configureSodiumLwjglTest("26.1.2","fabric")||!"true".equals(System.getProperty("sodium.checks.issue2561"))||!"true".equals(System.getProperty("sodium.checks.issue899")))throw new AssertionError("default mutated caller properties");
  System.clearProperty("sodium.checks.issue2561");System.clearProperty("sodium.checks.issue899");
  byte[] actualFabric=Files.readAllBytes(Path.of(args[2]));
  for(String version:List.of("26.1","26.1.1","26.1.2")){
   if(!ProsperoLauncher.developmentTest(version,"fabric")||!ProsperoGraphics.zink(version,"fabric"))throw new AssertionError("Fabric Zink development gate");
   Path zr=root.resolve("zink-"+version);String url="https://maven.fabricmc.net/net/fabricmc/fabric-loader/0.20.1/fabric-loader-0.20.1.jar";
   String profile="{\"inheritsFrom\":\""+version+"\",\"mainClass\":\""+ProsperoFabric.MAIN+"\",\"libraries\":[{\"name\":\"net.fabricmc:fabric-loader:0.20.1\",\"url\":\"https://maven.fabricmc.net/\",\"sha1\":\""+hash(actualFabric)+"\",\"size\":"+actualFabric.length+"}]}";
   var requests=new java.util.concurrent.atomic.AtomicInteger();
   var fabricInstall=new ProsperoFabric(zr.resolve("cache"),new ProsperoDownloads(u->{if(u.equals(url))return new ByteArrayInputStream(actualFabric);if(u.equals(ProsperoFabric.META+version)){if(requests.incrementAndGet()!=1)throw new AssertionError("verified loader was not pinned");return new ByteArrayInputStream(bytes("[{\"loader\":{\"stable\":true,\"version\":\"0.20.1\"}}]"));}if(u.equals(ProsperoFabric.META+version+"/0.20.1/profile/json"))return new ByteArrayInputStream(bytes(profile));throw new AssertionError("unexpected Fabric transport");}));
   var fr=fabricInstall.install(version,(t,d,n)->{},()->false);fabricInstall.install(version,(t,d,n)->{},()->false);fabricInstall.verify(fr);
   try(var checker=fabricInstall.dependencies(version)){if(!checker.accepts(version,List.of(">=26.1")))throw new AssertionError("genuine Fabric predicates");}
   var fl=new ProsperoLibrary(zr);var fi=fl.add("Fabric Zink",version,1,"fabric");fl.ready(fi,true);fl.save();
   Path iris=fl.game(fi).resolve("mods/iris-test.jar");Files.createDirectories(iris.getParent());
   try(var mod=new java.util.jar.JarOutputStream(Files.newOutputStream(iris))){mod.putNextEntry(new java.util.jar.JarEntry("fabric.mod.json"));mod.write(bytes("{\"id\":\"iris\",\"version\":\"1.0.0\",\"environment\":\"client\",\"depends\":{}}"));mod.closeEntry();}
   byte[] irisOriginal=Files.readAllBytes(iris);
   var fm=new ProsperoLauncher(testAuth,zr,InstanceCheck::open,()->{preparations.incrementAndGet();});sessionField.set(fm,new ProsperoAuth.Session("OwnedPlayer","0123456789abcdef0123456789abcdef","SECRET_FABRIC_ZINK",System.currentTimeMillis()+3600000));
   var detailField=ProsperoLauncher.class.getDeclaredField("detail");detailField.setAccessible(true);detailField.set(fm,fi);
   var play=ProsperoLauncher.class.getDeclaredMethod("play");play.setAccessible(true);play.invoke(fm);waitFor(fm);
   if(!fm.tick(0)[10].equals("LAUNCH")||!fm.tick(0)[69].equals("SUPPORTED"))throw new AssertionError("Fabric launch preparation: "+fm.tick(0)[2]);
   if(!fm.tick(0)[6].equals("PLAY")||Arrays.toString(fm.tick(0)).contains("DEV TEST")||fm.tick(0)[65].contains("Development"))throw new AssertionError("normal Fabric labels");
   if(!Arrays.equals(irisOriginal,Files.readAllBytes(iris)))throw new AssertionError("Iris testing modified original mod bytes");
   List<String> fa=List.of(fm.arguments(null,null));if(fa.contains("--graphicsBackend")||fa.contains("--demo")||!fa.contains("SECRET_FABRIC_ZINK"))throw new AssertionError("Fabric original GL/full account args");
   var currentField=ProsperoLauncher.class.getDeclaredField("current");currentField.setAccessible(true);Object previous=currentField.get(null);currentField.set(null,fm);
   if(!ProsperoLauncher.gameMain().equals(ProsperoFabric.MAIN)||!ProsperoLauncher.selectedZink())throw new AssertionError("upstream Knot path");
   currentField.set(null,previous);sessionField.set(fm,null);denied(()->fm.arguments(null,null));
  }
  if(ProsperoLauncher.launchable("26.1.3","vanilla")||ProsperoLauncher.launchable("26.1-snapshot-1","vanilla")||ProsperoGraphics.zink("26.2","vanilla")||!ProsperoGraphics.vulkan("26.2","GLFW")||!ProsperoGraphics.vulkan("26.3","SDL"))throw new AssertionError("version/backend boundary");
  Files.writeString(channel,"demo");if(ProsperoLauncher.launchable("26.1","vanilla"))throw new AssertionError("Zink leaked into default Demo");
  Files.delete(zinkResource);Files.delete(channel);System.clearProperty("ps5.glfw.binding");
  System.out.println("PASS normal launcher Zink build gate, all three Vanilla releases, normal labels, verified receipt/binding order, normal26.1.xVanilla/Fabric labels, owned-account guard, original GL arguments, genuine Fabric install/repair/Knot selection and untouched Iris test JAR launch preparation for all releases, Vulkan/default boundaries");
  var persisted=new ProsperoLibrary(root.resolve("model"));if(persisted.instances().size()!=1||persisted.instances().get(0).icon!=9||!persisted.instances().get(0).name.endsWith("1"))throw new AssertionError("controller persistence");
  System.out.println("PASS empty/persistent instances, isolated worlds, rename/icons/settings, L1/R1/keyboard/install/play controller flow, unsupported26.1 launch guard and startup-notice persistence, original bytes, pin verification/cache/repair/cancel/failure/traversal/HTTPS/native-classifier rejection");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-instances-')as folder:
 w=Path(folder).resolve();(w/'InstanceCheck.java').write_text(source)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'InstanceCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'-cp',str(w)+':'+cp,'InstanceCheck',str(w/'data'),str(w),str(dependency('fabric-loader'))],check=True,timeout=40)
