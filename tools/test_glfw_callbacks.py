#!/usr/bin/env python3
"""Initialize actual GLFW callback descriptors and libffi closures on core3.4.3."""
from pathlib import Path
import subprocess,tempfile,os,zipfile
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');binding=ROOT/'build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar'
with zipfile.ZipFile(binding)as z:names=[n[:-6].replace('/','.')for n in z.namelist()if n.endswith('CallbackI.class')]
source='''import org.lwjgl.glfw.*;import org.lwjgl.system.*;
public class CallbackCheck {
 public static void main(String[] args)throws Exception {
  System.load(System.getProperty("ps5.test.ffi"));
  int count=0;for(String name:args){Class<?> type=Class.forName(name);if(type.getField("DESCRIPTOR").get(null)==null)throw new AssertionError(name);count++;}
  int[] seen={0};try(GLFWErrorCallback callback=GLFWErrorCallback.create((error,description)->{if(error==123&&description==0)seen[0]++;})){
   if(callback.address()==0)throw new AssertionError("No actual native closure");JNI.invokePV(123,0L,callback.address());if(seen[0]!=1)throw new AssertionError("Native closure did not return to Java");
  }
  try(GLFWKeyCallback callback=GLFWKeyCallback.create((w,k,s,a,m)->{if(w==7&&k==87&&s==26&&a==1&&m==0)seen[0]++;})){
   JNI.invokePV(7L,87,26,1,0,callback.address());if(seen[0]!=2)throw new AssertionError("Key closure arguments");
  }
  System.out.println("PASS "+count+" real GLFW callback descriptor initializations against core3.4.3 and actual libffi native-to-Java error/key closures with arguments/free");
 }
}'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'CallbackCheck.java').write_text(source);cp=':'.join(map(str,[w,ROOT/'.tools/client/lwjgl-3.4.3.jar',binding]));subprocess.run([str(JDK/'bin/javac'),'-cp',cp,str(w/'CallbackCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'--enable-native-access=ALL-UNNAMED','-Dps5.test.ffi='+str(ROOT/'build/libffi-host/liblwjglffi.dylib'),'-Dorg.lwjgl.librarypath='+str(ROOT/'build/client-ports/lwjgl-native/host'),'-cp',cp,'CallbackCheck',*names],check=True,timeout=30,env=dict(os.environ,UBSAN_OPTIONS='handle_segv=0:handle_sigbus=0:handle_sigfpe=0:halt_on_error=1'))
