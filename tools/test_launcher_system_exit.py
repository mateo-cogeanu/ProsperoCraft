#!/usr/bin/env python3
"""Real child-JVM System.exit observers and existing clean-session rejection gates."""
from pathlib import Path
import subprocess,tempfile
from host_toolchain import ROOT,java_home

def main():
 jdk=java_home()
 with tempfile.TemporaryDirectory(prefix='prospero-system-exit-')as folder:
  w=Path(folder)
  sources={
   'net/minecraft/client/Minecraft.java':'package net.minecraft.client;public class Minecraft{public static Minecraft instance=new Minecraft();public boolean running;public static Minecraft getInstance(){return instance;}public boolean isRunning(){return running;}}',
   'org/lwjgl/sdl/SDLInit.java':'package org.lwjgl.sdl;public class SDLInit{public static int live;public static int SDL_WasInit(int flags){return live;}}',
   'ExitCheck.java':r'''import java.nio.file.*;import java.io.*;
public class ExitCheck{
 public static void main(String[]a)throws Exception{
  Path logs=Path.of(a[0]);String mode=a[1];Files.createDirectories(logs);
  Files.writeString(logs.resolve("latest.log"),"[old/INFO]: Stopping!\n");
  ProsperoSession session=new ProsperoSession(logs);Thread owner=Thread.currentThread();
  try(var report=new PrintStream(Files.newOutputStream(logs.resolve("audit")));var exit=new ProsperoExit(
   ()->{if(owner.getContextClassLoader()!=ExitCheck.class.getClassLoader())throw new IllegalStateException("wrong loader");session.verifyCleanReturn(owner.getContextClassLoader());},
   ()->{if(mode.equals("arm-failure"))throw new IllegalStateException("PRIVATE_TEXT");try{Files.writeString(logs.resolve("armed"),"VERIFIED");}catch(IOException e){throw new RuntimeException(e);}},report)){
   if(mode.equals("removed"))return;
   if(!mode.equals("stale"))Files.writeString(logs.resolve("latest.log"),"[Render thread/INFO]: Stopping!\n",StandardOpenOption.APPEND);
   if(mode.equals("fatal"))Files.writeString(logs.resolve("latest.log"),"[Render thread/FATAL]: failed\n",StandardOpenOption.APPEND);
   if(mode.equals("running"))net.minecraft.client.Minecraft.instance.running=true;
   if(mode.equals("sdl"))org.lwjgl.sdl.SDLInit.live=32;
   if(mode.equals("missing"))net.minecraft.client.Minecraft.instance=null;
   System.exit(mode.equals("nonzero")?7:0);
  }
 }
}
'''}
  for name,source in sources.items():
   p=w/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
  subprocess.run([jdk/'bin/javac','--release','25','-d',w,ROOT/'client/launcher/java/ProsperoExit.java',ROOT/'client/launcher/java/ProsperoSession.java',*[w/name for name in sources]],check=True)
  for mode in ('clean','stale','fatal','running','sdl','missing','removed','arm-failure','nonzero'):
   logs=w/mode;result=subprocess.run([jdk/'bin/java','-cp',w,'ExitCheck',logs,mode],timeout=20)
   assert result.returncode==(7 if mode=='nonzero'else 0),mode
   assert (logs/'armed').exists()==(mode in ('clean','nonzero')),mode
   audit=(logs/'audit').read_text();assert 'PRIVATE_TEXT'not in audit
   if mode not in ('clean','nonzero','removed'):assert 'SYSTEM_EXIT_REJECTED'in audit,mode
   if mode=='removed':assert audit=='',audit
 print('PASS real System.exit child JVM: clean audit/arm, stale/fatal/running/live-SDL/null/arm-failure rejection, removed observer, bounded diagnostics; nonzero status preserved for native refusal')
if __name__=='__main__':main()
