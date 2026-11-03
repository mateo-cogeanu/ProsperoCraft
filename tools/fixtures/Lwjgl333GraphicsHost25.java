/* SPDX-License-Identifier: GPL-3.0-or-later */
package prosperocraft.host333;
import org.lwjgl.glfw.*;
import org.lwjgl.opengl.*;
import org.lwjgl.system.*;
import java.nio.*;
import static org.lwjgl.glfw.GLFW.*;
import static org.lwjgl.opengl.GL11C.*;
import static org.lwjgl.opengl.GL20C.*;
import static org.lwjgl.opengl.GL30C.*;
import static org.lwjgl.opengl.GL32C.*;

/** Genuine333 callbacks/GL JNI on desktop GLFW; distinct from Zink/PS5 evidence. */
public class Lwjgl333GraphicsHost25 {
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 public static void main(String[]args)throws Exception{
  Configuration.LIBRARY_NAME.set(args[0]);Configuration.MEMORY_ALLOCATOR.set("system");
  Configuration.GLFW_LIBRARY_NAME.set(args[1]);Configuration.GLFW_CHECK_THREAD0.set(false);
  Configuration.OPENGL_EXPLICIT_INIT.set(true);Library.initialize();
  var field=sun.misc.Unsafe.class.getDeclaredField("theUnsafe");field.setAccessible(true);
  var unsafe=(sun.misc.Unsafe)field.get(null);var current=Platform.class.getDeclaredField("current");
  unsafe.putObjectVolatile(unsafe.staticFieldBase(current),unsafe.staticFieldOffset(current),Platform.PS5);
  boolean zink=args.length>2,absent=zink&&args[2].equals("absent");
  if(zink){System.setProperty("ps5.opengl.provider","zink");glfwInitHint(GLFW_PLATFORM,GLFW_PLATFORM_NULL);if(!absent)prosperocraft.lwjgl333.Bootstrap.configure();}
  try(GLFWErrorCallback error=GLFWErrorCallback.create((code,text)->{if(!absent)throw new AssertionError("GLFW error "+code);})){
   glfwSetErrorCallback(error);check(glfwInit(),"genuine GLFW init");
   boolean original=args.length>3&&args[3].equals("original121");
   if(original){
    System.setProperty("oshi.ps5","true");System.setProperty("ps5.cpu.brand","Host integration fixture");
    System.setProperty("ps5.cpu.vendor","Fixture");System.setProperty("ps5.cpu.signature","00000000");
    System.setProperty("ps5.cpu.logical",Integer.toString(Runtime.getRuntime().availableProcessors()));
    Class.forName("com.mojang.blaze3d.systems.RenderSystem").getMethod("initRenderThread").invoke(null);
   }
   if(absent){
    glfwWindowHint(GLFW_CLIENT_API,GLFW_NO_API);long plain=glfwCreateWindow(8,8,"No API boundary",0,0);check(plain!=0,"unchanged no-API path");glfwDestroyWindow(plain);
    glfwWindowHint(GLFW_CLIENT_API,GLFW_OPENGL_API);glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);check(glfwCreateWindow(8,8,"Missing Zink",0,0)==0,"missing Zink refusal");
    glfwTerminate();glfwSetErrorCallback(null);System.out.println("PASS333 actual GLFW missing-Zink refusal and unchanged no-API control");return;
   }
   for(int cycle=0;cycle<3;cycle++){
    glfwDefaultWindowHints();glfwWindowHint(GLFW_VISIBLE,GLFW_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT,GLFW_TRUE);
    long window=glfwCreateWindow(16,16,"333 binding validation",0,0);check(window!=0,"real core context");
    try{
     glfwMakeContextCurrent(window);if(cycle==0){if(zink)GL.create();else GL.create(GLFW::glfwGetProcAddress);}GL.createCapabilities();
     ByteBuffer bytes=MemoryUtil.memAlloc(96);
     try{
      MemoryUtil.memSet(MemoryUtil.memAddress(bytes),0x5a,96);bytes.position(16);
      glViewport(0,0,4,4);glClearColor(1,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
      glReadPixels(0,0,4,4,GL_RGBA,GL_UNSIGNED_BYTE,bytes);
      for(int i=0;i<16;i++){
       check(bytes.get(i)==0x5a&&bytes.get(80+i)==0x5a,"guard");
       check((bytes.get(16+4*i)&255)==255&&bytes.get(17+4*i)==0&&bytes.get(18+4*i)==0,"red pixel");
      }
      long sync=glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE,0);check(sync!=0,"real GL sync");
      glDeleteSync(sync);check(glGetError()==GL_NO_ERROR,"333 delete-sync JNI ABI");
      int buffer=glGenBuffers();glBindBuffer(GL_ARRAY_BUFFER,buffer);glBufferData(GL_ARRAY_BUFFER,64,GL_DYNAMIC_DRAW);
      ByteBuffer mapped=glMapBufferRange(GL_ARRAY_BUFFER,0,64,GL_MAP_WRITE_BIT|GL_MAP_INVALIDATE_BUFFER_BIT);
      check(mapped!=null,"mutable mapped buffer");mapped.putInt(0,0x12345678);check(glUnmapBuffer(GL_ARRAY_BUFFER),"real unmap");
      glBindBuffer(GL_ARRAY_BUFFER,0);glDeleteBuffers(buffer);
      check(glGetError()==GL_NO_ERROR,"GL errors");
      if(original){
       Class<?> device=Class.forName("fxe");
       check(device.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("client.jar"),"original client provenance");
       Object gpu=device.getConstructor(long.class,int.class,boolean.class,Class.forName("fyy"),boolean.class).newInstance(window,0,false,null,false);
       check(device.getMethod("getBackendName").invoke(gpu).equals("OpenGL"),"original GPU backend");
       device.getMethod("close").invoke(gpu);
       System.out.println("PASS original1.21.11 GlDevice constructor/capabilities/close; null shader lookup; not Main/world");
      }
      System.out.println("PASS333 genuine GL cycle"+cycle+" "+glGetString(GL_VERSION)+" renderer="+glGetString(GL_RENDERER)+"; clear/readback/guards/sync-delete/mapped-buffer");
     }finally{MemoryUtil.memFree(bytes);}
     GL.setCapabilities(null);glfwMakeContextCurrent(0);
    }finally{glfwDestroyWindow(window);}
   }
   GL.destroy();glfwTerminate();glfwSetErrorCallback(null);
  }
 }
}
