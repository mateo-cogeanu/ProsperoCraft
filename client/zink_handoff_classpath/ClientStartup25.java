/* SPDX-License-Identifier: GPL-3.0-or-later
 * Diagnostic launcher mailbox page and actual resident GLFW/LWJGL GL workload.
 * No original Minecraft class or account/install policy is replaced.
 */
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL;
import org.lwjgl.opengl.GL33C;
import org.lwjgl.system.Configuration;
import org.lwjgl.system.MemoryUtil;
public final class ClientStartup25 {
 public static native void checkpoint(String text);
 public static native void nativeSnapshot(long elapsedMillis,int phase);
 public static native boolean launcherMenu();
 public static native String[] cpuInformation();
 private static boolean normalQuit;
 public static boolean normalQuit(){return normalQuit;}
 public static String[] launcherTick(int buttons){
  boolean resumed=Boolean.getBoolean("ps5.launcher.resume");
  String[] fields=new String[111];Arrays.fill(fields,"");
  fields[0]="Zink JVM handoff";fields[2]=resumed?"Stage2b PASS: fresh launcher process returned":"Press X to close launcher and run real JVM/Zink presentation";
  fields[5]="Native graphics diagnostic";fields[6]=resumed?"STAGE2B PASS":"RUN HANDOFF";
  fields[7]="No Minecraft or account access; test only";fields[8]=resumed?"STAGE2B PASS":"READY";
  fields[9]="0";fields[10]=!resumed&&(buttons&0x4000)!=0?"LAUNCH":"WAIT";
  fields[11]="0";fields[12]="0";fields[13]="1";fields[14]="0";fields[28]="GRID";
  fields[30]="ON";fields[32]=resumed?"Stage2b PASS":"Run Zink handoff";fields[33]="JVM + GLFW + LWJGL";fields[34]="0";fields[35]=resumed?"RETURNED":"TEST";
  fields[79]="OFF";fields[104]="0";return fields;
 }
 private static void check(boolean value,String label){if(!value)throw new IllegalStateException(label);}
 public static void main(String[] args){
  if(Boolean.getBoolean("ps5.launcher.resume")){
   checkpoint("ZINK185 STAGE2B PASS: fresh process native launcher visible and new JVM active after verified test teardown");
   check(!launcherMenu(),"Resumed diagnostic must remain on its result page");return;
  }
  check(launcherMenu(),"Native launcher display/device cleanup and UI join");
  checkpoint("ZINK185 native launcher display/device closed and UI thread joined; actual JVM GL test begins");
  Configuration.MEMORY_ALLOCATOR.set("system");
  System.setProperty("ps5.opengl.provider","zink");
  Configuration.GLFW_LIBRARY_NAME.set("ps5glfw");
  Configuration.VULKAN_LIBRARY_NAME.set("ps5clientgpu");
  GLFW.glfwInitHint(GLFW.GLFW_PLATFORM,GLFW.GLFW_PLATFORM_NULL);
  try(var provider=new org.lwjgl.system.ps5.PS5Library("ps5clientgpu")){
   long address=provider.getFunctionAddress("vkGetInstanceProcAddr");check(address!=0,"Actual resident Vulkan loader");
   long configure=GLFW.getLibrary().getFunctionAddress("glfwInitVulkanLoader");check(configure!=0,"Actual GLFW loader configuration");
   org.lwjgl.system.JNI.invokePV(address,configure);
  }
  final int[] error={0};var callback=GLFW.glfwSetErrorCallback((code,text)->{error[0]=code;checkpoint("ZINK185 GLFW error code="+Integer.toHexString(code));});
  check(GLFW.glfwInit(),"Actual GLFW init");long window=0;boolean clean=false;
  try{
   GLFW.glfwDefaultWindowHints();GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR,3);GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR,3);
   GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE,GLFW.GLFW_OPENGL_CORE_PROFILE);GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_FORWARD_COMPAT,GLFW.GLFW_TRUE);
   var mode=GLFW.glfwGetVideoMode(GLFW.glfwGetPrimaryMonitor());check(mode!=null,"Actual display mode");
   window=GLFW.glfwCreateWindow(mode.width(),mode.height(),"ProsperoCraft Zink185",0,0);check(window!=0,"Actual GL window");
   GLFW.glfwMakeContextCurrent(window);GL.createCapabilities();GLFW.glfwSwapInterval(1);
   String renderer=GL33C.glGetString(GL33C.GL_RENDERER);check(renderer!=null&&renderer.contains("zink"),"Actual Zink renderer");
   checkpoint("ZINK185 actual GL capabilities created; renderer="+renderer);
   long started=System.nanoTime();int frames=0;
   try(var stack=org.lwjgl.system.MemoryStack.stackPush()){
    var width=stack.mallocInt(1);var height=stack.mallocInt(1);
    while(System.nanoTime()-started<6_000_000_000L){
     GLFW.glfwPollEvents();GLFW.glfwGetFramebufferSize(window,width,height);check(width.get(0)>0&&height.get(0)>0,"Framebuffer size");
     float phase=frames==0?0f:(System.nanoTime()-started)/6_000_000_000.0f;int color=Math.min(2,(int)(phase*3));
     GL33C.glViewport(0,0,width.get(0),height.get(0));GL33C.glDisable(GL33C.GL_SCISSOR_TEST);
     GL33C.glClearColor(color==0?.7f:.05f,color==1?.7f:.05f,color==2?.7f:.05f,1);GL33C.glClear(GL33C.GL_COLOR_BUFFER_BIT);
     GL33C.glEnable(GL33C.GL_SCISSOR_TEST);GL33C.glScissor((int)(phase*(width.get(0)-width.get(0)/12)),0,width.get(0)/12,height.get(0));
     GL33C.glClearColor(1,1,1,1);GL33C.glClear(GL33C.GL_COLOR_BUFFER_BIT);GL33C.glDisable(GL33C.GL_SCISSOR_TEST);
     if(frames==0){ByteBuffer pixel=MemoryUtil.memAlloc(132);try{
      for(int i=0;i<132;i++)pixel.put(i,(byte)0xa5);pixel.position(64).limit(68);
      GL33C.glReadPixels(0,0,1,1,GL33C.GL_RGBA,GL33C.GL_UNSIGNED_BYTE,pixel);GL33C.glFinish();
      for(int i=64;i<68;i++)check(pixel.get(i)==(byte)255,"Actual white pixel");pixel.clear();
      for(int i=0;i<64;i++)check(pixel.get(i)==(byte)0xa5&&pixel.get(68+i)==(byte)0xa5,"Readback guards");
     }finally{MemoryUtil.memFree(pixel);}}
     check(GL33C.glGetError()==GL33C.GL_NO_ERROR&&error[0]==0,"GL/frame error");GLFW.glfwSwapBuffers(window);check(error[0]==0,"Real kopper swap");frames++;
    }
   }
   check(frames>1,"Multiple real frames");GL33C.glFinish();check(GL33C.glGetError()==0,"Finish");
   GLFW.glfwMakeContextCurrent(0);GL.setCapabilities(null);GLFW.glfwDestroyWindow(window);window=0;check(error[0]==0,"Actual context/window teardown");
   GLFW.glfwTerminate();check(error[0]==0,"Actual GLFW/SDL quit");clean=true;
   checkpoint("ZINK185 actual GLFW/LWJGL test and teardown completed; frames="+frames);
  }finally{
   if(clean){var installed=GLFW.glfwSetErrorCallback(null);if(installed!=null)installed.free();if(callback!=null)callback.free();}
  }
  normalQuit=clean; // Native bootstrap also requires normal return, all checks and successful DestroyJavaVM.
 }
}
