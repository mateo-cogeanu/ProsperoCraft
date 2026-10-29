import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.SecureRandom;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

/** Local refresh credential only. No access-token/credential text in JSON or logs.
 * The adjacent app-local key is not a hardware-backed keychain: filesystem access
 * to both files can decrypt it. Sign out erases both; no credentials are packaged. */
final class ProsperoAccountStore {
 private static final byte[] HEADER=("ProsperoCraft account v2\n"+ProsperoAuth.CLIENT_ID+"\n").getBytes(StandardCharsets.US_ASCII);
 static final class SignInRequired extends java.io.IOException {SignInRequired(){super("Sign in again to use the approved ProsperoCraft application.");}}
 private final Path root;
 ProsperoAccountStore(Path library){root=library.resolve("account");}
 private void privateMode(Path path,boolean directory)throws Exception{
  try{Files.setPosixFilePermissions(path,PosixFilePermissions.fromString(directory?"rwx------":"rw-------"));}catch(UnsupportedOperationException|java.io.IOException unavailable){/* PS5 app-local storage may not expose chmod. */}
 }
 synchronized void save(String refresh)throws Exception {
  if(refresh==null||refresh.isEmpty()){clear();return;}
  if(refresh.length()>65536)throw new java.io.IOException("Invalid account credential");
  if(Files.isSymbolicLink(root))throw new java.io.IOException("Unsafe account storage");
  Files.createDirectories(root);privateMode(root,true);
  for(String n:new String[]{"key","session","session.tmp"})if(Files.isSymbolicLink(root.resolve(n)))throw new java.io.IOException("Unsafe account storage");
  if(Files.isSymbolicLink(root))throw new java.io.IOException("Unsafe account storage");
  byte[] key;
  if(Files.exists(root.resolve("key"))){key=Files.readAllBytes(root.resolve("key"));if(key.length!=32)throw new java.io.IOException("Invalid account key");}
  else{key=new byte[32];new SecureRandom().nextBytes(key);Files.write(root.resolve("key"),key,StandardOpenOption.CREATE_NEW);privateMode(root.resolve("key"),false);}
  byte[] nonce=new byte[12];new SecureRandom().nextBytes(nonce);
  try{Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,new SecretKeySpec(key,"AES"),new GCMParameterSpec(128,nonce));cipher.updateAAD(HEADER);byte[] body=cipher.doFinal(refresh.getBytes(StandardCharsets.UTF_8));byte[] all=new byte[HEADER.length+12+body.length];System.arraycopy(HEADER,0,all,0,HEADER.length);System.arraycopy(nonce,0,all,HEADER.length,12);System.arraycopy(body,0,all,HEADER.length+12,body.length);Path temp=root.resolve("session.tmp");Files.write(temp,all);privateMode(temp,false);Files.move(temp,root.resolve("session"),StandardCopyOption.REPLACE_EXISTING);privateMode(root.resolve("session"),false);}finally{Arrays.fill(key,(byte)0);}
 }
 synchronized String load()throws Exception {
  if(!Files.exists(root.resolve("session")))return "";
  if(Files.isSymbolicLink(root)||Files.isSymbolicLink(root.resolve("session"))||Files.isSymbolicLink(root.resolve("key")))throw new java.io.IOException("Unsafe account storage");
  if(Files.size(root.resolve("session"))>70000||Files.size(root.resolve("key"))!=32)throw new java.io.IOException("Invalid saved account");
  byte[] all=Files.readAllBytes(root.resolve("session"));
  // Unbound legacy credentials may belong to Mojang. Never decrypt or submit them.
  if(all.length<HEADER.length||!Arrays.equals(Arrays.copyOf(all,HEADER.length),HEADER))throw new SignInRequired();
  if(all.length<HEADER.length+28)throw new java.io.IOException("Invalid saved account");
  byte[] key=Files.readAllBytes(root.resolve("key"));
  try{Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,new SecretKeySpec(key,"AES"),new GCMParameterSpec(128,all,HEADER.length,12));c.updateAAD(HEADER);return new String(c.doFinal(all,HEADER.length+12,all.length-HEADER.length-12),StandardCharsets.UTF_8);}finally{Arrays.fill(key,(byte)0);}
 }
 boolean exists(){return Files.isRegularFile(root.resolve("session"),LinkOption.NOFOLLOW_LINKS);}
 synchronized void clear()throws Exception{if(Files.isSymbolicLink(root))throw new java.io.IOException("Unsafe account storage");Files.deleteIfExists(root.resolve("session"));Files.deleteIfExists(root.resolve("session.tmp"));Files.deleteIfExists(root.resolve("key"));}
 @Override public String toString(){return "Saved account [credentials redacted]";}
}
