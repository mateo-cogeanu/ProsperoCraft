#!/usr/bin/env python3
"""Account encryption/rotation/tamper/signout, skin decode and controller dropdowns."""
from pathlib import Path
import tempfile,subprocess,struct,zlib
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home');cp=str(ROOT/'.tools/client/gson-2.14.0.jar')
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
raw=bytearray()
for y in range(64):
 raw.append(0)
 for x in range(64):raw.extend((10,20,30,255)if 8<=x<16 and 8<=y<16 else (250,40,50,128)if 40<=x<48 and 8<=y<16 else(0,0,0,0))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,64,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
source=r'''
import java.nio.file.*;import java.util.*;import java.lang.reflect.*;
public class AccountUiCheck {
 interface Task{void run()throws Exception;}static void reject(Task t)throws Exception{try{t.run();throw new AssertionError("accepted invalid");}catch(Exception expected){}}
 static void set(Object o,String n,Object v)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);f.set(o,v);}
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void main(String[]args)throws Exception{
  Path base=Path.of(args[0]),classes=Path.of(args[1]);Files.createDirectories(base);
  var store=new ProsperoAccountStore(base);check(store.load().isEmpty(),"missing account");store.save("SECRET_REFRESH_ONE");check(store.load().equals("SECRET_REFRESH_ONE"),"roundtrip");check(!new String(Files.readAllBytes(base.resolve("account/session"))).contains("SECRET_REFRESH"),"plaintext credential");store.save("SECRET_REFRESH_TWO");check(store.load().equals("SECRET_REFRESH_TWO"),"rotation");byte[] bytes=Files.readAllBytes(base.resolve("account/session"));bytes[15]^=1;Files.write(base.resolve("account/session"),bytes);reject(()->store.load());store.clear();check(!store.exists()&&!Files.exists(base.resolve("account/key")),"signout cleanup");
  String face=ProsperoAvatar.decode(Files.readAllBytes(base.resolve("skin.png")));check(face.length()==384&&face.equals("821e28".repeat(64)),"face/hat composite "+face.substring(0,6));reject(()->ProsperoAvatar.decode(new byte[33]));check(ProsperoAvatar.fetch("https://evil.example/skin").isEmpty(),"untrusted skin URL");
  Files.writeString(classes.resolve("prosperocraft-channel.txt"),"temp_gametest");Path root=base.resolve("library");var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;lib.save();check(!lib.settings().snapshots,"new libraries show snapshots");
  var m=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("network");});check(m.tick(0)[81].equals("Sign in"),"signed-out account label");
  check(m.tick(0)[11].equals("0"),"Instances default");m.tick(0x800);check(m.tick(0)[11].equals("2")&&m.tick(0)[28].equals("CONTENT"),"R1 Settings");m.tick(0x800);check(m.tick(0)[11].equals("3"),"R1 Account");m.tick(0x800);check(m.tick(0)[11].equals("0"),"R1 Instances");
  set(m,"page",2);set(m,"row",0);check(m.tick(0x4000)[11].equals("10"),"resolution dropdown");m.tick(0x10);m.tick(0x4000);check(m.tick(0)[25].equals("1600 x 900"),"resolution choice");m.tick(0x4000);m.tick(0x40);m.tick(0x2000);check(m.tick(0)[25].equals("1600 x 900"),"cancel changed resolution");
  set(m,"page",1);set(m,"row",3);m.tick(0x4000);check(m.tick(0)[11].equals("10")&&Integer.parseInt(m.tick(0)[83])>25,"icon dropdown");m.tick(0x20);check(Integer.parseInt(m.tick(0)[15])>=8,"paged navigation");m.tick(0x4000);check(Integer.parseInt(m.tick(0)[24])>=8,"icon choice");
  set(m,"page",2);set(m,"row",0);set(m,"cached",null);String resolution=m.tick(0)[25];m.tick(0x20);check(m.tick(0)[25].equals(resolution),"right changed resolution outside dropdown");m.tick(0x80);check(m.tick(0)[25].equals(resolution),"left changed resolution outside dropdown");
  var accept=ProsperoLauncher.class.getDeclaredMethod("acceptAccount",ProsperoAuth.Session.class,int.class);accept.setAccessible(true);set(m,"page",3);set(m,"tab",2);set(m,"code","DEVICECODE");set(m,"uri","https://www.microsoft.com/link");var generation=ProsperoLauncher.class.getDeclaredField("generation");generation.setAccessible(true);accept.invoke(m,new ProsperoAuth.Session("Owner","0123456789abcdef0123456789abcdef","SECRET_TOKEN",System.currentTimeMillis()+3600000),generation.getInt(m));check(m.tick(0)[11].equals("0")&&m.tick(0)[12].equals("0")&&m.tick(0)[3].isEmpty()&&m.tick(0)[4].isEmpty(),"successful account did not return to Instances/clear device code");
  set(m,"page",3);set(m,"tab",2);set(m,"row",0);set(m,"cached",null);m.tick(0x40);check(m.tick(0)[15].equals("0"),"signed-in account exposes extra action");m.tick(0x4000);check(m.tick(0)[81].equals("Sign in")&&m.tick(0)[5].equals("Not signed in"),"account action did not sign out");
  set(m,"page",2);set(m,"row",3);set(m,"cached",null);m.tick(0x4000);check(m.tick(0)[27].equals("ON"),"snapshot enable");check(new ProsperoLibrary(root).settings().snapshots,"saved snapshot preference lost");
  set(m,"session",new ProsperoAuth.Session("Owner","0123456789abcdef0123456789abcdef","SECRET_TOKEN",System.currentTimeMillis()+3600000));set(m,"avatar",face);set(m,"cached",null);check(m.tick(0).length>81&&m.tick(0)[81].equals("Owner")&&m.tick(0)[80].equals(face),"account/head mailbox");check(!Arrays.toString(m.tick(0)).contains("SECRET_TOKEN"),"token leaked to UI");
  System.out.println("PASS encrypted refresh store/rotation/tamper/signout, bounded skin face/hat and URL guard, resolution/icon dropdown confirm/cancel/page, snapshot default, account/head mailbox and token redaction");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-account-ui-')as folder:
 w=Path(folder);(w/'data').mkdir();(w/'data/skin.png').write_bytes(png);(w/'AccountUiCheck.java').write_text(source)
 subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'AccountUiCheck.java')],check=True)
 subprocess.run([str(JDK/'bin/java'),'-cp',str(w)+':'+cp,'AccountUiCheck',str(w/'data'),str(w)],check=True,timeout=30)
