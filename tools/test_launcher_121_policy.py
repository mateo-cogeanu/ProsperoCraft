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
  var cards=new ProsperoLibrary(work.resolve("cards"));cards.settings().showIntro=false;cards.save();var normal=cards.add("Normal","26.3",1);cards.ready(normal,true);cards.add("Dev","1.21.11",1);cards.add("Soon","1.21.1",1);var cardModel=new ProsperoLauncher(new ProsperoAuth(),work.resolve("cards"),url->{throw new AssertionError("network");});String[] shown=cardModel.tick(0);check(shown[35].isEmpty()&&shown[39].equals("DEV TEST")&&shown[43].equals("COMING SOON"),"only dev/coming-soon card badges");
  var oldHardware=new ProsperoInstall.Receipt();oldHardware.classpath.add("libraries/com/github/oshi/oshi-core/6.6.5/oshi-core-6.6.5.jar");check(ProsperoInstall.hardwarePort(oldHardware).equals("oshi-6.6.5-ps5-platform.jar"),"exact665provider");
  Files.writeString(work.resolve("prosperocraft-121.txt"),"bad-token\n");
  check(!ProsperoLauncher.launchable("1.21.11","vanilla"),"bad-token refusal");
  Files.writeString(work.resolve("prosperocraft-zink.txt"),"all-loaders-26.1-zink-v2\n");
  for(String version:new String[]{"26.1","26.1.1","26.1.2"})for(String loader:new String[]{"vanilla","fabric"})
   check(ProsperoLauncher.launchable(version,loader)&&ProsperoGraphics.zink(version,loader),"existing26Zink unchanged");
  check(ProsperoLauncher.supported("26.2")&&ProsperoLauncher.supported("26.3"),"existing26support");
  check(ProsperoGraphics.vulkan("26.2","GLFW")&&ProsperoGraphics.vulkan("26.3","SDL"),"existing26Vulkan");
  for(int i=1;i<=6;i++)check(ProsperoLauncher.supported("26.4-snapshot-"+i),"snapshot unchanged");
  check(!ProsperoLauncher.supported("26.4-snapshot-7"),"future snapshot blocked");
  try(var parent=new URLClassLoader(new URL[]{work.resolve("parent").toUri().toURL()},ClassLoader.getPlatformClassLoader());
      var game=new ProsperoGameLoader(new URL[]{work.resolve("child").toUri().toURL()},parent,true);
      var legacy=new ProsperoGameLoader(new URL[]{work.resolve("child").toUri().toURL()},parent)){
   Class<?> own=game.loadClass("org.lwjgl.Fixture");check(own.getClassLoader()==game&&own.getMethod("version").invoke(null).equals("333"),"entire333 owner");
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
  System.out.println("PASS121 bounded releases/catalog, exact Vanilla resource gates, all Fabric deferred, no Vulkan, finite shutdown names, unchanged26decisions and coherent333/343/SDL class owners without fallback");
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
