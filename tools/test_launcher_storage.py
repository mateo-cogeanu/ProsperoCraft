#!/usr/bin/env python3
"""Check explicit app-storage reservation and honest OS-write error handling."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import json,tempfile,subprocess
ROOT=Path(__file__).resolve().parents[1];jdk=java_home()
cp=launcher_classpath()
param=json.loads((ROOT/'client/startup/param.json').read_text());assert param['downloadDataSize']==4096 and param['titleId']=='PPSA99874'
source=r'''
import java.nio.file.*;import java.io.*;import java.lang.reflect.*;
public class StorageCheck {
 public static void main(String[]args)throws Exception {
  var friendly=ProsperoLauncher.class.getDeclaredMethod("friendly",Exception.class);friendly.setAccessible(true);
  String[] reasons={"No space left on device","Disk quota exceeded","Permission denied","Read-only filesystem","Unclassified"};String[] codes={"ENOSPC","QUOTA","ACCESS","READ_ONLY","IO"};
  for(int i=0;i<reasons.length;i++){var error=new FileSystemException("/download0/ProsperoCraft/cache/public-file",null,reasons[i]);if(!ProsperoStorage.code(error).equals(codes[i]))throw new AssertionError("wrong category");String message=(String)friendly.invoke(null,error);if(i<2&&(!message.contains("App storage")||!message.contains("4GiB")))throw new AssertionError("misleading full-console error");}
  var generic=new IOException("No space left on device");if(!ProsperoStorage.code(generic).equals("ENOSPC"))throw new AssertionError();
  Path folder=Path.of(args[0]);var library=new ProsperoLibrary(folder);var instance=library.add("Keep this world","26.3",1);Files.writeString(library.game(instance).resolve("world-bytes"),"KEEP");
  var model=new ProsperoLauncher(new ProsperoAuth(),folder,null);if(!model.tick(0)[13].equals("2")||!model.tick(0)[32].equals("Keep this world")||!Files.readString(library.game(instance).resolve("world-bytes")).equals("KEEP"))throw new AssertionError("library/world mutated");
  if(!model.tick(0)[67].contains(folder.toString()))throw new AssertionError("actual path hidden");
  System.out.println("PASS4096MiBmanifest/same title, typed ENOSPC/quota/access/read-only categories and app-local full message, unchanged library/world path and visible data root; no invented free-space or console resize claim");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-storage-')as folder:
 w=Path(folder);(w/'StorageCheck.java').write_text(source)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'StorageCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'-cp',str(w)+':'+cp,'StorageCheck',str(w/'test')],check=True,timeout=30)
