/* SPDX-License-Identifier: GPL-3.0-or-later
 * Explicit host-only PS5 dispatch control, never packaged into the title.
 */
import java.lang.reflect.Field;
import sun.misc.Unsafe;
import org.lwjgl.system.Configuration;
import org.lwjgl.system.Library;
import org.lwjgl.system.MemoryUtil;
import org.lwjgl.system.Platform;
public final class ZinkHandoffHost25 {
 public static void main(String[] args)throws Throwable{
  System.load(args[0]);
  if(args[3].equals("resume")){System.setProperty("ps5.launcher.resume","true");ClientStartup25.main(new String[0]);if(ClientStartup25.normalQuit())throw new AssertionError("Resume did not run graphics");System.out.println("PASS184resume branch remains in modeled launcher without touching GL");return;}
  if(args[3].equals("reject")){try{ClientStartup25.main(new String[0]);throw new AssertionError("Rejected launcher handoff accepted");}catch(IllegalStateException expected){if(!"Native launcher display/device cleanup and UI join".equals(expected.getMessage()))throw expected;if(ClientStartup25.normalQuit())throw new AssertionError("Unsafe restart flag");System.out.println("PASS184rejected launcher barrier blocks GL and restart");return;}}
  Configuration.MEMORY_ALLOCATOR.set("system");Configuration.LIBRARY_NAME.set(args[1]);Configuration.GLFW_CHECK_THREAD0.set(false);
  System.load(args[1]);System.load(args[2]);Library.initialize();MemoryUtil.memBackend();
  Field f=Unsafe.class.getDeclaredField("theUnsafe");f.setAccessible(true);Unsafe u=(Unsafe)f.get(null);
  Field current=Platform.class.getDeclaredField("current");Object base=u.staticFieldBase(current);long offset=u.staticFieldOffset(current);Platform previous=Platform.get();
  u.putObjectVolatile(base,offset,Platform.PS5);
  try{ClientStartup25.main(new String[0]);if(!ClientStartup25.normalQuit())throw new AssertionError("Actual GL test failed cleanup");System.out.println("PASS184actual JVM GLFW/LWJGL Zink rendering/readback/guards/teardown; modeled launcher boundary, not PS5 handoff");}
  finally{u.putObjectVolatile(base,offset,previous);}
 }
}
