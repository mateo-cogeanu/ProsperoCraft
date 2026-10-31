import com.google.gson.*;
import java.io.*;
import java.net.*;
import javax.net.ssl.HttpsURLConnection;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Public content transport: bounded metadata, verified files, no credentials. */
final class ProsperoDownloads {
 static final String AGENT=ProsperoBuild.USER_AGENT;
 static final Set<String> HOSTS=Set.of("api.modrinth.com","cdn.modrinth.com","meta.fabricmc.net","maven.fabricmc.net");
 final ProsperoInstall.Source source;
 ProsperoDownloads(){this(ProsperoDownloads::network);}
 ProsperoDownloads(ProsperoInstall.Source source){this.source=source;}
 static void safe(String url)throws IOException {
  URI u;try{u=URI.create(url);}catch(RuntimeException e){throw new IOException("Invalid content URL");}
  if(!"https".equals(u.getScheme())||u.getUserInfo()!=null||u.getPort()!=-1||u.getFragment()!=null||!HOSTS.contains(u.getHost()))throw new IOException("Untrusted content URL");
 }
 static InputStream network(String url)throws Exception {
  safe(url);var c=(HttpsURLConnection)URI.create(url).toURL().openConnection();c.setConnectTimeout(15000);c.setReadTimeout(20000);c.setInstanceFollowRedirects(false);c.setUseCaches(false);c.setRequestProperty("User-Agent",AGENT);
  try{int status=c.getResponseCode();if(status!=200)throw new IOException(status==429?"Content service is busy. Please retry shortly.":"Content service HTTP "+status);var in=c.getInputStream();return new FilterInputStream(in){public void close()throws IOException{try{super.close();}finally{c.disconnect();}}};}catch(Exception e){c.disconnect();throw e;}
 }
 byte[] bytes(String url,int max,BooleanSupplier cancel)throws Exception {
  safe(url);ProsperoInstall.active(cancel);try(var in=source.open(url)){byte[] b=in.readNBytes(max+1);if(b.length>max)throw new IOException("Content metadata too large");ProsperoInstall.active(cancel);return b;}
 }
 JsonElement json(String url,BooleanSupplier cancel)throws Exception {
  try{return JsonParser.parseString(new String(bytes(url,4*1024*1024,cancel),java.nio.charset.StandardCharsets.UTF_8));}catch(JsonParseException|IllegalStateException e){throw new IOException("Invalid content metadata");}
 }
 static String encode(String s){return URLEncoder.encode(s,java.nio.charset.StandardCharsets.UTF_8);}
 static String hash(Path path,String algorithm)throws Exception {var d=MessageDigest.getInstance(algorithm);try(var in=Files.newInputStream(path)){byte[] b=new byte[65536];for(int n;(n=in.read(b))!=-1;)d.update(b,0,n);}return HexFormat.of().formatHex(d.digest());}
 static void noLinks(Path path)throws IOException {for(Path p=path.toAbsolutePath();p!=null;p=p.getParent())if(Files.isSymbolicLink(p))throw new IOException("Content storage contains a link");}
 record Pin(String url,String algorithm,String hash,long size){}
 void obtain(Pin pin,Path target,BooleanSupplier cancel)throws Exception {
  safe(pin.url);int digits=switch(pin.algorithm){case "SHA-512"->128;case "SHA-256"->64;case "SHA-1"->40;default->0;};
  if(digits==0||pin.hash==null||!pin.hash.matches("[a-f0-9]{"+digits+"}")||pin.size<0||pin.size>512L*1024*1024)throw new IOException("Invalid content file pin");
  noLinks(target);ProsperoInstall.active(cancel);if(Files.isRegularFile(target)&&Files.size(target)==pin.size&&hash(target,pin.algorithm).equals(pin.hash))return;
  Files.createDirectories(target.getParent());Path temp=target.resolveSibling(target.getFileName()+".part");noLinks(temp);
  try{var digest=MessageDigest.getInstance(pin.algorithm);long count=0;
   try(var in=source.open(pin.url);var out=Files.newOutputStream(temp)){byte[] b=new byte[65536];for(int n;(n=in.read(b))!=-1;){ProsperoInstall.active(cancel);count+=n;if(count>pin.size)throw new IOException("Content exceeds declared size");digest.update(b,0,n);out.write(b,0,n);}}
   if(count!=pin.size||!HexFormat.of().formatHex(digest.digest()).equals(pin.hash))throw new IOException("Content checksum mismatch. Retry the download.");
   ProsperoInstall.active(cancel);Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING);
  }finally{Files.deleteIfExists(temp);}
 }
 static String text(JsonObject o,String key){return o.has(key)&&!o.get(key).isJsonNull()?o.get(key).getAsString():"";}
 static boolean contains(JsonObject o,String key,String value){return o.has(key)&&o.getAsJsonArray(key).asList().stream().anyMatch(v->v.getAsString().equals(value));}
}
