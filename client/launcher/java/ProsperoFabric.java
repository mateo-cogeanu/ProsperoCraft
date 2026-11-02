import com.google.gson.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Standard upstream Fabric profile; original client JAR stays unchanged. */
final class ProsperoFabric {
 static final String META="https://meta.fabricmc.net/v2/versions/loader/";
 static final String MAIN="net.fabricmc.loader.impl.launch.knot.KnotClient";
 record Entry(String path,ProsperoDownloads.Pin pin){}
 static final class Receipt {String game,loader,main;ArrayList<Entry> files=new ArrayList<>();}
 final Path cache;final ProsperoDownloads download;
 ProsperoFabric(Path cache){this(cache,new ProsperoDownloads());}
 ProsperoFabric(Path cache,ProsperoDownloads download){this.cache=cache;this.download=download;}
 static void game(String version)throws IOException{if(!version.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}"))throw new IOException("Invalid Fabric game version");}
 Path receiptPath(String version)throws IOException{game(version);return cache.resolve("fabric/"+version+"/receipt.json");}
 Receipt install(String version,ProsperoInstall.Progress progress,BooleanSupplier cancel)throws Exception {
  game(version);Receipt previous=null;try{previous=read(version);verify(previous);}catch(Exception missing){}
  // Keep a previously chosen, verified loader pinned when repairing an instance.
  String loader=previous==null?"":previous.loader;
  if(loader.isEmpty())for(var row:download.json(META+version,cancel).getAsJsonArray()){
   var l=row.getAsJsonObject().getAsJsonObject("loader");if(l.get("stable").getAsBoolean()){loader=l.get("version").getAsString();break;}
  }
  if(!loader.matches("[0-9][A-Za-z0-9.+_-]{0,60}"))throw new IOException("Fabric is not available for this game version");
  JsonObject profile=download.json(META+version+"/"+loader+"/profile/json",cancel).getAsJsonObject();
  if(!version.equals(ProsperoDownloads.text(profile,"inheritsFrom"))||!MAIN.equals(ProsperoDownloads.text(profile,"mainClass")))throw new IOException("Unexpected Fabric profile");
  Receipt receipt=new Receipt();receipt.game=version;receipt.loader=loader;receipt.main=MAIN;
  for(var item:profile.getAsJsonArray("libraries")){
   var lib=item.getAsJsonObject();String[] coordinate=lib.get("name").getAsString().split(":");if(coordinate.length!=3)throw new IOException("Unsupported Fabric library");
   for(String part:coordinate)if(!part.matches("[A-Za-z0-9_.+\\-]+"))throw new IOException("Invalid Fabric coordinate");
   String path=coordinate[0].replace('.','/')+"/"+coordinate[1]+"/"+coordinate[2]+"/"+coordinate[1]+"-"+coordinate[2]+".jar";
   String url=lib.get("url").getAsString()+path;if(!URI.create(url).getHost().equals("maven.fabricmc.net"))throw new IOException("Unsupported Fabric Maven host");
   String hash=ProsperoDownloads.text(lib,"sha1");long size;
   if(hash.isEmpty()){
    // Fabric Loader itself has a Maven checksum sidecar, unlike ASM/Mixin profile entries.
    hash=new String(download.bytes(url+".sha1",256,cancel),java.nio.charset.StandardCharsets.US_ASCII).strip();
    byte[] jar=download.bytes(url,16*1024*1024,cancel);size=jar.length;
    var pin=new ProsperoDownloads.Pin(url,"SHA-1",hash,size);Path target=ProsperoInstall.relative(cache,"fabric/libraries/"+path);
    // Same verified-file path, including sidecar validation; cache the one fetched body.
    byte[] body=jar;new ProsperoDownloads(u->{if(!u.equals(url))throw new IOException();return new ByteArrayInputStream(body);}).obtain(pin,target,cancel);
   }else size=lib.get("size").getAsLong();
   var entry=new Entry("fabric/libraries/"+path,new ProsperoDownloads.Pin(url,"SHA-1",hash,size));download.obtain(entry.pin,ProsperoInstall.relative(cache,entry.path),cancel);receipt.files.add(entry);
  }
  if(receipt.files.isEmpty())throw new IOException("Fabric profile contains no libraries");
  ProsperoInstall.active(cancel);ProsperoInstall.save(receiptPath(version),new Gson().toJson(receipt));progress.update("Fabric "+loader+" ready",1,1);return receipt;
 }
 Receipt read(String version)throws Exception {Path path=receiptPath(version);ProsperoDownloads.noLinks(path);if(Files.size(path)>256*1024)throw new IOException("Invalid Fabric receipt");Receipt r=new Gson().fromJson(Files.readString(path),Receipt.class);if(r==null||!version.equals(r.game)||!MAIN.equals(r.main)||r.loader==null||!r.loader.matches("[0-9][A-Za-z0-9.+_-]{0,60}")||r.files==null||r.files.isEmpty()||r.files.size()>64)throw new IOException("Repair the Fabric download");return r;}
 void verify(Receipt receipt)throws Exception {for(var e:receipt.files){Path p=ProsperoInstall.relative(cache,e.path);ProsperoDownloads.safe(e.pin.url());ProsperoDownloads.noLinks(p);if(!Files.isRegularFile(p)||Files.size(p)!=e.pin.size()||!ProsperoDownloads.hash(p,e.pin.algorithm()).equals(e.pin.hash()))throw new IOException("Fabric files need Repair download");}}
 java.net.URLClassLoader loader(Receipt receipt,java.net.URLClassLoader vanilla)throws Exception {verify(receipt);ArrayList<URL> urls=new ArrayList<>();for(var e:receipt.files)urls.add(ProsperoInstall.relative(cache,e.path).toUri().toURL());urls.addAll(List.of(vanilla.getURLs()));return new ProsperoGameLoader(urls.toArray(URL[]::new),vanilla.getParent());}
 ProsperoDependencies.Versions dependencies(String game)throws Exception {Receipt receipt=read(game);verify(receipt);for(var entry:receipt.files)if(entry.path.contains("/fabric-loader/"))return new ProsperoDependencies.Versions(ProsperoInstall.relative(cache,entry.path),receipt.loader);throw new IOException("Fabric loader metadata is unavailable. Repair the instance download.");}
 static void configure(java.net.URLClassLoader loader,Path game,String version){
  // Knot discovers the game from java.class.path. Preserve PS5 dependency overlays
  // ahead of publisher libraries while its own standard Mixin loader owns the game.
  // Restore standard cached resource reads after104 startup stalled with
  // uncached archive churn. Causation and descriptor headroom need PS5 tests.
  URLConnection.setDefaultUseCaches("jar",true);
  String existing=System.getProperty("java.class.path","");var entries=new LinkedHashSet<String>(List.of(existing.split(java.io.File.pathSeparator)));
  var systemLibraries=new LinkedHashSet<String>(entries);
  for(URL url:loader.getURLs())try{Path path=Path.of(url.toURI());entries.add(path.toString());String file=path.getFileName().toString();if(file.startsWith("lwjgl-")||file.startsWith("oshi-"))systemLibraries.add(path.toString());}catch(Exception invalid){throw new IllegalArgumentException(invalid);}
  systemLibraries.remove("");System.setProperty("fabric.systemLibraries",String.join(java.io.File.pathSeparator,systemLibraries));
  entries.remove("");System.setProperty("java.class.path",String.join(java.io.File.pathSeparator,entries));System.setProperty("fabric.gameVersion",version);
  System.setProperty("fabric.gameJarPath.client",game.toString());
 }
}
