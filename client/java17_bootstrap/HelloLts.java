/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.PrintWriter;
import java.lang.management.ManagementFactory;
import java.lang.reflect.InvocationTargetException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

/** Original-game bootstrap only; no authentication, game replacement or rendering. */
public final class HelloLts {
 private static native void nativeStage(int value);
 private static native int nativeMultiply(int a,int b);
 private static PrintWriter log;
 private static void stage(String value) { log.println(value); log.flush(); }
 // Only report bounded code locations. Exception messages and source paths stay out of the log.
 private static void reportMainFailure(Throwable failure) {
  for (int depth = 0; failure != null && depth < 5; depth++) {
   StackTraceElement[] frames = failure.getStackTrace();
   for (int i = 0; i < Math.min(frames.length, 8); i++) {
    StackTraceElement frame = frames[i];
    String owner = frame.getClassName();
    String method = frame.getMethodName();
    if (owner.matches("[A-Za-z0-9_.$]{1,160}") && method.matches("[A-Za-z0-9_$<>]{1,80}"))
     stage("Main failure depth " + depth + " frame " + i + ": " + owner + "." + method
         + " line " + frame.getLineNumber());
   }
   failure = failure.getCause();
  }
 }
 private static void verifyGraphics(ClassLoader loader) throws ReflectiveOperationException {
  Class<?> glfw = loader.loadClass("org.lwjgl.glfw.GLFW");
  stage("Graphics: initialize resident GLFW");
  if (!(boolean) glfw.getMethod("glfwInit").invoke(null))
   throw new IllegalStateException("GLFW initialization failed");
  long window = 0;
  try {
   Class<?> gl = loader.loadClass("org.lwjgl.opengl.GL");
   var hint = glfw.getMethod("glfwWindowHint", int.class, int.class);
   hint.invoke(null, 0x00022002, 3); // GLFW_CONTEXT_VERSION_MAJOR
   hint.invoke(null, 0x00022003, 3); // GLFW_CONTEXT_VERSION_MINOR
   hint.invoke(null, 0x00022008, 0x00032001); // GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE
   stage("Graphics: create GLFW window");
   window = (long) glfw.getMethod("glfwCreateWindow", int.class, int.class, CharSequence.class,
       long.class, long.class).invoke(null, 1280, 720, "ProsperoCraft Java 17 graphics test", 0L, 0L);
   if (window == 0) throw new IllegalStateException("GLFW window creation failed");
   glfw.getMethod("glfwMakeContextCurrent", long.class).invoke(null, window);
   gl.getMethod("createCapabilities").invoke(null);
   Class<?> gl11 = loader.loadClass("org.lwjgl.opengl.GL11C");
   String renderer = (String) gl11.getMethod("glGetString", int.class).invoke(null, 0x1F01);
   if (renderer == null || !renderer.toLowerCase(java.util.Locale.ROOT).contains("zink"))
    throw new IllegalStateException("Unexpected renderer");
   stage("Graphics: Zink context confirmed");
   var color = gl11.getMethod("glClearColor", float.class, float.class, float.class, float.class);
   var clear = gl11.getMethod("glClear", int.class);
   var error = gl11.getMethod("glGetError");
   var swap = glfw.getMethod("glfwSwapBuffers", long.class);
   var glfwError = glfw.getMethod("nglfwGetError", long.class);
   var poll = glfw.getMethod("glfwPollEvents");
   glfw.getMethod("glfwSwapInterval", int.class).invoke(null, 1);
   for (int channel = 0; channel < 3; channel++) {
    long start = System.nanoTime();
    do {
     poll.invoke(null);
     color.invoke(null, channel == 0 ? 0.75f : 0.05f, channel == 1 ? 0.75f : 0.05f,
                  channel == 2 ? 0.75f : 0.05f, 1f);
     clear.invoke(null, 0x4000);
     if ((int) error.invoke(null) != 0) throw new IllegalStateException("OpenGL clear failed");
     swap.invoke(null, window);
     if ((int) glfwError.invoke(null, 0L) != 0) throw new IllegalStateException("GLFW frame error");
    } while (System.nanoTime() - start < 1_000_000_000L);
   }
   gl11.getMethod("glFinish").invoke(null);
   if ((int) error.invoke(null) != 0) throw new IllegalStateException("OpenGL finish failed");
   stage("Graphics: submitted red, green and blue frames");
  } finally {
   try {
    if (window != 0) {
     glfw.getMethod("glfwMakeContextCurrent", long.class).invoke(null, 0L);
     loader.loadClass("org.lwjgl.opengl.GL")
       .getMethod("setCapabilities", loader.loadClass("org.lwjgl.opengl.GLCapabilities"))
       .invoke(null, (Object) null);
     glfw.getMethod("glfwDestroyWindow", long.class).invoke(null, window);
    }
   } finally {
    glfw.getMethod("glfwTerminate").invoke(null);
   }
  }
  stage("Graphics: GLFW teardown completed");
 }
 public static int run() throws Exception {
  nativeStage(0);
  nativeStage(1);
  Path root=Path.of(System.getProperty("ps5.mc17.testRoot","/download0"));
  nativeStage(2);
  try(PrintWriter output=new PrintWriter(Files.newBufferedWriter(root.resolve("mc120-java17-stages.log")))) {
   log=output;nativeStage(3);
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

   nativeStage(4);
   stage("Java17 real runtime; modules: desktop beans, XML, logging, management, unsupported");
   Class.forName("java.beans.PropertyChangeEvent");Class.forName("javax.xml.parsers.DocumentBuilderFactory");
   Class.forName("sun.misc.Unsafe");
   nativeStage(5);
   if(ManagementFactory.getRuntimeMXBean().getVmName().isBlank())throw new AssertionError("VM management identity");
   nativeStage(6);
   stage("Actual management/native RuntimeMXBean identity passed");
   nativeStage(10);
   Path folder=Path.of(System.getProperty("ps5.mc17.jars","/app0/assets/java17/extra"));
   java.util.List<String> names=Files.readAllLines(folder.resolve("classpath.list"));
   if(names.size()<2||names.size()>128)throw new AssertionError("Invalid verified classpath count");
   java.util.HashSet<String> unique=new java.util.HashSet<>();
   URL[] urls=new URL[names.size()];
   for(int i=0;i<names.size();i++){
    String name=names.get(i);
    if(!name.matches("[0-9]{3}-[A-Za-z0-9_.-]+\\.jar")||!unique.add(name))
     throw new AssertionError("Invalid verified classpath entry");
    urls[i]=new URL("file","",folder.toAbsolutePath().toString()+"/"+name);
   }
   nativeStage(11);
   // One coherent owner for the complete old binding, overlay and original game.
   nativeStage(12);
   try(URLClassLoader loader=new URLClassLoader(urls,ClassLoader.getPlatformClassLoader())) {
    nativeStage(13);
    ClassLoader previous=Thread.currentThread().getContextClassLoader();
    Thread.currentThread().setContextClassLoader(loader);
    try {
    if(!Boolean.getBoolean("ps5.mc17.hostEntryOnly")) {
     nativeStage(7);
     stage("Initialize truthful PS5 LWJGL331 with Java17 JNI table");
     loader.loadClass("prosperocraft.lwjgl331.Bootstrap").getMethod("configure").invoke(null);
     Class<?> memory=loader.loadClass("org.lwjgl.system.MemoryUtil");
     ByteBuffer buffer=(ByteBuffer)memory.getMethod("memAlloc",int.class).invoke(null,32);
     try { buffer.putLong(0,0x123456789abcdefL);if(buffer.getLong(0)!=0x123456789abcdefL)throw new AssertionError("Native memory roundtrip"); }
     finally { memory.getMethod("memFree",java.nio.Buffer.class).invoke(null,buffer); }
     nativeStage(8);
     stage("Actual331 native allocation/read/write/free passed");
    } else stage("HOST ONLY: native PS5 binding skipped explicitly");
    nativeStage(9);
    stage("Invoke unchanged Minecraft1.20 Main with no auth/game arguments");
    try {
     Class<?> main = Class.forName("net.minecraft.client.main.Main", true, loader);
     nativeStage(14);
     main.getMethod("main", String[].class).invoke(null, (Object) new String[0]);
     throw new AssertionError("Original argument gate unexpectedly returned");
    } catch (InvocationTargetException invocation) {
     Throwable cause = invocation.getCause();
     if (cause == null || !cause.getClass().getName().equals("joptsimple.MissingRequiredOptionsException")) {
      reportMainFailure(invocation);
      throw invocation;
     }
     stage("Original Minecraft1.20 parser reached required accessToken/version gate, as intended");
    } catch (ReflectiveOperationException | LinkageError failure) {
     reportMainFailure(failure);
     throw failure;
    }
    if (Boolean.getBoolean("ps5.mc17.graphicsProbe")) {
     try {
      verifyGraphics(loader);
     } catch (ReflectiveOperationException | RuntimeException | LinkageError failure) {
      reportMainFailure(failure);
      throw failure;
     }
    }
    stage("PASS original1.20 bootstrap; no menu/world/rendering claim");
    } finally { Thread.currentThread().setContextClassLoader(previous); }
   }
   return 17;
  }
 }
 private HelloLts() { }
}
