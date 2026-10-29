#!/usr/bin/env python3
"""Verify pinned original26.2install, GLFW dependency and supported launch policy.

Populate build/version122-research with checksum-verified publisher metadata,
client/dependency JARs, asset indexes and missing objects first. Original26.3
artifacts/objects are reused; this check never transforms a game/mod JAR.
"""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];JDK=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
research=ROOT/'build/version122-research';work=ROOT/'build/version122-test';work.mkdir(exist_ok=True)
lock=json.loads((ROOT/'client/26.2.lock.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Resolve every original game's LWJGL method descriptor against the actual
# parent/instance dependency boundary without initializing native classes.
import struct
references=set()
def method_references(blob):
 count=struct.unpack_from('>H',blob,8)[0];cp=[None]*count;offset=10;index=1
 while index<count:
  tag=blob[offset];offset+=1
  if tag==1:
   size=struct.unpack_from('>H',blob,offset)[0];offset+=2;cp[index]=blob[offset:offset+size].decode('utf-8','replace');offset+=size
  elif tag in (3,4):offset+=4
  elif tag in (5,6):offset+=8;index+=1
  elif tag in (7,8,16,19,20):cp[index]=(tag,struct.unpack_from('>H',blob,offset)[0]);offset+=2
  elif tag in (9,10,11,12,17,18):cp[index]=(tag,*struct.unpack_from('>HH',blob,offset));offset+=4
  elif tag==15:offset+=3
  else:raise ValueError('Unknown class constant tag '+str(tag))
  index+=1
 for item in cp:
  if isinstance(item,tuple)and item[0]in (10,11):
   owner=cp[cp[item[1]][1]];name=cp[item[2]]
   if owner.startswith('org/lwjgl/')and not owner.startswith('org/lwjgl/glfw/'):
    references.add((owner.replace('/','.'),cp[name[1]],cp[name[2]]))
with zipfile.ZipFile(research/'26.2-client.jar')as game:
 for name in game.namelist():
  if name.endswith('.class'):method_references(game.read(name))
(research/'native-method-refs.json').write_text(json.dumps(sorted(references),indent=2))
paths={};checks={}
def keep(url,path,pin):
 assert path.stat().st_size==pin['size'] and hashlib.sha1(path.read_bytes()).hexdigest()==pin['sha1'],path
 paths[url]=str(path);checks[str(path)]=sha(path)
for row in lock['versions']:
 path=research/(row['id']+'.json');b=path.read_bytes();assert hashlib.sha1(b).hexdigest()==row['metadata']['sha1'];meta=json.loads(b);paths[row['metadata']['url']]=str(path)
 assert meta['id']==row['id'] and meta['javaVersion']['majorVersion']==25
 native=lambda m:{x['name']:x['downloads']['artifact']['sha1']for x in m['libraries']if x['name'].startswith('org.lwjgl:')and ':natives-'not in x['name']}
 assert set(native(meta))==set(row['lwjgl']) and all(':3.4.1' in name for name in native(meta)), '26.2 original LWJGL pins'
 keep(meta['downloads']['client']['url'],research/(row['id']+'-client.jar'),meta['downloads']['client'])
 for lib in meta['libraries']:
  if ':natives-'in lib['name'] or (lib['name'].startswith('io.netty:netty-transport-native-') and len(lib['name'].split(':'))>3) or 'artifact'not in lib.get('downloads',{}):continue
  if 'rules'in lib and not any(rule.get('action')=='allow' and rule.get('os',{}).get('name','linux')=='linux' for rule in lib['rules']):continue
  artifact=lib['downloads']['artifact'];name=Path(artifact['path']).name
  p=research/name
  if not p.exists():p=ROOT/'.tools/client'/name
  keep(artifact['url'],p,artifact)
 index=meta['assetIndex'];p=research/('assets-'+index['id']+'.json');keep(index['url'],p,index)
 for v in json.loads(p.read_text())['objects'].values():
  h=v['hash'];p=ROOT/'.tools/client-assets/objects'/h[:2]/h
  if not p.exists():p=research/'objects'/h[:2]/h
  assert p.exists() and p.stat().st_size==v['size'] and hashlib.sha1(p.read_bytes()).hexdigest()==h
  paths['https://resources.download.minecraft.net/'+h[:2]+'/'+h]=str(p)
(work/'url-map.json').write_text(json.dumps(paths))
# The launcher parent owns native dispatch and Gson, but no old game/dependency classes.
parent=':'.join(str(ROOT/'.tools/client'/a['file'])for a in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts']if a['id'].startswith(('org.lwjgl:','com.google.code.gson:')))
source=r'''
import java.nio.file.*;import java.net.*;import java.util.*;import java.lang.reflect.*;import com.google.gson.*;
public class Release262Check {
 static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
 public static void main(String[] a)throws Exception {
  Path project=Path.of(a[0]),work=Path.of(a[1]);System.setProperty("ps5.glfw.binding",project.resolve("build/client-ports/glfw/lwjgl-glfw-3.4.1-ps5-callback343.jar").toString());var mapping=JsonParser.parseString(Files.readString(work.resolve("url-map.json"))).getAsJsonObject();
  var installer=new ProsperoInstall(work.resolve("cache"),url->{var p=mapping.get(url);if(p==null)throw new java.io.IOException("Unexpected network request");return Files.newInputStream(Path.of(p.getAsString()));});
  if(a.length>2){String id=a[2];var receipt=installer.receipt(id);try(var loader=installer.loader(receipt)){
   Thread.currentThread().setContextClassLoader(loader);Path game=work.resolve("smoke-"+id);Files.createDirectories(game);
   Class.forName("net.minecraft.client.main.Main",false,loader).getMethod("main",String[].class).invoke(null,(Object)new String[]{"--demo","--disableMultiplayer","--disableChat","--username","PS5Demo","--uuid","00000000-0000-3000-8000-000000000000","--accessToken","0","--version",id,"--versionType","release","--gameDir",game.toString(),"--assetsDir",work.resolve("cache/assets").toString(),"--assetIndex",receipt.assetIndex,"--graphicsBackend","vulkan","--width","1920","--height","1080"});
  }return;}
  var versions=JsonParser.parseString(Files.readString(project.resolve("client/26.2.lock.json"))).getAsJsonObject().getAsJsonArray("versions");
  for(var entry:versions){var row=entry.getAsJsonObject();String id=row.get("id").getAsString();var pin=row.getAsJsonObject("metadata");
   var receipt=installer.install(new ProsperoInstall.Version(id,"snapshot",pin.get("url").getAsString(),pin.get("sha1").getAsString()),4,(s,d,t)->{},()->false);installer.verify(receipt);
   check(receipt.javaMajor==25&&receipt.window.equals("GLFW")&&receipt.assetIndex.equals(row.get("assetIndex").getAsString()),"metadata handoff "+id);
   check(ProsperoLauncher.supported(id)&&!ProsperoLauncher.snapshot(id),"snapshot gate "+id);
   try(var loader=installer.loader(receipt)){
    var binding=Class.forName("org.lwjgl.glfw.GLFWErrorCallbackI",false,loader);check(binding.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("lwjgl-glfw-3.4.1-ps5-callback343.jar"),"correct callback ABI binding precedence");
    var main=Class.forName("net.minecraft.client.main.Main",false,loader);check(main.getClassLoader()==loader,"game loader");check(main.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("versions/"+id+"/client.jar"),"intact game source");
    check(Class.forName("org.lwjgl.system.Configuration",false,loader).getClassLoader()==ProsperoInstall.class.getClassLoader(),"native dispatch parent");
    int resolved=0;for(var reference:JsonParser.parseString(Files.readString(project.resolve("build/version122-research/native-method-refs.json"))).getAsJsonArray()){
     var ref=reference.getAsJsonArray();Class<?> owner=Class.forName(ref.get(0).getAsString(),false,loader);String name=ref.get(1).getAsString();var type=java.lang.invoke.MethodType.fromMethodDescriptorString(ref.get(2).getAsString(),loader);
     if(name.equals("<init>"))owner.getDeclaredConstructor(type.parameterArray());else{Method method;try{method=owner.getDeclaredMethod(name,type.parameterArray());}catch(NoSuchMethodException inherited){method=owner.getMethod(name,type.parameterArray());}check(method.getReturnType()==type.returnType(),"return ABI "+owner+" "+name);}resolved++;
    }System.out.println("PASS "+resolved+" original26.2game LWJGL method references resolve against actual parent/instance dependencies without initialization");

    String port=ProsperoInstall.hardwarePort(receipt);check(port.equals(id.endsWith("-6")?"oshi-7.7.2-ps5-provider.jar":"oshi-6.9.0-ps5-platform.jar"),"matching OSHI provider");
    Path provider=project.resolve(id.endsWith("-6")?"build/client-ports/oshi7/":"build/client-ports/oshi/").resolve(port);var urls=new ArrayList<URL>();urls.add(provider.toUri().toURL());urls.addAll(List.of(loader.getURLs()));
    try(var hardware=new URLClassLoader(urls.toArray(URL[]::new),ProsperoInstall.class.getClassLoader())){
     System.setProperty("oshi.ps5","true");System.setProperty("ps5.cpu.brand","AMD Fixture CPU");System.setProperty("ps5.cpu.vendor","AuthenticAMD");System.setProperty("ps5.cpu.signature","00870F10");System.setProperty("ps5.cpu.logical","8");Thread.currentThread().setContextClassLoader(hardware);
     var debug=Class.forName("com.mojang.blaze3d.platform.GLX",true,hardware);String cpu=(String)debug.getMethod("_getCpuInfo").invoke(null);check(cpu.equals("8x AMD Fixture CPU"),"original snapshot CPU entry "+id+" "+cpu);
     check(debug.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("versions/"+id+"/client.jar"),"game CPU class replaced");
     if(id.endsWith("-6")){
      var factory=Class.forName("oshi.spi.SystemInfoFactory",true,hardware);Object selected=factory.getMethod("create").invoke(null);check(selected.getClass().getName().equals("oshi.ps5.Ps5SystemInfoProvider"),"OSHI7 provider selection");
      try{selected.getClass().getMethod("getOperatingSystem").invoke(selected);throw new AssertionError("invented OS telemetry");}catch(InvocationTargetException expected){check(expected.getCause() instanceof UnsupportedOperationException,"unsupported OS metrics");}
      System.clearProperty("oshi.ps5");check(!(Boolean)selected.getClass().getMethod("isAvailable").invoke(selected),"PS5 provider active on desktop");
     }
    }finally{Thread.currentThread().setContextClassLoader(Release262Check.class.getClassLoader());System.clearProperty("oshi.ps5");}

   }
   var library=new ProsperoLibrary(work.resolve(id));var instance=library.add("26.2 Test",id,1);library.ready(instance,true);
   var model=new ProsperoLauncher(new ProsperoAuth(),library.root,url->{throw new java.io.IOException("No network in launch policy test");});
   var prepare=ProsperoLauncher.class.getDeclaredMethod("prepareLaunch",ProsperoLibrary.Instance.class,ProsperoInstall.Receipt.class);prepare.setAccessible(true);
   var copy=installer.receipt(id);copy.javaMajor=26;
   try{prepare.invoke(model,instance,copy);throw new AssertionError("future Java accepted");}catch(InvocationTargetException expected){check(expected.getCause() instanceof java.io.IOException&&expected.getCause().getMessage().contains("requires Java 26"),"future Java error");}
   // Set already-verified launch state to inspect argument routing without account I/O.
   for(String key:new String[]{"detail","receipt","launch"}){var f=ProsperoLauncher.class.getDeclaredField(key);f.setAccessible(true);f.set(model,key.equals("detail")?instance:key.equals("receipt")?receipt:true);}
   var current=ProsperoLauncher.class.getDeclaredField("current");current.setAccessible(true);Object before=current.get(null);try{current.set(null,model);check(!ProsperoLauncher.selectedResidentJna()&&ProsperoLauncher.selectedGlfw(),"26.2 GLFW and existing JNA policy");}finally{current.set(null,before);}
   List<String> args=List.of(model.arguments(null,null));check(args.get(args.indexOf("--version")+1).equals(id)&&args.get(args.indexOf("--versionType")+1).equals("release")&&args.get(args.indexOf("--assetIndex")+1).equals(receipt.assetIndex)&&args.contains("vulkan"),"26.2 original arguments");
   System.out.println("PASS "+id+" publisher install/assets/hash verification; isolated original Main; native dispatch/provider/argument/runtime policy");
  }
  check(!ProsperoLauncher.supported("26.4-snapshot-7")&&!ProsperoLauncher.supported("26.4-snapshot-999")&&!ProsperoLauncher.supported("26.1")&&ProsperoLauncher.supported("26.3"),"bounded support list");
 }
}
'''
(work/'Release262Check.java').write_text(source)
subprocess.run([str(JDK/'bin/javac'),'--release','25','-cp',parent,'-d',str(work),*map(str,sorted((ROOT/'client/launcher/java').glob('*.java'))),str(work/'Release262Check.java')],check=True)
subprocess.run([str(JDK/'bin/java'),'-cp',str(work)+':'+parent,'Release262Check',str(ROOT),str(work)],check=True,timeout=240)
for row in lock['versions']:
 result=subprocess.run([str(JDK/'bin/java'),'-cp',str(work)+':'+parent,'Release262Check',str(ROOT),str(work),row['id']],capture_output=True,text=True,timeout=60)
 text=result.stdout+result.stderr;(work/(row['id']+'-main.log')).write_text(text)
 assert result.returncode!=0 and ('UnsatisfiedLinkError' in text or 'Failed to locate library' in text) and 'org.lwjgl' in text and 'MissingRequiredOptionsException' not in text,(row['id'],result.returncode,text[-2000:])
 print('PASS actual original Main startup reaches expected unprovided host LWJGL native bootstrap:',row['id'],'exit',result.returncode)
for p,digest in checks.items():assert sha(Path(p))==digest,'Publisher original changed'
print('PASS pinned26.2original JARs unchanged; no PS5 startup/menu/gameplay acceptance')
