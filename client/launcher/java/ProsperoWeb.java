/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.function.*;
import java.util.zip.ZipFile;
import com.google.gson.*;

/** Menu-scoped administrative service. One worker/socket/upload; no diagnostics sharing. */
final class ProsperoWeb implements AutoCloseable {
 static final long PAIRING_MS=5*60_000L;
 static final long MAX_UPLOAD=16L*1024*1024*1024, UPLOAD_MS=30*60_000L, SESSION_MS=15*60_000L;
 static final int UPLOAD_IDLE_MS=30_000;
 static final String UPLOAD_LABEL="16 GiB";
 static final long UPLOAD_RATE=512*1024, UPLOAD_GRACE_MS=5*60_000L;
 static long uploadMillis(long bytes){return Math.max(UPLOAD_MS,((bytes+UPLOAD_RATE-1)/UPLOAD_RATE)*1000+UPLOAD_GRACE_MS);}
 interface Owner {
  Object snapshot()throws Exception;
  default String selectedInstance(){return "";}
  void begin()throws Exception;
  void end(boolean changed);
 }
 interface Addresses {List<String> get()throws Exception;}
 interface UploadSink {OutputStream open(Path staging)throws IOException;}
 private final UploadSink sink;
 record Status(String state,List<String> addresses,int port){}
 private final ProsperoLibrary library;private final Owner owner;private final Addresses discovery;
 private final LongSupplier clock;private final SecureRandom random=new SecureRandom();
 private final ServerSocket server;private volatile Socket active;private final Thread thread;
 private volatile boolean closed;private volatile Status status;
 private volatile long pairingExpires;private volatile String pairing;private volatile String session="";private volatile long expires;private long attemptWindow;private int attempts;
 private volatile List<String> hosts=List.of();private long refreshAt;
 ProsperoWeb(ProsperoLibrary library,Owner owner,int port)throws IOException {this(library,owner,port,ProsperoWeb::localAddresses,System::currentTimeMillis);}
 ProsperoWeb(ProsperoLibrary library,Owner owner,int port,Addresses discovery,LongSupplier clock)throws IOException {
  this(library,owner,port,discovery,clock,p->Files.newOutputStream(p,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS));
 }
 ProsperoWeb(ProsperoLibrary library,Owner owner,int port,Addresses discovery,LongSupplier clock,UploadSink sink)throws IOException {
  this.library=library;this.owner=owner;this.discovery=discovery;this.clock=clock;this.sink=sink;
  pairing=shortCode();pairingExpires=clock.getAsLong()+PAIRING_MS;server=new ServerSocket();
  try{server.setReuseAddress(true);server.bind(new InetSocketAddress(port),4);server.setSoTimeout(1000);}catch(IOException failed){server.close();throw failed;}
  status=new Status("Discovering local addresses",List.of(),server.getLocalPort());
  thread=new Thread(this::serve,"ProsperoCraft local manager");thread.setDaemon(true);thread.start();
 }
 String pairing(){renewPairing();return pairing;}
 private synchronized void renewPairing(){if(!closed&&clock.getAsLong()>=pairingExpires){pairingExpires=clock.getAsLong()+PAIRING_MS;pairing=shortCode();}}
 Status status(){return status;}
 int port(){return server.getLocalPort();}
 static String normalizeCode(String value){
  if(value==null||!value.matches("[A-Za-z2-9]{3}-?[A-Za-z2-9]{3}"))return "";
  return value.replace("-","").toUpperCase(Locale.ROOT);
 }
 private String shortCode(){
  final String alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789";String code;
  do{StringBuilder b=new StringBuilder();for(int n=0;n<6;n++)b.append(alphabet.charAt(random.nextInt(alphabet.length())));code=b.toString();}while(!code.matches(".*[A-Z].*")||!code.matches(".*[2-9].*")||(code.substring(0,3)+"-"+code.substring(3)).equals(pairing));
  return code.substring(0,3)+"-"+code.substring(3);
 }
 private String secret(){byte[] b=new byte[16];random.nextBytes(b);return HexFormat.of().formatHex(b);}
 static List<String> localAddresses()throws SocketException {
  var found=new TreeSet<String>();var interfaces=NetworkInterface.getNetworkInterfaces();
  if(interfaces!=null)for(var nic:Collections.list(interfaces))if(nic.isUp()&&!nic.isLoopback())for(var ip:Collections.list(nic.getInetAddresses()))
   if(ip instanceof Inet4Address&&!ip.isLoopbackAddress()&&!ip.isLinkLocalAddress()&&ip.isSiteLocalAddress())found.add(ip.getHostAddress());
  return List.copyOf(found);
 }
 private void refresh(){
  long now=clock.getAsLong();renewPairing();if(now<refreshAt)return;refreshAt=now+3000;
  try{var ips=discovery.get();if(ips.size()>16)ips=ips.subList(0,16);var current=List.copyOf(ips);
   // Address removal revokes a paired browser. Never keep stale QR addresses.
   if(!status.addresses().equals(current)){session="";expires=0;}
   hosts=current.stream().map(ip->ip+":"+port()).toList();status=new Status(current.isEmpty()?"No private IPv4 address available":"Ready",current,port());
  }catch(Exception unavailable){hosts=List.of();session="";status=new Status("Network discovery unavailable",List.of(),port());}
 }
 private void serve(){
  try{while(!closed){refresh();try(Socket socket=server.accept()){active=socket;socket.setSoTimeout(5000);handle(socket);}catch(SocketTimeoutException idle){}catch(Exception failure){/* Never log URLs, headers, credentials, paths or exception text. */}finally{active=null;}}}
  finally{status=new Status("Stopped",List.of(),0);hosts=List.of();}
 }
 static final class Refused extends IOException {final int status;Refused(int status,String reason){super(reason);this.status=status;}}
 static void require(boolean ok,int status,String reason)throws Refused{if(!ok)throw new Refused(status,reason);}
 private String line(InputStream in,int max,long deadline)throws IOException {
  var out=new ByteArrayOutputStream();while(out.size()<max){require(clock.getAsLong()<deadline,408,"Request timed out");int c=in.read();if(c<0)throw new EOFException();if(c=='\n'){byte[] b=out.toByteArray();require(b.length>0&&b[b.length-1]=='\r',400,"Invalid request");return new String(b,0,b.length-1,StandardCharsets.US_ASCII);}require(c>=32||c=='\r',400,"Invalid request");out.write(c);}throw new Refused(431,"Request headers too large");
 }
 private void handle(Socket socket)throws IOException {
  var in=new BufferedInputStream(socket.getInputStream(),8192);var out=socket.getOutputStream();String cookie="";
  try{
   long deadline=clock.getAsLong()+5000;String[] request=line(in,2048,deadline).split(" ",-1);require(request.length==3&&request[2].equals("HTTP/1.1"),400,"HTTP/1.1 required");
   String method=request[0],path=request[1];
   try{path=URLDecoder.decode(path.replace("+","%2B"),StandardCharsets.UTF_8);}catch(IllegalArgumentException invalid){throw new Refused(400,"Invalid route encoding");}require(Set.of("GET","POST","PUT","DELETE").contains(method),405,"Method unavailable");
   require(path.matches("/[A-Za-z0-9/ ._()+-]*")&&!path.contains(".."),400,"Invalid route");
   var headers=new HashMap<String,String>();int bytes=0;
   for(int i=0;;i++){String h=line(in,2048,deadline);bytes+=h.length();require(bytes<=8192&&i<=32,431,"Request headers too large");if(h.isEmpty())break;int at=h.indexOf(':');require(at>0,400,"Invalid header");String key=h.substring(0,at).toLowerCase(Locale.ROOT);require(key.matches("[a-z0-9-]+")&&!headers.containsKey(key),400,"Duplicate or invalid header");headers.put(key,h.substring(at+1).strip());}
   require(!headers.containsKey("transfer-encoding")&&!headers.containsKey("expect"),400,"Use a bounded Content-Length upload");
   String host=headers.getOrDefault("host","");require(hosts.contains(host),403,"Address changed. Reopen the launcher address");
   long length=0;try{String l=headers.getOrDefault("content-length","0");require(l.matches("[0-9]{1,18}"),400,"Invalid length");length=Long.parseLong(l);}catch(NumberFormatException bad){throw new Refused(400,"Invalid length");}
   require(length<=MAX_UPLOAD,413,"Maximum file size is "+UPLOAD_LABEL);
   if(method.equals("GET"))require(length==0,400,"Unexpected body");
   if(!method.equals("GET")){require(("http://"+host).equals(headers.get("origin")),403,"Open this page directly from the launcher address");require("1".equals(headers.get("x-prospero-request")),403,"Browser request required");}
   if(method.equals("GET")&&path.matches("/icon/[0-9]{1,2}")){int icon=Integer.parseInt(path.substring(6));require(icon<ProsperoWebIcons.PNG.length,404,"Icon unavailable");respondBytes(out,200,"image/png",Base64.getDecoder().decode(ProsperoWebIcons.PNG[icon]),"");return;}
   if(method.equals("GET")&&path.equals("/i")){
    String id=owner.selectedInstance();require(id.matches("[a-f0-9-]{36}")&&library.instances().stream().anyMatch(i->i.id.equals(id)),404,"Selected instance unavailable");
    respond(out,302,"text/plain","Opening your instance","Location: /instance/"+id+"\r\n");return;
   }
   if(method.equals("GET")&&(path.equals("/")||path.matches("/instance/[a-f0-9-]{36}"))){respond(out,200,"text/html; charset=utf-8",ProsperoWebPage.HTML,"");return;}
   if(method.equals("POST")&&path.equals("/pair")){
    require(length==0,400,"Unexpected pairing body");long now=clock.getAsLong();if(now-attemptWindow>=60_000){attemptWindow=now;attempts=0;}require(++attempts<=5,429,"Too many attempts. Wait one minute");
    require(now<pairingExpires,401,"Pairing code expired. Use the new code on your PS5");String supplied=normalizeCode(headers.getOrDefault("x-pair-code",""));require(!closed&&!supplied.isEmpty()&&MessageDigest.isEqual(normalizeCode(pairing).getBytes(StandardCharsets.US_ASCII),supplied.getBytes(StandardCharsets.US_ASCII)),401,"Pairing code did not match");
    session=secret();expires=now+SESSION_MS;cookie="Set-Cookie: prospero="+session+"; HttpOnly; SameSite=Strict; Path=/; Max-Age=900\r\n";
    respond(out,200,"application/json","{}",cookie);return;
   }
   boolean authorized=false;for(String part:headers.getOrDefault("cookie","").split(";"))if(part.strip().equals("prospero="+session)&&!session.isEmpty())authorized=true;
   require(authorized&&clock.getAsLong()<expires,401,"Session expired. Pair using the code on your PS5");
   if(method.equals("POST")&&path.equals("/revoke")){session="";expires=0;respond(out,200,"application/json","{}","Set-Cookie: prospero=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0\r\n");return;}
   if(method.equals("GET")&&path.equals("/api")){respond(out,200,"application/json",new Gson().toJson(owner.snapshot()),"");return;}
   String[] route=path.split("/");require(route.length==5&&route[1].equals("content"),404,"Page unavailable");
   var instance=library.instances().stream().filter(i->i.id.equals(route[2])).findFirst().orElseThrow(()->new Refused(404,"Instance unavailable"));
   String kind=route[3];require(DESTINATIONS.containsKey(kind),400,"Invalid content destination");
   boolean mutate=!method.equals("GET");boolean entered=false,changed=false;
   try{
    if(mutate){owner.begin();entered=true;}
    Path folder=folder(instance,kind,mutate);String name=route[4];
    if(method.equals("GET")&&name.equals("list")){respond(out,200,"application/json",new Gson().toJson(list(folder)),"");return;}
    require(route.length==5&&Set.of("PUT","DELETE").contains(method),405,"Operation unavailable");validName(name,kind);Path target=folder.resolve(name);noLink(target);
    if(method.equals("DELETE")){
     require("yes".equals(headers.get("x-confirm-delete")),400,"Confirm removal first");require(Files.isRegularFile(target,LinkOption.NOFOLLOW_LINKS),404,"File unavailable");
     // Managed content must be uninstalled by the existing receipt-aware launcher.
     require(!managed(instance,name),409,"Use the launcher to uninstall Modrinth-managed content");Files.delete(target);changed=true;
    }else{
     require(instance.loader.equals("fabric")||kind.equals("resources"),409,"This content needs a compatible Fabric mod; use a Fabric instance");require(length>0,400,"Empty upload");require(!Files.exists(target,LinkOption.NOFOLLOW_LINKS),409,"Filename already exists. Remove it explicitly or rename your upload");
     Path staging=Files.createTempFile(folder,".prospero-upload-",".part");
     try{
      // Capacity query is unsupported on the console; ENOSPC/quota write errors are authoritative.
      byte[] buffer=new byte[65536];long left=length,until=clock.getAsLong()+uploadMillis(length);socket.setSoTimeout(UPLOAD_IDLE_MS);
      try(var file=sink.open(staging)){
       while(left>0){require(!closed&&clock.getAsLong()<until,408,"Upload timed out");int count=in.read(buffer,0,(int)Math.min(buffer.length,left));if(count<0)throw new Refused(400,"Upload interrupted");require(!closed&&clock.getAsLong()<until,408,"Upload timed out");file.write(buffer,0,count);left-=count;}
      }
      require(!closed,409,"Service stopped; upload cancelled");require(clock.getAsLong()<until,408,"Upload timed out");inspect(staging,kind);noLink(target);require(!closed,409,"Service stopped; upload cancelled");require(!Files.exists(target,LinkOption.NOFOLLOW_LINKS),409,"Filename already exists");
      // No replacement flag: a racing existing filename is never overwritten.
      Files.move(staging,target);changed=true;
     }finally{Files.deleteIfExists(staging);}
    }
    respond(out,200,"application/json","{\"result\":\"Saved. Refresh the installed list. Compatibility is not established by upload.\"}","");
   }finally{if(entered)owner.end(changed);}
  }catch(Refused denied){respond(out,denied.status,"application/json",new Gson().toJson(Map.of("error",denied.getMessage())),"");}
  catch(SocketTimeoutException timeout){respond(out,408,"application/json","{\"error\":\"Transfer stopped responding. Retry the upload.\"}","");}
  catch(Exception failure){String code=failure instanceof IOException io?ProsperoStorage.code(io):"IO";respond(out,500,"application/json",new Gson().toJson(Map.of("error",Set.of("ENOSPC","QUOTA").contains(code)?"Storage is full. The upload was not installed.":"Operation unavailable. Check storage and retry; existing files are preserved.")),"");}finally{
   // Deliver an early refusal before closing a socket with an unread upload body.
   // Discard only a small bounded tail; never allocate/read the advertised body.
   try{socket.shutdownOutput();socket.setSoTimeout(100);byte[] discard=new byte[4096];long until=System.nanoTime()+200_000_000L;int left=65536;while(left>0&&System.nanoTime()<until){int n=in.read(discard,0,Math.min(left,discard.length));if(n<0)break;left-=n;}}catch(IOException ignored){}
  }
 }
 static final Map<String,String> DESTINATIONS=Map.of("mods","mods","resources","resourcepacks","shaders","shaderpacks","litematica","schematics","worldedit","config/worldedit/schematics");
 static void noLink(Path path)throws IOException{require(!Files.isSymbolicLink(path),400,"Linked storage is unavailable");}
 Path folder(ProsperoLibrary.Instance instance,String kind,boolean create)throws IOException {
  if(kind.equals("mods"))require(instance.loader.equals("fabric"),409,"Mods require a Fabric instance");
  Path target=library.game(instance).resolve(DESTINATIONS.get(kind));Path at=library.root.toAbsolutePath().normalize();ProsperoDownloads.noLinks(at);
  for(Path part:at.relativize(target.toAbsolutePath().normalize())){at=at.resolve(part);noLink(at);if(create&&!Files.exists(at,LinkOption.NOFOLLOW_LINKS))Files.createDirectory(at);if(Files.exists(at,LinkOption.NOFOLLOW_LINKS))require(Files.isDirectory(at,LinkOption.NOFOLLOW_LINKS),400,"Invalid content directory");}
  if(create&&Files.isDirectory(target,LinkOption.NOFOLLOW_LINKS))try(var leftovers=Files.newDirectoryStream(target,".prospero-upload-*.part")){int count=0;for(Path file:leftovers){require(++count<=2048,409,"Too many interrupted uploads");if(Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))Files.delete(file);}}
  return target;
 }
 static void validName(String name,String kind)throws IOException {
  require(name.length()<=120&&name.matches("[A-Za-z0-9][A-Za-z0-9 ._()+-]*")&&!name.contains(".."),400,"Use a simple filename up to 120 characters");
  String lower=name.toLowerCase(Locale.ROOT);boolean valid=switch(kind){case "mods"->lower.endsWith(".jar");case "resources","shaders"->lower.endsWith(".zip");case "litematica"->lower.endsWith(".litematic");case "worldedit"->lower.endsWith(".schem")||lower.endsWith(".schematic");default->false;};require(valid,400,"Unsupported format for this destination");
 }
 static int u16(byte[] b,int i){return (b[i]&255)|(b[i+1]&255)<<8;}
 static long u32(byte[] b,int i){return Integer.toUnsignedLong(u16(b,i)|u16(b,i+2)<<16);}
 // ZIP64 fields are unsigned; values outside Java/file limits are refused before allocation.
 static long u64(byte[] bytes,int at)throws IOException {long value=u32(bytes,at)|(u32(bytes,at+4)<<32);require(value>=0,400,"ZIP value exceeds supported range");return value;}
 static long directory(Path file,String kind)throws IOException {
  boolean pack=kind.equals("resources")||kind.equals("shaders");long maxEntries=pack?100_000:8192,maxDirectory=pack?16L*1024*1024:4L*1024*1024;
  try(var input=new RandomAccessFile(file.toFile(),"r")){
   int n=(int)Math.min(input.length(),65557);byte[] tail=new byte[n];long start=input.length()-n;input.seek(start);input.readFully(tail);int end=-1;
   for(int i=n-22;i>=0;i--)if(u32(tail,i)==0x06054b50L&&i+22+u16(tail,i+20)==n){end=i;break;}
   require(end>=0,400,"Missing ZIP directory");
   require(u16(tail,end+4)==0&&u16(tail,end+6)==0&&u16(tail,end+8)==u16(tail,end+10),400,"Split ZIP archives are unsupported");
   long count=u16(tail,end+10),size=u32(tail,end+12),offset=u32(tail,end+16),boundary=start+end;
   byte[] location=new byte[20];if(boundary>=20){input.seek(boundary-20);input.readFully(location);}
   boolean locator=boundary>=20&&u32(location,0)==0x07064b50L;
   if(locator||count==65535||size==0xffffffffL||offset==0xffffffffL){
    require(pack&&locator,400,"Missing or unsupported ZIP64 directory");long locPosition=boundary-20;
    require(u32(location,4)==0&&u32(location,16)==1,400,"Split ZIP64 archives are unsupported");
    long record=u64(location,8);require(record<=locPosition-56,400,"Invalid ZIP64 record offset");
    byte[] fixed=new byte[56];input.seek(record);input.readFully(fixed);
    require(u32(fixed,0)==0x06064b50L,400,"Invalid ZIP64 record");long recordSize=u64(fixed,4);
    require(recordSize>=44&&recordSize<=65536&&recordSize==locPosition-record-12,400,"Invalid ZIP64 record size");
    require(u32(fixed,16)==0&&u32(fixed,20)==0,400,"Split ZIP64 archives are unsupported");
    long actualCount=u64(fixed,32),actualSize=u64(fixed,40),actualOffset=u64(fixed,48);
    require(u64(fixed,24)==actualCount&&(count==65535||count==actualCount)&&(size==0xffffffffL||size==actualSize)&&(offset==0xffffffffL||offset==actualOffset),400,"Inconsistent ZIP64 directory");
    count=actualCount;size=actualSize;offset=actualOffset;boundary=record;
   }
   require(count>0&&count<=maxEntries&&size<=maxDirectory&&offset<=boundary&&size<=boundary-offset,400,"ZIP directory limit exceeded or invalid offset");
   return count;
  }
 }
 static void inspect(Path file,String kind)throws IOException {
  if(kind.equals("litematica")||kind.equals("worldedit")){
   // Bounded gzip/NBT signature check only; no promise of mod/version schema compatibility.
   try(var in=new java.io.PushbackInputStream(Files.newInputStream(file),2)){int a=in.read(),b=in.read();require(a==31&&b==139||a==10,400,"Expected gzip or compound NBT schematic");if(a==31){in.unread(new byte[]{(byte)a,(byte)b});try(var gzip=new java.util.zip.GZIPInputStream(in)){require(gzip.read()==10,400,"Expected compound NBT schematic");}}}return;
  }
  long directoryEntries=directory(file,kind);
  try(var zip=new ZipFile(file.toFile())){
   require(zip.size()==directoryEntries,400,"Archive directory count mismatch");
   require(!kind.equals("resources")||zip.getEntry("pack.mcmeta")!=null,400,"Resource pack needs pack.mcmeta");
   require(!kind.equals("mods")||zip.getEntry("fabric.mod.json")!=null,400,"Expected a Fabric mod JAR");
   boolean shader=false;for(var entries=zip.entries();entries.hasMoreElements();){var e=entries.nextElement();String n=e.getName();require(n.length()<=512&&!n.startsWith("/")&&!n.contains("\\")&&Arrays.stream(n.split("/")).noneMatch(p->p.equals("..")),400,"Unsafe archive paths");shader|=n.startsWith("shaders/");}
   require(!kind.equals("shaders")||shader,400,"Shader pack needs a shaders directory");
  }catch(java.util.zip.ZipException invalid){throw new Refused(400,"Not a readable ZIP/JAR");}
 }
 private boolean managed(ProsperoLibrary.Instance instance,String name)throws Exception {
  for(var kind:ProsperoModrinth.Kind.values())for(var local:new ProsperoModrinth().local(library.game(instance),kind))if(local.filename().equals(name)&&!local.project().isEmpty())return true;return false;
 }
 List<Object> list(Path folder)throws IOException {
  var result=new ArrayList<Object>();if(!Files.exists(folder,LinkOption.NOFOLLOW_LINKS))return result;
  try(var files=Files.newDirectoryStream(folder)){for(Path f:files){require(result.size()<2048,409,"Too many files; use the launcher");if(Files.isRegularFile(f,LinkOption.NOFOLLOW_LINKS)&&!f.getFileName().toString().startsWith("."))result.add(Map.of("name",f.getFileName().toString(),"size",Files.size(f)));}}return result;
 }
 static void respond(OutputStream out,int code,String type,String body,String extra)throws IOException {
  respondBytes(out,code,type,body.getBytes(StandardCharsets.UTF_8),extra);
 }
 static void respondBytes(OutputStream out,int code,String type,byte[] b,String extra)throws IOException {
  String headers="HTTP/1.1 "+code+" Result\r\nContent-Type: "+type+"\r\nContent-Length: "+b.length+"\r\nConnection: close\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nReferrer-Policy: no-referrer\r\nContent-Security-Policy: default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'\r\n"+extra+"\r\n";
  out.write(headers.getBytes(StandardCharsets.US_ASCII));out.write(b);out.flush();
 }
 @Override public void close(){closed=true;pairing="";session="";expires=0;status=new Status("Stopped",List.of(),0);hosts=List.of();try{server.close();}catch(IOException ignored){}Socket socket=active;if(socket!=null)try{socket.close();}catch(IOException ignored){} }
 boolean stopped()throws InterruptedException{thread.join(6000);return !thread.isAlive();}
}
