#!/usr/bin/env python3
"""Actual saved-login migration and fresh-app refresh restoration without live credentials."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];JDK=java_home();cp=launcher_classpath()
source=r'''
import java.nio.file.*;import java.nio.charset.*;import java.util.*;import java.util.concurrent.atomic.*;import javax.crypto.*;import javax.crypto.spec.*;import com.google.gson.*;
public final class AuthMigrationCheck {
 static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
 static void waitFor(ProsperoLauncher model)throws Exception{long until=System.nanoTime()+5_000_000_000L;while(model.tick(0)[64].equals("BUSY")&&System.nanoTime()<until)Thread.sleep(2);check(!model.tick(0)[64].equals("BUSY"),"account task timeout");}
 static ProsperoAuth.Clock clock(){return new ProsperoAuth.Clock(){public long millis(){return System.currentTimeMillis();}public void sleep(long t){}};}
 static byte[] cipher(String token,byte[] aad,byte[] key)throws Exception{byte[] nonce=new byte[12];Arrays.fill(nonce,(byte)7);Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,new SecretKeySpec(key,"AES"),new GCMParameterSpec(128,nonce));c.updateAAD(aad);byte[] encrypted=c.doFinal(token.getBytes(StandardCharsets.UTF_8));byte[] all=new byte[12+encrypted.length];System.arraycopy(nonce,0,all,0,12);System.arraycopy(encrypted,0,all,12,encrypted.length);return all;}
 static Map<String,String> files(Path root)throws Exception{Map<String,String> result=new TreeMap<>();try(var paths=Files.walk(root)){for(Path p:paths.filter(Files::isRegularFile).toList())result.put(root.relativize(p).toString(),HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p))));}return result;}
 public static void main(String[] a)throws Exception{
  Path root=Path.of(a[0]);var library=new ProsperoLibrary(root);library.settings().showIntro=false;library.settings().snapshots=true;library.settings().resolution=3;var instance=library.add("Keep world","26.3",1);library.ready(instance,true);library.save();
  Files.createDirectories(library.game(instance).resolve("saves/World"));Files.writeString(library.game(instance).resolve("saves/World/level.dat"),"WORLD_BYTES");Files.createDirectories(root.resolve("cache"));Files.writeString(root.resolve("cache/keep.jar"),"DOWNLOAD_BYTES");
  Path account=root.resolve("account");Files.createDirectories(account);byte[] key=new byte[32];Arrays.fill(key,(byte)3);Files.write(account.resolve("key"),key);Files.write(account.resolve("session"),cipher("LEGACY_MOJANG_REFRESH","ProsperoCraft account v1".getBytes(StandardCharsets.US_ASCII),key));
  var before=files(root);var calls=new AtomicInteger();var unavailable=new ProsperoAuth((e,m,t,b,bearer)->{calls.incrementAndGet();throw new AssertionError("legacy credential reached network");},clock());
  var model=new ProsperoLauncher(unavailable,root,url->{throw new AssertionError("Unexpected downloader");});waitFor(model);
  check(calls.get()==0&&model.tick(0)[5].equals("Not signed in")&&model.tick(0)[2].contains("Sign in again"),"legacy account must request fresh sign-in without network");check(before.equals(files(root)),"migration touched existing files");
  var store=new ProsperoAccountStore(root);try{store.load();throw new AssertionError("legacy decrypted/reused");}catch(ProsperoAccountStore.SignInRequired expected){}
  store.save("APP_REFRESH_INITIAL");check(store.load().equals("APP_REFRESH_INITIAL"),"current-client roundtrip");byte[] stored=Files.readAllBytes(account.resolve("session"));check(!new String(stored,StandardCharsets.ISO_8859_1).contains("APP_REFRESH_INITIAL"),"plaintext refresh");
  // An encrypted v2 credential marked for another GUID must not be submitted.
  byte[] foreign=stored.clone();String header="ProsperoCraft account v2\n";foreign[header.length()]=foreign[header.length()]=='f'?(byte)'e':(byte)'f';Files.write(account.resolve("session"),foreign);
  model=new ProsperoLauncher(unavailable,root,url->{throw new AssertionError("Unexpected downloader");});waitFor(model);check(calls.get()==0&&model.tick(0)[2].contains("Sign in again"),"foreign app token reached network");
  // Re-labeling ciphertext from another client as this app fails GCM authentication.
  byte[] otherHeader=(header+"e0c7635e-8d50-4d7e-afa3-d15db4a0a3d3\n").getBytes(StandardCharsets.US_ASCII);byte[] body=cipher("FOREIGN_REFRESH",otherHeader,key);byte[] forged=new byte[otherHeader.length+body.length];System.arraycopy((header+ProsperoAuth.CLIENT_ID+"\n").getBytes(StandardCharsets.US_ASCII),0,forged,0,otherHeader.length);System.arraycopy(body,0,forged,otherHeader.length,body.length);Files.write(account.resolve("session"),forged);
  try{store.load();throw new AssertionError("client binding bypassed");}catch(AEADBadTagException expected){}
  store.save("APP_REFRESH_INITIAL");var order=new ArrayList<ProsperoAuth.Endpoint>();
  var auth=new ProsperoAuth((e,m,t,b,bearer)->{order.add(e);String text=switch(e){
   case TOKEN->{check(b.contains("APP_REFRESH_INITIAL")&&b.contains(ProsperoAuth.CLIENT_ID)&&!b.contains("LEGACY"),"wrong refresh request");yield "{\"access_token\":\"MSA_FIXTURE\",\"refresh_token\":\"APP_REFRESH_ROTATED\"}";}
   case XBOX->{check(b.contains("d=MSA_FIXTURE"),"ticket prefix");yield "{\"Token\":\"XBL_FIXTURE\",\"DisplayClaims\":{\"xui\":[{\"uhs\":\"uhs\"}]}}";}
   case XSTS->"{\"Token\":\"XSTS_FIXTURE\",\"DisplayClaims\":{\"xui\":[{\"uhs\":\"uhs\"}]}}";
   case MINECRAFT->"{\"access_token\":\"MC_FIXTURE\",\"expires_in\":86400}";
   case LICENSE->"{\"items\":[{\"name\":\"game_minecraft\"}]}";
   case PROFILE->"{\"id\":\"0123456789abcdef0123456789abcdef\",\"name\":\"Owner\"}";
   default->throw new AssertionError("Interactive flow during current-app restore");};return new ProsperoAuth.Reply(200,JsonParser.parseString(text).getAsJsonObject());},clock());
  model=new ProsperoLauncher(auth,root,url->{throw new AssertionError("Unexpected downloader");});waitFor(model);
  check(order.equals(List.of(ProsperoAuth.Endpoint.TOKEN,ProsperoAuth.Endpoint.XBOX,ProsperoAuth.Endpoint.XSTS,ProsperoAuth.Endpoint.MINECRAFT,ProsperoAuth.Endpoint.LICENSE,ProsperoAuth.Endpoint.PROFILE)),"restore pipeline");check(model.tick(0)[5].equals("Owner")&&store.load().equals("APP_REFRESH_ROTATED"),"restored profile/rotation");
  check(Files.readString(library.game(instance).resolve("saves/World/level.dat")).equals("WORLD_BYTES")&&Files.readString(root.resolve("cache/keep.jar")).equals("DOWNLOAD_BYTES"),"world/cache changed");var reopened=new ProsperoLibrary(root);check(reopened.instances().size()==1&&reopened.settings().snapshots&&reopened.settings().resolution==3,"instances/settings changed");
  var offline=new ProsperoAuth((e,m,t,b,bearer)->{throw new java.io.IOException("SECRET_NETWORK_DETAIL");},clock());model=new ProsperoLauncher(offline,root,url->{throw new AssertionError("Unexpected downloader");});waitFor(model);check(store.load().equals("APP_REFRESH_ROTATED"),"network failure erased valid refresh");
  var revoked=new ProsperoAuth((e,m,t,b,bearer)->new ProsperoAuth.Reply(400,JsonParser.parseString("{\"error\":\"invalid_grant\"}").getAsJsonObject()),clock());model=new ProsperoLauncher(revoked,root,url->{throw new AssertionError("Unexpected downloader");});waitFor(model);check(!store.exists()&&!Files.exists(account.resolve("key")),"revoked credential cleanup");
  store.save("NEW_SIGNOUT_FIXTURE");store.clear();check(!store.exists()&&!Files.exists(account.resolve("key")),"signout");
  System.out.println("PASS legacy/foreign-client refresh blocked before network; authenticated client binding, fresh-app restore/rotation/ownership/profile, network-failure retention/revocation/signout, unchanged instances/worlds/downloads/settings");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='approved-auth-migration-')as folder:
 w=Path(folder);(w/'AuthMigrationCheck.java').write_text(source);(w/'prosperocraft-channel.txt').write_text('temp_gametest\n')
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*map(str,(ROOT/'client/launcher/java').glob('*.java')),str(w/'AuthMigrationCheck.java')],check=True)
 result=subprocess.run([str(JDK/'bin/java'),'-cp',str(w)+':'+cp,'AuthMigrationCheck',str(w/'data')],capture_output=True,text=True,timeout=30)
 assert not any(secret in result.stdout+result.stderr for secret in ['LEGACY_MOJANG_REFRESH','APP_REFRESH_INITIAL','APP_REFRESH_ROTATED','FOREIGN_REFRESH','MSA_FIXTURE','XBL_FIXTURE','XSTS_FIXTURE','MC_FIXTURE','SECRET_NETWORK_DETAIL','NEW_SIGNOUT_FIXTURE']),'credential leaked to diagnostics'
 print(result.stdout);print(result.stderr);result.check_returncode()
