#!/usr/bin/env python3
"""Original FFM backend's property route + actual native facade and SDL events."""
from pathlib import Path
import subprocess,tempfile,zipfile,json,os,hashlib
r=Path(__file__).resolve().parents[1];assert hashlib.sha256((r/'build/triggers116-test/controlify.jar').read_bytes()).hexdigest()=='bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a';jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
code=r'''
#include <SDL3/SDL.h>
#include <dlfcn.h>
int prospero_controlify_events_preinit(void);
void prospero_controlify_SetEventFilter(SDL_EventFilter,void*);
bool prospero_controlify_GetEventFilter(SDL_EventFilter*,void**);
bool prospero_controlify_PollEvent(SDL_Event*);
void SDL_SetEventFilter(SDL_EventFilter f,void*u){prospero_controlify_SetEventFilter(f,u);}
bool SDL_GetEventFilter(SDL_EventFilter*f,void**u){return prospero_controlify_GetEventFilter(f,u);}
bool SDL_PollEvent(SDL_Event*e){return prospero_controlify_PollEvent(e);}
int TestInit(void){return prospero_controlify_events_preinit();}
int TestPush(int type){SDL_Event e;SDL_zero(e);e.type=type;e.jdevice.which=7;return SDL_PushEvent(&e);}
int TestGameHas(int type){
 void*h=dlopen("/opt/homebrew/lib/libSDL3.dylib",RTLD_LAZY|RTLD_LOCAL);
 bool(*poll)(SDL_Event*)=(bool(*)(SDL_Event*))dlsym(h,"SDL_PollEvent");
 SDL_Event e;int found=0;while(poll(&e))if(e.type==(Uint32)type)found=1;dlclose(h);return found;
}
'''
java=r'''
import java.lang.foreign.*;import java.lang.invoke.*;import dev.isxander.sdl.ffm.internal.SdlFfmNative;
public class LookupCheck {
 static final Linker LINKER=Linker.nativeLinker();
 static byte filter(MemorySegment data,MemorySegment event){int type=event.reinterpret(128).get(ValueLayout.JAVA_INT,0);return(byte)(type==1541||type==1542?1:0);}
 static MethodHandle call(SymbolLookup lookup,String name,FunctionDescriptor desc){return LINKER.downcallHandle(lookup.find(name).orElseThrow(),desc);}
 public static void main(String[]a)throws Throwable{
  ClientStartup25.configureControlifyNative();if(!System.getProperty("dev.isxander.sdl.library").equals("/app0/libSDL3.so"))throw new AssertionError("launcher path");
  System.load("/opt/homebrew/lib/libSDL3.dylib");
  var facade=SymbolLookup.libraryLookup(java.nio.file.Path.of(a[0]),Arena.global());
  if((int)call(facade,"TestInit",FunctionDescriptor.of(ValueLayout.JAVA_INT)).invokeExact()!=0)throw new AssertionError("init");
  boolean fixed=Boolean.parseBoolean(a[1]);
  if(fixed)System.setProperty("dev.isxander.sdl.library",a[0]);else{System.clearProperty("dev.isxander.sdl.library");System.setProperty("dev.isxander.sdl.libraryName","SDL3");}
  var configure=Class.forName("dev.isxander.sdl.ffm.SdlNativeLibrary").getDeclaredMethod("configure");configure.setAccessible(true);configure.invoke(null);
  var setter=SdlFfmNative.downcall("SDL_SetEventFilter",FunctionDescriptor.ofVoid(ValueLayout.ADDRESS,ValueLayout.ADDRESS));
  try(var arena=Arena.ofConfined()){
   var callback=LINKER.upcallStub(MethodHandles.lookup().findStatic(LookupCheck.class,"filter",MethodType.methodType(byte.class,MemorySegment.class,MemorySegment.class)),FunctionDescriptor.of(ValueLayout.JAVA_BYTE,ValueLayout.ADDRESS,ValueLayout.ADDRESS),arena);
   setter.invokeExact(callback,MemorySegment.NULL);
   var push=call(facade,"TestPush",FunctionDescriptor.of(ValueLayout.JAVA_INT,ValueLayout.JAVA_INT));
   int posted=(int)push.invokeExact(768);if(posted!=(fixed?1:0))throw new AssertionError("physical posted="+posted+" fixed="+fixed);
   int found=(int)call(facade,"TestGameHas",FunctionDescriptor.of(ValueLayout.JAVA_INT,ValueLayout.JAVA_INT)).invokeExact(768);if(found!=(fixed?1:0))throw new AssertionError("game delivery");
   int conn=(int)push.invokeExact(1541);if(conn!=1)throw new AssertionError("connection push");
   if(fixed){var event=arena.allocate(128,8);byte seen=(byte)SdlFfmNative.downcall("SDL_PollEvent",FunctionDescriptor.of(ValueLayout.JAVA_BYTE,ValueLayout.ADDRESS)).invokeExact(event);if(seen==0||event.get(ValueLayout.JAVA_INT,0)!=1541)throw new AssertionError("facade connection poll");}
   setter.invokeExact(MemorySegment.NULL,MemorySegment.NULL);
  }
  System.out.println("PASS actual originalFFM configure/downcalls/upcall;mode="+(fixed?"handlepath:physicalgame+connectionmodpreserved":"loaderLookup:originalphysicaleventdropREPRODUCED"));
 }
}
'''
lock=json.loads((r/'client/26.3.lock.json').read_text());cp=':'.join(str(r/'.tools/client'/a['file'])for a in lock['artifacts'])
with tempfile.TemporaryDirectory(prefix='controlify-ffm-lookup-')as d:
 w=Path(d)
 with zipfile.ZipFile(r/'build/triggers116-test/controlify.jar')as z:
  for part in ['sdl-api-','sdl-backend-ffm-']:
   name=next(n for n in z.namelist()if part in n and n.endswith('.jar'));dest=w/(part+'.jar');dest.write_bytes(z.read(name));cp+=':'+str(dest)
 (w/'bridge.c').write_text(code);lib=w/'libscopedSDL.dylib'
 subprocess.run(['clang','-dynamiclib','-std=c11','-fsanitize=undefined','-I/opt/homebrew/include',str(w/'bridge.c'),str(r/'client/ports/sdl/ps5_controlify_events.c'),'-L/opt/homebrew/lib','-lSDL3','-o',str(lib)],check=True)
 (w/'LookupCheck.java').write_text(java);cp=str(r/'build/startup-host-096')+':'+cp
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),str(w/'LookupCheck.java')],check=True)
 for mode in ['false','true']:
  subprocess.run([str(jdk/'bin/java'),'--enable-native-access=ALL-UNNAMED','-Xverify:all','-Djava.library.path=/opt/homebrew/lib','-cp',str(w)+':'+cp,'LookupCheck',str(lib),mode],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',UBSAN_OPTIONS='halt_on_error=1'),timeout=40)
