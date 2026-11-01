/* SPDX-License-Identifier: MIT
 * Host-only execution of actual GLFW/LWJGL and original publisher GL bootstrap.
 * The PS5 enum override exercises the existing resident-style host lookup;
 * it is never packaged or a target-platform identity workaround.
 */
import org.lwjgl.glfw.*;
import org.lwjgl.opengl.*;
import org.lwjgl.system.*;
import sun.misc.Unsafe;
import java.lang.reflect.*;
import java.nio.*;
import java.util.concurrent.atomic.AtomicReference;
import static org.lwjgl.opengl.GL11C.*;
import static org.lwjgl.opengl.GL20C.*;
import static org.lwjgl.opengl.GL30C.*;
import static org.lwjgl.glfw.GLFW.*;

public class ZinkGlfwHost25 {
 static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
 static void pixels(){
  ByteBuffer bytes=MemoryUtil.memAlloc(96);
  try{
   for(int i=0;i<96;i++)bytes.put(i,(byte)0x5a);
   glViewport(0,0,4,4);glClearColor(1,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
   bytes.position(16);glReadPixels(0,0,4,4,GL_RGBA,GL_UNSIGNED_BYTE,bytes);bytes.position(0);
   for(int i=0;i<16;i++){check(bytes.get(i)==0x5a&&bytes.get(80+i)==0x5a,"guard");check((bytes.get(16+4*i)&255)==255&&bytes.get(17+4*i)==0&&bytes.get(18+4*i)==0&&(bytes.get(19+4*i)&255)==255,"pixel");}
   int vs=glCreateShader(GL_VERTEX_SHADER),fs=glCreateShader(GL_FRAGMENT_SHADER),program=glCreateProgram(),vao=glGenVertexArrays();
   try{
    glShaderSource(vs,"#version 330 core\nconst vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));void main(){gl_Position=vec4(p[gl_VertexID],0,1);}");glCompileShader(vs);check(glGetShaderi(vs,GL_COMPILE_STATUS)!=0,"vertex shader");
    glShaderSource(fs,"#version 330 core\nout vec4 color;void main(){color=vec4(0,1,0,1);}");glCompileShader(fs);check(glGetShaderi(fs,GL_COMPILE_STATUS)!=0,"fragment shader");
    glAttachShader(program,vs);glAttachShader(program,fs);glLinkProgram(program);check(glGetProgrami(program,GL_LINK_STATUS)!=0,"link");
    glUseProgram(program);glBindVertexArray(vao);glDrawArrays(GL_TRIANGLES,0,3);
    bytes.position(16);glReadPixels(0,0,4,4,GL_RGBA,GL_UNSIGNED_BYTE,bytes);bytes.position(0);
    for(int i=0;i<16;i++){check(bytes.get(i)==0x5a&&bytes.get(80+i)==0x5a,"draw guard");check(bytes.get(16+4*i)==0&&(bytes.get(17+4*i)&255)==255&&bytes.get(18+4*i)==0&&(bytes.get(19+4*i)&255)==255,"draw pixel");}
   }finally{glUseProgram(0);glDeleteVertexArrays(vao);glDeleteProgram(program);glDeleteShader(vs);glDeleteShader(fs);}
   check(glGetError()==GL_NO_ERROR,"GL errors");
  }finally{MemoryUtil.memFree(bytes);}
 }
 public static void main(String[] args)throws Exception{
  Configuration.MEMORY_ALLOCATOR.set("system");Configuration.LIBRARY_NAME.set(args[0]);
  Configuration.GLFW_LIBRARY_NAME.set(args[2]);Configuration.OPENGL_EXPLICIT_INIT.set(true);
  Configuration.GLFW_CHECK_THREAD0.set(false); // SDL dummy platform, no Cocoa event loop.
  System.load(args[0]);System.load(args[1]);Library.initialize();MemoryUtil.memBackend();
  glfwInitHint(GLFW_PLATFORM,GLFW_PLATFORM_NULL);check(glfwInit(),"actual GLFW SDL init");
  if(args[3].equals("absent")){
   glfwWindowHint(GLFW_CLIENT_API,GLFW_NO_API);long plain=glfwCreateWindow(8,8,"No API control",0,0);check(plain!=0,"Vulkan/no API window unchanged");glfwDestroyWindow(plain);
   glfwWindowHint(GLFW_CLIENT_API,GLFW_OPENGL_API);glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
   check(glfwCreateWindow(8,8,"Missing Zink",0,0)==0,"missing resident provider accepted");check(glfwGetError(null)==GLFW_API_UNAVAILABLE,"absence error");glfwTerminate();System.out.println("PASS real GLFW missing-Zink refusal; existing no-API window works");return;
  }
  Configuration.OPENGL_LIBRARY_NAME.set(args[4]);System.load(args[4]);
  Field unsafeField=Unsafe.class.getDeclaredField("theUnsafe");unsafeField.setAccessible(true);Unsafe unsafe=(Unsafe)unsafeField.get(null);
  Field platform=Platform.class.getDeclaredField("current");Object base=unsafe.staticFieldBase(platform);long offset=unsafe.staticFieldOffset(platform);Platform previous=Platform.get();
  unsafe.putObjectVolatile(base,offset,Platform.PS5);System.setProperty("ps5.opengl.provider","zink");
  try{
   GL.create();
   // Same consumer OSHI boundary as the launcher, with explicit host fixture
   // CPU metadata. This avoids invoking unrelated macOS IOKit/JNA telemetry.
   System.setProperty("oshi.ps5","true");System.setProperty("ps5.cpu.brand","Host integration fixture");
   System.setProperty("ps5.cpu.vendor","Fixture");System.setProperty("ps5.cpu.signature","00000000");
   System.setProperty("ps5.cpu.logical",Integer.toString(Runtime.getRuntime().availableProcessors()));
   Class<?> backend=Class.forName("com.mojang.blaze3d.opengl.GlBackend");
   check(backend.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("-client.jar"),"original backend provenance");
   Class.forName("com.mojang.blaze3d.systems.RenderSystem").getMethod("initRenderThread").invoke(null);
   for(int cycle=0;cycle<3;cycle++){
    glfwDefaultWindowHints();backend.getMethod("setWindowHints").invoke(backend.getConstructor().newInstance());
    long window=glfwCreateWindow(8,8,"Real Zink",0,0);check(window!=0,"original GL hints");glfwMakeContextCurrent(window);check(glfwGetCurrentContext()==window,"current context");
    GL.createCapabilities();String renderer=glGetString(GL_RENDERER);check(renderer!=null&&renderer.contains("zink"),"actual Zink renderer");
    check(GL.getCapabilities().OpenGL33,"GL3.3 core");check(glfwGetProcAddress("glClear")!=0,"GLFW function address");
    try(SharedLibrary provider=new org.lwjgl.system.ps5.PS5Library("libps5zink.so")){
     long entry=provider.getFunctionAddress("ps5zink_get_proc_address");check(entry!=0,"real resident-style entry");
     try(MemoryStack stack=MemoryStack.stackPush()){check(JNI.invokePP(MemoryUtil.memAddress(stack.ASCII("glClear")),entry)==glfwGetProcAddress("glClear"),"same actual GL provider");}
    }
    pixels();glfwSwapInterval(0);glfwSwapBuffers(window);
    AtomicReference<Throwable> failure=new AtomicReference<>();Thread worker=new Thread(()->{try{glfwMakeContextCurrent(window);check(glfwGetCurrentContext()==0,"foreign thread stole current context");check(glfwGetError(null)==GLFW_PLATFORM_ERROR,"foreign binding refusal");}catch(Throwable e){failure.set(e);}});worker.start();worker.join();if(failure.get()!=null)throw new AssertionError(failure.get());
    GL.setCapabilities(null);glfwMakeContextCurrent(0);
    worker=new Thread(()->{try{glfwMakeContextCurrent(window);check(glfwGetCurrentContext()==window,"thread transfer");GL.createCapabilities();pixels();GL.setCapabilities(null);glfwMakeContextCurrent(0);}catch(Throwable e){failure.set(e);}});worker.start();worker.join();if(failure.get()!=null)throw new AssertionError(failure.get());
    glfwMakeContextCurrent(window);
    // Invoke the *original* game's constructor through capability creation.
    // Deliberately null debug options stop it at a known later boundary; this
    // is not a claim of a complete GlDevice, Main or title-screen bootstrap.
    Class<?> device=Class.forName("com.mojang.blaze3d.opengl.GlDevice");
    Constructor<?> ctor=device.getDeclaredConstructor(long.class,Class.forName("com.mojang.blaze3d.shaders.ShaderSource"),Class.forName("com.mojang.blaze3d.shaders.GpuDebugOptions"));ctor.setAccessible(true);
    GL.setCapabilities(null);
    try{ctor.newInstance(window,null,null);throw new AssertionError("expected injected debug-options boundary");}catch(InvocationTargetException expected){check(expected.getCause() instanceof NullPointerException,"original bootstrap boundary: "+expected.getCause().getClass().getName());}
    check(GL.getCapabilities().OpenGL33,"original GlDevice failed before capability creation");
    check(glGetString(GL_RENDERER).contains("zink"),"original capability provider");
    GL.setCapabilities(null);glfwMakeContextCurrent(0);glfwDestroyWindow(window);
    System.out.println("PASS actual GLFW/LWJGL Zink draw/guard/thread/destroy and original GlDevice capability boundary cycle "+cycle);
   }
   GL.destroy();
  }finally{System.clearProperty("ps5.opengl.provider");unsafe.putObjectVolatile(base,offset,previous);glfwTerminate();}
 }
}
