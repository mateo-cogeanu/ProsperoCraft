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
 record Selection(Path root,String notice){}
 interface Probe {void check(Path root)throws IOException;}
 interface Copier {void copy(Path source,Path destination)throws IOException;}
 record Stamp(long size,java.nio.file.attribute.FileTime modified,String digest){}
 static Selection current()throws IOException {
  String explicit=System.getProperty("ps5.launcher.root");
  if(explicit!=null&&!explicit.isBlank())return new Selection(Path.of(explicit),"");
  return select(Path.of("/download0/ProsperoCraft"),Path.of("/data/ProsperoCraft"),ProsperoStorageRoot::probe,ProsperoStorageRoot::copy);
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
 static Selection select(Path legacy,Path preferred,Probe probe,Copier copier)throws IOException {
  legacy=legacy.toAbsolutePath().normalize();preferred=preferred.toAbsolutePath().normalize();
  if(legacy.startsWith(preferred)||preferred.startsWith(legacy))throw new IOException("Storage locations overlap");noLinks(legacy);
  boolean selected=marker(legacy.resolve(POINTER),"shared-v1\n");
  if(attributes(legacy.resolve(POINTER))!=null&&!selected)throw new IOException("Storage selection marker is invalid. Both storage locations are preserved.");
  try{probe.check(preferred);}catch(IOException unavailable){
   if(selected)throw new IOException("Shared storage is unavailable. Reopen with ShadowMountPlus access to /data; shared worlds are preserved.");
   if(nonempty(legacy))return new Selection(legacy,"Shared storage is unavailable. Your existing library remains in download0; update ShadowMountPlus to enable /data.");
   throw new IOException("Shared storage is unavailable. Update ShadowMountPlus to enable /data/ProsperoCraft. Existing data is preserved.");
  }
  noLinks(preferred);
  var library=attributes(preferred.resolve("library.json"));if(library!=null&&!library.isRegularFile())throw new IOException("Shared library metadata is not a regular file");
  if(selected){if(!directory(preferred)||(library==null&&!marker(preferred.resolve(READY),"shared-v1\n")))throw new IOException("Selected shared storage is missing. The old backup was not opened.");return new Selection(preferred,"");}
  if(nonempty(preferred)){
   if(nonempty(legacy)&&!marker(preferred.resolve(READY),"shared-v1\n"))throw new IOException("Libraries already exist in both storage locations. Both are preserved; no merge was attempted.");
   if(attributes(preferred.resolve("library.json"))==null&&!marker(preferred.resolve(READY),"shared-v1\n"))throw new IOException("Shared storage already contains files without a library. Both locations are preserved.");
   remember(legacy);return new Selection(preferred,"");
  }
  boolean old=nonempty(legacy);
  if(old){try{migrate(legacy,preferred,copier);}catch(IOException incomplete){if(directory(preferred)&&marker(preferred.resolve(READY),"shared-v1\n"))throw incomplete;return new Selection(legacy,"Shared-storage copy could not finish. Your original library is active; its files are preserved. Restart to retry.");}}
  else{Files.createDirectories(preferred);privateMode(preferred,true);Files.writeString(preferred.resolve(READY),"shared-v1\n",StandardOpenOption.CREATE_NEW);}
  remember(legacy);
  return new Selection(preferred,old?"Storage moved to /data/ProsperoCraft. Your original download0 library is retained as a backup.":"");
 }
 static void remember(Path legacy)throws IOException {
  Files.createDirectories(legacy);privateMode(legacy,true);Path marker=legacy.resolve(POINTER);noLinks(marker);
  if(attributes(marker)!=null){if(!marker(marker,"shared-v1\n"))throw new IOException("Storage selection marker is invalid");return;}
  Files.writeString(marker,"shared-v1\n",StandardOpenOption.CREATE_NEW);privateMode(marker,false);
 }
 static String digest(Path path)throws IOException {
  try{var digest=MessageDigest.getInstance("SHA-256");try(var in=Files.newInputStream(path,LinkOption.NOFOLLOW_LINKS)){byte[] buffer=new byte[65536];for(int n;(n=in.read(buffer))!=-1;)digest.update(buffer,0,n);}return HexFormat.of().formatHex(digest.digest());}catch(java.security.NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 static void copy(Path source,Path destination)throws IOException {
  try(var in=Files.newInputStream(source,LinkOption.NOFOLLOW_LINKS);var out=Files.newOutputStream(destination,StandardOpenOption.CREATE,StandardOpenOption.TRUNCATE_EXISTING,LinkOption.NOFOLLOW_LINKS)){
   privateMode(destination,false);byte[] buffer=new byte[65536];for(int n;(n=in.read(buffer))!=-1;)out.write(buffer,0,n);
  }
 }
 static void migrate(Path source,Path target,Copier copier)throws IOException {
  Path stage=target.resolveSibling(".ProsperoCraft-migration");noLinks(stage);
  String identity="ProsperoCraft migration v1\n"+source+"\n"+target+"\n";
  if(directory(stage)){if(!marker(stage.resolve(OWNER),identity))throw new IOException("Unrecognized storage migration folder; original data is preserved");}
  else{Files.createDirectory(stage);privateMode(stage,true);Files.writeString(stage.resolve(OWNER),identity,StandardOpenOption.CREATE_NEW);privateMode(stage.resolve(OWNER),false);}
  Map<String,Stamp> files=new HashMap<>();Set<String> directories=new HashSet<>();int[] entries={0};
  Files.walkFileTree(source,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {
    if(++entries[0]>MAX_ENTRIES)throw new IOException("Storage migration entry limit exceeded");String name=source.relativize(dir).toString();directories.add(name);Path destination=stage.resolve(name);noLinks(destination);Files.createDirectories(destination);privateMode(destination,true);return FileVisitResult.CONTINUE;
   }
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {
    if(++entries[0]>MAX_ENTRIES||!a.isRegularFile())throw new IOException("Unsupported file in storage migration");String name=source.relativize(file).toString();
    if(file.getParent().equals(source)&&Set.of(OWNER,PART,READY,POINTER).contains(name))throw new IOException("Reserved storage migration filename");
    Path destination=stage.resolve(name);noLinks(destination);String expected=digest(file);var previous=attributes(destination);
    if(previous==null||!previous.isRegularFile()||previous.size()!=a.size()||!digest(destination).equals(expected)){
     Path part=stage.resolve(PART);noLinks(part);var partial=attributes(part);if(partial!=null&&!partial.isRegularFile())throw new IOException("Invalid storage migration partial");
     copier.copy(file,part);if(Files.size(part)!=a.size()||!digest(part).equals(expected))throw new IOException("Storage migration copy verification failed");
     Files.move(part,destination,StandardCopyOption.REPLACE_EXISTING);privateMode(destination,false);
    }
    var after=attributes(file);if(after==null||after.size()!=a.size()||!after.lastModifiedTime().equals(a.lastModifiedTime()))throw new IOException("Source data changed during storage migration");
    files.put(name,new Stamp(a.size(),a.lastModifiedTime(),expected));return FileVisitResult.CONTINUE;
   }
  });
  // Re-read sources after the full copy: no missing/new/changed world files at commit.
  Set<String> checkedFiles=new HashSet<>(),checkedDirectories=new HashSet<>();
  Files.walkFileTree(source,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {String name=source.relativize(dir).toString();if(!directories.contains(name))throw new IOException("Source directories changed during migration");checkedDirectories.add(name);return FileVisitResult.CONTINUE;}
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {
    String name=source.relativize(file).toString();Stamp before=files.get(name);if(before==null||!a.isRegularFile()||a.size()!=before.size()||!a.lastModifiedTime().equals(before.modified())||!digest(file).equals(before.digest())||!digest(stage.resolve(name)).equals(before.digest()))throw new IOException("Source data changed during storage migration");checkedFiles.add(name);return FileVisitResult.CONTINUE;
   }
  });
  if(!checkedFiles.equals(files.keySet())||!checkedDirectories.equals(directories))throw new IOException("Source data disappeared during storage migration");
  Files.walkFileTree(stage,EnumSet.noneOf(FileVisitOption.class),64,new SimpleFileVisitor<>(){
   public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes a)throws IOException {if(!directories.contains(stage.relativize(dir).toString()))throw new IOException("Unexpected staged directory");return FileVisitResult.CONTINUE;}
   public FileVisitResult visitFile(Path file,BasicFileAttributes a)throws IOException {String name=stage.relativize(file).toString();if(!a.isRegularFile()||(!name.equals(OWNER)&&!name.equals(READY)&&!files.containsKey(name)))throw new IOException("Unexpected staged file");return FileVisitResult.CONTINUE;}
  });
  if(attributes(stage.resolve(READY))==null)Files.writeString(stage.resolve(READY),"shared-v1\n",StandardOpenOption.CREATE_NEW);
  if(!marker(stage.resolve(READY),"shared-v1\n"))throw new IOException("Invalid shared-storage commit marker");privateMode(stage.resolve(READY),false);
  // A single same-filesystem directory rename publishes only a verified complete tree.
  if(directory(target))Files.delete(target); // succeeds only for an empty target
  Files.move(stage,target);
 }
}
