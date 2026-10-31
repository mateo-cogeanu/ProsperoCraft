#!/usr/bin/env python3
"""Real socket/parser, authorization, staging, archive and launcher lifecycle checks."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import subprocess,tempfile
from generate_theme_tokens import outputs
from generate_web_icons import generated
assert (Path(__file__).resolve().parents[1]/"client/launcher/java/ProsperoWebIcons.java").read_text()==generated()
ROOT=Path(__file__).resolve().parents[1]
for path,expected in outputs().items():assert path.read_text()==expected, 'Regenerate shared theme tokens'
source=r'''
import java.nio.file.*;import java.net.*;import java.net.http.*;import java.io.*;import java.util.*;import java.util.concurrent.atomic.*;import java.util.zip.*;import com.google.gson.*;
public class WebCheck {
 static void ok(boolean b){if(!b)throw new AssertionError();}
 static class Owner implements ProsperoWeb.Owner {volatile boolean locked,busy;String selected="";public String selectedInstance(){return selected;}int changed;public Object snapshot(){return Map.of("instances",List.of(),"theme",ProsperoTheme.web(2));}public void begin()throws Exception{if(locked||busy)throw new ProsperoWeb.Refused(409,"Locked");busy=true;}public void end(boolean c){busy=false;if(c)changed++;}}
 record Reply(int code,String body,String cookie,String location){}
 static Reply request(ProsperoWeb web,String method,String path,String headers,byte[] body)throws Exception {
  try(Socket s=new Socket("127.0.0.1",web.port())){s.setSoTimeout(6000);var out=s.getOutputStream();String host="127.0.0.1:"+web.port();out.write((method+" "+path+" HTTP/1.1\r\nHost: "+host+"\r\nOrigin: http://"+host+"\r\nX-Prospero-Request: 1\r\nContent-Length: "+body.length+"\r\n"+headers+"\r\n").getBytes());out.write(body);out.flush();String response=new String(s.getInputStream().readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);String cookie="",location="";for(String line:response.split("\r\n"))if(line.startsWith("Location: "))location=line.substring(10);else if(line.startsWith("Set-Cookie: "))cookie=line.substring(12).split(";")[0];return new Reply(Integer.parseInt(response.split(" ")[1]),response.substring(response.indexOf("\r\n\r\n")+4),cookie,location);}
 }
 static byte[] zip(String entry)throws Exception{var out=new ByteArrayOutputStream();try(var zip=new ZipOutputStream(out)){zip.putNextEntry(new ZipEntry(entry));zip.write("{}".getBytes());zip.closeEntry();}return out.toByteArray();}
 static void waitReady(ProsperoWeb web)throws Exception {for(int i=0;i<100&&web.status().addresses().isEmpty();i++)Thread.sleep(10);ok(!web.status().addresses().isEmpty());}
 static void set(Object o,String key,Object value)throws Exception{var f=o.getClass().getDeclaredField(key);f.setAccessible(true);f.set(o,value);var cached=o.getClass().getDeclaredField("cached");cached.setAccessible(true);cached.set(o,null);}
 public static void main(String[] args)throws Exception{
  Path root=Path.of(args[0]);var lib=new ProsperoLibrary(root);var item=lib.add("Web instance","26.3",1,"fabric");var other=lib.add("Other","26.2",2);var owner=new Owner();owner.selected=item.id;var clock=new AtomicLong(System.currentTimeMillis());var addresses=new AtomicReference<>(List.of("127.0.0.1"));
  var web=new ProsperoWeb(lib,owner,0,addresses::get,clock::get);waitReady(web);String host="127.0.0.1:"+web.port();
  String firstCode=web.pairing();ok(firstCode.matches("[A-Z2-9]{3}-[A-Z2-9]{3}")&&firstCode.matches(".*[2-9].*")&&firstCode.matches(".*[A-Z].*"));
  ok(ProsperoWeb.normalizeCode("a2e-34e").equals("A2E34E"));ok(ProsperoWeb.normalizeCode("a2e34e").equals("A2E34E"));ok(ProsperoWeb.normalizeCode("a2e--34e").isEmpty());ok(ProsperoWeb.normalizeCode("").isEmpty());
  var shortLink=request(web,"GET","/i","",new byte[0]);ok(shortLink.code==302&&shortLink.location.equals("/instance/"+item.id));owner.selected=UUID.randomUUID().toString();ok(request(web,"GET","/i","",new byte[0]).code==404);owner.selected=item.id;
  ok(request(web,"GET","/instance/"+item.id,"",new byte[0]).code==200);ok(request(web,"GET","/api","",new byte[0]).code==401);
  ok(request(web,"POST","/pair","X-Pair-Code: wrong\r\n",new byte[0]).code==401);
  Reply pair=request(web,"POST","/pair","X-Pair-Code: "+web.pairing().replace("-","").toLowerCase(Locale.ROOT)+"\r\n",new byte[0]);ok(pair.code==200&&!pair.cookie.isEmpty());String auth="Cookie: "+pair.cookie+"\r\n";
  ok(request(web,"GET","/api",auth,new byte[0]).code==200);ok(request(web,"GET","/icon/1","",new byte[0]).code==200);ok(request(web,"GET","/icon/99","",new byte[0]).code==404);
  String base="/content/"+item.id+"/";
  ok(request(web,"GET",base+"mods/list",auth,new byte[0]).body.equals("[]"));
  for(String kind:List.of("mods","resources","shaders","litematica","worldedit")){
   String name=kind.equals("mods")?"mod.jar":kind.equals("litematica")?"build.litematic":kind.equals("worldedit")?"build.schem":"pack.zip";
   byte[] body=kind.equals("mods")?zip("fabric.mod.json"):kind.equals("resources")?zip("pack.mcmeta"):kind.equals("shaders")?zip("shaders/test.fsh"):new byte[]{10,0,0,0};
   var reply=request(web,"PUT",base+kind+"/"+name,auth,body);ok(reply.code==200);ok(Files.exists(lib.game(item).resolve(ProsperoWeb.DESTINATIONS.get(kind)).resolve(name)));
   ok(request(web,"PUT",base+kind+"/"+name,auth,body).code==409);ok(request(web,"GET",base+kind+"/list",auth,new byte[0]).body.contains(name));
   ok(request(web,"DELETE",base+kind+"/"+name,auth,new byte[0]).code==400);ok(request(web,"DELETE",base+kind+"/"+name,auth+"X-Confirm-Delete: yes\r\n",new byte[0]).code==200);
  }
  ok(request(web,"PUT",base+"mods/with%20space%2B.jar",auth,zip("fabric.mod.json")).code==200);
  ok(request(web,"PUT",base+"mods/fake.jar",auth,"not a jar".getBytes()).code==400);
  ok(request(web,"PUT",base+"resources/wrong.zip",auth,zip("bad")).code==400);
  ok(request(web,"PUT",base+"resources/evil.zip",auth,zip("../escape")).code==400);
  ok(request(web,"PUT",base+"mods/%2e%2e%2fescape.jar",auth,zip("fabric.mod.json")).code==400);
  ok(request(web,"PUT","/content/00000000-0000-0000-0000-000000000000/mods/file.jar",auth,zip("fabric.mod.json")).code==404);
  ok(request(web,"PUT",base+"arbitrary/file.jar",auth,zip("fabric.mod.json")).code==400);
  owner.locked=true;ok(request(web,"PUT",base+"mods/locked.jar",auth,zip("fabric.mod.json")).code==409);owner.locked=false;
  Path outside=root.resolve("outside");Files.createDirectory(outside);Files.createSymbolicLink(lib.game(item).resolve("shaderpacks/link.zip"),outside);ok(request(web,"DELETE",base+"shaders/link.zip",auth+"X-Confirm-Delete: yes\r\n",new byte[0]).code==400);
  // Oversized/ambiguous HTTP requests are refused before any body is consumed.
  try(Socket s=new Socket("127.0.0.1",web.port())){s.getOutputStream().write(("PUT "+base+"mods/huge.jar HTTP/1.1\r\nHost: "+host+"\r\nContent-Length: 134217729\r\n\r\n").getBytes());ok(new String(s.getInputStream().readAllBytes()).startsWith("HTTP/1.1 413"));}
  try(Socket s=new Socket("127.0.0.1",web.port())){s.getOutputStream().write(("POST /pair HTTP/1.1\r\nHost: "+host+"\r\nOrigin: http://evil.invalid\r\nX-Prospero-Request: 1\r\n\r\n").getBytes());ok(new String(s.getInputStream().readAllBytes()).startsWith("HTTP/1.1 403"));}
  try(Socket s=new Socket("127.0.0.1",web.port())){s.getOutputStream().write(("PUT "+base+"mods/interrupted.jar HTTP/1.1\r\nHost: "+host+"\r\nOrigin: http://"+host+"\r\nX-Prospero-Request: 1\r\nContent-Length: 1000\r\n"+auth+"\r\nshort").getBytes());s.shutdownOutput();ok(new String(s.getInputStream().readAllBytes()).startsWith("HTTP/1.1 400"));}
  ok(!owner.busy&&!Files.exists(lib.game(item).resolve("mods/interrupted.jar")));try(var files=Files.walk(lib.game(item))){ok(files.noneMatch(p->p.toString().endsWith(".part")));}
  clock.addAndGet(ProsperoWeb.SESSION_MS+1);ok(!web.pairing().equals(firstCode));ok(request(web,"POST","/pair","X-Pair-Code: "+firstCode+"\r\n",new byte[0]).code==401);ok(request(web,"GET","/api",auth,new byte[0]).code==401);
  pair=request(web,"POST","/pair","X-Pair-Code: "+web.pairing()+"\r\n",new byte[0]);ok(pair.code==200);auth="Cookie: "+pair.cookie+"\r\n";
  ok(request(web,"POST","/revoke",auth,new byte[0]).code==200);ok(request(web,"GET","/api",auth,new byte[0]).code==401);
  addresses.set(List.of());clock.addAndGet(4000);request(web,"GET","/",auth,new byte[0]);Thread.sleep(1100);ok(web.status().addresses().isEmpty());web.close();ok(web.stopped());
  var full=new ProsperoWeb(lib,owner,0,()->List.of("127.0.0.1"),clock::get,p->new OutputStream(){public void write(int b)throws IOException{throw new IOException("No space left on device");}});waitReady(full);
  var fullPair=request(full,"POST","/pair","X-Pair-Code: "+full.pairing()+"\r\n",new byte[0]);var fullReply=request(full,"PUT",base+"mods/full.jar","Cookie: "+fullPair.cookie+"\r\n",zip("fabric.mod.json"));ok(fullReply.code==500&&fullReply.body.contains("Storage is full"));ok(!owner.busy&&!Files.exists(lib.game(item).resolve("mods/full.jar")));try(var paths=Files.walk(lib.game(item))){ok(paths.noneMatch(p->p.toString().endsWith(".part")));}full.close();ok(full.stopped());
  for(int n=0;n<4;n++){var again=new ProsperoWeb(lib,owner,0,()->List.of("127.0.0.1"),clock::get);waitReady(again);again.close();ok(again.stopped());}
  var limited=new ProsperoWeb(lib,owner,0,()->List.of("127.0.0.1"),clock::get);waitReady(limited);for(int i=0;i<5;i++)ok(request(limited,"POST","/pair","X-Pair-Code: WRONG2\r\n",new byte[0]).code==401);ok(request(limited,"POST","/pair","X-Pair-Code: "+limited.pairing()+"\r\n",new byte[0]).code==429);clock.addAndGet(60_001);ok(request(limited,"POST","/pair","X-Pair-Code: "+limited.pairing()+"\r\n",new byte[0]).code==200);limited.close();ok(limited.stopped());
  // Real launcher screen owns service and blocks mutation when leaving/launching.
  lib.settings().showIntro=false;lib.save();var launcher=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError();});launcher.tick(0x4000);launcher.tick(0x10008000|4<<20|3<<16|1);launcher.tick(0x10008000|5<<20|3<<16|8);ok(launcher.tick(0)[11].equals("15"));launcher.tick(0x2000);ok(launcher.tick(0)[11].equals("5"));launcher.tick(0x20);ok(launcher.tick(0)[15].equals("8"));launcher.tick(0x10);ok(launcher.tick(0)[15].equals("4"));launcher.tick(0x20);ok(launcher.tick(0)[15].equals("7"));launcher.tick(0x40);ok(launcher.tick(0)[15].equals("8"));launcher.tick(0x40);ok(launcher.tick(0)[15].equals("5"));launcher.tick(0x20);ok(launcher.tick(0)[15].equals("6"));launcher.tick(0x10);ok(launcher.tick(0)[15].equals("8"));
  System.out.println("PASS real bounded HTTP/pair/session expiry/revoke/origin/traversal/formats/duplicates/staging/disconnect/locks/network changes/restarts/launcher lifecycle; shared themes current");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-web-') as td:
    w=Path(td).resolve();(w/'WebCheck.java').write_text(source);cp=launcher_classpath();jdk=java_home()
    subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p) for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'WebCheck.java')],check=True)
    subprocess.run([str(jdk/'bin/java'),'-cp',str(w)+':'+cp,'WebCheck',str(w/'data')],check=True,timeout=60)
