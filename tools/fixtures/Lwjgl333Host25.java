/* SPDX-License-Identifier: GPL-3.0-or-later */
import org.lwjgl.*;
import org.lwjgl.glfw.*;
import org.lwjgl.system.*;
import java.nio.*;
import java.util.concurrent.atomic.*;

/** Executes genuine333 core/GLFW callback/STB bindings, no game replacements. */
public class Lwjgl333Host25 {
 public static void main(String[] args)throws Exception {
  Configuration.LIBRARY_NAME.set(args[0]);
  Configuration.MEMORY_ALLOCATOR.set("system");
  Library.initialize();
  // Host-only enum selection, as in existing PS5 dispatch fixtures. Never
  // packaged and does not alter target os.name/architecture/version identity.
  var field=sun.misc.Unsafe.class.getDeclaredField("theUnsafe");field.setAccessible(true);
  var unsafe=(sun.misc.Unsafe)field.get(null);var current=Platform.class.getDeclaredField("current");
  unsafe.putObjectVolatile(unsafe.staticFieldBase(current),unsafe.staticFieldOffset(current),Platform.PS5);
  if(!Version.getVersion().equals("3.3.3+5"))throw new AssertionError("truthful version");
  ByteBuffer bytes=MemoryUtil.memAlloc(128);
  try{MemoryUtil.memSet(MemoryUtil.memAddress(bytes),0x5a,128);for(int i=0;i<128;i++)if(bytes.get(i)!=(byte)0x5a)throw new AssertionError("memory");}
  finally{MemoryUtil.memFree(bytes);}
  int[] seen={0};
  try(GLFWErrorCallback callback=GLFWErrorCallback.create((error,text)->{if(error==123&&text==0)seen[0]++;})){
   JNI.invokePV(123,0L,callback.address());
  }
  try(GLFWKeyCallback callback=GLFWKeyCallback.create((window,key,scan,action,mods)->{if(window==7&&key==87&&scan==26&&action==1&&mods==0)seen[0]++;})){
   JNI.invokePV(7L,87,26,1,0,callback.address());
  }
  if(seen[0]!=2)throw new AssertionError("real libffi closures/arguments");
  var tableMethod=ThreadLocalUtil.class.getDeclaredMethod("getThreadJNIEnv");tableMethod.setAccessible(true);
  long env=((Number)tableMethod.invoke(null)).longValue(),foreign=MemoryUtil.memGetAddress(env);
  long originalSlot=MemoryUtil.memGetAddress(foreign+3L*Pointer.POINTER_SIZE);
  ThreadLocalUtil.setFunctionMissingAddresses(8);
  if(MemoryUtil.memGetAddress(env)==foreign||MemoryUtil.memGetAddress(foreign+3L*Pointer.POINTER_SIZE)!=originalSlot)
   throw new AssertionError("foreign JNI table changed");
  try{ThreadLocalUtil.setFunctionMissingAddresses(8);throw new AssertionError("duplicate guard table");}catch(IllegalStateException expected){}
  ThreadLocalUtil.setCapabilities(0);ThreadLocalUtil.setFunctionMissingAddresses(0);
  var failure=new AtomicReference<Throwable>();Thread[] threads=new Thread[16];
  for(int i=0;i<threads.length;i++){
   threads[i]=new Thread(()->{try{
    for(int n=0;n<100;n++){
     try(GLFWErrorCallback callback=GLFWErrorCallback.create((error,text)->{if(error!=91)throw new AssertionError("thread callback");})){
      JNI.invokePV(91,0L,callback.address());
     }
    }
   }catch(Throwable t){failure.compareAndSet(null,t);}},"333 callback lifecycle");threads[i].start();
  }
  for(Thread thread:threads)thread.join();if(failure.get()!=null)throw new AssertionError(failure.get());
  System.setProperty("ps5.test.ffiCore",args[0]);
  ClientSTB25.main(new String[0]);
  System.out.println("PASS genuine333 core memory/version, actual GLFW error/key closures,1600 concurrent callback lifetimes and original STB PNG/guards/refusal/structs");
 }
}
