/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.File;
import java.io.PrintWriter;
import java.lang.management.ManagementFactory;
import java.lang.reflect.InvocationTargetException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/** Original-game bootstrap only; no authentication, game replacement or rendering. */
public final class HelloLts {
 private static native int nativeMultiply(int a,int b);
 private static PrintWriter log;
 private static void stage(String value) { log.println(value); log.flush(); }
 public static int run() throws Exception {
  Path root=Path.of(System.getProperty("ps5.mc17.testRoot","/download0"));
  try(PrintWriter output=new PrintWriter(Files.newBufferedWriter(root.resolve("mc120-java17-stages.log")))) {
   log=output;
   if(Runtime.version().feature()!=17)throw new AssertionError("Actual Java17 required");
        if (nativeMultiply(6, 7) != 42) throw new AssertionError("JNI arguments/result");
        long value = 0;
        for (int i = 0; i < 10000; i++) value += i;
        if (value != 49995000L) throw new AssertionError("Java arithmetic");
        if (!"PS5 \u03c0 \ud83c\udfae".equals(new String("PS5 \u03c0 \ud83c\udfae".toCharArray())))
            throw new AssertionError("UTF16 string");
        if (StrictMath.sin(0) != 0 || StrictMath.cos(0) != 1 || StrictMath.sqrt(144) != 12)
            throw new AssertionError("Original StrictMath natives");
        try {
            Integer.parseInt("expected exception");
            throw new AssertionError("Exception missing");
        } catch (NumberFormatException expected) { }
        final int[] worker = {0};
        Thread thread = new Thread(() -> worker[0] = nativeMultiply(17, 3), "Java17 probe worker");
        thread.start();
        thread.join(5000);
        if (thread.isAlive() || worker[0] != 51) throw new AssertionError("Java thread/JNI");

   stage("Java17 real runtime; modules: desktop beans, XML, logging, management, unsupported");
   Class.forName("java.beans.PropertyChangeEvent");Class.forName("javax.xml.parsers.DocumentBuilderFactory");
   Class.forName("sun.misc.Unsafe");
   if(ManagementFactory.getRuntimeMXBean().getVmName().isBlank())throw new AssertionError("VM management identity");
   stage("Actual management/native RuntimeMXBean identity passed");
   File folder=new File(System.getProperty("ps5.mc17.jars","/app0/assets/java17/extra"));
   File[] files=folder.listFiles((d,n)->n.endsWith(".jar"));
   if(files==null||files.length<2)throw new AssertionError("Verified publisher JAR directory missing");
   Arrays.sort(files);URL[] urls=new URL[files.length];
   for(int i=0;i<files.length;i++)urls[i]=files[i].toURI().toURL();
   // One coherent owner for the complete old binding, overlay and original game.
   try(URLClassLoader loader=new URLClassLoader(urls,ClassLoader.getPlatformClassLoader())) {
    ClassLoader previous=Thread.currentThread().getContextClassLoader();
    Thread.currentThread().setContextClassLoader(loader);
    try {
    if(!Boolean.getBoolean("ps5.mc17.hostEntryOnly")) {
     stage("Initialize truthful PS5 LWJGL331 with Java17 JNI table");
     loader.loadClass("prosperocraft.lwjgl331.Bootstrap").getMethod("configure").invoke(null);
     Class<?> memory=loader.loadClass("org.lwjgl.system.MemoryUtil");
     ByteBuffer buffer=(ByteBuffer)memory.getMethod("memAlloc",int.class).invoke(null,32);
     try { buffer.putLong(0,0x123456789abcdefL);if(buffer.getLong(0)!=0x123456789abcdefL)throw new AssertionError("Native memory roundtrip"); }
     finally { memory.getMethod("memFree",java.nio.Buffer.class).invoke(null,buffer); }
     stage("Actual331 native allocation/read/write/free passed");
    } else stage("HOST ONLY: native PS5 binding skipped explicitly");
    stage("Invoke unchanged Minecraft1.20 Main with no auth/game arguments");
    try { loader.loadClass("net.minecraft.client.main.Main").getMethod("main",String[].class).invoke(null,(Object)new String[0]);
     throw new AssertionError("Original argument gate unexpectedly returned");
    } catch(InvocationTargetException expected) {
     Throwable cause=expected.getCause();
     if(!cause.getClass().getName().equals("joptsimple.MissingRequiredOptionsException"))throw expected;
     stage("Original Minecraft1.20 parser reached required accessToken/version gate, as intended");
    }
    stage("PASS original1.20 bootstrap; no menu/world/rendering claim");
    } finally { Thread.currentThread().setContextClassLoader(previous); }
   }
   return 17;
  }
 }
 private HelloLts() { }
}
