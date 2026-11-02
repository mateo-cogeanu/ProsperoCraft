import java.net.URL;
import java.net.URLClassLoader;

/** Native LWJGL state and its package-private callers share the packaged owner. */
final class ProsperoGameLoader extends URLClassLoader {
 ProsperoGameLoader(URL[] urls,ClassLoader parent){super(urls,parent);}
 @Override protected Class<?> loadClass(String name,boolean resolve)throws ClassNotFoundException {
  // A missing parent binding must fail; falling back to a publisher copy splits
  // packages/singletons across loaders and can break package-private linkage.
  if(name.startsWith("org.lwjgl.")){Class<?> type=getParent().loadClass(name);if(resolve)resolveClass(type);return type;}
  return super.loadClass(name,resolve);
 }
}
