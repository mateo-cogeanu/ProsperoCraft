#!/usr/bin/env python3
"""Original Controlify layout codec -> actual 26.3 EditBox, plus safe installation."""
from pathlib import Path
import subprocess,json,hashlib,zipfile
r=Path(__file__).resolve().parents[1];w=r/'build/controlify-keyboard162-host';w.mkdir(exist_ok=True)
jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
jar=r/'build/triggers116-test/controlify.jar'
assert hashlib.sha256(jar.read_bytes()).hexdigest()=='bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a','Run test_controlify_triggers.py to obtain verified original Controlify'
lock=json.loads((r/'client/26.3.lock.json').read_text());cp=':'.join(str(r/'.tools/client'/a['file'])for a in lock['artifacts'])+':'+str(jar)
source=r'''
import com.google.gson.*;import com.mojang.serialization.JsonOps;
import java.nio.file.*;import java.util.*;import java.util.zip.*;
import net.minecraft.client.gui.components.*;import net.minecraft.client.input.KeyEvent;
import net.minecraft.network.chat.Component;import net.minecraft.server.packs.metadata.pack.PackMetadataSection;
import dev.isxander.controlify.screenop.keyboard.*;
import dev.isxander.controlify.screenop.compat.vanilla.EditBoxComponentProcessor.EditBoxInputTarget;
public class KeyboardCheck {
 static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
 static Path instance(Path root,Path jar,String name)throws Exception{Path g=root.resolve(name);Files.createDirectories(g.resolve("mods"));Files.copy(jar,g.resolve("mods/controlify.jar"));Files.writeString(g.resolve("options.txt"),"soundCategory_master:0.75\r\nresourcePacks:[\"vanilla\",\"file/C418 pack.zip\"]\r\nrenderDistance:17\r\n");return g;}
 static EditBox box(String text)throws Exception{var b=new EditBox(null,200,20,Component.literal("test"));var f=AbstractWidget.class.getDeclaredField("focused");f.setAccessible(true);f.setBoolean(b,true);b.setValue(text);return b;}
 static void key(EditBox b,KeyboardLayout.KeyFunction.CodeFunc function)throws Exception{
  var target=new EditBoxInputTarget(b);
  // The key-code record is package-private. Invoke its genuine accessors,
  // then the original Controlify InputTarget (no replacement game classes).
  for(Object code:function.codes()){
   int[] v=new int[3];String[] fields={"keycode","scancode","modifier"};
   for(int i=0;i<3;i++){var m=code.getClass().getDeclaredMethod(fields[i]);m.setAccessible(true);v[i]=(int)m.invoke(code);}
   target.acceptKeyCode(v[0],v[1],v[2]);
  }
 }
 public static void main(String[]args)throws Exception {
  Path root=Path.of(args[0]),jar=Path.of(args[1]);Path game=instance(root,jar,"working");String original=Files.readString(game.resolve("options.txt"));byte[] mod=Files.readAllBytes(game.resolve("mods/controlify.jar"));
  check(ProsperoControlifyKeyboard.prepare(game,"26.2","fabric").equals("NOT_APPLICABLE"),"26.2 untouched");
  check(ProsperoControlifyKeyboard.prepare(game,"26.3","vanilla").equals("NOT_APPLICABLE"),"vanilla untouched");
  check(Files.readString(game.resolve("options.txt")).equals(original),"options preserved when out of scope");
  check(ProsperoControlifyKeyboard.prepare(game,"26.3","fabric").equals("INSTALLED_LAYOUTS_3"),"installed");
  Path pack=game.resolve("resourcepacks").resolve(ProsperoControlifyKeyboard.PACK);byte[] packed=Files.readAllBytes(pack);
  check(Arrays.equals(mod,Files.readAllBytes(game.resolve("mods/controlify.jar"))),"original jar intact");
  check(Files.readString(game.resolve("options.before-controlify-keyboard162.txt")).equals(original),"exact options backup");
  String options=Files.readString(game.resolve("options.txt"));check(options.contains("soundCategory_master:0.75\r\n")&&options.contains("renderDistance:17\r\n")&&options.contains("file/C418 pack.zip")&&options.contains(ProsperoControlifyKeyboard.ID),"settings/order preserved");
  check(ProsperoControlifyKeyboard.prepare(game,"26.3","fabric").equals("READY"),"repeat");check(Arrays.equals(packed,Files.readAllBytes(pack)),"no rewrite");
  net.minecraft.SharedConstants.tryDetectVersion();net.minecraft.server.Bootstrap.bootStrap();
  try(ZipFile zip=new ZipFile(pack.toFile())){
   JsonObject meta=JsonParser.parseString(new String(zip.getInputStream(zip.getEntry("pack.mcmeta")).readAllBytes())).getAsJsonObject();
   PackMetadataSection.CLIENT_TYPE.codec().parse(JsonOps.INSTANCE,meta.get("pack")).getOrThrow();
   int layouts=0;
   for(var entry:Collections.list(zip.entries()))if(entry.getName().endsWith(".json")){
    JsonElement layout=JsonParser.parseString(new String(zip.getInputStream(entry).readAllBytes()));
    var decoded=KeyboardLayout.CODEC.parse(JsonOps.INSTANCE,layout).getOrThrow();
    KeyboardLayout.KeyFunction.CodeFunc back=null;
    for(var row:decoded.keys())for(var k:row)if(k.regular() instanceof KeyboardLayout.KeyFunction.CodeFunc code)back=code;
    check(back!=null,"code action decoded");
    EditBox b=box("abc");new EditBoxInputTarget(b).acceptKeyCode(42,0,0);check(b.getValue().equals("abc"),"original failure reproduced");
    key(b,back);check(b.getValue().equals("ab"),"actual deletion");
    key(b,back);key(b,back);key(b,back);check(b.getValue().isEmpty(),"repeat/empty");
    b=box("abcd");b.moveCursorTo(2,false);key(b,back);check(b.getValue().equals("acd"),"middle");
    b=box("abcd");b.moveCursorTo(1,false);b.setHighlightPos(3);key(b,back);check(b.getValue().equals("ad"),"selection");
    b=box("a\ud83d\ude00");key(b,back);check(b.getValue().equals("a"),"Unicode codepoint deletion");layouts++;
   }
   check(layouts==3,"all full/simple/server-IP layouts decoded");
  }
  Files.writeString(game.resolve("options.txt"),options.replace(",\""+ProsperoControlifyKeyboard.ID+"\"",""));
  check(ProsperoControlifyKeyboard.prepare(game,"26.3","fabric").equals("DISABLED_BY_USER"),"honor disabled pack");
  Files.delete(game.resolve("mods/controlify.jar"));check(ProsperoControlifyKeyboard.prepare(game,"26.3","fabric").equals("NOT_PINNED")&&!Files.exists(pack),"stale owned override removed");
  Path updated=instance(root,jar,"updated");ProsperoControlifyKeyboard.prepare(updated,"26.3","fabric");
  Files.delete(updated.resolve("mods/controlify.jar"));
  try(var out=new ZipOutputStream(Files.newOutputStream(updated.resolve("mods/new-controlify.jar")))){out.putNextEntry(new ZipEntry("fabric.mod.json"));out.write("{\"id\":\"controlify\",\"version\":\"future-test\"}".getBytes());out.closeEntry();}
  check(ProsperoControlifyKeyboard.prepare(updated,"26.3","fabric").equals("NOT_PINNED"),"updated mod rejected");
  check(!Files.readString(updated.resolve("options.txt")).contains(ProsperoControlifyKeyboard.ID)&&Files.readString(updated.resolve("options.txt")).contains("file/C418 pack.zip"),"stale selection removed, other packs kept");
  Path invalid=instance(root,jar,"invalid");Files.writeString(invalid.resolve("options.txt"),"resourcePacks:not json\n");try{ProsperoControlifyKeyboard.prepare(invalid,"26.3","fabric");throw new AssertionError("invalid options accepted");}catch(java.io.IOException expected){}check(Files.readString(invalid.resolve("options.txt")).equals("resourcePacks:not json\n")&&!Files.exists(invalid.resolve("resourcepacks").resolve(ProsperoControlifyKeyboard.PACK)),"invalid untouched");
  Path collision=instance(root,jar,"collision");Files.createDirectories(collision.resolve("resourcepacks"));Path foreign=collision.resolve("resourcepacks").resolve(ProsperoControlifyKeyboard.PACK);Files.writeString(foreign,"user file");check(ProsperoControlifyKeyboard.prepare(collision,"26.3","fabric").equals("SKIPPED_PACK_NAME_COLLISION")&&Files.readString(foreign).equals("user file"),"foreign file preserved");
  System.out.println("PASS original Controlify layout/pack codecs and actual Minecraft EditBox: reproduces original no-op; fixes end/middle/selection/Unicode/repeat/empty across3layouts;unchangedmod,scope,options backup/order,idempotency,userdisable,stale cleanup,malformedoptions/collision preservation");
 }
}
'''
(w/'KeyboardCheck.java').write_text(source)
subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (r/'client/launcher/java').glob('*.java')],str(w/'KeyboardCheck.java')],check=True)
import tempfile
with tempfile.TemporaryDirectory(prefix='controlify-keyboard-')as temp:
 subprocess.run([str(jdk/'bin/java'),'--enable-native-access=ALL-UNNAMED','-Xverify:all','-cp',str(w)+':'+cp,'KeyboardCheck',temp,str(jar)],check=True,timeout=60)
