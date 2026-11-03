import java.net.URL;
import java.net.URLClassLoader;

/** Native LWJGL state and its package-private callers share the packaged owner. */
final class ProsperoGameLoader extends URLClassLoader {
 private final boolean lwjgl333;
 ProsperoGameLoader(URL[] urls,ClassLoader parent){this(urls,parent,false);}
 ProsperoGameLoader(URL[] urls,ClassLoader parent,boolean lwjgl333){super(urls,parent);this.lwjgl333=lwjgl333;}
 @Override protected Class<?> loadClass(String name,boolean resolve)throws ClassNotFoundException {
  // A missing parent binding must fail; falling back to a publisher copy splits
  // packages/singletons across loaders and can break package-private linkage.
  if(lwjgl333&&(name.startsWith("prosperocraft.lwjgl333.")||(name.startsWith("org.lwjgl.")&&!name.startsWith("org.lwjgl.sdl.")))){
   synchronized(getClassLoadingLock(name)){
    Class<?> type=findLoadedClass(name);if(type==null)type=findClass(name);if(resolve)resolveClass(type);return type;
   }
  }
  if(name.startsWith("org.lwjgl.")){Class<?> type=getParent().loadClass(name);if(resolve)resolveClass(type);return type;}
  return super.loadClass(name,resolve);
 }
}
