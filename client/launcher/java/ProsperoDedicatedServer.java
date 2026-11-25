import java.io.*;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.BooleanSupplier;
import java.util.zip.ZipFile;

/** Verified Vanilla bundles and one dedicated world per release. */
final class ProsperoDedicatedServer {
 record Release(String version,String sha1,long size){}
 static final List<Release> RELEASES=List.of(
  new Release("26.3","33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c",62294556),
  new Release("26.2","823e2250d24b3ddac457a60c92a6a941943fcd6a",60894273),
  new Release("26.1.2","97ccd4c0ed3f81bbb7bfacddd1090b0c56f9bc51",60417480),
  new Release("26.1.1","49c8195703ad0ba4f0a4efbccfd85a4a8ca57431",60417481),
  new Release("26.1","3872a7f07a1a595e651aef8b058dfc2bb3772f46",60417588));
 static final String EULA="https://www.minecraft.net/eula";
 static final int PORT=25565;
 private static final String CONSENT="# Accepted from the ProsperoCraft Servers tab\neula=true\n";

 static Path base(Path fallback){
  String selected=System.getenv("PROSPERO_STORAGE_BASE");
  return selected==null?fallback:Path.of(selected);
 }
 static Path home(Path base,Release release){return base.resolve("servers").resolve(release.version());}
 static Release release(String version)throws IOException {
  return RELEASES.stream().filter(r->r.version().equals(version)).findFirst()
      .orElseThrow(()->new IOException("Choose a supported Vanilla server release."));
 }
 static void prepare(Path home,Release release,boolean accept,ProsperoInstall.Source source,
                     ProsperoInstall.Progress progress,BooleanSupplier cancel)throws Exception {
  Path consent=home.resolve("eula.txt");
  ProsperoDownloads.noLinks(consent);
  if(!accept&&!accepted(home))throw new IOException("Read and accept the Minecraft EULA before starting.");
  Files.createDirectories(home);
  String url="https://piston-data.mojang.com/v1/objects/"+release.sha1()+"/server.jar";
  var pin=new ProsperoInstall.FilePin("server.jar",url,release.sha1(),release.size());
  ProsperoInstall installer=source==null?new ProsperoInstall(home):new ProsperoInstall(home,source);
  long[] total={0};
  progress.update("Downloading Vanilla "+release.version(),0,release.size());
  installer.obtain(pin,cancel,false,n->progress.update("Downloading Vanilla "+release.version(),total[0]+=n,release.size()));
  ProsperoInstall.active(cancel);
  if(accept&&!accepted(home))ProsperoDependencies.writeCompatibility(consent,CONSENT);
 }
 static boolean accepted(Path home)throws IOException {
  Path file=home.resolve("eula.txt");
  ProsperoDownloads.noLinks(file);
  if(!Files.isRegularFile(file)||Files.size(file)>4096)return false;
  var consent=new Properties();
  try(var in=Files.newInputStream(file)){consent.load(in);}
  return "true".equals(consent.getProperty("eula"));
 }
 static void defaults(Path home)throws IOException {
  Path file=home.resolve("server.properties");
  ProsperoDownloads.noLinks(file);
  if(!Files.exists(file))Files.writeString(file,"motd=ProsperoCraft Vanilla Server\nserver-port="+PORT+
      "\nonline-mode=true\nview-distance=6\nsimulation-distance=4\nmax-players=8\n"+
      "enable-rcon=false\nenable-query=false\nmanagement-server-enabled=false\nlevel-name=world\n",
      StandardOpenOption.CREATE_NEW);
 }
 /** UTF-8 like the dedicated server, with its ISO-8859-1 fallback for older files. */
 static Properties loadProperties(Path file)throws IOException {
  var options=new Properties();
  try(var in=Files.newBufferedReader(file,StandardCharsets.UTF_8)){options.load(in);}
  catch(java.nio.charset.CharacterCodingException legacy){options.clear();try(var in=Files.newBufferedReader(file,StandardCharsets.ISO_8859_1)){options.load(in);}}
  return options;
 }
 /** Browser-editable server.properties keys, validated; applied on the next start. */
 static final List<String> EDITABLE=List.of("motd","max-players","difficulty","gamemode","view-distance","simulation-distance","pvp","white-list");
 static String validSetting(String key,String value){
  String v=value==null?"":value.strip();
  boolean ok=switch(key){
   case "motd"->v.length()<=59&&v.codePoints().allMatch(c->c>=32&&c!=127&&c!=0xa7&&!Character.isISOControl(c));
   case "max-players"->v.matches("[0-9]{1,2}")&&Integer.parseInt(v)>=1&&Integer.parseInt(v)<=20;
   case "view-distance","simulation-distance"->v.matches("[0-9]{1,2}")&&Integer.parseInt(v)>=3&&Integer.parseInt(v)<=12;
   case "difficulty"->List.of("peaceful","easy","normal","hard").contains(v);
   case "gamemode"->List.of("survival","creative","adventure","spectator").contains(v);
   case "pvp","white-list"->v.equals("true")||v.equals("false");
   default->false;
  };
  if(!ok)throw new IllegalArgumentException("Invalid value for "+key);
  return v;
 }
 static Map<String,String> settings(Path home)throws IOException {
  Path file=home.resolve("server.properties");ProsperoDownloads.noLinks(file);
  var options=Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)&&Files.size(file)<=65536?loadProperties(file):new Properties();
  var result=new LinkedHashMap<String,String>();
  var fallback=Map.of("motd","ProsperoCraft Vanilla Server","max-players","8","difficulty","easy","gamemode","survival","view-distance","6","simulation-distance","4","pvp","true","white-list","false");
  for(String key:EDITABLE){String value=options.getProperty(key,fallback.get(key));try{result.put(key,validSetting(key,value));}catch(IllegalArgumentException invalid){result.put(key,fallback.get(key));}}
  return result;
 }
 static void saveSettings(Path home,Map<String,String> changes)throws IOException {
  if(changes.isEmpty()||changes.size()>EDITABLE.size())throw new IllegalArgumentException("No server settings to save");
  var valid=new LinkedHashMap<String,String>();
  for(var e:changes.entrySet()){if(!EDITABLE.contains(e.getKey()))throw new IllegalArgumentException("Unsupported server setting");valid.put(e.getKey(),validSetting(e.getKey(),e.getValue()));}
  Files.createDirectories(home);defaults(home);
  Path file=home.resolve("server.properties");
  if(Files.size(file)>65536)throw new IOException("Server settings file is too large");
  var options=loadProperties(file);
  valid.forEach(options::setProperty);
  var text=new StringWriter();options.store(text,"ProsperoCraft Vanilla Server");
  ProsperoDependencies.writeCompatibility(file,text.toString());
 }
 /** Browser console accepts a small set of standard administration commands only. */
 static String validCommand(String raw){
  String command=raw==null?"":raw.strip();
  if(command.startsWith("/"))command=command.substring(1);
  if(command.isEmpty()||command.length()>200||!command.chars().allMatch(c->c>=32&&c<127))throw new IllegalArgumentException("Enter a short command using plain characters");
  String name="[A-Za-z0-9_]{1,16}";
  boolean ok=command.matches("say .{1,180}")||command.matches("list( uuids)?")||command.matches("(op|deop|pardon) "+name)
   ||command.matches("whitelist (on|off|list|reload)")||command.matches("whitelist (add|remove) "+name)
   ||command.matches("(kick|ban) "+name+"( .{1,120})?")||command.matches("time set (day|noon|night|midnight|[0-9]{1,6})")
   ||command.matches("weather (clear|rain|thunder)")||command.matches("difficulty (peaceful|easy|normal|hard)")
   ||command.matches("save-all( flush)?")||command.matches("seed");
  if(!ok)throw new IllegalArgumentException("Command not allowed here. Try say, list, op, deop, whitelist, kick, ban, pardon, time, weather, difficulty or save-all");
  return command;
 }
 static URLClassLoader open(Path home,Release release)throws Exception {
  Path bundle=home.resolve("server.jar");
  ProsperoDownloads.noLinks(bundle);
  if(!accepted(home)||!Files.isRegularFile(bundle)||Files.size(bundle)!=release.size()
      ||!ProsperoInstall.hash(bundle).equals(release.sha1()))throw new IOException("Server files or EULA consent are missing. Start from the Servers tab.");
  Path libs=home.resolve("runtime");
  ProsperoDownloads.noLinks(libs);
  Files.createDirectories(libs);
  var urls=new ArrayList<URL>();
  try(var zip=new ZipFile(bundle.toFile())){
   for(String list:List.of("versions","libraries")){
    var entry=zip.getEntry("META-INF/"+list+".list");
    if(entry==null||entry.getSize()<1||entry.getSize()>65536)throw new IOException("Invalid Vanilla bundle inventory.");
    String[] rows;
    try(var in=zip.getInputStream(entry)){rows=new String(in.readNBytes(65537),StandardCharsets.UTF_8).lines().toArray(String[]::new);}
    if(rows.length==0||rows.length>256||(list.equals("versions")&&rows.length!=1))throw new IOException("Invalid Vanilla bundle inventory count.");
    for(String line:rows){
     String[] fields=line.split("\t",-1);
     if(fields.length!=3||!fields[0].matches("[a-f0-9]{64}")||!fields[2].endsWith(".jar")
         ||(list.equals("versions")&&!release.version().equals(fields[1])))throw new IOException("Invalid Vanilla bundle entry.");
     Path jar=libs.resolve(fields[0]+".jar");
     ProsperoDownloads.noLinks(jar);
     if(!Files.isRegularFile(jar)||!ProsperoDownloads.hash(jar,"SHA-256").equals(fields[0])){
      var payload=zip.getEntry("META-INF/"+list+"/"+fields[2]);
      if(payload==null||payload.getSize()<1||payload.getSize()>128L*1024*1024)throw new IOException("Invalid bundled JAR length.");
      Path tmp=Files.createTempFile(libs,"extract-",".part");
      try{
       try(var in=zip.getInputStream(payload);var out=Files.newOutputStream(tmp)){
        var digest=MessageDigest.getInstance("SHA-256");
        long size=new java.security.DigestInputStream(in,digest).transferTo(out);
        if(size!=payload.getSize()||!HexFormat.of().formatHex(digest.digest()).equals(fields[0]))throw new IOException("Bundled JAR checksum mismatch.");
       }
       Files.move(tmp,jar,StandardCopyOption.REPLACE_EXISTING);
      }finally{Files.deleteIfExists(tmp);}
     }
     urls.add(jar.toUri().toURL());
    }
   }
  }
  return new URLClassLoader(urls.toArray(URL[]::new),ClassLoader.getPlatformClassLoader());
 }

 static final class Session {
  enum Status {STARTING,RUNNING,STOPPING,STOPPED,FAILED}
  volatile Status status=Status.STARTING;
  volatile boolean stopRequested;
  private volatile boolean ready,saveFailed;
  private volatile String address="";
  private final ArrayDeque<String> console=new ArrayDeque<>();private long consoleSerial;
  private final Set<String> players=new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
  private final java.util.concurrent.ConcurrentLinkedQueue<String> pending=new java.util.concurrent.ConcurrentLinkedQueue<>();
  private volatile long onlineSince;private volatile int maxPlayers=8;
  static final int CONSOLE_LINES=50,CONSOLE_WIDTH=300;
  private static final java.util.regex.Pattern JOINED=java.util.regex.Pattern.compile("\\[Server thread/INFO\\]: ([A-Za-z0-9_]{1,16}) (joined|left) the game$");
  synchronized List<String> console(){return List.copyOf(console);}
  synchronized long consoleSerial(){return consoleSerial;}
  synchronized List<String> players(){return List.copyOf(players);}
  int maxPlayers(){return maxPlayers;}
  long uptimeSeconds(){long since=onlineSince;return status==Status.RUNNING&&since>0?Math.max(0,(System.currentTimeMillis()-since)/1000):0;}
  void command(String raw){
   if(status!=Status.RUNNING)throw new IllegalStateException("Commands are available while the server is online");
   if(pending.size()>=16)throw new IllegalStateException("Too many commands waiting. Try again in a moment");
   pending.add(validCommand(raw));
  }
  synchronized void observe(String text){
   String shown=text.length()>CONSOLE_WIDTH?text.substring(0,CONSOLE_WIDTH)+"...":text;
   console.addLast(shown);consoleSerial++;while(console.size()>CONSOLE_LINES)console.removeFirst();
   var m=JOINED.matcher(text);if(m.find()){if(m.group(2).equals("joined"))players.add(m.group(1));else players.remove(m.group(1));}
  }
  private final Path home;
  private final Release release;
  Session(Path home,Release release){this.home=home;this.release=release;}
  String address(){return address;}
  void requestStop(){if(status==Status.RUNNING)stopRequested=true;}
  boolean finished(){return status==Status.STOPPED||status==Status.FAILED;}
  void start(){
   var group=new ThreadGroup("Prospero dedicated server");
   var thread=new Thread(group,()->run(group),"Prospero server control");
   thread.start();
  }
  private static Thread serverThread(ThreadGroup group)throws IOException {
   Thread[] threads=new Thread[1024];
   int count=group.enumerate(threads,true);
   if(count==threads.length)throw new IOException("Server thread inventory is full.");
   for(int n=0;n<count;n++)if(threads[n].getName().equals("Server thread")&&threads[n].isAlive())return threads[n];
   return null;
  }
  private void run(ThreadGroup group) {
   PrintStream output=System.out;
   InputStream originalInput=System.in;
   PrintStream originalError=System.err;
   if(!Path.of("").toAbsolutePath().normalize().equals(home.toAbsolutePath().normalize())){
    output.println("PS5_SERVER refused: incorrect working directory");
    status=Status.FAILED;
    return;
   }
   Status completion;
   try(var game=open(home,release);var input=new PipedInputStream();
       var commands=new PipedOutputStream(input);
       var observed=new PrintStream(new OutputStream(){
        final ByteArrayOutputStream line=new ByteArrayOutputStream();
        @Override public synchronized void write(int c){
         output.write(c);
         if(c!='\n'){if(line.size()<4096)line.write(c);return;}
         String text=line.toString(StandardCharsets.UTF_8);
         line.reset();
         observe(text);
         if(text.contains("Server thread/INFO")&&text.contains("Done (")&&text.contains("For help"))ready=true;
         if(text.contains("Server thread/ERROR"))saveFailed=true;
         output.flush();
        }
       },true,StandardCharsets.UTF_8)){
    Files.createDirectories(home);
    for(String filename:List.of("world","ops.json","whitelist.json","banned-ips.json","banned-players.json","usercache.json","logs"))
     ProsperoDownloads.noLinks(home.resolve(filename));
    defaults(home);
    List<String> ips=ProsperoWeb.localAddresses();
    Path settings=home.resolve("server.properties");
    if(ips.isEmpty()||Files.size(settings)>65536)throw new IOException("A local IPv4 address and valid server settings are required.");
    var options=loadProperties(settings);
    String ip=ips.getFirst();address=ip+":"+PORT;
    try{maxPlayers=Math.clamp(Integer.parseInt(options.getProperty("max-players","8").strip()),1,1000);}catch(NumberFormatException ignored){maxPlayers=8;}
    options.setProperty("server-ip",ip);
    options.setProperty("server-port",Integer.toString(PORT));
    options.setProperty("online-mode","true");
    options.setProperty("enable-rcon","false");
    options.setProperty("enable-query","false");
    options.setProperty("management-server-enabled","false");
    options.setProperty("level-name","world");
    var properties=new StringWriter();options.store(properties,"ProsperoCraft Vanilla Server");
    ProsperoDependencies.writeCompatibility(settings,properties.toString());
    System.setIn(input);System.setOut(observed);System.setErr(observed);
    Thread.currentThread().setContextClassLoader(game);
    Class.forName("net.minecraft.server.Main",true,game).getMethod("main",String[].class)
       .invoke(null,(Object)new String[]{"--nogui","--universe",home.toString(),"--world","world"});
    Thread server=serverThread(group);
    if(server==null)throw new IOException("The dedicated server did not start.");
    while(server.isAlive()){
     if(ready&&status==Status.STARTING){onlineSince=System.currentTimeMillis();status=Status.RUNNING;}
     for(String queued;status==Status.RUNNING&&!stopRequested&&(queued=pending.poll())!=null;){commands.write((queued+"\n").getBytes(StandardCharsets.US_ASCII));commands.flush();}
     if(stopRequested&&status==Status.RUNNING){
      commands.write("stop\n".getBytes(StandardCharsets.US_ASCII));commands.flush();
      status=Status.STOPPING;
     }
     server.join(150);
    }
    if(status!=Status.STOPPING||saveFailed||!Files.isRegularFile(home.resolve("world/level.dat")))
     throw new IOException("The server stopped without a verified save.");
    completion=Status.STOPPED;
   } catch(Exception|LinkageError failure){
    output.println("PS5_SERVER failed: "+failure.getClass().getSimpleName());
    // Never signal that the UI can replace the process while its server is alive.
    try{Thread owner=serverThread(group);if(owner!=null)owner.join();}
    catch(InterruptedException interrupted){Thread.currentThread().interrupt();return;}
    catch(IOException unavailable){return;}
    completion=Status.FAILED;
   } finally {
    System.setIn(originalInput);System.setOut(output);System.setErr(originalError);
   }
   status=completion;
  }
 }
}
