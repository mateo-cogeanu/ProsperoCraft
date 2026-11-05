/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.security.MessageDigest;
import java.util.*;

/** Shared storage selection and copy-before-switch migration. Never deletes legacy data. */
final class ProsperoStorageRoot {
 static final String POINTER=".shared-storage-v1",OWNER=".prospero-migration-owner",PART=".prospero-migration-part",READY=".prospero-shared-v1";
 static final int MAX_ENTRIES=262144;
 record Selection(Path root,String notice,Path legacy){
  Selection(Path root,String notice){this(root,notice,null);}
 }
 interface Probe {void check(Path root)throws IOException;}
 interface Progress {boolean update(String phase,long done,long total);}
 static final Progress SILENT=(phase,done,total)->true;
 static final class MigrationProgress {
  private static final class Paused extends IOException {}
  private final Progress display;
  private String phase="";
  private final byte[] buffer=new byte[65536];
  private long done,total,lastUpdate;
  MigrationProgress(Progress display){this.display=display;}
  void phase(String next,long units)throws IOException {
   phase=next;done=0;total=units;lastUpdate=System.nanoTime();
   publish();
  }
  void advance(long count)throws IOException {
   if(total==0)count=0;
   if(count>total-done)throw new IOException("Library grew during migration");
   done+=count;
   long now=System.nanoTime();
   if(now-lastUpdate>=200_000_000L){lastUpdate=now;publish();}
  }
  void finish()throws IOException {
   if(done!=total)throw new IOException("Library size changed during migration");
   publish();
  }
  private void publish()throws IOException {
   if(!display.update(phase,done,total))throw new Paused();
  }
 }
 interface Copier {void copy(Path source,Path destination)throws IOException;}
 record Stamp(long size,java.nio.file.attribute.FileTime modified,String digest){}
 static Selection current()throws IOException {return current(SILENT);}
 static Selection current(Progress progress)throws IOException {
  String explicit=System.getProperty("ps5.launcher.root");
  if(explicit!=null&&!explicit.isBlank())return new Selection(Path.of(explicit),"");
  if("/download0/ProsperoCraft".equals(System.getenv("PROSPERO_STORAGE_BASE")))return fallback(Path.of("/download0/ProsperoCraft"),"Shared storage access failed. Using the original download0 library; it may be older.");
  progress.update("Opening library catalog",0,0);
  return ProsperoMigration.open(Path.of("/download0/ProsperoCraft"),Path.of("/data/ProsperoCraft/library"));
 }
 static BasicFileAttributes attributes(Path path)throws IOException {
  try{return Files.readAttributes(path,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);}catch(NoSuchFileException absent){return null;}
 }
 static void noLinks(Path path)throws IOException {
  for(Path at=path.toAbsolutePath().normalize();at!=null;at=at.getParent()){var a=attributes(at);if(a!=null&&a.isSymbolicLink())throw new IOException("Linked storage is unavailable");}
 }
 static boolean directory(Path path)throws IOException {var a=attributes(path);if(a==null)return false;if(!a.isDirectory())throw new IOException("Storage directory is unavailable");return true;}
 static void privateMode(Path path,boolean directory){try{Files.setPosixFilePermissions(path,PosixFilePermissions.fromString(directory?"rwx------":"rw-------"));}catch(IOException|UnsupportedOperationException unavailable){}}
 static boolean nonempty(Path path)throws IOException {if(!directory(path))return false;try(var entries=Files.newDirectoryStream(path)){return entries.iterator().hasNext();}}
 static boolean marker(Path path,String expected)throws IOException {var a=attributes(path);return a!=null&&a.isRegularFile()&&a.size()<=8192&&Files.readString(path).equals(expected);}
 static void probe(Path root)throws IOException {
  noLinks(root);Path parent=directory(root)?root:root.getParent();if(!directory(parent))throw new IOException("Shared storage is not mounted");
  // Prove the metadata/list/rename operations used by Java, not only one open().
  try(var entries=Files.newDirectoryStream(parent)){entries.iterator().hasNext();}
  Path test=Files.createTempDirectory(parent,".prospero-storage-check-");privateMode(test,true);
  Path first=test.resolve("before"),second=test.resolve("after");
  try{
   Files.writeString(first,"ProsperoCraft storage check",StandardOpenOption.CREATE_NEW);privateMode(first,false);Files.move(first,second);
   if(!Files.readString(second).equals("ProsperoCraft storage check")||!attributes(second).isRegularFile())throw new IOException("Shared storage verification failed");
   try(var entries=Files.newDirectoryStream(test)){if(!entries.iterator().hasNext())throw new IOException("Shared storage listing failed");}
   test.toRealPath();
  }finally{Files.deleteIfExists(first);Files.deleteIfExists(second);Files.delete(test);}
 }
 static Selection fallback(Path legacy,String notice)throws IOException {
  noLinks(legacy);ProsperoLibrary.verifyReadable(legacy);return new Selection(legacy,notice);
 }
 static boolean freshShared(Path root)throws IOException {
  if(!marker(root.resolve(READY),"fresh-v1\n"))return false;
  try(var entries=Files.newDirectoryStream(root)){for(Path entry:entries)if(!Set.of(READY,OWNER).contains(entry.getFileName().toString()))return false;}return true;
 }
 static Selection select(Path legacy,Path preferred,Probe probe,Copier copier)throws IOException {
  return select(legacy,preferred,probe,copier,SILENT);
 }
 static Selection select(Path legacy,Path preferred,Probe probe,Copier copier,Progress display)throws IOException {
  display.update("Checking library storage",0,0);
  legacy=legacy.toAbsolutePath().normalize();preferred=preferred.toAbsolutePath().normalize();
  if(legacy.startsWith(preferred)||preferred.startsWith(legacy))throw new IOException("Storage locations overlap");
  try{probe.check(preferred);noLinks(preferred);}catch(IOException unavailable){return fallback(legacy,"Shared storage is unavailable. Using the original download0 library; it may be older.");}
  try{
   if(nonempty(preferred)){
    boolean known=marker(preferred.resolve(READY),"shared-v1\n")||marker(preferred.resolve(READY),"fresh-v1\n");
    if(!known&&nonempty(legacy))throw new IOException("Libraries exist in both locations; no automatic merge");
    if(!freshShared(preferred))ProsperoLibrary.verifyReadable(preferred);return new Selection(preferred,"");
   }
   if(nonempty(legacy)){
    ProsperoLibrary.verifyReadable(legacy);migrate(legacy,preferred,copier,new MigrationProgress(display));
    return new Selection(preferred,"Storage copied and verified in /data/ProsperoCraft. The original download0 library remains as a backup.");
   }
   Files.createDirectories(preferred);privateMode(preferred,true);Files.writeString(preferred.resolve(READY),"fresh-v1\n",StandardOpenOption.CREATE_NEW);
   return new Selection(preferred,"");
  }catch(MigrationProgress.Paused cancelled){
   return fallback(legacy,"Storage move paused. Using the original library for this session. Restart to resume.");
  }catch(IOException incomplete){return fallback(legacy,"Shared storage could not be loaded or verified. Using the original download0 library; shared files are preserved. Restart to retry.");}
 }
 static String digest(Path path,MigrationProgress progress,boolean countBytes)throws IOException {
  try{var digest=MessageDigest.getInstance("SHA-256");try(var in=Files.newInputStream(path,LinkOption.NOFOLLOW_LINKS)){byte[] buffer=progress.buffer;for(int n;(n=in.read(buffer))!=-1;){digest.update(buffer,0,n);progress.advance(countBytes?n:0);}}return HexFormat.of().formatHex(digest.digest());}catch(java.security.NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 static void copy(Path source,Path destination)throws IOException {copy(source,destination,new MigrationProgress(SILENT));}
 static void copy(Path source,Path destination,MigrationProgress progress)throws IOException {
  try(var in=Files.newInputStream(source,LinkOption.NOFOLLOW_LINKS);var out=Files.newOutputStream(destination,StandardOpenOption.CREATE,StandardOpenOption.TRUNCATE_EXISTING,LinkOption.NOFOLLOW_LINKS)){
   privateMode(destination,false);byte[] buffer=progress.buffer;for(int n;(n=in.read(buffer))!=-1;){out.write(buffer,0,n);progress.advance(n);}
  }
 }
 // Add one unit per file so an empty file is counted only after its metadata checks.
 static long inventory(Path source,MigrationProgress progress)throws IOException {
  long[] total={0};
  int[] entries={0};
  Files.walkFileTree(source,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   private void entry()throws IOException {
    progress.advance(0);
    if(++entries[0]>MAX_ENTRIES)throw new IOException("Storage migration entry limit exceeded");
   }
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes attributes)throws IOException {
    entry();
    return FileVisitResult.CONTINUE;
   }
   public FileVisitResult visitFile(Path file,BasicFileAttributes attributes)throws IOException {
    entry();
    if(!attributes.isRegularFile())throw new IOException("Unsupported file in storage migration");
    if(file.equals(source.resolve(POINTER)))return FileVisitResult.CONTINUE;
    if(attributes.size()>=Long.MAX_VALUE-total[0])throw new IOException("Storage migration size exceeded");
    total[0]+=attributes.size()+1;
    return FileVisitResult.CONTINUE;
   }
  });
  return total[0];
 }
 static void migrate(Path source,Path target,Copier copier,MigrationProgress progress)throws IOException {
  Path stage=target.resolveSibling(".ProsperoCraft-migration");
  verifiedTree(source,target,stage,copier,progress,false);
  ProsperoLibrary.verifyReadable(stage);
  if(attributes(stage.resolve(READY))==null)Files.writeString(stage.resolve(READY),"shared-v1\n",StandardOpenOption.CREATE_NEW);
  if(!marker(stage.resolve(READY),"shared-v1\n"))throw new IOException("Invalid shared-storage commit marker");
  privateMode(stage.resolve(READY),false);
  if(directory(target))Files.delete(target);
  Files.move(stage,target);
 }
 static void verifiedTree(Path source,Path target,Path stage,Copier copier,MigrationProgress progress,boolean incremental)throws IOException {
  noLinks(source);
  progress.phase("Scanning your library",0);
  long total=inventory(source,progress);
  progress.phase("Moving your library",total);
  noLinks(stage);
  String identity="ProsperoCraft migration v1\n"+source+"\n"+target+"\n";
  if(directory(stage)){if(!marker(stage.resolve(OWNER),identity))throw new IOException("Unrecognized storage migration folder; original data is preserved");}
  else{Files.createDirectory(stage);privateMode(stage,true);Files.writeString(stage.resolve(OWNER),identity,StandardOpenOption.CREATE_NEW);privateMode(stage.resolve(OWNER),false);}
  Map<String,Stamp> files=new HashMap<>();Set<String> directories=new HashSet<>();int[] entries={0};
  Files.walkFileTree(source,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {
    progress.advance(0);if(++entries[0]>MAX_ENTRIES)throw new IOException("Storage migration entry limit exceeded");String name=source.relativize(dir).toString();directories.add(name);Path destination=stage.resolve(name);noLinks(destination);Files.createDirectories(destination);privateMode(destination,true);return FileVisitResult.CONTINUE;
   }
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {
    progress.advance(0);if(++entries[0]>MAX_ENTRIES||!a.isRegularFile())throw new IOException("Unsupported file in storage migration");String name=source.relativize(file).toString();
    if(!incremental&&file.getParent().equals(source)&&name.equals(POINTER))return FileVisitResult.CONTINUE;
    if(file.getParent().equals(source)&&Set.of(OWNER,PART,READY,POINTER).contains(name))throw new IOException("Reserved storage migration filename");
    Path destination=stage.resolve(name);noLinks(destination);String expected=digest(file,progress,false);var previous=attributes(destination);
    if(previous==null||!previous.isRegularFile()||previous.size()!=a.size()||!digest(destination,progress,false).equals(expected)){
     Path part=stage.resolve(PART);noLinks(part);var partial=attributes(part);if(partial!=null&&!partial.isRegularFile())throw new IOException("Invalid storage migration partial");
     if(copier==null)copy(file,part,progress);else{copier.copy(file,part);progress.advance(a.size());}if(Files.size(part)!=a.size()||!digest(part,progress,false).equals(expected))throw new IOException("Storage migration copy verification failed");
     Files.move(part,destination,StandardCopyOption.REPLACE_EXISTING);privateMode(destination,false);
    }else progress.advance(a.size());
    var after=attributes(file);if(after==null||after.size()!=a.size()||!after.lastModifiedTime().equals(a.lastModifiedTime()))throw new IOException("Source data changed during storage migration");
    files.put(name,new Stamp(a.size(),a.lastModifiedTime(),expected));progress.advance(1);return FileVisitResult.CONTINUE;
   }
  });
  progress.finish();
  // Re-read sources after the full copy: no missing/new/changed world files at commit.
  progress.phase("Verifying your library",total);
  Set<String> checkedFiles=new HashSet<>(),checkedDirectories=new HashSet<>();
  Files.walkFileTree(source,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {progress.advance(0);String name=source.relativize(dir).toString();if(!directories.contains(name))throw new IOException("Source directories changed during migration");checkedDirectories.add(name);return FileVisitResult.CONTINUE;}
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {
    String name=source.relativize(file).toString();if(!incremental&&file.getParent().equals(source)&&name.equals(POINTER))return FileVisitResult.CONTINUE;Stamp before=files.get(name);if(before==null||!a.isRegularFile()||a.size()!=before.size()||!a.lastModifiedTime().equals(before.modified())||!digest(file,progress,false).equals(before.digest())||!digest(stage.resolve(name),progress,true).equals(before.digest()))throw new IOException("Source data changed during storage migration");checkedFiles.add(name);progress.advance(1);return FileVisitResult.CONTINUE;
   }
  });
  if(!checkedFiles.equals(files.keySet())||!checkedDirectories.equals(directories))throw new IOException("Source data disappeared during storage migration");
  progress.finish();
  progress.phase("Checking copied files",0);
  Files.walkFileTree(stage,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {
    progress.advance(0);
    if(directories.contains(stage.relativize(dir).toString()))return FileVisitResult.CONTINUE;
    if(!incremental)throw new IOException("Unexpected staged directory");
    ProsperoMigration.purge(dir);
    return FileVisitResult.SKIP_SUBTREE;
   }
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {
    progress.advance(0);
    String name=stage.relativize(file).toString();
    if(!a.isRegularFile())throw new IOException("Unexpected staged file type");
    if(name.equals(OWNER)||(!incremental&&name.equals(READY))||files.containsKey(name)){
     if(incremental)ProsperoMigration.force(file,false);
     return FileVisitResult.CONTINUE;
    }
    if(!incremental)throw new IOException("Unexpected staged file");
    Files.delete(file);
    return FileVisitResult.CONTINUE;
   }
   public FileVisitResult postVisitDirectory(Path dir,IOException error)throws IOException{
    if(error!=null)throw error;
    if(incremental)ProsperoMigration.force(dir,true);
    return FileVisitResult.CONTINUE;
   }
  });
  progress.phase("Finishing library move",0);
 }
}
