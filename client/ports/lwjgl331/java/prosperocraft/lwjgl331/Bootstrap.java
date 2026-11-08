/* SPDX-License-Identifier: GPL-3.0-or-later */
package prosperocraft.lwjgl331;

import org.lwjgl.Version;
import org.lwjgl.system.*;
import org.lwjgl.glfw.GLFW;

/** Entirely owned by the matched331 game loader. No game class or callback hook. */
public final class Bootstrap {
 private static boolean configured;
 private static native int nativeInterfaceSize();
 private static native int nativeGetVersion();
 private static native void beginShutdown();
 public static synchronized void configure(){
  if(configured)return;
  if(Platform.get()!=Platform.PS5||!Version.getVersion().equals("3.3.1 build 7"))throw new LinkageError("Matched truthful PS5 LWJGL331 owner required");
  Configuration.MEMORY_ALLOCATOR.set("system");
  Configuration.LIBRARY_NAME.set("lwjgl331");
  Configuration.GLFW_LIBRARY_NAME.set("ps5glfw");
  Configuration.OPENAL_LIBRARY_NAME.set("ps5openal");
  Library.initialize();
  RuntimeAbi.validate(System.getProperty("java.specification.version"), nativeGetVersion(), nativeInterfaceSize());
  // Separate group owns only its own native thread attachment/destructor state.
  Runtime.getRuntime().addShutdownHook(new Thread(Bootstrap::beginShutdown,"LWJGL331 native shutdown"));
  System.setProperty("ps5.opengl.provider","zink");
  configured=true;
 }
 private Bootstrap(){}
}
