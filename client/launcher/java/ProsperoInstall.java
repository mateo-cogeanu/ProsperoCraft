import com.google.gson.*;
import java.io.*;
import java.net.*;
import javax.net.ssl.HttpsURLConnection;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.BooleanSupplier;

/** Publisher metadata -> verified immutable cache. No game transformations or native downloads. */
public final class ProsperoInstall {
 static final String MANIFEST="https://piston-meta.mojang.com/mc/game/version_manifest_v2.json";
 interface Source {InputStream open(String url)throws Exception;}
 interface Progress {void update(String text,long completed,long total);}
 record Version(String id,String type,String url,String sha1){}
 record FilePin(String path,String url,String sha1,long size){}
 static final class Receipt {String version,assetIndex,window;int javaMajor;ArrayList<FilePin> files=new ArrayList<>();ArrayList<String> classpath=new ArrayList<>();}
 private final Path root;private final Source source;
 ProsperoInstall(Path root){this(root,ProsperoInstall::network);}
 ProsperoInstall(Path root,Source source){this.root=root;this.source=source;}
 static void safeUrl(String url)throws IOException {
  URI uri;try{uri=URI.create(url);}catch(RuntimeException e){throw new IOException("Invalid publisher URL");}
  if(!"https".equals(uri.getScheme())||uri.getUserInfo()!=null||uri.getPort()!=-1||!Set.of("piston-meta.mojang.com","piston-data.mojang.com","libraries.minecraft.net","resources.download.minecraft.net","launchermeta.mojang.com","launcher.mojang.com").contains(uri.getHost()))throw new IOException("Untrusted publisher URL");
 }
 static InputStream network(String url)throws Exception {
  safeUrl(url);HttpsURLConnection c=(HttpsURLConnection)URI.create(url).toURL().openConnection();c.setConnectTimeout(15000);c.setReadTimeout(20000);c.setInstanceFollowRedirects(false);c.setUseCaches(false);c.setRequestProperty("User-Agent",ProsperoBuild.USER_AGENT);
  try{if(c.getResponseCode()!=200)throw new IOException("Publisher download HTTP "+c.getResponseCode());InputStream input=c.getInputStream();return new FilterInputStream(input){public void close()throws IOException{try{super.close();}finally{c.disconnect();}}};}catch(Exception error){c.disconnect();throw error;}
 }
 static void active(BooleanSupplier cancelled)throws IOException {if(Thread.currentThread().isInterrupted()||cancelled.getAsBoolean())throw new IOException("Download cancelled. Verified files are kept for retry.");}
 static Path relative(Path base,String path)throws IOException {
  if(path==null||path.isEmpty()||path.indexOf('\\')>=0||path.indexOf('\0')>=0)throw new IOException("Invalid cache path");
  Path result=base.resolve(path).normalize();if(!result.startsWith(base.normalize())||Path.of(path).isAbsolute()||Arrays.asList(path.split("/")).contains(".."))throw new IOException("Unsafe cache path");return result;
 }
 static String hash(Path path)throws Exception {var digest=MessageDigest.getInstance("SHA-1");try(var in=Files.newInputStream(path)){byte[] chunk=new byte[65536];for(int n;(n=in.read(chunk))!=-1;)digest.update(chunk,0,n);}return HexFormat.of().formatHex(digest.digest());}
 static void save(Path path,String text)throws IOException {Files.createDirectories(path.getParent());Path temp=path.resolveSibling(path.getFileName()+".tmp");Files.writeString(temp,text,StandardCharsets.UTF_8);Files.move(temp,path,StandardCopyOption.REPLACE_EXISTING);}
 static JsonObject object(byte[] bytes)throws IOException {try{return JsonParser.parseString(new String(bytes,StandardCharsets.UTF_8)).getAsJsonObject();}catch(RuntimeException e){throw new IOException("Invalid publisher metadata");}}
 byte[] json(String url,BooleanSupplier cancelled)throws Exception {
  safeUrl(url);active(cancelled);try(var in=source.open(url)){byte[] bytes=in.readNBytes(2*1024*1024+1);if(bytes.length>2*1024*1024)throw new IOException("Publisher metadata too large");active(cancelled);return bytes;}
 }
 List<Version> catalog(boolean snapshots,BooleanSupplier cancelled)throws Exception {
  byte[] bytes;
  try{bytes=json(MANIFEST,cancelled);save(root.resolve("catalog.json"),new String(bytes,StandardCharsets.UTF_8));}
  catch(Exception offline){active(cancelled);Path cached=root.resolve("catalog.json");if(!Files.isRegularFile(cached))throw offline;bytes=Files.readAllBytes(cached);}
  ArrayList<Version> versions=new ArrayList<>();
  for(JsonElement item:object(bytes).getAsJsonArray("versions")){JsonObject row=item.getAsJsonObject();String id=row.get("id").getAsString(),type=row.get("type").getAsString();
   if(id.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}")&&(type.equals("release")||snapshots)){String url=row.get("url").getAsString(),sha=row.get("sha1").getAsString();safeUrl(url);if(!sha.matches("[a-f0-9]{40}"))throw new IOException("Invalid metadata hash");versions.add(new Version(id,type,url,sha));}}
  return List.copyOf(versions);
 }
 private void obtain(FilePin pin,BooleanSupplier cancelled)throws Exception {
  if(!pin.sha1.matches("[a-f0-9]{40}")||pin.size<0||pin.size>1024L*1024*1024)throw new IOException("Invalid publisher file pin");
  safeUrl(pin.url);Path path=relative(root,pin.path);active(cancelled);
  if(Files.isRegularFile(path)&&Files.size(path)==pin.size&&hash(path).equals(pin.sha1))return;
  Files.createDirectories(path.getParent());Path temp=path.resolveSibling(path.getFileName()+".part");
  try{
   var digest=MessageDigest.getInstance("SHA-1");long count=0;
   try(var in=source.open(pin.url);var out=Files.newOutputStream(temp)){byte[] bytes=new byte[65536];for(int n;(n=in.read(bytes))!=-1;){active(cancelled);count+=n;if(count>pin.size)throw new IOException("Download exceeds publisher size");digest.update(bytes,0,n);out.write(bytes,0,n);}}
   if(count!=pin.size||!HexFormat.of().formatHex(digest.digest()).equals(pin.sha1))throw new IOException("Publisher checksum mismatch. Retry the download.");
   active(cancelled);Files.move(temp,path,StandardCopyOption.REPLACE_EXISTING);
  }finally{Files.deleteIfExists(temp);}
 }
 private static FilePin pin(String path,JsonObject data){return new FilePin(path,data.get("url").getAsString(),data.get("sha1").getAsString(),data.get("size").getAsLong());}
 static boolean allowed(JsonObject lib){
  if(!lib.has("rules"))return true;boolean allowed=false;
  for(var item:lib.getAsJsonArray("rules")){var rule=item.getAsJsonObject();boolean matches=!rule.has("features");if(rule.has("os")){var os=rule.getAsJsonObject("os");if(os.has("name"))matches&=os.get("name").getAsString().equals("linux");if(os.has("arch"))matches&=os.get("arch").getAsString().matches("x86_64|amd64");if(os.has("version"))matches=false;}if(matches)allowed=rule.get("action").getAsString().equals("allow");}return allowed;
 }
 Receipt install(Version version,int workers,Progress progress,BooleanSupplier cancelled)throws Exception {
  if(!version.id.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}"))throw new IOException("Only26.x instances are supported");
  byte[] metadata=json(version.url,cancelled);if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-1").digest(metadata)).equals(version.sha1))throw new IOException("Version metadata checksum mismatch");
  JsonObject meta=object(metadata);if(!version.id.equals(meta.get("id").getAsString()))throw new IOException("Version metadata identity mismatch");
  int javaMajor=meta.getAsJsonObject("javaVersion").get("majorVersion").getAsInt();if(javaMajor<8||javaMajor>100)throw new IOException("Invalid publisher Java requirement");
  if(!"net.minecraft.client.main.Main".equals(meta.get("mainClass").getAsString()))throw new IOException("Unsupported client entry point");
  Receipt receipt=new Receipt();receipt.javaMajor=javaMajor;receipt.version=version.id;receipt.assetIndex=meta.getAsJsonObject("assetIndex").get("id").getAsString();receipt.window="GLFW";
  String client="versions/"+version.id+"/client.jar";receipt.files.add(pin(client,meta.getAsJsonObject("downloads").getAsJsonObject("client")));receipt.classpath.add(client);
  for(var item:meta.getAsJsonArray("libraries")){JsonObject lib=item.getAsJsonObject();String name=lib.get("name").getAsString();if(name.contains(":natives-")||(name.startsWith("io.netty:netty-transport-native-")&&name.split(":").length>3)||!allowed(lib))continue;
   if(name.startsWith("org.lwjgl:lwjgl-sdl:"))receipt.window="SDL";
   JsonObject downloads=lib.getAsJsonObject("downloads");if(downloads==null||!downloads.has("artifact"))continue;JsonObject artifact=downloads.getAsJsonObject("artifact");String path="libraries/"+artifact.get("path").getAsString();relative(root,path);receipt.files.add(pin(path,artifact));receipt.classpath.add(path);
  }
  JsonObject index=meta.getAsJsonObject("assetIndex");FilePin indexPin=pin("assets/indexes/"+receipt.assetIndex+".json",index);receipt.files.add(indexPin);
  progress.update("Reading asset list",0,1);obtain(indexPin,cancelled);JsonObject objects=object(Files.readAllBytes(relative(root,indexPin.path))).getAsJsonObject("objects");Set<String> unique=new HashSet<>();
  for(var entry:objects.entrySet()){JsonObject row=entry.getValue().getAsJsonObject();String sha=row.get("hash").getAsString();if(!sha.matches("[a-f0-9]{40}"))throw new IOException("Invalid asset hash");if(unique.add(sha))receipt.files.add(new FilePin("assets/objects/"+sha.substring(0,2)+"/"+sha,"https://resources.download.minecraft.net/"+sha.substring(0,2)+"/"+sha,sha,row.get("size").getAsLong()));}
  long total=receipt.files.stream().mapToLong(FilePin::size).sum();var completed=new java.util.concurrent.atomic.AtomicLong();
  ExecutorService pool=Executors.newFixedThreadPool(Math.max(1,Math.min(workers,6)),task->{Thread t=new Thread(task,"ProsperoCraft download");t.setDaemon(true);return t;});ArrayList<Future<?>> jobs=new ArrayList<>();
  try{
   for(FilePin file:receipt.files)jobs.add(pool.submit(()->{try{obtain(file,cancelled);progress.update("Downloading "+version.id,completed.addAndGet(file.size),total);}catch(Exception error){throw new CompletionException(error);}}));
   for(var job:jobs){active(cancelled);try{job.get();}catch(ExecutionException error){Throwable cause=error.getCause();if(cause instanceof CompletionException&&cause.getCause()!=null)cause=cause.getCause();if(cause instanceof Exception checked)throw checked;throw error;}}
  }finally{for(var job:jobs)job.cancel(true);pool.shutdownNow();if(!pool.awaitTermination(25,TimeUnit.SECONDS))throw new IOException("Downloads are still stopping; reopen before retrying");}
  active(cancelled);save(root.resolve("versions/"+version.id+"/metadata.json"),new String(metadata,StandardCharsets.UTF_8));save(root.resolve("versions/"+version.id+"/receipt.json"),new Gson().toJson(receipt));progress.update("Ready to play",total,total);return receipt;
 }
 Receipt receipt(String version)throws Exception {if(!version.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}"))throw new IOException("Invalid version");return new Gson().fromJson(Files.readString(root.resolve("versions/"+version+"/receipt.json")),Receipt.class);}
 void verify(Receipt receipt)throws Exception {
  if(receipt==null||receipt.classpath==null||receipt.classpath.isEmpty()||receipt.files==null)throw new IOException("Install this instance first");
  for(String entry:receipt.classpath){FilePin pin=receipt.files.stream().filter(f->f.path.equals(entry)).findFirst().orElseThrow(()->new IOException("Unverified class path"));Path path=relative(root,entry);if(!Files.isRegularFile(path)||Files.size(path)!=pin.size||!hash(path).equals(pin.sha1))throw new IOException("Instance files need repair. Select Repair download.");}
  String indexPath="assets/indexes/"+receipt.assetIndex+".json";FilePin index=receipt.files.stream().filter(f->f.path.equals(indexPath)).findFirst().orElseThrow(()->new IOException("Missing asset index pin"));Path path=relative(root,indexPath);
  if(!Files.isRegularFile(path)||Files.size(path)!=index.size||!hash(path).equals(index.sha1))throw new IOException("Asset index needs repair download");
 }
 static String hardwarePort(Receipt receipt){if(receipt.classpath.stream().anyMatch(p->p.endsWith("/oshi-core-6.9.0.jar")))return "oshi-6.9.0-ps5-platform.jar";if(receipt.classpath.stream().anyMatch(p->p.endsWith("/oshi-common-7.7.2.jar")))return "oshi-7.7.2-ps5-provider.jar";return null;}
 java.net.URLClassLoader loader(Receipt receipt)throws Exception {verify(receipt);ArrayList<URL> urls=new ArrayList<>();String port=hardwarePort(receipt);if(port!=null){Path hardware=Path.of("/app0/assets/java25/ports/"+port);if(Files.isRegularFile(hardware))urls.add(hardware.toUri().toURL());}if("26.2".equals(receipt.version)&&"GLFW".equals(receipt.window)){Path binding=Path.of(System.getProperty("ps5.glfw.binding","/app0/assets/java25/ports/lwjgl-glfw-3.4.1-ps5-callback343.jar"));if(!Files.isRegularFile(binding))throw new IOException("26.2 GLFW callback binding missing from app; update ProsperoCraft.");urls.add(binding.toUri().toURL());}for(String file:receipt.classpath)urls.add(relative(root,file).toUri().toURL());return new URLClassLoader(urls.toArray(URL[]::new),ProsperoInstall.class.getClassLoader());}
}
