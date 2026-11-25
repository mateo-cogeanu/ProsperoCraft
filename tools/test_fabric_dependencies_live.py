#!/usr/bin/env python3
"""Real pinned Vitrail/Sodium/Fabric API bytes; no game invocation or class rewriting."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');w=ROOT/'build/dependencies108-live';w.mkdir(exist_ok=True)
source=r'''
import java.nio.file.*;import java.io.*;import java.util.*;
public class LiveDependencies {
 public static void main(String[]args)throws Exception{Path root=Path.of(args[0]),game=root.resolve("instance/game");Files.createDirectories(game);var fabric=new ProsperoFabric(root.resolve("cache"));var f=fabric.install("26.3",(m,d,t)->{},()->false);
  try(var versions=fabric.dependencies("26.3")){
   byte[] pinned=new ProsperoDownloads().bytes(ProsperoModrinth.API+"version/Q3nKuPKJ",1024*1024,()->false);
   var api=new ProsperoModrinth(new ProsperoDownloads(url->{if(url.startsWith(ProsperoModrinth.API+"project/oSIKhgz3/version?"))return new ByteArrayInputStream(("["+new String(pinned,java.nio.charset.StandardCharsets.UTF_8)+"]").getBytes(java.nio.charset.StandardCharsets.UTF_8));return ProsperoDownloads.network(url);}));
   if(api.local(game,ProsperoModrinth.Kind.MOD).isEmpty()){if(api.queue(game).stream().noneMatch(q->q.project().equals("oSIKhgz3")))api.toggle(game,new ProsperoModrinth.Selection("oSIKhgz3","Vitrail0.13.0",ProsperoModrinth.Kind.MOD));api.downloadAll(game,"26.3","fabric",(m,d,t)->System.out.println(m),()->false,x->{},versions);}
   if(api.installed(game).files.stream().noneMatch(x->x.project().equals("AANobbMI")&&x.version().equals("bAZQdGpg")))throw new AssertionError("Vitrail Sodium pin missing; use a fresh test directory");
   if(api.installed(game).files.stream().noneMatch(x->x.project().equals("P7dR8mSH")))throw new AssertionError("real Fabric API was not auto-installed");
   var jars=api.local(game,ProsperoModrinth.Kind.MOD).stream().map(x->game.resolve("mods").resolve(x.filename())).toList();if(!ProsperoDependencies.missing(jars,"26.3",versions).isEmpty())throw new AssertionError("real JAR dependencies unresolved");
   ProsperoDependencies.verifyGraphics(jars,false,"26.3");
   var item=api.local(game,ProsperoModrinth.Kind.MOD).stream().filter(x->x.project().equals("P7dR8mSH")).findFirst().orElseThrow();api.uninstall(game,item);api.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,false);
   if(api.local(game,ProsperoModrinth.Kind.MOD).stream().noneMatch(x->x.project().equals("P7dR8mSH")))throw new AssertionError("real existing-instance repair failed");
   api.repair(game,"26.3","fabric",versions,(m,d,t)->{},()->false,true);
   for(boolean reverse:List.of(false,true)){
    Path irisGame=root.resolve("iris-"+reverse+"/game");
    if(Files.exists(irisGame.getParent()))try(var walk=Files.walk(irisGame.getParent())){for(var path:walk.sorted(Comparator.reverseOrder()).toList())Files.delete(path);}
    Files.createDirectories(irisGame);var iris=new ProsperoModrinth(new ProsperoDownloads(url->{
     String pin=url.startsWith(ProsperoModrinth.API+"project/YL57xq9U/version?")?"vTN4NRGW":url.startsWith(ProsperoModrinth.API+"project/AANobbMI/version?")?"g6ju16VJ":url.startsWith(ProsperoModrinth.API+"project/P7dR8mSH/version?")?"EQKgpeKu":"";
     if(pin.isEmpty())return ProsperoDownloads.network(url);
     byte[] metadata=new ProsperoDownloads().bytes(ProsperoModrinth.API+"version/"+pin,1024*1024,()->false);
     return new ByteArrayInputStream(("["+new String(metadata,java.nio.charset.StandardCharsets.UTF_8)+"]").getBytes(java.nio.charset.StandardCharsets.UTF_8));
    }));
    for(String project:reverse?List.of("AANobbMI","P7dR8mSH","YL57xq9U"):List.of("P7dR8mSH","YL57xq9U","AANobbMI"))iris.toggle(irisGame,new ProsperoModrinth.Selection(project,project,ProsperoModrinth.Kind.MOD));
    iris.downloadAll(irisGame,"26.3","fabric",(m,d,t)->System.out.println(m),()->false,x->{},versions);
    var sodium=iris.installed(irisGame).files.stream().filter(x->x.project().equals("AANobbMI")).findFirst().orElseThrow();
    if(!sodium.version().equals("bAZQdGpg")||iris.installed(irisGame).files.size()!=3||!iris.queue(irisGame).isEmpty())throw new AssertionError("real Iris exact Sodium pin not honored");
    var irisJars=iris.local(irisGame,ProsperoModrinth.Kind.MOD).stream().map(x->irisGame.resolve("mods").resolve(x.filename())).toList();
    if(!ProsperoDependencies.missing(irisJars,"26.3",versions).isEmpty())throw new AssertionError("real Iris dependency manifests unresolved");
    try{ProsperoDependencies.verifyVulkan(irisJars);throw new AssertionError("real Iris accepted for Vulkan launch");}catch(IOException expected){if(!expected.getMessage().contains("OpenGL"))throw expected;}

   }
   Path upgradeGame=root.resolve("vitrail301-preserve/game");
   if(Files.exists(upgradeGame.getParent()))try(var walk=Files.walk(upgradeGame.getParent())){for(var path:walk.sorted(Comparator.reverseOrder()).toList())Files.delete(path);}
   Files.createDirectories(upgradeGame);Files.writeString(upgradeGame.resolve("world-marker"),"KEEP");
   boolean[] oldSelection={true};
   var upgrade=new ProsperoModrinth(new ProsperoDownloads(url->{
    String pin=url.startsWith(ProsperoModrinth.API+"project/AANobbMI/version?")?(oldSelection[0]?"bAZQdGpg":"6etTPjD5"):url.startsWith(ProsperoModrinth.API+"project/oSIKhgz3/version?")?"Q3nKuPKJ":url.startsWith(ProsperoModrinth.API+"project/P7dR8mSH/version?")?"EQKgpeKu":"";
    if(pin.isEmpty())return ProsperoDownloads.network(url);byte[] metadata=new ProsperoDownloads().bytes(ProsperoModrinth.API+"version/"+pin,1024*1024,()->false);
    return new ByteArrayInputStream(("["+new String(metadata,java.nio.charset.StandardCharsets.UTF_8)+"]").getBytes(java.nio.charset.StandardCharsets.UTF_8));
   }));
   upgrade.toggle(upgradeGame,new ProsperoModrinth.Selection("AANobbMI","Sodium 0.9.2",ProsperoModrinth.Kind.MOD));upgrade.downloadAll(upgradeGame,"26.3","fabric",(m,d,t)->System.out.println(m),()->false,x->{},versions);
   String oldSodium=upgrade.installed(upgradeGame).files.stream().filter(x->x.project().equals("AANobbMI")).findFirst().orElseThrow().filename();
   oldSelection[0]=false;
   upgrade.toggle(upgradeGame,new ProsperoModrinth.Selection("oSIKhgz3","Vitrail",ProsperoModrinth.Kind.MOD));upgrade.downloadAll(upgradeGame,"26.3","fabric",(m,d,t)->System.out.println(m),()->false,x->{},versions);
   if(!Files.exists(upgradeGame.resolve("mods/"+oldSodium))||upgrade.installed(upgradeGame).files.stream().noneMatch(x->x.project().equals("AANobbMI")&&x.version().equals("bAZQdGpg"))||upgrade.installed(upgradeGame).files.size()!=3||!Files.readString(upgradeGame.resolve("world-marker")).equals("KEEP"))throw new AssertionError("real Vitrail required Sodium pin was not retained");
   var upgradeJars=upgrade.local(upgradeGame,ProsperoModrinth.Kind.MOD).stream().map(x->upgradeGame.resolve("mods").resolve(x.filename())).toList();if(!ProsperoDependencies.missing(upgradeJars,"26.3",versions).isEmpty())throw new AssertionError("real upgraded manifests incompatible");ProsperoDependencies.verifyVulkan(upgradeJars);
   System.out.println("PASS real Vitrail required-dependency resolution preserves installed Sodium0.9.2;API added,world preserved,all original hashes and upstream predicates verified");
   System.out.println("PASS real Iris1.11.7 plus separately queued Sodium0.9.3beta and FabricAPI selects required Sodium0.9.2 in both queue orders; verified original bytes and upstream Fabric predicates; no PS5 rendering claim");
   System.out.println("PASS real pinned Vitrail0.13.0/Sodium/Fabric API verified downloads,upstream0.20.1predicates,nested required module discovery,API auto-install and existing-instance repair;official JARs untouched,no game execution");
  }
 }
}
'''
(w/'LiveDependencies.java').write_text(source);cp=':'.join(str(ROOT/'.tools/client'/r['file'])for r in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts'])
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'LiveDependencies.java')],check=True)
subprocess.run([str(JDK/'bin/java'),'-Xverify:all','-cp',str(w)+':'+cp,'LiveDependencies',str(w/'data-vitrail-pin')],check=True,timeout=180)
