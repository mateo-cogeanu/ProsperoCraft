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
   'org/lwjgl/sdl/SDLInit.java':'package org.lwjgl.sdl;public class SDLInit{public static volatile int live;public static int SDL_WasInit(int flags){return live;}}',
   'ExitCheck.java':r'''import java.nio.file.*;import java.io.*;
public class ExitCheck{
 static final java.util.concurrent.CountDownLatch auditEntered=new java.util.concurrent.CountDownLatch(1);
 public static void main(String[]a)throws Exception{
  Path logs=Path.of(a[0]);String mode=a[1];Files.createDirectories(logs);
  Files.writeString(logs.resolve("latest.log"),"[old/INFO]: Stopping!\n");
  ProsperoSession session=new ProsperoSession(logs);Thread owner=Thread.currentThread();
  try(var report=new PrintStream(Files.newOutputStream(logs.resolve("audit")));var exit=new ProsperoExit(
   ()->{if(owner.getContextClassLoader()!=ExitCheck.class.getClassLoader())throw new IllegalStateException("wrong loader");session.awaitCleanReturn(owner.getContextClassLoader(),mode.equals("delayed-sdl")?2000:300,stage->{try{Files.writeString(logs.resolve("audit-state"),stage);}catch(IOException failure){throw new RuntimeException(failure);}});},
   ()->{if(mode.equals("arm-failure"))throw new IllegalStateException("PRIVATE_TEXT");try{Files.writeString(logs.resolve("armed"),"VERIFIED");}catch(IOException e){throw new RuntimeException(e);}},report,stage->{if(stage.equals("PS5_SESSION SYSTEM_EXIT_AUDIT_ENTER"))auditEntered.countDown();if(mode.equals("checkpoint-failure"))throw new IllegalStateException("PRIVATE_TEXT");try{Files.writeString(logs.resolve("stages"),stage+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}catch(IOException e){throw new RuntimeException(e);}})){
   if(mode.equals("removed"))return;
   if(!mode.equals("stale"))Files.writeString(logs.resolve("latest.log"),"[Render thread/INFO]: Stopping!\n",StandardOpenOption.APPEND);
   if(mode.equals("fatal"))Files.writeString(logs.resolve("latest.log"),"[Render thread/FATAL]: failed\n",StandardOpenOption.APPEND);
   if(mode.equals("running"))net.minecraft.client.Minecraft.instance.running=true;
   if(mode.equals("sdl"))org.lwjgl.sdl.SDLInit.live=32;
   if(mode.equals("residual")){System.setProperty("ps5.finalSdlExitCleanup","true");org.lwjgl.sdl.SDLInit.live=0x6210;}
   if(mode.equals("video")){System.setProperty("ps5.finalSdlExitCleanup","true");org.lwjgl.sdl.SDLInit.live=0x6230;}
   if(mode.equals("unknown")){System.setProperty("ps5.finalSdlExitCleanup","true");org.lwjgl.sdl.SDLInit.live=0x10000;}

   if(mode.equals("delayed-sdl")){
    org.lwjgl.sdl.SDLInit.live=32;
    Runtime.getRuntime().addShutdownHook(new Thread(()->{try{auditEntered.await();Thread.sleep(120);}catch(InterruptedException failure){throw new AssertionError(failure);}org.lwjgl.sdl.SDLInit.live=0;},"Concurrent real cleanup hook"));
   }
   if(mode.equals("missing"))net.minecraft.client.Minecraft.instance=null;
   System.exit(mode.equals("nonzero")?7:0);
  }
 }
}
'''}
  for name,source in sources.items():
   p=w/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
  subprocess.run([jdk/'bin/javac','--release','25','-d',w,ROOT/'client/launcher/java/ProsperoExit.java',ROOT/'client/launcher/java/ProsperoSession.java',*[w/name for name in sources]],check=True)
  for mode in ('clean','stale','fatal','running','sdl','missing','removed','arm-failure','checkpoint-failure','nonzero','delayed-sdl','residual','video','unknown'):
   logs=w/mode;result=subprocess.run([jdk/'bin/java','-cp',w,'ExitCheck',logs,mode],timeout=20)
   assert result.returncode==(7 if mode=='nonzero'else 0),mode
   assert (logs/'armed').exists()==(mode in ('clean','nonzero','delayed-sdl')),mode
   audit=(logs/'audit').read_text();assert 'PRIVATE_TEXT'not in audit
   if mode in ('clean','nonzero','delayed-sdl'):assert (logs/'audit-state').read_text()=='PS5_SESSION AUDIT all clean',mode
   if mode=='residual':assert 'sdlMask=6210'in (logs/'audit-state').read_text()
   if mode=='sdl':assert 'sdlMask=20' in (logs/'audit-state').read_text()
   if (logs/'audit-state').exists():assert 'PRIVATE_TEXT'not in (logs/'audit-state').read_text()
   if mode not in ('clean','nonzero','delayed-sdl','removed'):assert 'SYSTEM_EXIT_REJECTED'in audit,mode
   if mode=='removed':assert audit=='',audit
   stages=logs/'stages'
   if mode in ('removed','checkpoint-failure'):assert not stages.exists(),mode
   else:
    expected=['PS5_SESSION SYSTEM_EXIT_AUDIT_ENTER','PS5_SESSION SYSTEM_EXIT_AUDIT_'+('ARMED'if mode in ('clean','nonzero','delayed-sdl')else'REJECTED')]
    assert stages.read_text().splitlines()==expected,(mode,stages.read_text())
 print('PASS real System.exit child JVM: clean audit/arm, stale/fatal/running/live-SDL/null/arm-failure rejection, removed observer, bounded diagnostics and genuine concurrent delayed-cleanup hook; nonzero status preserved for native refusal')
if __name__=='__main__':main()
