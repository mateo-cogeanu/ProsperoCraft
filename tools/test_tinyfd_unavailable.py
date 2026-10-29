#!/usr/bin/env python3
"""Original LWJGL tinyfd JNI reports unavailable/cancel without a desktop service."""
from pathlib import Path
import subprocess,tempfile,os
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
source='''
import org.lwjgl.util.tinyfd.TinyFileDialogs;
public class DialogCheck {
 public static void main(String[] args){
  String version=TinyFileDialogs.tinyfd_getGlobalChar("tinyfd_version");
  if(version==null||!version.contains("PS5 dialog adapter")||!version.contains("unavailable"))throw new AssertionError("false desktop service claim");
  if(TinyFileDialogs.tinyfd_getGlobalChar("not-a-real-query")!=null)throw new AssertionError("invented metadata");
  if(TinyFileDialogs.tinyfd_messageBox("test","test","yesno","error",1)!=0)throw new AssertionError("invented confirmation");
  if(TinyFileDialogs.tinyfd_openFileDialog("test","",null,null,false)!=null)throw new AssertionError("invented filename");
  if(TinyFileDialogs.tinyfd_selectFolderDialog("test","")!=null)throw new AssertionError("invented folder");
  System.out.println("PASS original TinyFileDialogs JNI startup query explicitly reports unavailable; unknown metadata null; message/file/folder requests return cancel without shell or prompt");
 }
}
'''
with tempfile.TemporaryDirectory()as d:
 w=Path(d);(w/'DialogCheck.java').write_text(source);lib=w/'liblwjgl_tinyfd.dylib'
 subprocess.run(['clang','-std=c11','-dynamiclib','-fsanitize=undefined','-I'+str(JDK/'include'),'-I'+str(JDK/'include/darwin'),str(ROOT/'client/ports/tinyfd/ps5_dialogs.c'),'-o',str(lib)],check=True)
 cp=':'.join(map(str,[w,ROOT/'.tools/client/lwjgl-3.4.3.jar',ROOT/'build/version122-research/lwjgl-tinyfd-3.4.1.jar']))
 subprocess.run([str(JDK/'bin/javac'),'-cp',cp,str(w/'DialogCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-Xcheck:jni','--enable-native-access=ALL-UNNAMED','-Dorg.lwjgl.librarypath='+str(w)+':'+str(ROOT/'build/client-ports/lwjgl-native/host'),'-cp',cp,'DialogCheck'],check=True,timeout=30,env=dict(os.environ,UBSAN_OPTIONS='handle_segv=0:handle_sigbus=0:handle_sigfpe=0:halt_on_error=1'))
