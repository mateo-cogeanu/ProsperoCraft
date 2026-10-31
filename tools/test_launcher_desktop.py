#!/usr/bin/env python3
"""Exercise actual launcher desktop commands and native HID packet policy."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath, executable
import subprocess,tempfile
R=Path(__file__).resolve().parents[1]
J=(java_home()/'bin')
java=r'''
import java.nio.file.*;import java.util.*;
public class DesktopCheck {
 static void ok(boolean b){if(!b)throw new AssertionError();}
 static void set(Object o,String key,Object v)throws Exception{var f=o.getClass().getDeclaredField(key);f.setAccessible(true);f.set(o,v);var c=o.getClass().getDeclaredField("cached");c.setAccessible(true);c.set(o,null);}
 static int click(int page,int kind,int row){return 0x10008000|page<<20|kind<<16|row;}
 public static void main(String[] args)throws Exception{
  ok(ProsperoLauncher.supported("26.2","fabric"));ok(!ProsperoLauncher.developmentTest("26.2","fabric"));ok(!ProsperoChannel.fabric262Test());ok(!ProsperoLauncher.supported("26.1","fabric"));
  var root=Path.of(args[0]);var lib=new ProsperoLibrary(root);lib.settings().showIntro=false;lib.save();var item=lib.add("Preserved","26.2",1,"fabric");lib.ready(item,true);String saved=Files.readString(root.resolve("library.json"));
  var m=new ProsperoLauncher(new ProsperoAuth(),root,url->{throw new AssertionError("No network");});
  ok(m.tick(0)[35].equals("READY"));m.tick(click(0,1,0));ok(m.tick(0)[11].equals("4"));ok(m.tick(0)[69].equals("SUPPORTED"));ok(!m.tick(0)[6].contains("DEV"));
  m.tick(click(0,3,1));ok(m.tick(0)[11].equals("4")); // stale click ignored
  m.tick(click(4,3,1));ok(m.tick(0)[11].equals("5"));m.tick(click(5,3,0));ok(m.tick(0)[11].equals("6"));
  set(m,"keyboard","");m.tick(0x30000000|'A');m.tick(0x30000000|'z');m.tick(0x30000000|' ');ok(m.tick(0)[29].equals("Az "));m.tick(0x20000002);ok(m.tick(0)[29].equals("Az"));
  m.tick(0x2000);ok(m.tick(0)[11].equals("5"));ok(Files.readString(root.resolve("library.json")).equals(saved));
  m.tick(click(5,0,1));ok(m.tick(0)[11].equals("2"));m.tick(click(2,3,6));ok(m.tick(0)[11].equals("10"));m.tick(click(10,3,2));ok(m.tick(0)[11].equals("2"));ok(m.tick(0)[104].equals("2"));
  set(m,"page",9);set(m,"row",0);set(m,"detail",item);m.tick(click(9,0,1));ok(m.tick(0)[11].equals("9"));m.tick(click(9,3,0));ok(m.tick(0)[11].equals("5")); // modal blocks tabs, explicit No
  set(m,"page",6);set(m,"keyboard","");m.tick(0x30000000|'x');m.tick(click(6,4,4)&~0x8000);ok(m.tick(0)[11].equals("6"));m.tick(0x20000001);ok(m.tick(0)[11].equals("5"));ok(m.tick(0)[16].equals("x"));
  System.out.println("PASS supported Fabric26.2; real model pointer/tab/dropdown/modal/stale click; typing/backspace/commit/cancel; library preservation");
 }
}
'''
cpp=r'''
#include "desktop_input.hpp"
#include "cursor_shape.hpp"
#include <cmath>
#include <cassert>
#include <vector>
#include <cstring>
using namespace prospero_menu;
static std::vector<prospero_keyboard_packet> kp;static std::vector<prospero_mouse_packet> mp;static int closes=0;
extern "C" int prospero_hid_open(int mouse,int i){return i==0?mouse+10:-1;}
extern "C" void prospero_hid_close(int,int){closes++;}
extern "C" int prospero_hid_read(int mouse,int,void* out,int){if(mouse){int n=mp.size();memcpy(out,mp.data(),n*sizeof(prospero_mouse_packet));mp.clear();return n;}int n=kp.size();memcpy(out,kp.data(),n*sizeof(prospero_keyboard_packet));kp.clear();return n;}
int main(){
 CursorShape shape;assert(shape.count>90&&shape.count<128);for(int i=0;i<shape.count;i++){int a=(i+shape.count-1)%shape.count,b=(i+1)%shape.count;float ax=shape.xy[i*2]-shape.xy[a*2],ay=shape.xy[i*2+1]-shape.xy[a*2+1],bx=shape.xy[b*2]-shape.xy[i*2],by=shape.xy[b*2+1]-shape.xy[i*2+1];float lengths=std::sqrt((ax*ax+ay*ay)*(bx*bx+by*by));assert(lengths>0&&(ax*bx+ay*by)/lengths>0.8f);}
 assert(desktop_hit(0,70,342,0,2).target==0);assert(desktop_hit(0,69,342,0,2).kind==-1);assert(desktop_hit(0,520,342,0,2).target==1);assert(desktop_hit(0,491,342,0,2).kind==-1);
 assert(desktop_hit(6,900,70,0,0).kind==-1);assert(desktop_hit(10,300,285,8,20).target==8);assert(desktop_hit(5,1350,650,0,0).target==7);assert(desktop_hit(12,1600,550,0,1,0,false,true).target==20);
 assert(desktop_char(4,false,false)=='a'&&desktop_char(4,true,false)=='A'&&desktop_char(4,true,true)=='a');
 DesktopInput d;std::vector<unsigned> events;int clicks=0;auto emit=[&](unsigned x){events.push_back(x);};auto point=[&](int x,int y,bool c){assert(x>=0&&x<1920&&y>=0&&y<1080);clicks+=c;};
 prospero_keyboard_packet k{};k.connected=1;k.keys[0]=40;kp={k};d.poll(1,emit,point);assert(events.empty()); // held on entry
 k.keys[0]=0;kp={k};d.poll(2,emit,point);k.keys[0]=4;kp={k};d.poll(3,emit,point);assert(events.back()==(0x30000000|'a'));size_t n=events.size();d.poll(500,emit,point);assert(events.size()==n); // no stale repeat
 kp={k};d.poll(501,emit,point);assert(events.size()==n+1);k.intercepted=1;kp={k};d.poll(502,emit,point);k.intercepted=0;kp={k};d.poll(503,emit,point);assert(events.size()==n+1); // rearm after intercept
 prospero_mouse_packet m{};m.connected=1;m.buttons=1;mp={m};d.poll(504,emit,point);assert(clicks==0);m.buttons=0;mp={m};d.poll(505,emit,point);m.buttons=1;m.x=50000;m.y=-50000;mp={m};d.poll(506,emit,point);assert(clicks==1&&d.x==1919&&d.y==0&&d.cursor);mp={m};d.poll(507,emit,point);assert(clicks==1);d.close();assert(closes==2&&!d.cursor);
}
'''
with tempfile.TemporaryDirectory() as td:
 w=Path(td);(w/'DesktopCheck.java').write_text(java);cp=launcher_classpath();out=w/'classes';out.mkdir()
 subprocess.run([str(J/'javac'),'--release','25','-cp',cp,'-d',str(out),*[str(p)for p in (R/'client/launcher/java').glob('*.java')],str(w/'DesktopCheck.java')],check=True)
 (out/'prosperocraft-channel.txt').write_text('temp_gametest\n')
 subprocess.run([str(J/'java'),'-cp',str(out)+':'+cp,'DesktopCheck',str(w/'data')],check=True)
 (w/'test.cpp').write_text(cpp)
 subprocess.run([executable('clang++', env='CXX'),'-std=c++20','-fsanitize=address,undefined','-I'+str(R/'client/launcher'),str(w/'test.cpp'),'-o',str(w/'test')],check=True)
 subprocess.run([str(w/'test')],check=True)
print('PASS native HID packet read/held-on-entry/repeat/intercept/clamp/single-click/close and layout hit boundaries under ASan/UBSan')
