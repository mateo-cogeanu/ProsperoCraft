import com.google.gson.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Instance-scoped Modrinth browser and checksum-verified download queue. */
final class ProsperoModrinth {
 static final String API="https://api.modrinth.com/v2/";
 enum Kind {MOD("mod","mods","Mods"),SHADER("shader","shaderpacks","Shaders"),RESOURCE("resourcepack","resourcepacks","Resource packs");final String type,folder,title;Kind(String t,String f,String n){type=t;folder=f;title=n;}}
 record Hit(String id,String title,String description,long downloads,String icon){Hit(String id,String t,String d,long n){this(id,t,d,n,"");}}
 record Results(List<Hit> hits,int total){}
 record Selection(String project,String title,Kind kind){}
 record File(String project,String version,Kind kind,String filename,ProsperoDownloads.Pin pin){}
 static final class Installed {ArrayList<File> files=new ArrayList<>();}
 final ProsperoDownloads download;
 ProsperoModrinth(){this(new ProsperoDownloads());}
 ProsperoModrinth(ProsperoDownloads download){this.download=download;}
 static void id(String id)throws IOException {if(id==null||!id.matches("[A-Za-z0-9_-]{1,80}"))throw new IOException("Invalid Modrinth identifier");}
 static boolean validFilename(String name,Kind kind){
  if(name==null||kind==null||name.isEmpty()||name.startsWith(".")||name.endsWith(" ")||name.getBytes(java.nio.charset.StandardCharsets.UTF_8).length>180||!name.endsWith(kind==Kind.MOD?".jar":".zip"))return false;
  for(int cp:name.codePoints().toArray())if(Character.isISOControl(cp)||Character.getType(cp)==Character.FORMAT||Character.getType(cp)==Character.LINE_SEPARATOR||Character.getType(cp)==Character.PARAGRAPH_SEPARATOR||cp>=0xd800&&cp<=0xdfff||"/\\:<>\"|?*".indexOf(cp)>=0)return false;
  return true;
 }
 static List<Selection> defaultMods(String loader){return Set.of("fabric","neoforge").contains(loader)?List.of(new Selection("DOUdJVEm","Controlify",Kind.MOD)):List.of();}
 void installDefaults(Path game,String version,String loader,ProsperoDependencies.Versions checker,ProsperoInstall.Progress progress,BooleanSupplier cancel)throws Exception{
  List<Selection> defaults=defaultMods(loader);if(defaults.isEmpty())return;
  installSelected(game,version,loader,progress,cancel,f->{},checker,defaults,Map.of(),false);
 }
 static String array(String s){return new Gson().toJson(List.of(s));}
 Results search(Kind kind,String game,String loader,String query,int offset,BooleanSupplier cancel)throws Exception {
  if(!ProsperoVersions.valid(game))throw new IOException("Invalid content game version");if(query.length()>80||offset<0||offset>100000)throw new IOException("Invalid content search");
  if(kind==Kind.MOD&&!loader.equals("fabric"))return new Results(List.of(),0);
  var facets=new ArrayList<List<String>>();facets.add(List.of("project_type:"+kind.type));facets.add(List.of("versions:"+game));
  if(kind==Kind.MOD){facets.add(List.of("categories:fabric"));facets.add(List.of("client_side:required","client_side:optional"));}
  String url=API+"search?index=downloads&limit=4&offset="+offset+"&query="+ProsperoDownloads.encode(query)+"&facets="+ProsperoDownloads.encode(new Gson().toJson(facets));
  var data=download.json(url,cancel).getAsJsonObject();ArrayList<Hit> hits=new ArrayList<>();
  for(var item:data.getAsJsonArray("hits")){var row=item.getAsJsonObject();String project=row.get("project_id").getAsString();id(project);hits.add(new Hit(project,row.get("title").getAsString(),ProsperoDownloads.text(row,"description"),row.get("downloads").getAsLong(),ProsperoDownloads.text(row,"icon_url")));if(hits.size()==4)break;}
  return new Results(List.copyOf(hits),data.get("total_hits").getAsInt());
 }
 // Installed lists use the actual instance folders, including manually added files.
 record Local(String title,String filename,String project,Kind kind){}
 List<Local> local(Path game,Kind kind)throws Exception {
  var receipt=installed(game);Path folder=game.resolve(kind.folder);ProsperoDownloads.noLinks(folder);
  if(!Files.isDirectory(folder))return List.of();var found=new ArrayList<Local>();
  try(var files=Files.list(folder)){for(Path p:files.limit(1025).toList()){
   if(found.size()>=1024)throw new IOException("Too many installed files");String name=p.getFileName().toString();
   if(!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)||!name.endsWith(kind==Kind.MOD?".jar":".zip"))continue;
   var known=receipt.files.stream().filter(f->f.kind==kind&&f.filename.equals(name)).findFirst();
   found.add(new Local(name,name,known.isPresent()?known.get().project:"",kind));
  }}found.sort(Comparator.comparing(Local::title,String.CASE_INSENSITIVE_ORDER));return List.copyOf(found);
 }
 // Move out of the game's folders first, commit the receipt, then reclaim bytes.
 // If metadata cannot commit, put the exact original file back.
 synchronized boolean uninstall(Path game,Local item)throws Exception {
  if(item==null||item.kind==null||item.filename==null||item.filename.isEmpty()||item.filename.contains("/")||item.filename.contains("\\")||item.filename.equals(".")||item.filename.equals("..")||!item.filename.endsWith(item.kind==Kind.MOD?".jar":".zip"))throw new IOException("Invalid installed file");
  Path target=game.resolve(item.kind.folder).resolve(item.filename);ProsperoDownloads.noLinks(target);
  if(!Files.isRegularFile(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Installed file is no longer available");
  Installed receipt=installed(game);for(File f:receipt.files)if(f==null||f.kind==null||f.filename==null)throw new IOException("Invalid content receipt");
  receipt.files.removeIf(f->f.kind==item.kind&&f.filename.equals(item.filename));
  Path removed=state(game,"content-uninstall").resolve(UUID.randomUUID().toString());ProsperoDownloads.noLinks(removed);Files.createDirectories(removed);
  Path staged=removed.resolve("removed-file");Files.move(target,staged);
  try{ProsperoInstall.save(state(game,"content-installed.json"),new Gson().toJson(receipt));}
  catch(Exception failure){try{Files.move(staged,target);Files.deleteIfExists(removed);}catch(Exception rollback){failure.addSuppressed(rollback);}throw failure;}
  try{Files.delete(staged);Files.delete(removed);return true;}catch(IOException cleanup){return false;}
 }
 String icon(Path game,String project,String url,BooleanSupplier cancel){
  if(project.isEmpty())return "";
  try{id(project);Path path=state(game,"content-icons32").resolve(project+".txt");ProsperoDownloads.noLinks(path);
   if(Files.isRegularFile(path)&&Files.size(path)==6144){String saved=Files.readString(path);if(saved.matches("[a-f0-9]{6144}"))return saved;}
   if(url.isEmpty())url=ProsperoDownloads.text(download.json(API+"project/"+project,cancel).getAsJsonObject(),"icon_url");
   if(url.isEmpty())return "";ProsperoDownloads.safe(url);if(!java.net.URI.create(url).getHost().equals("cdn.modrinth.com"))return "";
   String pixels=ProsperoContentImages.decode(download.bytes(url,1024*1024,cancel));ProsperoInstall.save(path,pixels);return pixels;
  }catch(Exception unavailable){return "";}
 }
 static Path state(Path game,String file)throws IOException {Path p=game.getParent().resolve(file);ProsperoDownloads.noLinks(p);return p;}
 List<Selection> queue(Path game)throws Exception {
  Path path=state(game,"content-queue.json");if(!Files.exists(path))return List.of();if(Files.size(path)>256*1024)throw new IOException("Content queue is too large");
  var result=new ArrayList<Selection>();for(var item:JsonParser.parseString(Files.readString(path)).getAsJsonArray()){
   Selection s=new Gson().fromJson(item,Selection.class);if(s==null||s.kind==null||s.title==null)throw new IOException("Invalid content queue");id(s.project);result.add(s);if(result.size()>128)throw new IOException("Content queue is full");
  }return List.copyOf(result);
 }
 synchronized void toggle(Path game,Selection selection)throws Exception {
  id(selection.project);var list=new ArrayList<>(queue(game));boolean removed=list.removeIf(s->s.project.equals(selection.project)&&s.kind==selection.kind);
  if(!removed){if(list.size()>=128)throw new IOException("Download queue is full");list.add(selection);}ProsperoInstall.save(state(game,"content-queue.json"),new Gson().toJson(list));
 }
 JsonObject version(String project,String pinned,Kind kind,String game,BooleanSupplier cancel)throws Exception {
  id(project);JsonObject version;
  if(!pinned.isEmpty()){id(pinned);version=download.json(API+"version/"+pinned,cancel).getAsJsonObject();}
  else{
   String filter=kind==Kind.MOD?"&loaders="+ProsperoDownloads.encode(array("fabric")):"";
   var versions=download.json(API+"project/"+project+"/version?game_versions="+ProsperoDownloads.encode(array(game))+filter+"&include_changelog=false",cancel).getAsJsonArray();
   if(versions.isEmpty())throw new IOException("No compatible download for "+project+" on "+game);
   version=versions.get(0).getAsJsonObject();
  }
  if(!project.equals(ProsperoDownloads.text(version,"project_id"))||!ProsperoDownloads.contains(version,"game_versions",game)||(kind==Kind.MOD&&!ProsperoDownloads.contains(version,"loaders","fabric")))throw new IOException("Content version is incompatible with this instance");
  if("unsupported".equals(ProsperoDownloads.text(version,"client_side"))||ProsperoDownloads.text(version,"environment").matches("server_only|dedicated_server_only|server_only_client_optional"))throw new IOException("This download is server-only");
  return version;
 }
 File file(JsonObject version,Kind kind)throws Exception {
  JsonObject selected=null;for(var item:version.getAsJsonArray("files")){var f=item.getAsJsonObject();if(selected==null)selected=f;if(f.has("primary")&&f.get("primary").getAsBoolean()){selected=f;break;}}
  if(selected==null)throw new IOException("Content has no downloadable file");String name=selected.get("filename").getAsString();
  if(!validFilename(name,kind))throw new IOException("Unsupported content filename");
  String project=version.get("project_id").getAsString(),id=version.get("id").getAsString();id(project);id(id);
  JsonObject hashes=selected.getAsJsonObject("hashes");String algorithm=hashes.has("sha512")?"SHA-512":"SHA-1",hash=hashes.get(algorithm.equals("SHA-512")?"sha512":"sha1").getAsString();
  return new File(project,id,kind,name,new ProsperoDownloads.Pin(selected.get("url").getAsString(),algorithm,hash,selected.get("size").getAsLong()));
 }
 private void resolve(Selection s,String pinned,String game,LinkedHashMap<String,File> plan,Set<String> active,List<JsonObject> versions,BooleanSupplier cancel,Map<String,String> constraints,Map<String,String> required)throws Exception {
  String key=s.kind+":"+s.project;
  if(!pinned.isEmpty()){String other=required.putIfAbsent(s.project,pinned);if(other!=null&&!other.equals(pinned))throw new IOException("Required mod versions conflict for "+s.project+": "+other+" and "+pinned);}
  File prior=plan.get(key);if(prior!=null)return;
  if(pinned.isEmpty())pinned=constraints.getOrDefault(s.project,"");
  if(plan.size()+active.size()>=128)throw new IOException("Too many required dependencies");if(!active.add(key))throw new IOException("Dependency cycle in Modrinth metadata");
  var v=version(s.project,pinned,s.kind,game,cancel);File f=file(v,s.kind);versions.add(v);
  if(v.has("dependencies"))for(var element:v.getAsJsonArray("dependencies")){
   var dep=element.getAsJsonObject();if(!"required".equals(ProsperoDownloads.text(dep,"dependency_type")))continue;
   String project=ProsperoDownloads.text(dep,"project_id"),id=ProsperoDownloads.text(dep,"version_id");
   if(project.isEmpty()&&!id.isEmpty()){ProsperoModrinth.id(id);project=download.json(API+"version/"+id,cancel).getAsJsonObject().get("project_id").getAsString();}
   if(project.isEmpty())throw new IOException("A required dependency needs manual installation");
   // Modrinth libraries required by Fabric mods are mods, never desktop natives.
   if(s.kind!=Kind.MOD)throw new IOException("This pack has required dependencies; install them separately first");
   resolve(new Selection(project,project,Kind.MOD),id,game,plan,active,versions,cancel,constraints,required);
  }
  active.remove(key);plan.put(key,f);
 }
 private void resolveAll(List<Selection> selected,Map<String,String> pins,String game,LinkedHashMap<String,File> plan,List<JsonObject> versions,BooleanSupplier cancel)throws Exception {
  Map<String,String> constraints=new HashMap<>(pins);Set<Map<String,String>> seen=new HashSet<>();
  for(int pass=0;pass<128;pass++){
   ProsperoInstall.active(cancel);
   if(!seen.add(Map.copyOf(constraints)))throw new IOException("Required mod versions do not converge; change the conflicting selection");
   plan.clear();versions.clear();Map<String,String> required=new HashMap<>();
   for(var s:selected)resolve(s,"",game,plan,new HashSet<>(),versions,cancel,constraints,required);
   boolean matches=true;for(var entry:required.entrySet()){
    File f=plan.get("MOD:"+entry.getKey());if(f==null||!f.version.equals(entry.getValue())){matches=false;break;}
   }
   if(matches)return;
   constraints=new HashMap<>(pins);constraints.putAll(required);
  }
  throw new IOException("Too many dependency version resolution passes");
 }
 Installed installed(Path game)throws Exception {
  Path path=state(game,"content-installed.json");if(!Files.exists(path))return new Installed();if(Files.size(path)>1024*1024)throw new IOException("Content receipt too large");
  Installed r=new Gson().fromJson(Files.readString(path),Installed.class);if(r==null||r.files==null||r.files.size()>1024)throw new IOException("Invalid content receipt");
  Set<String> entries=new HashSet<>();for(File f:r.files){
   if(f==null||f.kind==null||f.pin==null||!validFilename(f.filename,f.kind))throw new IOException("Invalid content receipt filename");
   id(f.project);id(f.version);if(!entries.add(f.kind+":"+f.project))throw new IOException("Duplicate content receipt project");
   if(!Set.of("SHA-512","SHA-1").contains(f.pin.algorithm())||f.pin.hash()==null||!f.pin.hash().matches(f.pin.algorithm().equals("SHA-512")?"[a-f0-9]{128}":"[a-f0-9]{40}"))throw new IOException("Invalid content receipt hash");
  }return r;
 }
 private List<Path> modPaths(Path game,Map<String,File> plan,Path stage,Set<Path> replaced)throws Exception {
  Map<String,Path> paths=new LinkedHashMap<>();for(Local local:local(game,Kind.MOD)){Path path=game.resolve("mods").resolve(local.filename);if(!replaced.contains(path))paths.put(local.filename,path);}
  for(File f:plan.values())if(f.kind==Kind.MOD)paths.put(f.filename,stage.resolve(f.pin.hash()+".bin"));return List.copyOf(paths.values());
 }
 private Map<Path,File> replacements(Path game,Installed receipt,Map<String,File> plan,Path stage,ProsperoDependencies.Versions checker)throws Exception {
  Map<Path,File> replaced=new LinkedHashMap<>();
  for(File next:plan.values())for(File old:receipt.files)if(old.kind==next.kind&&old.project.equals(next.project)&&!old.version.equals(next.version)){
   Path path=game.resolve(old.kind.folder).resolve(old.filename);ProsperoDownloads.noLinks(path);
   if(!Files.exists(path))continue;
   if(next.kind!=Kind.MOD||checker==null)throw new IOException("Another version is already installed. Keep it or remove it before adding a new version.");
   if(!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||!ProsperoDownloads.hash(path,old.pin.algorithm()).equals(old.pin.hash()))throw new IOException("Installed mod was modified: "+old.filename+". Keep it or uninstall it before updating.");
   var before=ProsperoDependencies.rootModule(path);var after=ProsperoDependencies.rootModule(stage.resolve(next.pin.hash()+".bin"));
   if(!before.id().equals(after.id())||checker.compare(after.version(),before.version())<=0)throw new IOException("Required mod version would not upgrade "+old.filename+". Automatic downgrades are not allowed.");
   if(replaced.put(path,next)!=null)throw new IOException("Duplicate installed mod update target");
  }
  return replaced;
 }
 private void publish(Path game,Installed receipt,Map<String,File> plan,Path stage,Map<Path,File> replaced,BooleanSupplier cancel)throws Exception {
  Path backup=state(game,"content-updates").resolve(UUID.randomUUID().toString());ProsperoDownloads.noLinks(backup);Files.createDirectories(backup);
  Map<Path,Path> moved=new LinkedHashMap<>();List<Path> created=new ArrayList<>();
  try{
   for(Path old:replaced.keySet()){ProsperoInstall.active(cancel);Path saved=backup.resolve(Integer.toString(moved.size()));Files.move(old,saved);moved.put(old,saved);}
   for(File f:plan.values()){
    ProsperoInstall.active(cancel);Path target=game.resolve(f.kind.folder).resolve(f.filename);ProsperoDownloads.noLinks(target);Files.createDirectories(target.getParent());
    if(!Files.exists(target)){Path part=target.resolveSibling(f.filename+".part");ProsperoDownloads.noLinks(part);try{Files.copy(stage.resolve(f.pin.hash()+".bin"),part,StandardCopyOption.REPLACE_EXISTING);ProsperoInstall.active(cancel);Files.move(part,target);created.add(target);}finally{Files.deleteIfExists(part);}}
   }
   Installed next=new Installed();next.files.addAll(receipt.files);
   for(File f:plan.values()){next.files.removeIf(old->old.project.equals(f.project)&&old.kind==f.kind);next.files.add(f);}
   ProsperoInstall.active(cancel);ProsperoInstall.save(state(game,"content-installed.json"),new Gson().toJson(next));
  }catch(Exception failure){
   for(int i=created.size()-1;i>=0;i--)try{Files.delete(created.get(i));}catch(Exception rollback){failure.addSuppressed(rollback);}
   for(var entry:moved.entrySet())try{Files.move(entry.getValue(),entry.getKey());}catch(Exception rollback){failure.addSuppressed(rollback);}
   try{Files.delete(backup);}catch(Exception cleanup){failure.addSuppressed(cleanup);}throw failure;
  }
  // A cleanup failure leaves private backups outside mods; the committed instance stays valid.
  try{for(Path saved:moved.values())Files.delete(saved);Files.delete(backup);}catch(IOException cleanup){System.err.println("PS5_CONTENT update backup cleanup pending");}
 }
 void repair(Path game,String version,String loader,ProsperoDependencies.Versions checker,ProsperoInstall.Progress progress,BooleanSupplier cancel,boolean offline)throws Exception {
  var paths=new ArrayList<Path>();for(var local:local(game,Kind.MOD))paths.add(game.resolve("mods").resolve(local.filename));
  if(ProsperoDependencies.requiredUpdates(paths,version,checker).isEmpty())return;
  if(offline)throw new IOException("Required mod dependencies are missing. Connect online to repair this instance.");
  var roots=new ArrayList<Selection>();var pins=new HashMap<String,String>();
  for(File f:installed(game).files)if(f.kind==Kind.MOD&&Files.isRegularFile(game.resolve("mods").resolve(f.filename))){roots.add(new Selection(f.project,f.filename,Kind.MOD));pins.put(f.project,f.version);}
  installSelected(game,version,loader,progress,cancel,f->{},checker,roots,pins,false);
 }
 void downloadAll(Path game,String gameVersion,String loader,ProsperoInstall.Progress progress,BooleanSupplier cancel)throws Exception {downloadAll(game,gameVersion,loader,progress,cancel,f->{});}
 void downloadAll(Path game,String gameVersion,String loader,ProsperoInstall.Progress progress,BooleanSupplier cancel,java.util.function.Consumer<File> current)throws Exception {downloadQueued(game,gameVersion,loader,progress,cancel,current,null);}
 void downloadAll(Path game,String gameVersion,String loader,ProsperoInstall.Progress progress,BooleanSupplier cancel,java.util.function.Consumer<File> current,ProsperoDependencies.Versions versions)throws Exception {downloadQueued(game,gameVersion,loader,progress,cancel,current,versions);}
 record DownloadFailure(String project,String title,Kind kind,String error){}
 static final class ContentDownloadFailure extends IOException {
  final String key;ContentDownloadFailure(File file,IOException cause){super(file.filename+": "+cause.getMessage(),cause);key=file.kind+":"+file.project;}
 }
 private void downloadQueued(Path game,String gameVersion,String loader,ProsperoInstall.Progress progress,BooleanSupplier cancel,java.util.function.Consumer<File> current,ProsperoDependencies.Versions checker)throws Exception {
  var selected=queue(game);if(selected.isEmpty())throw new IOException("Select something for the queue first");
  List<List<Selection>> groups=new ArrayList<>();List<Set<String>> keys=new ArrayList<>();Map<Selection,Set<String>> requiredByRoot=new HashMap<>();
  for(Selection root:selected){
   ProsperoInstall.active(cancel);var plan=new LinkedHashMap<String,File>();Set<String> linked=new HashSet<>();linked.add(root.kind+":"+root.project);
   try{resolveAll(List.of(root),Map.of(),gameVersion,plan,new ArrayList<>(),cancel);}catch(Exception unavailable){ProsperoInstall.active(cancel);}
   linked.addAll(plan.keySet());requiredByRoot.put(root,Set.copyOf(linked));List<Selection> group=new ArrayList<>();group.add(root);
   for(int i=groups.size()-1;i>=0;i--)if(!Collections.disjoint(linked,keys.get(i))){group.addAll(groups.remove(i));linked.addAll(keys.remove(i));}
   groups.add(group);keys.add(linked);
  }
  List<DownloadFailure> failures=new ArrayList<>();int complete=0;
  for(var original:groups){
   var group=new ArrayList<>(original);
   while(!group.isEmpty()){
    ProsperoInstall.active(cancel);
    try{installSelected(game,gameVersion,loader,progress,cancel,current,checker,group,Map.of(),false);}
    catch(Exception failure){
     ProsperoInstall.active(cancel);String error=failure.getMessage();if(error==null)error="Download could not finish";
     var blocked=new ArrayList<Selection>();
     if(failure instanceof ContentDownloadFailure unavailable)for(var root:group)if(requiredByRoot.get(root).contains(unavailable.key))blocked.add(root);
     if(blocked.isEmpty())blocked.addAll(group);
     for(var root:blocked)failures.add(new DownloadFailure(root.project,root.title,root.kind,error));
     group.removeAll(blocked);continue;
    }
    var remaining=new ArrayList<>(queue(game));remaining.removeIf(s->group.stream().anyMatch(root->root.project.equals(s.project)&&root.kind==s.kind));
    ProsperoInstall.save(state(game,"content-queue.json"),new Gson().toJson(remaining));complete+=group.size();break;
   }
  }
  ProsperoInstall.save(state(game,"content-download-errors.json"),new Gson().toJson(failures));
  if(!failures.isEmpty()){
   StringBuilder message=new StringBuilder("Downloaded "+complete+" queued items; "+failures.size()+" failed and remain queued. ");
   for(var failure:failures){String detail=failure.title+": "+failure.error;if(message.length()+detail.length()>450)break;message.append(detail).append(" ");}
   throw new IOException(message.toString());
  }
 }
 private void installSelected(Path game,String gameVersion,String loader,ProsperoInstall.Progress progress,BooleanSupplier cancel,java.util.function.Consumer<File> current,ProsperoDependencies.Versions checker,List<Selection> selected,Map<String,String> pins,boolean clearQueue)throws Exception {
  if(clearQueue&&selected.isEmpty())throw new IOException("Select something for the queue first");
  if(!loader.equals("fabric")&&selected.stream().anyMatch(s->s.kind==Kind.MOD))throw new IOException("Mods require a Fabric instance");
  LinkedHashMap<String,File> plan=new LinkedHashMap<>();ArrayList<JsonObject> versions=new ArrayList<>();
  var roots=new ArrayList<>(selected);var rootPins=new HashMap<>(pins);
  progress.update("Resolving selected content and required versions",0,1);resolveAll(roots,rootPins,gameVersion,plan,versions,cancel);
  Installed receipt=installed(game);
  Path stage=game.getParent().resolve("content-downloads");long total=0,done=0;Map<Path,File> replaced=Map.of();
  for(int pass=0;pass<16;pass++){
   total=plan.values().stream().mapToLong(f->f.pin.size()).sum();done=0;
   for(File f:plan.values()){ProsperoInstall.active(cancel);current.accept(f);progress.update("Downloading "+f.filename,done,total);try{download.obtain(f.pin,stage.resolve(f.pin.hash()+".bin"),cancel);}catch(IOException failure){ProsperoInstall.active(cancel);throw new ContentDownloadFailure(f,failure);}done+=f.pin.size();progress.update("Downloading "+f.filename,done,total);}
   replaced=replacements(game,receipt,plan,stage,checker);
   if(!loader.equals("fabric"))break;
   var needs=ProsperoDependencies.requiredUpdates(modPaths(game,plan,stage,replaced.keySet()),gameVersion,checker);
   if(needs.isEmpty())break;
   if(pass<15){
    Set<String> projects=new LinkedHashSet<>();
    if(needs.stream().anyMatch(n->n.id().equals("fabric")||n.id().startsWith("fabric-")))projects.add("P7dR8mSH");
    for(File old:receipt.files)if(old.kind==Kind.MOD){Path path=game.resolve("mods").resolve(old.filename);if(!Files.isRegularFile(path))continue;
     var ids=ProsperoDependencies.providedIds(path);if(needs.stream().anyMatch(n->ids.contains(n.id())))projects.add(old.project);
    }
    boolean changed=false;
    for(String project:projects){
     File prior=plan.get("MOD:"+project);String latest=version(project,"",Kind.MOD,gameVersion,cancel).get("id").getAsString();
     if(prior!=null&&prior.version.equals(latest))continue;
     progress.update("Updating required dependency "+project,0,1);
     if(roots.stream().noneMatch(s->s.project.equals(project)))roots.add(new Selection(project,project,Kind.MOD));rootPins.put(project,latest);changed=true;
    }
    if(changed){var priorPlan=new LinkedHashMap<>(plan);resolveAll(roots,rootPins,gameVersion,plan,versions,cancel);if(!priorPlan.equals(plan))continue;}
   }
   var n=needs.getFirst();throw new IOException(n.owner()+" needs "+n.id()+" "+n.versions()+". No compatible automatic dependency was found; files are kept.");
  }
  for(var v:versions)if(v.has("dependencies"))for(var item:v.getAsJsonArray("dependencies")){
   var d=item.getAsJsonObject();if(!"incompatible".equals(ProsperoDownloads.text(d,"dependency_type")))continue;
   String project=ProsperoDownloads.text(d,"project_id"),id=ProsperoDownloads.text(d,"version_id");
   if(plan.values().stream().anyMatch(f->f.project.equals(project)||( !id.isEmpty()&&f.version.equals(id)))||receipt.files.stream().filter(f->!plan.containsKey(f.kind+":"+f.project)).anyMatch(f->f.project.equals(project)||(!id.isEmpty()&&f.version.equals(id))))throw new IOException("Selected content conflicts with another installed or queued mod");
  }
  Set<Path> targets=new HashSet<>();for(File f:plan.values()){
   Path target=game.resolve(f.kind.folder).resolve(f.filename);ProsperoDownloads.noLinks(target);if(!targets.add(target))throw new IOException("Two downloads use the same filename");
   if(replaced.containsKey(target)&&!replaced.get(target).project.equals(f.project))throw new IOException("An updated mod uses another project's filename");
   if(Files.exists(target)&&!replaced.containsKey(target)&&!ProsperoDownloads.hash(target,f.pin.algorithm()).equals(f.pin.hash()))throw new IOException("Existing content uses "+f.filename+". Keep or remove it before downloading.");
  }
  publish(game,receipt,plan,stage,replaced,cancel);
  ProsperoInstall.active(cancel);if(clearQueue)ProsperoInstall.save(state(game,"content-queue.json"),"[]");
  for(File f:plan.values())Files.deleteIfExists(stage.resolve(f.pin.hash()+".bin"));progress.update("Downloads complete",total,total);
 }
}
