/* SPDX-License-Identifier: GPL-3.0-or-later */
package prosperocraft.lwjgl333;

import org.lwjgl.Version;
import org.lwjgl.system.*;
import org.lwjgl.glfw.GLFW;

/** Entirely owned by the matched333 game loader. No game class or callback hook. */
public final class Bootstrap {
 private static boolean configured;
 private static native int nativeInterfaceSize();
 private static native int nativeGetVersion();
 private static native void beginShutdown();
 public static synchronized void configure(){
  if(configured)return;
  if(Platform.get()!=Platform.PS5||!Version.getVersion().equals("3.3.3+5"))throw new LinkageError("Matched truthful PS5 LWJGL333 owner required");
  Configuration.MEMORY_ALLOCATOR.set("system");
  Configuration.LIBRARY_NAME.set("lwjgl333");
  Configuration.GLFW_LIBRARY_NAME.set("ps5glfw");
  Configuration.OPENAL_LIBRARY_NAME.set("ps5openal");
  Library.initialize();
  int version=nativeGetVersion();
  if((version!=0x00180000&&version!=0x00190000)||nativeInterfaceSize()!=236)
   throw new LinkageError("LWJGL333 native JNI table does not match the Java25 integration");
  // Separate group owns only its own native thread attachment/destructor state.
  Runtime.getRuntime().addShutdownHook(new Thread(Bootstrap::beginShutdown,"LWJGL333 native shutdown"));
  System.setProperty("ps5.opengl.provider","zink");
  GLFW.glfwInitHint(GLFW.GLFW_PLATFORM,GLFW.GLFW_PLATFORM_NULL);
  configured=true;
 }
 private Bootstrap(){}
}
