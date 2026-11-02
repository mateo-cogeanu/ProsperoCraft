/** Finite non-initializing parent binding preflight; no native call or JAR rewrite. */
final class ProsperoBindings {
 static void verify(ClassLoader owner)throws ClassNotFoundException {
  for(String name:new String[]{"org.lwjgl.openal.ALC","org.lwjgl.openal.ALC10","org.lwjgl.openal.ALC11","org.lwjgl.openal.ALCCapabilities","org.lwjgl.openal.AL","org.lwjgl.openal.AL10","org.lwjgl.openal.AL11","org.lwjgl.openal.ALCapabilities"}){
   if(Class.forName(name,false,owner).getClassLoader()!=owner)throw new ClassNotFoundException("Packaged LWJGL binding owner mismatch");
  }
 }
}
