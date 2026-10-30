import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.zip.*;

/** A normal resource-pack override for the pinned Controlify 26.3 layout bug. */
final class ProsperoControlifyKeyboard {
 static final String MOD_SHA256="bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a";
 static final String PACK="prosperocraft-controlify-keyboard-26.3.zip", ID="file/"+PACK;
 private static final String OWNER="prosperocraft-controlify-keyboard-v1";
 private static final String MARKER="prosperocraft-keyboard-fix.txt";
 static String prepare(Path game,String version,String loader)throws IOException {
  if(!"26.3".equals(version)||!"fabric".equals(loader))return "NOT_APPLICABLE";
  Path pack=game.resolve("resourcepacks").resolve(PACK),mods=game.resolve("mods");
  Path controlify=null;int count=0;
  if(Files.isDirectory(mods))try(var files=Files.list(mods)){
   for(Path jar:files.filter(p->Files.isRegularFile(p)&&p.getFileName().toString().endsWith(".jar")).toList()){
    try(ZipFile zip=new ZipFile(jar.toFile())){
     ZipEntry meta=zip.getEntry("fabric.mod.json");if(meta==null)continue;
     JsonObject info=JsonParser.parseString(read(zip,meta)).getAsJsonObject();
     if(info.has("id")&&"controlify".equals(info.get("id").getAsString())){controlify=jar;count++;}
    }catch(ZipException|IllegalStateException|JsonParseException invalid){/* Not a loadable Fabric metadata record. */}
   }
  }
  boolean exists=Files.exists(pack),owned=exists&&owned(pack);
  if(exists&&!owned)return "SKIPPED_PACK_NAME_COLLISION";
  if(count!=1||!MOD_SHA256.equals(sha(controlify))){
   if(owned){select(game,false);Files.delete(pack);}
   return "NOT_PINNED";
  }
  if(owned)return selected(game)?"READY":"DISABLED_BY_USER";
  // Validate options before creating a pack or changing any selection.
  selections(game);
  Map<String,byte[]> layouts=new TreeMap<>();byte[] license;
  try(ZipFile zip=new ZipFile(controlify.toFile())){
   license=read(zip,Objects.requireNonNull(zip.getEntry("META-INF/LICENSE"))).getBytes(StandardCharsets.UTF_8);
   var entries=zip.entries();int changes=0;
   while(entries.hasMoreElements()){
    ZipEntry e=entries.nextElement();String name=e.getName();
    if(!e.isDirectory()&&name.startsWith("assets/controlify/keyboard_layout/")&&name.endsWith(".json")){
     if(layouts.size()>=32)throw new IOException("Too many Controlify keyboard layouts");
     JsonObject layout=JsonParser.parseString(read(zip,e)).getAsJsonObject();
     int changed=backspace(layout.get("keys"));
     if(changed>0){layouts.put(name,layout.toString().getBytes(StandardCharsets.UTF_8));changes+=changed;}
    }
   }
   if(layouts.size()!=3||changes!=3)throw new IOException("Unexpected pinned Controlify layout shape");
  }
  Files.createDirectories(pack.getParent());Path temp=Files.createTempFile(pack.getParent(),"keyboard-",".tmp");
  try{
   try(ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(temp))){
    entry(out,MARKER,OWNER.getBytes(StandardCharsets.UTF_8));
    entry(out,"licenses/Controlify-LGPL-3.0.txt",license);
    entry(out,"NOTICE.txt",("Layouts derived from Controlify 3.5.3+mc26.3 by isXander and contributors; LGPL-3.0.\nhttps://github.com/isXander/Controlify\nOriginal JAR SHA256 "+MOD_SHA256+"\nProsperoCraft changes only the backspace function to supply scancode42/keycode8 through the supported layout codec.\n").getBytes(StandardCharsets.UTF_8));
    entry(out,"pack.mcmeta",("{\"pack\":{\"description\":\"Controlify 26.3 keyboard compatibility\",\"min_format\":[97,1],\"max_format\":[97,1]}}").getBytes(StandardCharsets.UTF_8));
    for(var e:layouts.entrySet())entry(out,e.getKey(),e.getValue());
   }
   Files.move(temp,pack); // Never replace an unrelated file which appeared meanwhile.
   try{select(game,true);}catch(IOException|RuntimeException failure){Files.deleteIfExists(pack);throw failure;}
  }finally{Files.deleteIfExists(temp);}
  return "INSTALLED_LAYOUTS_3";
 }
 private static int backspace(JsonElement value){
  if(value==null)return 0;int changed=0;
  if(value.isJsonArray())for(JsonElement e:value.getAsJsonArray())changed+=backspace(e);
  else if(value.isJsonObject()){
   JsonObject object=value.getAsJsonObject();
   for(var e:new ArrayList<>(object.entrySet())){
    JsonElement f=e.getValue();
    if(f.isJsonObject()&&f.getAsJsonObject().has("action")&&"backspace".equals(f.getAsJsonObject().get("action").getAsString())){
     // Upstream field names are historical: first=SDL scancode, second=keycode
     // in 26.3's KeyEvent. Keep the actual backspace position AND shortcut value.
     JsonObject code=new JsonObject();code.addProperty("keycode",42);code.addProperty("scancode",8);
     JsonArray codes=new JsonArray();codes.add(code);JsonObject function=new JsonObject();function.add("codes",codes);
     JsonObject label=new JsonObject();label.addProperty("translate","controlify.keyboard.special.backspace");function.add("display_name",label);object.add(e.getKey(),function);changed++;
    }else changed+=backspace(f);
   }
  }
  return changed;
 }
 private static String read(ZipFile zip,ZipEntry entry)throws IOException {
  try(InputStream in=zip.getInputStream(entry)){byte[] bytes=in.readNBytes(65537);if(bytes.length>65536)throw new IOException("Oversized keyboard metadata");return new String(bytes,StandardCharsets.UTF_8);}
 }
 private static boolean owned(Path pack)throws IOException {
  try(ZipFile zip=new ZipFile(pack.toFile())){ZipEntry marker=zip.getEntry(MARKER);return marker!=null&&OWNER.equals(read(zip,marker));}catch(ZipException invalid){return false;}
 }
 private static void entry(ZipOutputStream out,String name,byte[] bytes)throws IOException {ZipEntry e=new ZipEntry(name);e.setTime(0);out.putNextEntry(e);out.write(bytes);out.closeEntry();}
 private static String sha(Path path)throws IOException {
  try{MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream in=Files.newInputStream(path);DigestInputStream data=new DigestInputStream(in,digest)){data.transferTo(OutputStream.nullOutputStream());}return HexFormat.of().formatHex(digest.digest());}
  catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 private static JsonArray selections(Path game)throws IOException {
  Path options=game.resolve("options.txt");if(!Files.exists(options))return new JsonArray();
  String found=null;
  for(String line:Files.readString(options).split("\\R"))if(line.startsWith("resourcePacks:")){if(found!=null)throw new IOException("Duplicate resource pack option");found=line.substring("resourcePacks:".length());}
  try{JsonArray list=found==null?new JsonArray():JsonParser.parseString(found).getAsJsonArray();for(JsonElement e:list)if(!e.isJsonPrimitive()||!e.getAsJsonPrimitive().isString())throw new IOException("Invalid resource pack list");return list;}
  catch(RuntimeException invalid){throw new IOException("Invalid resource pack option",invalid);}
 }
 private static boolean selected(Path game)throws IOException {for(JsonElement e:selections(game))if(ID.equals(e.getAsString()))return true;return false;}
 private static void select(Path game,boolean enable)throws IOException {
  JsonArray list=selections(game),result=new JsonArray();for(JsonElement e:list)if(!ID.equals(e.getAsString()))result.add(e);
  if(enable)result.add(ID);
  Path options=game.resolve("options.txt");String original=Files.exists(options)?Files.readString(options):"";
  String replacement="resourcePacks:"+result;
  String desired=original.replaceAll("(?m)^resourcePacks:[^\\r\\n]*",java.util.regex.Matcher.quoteReplacement(replacement));
  if(!original.lines().anyMatch(s->s.startsWith("resourcePacks:")))desired=original+(original.isEmpty()||original.endsWith("\n")?"":"\n")+replacement+"\n";
  if(desired.equals(original))return;
  Path backup=game.resolve("options.before-controlify-keyboard162.txt");if(Files.exists(options)&&!Files.exists(backup))Files.copy(options,backup);
  ProsperoInstall.save(options,desired);
 }
}
