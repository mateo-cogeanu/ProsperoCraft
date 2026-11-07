import java.lang.reflect.Method;

/** Bind the LTS Controlify backend through the game's original JNA owner. */
final class ProsperoControlifyJna {
 private final Object library;
 private final Method function, nativeValue, invokeInt;

 private ProsperoControlifyJna(Object library,Method function,Method nativeValue,Method invokeInt){
  this.library=library;this.function=function;this.nativeValue=nativeValue;this.invokeInt=invokeInt;
 }
 static ProsperoControlifyJna open(ClassLoader owner,String path)throws ReflectiveOperationException{
  Class<?> library=Class.forName("com.sun.jna.NativeLibrary",true,owner);
  if(library.getClassLoader()!=owner)throw new IllegalStateException("JNA must belong to the selected game loader");
  Class<?> pointer=Class.forName("com.sun.jna.Pointer",false,owner);
  Class<?> function=Class.forName("com.sun.jna.Function",false,owner);
  Object handle=library.getMethod("getInstance",String.class).invoke(null,path);
  return new ProsperoControlifyJna(handle,library.getMethod("getFunction",String.class),
      pointer.getMethod("nativeValue",pointer),function.getMethod("invokeInt",Object[].class));
 }
 long address(String name)throws ReflectiveOperationException{
  return (Long)nativeValue.invoke(null,function.invoke(library,name));
 }
 int version()throws ReflectiveOperationException{
  return (Integer)invokeInt.invoke(function.invoke(library,"SDL_GetVersion"),(Object)new Object[0]);
 }
}
