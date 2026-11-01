import com.google.gson.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import java.net.*;
import java.lang.reflect.*;

/** Read-only Fabric manifests, including nested modules; upstream version predicates. */
final class ProsperoDependencies {
 record Need(String owner,String id,List<String> versions){}
 record Module(String id,String version,Map<String,List<String>> depends){}
 static final class Versions implements AutoCloseable {
  final URLClassLoader loader;final Method parseVersion,parsePredicate;final String fabric;
  Versions(Path jar,String fabric)throws Exception {this.fabric=fabric;loader=new URLClassLoader(new URL[]{jar.toUri().toURL()},ProsperoDependencies.class.getClassLoader());parseVersion=loader.loadClass("net.fabricmc.loader.api.Version").getMethod("parse",String.class);parsePredicate=loader.loadClass("net.fabricmc.loader.api.metadata.version.VersionPredicate").getMethod("parse",String.class);}
  @SuppressWarnings("unchecked")
  boolean accepts(String version,List<String> choices)throws Exception {Object value=parseVersion.invoke(null,version);for(String choice:choices){Object predicate=parsePredicate.invoke(null,choice);if(((java.util.function.Predicate<Object>)predicate).test(value))return true;}return false;}
  @SuppressWarnings("unchecked")
  int compare(String a,String b)throws Exception{return ((Comparable<Object>)parseVersion.invoke(null,a)).compareTo(parseVersion.invoke(null,b));}
  public void close()throws IOException{loader.close();}
 }
 static final class Scan {
  final Map<String,List<Module>> modules=new LinkedHashMap<>();final Map<String,Module> roots=new HashMap<>();int count;long nestedBytes;
  void manifest(byte[] json,java.util.function.Function<String,byte[]> nested,int depth)throws Exception {
   if(++count>1024||depth>8)throw new IOException("Too many nested Fabric modules");
   var m=JsonParser.parseString(new String(json,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();String id=ProsperoDownloads.text(m,"id"),version=ProsperoDownloads.text(m,"version");
   if(id.isEmpty()||version.isEmpty())throw new IOException("Invalid Fabric mod manifest");
   if("server".equals(ProsperoDownloads.text(m,"environment")))throw new IOException("Server-only mod: "+id);
   Map<String,List<String>> depends=new LinkedHashMap<>();if(m.has("depends"))for(var e:m.getAsJsonObject("depends").entrySet()){ArrayList<String> terms=new ArrayList<>();if(e.getValue().isJsonArray())for(var v:e.getValue().getAsJsonArray())terms.add(v.getAsString());else terms.add(e.getValue().getAsString());if(terms.isEmpty())throw new IOException("Empty dependency condition");depends.put(e.getKey(),List.copyOf(terms));}
   Module module=new Module(id,version,depends);modules.computeIfAbsent(id,k->new ArrayList<>()).add(module);if(depth==0){Module prior=roots.putIfAbsent(id,module);if(prior!=null&&!prior.version.equals(version))throw new IOException("Multiple top-level versions provide mod "+id);}
   if(m.has("provides"))for(var v:m.getAsJsonArray("provides"))modules.computeIfAbsent(v.getAsString(),k->new ArrayList<>()).add(module);
   if(m.has("jars"))for(var entry:m.getAsJsonArray("jars")){String path=entry.getAsJsonObject().get("file").getAsString();if(path.startsWith("/")||path.contains("\\")||Arrays.asList(path.split("/")).contains(".."))throw new IOException("Invalid nested mod path");byte[] bytes=nested.apply(path);nestedBytes+=bytes.length;if(nestedBytes>64L*1024*1024)throw new IOException("Nested mod metadata exceeds limit");archive(bytes,depth+1);}
  }
  byte[] bounded(InputStream in,int max)throws IOException {try(in){byte[] b=in.readNBytes(max+1);if(b.length>max)throw new IOException("Mod metadata exceeds limit");return b;}}
  void file(Path path)throws Exception {
   ProsperoDownloads.noLinks(path);try(var zip=new ZipFile(path.toFile())){var entry=zip.getEntry("fabric.mod.json");if(entry==null)return;byte[] json=bounded(zip.getInputStream(entry),128*1024);manifest(json,p->{try{var nested=zip.getEntry(p);if(nested==null)throw new IOException("Nested mod missing");return bounded(zip.getInputStream(nested),16*1024*1024);}catch(IOException bad){throw new java.io.UncheckedIOException(bad);}},0);}
  }
  void archive(byte[] bytes,int depth)throws Exception {
   Map<String,byte[]> entries=new HashMap<>();int seen=0;try(var zip=new ZipInputStream(new ByteArrayInputStream(bytes))){for(ZipEntry e;(e=zip.getNextEntry())!=null;){if(++seen>16384||entries.size()>256)throw new IOException("Nested mod archive exceeds limit");if(e.getName().equals("fabric.mod.json")||e.getName().endsWith(".jar")){int max=e.getName().endsWith(".jar")?16*1024*1024:128*1024;byte[] body=zip.readNBytes(max+1);if(body.length>max)throw new IOException("Nested mod entry too large");nestedBytes+=body.length;if(nestedBytes>64L*1024*1024)throw new IOException("Nested mod metadata exceeds limit");entries.put(e.getName(),body);}}}
   if(entries.containsKey("fabric.mod.json"))manifest(entries.get("fabric.mod.json"),p->{byte[] b=entries.get(p);if(b==null)throw new IllegalArgumentException("Nested mod missing");return b;},depth);
  }
 }
 static void verifyVulkan(Collection<Path> jars)throws Exception {verifyGraphics(jars,false);}
 static void verifyGraphics(Collection<Path> jars,boolean zink)throws Exception {
  Scan scan=new Scan();for(Path path:jars)scan.file(path);
  if(!zink&&scan.modules.containsKey("iris"))throw new IOException("Iris needs OpenGL; this build uses Vulkan. Uninstall Iris in Installed. Use Vitrail for shaders.");
 }
 static Set<String> providedIds(Path jar)throws Exception {Scan scan=new Scan();scan.file(jar);return Set.copyOf(scan.modules.keySet());}
 static Module rootModule(Path jar)throws Exception {
  Scan scan=new Scan();scan.file(jar);if(scan.roots.size()!=1)throw new IOException("Cannot identify installed Fabric mod for update");return scan.roots.values().iterator().next();
 }
 static List<Need> missing(Collection<Path> jars,String game,Versions versions)throws Exception {return missing(jars,game,versions,false);}
 static List<Need> requiredUpdates(Collection<Path> jars,String game,Versions versions)throws Exception {return missing(jars,game,versions,true);}
 private static List<Need> missing(Collection<Path> jars,String game,Versions versions,boolean updates)throws Exception {
  Scan scan=new Scan();for(Path path:jars)scan.file(path);
  var chosen=new HashMap<String,Module>();for(var e:scan.modules.entrySet()){
   Module best=scan.roots.get(e.getKey());if(best==null)for(Module candidate:e.getValue())if(best==null||(versions==null?candidate.version.compareTo(best.version):versions.compare(candidate.version,best.version))>0)best=candidate;chosen.put(e.getKey(),best);
  }
  for(int pass=0;pass<128;pass++){
   var requirements=new LinkedHashMap<String,List<Need>>();
   for(Module mod:new HashSet<>(chosen.values()))for(var dep:mod.depends.entrySet())requirements.computeIfAbsent(dep.getKey(),k->new ArrayList<>()).add(new Need(mod.id,dep.getKey(),dep.getValue()));
   var missing=new ArrayList<Need>();boolean changed=false;
   for(var entry:requirements.entrySet()){
    String id=entry.getKey();String builtin=id.equals("minecraft")?game:id.equals("java")?"25":id.equals("fabricloader")?versions==null?"0.20.1":versions.fabric:null;
    if(builtin!=null){for(Need need:entry.getValue())if(!accepts(versions,builtin,need.versions))throw new IOException(need.owner+" requires "+id+" "+need.versions+"; installed "+builtin);continue;}
    List<Module> candidates=scan.modules.get(id);if(candidates==null){missing.addAll(entry.getValue());continue;}
    Module fixed=scan.roots.get(id),best=null;
    for(Module candidate:candidates){if(fixed!=null&&!fixed.version.equals(candidate.version))continue;boolean fits=true;for(Need need:entry.getValue())if(!accepts(versions,candidate.version,need.versions)){fits=false;break;}
     if(fits&&(best==null||(versions==null?candidate.version.compareTo(best.version):versions.compare(candidate.version,best.version))>0))best=candidate;
    }
    if(best==null){if(updates){for(Need need:entry.getValue())if(!accepts(versions,chosen.get(id).version,need.versions))missing.add(need);continue;}Need n=entry.getValue().getFirst();throw new IOException(n.owner+" requires "+id+" "+n.versions+"; installed "+chosen.get(id).version+". Change the conflicting mod first.");}
    if(!best.equals(chosen.get(id))){chosen.put(id,best);changed=true;}
   }
   if(!changed)return missing;
  }
  throw new IOException("Mod dependency versions cannot be resolved together");
 }
 private static boolean accepts(Versions versions,String actual,List<String> terms)throws Exception{return versions==null?terms.contains("*"):versions.accepts(actual,terms);}
}
