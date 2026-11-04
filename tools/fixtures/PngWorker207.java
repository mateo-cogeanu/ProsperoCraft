/* SPDX-License-Identifier: GPL-3.0-or-later */
import org.lwjgl.system.*;
import org.lwjgl.stb.*;
import java.io.*;
import java.nio.*;
import java.util.concurrent.atomic.*;

/** Host-only fault fixture for the original STB PNG callback path. */
public class PngWorker207 {
 static native void fault(int mode);
 static native int deniedCalls();
 public static void main(String[]args)throws Exception{
  Configuration.LIBRARY_NAME.set(args[0]);Configuration.MEMORY_ALLOCATOR.set("system");Library.initialize();
  var field=sun.misc.Unsafe.class.getDeclaredField("theUnsafe");field.setAccessible(true);var unsafe=(sun.misc.Unsafe)field.get(null);
  var current=Platform.class.getDeclaredField("current");unsafe.putObjectVolatile(unsafe.staticFieldBase(current),unsafe.staticFieldOffset(current),Platform.PS5);
  AtomicReference<Throwable> failure=new AtomicReference<>();Thread[]threads=new Thread[32];
  for(int i=0;i<threads.length;i++){threads[i]=new Thread(()->{try{
   ByteBuffer pixels=MemoryUtil.memAlloc(64);for(int k=0;k<64;k++)pixels.put(k,(byte)(k*3));
   try{for(int mode=2;mode<=3;mode++){
    ByteArrayOutputStream encoded=new ByteArrayOutputStream();
    try(STBIWriteCallback callback=STBIWriteCallback.create((context,data,size)->{byte[]bytes=new byte[size];MemoryUtil.memByteBuffer(data,size).get(bytes);encoded.writeBytes(bytes);})){
     int before=deniedCalls();fault(mode);boolean ok;
     try{ok=STBImageWrite.stbi_write_png_to_func(callback,0,4,4,4,pixels,16);}finally{fault(0);}
     if(!ok||deniedCalls()!=before)throw new AssertionError("callback attempted native state allocation/setter");
    }
    byte[]png=encoded.toByteArray();if(png.length<8||png[0]!=(byte)137||png[1]!='P'||png[2]!='N'||png[3]!='G')throw new AssertionError("PNG signature");
    ByteBuffer input=MemoryUtil.memAlloc(png.length);try{input.put(png).flip();try(MemoryStack stack=MemoryStack.stackPush()){
     IntBuffer w=stack.mallocInt(1),h=stack.mallocInt(1),c=stack.mallocInt(1);ByteBuffer decoded=STBImage.stbi_load_from_memory(input,w,h,c,4);
     if(decoded==null||w.get(0)!=4||h.get(0)!=4)throw new AssertionError("PNG decode");
     try{for(int k=0;k<64;k++)if(decoded.get(k)!=pixels.get(k))throw new AssertionError("PNG bytes");}finally{STBImage.stbi_image_free(decoded);}
    }}finally{MemoryUtil.memFree(input);}
   }}finally{MemoryUtil.memFree(pixels);}
  }catch(Throwable t){failure.compareAndSet(null,t);}},"Original STB PNG callback worker");threads[i].start();}
  for(Thread t:threads)t.join();if(failure.get()!=null)throw new AssertionError(failure.get());
  System.out.println("PASS64 original333 PNG write/decode callbacks on32Java workers; native-record calloc and TLS setter forced to refuse; neither called; XcheckJNI");
 }
}
