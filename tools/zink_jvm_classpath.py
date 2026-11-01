"""Consumer diagnostic classpath construction and non-initializing JDK checks.

Read only explicit package JARs. Never searches private/game caches or downloads.
"""
import hashlib,json,re,subprocess,zipfile
from pathlib import Path
PREFIX='/app0/assets/java25/'
GLFW='ports/lwjgl-glfw-3.4.1-ps5-callback343.jar'
REQUIRED=('ClientStartup25','org.lwjgl.glfw.GLFW','org.lwjgl.glfw.GLFWErrorCallbackI','org.lwjgl.opengl.GL','org.lwjgl.opengl.GL33C','org.lwjgl.system.ps5.PS5Library','org.lwjgl.system.MemoryUtil','org.lwjgl.system.MemoryStack')

def parse_header(text):
 match=re.fullmatch(r'#pragma once\s*#define CLIENT_CLASSPATH_OPTION ("(?:[^"\\]|\\.)*")\s*',text)
 if not match:raise ValueError('Unrecognized classpath header')
 option=json.loads(match[1])
 if not option.startswith('-Djava.class.path='):raise ValueError('Wrong option')
 return option[len('-Djava.class.path='):].split(':')

def fix_header(text):
 paths=parse_header(text)
 entry=PREFIX+GLFW
 # The adapted binding must precede any parent/default GLFW classes.
 paths=[entry,*[path for path in paths if path!=entry]]
 return '#pragma once\n#define CLIENT_CLASSPATH_OPTION '+json.dumps('-Djava.class.path='+':'.join(paths))+'\n'

def verify_app_classpath(app,header,jdk,work):
 root=Path(app)/'assets/java25';paths=parse_header(header);local=[]
 for path in paths:
  if not path.startswith(PREFIX):raise ValueError('Classpath outside package root')
  relative=Path(path[len(PREFIX):])
  if relative.is_absolute()or '..'in relative.parts:raise ValueError('Escaping classpath')
  file=root/relative
  if not file.is_file():raise FileNotFoundError('Missing classpath entry: '+str(relative))
  local.append(file)
 owners={}
 for file in local:
  with zipfile.ZipFile(file)as jar:
   names=set(jar.namelist())
  for name in REQUIRED:
   if name.replace('.','/')+'.class'in names and name not in owners:owners[name]=file.relative_to(root).as_posix()
 missing=set(REQUIRED)-set(owners)
 if missing:raise ValueError('Required classes absent from effective JVM classpath: '+','.join(sorted(missing)))
 if owners['org.lwjgl.glfw.GLFW']!=GLFW:raise ValueError('Wrong effective GLFW class provider')
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 source=work/'ClasspathCheck.java'
 source.write_text('''import java.net.*;import java.nio.file.*;public class ClasspathCheck{public static void main(String[]args)throws Exception{int split=Integer.parseInt(args[0]);URL[]urls=new URL[split];for(int i=0;i<split;i++)urls[i]=Path.of(args[i+1]).toUri().toURL();try(var loader=new URLClassLoader(urls,ClassLoader.getPlatformClassLoader())){for(int i=split+1;i<args.length;i++)Class.forName(args[i],false,loader);}System.out.println("PASS packaged classpath non-initializing resolution");}}''')
 subprocess.run([str(Path(jdk)/'bin/javac'),'--release','25','-d',str(work),str(source)],check=True)
 subprocess.run([str(Path(jdk)/'bin/java'),'-Xverify:all','-cp',str(work),'ClasspathCheck',str(len(local)),*map(str,local),*REQUIRED],check=True)
 return {'paths':paths,'header_sha256':hashlib.sha256(header.encode()).hexdigest(),'required_classes':owners,'jars_sha256':{file.relative_to(root).as_posix():hashlib.sha256(file.read_bytes()).hexdigest()for file in local},'verification':'PASS real JDK25 non-initializing package classpath resolution; no native initialization/PS5 execution'}
