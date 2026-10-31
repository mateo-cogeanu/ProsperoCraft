import com.google.gson.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;

/** Persistent instance metadata; display names are never used as directory names. */
public final class ProsperoLibrary {
 static final String[] ICONS={"ProsperoCraft", "Grass", "Nether star", "Ender pearl", "Redstone flame", "Planks", "Gold", "Snow / stone", "Bee", "Bee Legacy", "Brick", "Chicken", "Creeper", "Diamond", "Dirt", "Enderman", "Fabricmc", "Fox", "Fox Legacy", "Ftb Logo", "Gear", "Herobrine", "Iron", "Magitech", "Meat", "Modrinth", "Neoforged", "Quiltmc", "Skeleton", "Squarecreeper", "Steve", "Tnt"};
 static final int GAME_WIDTH=1920,GAME_HEIGHT=1080,LOCKED_RESOLUTION=2;
 static final int[][] RESOLUTIONS={{1280,720},{1600,900},{1920,1080},{2560,1440},{3840,2160}};
 static String resolutionLabel(int i){return RESOLUTIONS[i][0]+" x "+RESOLUTIONS[i][1];}
 static final class Instance {String id=UUID.randomUUID().toString(),name,version,loader="vanilla";int icon;boolean ready,defaultContentPending;Instance(String n,String v,int i){name=clean(n);version=v;icon=i;}}
 static final class Favorite {String instance,kind,target,name;Favorite(String i,ProsperoDestinations.Entry e){instance=i;kind=e.kind();target=e.target();name=e.name();}}
 static final class Settings {int[] controllerKeys=ProsperoInput.DEFAULT.clone();int resolution=LOCKED_RESOLUTION,workers=4,theme=0,background=5,backgroundDefaultsRevision=0;boolean vibration=true,reducedMotion=false,snapshots=false,showIntro=true,showControls=true;}
 static final class State {int schema=1;ArrayList<Instance> instances=new ArrayList<>();Settings settings=new Settings();ArrayList<Favorite> favorites=new ArrayList<>();}
 final Path root;private State state;
 ProsperoLibrary(Path root)throws Exception {
  this.root=root;Files.createDirectories(root);Path file=root.resolve("library.json");
  if(Files.isRegularFile(file)){
   try{if(Files.size(file)>1024*1024)throw new IOException();state=new Gson().fromJson(Files.readString(file),State.class);validate();}
   catch(Exception bad){throw new IOException("Library data could not be read. Your instance folders are preserved.");}
  }else state=new State();
  recoverInterruptedMoves();recoverPermanentDeletes();recoverCopies();
  // Apply the requested Waves default once, including existing libraries.
  if(state.settings.backgroundDefaultsRevision<1){state.settings.background=5;state.settings.backgroundDefaultsRevision=1;save();}

 }
 static String clean(String name){String value=name==null?"":name.strip();if(value.isEmpty()||value.length()>40||!value.matches("[A-Za-z0-9 ._()!+-]+"))throw new IllegalArgumentException("Use1-40 letters, numbers, spaces or ._()!+-");return value;}
 private void validate()throws Exception {
  if(state==null||state.schema!=1||state.instances==null||state.settings==null||state.instances.size()>256)throw new IOException();if(state.favorites==null)state.favorites=new ArrayList<>();if(state.favorites.size()>1024)throw new IOException();
  for(var f:state.favorites)if(f==null||f.instance==null||!f.instance.matches("[a-f0-9-]{36}")||!ProsperoDestinations.valid(f.kind==null?"":f.kind,f.target)||f.name==null||f.name.length()>80)throw new IOException();
  Set<String> ids=new HashSet<>();
  for(var i:state.instances){if(i==null||!i.id.matches("[a-f0-9-]{36}")||!ids.add(i.id)||!i.version.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}")||i.icon<0||i.icon>=ICONS.length)throw new IOException();clean(i.name);if(i.loader==null)i.loader="vanilla";if(!Set.of("vanilla","fabric").contains(i.loader))throw new IOException();}
  if(state.settings.controllerKeys==null)state.settings.controllerKeys=ProsperoInput.DEFAULT.clone();ProsperoInput.validate(state.settings.controllerKeys);
  if(state.settings.theme<0||state.settings.theme>5)state.settings.theme=0;
  if(state.settings.background<1||state.settings.background>10)state.settings.background=5;
  if(state.settings.resolution<0||state.settings.resolution>=RESOLUTIONS.length||state.settings.workers<1||state.settings.workers>6)throw new IOException();
 }
 synchronized List<Instance> instances(){return List.copyOf(state.instances);}
 synchronized Settings settings(){return state.settings;}
 synchronized Instance add(String name,String version,int icon)throws Exception {return add(name,version,icon,"vanilla");}
 synchronized Instance add(String name,String version,int icon,String loader)throws Exception {
  if(!Set.of("vanilla","fabric").contains(loader))throw new IOException("This loader is coming soon");
  if(state.instances.size()>=256)throw new IOException("This library is full");if(!version.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}")||icon<0||icon>=ICONS.length)throw new IOException("Invalid instance choice");
  Instance instance=new Instance(name,version,icon);instance.loader=loader;instance.defaultContentPending=Set.of("fabric","neoforge").contains(loader);Files.createDirectories(game(instance));state.instances.add(instance);try{save();}catch(Exception error){state.instances.remove(instance);throw error;}return instance;
 }
 Path game(Instance i){return root.resolve("instances").resolve(i.id).resolve("game");}
 synchronized List<Favorite> favorites(){return state.favorites.stream().filter(f->state.instances.stream().anyMatch(i->i.id.equals(f.instance))).toList();}
 synchronized boolean favorite(Instance i,ProsperoDestinations.Entry e){return state.favorites.stream().anyMatch(f->f.instance.equals(i.id)&&f.kind.equals(e.kind())&&f.target.equals(e.target()));}
 synchronized void toggleFavorite(Instance i,ProsperoDestinations.Entry e)throws Exception {
  var before=new ArrayList<>(state.favorites);if(!state.instances.contains(i)||!ProsperoDestinations.valid(e.kind(),e.target()))throw new IOException("Invalid favorite");
  if(favorite(i,e))state.favorites.removeIf(f->f.instance.equals(i.id)&&f.kind.equals(e.kind())&&f.target.equals(e.target()));else{if(state.favorites.size()>=1024)throw new IOException("Home is full");state.favorites.add(new Favorite(i.id,e));}
  try{save();}catch(Exception failure){state.favorites=before;throw failure;}
 }
 private static void noLink(Path path)throws IOException{if(Files.isSymbolicLink(path))throw new IOException("Instance storage contains an unexpected link");}
 private Path trash(){return root.resolve("trash/instances");} // Legacy interrupted-move migration only.
 private static void purge(Path folder)throws IOException {
  if(!Files.exists(folder,LinkOption.NOFOLLOW_LINKS))return;
  Files.walkFileTree(folder,new SimpleFileVisitor<Path>(){
   public FileVisitResult visitFile(Path file,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{Files.delete(file);return FileVisitResult.CONTINUE;}
   public FileVisitResult postVisitDirectory(Path dir,IOException error)throws IOException{if(error!=null)throw error;Files.delete(dir);return FileVisitResult.CONTINUE;}
  });
 }
 // A private journal permits rollback before metadata commit and finishes a
 // committed permanent deletion after interruption. It is never user undo.
 synchronized boolean delete(Instance instance)throws Exception {
  int at=state.instances.indexOf(instance);if(at<0)throw new IOException("Instance is no longer in this library");
  Path base=root.resolve("pending-delete");noLink(root.resolve("instances"));noLink(base);Path source=game(instance).getParent();noLink(source);
  Path journal=base.resolve(UUID.randomUUID().toString());Files.createDirectories(journal);Files.writeString(journal.resolve("id"),instance.id);
  boolean moved=Files.exists(source,LinkOption.NOFOLLOW_LINKS);if(moved)Files.move(source,journal.resolve("files"));
  var favorites=new ArrayList<>(state.favorites);state.instances.remove(at);state.favorites.removeIf(f->f.instance.equals(instance.id));
  try{save();}catch(Exception failure){state.instances.add(at,instance);state.favorites=favorites;if(moved)try{Files.move(journal.resolve("files"),source);}catch(Exception rollback){failure.addSuppressed(rollback);}throw failure;}
  try{purge(journal);return true;}catch(IOException cleanup){return false;}
 }
 private void recoverPermanentDeletes()throws Exception {
  Path base=root.resolve("pending-delete");noLink(base);if(!Files.isDirectory(base))return;
  try(var dirs=Files.list(base)){for(Path journal:dirs.toList()){
   noLink(journal);Path idFile=journal.resolve("id");noLink(idFile);if(!Files.isRegularFile(idFile)||Files.size(idFile)>40)throw new IOException("Invalid deletion journal");String id=Files.readString(idFile);if(!id.matches("[a-f0-9-]{36}"))throw new IOException("Invalid deletion journal");
   Path files=journal.resolve("files");noLink(files);var live=state.instances.stream().filter(i->i.id.equals(id)).findFirst();
   if(live.isPresent()&&Files.isDirectory(files)){Path target=game(live.get()).getParent();noLink(root.resolve("instances"));noLink(target);if(Files.exists(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Deletion recovery has conflicting folders");Files.createDirectories(target.getParent());Files.move(files,target);}
   purge(journal);
  }}
 }
 // Complete neither half of a crashed move: roll it back to the persisted library.
 private void recoverInterruptedMoves()throws Exception {
  noLink(root.resolve("instances"));noLink(trash().getParent());noLink(trash());if(!Files.isDirectory(trash()))return;
  try(var entries=Files.list(trash())){for(Path folder:entries.toList()){
   if(Files.isSymbolicLink(folder)||!Files.isRegularFile(folder.resolve("deleted")))continue;
   noLink(folder.resolve("instance.json"));if(Files.size(folder.resolve("instance.json"))>8192)throw new IOException("Invalid deleted instance metadata");
   Instance instance=new Gson().fromJson(Files.readString(folder.resolve("instance.json")),Instance.class);
   if(instance==null||instance.id==null||!instance.id.matches("[a-f0-9-]{36}"))throw new IOException("Invalid deleted instance metadata");
   Path files=folder.resolve("files"),live=game(instance).getParent();noLink(files);noLink(live);
   boolean listed=state.instances.stream().anyMatch(i->i.id.equals(instance.id));
   if(listed&&Files.isDirectory(files)){
    if(Files.exists(live,LinkOption.NOFOLLOW_LINKS))throw new IOException("Interrupted deletion has conflicting folders. Both copies are kept.");
    Files.createDirectories(live.getParent());Files.move(files,live);Files.delete(folder.resolve("deleted"));
   }else if(listed&&!Files.exists(files,LinkOption.NOFOLLOW_LINKS))Files.delete(folder.resolve("deleted"));
   else if(!listed&&!Files.exists(files,LinkOption.NOFOLLOW_LINKS)&&Files.isDirectory(live))Files.move(live,files);
  }}
 }
 private void recoverCopies()throws Exception {
  Path base=root.resolve("pending-copy");noLink(base);noLink(root.resolve("instances"));if(!Files.isDirectory(base))return;
  try(var journals=Files.list(base)){for(Path journal:journals.toList()){
   noLink(journal);String id=journal.getFileName().toString();if(!id.matches("[a-f0-9-]{36}"))throw new IOException("Invalid duplicate journal");
   Path marker=journal.resolve("id");noLink(marker);if(!Files.exists(marker,LinkOption.NOFOLLOW_LINKS)){purge(journal);continue;}
   if(!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)||Files.size(marker)>40||!Files.readString(marker).equals(id))throw new IOException("Invalid duplicate journal marker");
   Path target=root.resolve("instances").resolve(id);noLink(target);
   if(state.instances.stream().noneMatch(instance->instance.id.equals(id)))purge(target);
   else if(!Files.exists(target,LinkOption.NOFOLLOW_LINKS)){
    Path staged=journal.resolve("files");noLink(staged);if(!Files.isDirectory(staged,LinkOption.NOFOLLOW_LINKS))throw new IOException("Duplicated instance folder is missing; recovery files are preserved");Files.move(staged,target);
   }
   purge(journal);
  }}
 }
 Instance duplicate(Instance original,ProsperoInstall.Progress progress,java.util.function.BooleanSupplier cancel)throws Exception {
  final Instance copy;final Path source;
  synchronized(this){
   if(!state.instances.contains(original))throw new IOException("Instance is no longer in this library");
   if(state.instances.size()>=256)throw new IOException("This library is full");
   String name;int n=1;var names=state.instances.stream().map(instance->instance.name).toList();
   do{String suffix=n==1?" Copy":" Copy "+n;name=original.name.substring(0,Math.min(original.name.length(),40-suffix.length())).stripTrailing()+suffix;n++;}while(names.contains(name));
   copy=new Instance(name,original.version,original.icon);copy.loader=original.loader;copy.ready=original.ready;copy.defaultContentPending=original.defaultContentPending;
   source=game(original).getParent();
  }
  noLink(root.resolve("instances"));noLink(source);Path base=root.resolve("pending-copy");noLink(base);Files.createDirectories(base);
  Path journal=base.resolve(copy.id),staged=journal.resolve("files"),target=game(copy).getParent();noLink(target);
  if(Files.exists(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Duplicate destination already exists");
  Files.createDirectory(journal);long[] size={0},done={0};boolean[] moved={false},committed={false};
  try{
   Files.writeString(journal.resolve("id"),copy.id,StandardOpenOption.CREATE_NEW);
   Files.walkFileTree(source,new SimpleFileVisitor<Path>(){
    public FileVisitResult preVisitDirectory(Path dir,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{ProsperoInstall.active(cancel);return FileVisitResult.CONTINUE;}
    public FileVisitResult visitFile(Path file,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{ProsperoInstall.active(cancel);if(!attrs.isRegularFile()||attrs.isSymbolicLink())throw new IOException("Cannot duplicate linked or special files");size[0]=Math.addExact(size[0],attrs.size());return FileVisitResult.CONTINUE;}
   });
   Files.walkFileTree(source,new SimpleFileVisitor<Path>(){
    public FileVisitResult preVisitDirectory(Path dir,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{ProsperoInstall.active(cancel);Files.createDirectory(staged.resolve(source.relativize(dir)));return FileVisitResult.CONTINUE;}
    public FileVisitResult visitFile(Path file,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{
     ProsperoInstall.active(cancel);if(!attrs.isRegularFile()||attrs.isSymbolicLink())throw new IOException("Cannot duplicate linked or special files");Path destination=staged.resolve(source.relativize(file));
     try(var in=Files.newInputStream(file,LinkOption.NOFOLLOW_LINKS);var out=Files.newOutputStream(destination,StandardOpenOption.CREATE_NEW)){
      byte[] buffer=new byte[65536];for(int count;(count=in.read(buffer))!=-1;){ProsperoInstall.active(cancel);out.write(buffer,0,count);done[0]+=count;progress.update("Duplicating "+original.name,done[0],size[0]);}
     }return FileVisitResult.CONTINUE;
    }
   });
   ProsperoInstall.active(cancel);Files.move(staged,target);moved[0]=true;
   synchronized(this){
    ProsperoInstall.active(cancel);if(state.instances.size()>=256)throw new IOException("This library is full");state.instances.add(copy);
    try{save();committed[0]=true;}catch(Exception error){state.instances.remove(copy);throw error;}
   }
   try{purge(journal);}catch(IOException cleanup){System.err.println("PS5_INSTANCE duplicate journal cleanup pending");}
   return copy;
  }catch(Exception failure){
   if(!committed[0]){try{if(moved[0])purge(target);purge(journal);}catch(IOException cleanup){failure.addSuppressed(cleanup);}}
   throw failure;
  }
 }
 synchronized void rename(Instance i,String name)throws Exception{String before=i.name;i.name=clean(name);try{save();}catch(Exception error){i.name=before;throw error;}}
 synchronized void icon(Instance i,int icon)throws Exception{if(icon<0||icon>=ICONS.length)throw new IOException("Invalid icon");int before=i.icon;i.icon=icon;try{save();}catch(Exception error){i.icon=before;throw error;}}
 synchronized void defaultContentInstalled(Instance i)throws Exception{boolean before=i.defaultContentPending;i.defaultContentPending=false;try{save();}catch(Exception error){i.defaultContentPending=before;throw error;}}
 synchronized void ready(Instance i,boolean value)throws Exception{i.ready=value;save();}
 synchronized void save()throws Exception {
  validate();Path file=root.resolve("library.json");if(Files.isRegularFile(file))Files.copy(file,root.resolve("library.json.backup"),StandardCopyOption.REPLACE_EXISTING);ProsperoInstall.save(file,new GsonBuilder().setPrettyPrinting().create().toJson(state));
 }
}
