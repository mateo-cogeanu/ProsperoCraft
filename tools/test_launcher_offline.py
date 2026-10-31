#!/usr/bin/env python3
"""Exercise signed offline imports and actual launcher arguments without credentials."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import json, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
JDK=java_home()
source=r'''
import java.nio.file.*;import java.security.*;import java.util.*;import com.google.gson.*;
public class OfflineCheck {
 static void reject(RunnableX job)throws Exception{try{job.run();throw new AssertionError("accepted invalid proof");}catch(java.io.IOException|java.security.SignatureException expected){}}
 interface RunnableX{void run()throws Exception;}
 static String record(KeyPair key,long checked,long expires,String name)throws Exception{
  var body=new JsonObject();body.addProperty("schema",1);body.addProperty("name",name);body.addProperty("id","1234567890abcdef1234567890abcdef");body.addProperty("verifiedAt",checked);body.addProperty("expiresAt",expires);
  byte[] payload=body.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);var sign=Signature.getInstance("SHA256withRSA");sign.initSign(key.getPrivate());sign.update(payload);return "{\"payload\":\""+Base64.getEncoder().encodeToString(payload)+"\",\"signature\":\""+Base64.getEncoder().encodeToString(sign.sign())+"\"}";
 }
 static void set(Object object,String name,Object value)throws Exception{var f=object.getClass().getDeclaredField(name);f.setAccessible(true);f.set(object,value);}
 static void done(ProsperoLauncher model)throws Exception{for(int n=0;n<500&&model.tick(0)[64].equals("BUSY");n++)Thread.sleep(10);if(model.tick(0)[64].equals("BUSY"))throw new AssertionError("worker timed out");}
 public static void main(String[] args)throws Exception{
  Path root=Path.of(args[0]);Files.createDirectories(root);var gen=KeyPairGenerator.getInstance("RSA");gen.initialize(2048);var key=gen.generateKeyPair();byte[] pub=key.getPublic().getEncoded();Files.write(Path.of(args[1]).resolve("offline-import-public-key.der"),pub);
  Files.writeString(Path.of(args[1]).resolve("prosperocraft-channel.txt"),"offline");long now=System.currentTimeMillis();Path proof=root.resolve("offline-account.json");String good=record(key,now,now+86400000,"OwnedPlayer");Files.writeString(proof,good);
  var account=ProsperoOfflineAccount.load(root,now);if(account==null||!account.name.equals("OwnedPlayer"))throw new AssertionError("valid proof rejected");
  reject(()->ProsperoOfflineAccount.read(proof,gen.generateKeyPair().getPublic().getEncoded(),now));
  Files.writeString(proof,record(key,now-10000,now-1,"OwnedPlayer"));reject(()->ProsperoOfflineAccount.read(proof,pub,now));
  Files.writeString(proof,record(key,now,now+ProsperoOfflineAccount.WEEK+1,"OwnedPlayer"));reject(()->ProsperoOfflineAccount.read(proof,pub,now));
  Files.writeString(proof,record(key,now+120000,now+86400000,"OwnedPlayer"));reject(()->ProsperoOfflineAccount.read(proof,pub,now));
  Files.writeString(proof,record(key,now,now+86400000,"../invalid"));reject(()->ProsperoOfflineAccount.read(proof,pub,now));
  var env=JsonParser.parseString(good).getAsJsonObject();byte[] payload=Base64.getDecoder().decode(env.get("payload").getAsString());payload[10]^=1;env.addProperty("payload",Base64.getEncoder().encodeToString(payload));Files.writeString(proof,env.toString());reject(()->ProsperoOfflineAccount.read(proof,pub,now));Files.writeString(proof,good);
  var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;var instance=lib.add("Existing instance","26.3",1);lib.ready(instance,true);Files.writeString(lib.game(instance).resolve("keep-world.txt"),"keep");
  Path cache=root.resolve("cache");Files.createDirectories(cache.resolve("versions/26.3"));Files.createDirectories(cache.resolve("assets/indexes"));Files.writeString(cache.resolve("versions/26.3/client.jar"),"original fixture");Files.writeString(cache.resolve("assets/indexes/34.json"),"{}");
  var receipt=new ProsperoInstall.Receipt();receipt.version="26.3";receipt.window="SDL";receipt.assetIndex="34";receipt.classpath.add("versions/26.3/client.jar");for(String path:List.of("versions/26.3/client.jar","assets/indexes/34.json")){Path file=cache.resolve(path);receipt.files.add(new ProsperoInstall.FilePin(path,"https://piston-data.mojang.com/fixture",ProsperoInstall.hash(file),Files.size(file)));}Files.writeString(cache.resolve("versions/26.3/receipt.json"),new Gson().toJson(receipt));
  var model=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("offline attempted network");});model.tick(0x4000);for(int n=0;n<3;n++)model.tick(0x40);if(!model.tick(0)[15].equals("3")||!model.tick(0)[71].equals("OFFLINE"))throw new AssertionError("offline UI inaccessible");model.tick(0x4000);done(model);if(!model.tick(0)[10].equals("LAUNCH"))throw new AssertionError(model.tick(0)[2]);
  var launch=Arrays.asList(model.arguments(null,null));if(launch.contains("--demo")||!launch.get(launch.indexOf("--username")+1).equals("OwnedPlayer")||!launch.get(launch.indexOf("--uuid")+1).equals(account.id)||!launch.contains("--disableMultiplayer")||!launch.contains("--disableChat")||!launch.get(launch.indexOf("--accessToken")+1).equals("0")||!launch.contains("1920")||!launch.contains("1080"))throw new AssertionError("wrong offline launch arguments");
  Files.writeString(proof,record(key,now-10000,now-1,"OwnedPlayer"));try{model.arguments(null,null);throw new AssertionError("expired after selection accepted");}catch(java.io.IOException expected){}Files.writeString(proof,good);
  var demo=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});demo.tick(0x4000);demo.tick(0x4000);done(demo);if(!Arrays.asList(demo.arguments(null,null)).contains("--demo"))throw new AssertionError("demo changed");
  if(!Files.readString(lib.game(instance).resolve("keep-world.txt")).equals("keep"))throw new AssertionError("world lost");Files.delete(proof);var absent=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});if(!absent.tick(0)[71].isEmpty())throw new AssertionError("missing proof accepted");
  Files.writeString(proof,good);Files.writeString(Path.of(args[1]).resolve("prosperocraft-channel.txt"),"demo");
  var publicModel=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});if(!publicModel.tick(0)[71].isEmpty()||!publicModel.tick(0)[73].equals("DEMO BRANCH")||ProsperoOfflineAccount.load(root,now)!=null)throw new AssertionError("Demo accepted offline profile");
  set(model,"offlineLaunch",true);try{model.arguments(null,null);throw new AssertionError("Demo allowed forced offline launch");}catch(java.io.IOException expected){}
  Files.delete(Path.of(args[1]).resolve("prosperocraft-channel.txt"));if(ProsperoChannel.offline())throw new AssertionError("missing channel enabled offline");Files.writeString(Path.of(args[1]).resolve("prosperocraft-channel.txt"),"unexpected");if(ProsperoChannel.offline())throw new AssertionError("invalid channel enabled offline");
  System.out.println("PASS signed ownership lease/signature tampering/wrong key/expiry/future/invalid profile; actual offline controller/cache/arguments, no network/token, demo/world/1080p preserved");
 }
}'''
with tempfile.TemporaryDirectory(prefix='prospero-offline-') as folder:
    w=Path(folder);(w/'OfflineCheck.java').write_text(source)
    cp=launcher_classpath()
    subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'OfflineCheck.java')],check=True)
    subprocess.run([str(JDK/'bin/java'),'-cp',str(w)+':'+cp,'OfflineCheck',str(w/'data'),str(w)],check=True,timeout=40)
