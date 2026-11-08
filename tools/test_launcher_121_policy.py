#!/usr/bin/env python3
"""Injected121 Vanilla gates and binding-owner isolation; no game/network inputs."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

from host_toolchain import ROOT, java_home, launcher_classpath


def main():
    jdk, cp = java_home(), launcher_classpath()
    with tempfile.TemporaryDirectory(prefix='launcher121-') as temporary:
        work = Path(temporary)
        source = work / 'Policy121.java'
        source.write_text(r'''
import java.nio.file.*;import java.net.*;import java.util.*;
public class Policy121 {
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 public static void main(String[]args)throws Exception{
  Path work=Path.of(args[0]);
  check(!ProsperoLauncher.observeDiagnostics("26.1.2","fabric"),"world observer disabled by default");
  System.setProperty("ps5.world2612Observer","true");
  check(ProsperoLauncher.observeDiagnostics("26.1.2","fabric"),"selected Fabric world observer");
  check(ProsperoLauncher.observeDiagnostics("1.21.4","fabric"),"terrain observer scope");
  check(ProsperoLauncher.observeDiagnostics("1.21.2","fabric"),"Sodium freeze observer scope");
  check(!ProsperoLauncher.observeDiagnostics("1.21.2","vanilla"),"Sodium freeze Vanilla excluded");
  check(!ProsperoLauncher.observeDiagnostics("1.21.4","vanilla"),"terrain observer Vanilla excluded");
  for(String v:new String[]{"26.1","26.1.1","26.2","26.3","1.21.11"})check(!ProsperoLauncher.observeDiagnostics(v,"fabric"),"observer version scope "+v);
  check(!ProsperoLauncher.observeDiagnostics("26.1.2","vanilla"),"observer loader scope");
  System.clearProperty("ps5.world2612Observer");
  for(String good:new String[]{"1.21","1.21.1","1.21.11","1.21.99"})check(ProsperoVersions.valid(good),"121valid "+good);
  for(String bad:new String[]{"1.20.6","1.21-pre1","1.21.11-rc1","1.21.","1.21.100","1.21.-1","1.21/escape","1.21.1\n"})check(!ProsperoVersions.valid(bad),"121invalid "+bad);
  check(!ProsperoVersions.valid(null),"null id");
  for(int i=0;i<10;i++)for(String tail:new String[]{"",".1","-snapshot-1","..","_abc","/bad","!bad"}){
   String id="26."+i+tail;check(ProsperoVersions.valid(id)==id.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}"),"26regex unchanged");
  }
  check(ProsperoVersions.catalog("1.21.11","release",false),"release catalog");
  check(!ProsperoVersions.catalog("1.21.11","snapshot",true),"121snapshots excluded");
  check(!ProsperoVersions.catalog("1.21-pre1","snapshot",true),"121pres excluded");
  check(!Prospero121.available("1.21.11","vanilla"),"default no gate");
  Files.writeString(work.resolve("prosperocraft-channel.txt"),"temp_gametest\n");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-1.21.11-zink-v1\n");
  check(Prospero121.available("1.21.11","vanilla"),"explicit Vanilla candidate");
  for(String version:Prospero121.RELEASES){
   check(Prospero121.available(version,"vanilla")==version.equals("1.21.11"),"per-release gate");
   check(!Prospero121.available(version,"fabric"),"Fabric deferred");
   check(!ProsperoGraphics.vulkan(version,"GLFW"),"no Vulkan argument");
   check(!ProsperoLauncher.launchable(version,"fabric"),"no Fabric launch");
   check(Prospero121.shutdownAccessors(version).length==3,"mapped shutdown table");
  }
  check(ProsperoGraphics.glfw("1.21.11")&&ProsperoGraphics.zink("1.21.11","vanilla"),"121 GLFW/Zink");
  check(ProsperoLauncher.launchable("1.21.11","vanilla"),"Vanilla development launch");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-1.21.10-1.21.11-zink-v2\n");
  for(String version:Prospero121.RELEASES){check(Prospero121.available(version,"vanilla")==Set.of("1.21.10","1.21.11").contains(version),"208two explicit releases");check(!Prospero121.available(version,"fabric"),"208noFabric");}
  check(ProsperoGraphics.glfw("1.21.10")&&ProsperoGraphics.zink("1.21.10","vanilla"),"12110Zink");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-1.21.9-1.21.11-zink-v3\n");
  check(ProsperoLauncher.supported("1.21.9","vanilla")&&!ProsperoLauncher.developmentTest("1.21.9","vanilla"),"1219 promoted Vanilla launch");
  for(String version:Set.of("1.21.10","1.21.11")){
   check(ProsperoLauncher.supported(version,"vanilla")&&!ProsperoLauncher.developmentTest(version,"vanilla"),"promoted Vanilla release");
   check(ProsperoGraphics.zink(version,"vanilla")&&!ProsperoLauncher.launchable(version,"fabric"),"unchanged renderer and Fabric gate");
  }
  var cards=new ProsperoLibrary(work.resolve("cards"));cards.settings().showIntro=false;cards.save();var normal=cards.add("Normal","26.3",1);cards.ready(normal,true);cards.add("Stable","1.21.11",1);cards.add("Vanilla 1.21.9","1.21.9",1);cards.add("Soon","1.21.1",1);var cardModel=new ProsperoLauncher(new ProsperoAuth(),work.resolve("cards"),url->{throw new AssertionError("network");});String[] shown=cardModel.tick(0);check(shown[35].isEmpty()&&shown[39].isEmpty()&&shown[43].isEmpty()&&shown[47].equals("COMING SOON"),"promoted releases have no badge; unsupported release remains Coming Soon");
  var oldHardware=new ProsperoInstall.Receipt();oldHardware.classpath.add("libraries/com/github/oshi/oshi-core/6.6.5/oshi-core-6.6.5.jar");check(ProsperoInstall.hardwarePort(oldHardware).equals("oshi-6.6.5-ps5-platform.jar"),"exact665provider");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-1.21-1.21.11-zink-v4\n");
  for(String version:Prospero121.RELEASES){
   boolean released=Set.of("1.21.9","1.21.10","1.21.11").contains(version);
   check(ProsperoLauncher.launchable(version,"vanilla")&&ProsperoGraphics.glfw(version)&&ProsperoGraphics.zink(version,"vanilla"),"all Vanilla versions use Zink/GLFW");
   check(ProsperoLauncher.developmentTest(version,"vanilla")==!released,"only newly enabled versions show DEV TEST");
   check(!ProsperoLauncher.launchable(version,"fabric"),"Fabric stays deferred");
  }
  var candidateCards=new ProsperoLauncher(new ProsperoAuth(),work.resolve("cards"),url->{throw new AssertionError("network");}).tick(0);
  check(candidateCards[43].isEmpty()&&candidateCards[47].equals("DEV TEST"),"only newly enabled instance card has DEV TEST badge");
  check(!ProsperoLauncher.launchable("1.21.12","vanilla"),"future releases stay blocked");
  oldHardware.version="1.21.3";
  oldHardware.classpath.clear();
  oldHardware.classpath.add("libraries/com/github/oshi/oshi-core/6.4.10/oshi-core-6.4.10.jar");
  check("oshi-6.4.10-ps5-platform.jar".equals(ProsperoInstall.hardwarePort(oldHardware)),"exact6410provider");
  oldHardware.version="26.3";
  check(ProsperoInstall.hardwarePort(oldHardware)==null,"no6410 provider on 26.x");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-fabric-1.21-1.21.11-zink-v5\n");
  for(String version:Prospero121.RELEASES){
   ProsperoFabric.game(version);
   check(ProsperoLauncher.supported(version,"vanilla")&&!ProsperoLauncher.developmentTest(version,"vanilla"),"console-tested Vanilla normal status");
   check(ProsperoLauncher.launchable(version,"fabric")&&ProsperoLauncher.developmentTest(version,"fabric"),"Fabric DEV TEST");
   check(ProsperoGraphics.zink(version,"fabric")&&!ProsperoGraphics.vulkan(version,"GLFW"),"Fabric uses Zink and no Vulkan argument");
   check(!ProsperoLauncher.launchable(version,"quilt"),"other loaders stay gated");
  }
  for(String bad:new String[]{"1.21.12","1.21.1-pre1","1.20.6"}){
   try{ProsperoFabric.game(bad);throw new AssertionError("unsupported Fabric version");}
   catch(java.io.IOException expected){}
  }
  Files.writeString(work.resolve("prosperocraft-sodium-lwjgl-test.txt"),"sodium-lwjgl-version-test-v1\n");
  check(!ProsperoGraphics.configureSodiumLwjglTest("1.21.11","fabric"),"no 3.4 version-check override for 3.3.3");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"bad-token\n");
  check(!ProsperoLauncher.launchable("1.21.11","vanilla"),"bad-token refusal");
  Files.writeString(work.resolve("prosperocraft-zink.txt"),"all-loaders-26.1-zink-v2\n");
  for(String version:new String[]{"26.1","26.1.1","26.1.2"})for(String loader:new String[]{"vanilla","fabric"})
   check(ProsperoLauncher.launchable(version,loader)&&ProsperoGraphics.zink(version,loader),"existing26Zink unchanged");
  var fabricCache=work.toRealPath().resolve("fabric-policy");
  var fabric=new ProsperoFabric(fabricCache);
  var profile=new ProsperoFabric.Receipt();profile.game="1.21.3";profile.loader="0.20.1";profile.main=ProsperoFabric.MAIN;
  String newAsm="fabric/libraries/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar";
  Path newPath=fabricCache.resolve(newAsm);Files.createDirectories(newPath.getParent());Files.writeString(newPath,"new ASM fixture");
  profile.files.add(new ProsperoFabric.Entry(newAsm,new ProsperoDownloads.Pin("https://maven.fabricmc.net/fixture.jar","SHA-1",ProsperoDownloads.hash(newPath,"SHA-1"),Files.size(newPath))));
  Path oldAsm=fabricCache.resolve("libraries/org/ow2/asm/asm/9.3/asm-9.3.jar");
  Path other=fabricCache.resolve("libraries/org/ow2/asm/other/9.3/other-9.3.jar");
  try(var vanilla=new URLClassLoader(new URL[]{oldAsm.toUri().toURL(),other.toUri().toURL()},Policy121.class.getClassLoader());
      var merged=fabric.loader(profile,vanilla)){
   check(List.of(merged.getURLs()).equals(List.of(newPath.toUri().toURL(),other.toUri().toURL())),"Fabric takes precedence only for matching Maven artifacts");
  }
  var badgePath=work.resolve("experimental-cards");
  var badges=new ProsperoLibrary(badgePath);badges.settings().showIntro=false;badges.save();
  badges.add("Fabric","26.1",1,"fabric");badges.add("Vanilla","26.1",1);
  badges.add("Fabric patch","26.1.1",1,"fabric");badges.add("Fabric newer","26.3",1,"fabric");
  String[] badgeFields=new ProsperoLauncher(new ProsperoAuth(),badgePath,url->{throw new AssertionError("network");}).tick(0);
  check(badgeFields[35].isEmpty()&&badgeFields[39].isEmpty()&&badgeFields[43].isEmpty()&&badgeFields[47].isEmpty(),"26.x cards have no experimental badges");

  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-fabric-1.21-1.21.11-zink-v6\n");
  Set<String> promoted=Set.of("1.21.7","1.21.8","1.21.9","1.21.10","1.21.11");
  for(String version:Prospero121.RELEASES){
   boolean stable=promoted.contains(version);
   check(ProsperoLauncher.supported(version,"fabric")==stable,"requested Fabric promotion");
   check(ProsperoLauncher.experimental(version,"fabric")==!stable,"remaining Fabric experimental");
   check(ProsperoLauncher.launchable(version,"fabric"),"all implemented Fabric still launchable");
   check(ProsperoLauncher.supported(version,"vanilla")&&!ProsperoLauncher.experimental(version,"vanilla"),"Vanilla status retained");
  }
  Path publishedCards=work.resolve("release-cards");var published=new ProsperoLibrary(publishedCards);
  published.settings().showIntro=false;published.save();
  for(String version:List.of("1.21.11","1.21.10","1.21.9","1.21.8","1.21.7","1.21.6","1.21.1","1.21"))
   published.add(version,version,1,"fabric");
  var releaseModel=new ProsperoLauncher(new ProsperoAuth(),publishedCards,url->{throw new AssertionError("network");});
  String[] releaseCards=releaseModel.tick(0);
  for(int i=0;i<8;i++)check(releaseCards[35+i*4].equals(i<5?"":"EXPERIMENTAL"),"exact requested card labels");
  var sessionField=ProsperoLauncher.class.getDeclaredField("session");sessionField.setAccessible(true);
  sessionField.set(releaseModel,new ProsperoAuth.Session("Fixture","fixture-id","fixture-token",System.currentTimeMillis()+3_600_000));
  var detailField=ProsperoLauncher.class.getDeclaredField("detail");detailField.setAccessible(true);
  var cachedField=ProsperoLauncher.class.getDeclaredField("cached");cachedField.setAccessible(true);
  for(var instance:published.instances()){
   instance.ready=true;detailField.set(releaseModel,instance);cachedField.set(releaseModel,null);
   check(releaseModel.tick(0)[6].equals(promoted.contains(instance.version)?"PLAY":"EXPERIMENTAL - PLAY"),"detail launch status agrees with cards");
  }
  check(!ProsperoLauncher.experimental("1.21.12","fabric")&&!ProsperoLauncher.launchable("1.21.12","fabric"),"future Fabric still blocked");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-fabric-1.21-1.21.11-zink-v7\n");
  for(String version:Prospero121.RELEASES){
   for(String loader:List.of("fabric","vanilla"))
    check(ProsperoLauncher.supported(version,loader)&&!ProsperoLauncher.experimental(version,loader)
         &&!ProsperoLauncher.developmentTest(version,loader),"released "+version+" "+loader);
   check(!ProsperoLauncher.launchable(version,"neoforge"),"unimplemented loader stays blocked");
  }
  check(!ProsperoLauncher.launchable("1.21.12","fabric"),"future Fabric stays blocked");
  for(var instance:published.instances()){
   detailField.set(releaseModel,instance);cachedField.set(releaseModel,null);
   String[] released=releaseModel.tick(0);
   check(released[6].equals("PLAY")&&released[69].equals("SUPPORTED"),"promoted Fabric detail");
   for(int i=0;i<8;i++)check(released[35+i*4].isEmpty(),"promoted Fabric card");
  }
  Files.writeString(work.resolve("prosperocraft-121.txt"),"vanilla-fabric-1.21-1.21.11-zink-v5\n");

  check(ProsperoLauncher.supported("26.2")&&ProsperoLauncher.supported("26.3"),"existing26support");
  check(ProsperoGraphics.vulkan("26.2","GLFW")&&ProsperoGraphics.vulkan("26.3","SDL"),"existing26Vulkan");
  for(int i=1;i<=6;i++)check(ProsperoLauncher.supported("26.4-snapshot-"+i),"snapshot unchanged");
  check(!ProsperoLauncher.supported("26.4-snapshot-7"),"future snapshot blocked");
  try(var parent=new URLClassLoader(new URL[]{work.resolve("parent").toUri().toURL()},ClassLoader.getPlatformClassLoader());
      var game=new ProsperoGameLoader(new URL[]{work.resolve("child").toUri().toURL()},parent,true);
      var legacy=new ProsperoGameLoader(new URL[]{work.resolve("child").toUri().toURL()},parent)){
   Class<?> own=game.loadClass("org.lwjgl.Fixture");check(own.getClassLoader()==game&&own.getMethod("version").invoke(null).equals("333"),"entire333 owner");
   check(game.getResource("org/lwjgl/Fixture.class").toString().contains("/child/"),"Knot sees same 333 source as class owner");
   check(game.getResource("org/lwjgl/ParentOnly.class")==null,"resource lookup cannot leak 343");
   check(game.getResource("org/lwjgl/sdl/Fixture.class").toString().contains("/parent/"),"SDL resource stays parent");
   check(legacy.loadClass("org.lwjgl.Fixture")==parent.loadClass("org.lwjgl.Fixture"),"legacy parent unchanged");
   check(game.loadClass("org.lwjgl.sdl.Fixture")==parent.loadClass("org.lwjgl.sdl.Fixture"),"SDL stays parent");
   try{game.loadClass("org.lwjgl.ParentOnly");throw new AssertionError("343package fallback");}catch(ClassNotFoundException expected){}
   check(game.loadClass("prosperocraft.lwjgl333.Probe").getClassLoader()==game,"bootstrap owner");
  }
  ClassLoader bindings=new ClassLoader(Policy121.class.getClassLoader()){
   @Override public Class<?> loadClass(String name)throws ClassNotFoundException{
    if(name.startsWith("org.lwjgl.sdl."))throw new ClassNotFoundException("SDL belongs to launcher");
    return super.loadClass(name);
   }
  };
  Path logs=work.resolve("mapped-logs");var session=new ProsperoSession(logs,new String[]{"MappedGame","V","v"});
  try{session.verifyCleanReturn(bindings);throw new AssertionError("stale/missing stopping accepted");}catch(ProsperoSession.NotClean expected){}
  Files.writeString(logs.resolve("latest.log"),"[Render thread/INFO]: Stopping!\n",StandardOpenOption.APPEND);
  session.verifyCleanReturn(bindings);
  MappedGame.running=true;try{session.verifyCleanReturn(bindings);throw new AssertionError("running accepted");}catch(ProsperoSession.NotClean expected){}MappedGame.running=false;
  org.lwjgl.sdl.SDLInit.live=32;try{session.verifyCleanReturn(bindings);throw new AssertionError("live SDL accepted");}catch(ProsperoSession.NotClean expected){}org.lwjgl.sdl.SDLInit.live=0;
  Files.writeString(logs.resolve("latest.log"),"[Render thread/FATAL]: crash\n",StandardOpenOption.APPEND);
  try{session.verifyCleanReturn(bindings);throw new AssertionError("fatal accepted");}catch(ProsperoSession.NotClean expected){}
  System.out.println("PASS121 bounded releases/catalog, exact historical gates, candidate Fabric and Maven artifact precedence, no Vulkan, finite shutdown names, unchanged26decisions and coherent333/343/SDL class owners without fallback");
 }
}
''')
        for owner, version in (('parent', '343'), ('child', '333')):
            directory = work / (owner + '-source')
            file = directory / 'org/lwjgl/Fixture.java'
            file.parent.mkdir(parents=True)
            file.write_text('package org.lwjgl;public class Fixture{public static String version(){return "' + version + '";}}')
            files = [file]
            if owner == 'parent':
                for name in ('org/lwjgl/ParentOnly.java', 'org/lwjgl/sdl/Fixture.java'):
                    p = directory / name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text('package ' + ('.'.join(Path(name).parts[:-1])) + ';public class ' + p.stem + '{}')
                    files.append(p)
            else:
                p = directory / 'prosperocraft/lwjgl333/Probe.java'
                p.parent.mkdir(parents=True)
                p.write_text('package prosperocraft.lwjgl333;public class Probe{}')
                files.append(p)
            subprocess.run([str(jdk / 'bin/javac'), '-d', str(work / owner), *map(str, files)], check=True)
        mapped = work / 'MappedGame.java'
        mapped.write_text('public class MappedGame{public static boolean running;private static final MappedGame INSTANCE=new MappedGame();public static MappedGame V(){return INSTANCE;}public boolean v(){return running;}}')
        sdl = work / 'org/lwjgl/sdl/SDLInit.java'
        sdl.parent.mkdir(parents=True)
        sdl.write_text('package org.lwjgl.sdl;public class SDLInit{public static int live;public static int SDL_WasInit(int ignored){return live;}}')
        subprocess.run([str(jdk / 'bin/javac'), '--release', '25', '-cp', cp, '-d', str(work), str(mapped), str(sdl),
                        *map(str, (ROOT / 'client/launcher/java').glob('*.java')), str(source)], check=True)
        subprocess.run([str(jdk / 'bin/java'), '-ea', '-cp', str(work) + os.pathsep + cp,
                        'Policy121', str(work)], check=True)


if __name__ == '__main__':
    main()
