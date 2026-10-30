import java.nio.file.*;
import java.util.*;

/** Controller model. Native UI is independent; downloads and authentication use workers. */
public final class ProsperoLauncher {
 static final int FIELD_COUNT=105;
 private int feedbackSerial;private String feedbackCue="";
 private void feedback(String cue){feedbackCue=cue;feedbackSerial=feedbackSerial==Integer.MAX_VALUE?1:feedbackSerial+1;cached=null;}
 static final String[] THEMES={"Forest","Ocean","Amethyst","Rose","Amber","Graphite"};
 static final String[] BACKGROUNDS={"Gradient","Aurora","Grid","Stars","Waves","Bokeh","Phosphor","Paper","Dots","Vista"};
 interface Menu {boolean show();}
 private static ProsperoLauncher current;
 private final ProsperoAuth auth;private final ProsperoLibrary library;private final ProsperoInstall installer;
 private final ProsperoFabric fabric;private final ProsperoModrinth modrinth=new ProsperoModrinth();
 private ProsperoModrinth.Local pendingUninstall;private int uninstallReturnRow;private int bindingIndex=8;private int shadowScale=100;private boolean contentInstalled;private String activeContentIcon="";private List<ProsperoModrinth.Local> localContent=List.of();private final Map<String,String> contentIcons=new HashMap<>();
 private int draftLoader=0,contentOffset=0,contentTotal=0;private String contentQuery="";private ProsperoModrinth.Kind contentKind=ProsperoModrinth.Kind.MOD;private List<ProsperoModrinth.Hit> contentHits=List.of();private List<ProsperoModrinth.Selection> contentQueue=List.of();
 private int dropdownKind,dropdownChoice,dropdownReturn,dropdownRow;
 private int selected=0,page=0,tab=0,row=0,generation=0,versionChoice=0,draftIcon=1,key=0,keyboardReturn=1;
 private boolean launchPrepared=false,awaitingTutorial=false;
 private boolean top=false,busy=false,launch=false,lowercase=false,customName=false;private String task="",message="",code="",uri="",draftName="",keyboard="",originalText="";
 private List<ProsperoInstall.Version> versions=List.of();private ProsperoLibrary.Instance detail;
 private int guideReturn=0,guideTab=0,guideSection=0;private boolean guideTop=false;private ProsperoOfflineAccount offlineAccount;private boolean offlineLaunch;
 private String fabricLoaderVersion="";private String avatar="";private final ProsperoAccountStore accounts;
 private ProsperoAuth.Session session;private Thread worker;private long completed,total,lastProgress;private String[] cached;
 private ProsperoInstall.Receipt receipt;private java.net.URLClassLoader loader;
 ProsperoLauncher(ProsperoAuth auth)throws Exception{this(auth,Path.of(System.getProperty("ps5.launcher.root","/download0/ProsperoCraft")),null);}
 ProsperoLauncher(ProsperoAuth auth,Path root,ProsperoInstall.Source source)throws Exception{this.auth=auth;library=new ProsperoLibrary(root);accounts=new ProsperoAccountStore(root);offlineAccount=ProsperoOfflineAccount.load(root,System.currentTimeMillis());fabric=new ProsperoFabric(root.resolve("cache"));installer=source==null?new ProsperoInstall(root.resolve("cache")):new ProsperoInstall(root.resolve("cache"),source);if(library.settings().showIntro&&!Boolean.getBoolean("ps5.launcher.resume")){page=7;row=1;}if(ProsperoChannel.tempGameTest()&&accounts.exists())restoreAccount();}
 static String[] run(Menu menu)throws Exception {
  current=new ProsperoLauncher(new ProsperoAuth());
  if(!menu.show()){current.cancel();throw new IllegalStateException("Launcher display handoff failed;game not started");}
  synchronized(current){if(!current.launch)throw new IllegalStateException("No launch selected");}
  return current.arguments(null,null);
 }
 static String prepareControlifyKeyboard()throws java.io.IOException{return ProsperoControlifyKeyboard.prepare(selectedWork(),current.detail.version,current.detail.loader);}
 static Path selectedWork(){return current.library.game(current.detail);}
 static String controllerBindings(){return ProsperoInput.hint(current.library.settings().controllerKeys);}
 static ClassLoader gameLoader(){return current.loader;}
 static String launchIdentity(){
  var instance=current.detail;
  String identity="PS5_LAUNCH game="+instance.version+" loader="+instance.loader+" window="+current.receipt.window+" fabric262_test="+developmentTest(instance.version,instance.loader);
  if("fabric".equals(instance.loader))identity+=" fabric_loader="+current.fabricLoaderVersion;
  return identity;
 }
 static String gameMain(){return "fabric".equals(current.detail.loader)?ProsperoFabric.MAIN:"net.minecraft.client.main.Main";}
 static ClassLoader runningGameLoader(){return "fabric".equals(current.detail.loader)?Thread.currentThread().getContextClassLoader():gameLoader();}
 static void configureGameLaunch(){if("fabric".equals(current.detail.loader))ProsperoFabric.configure(current.loader,current.library.root.resolve("cache/versions/"+current.detail.version+"/client.jar"),current.detail.version);}
 static boolean selectedResidentJna(){return current.receipt!=null&&current.receipt.classpath.stream().anyMatch(p->p.endsWith("/jna-5.19.1.jar"));}
 static boolean verifySelected()throws Exception{current.installer.verify(current.receipt);return true;}
 public static String[] nativeTick(int buttons){return current.tick(buttons);}
 synchronized void cancel(){generation++;code="";uri="";if(worker!=null&&worker.isAlive()){worker.interrupt();busy=true;task="STOPPING";}else{busy=false;task="";}cached=null;}
 private void runTask(String kind,Job job){if(busy){message="A task is running. Circle cancels it.";return;}busy=true;task=kind;int attempt=++generation;worker=new Thread(()->{try{job.run(attempt);}catch(Exception failure){synchronized(this){if(generation==attempt){message=failure instanceof ProsperoAuth.Failure?failure.getMessage():friendly(failure);feedback("error");System.err.println("PS5_LAUNCHER task="+kind+" result=FAILED storageCode="+(failure instanceof java.io.IOException io?ProsperoStorage.code(io):"NONE"));}}}finally{synchronized(this){if(generation==attempt||worker==Thread.currentThread()){busy=false;task="";code="";uri="";cached=null;}}}},"ProsperoCraft "+kind);worker.setDaemon(true);worker.start();}
 interface Job{void run(int attempt)throws Exception;}
 private static String friendly(Exception error){if(error instanceof java.io.IOException io&&java.util.Set.of("ENOSPC","QUOTA").contains(ProsperoStorage.code(io)))return "App storage is full. Refresh the loader metadata and relaunch; this build requests4GiB.";if(error instanceof IllegalArgumentException)return "Use1-40 letters, numbers, spaces or ._()!+-";if(error instanceof java.io.IOException)return error.getMessage()==null?"Storage or download error. Retry when ready.":error.getMessage();return "This action could not finish. Your worlds are kept. Try again.";}
 private synchronized boolean cancelled(int attempt){return attempt!=generation;}
 private String defaultName(String version){String base=(draftLoader==1?"Fabric ":"Vanilla ")+version;if(base.length()>34)base=base.substring(0,34);String name=base;int n=2;var existing=library.instances().stream().map(i->i.name).toList();while(existing.contains(name))name=base+" ("+(n++)+")";return name;}
 private void catalog(){message="Getting available26.x versions";runTask("CATALOG",attempt->{var result=installer.catalog(library.settings().snapshots,()->cancelled(attempt));synchronized(this){if(!cancelled(attempt)){versions=result;versionChoice=0;if(draftName.isEmpty()&&!versions.isEmpty())draftName=defaultName(versions.get(0).id());message="Choose a version, name and icon.";cached=null;}}});}
 private ProsperoAuth.View accountView(int attempt){return new ProsperoAuth.View(){public void stage(String text){synchronized(ProsperoLauncher.this){if(!cancelled(attempt)){message=text;cached=null;}}}public void code(String value,String address){synchronized(ProsperoLauncher.this){if(!cancelled(attempt)){code=value;uri=address;cached=null;}}}};}
 private void acceptAccount(ProsperoAuth.Session result,int attempt)throws Exception {
  synchronized(this){if(cancelled(attempt))return;session=result;avatar="";selectTab(0);code="";uri="";message="Connected. Owned Minecraft Java is ready to play.";feedback("success");cached=null;try{accounts.save(auth.refreshCredential(result));}catch(Exception storage){message="Connected. Account could not be saved on this console.";}}
  String face="";try{face=ProsperoAvatar.fetch(auth.skin(result));if(face.isEmpty()&&auth.skin(result).isEmpty())face=ProsperoAvatar.defaultFace(library.root,result.id);}catch(Exception unavailable){}
  synchronized(this){if(!cancelled(attempt)&&session==result){avatar=face;cached=null;}}
 }
 private void restoreAccount(){runTask("ACCOUNT",attempt->{String refresh;try{refresh=accounts.load();}catch(ProsperoAccountStore.SignInRequired changedApp){synchronized(this){if(!cancelled(attempt)){message=changedApp.getMessage();cached=null;}}return;}if(refresh.isEmpty())return;try{acceptAccount(auth.resume(refresh,accountView(attempt),()->cancelled(attempt)),attempt);}catch(ProsperoAuth.Failure failure){if(failure.code.equals("DECLINED")||failure.code.equals("REGISTRATION"))accounts.clear();throw failure;}});}
 private void signIn(){if(busy)return;message="Connecting to Microsoft";runTask("AUTH",attempt->acceptAccount(auth.signIn(accountView(attempt),()->cancelled(attempt)),attempt));}

 private void install(boolean play){if(detail==null||busy)return;var instance=detail;message="Preparing "+instance.version;completed=0;total=1;runTask("DOWNLOAD",attempt->{
  ProsperoInstall.Version version=versions.stream().filter(v->v.id().equals(instance.version)).findFirst().orElse(null);
  if(version==null)version=installer.catalog(true,()->cancelled(attempt)).stream().filter(v->v.id().equals(instance.version)).findFirst().orElseThrow(()->new java.io.IOException("This version is not in the publisher catalog"));
  var installed=installer.install(version,library.settings().workers,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){completed=done;total=size;long now=System.currentTimeMillis();if(now-lastProgress>100||done==size){message=text;lastProgress=now;cached=null;}}}},()->cancelled(attempt));
  if("fabric".equals(instance.loader))fabric.install(instance.version,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){message=text;cached=null;}}},()->cancelled(attempt));
  if(instance.defaultContentPending&&!ProsperoModrinth.defaultMods(instance.loader).isEmpty()){
   try(var checker=fabric.dependencies(instance.version)){modrinth.installDefaults(library.game(instance),instance.version,instance.loader,checker,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){message=text;completed=done;total=size;cached=null;}}},()->cancelled(attempt));}
   ProsperoInstall.active(()->cancelled(attempt));library.defaultContentInstalled(instance);
  }
  if(play)repairDependencies(instance,attempt,false);
  synchronized(this){if(!cancelled(attempt)){library.ready(instance,true);if(session!=null&&avatar.isEmpty()&&auth.skin(session).isEmpty())try{avatar=ProsperoAvatar.defaultFace(library.root,session.id);}catch(Exception ignored){}message="Download complete. Ready for your next world.";feedback("success");if(play)prepareLaunch(instance,installed);cached=null;}}
 });}
 private void duplicateInstance(){
  if(detail==null||busy)return;var original=detail;
  runTask("DUPLICATE",attempt->{var copy=library.duplicate(original,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){message=text;completed=done;total=size;cached=null;}}},()->cancelled(attempt));
   synchronized(this){if(!cancelled(attempt)){detail=copy;selected=library.instances().indexOf(copy);page=4;row=0;top=false;message="Created "+copy.name;feedback("success");cached=null;}}
  });
 }
 private void repairDependencies(ProsperoLibrary.Instance instance,int attempt,boolean offline)throws Exception {
  if(!"fabric".equals(instance.loader))return;
  var game=library.game(instance);
  ProsperoDependencies.verifyVulkan(modrinth.local(game,ProsperoModrinth.Kind.MOD).stream().map(file->game.resolve("mods").resolve(file.filename())).toList());
  try(var checker=fabric.dependencies(instance.version)){modrinth.repair(library.game(instance),instance.version,instance.loader,checker,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){message=text;completed=done;total=size;cached=null;}}},()->cancelled(attempt),offline);}
 }
 private void prepareLaunch(ProsperoLibrary.Instance instance,ProsperoInstall.Receipt installed)throws Exception {prepareLaunch(instance,installed,false);}
 private void prepareLaunch(ProsperoLibrary.Instance instance,ProsperoInstall.Receipt installed,boolean offline)throws Exception {
  if(offline&&(!ProsperoChannel.offline()||offlineAccount==null||!offlineAccount.valid(System.currentTimeMillis())))throw new java.io.IOException("Offline profile expired. Verify your account again on your computer.");
  if(ProsperoChannel.tempGameTest()&&!offline&&(session==null||!session.valid(System.currentTimeMillis())))throw new java.io.IOException("Sign in with an owning Microsoft account before playing the full game.");
  if(installed.javaMajor>Runtime.version().feature())throw new java.io.IOException("This instance requires Java "+installed.javaMajor+"; this app includes Java "+Runtime.version().feature());
  if(!launchable(instance.version,instance.loader)||!("SDL".equals(installed.window)||("26.2".equals(instance.version)&&"GLFW".equals(installed.window)))){message="Coming soon for this version. Downloads are kept.";return;}

  installer.verify(installed);receipt=installed;loader=installer.loader(installed);if("fabric".equals(instance.loader)){var f=fabric.read(instance.version);loader=fabric.loader(f,loader);fabricLoaderVersion=f.loader;}detail=instance;offlineLaunch=offline;launchPrepared=true;launch=!awaitingTutorial;message="Starting "+instance.name;
 }
 static boolean supported(String version){return "26.2".equals(version)||"26.3".equals(version)||snapshot(version);}
 static boolean supported(String version,String loader){return supported(version);}
 static boolean developmentTest(String version,String loader){return false;}
 static boolean launchable(String version,String loader){return supported(version,loader)||developmentTest(version,loader);}
 private boolean draftSupported(String version){return launchable(version,draftLoader==1?"fabric":"vanilla");}
 private String fabricLabel(){return "Fabric";}
 static boolean selectedGlfw(){return current.receipt!=null&&"26.2".equals(current.receipt.version)&&"GLFW".equals(current.receipt.window);}
 static boolean snapshot(String version){return java.util.Set.of("26.4-snapshot-1","26.4-snapshot-2","26.4-snapshot-3","26.4-snapshot-4","26.4-snapshot-5","26.4-snapshot-6").contains(version==null?"":version);}
 private void play(){if(detail==null||busy)return;if(!launchable(detail.version,detail.loader)){message="26.2".equals(detail.version)&&"fabric".equals(detail.loader)?"Fabric for Minecraft 26.2 is coming soon. Your downloads and worlds are kept.":"Coming soon. This build launches 26.2 Vanilla, 26.3 and 26.4 snapshots 1–6.";feedback("error");return;}if(ProsperoChannel.tempGameTest()&&(session==null||!session.valid(System.currentTimeMillis()))){page=3;tab=2;top=false;row=0;signIn();return;}awaitingTutorial=ProsperoChannel.tempGameTest()&&library.settings().showControls;if(awaitingTutorial){page=11;row=1;top=false;launchPrepared=false;}if(!detail.ready){install(true);return;}var instance=detail;runTask("VERIFY",attempt->{var installed=installer.receipt(instance.version);installer.verify(installed);repairDependencies(instance,attempt,false);synchronized(this){if(!cancelled(attempt))prepareLaunch(instance,installed);}});}
 private void playOffline(){
  if(detail==null||busy)return;
  if(!ProsperoChannel.offline()){message="This is the Demo branch.";return;}
  offlineAccount=ProsperoOfflineAccount.load(library.root,System.currentTimeMillis());
  if(offlineAccount==null){message="A verified offline profile is required. Export it from your computer.";return;}
  if(!launchable(detail.version,detail.loader)||!detail.ready){message="Download a supported instance before playing offline.";return;}
  var instance=detail;runTask("VERIFY",attempt->{var installed=installer.receipt(instance.version);repairDependencies(instance,attempt,true);synchronized(this){if(!cancelled(attempt))prepareLaunch(instance,installed,true);}});
 }
 private void beginName(int back){keyboardReturn=back;page=6;keyboard=back==12?contentQuery:back==5?detail.name:draftName;originalText=keyboard;key=0;}
 private void keyboard(int buttons)throws Exception {
  final String chars=lowercase?"1234567890qwertyuiopasdfghjkl_zxcvbnm .-":"1234567890QWERTYUIOPASDFGHJKL_ZXCVBNM .-";
  if((buttons&0x100)!=0)lowercase=!lowercase;
  if((buttons&0x200)!=0&&keyboard.length()<40)keyboard+=" ";
  if((buttons&0x8)!=0)keyboard="";
  if((buttons&0x80)!=0)key=(key+39)%40;if((buttons&0x20)!=0)key=(key+1)%40;if((buttons&0x10)!=0)key=(key+30)%40;if((buttons&0x40)!=0)key=(key+10)%40;
  if((buttons&0x4000)!=0&&keyboard.length()<40)keyboard+=chars.charAt(key);
  if((buttons&0x1000)!=0&&!keyboard.isEmpty())keyboard=keyboard.substring(0,keyboard.length()-1);
  if((buttons&0x8000)!=0){if(keyboardReturn==12){contentQuery=keyboard.strip();contentOffset=0;contentHits=List.of();browse();}else if(keyboardReturn==5)library.rename(detail,keyboard);else{draftName=ProsperoLibrary.clean(keyboard);customName=true;}page=keyboardReturn;}
  if((buttons&0x2000)!=0){keyboard=originalText;page=keyboardReturn;}
 }
 synchronized String[] tick(int buttons){
  String[] before=state();int serial=feedbackSerial;String[] after=tickModel(buttons);
  if(buttons!=0&&serial==feedbackSerial){
   boolean changed=false;for(int at:new int[]{2,8,9,10,11,12,13,15,19,22,24,26,27,28,29,30,31,64,68,75,79})changed|=!before[at].equals(after[at]);
   if(changed)feedback((buttons&0x2000)!=0?"back":(buttons&0xf008)!=0?"confirm":"move");
  }
  return state();
 }
 private int tabPage(){return switch(tab){case 0->0;case 1->2;default->3;};}
 private void selectTab(int next){tab=Math.floorMod(next,3);page=tabPage();top=false;selected=0;row=0;cached=null;}
 private void createInstance(){page=1;tab=0;top=false;row=0;if(versions.isEmpty()&&!busy)catalog();}
 private int cardCount(){return library.instances().size()+1;}
 private void navigateCards(int buttons){int count=cardCount();if((buttons&0x80)!=0)selected=Math.max(0,selected-1);if((buttons&0x20)!=0)selected=Math.min(count-1,selected+1);if((buttons&0x10)!=0){if(selected<4)top=true;else selected-=4;}if((buttons&0x40)!=0)selected=Math.min(count-1,selected+4);}
 private List<String> choices(){return switch(dropdownKind){case 0->versions.stream().map(v->v.id()+(v.type().equals("snapshot")?"  [snapshot]":"")+(draftSupported(v.id())?"":"  [Coming soon]")).toList();case 1,2->List.of(ProsperoLibrary.ICONS);case 3->java.util.stream.IntStream.range(0,ProsperoLibrary.RESOLUTIONS.length).mapToObj(ProsperoLibrary::resolutionLabel).toList();case 4->List.of("1","2","3","4","5","6");case 6->List.of("Vanilla",fabricLabel(),"NeoForge  [Coming soon]");case 7->ProsperoInput.LABELS;case 8->List.of(THEMES);default->List.of(BACKGROUNDS);};}
 private void dropdown(int kind,int choice){dropdownKind=kind;dropdownChoice=choice;dropdownReturn=page;dropdownRow=row;page=10;row=choice;top=false;}
 private void choose()throws Exception {switch(dropdownKind){case 0->{versionChoice=row;if(!customName)draftName=defaultName(versions.get(row).id());}case 1->draftIcon=row;case 2->library.icon(detail,row);case 3->{library.settings().resolution=row;library.save();}case 4->{library.settings().workers=row+1;library.save();}case 5->{library.settings().background=row+1;library.save();}case 8->{int before=library.settings().theme;library.settings().theme=row;try{library.save();}catch(Exception failed){library.settings().theme=before;throw failed;}}case 7->{int before=library.settings().controllerKeys[bindingIndex];library.settings().controllerKeys[bindingIndex]=ProsperoInput.CODES.get(row);try{library.save();}catch(Exception failed){library.settings().controllerKeys[bindingIndex]=before;throw failed;}}case 6->{if(row==2)throw new java.io.IOException("NeoForge is coming soon");draftLoader=row;if(!customName&&!versions.isEmpty())draftName=defaultName(versions.get(versionChoice).id());}}page=dropdownReturn;row=dropdownRow;}
 private void openContent(ProsperoModrinth.Kind kind)throws Exception {contentKind=kind;shadowScale=kind==ProsperoModrinth.Kind.SHADER?ProsperoShaderSettings.scale(library.game(detail)):100;contentInstalled=false;activeContentIcon="";contentQuery="";contentOffset=0;contentTotal=0;contentHits=List.of();contentQueue=modrinth.queue(library.game(detail));page=12;row=0;top=false;browse();}
 private void browse(){if(busy)return;var instance=detail;var kind=contentKind;String query=contentQuery;int offset=contentOffset;boolean installedView=contentInstalled;message=installedView?"Reading installed files":"Loading Modrinth";
  runTask("MODRINTH",attempt->{
   var locals=modrinth.local(library.game(instance),kind);var result=installedView?new ProsperoModrinth.Results(List.of(),locals.size()):modrinth.search(kind,instance.version,instance.loader,query,offset,()->cancelled(attempt));
   synchronized(this){if(cancelled(attempt)||detail!=instance)return;localContent=locals;contentHits=result.hits();contentTotal=result.total();message=installedView?(locals.isEmpty()?"Nothing installed in this category.":"Installed in this instance. Files are kept when you close the game."):contentHits.isEmpty()?"No compatible results. Try another search.":"Most downloaded for "+instance.version;cached=null;}
   var icons=new HashMap<String,String>();
   if(installedView){for(var local:locals.subList(Math.min(offset,locals.size()),Math.min(offset+4,locals.size())))icons.put(local.project(),modrinth.icon(library.game(instance),local.project(),"",()->cancelled(attempt)));}
   else for(var hit:result.hits())icons.put(hit.id(),modrinth.icon(library.game(instance),hit.id(),hit.icon(),()->cancelled(attempt)));
   synchronized(this){if(!cancelled(attempt)&&detail==instance){contentIcons.putAll(icons);cached=null;}}
  });
 }
 private int contentRows(){return contentInstalled?Math.min(4,Math.max(0,localContent.size()-contentOffset)):contentHits.size();}
 private void contentInput(int buttons)throws Exception {
  if((buttons&0x2000)!=0){if(busy){cancel();message="Cancelled. Verified downloads are kept.";}else{page=5;row=2+contentKind.ordinal();}return;}
  if(contentInstalled&&row>=20&&row<26){
   if((buttons&0x80)!=0)row-=16;
   if((buttons&0x10)!=0)row=row==20?10:row-1;
   if((buttons&0x40)!=0)row=Math.min(19+contentRows(),row+1);
  }else if(contentInstalled&&row>=4&&row<10){
   if((buttons&0x20)!=0)row+=16;
   if((buttons&0x10)!=0)row=row==4?2:row-1;
   if((buttons&0x40)!=0)row=Math.min(3+contentRows(),row+1);
  }else{
   if((buttons&0x80)!=0&&(row<4||row==10||row==11))row=row<2?0:row==10?(contentKind==ProsperoModrinth.Kind.SHADER?11:3):row==11?3:2;
   if((buttons&0x20)!=0&&(row<4||row==11))row=row<2?1:row==2?3:row==11?10:contentKind==ProsperoModrinth.Kind.SHADER?11:10;
   if((buttons&0x10)!=0)row=row<2?row:row==10||row==11?1:row<4?row-2:row==4?2:row-1;
   if((buttons&0x40)!=0)row=row<2?row+2:row<4||row==10||row==11?(contentRows()==0?row:4):Math.min(3+contentRows(),row+1);
  }
  if((buttons&0x4000)==0||busy)return;
  if(row==11&&contentKind==ProsperoModrinth.Kind.SHADER){shadowScale=ProsperoShaderSettings.toggle(library.game(detail));message="Shadow map scale "+shadowScale+"% next launch. "+(shadowScale==50?"Lower shadow detail, one quarter of the shadow pixels.":"Full shadow resolution.");return;}
  if(row==10){contentInstalled=!contentInstalled;contentOffset=0;row=10;browse();return;}
  if(row==0){contentInstalled=false;beginName(12);return;}
  if(row==1){var instance=detail;message="Preparing download queue";completed=0;total=1;runTask("CONTENT",attempt->{
   try(var checker="fabric".equals(instance.loader)?fabric.dependencies(instance.version):null){
    modrinth.downloadAll(library.game(instance),instance.version,instance.loader,(text,done,size)->{synchronized(this){if(!cancelled(attempt)){message=text;completed=done;total=size;cached=null;}}},()->cancelled(attempt),file->{String icon=modrinth.icon(library.game(instance),file.project(),"",()->cancelled(attempt));synchronized(this){if(!cancelled(attempt)){activeContentIcon=icon;cached=null;}}},checker);
   }finally{
    synchronized(this){if(!cancelled(attempt)){contentQueue=modrinth.queue(library.game(instance));localContent=modrinth.local(library.game(instance),contentKind);activeContentIcon="";cached=null;}}
   }
   synchronized(this){if(!cancelled(attempt)){message="Downloads and required dependencies complete.";feedback("success");cached=null;}}
  });return;}

  if(row==2||row==3){int next=row==2?Math.max(0,contentOffset-4):contentOffset+4;if(next!=contentOffset&&next<contentTotal){contentOffset=next;contentHits=List.of();browse();}return;}
  if(contentInstalled){if(row>=20&&row-20<contentRows()){pendingUninstall=localContent.get(contentOffset+row-20);uninstallReturnRow=row;page=14;row=0;}else message="Press RIGHT to select Uninstall.";return;}
  if(row<4||row-4>=contentHits.size())return;
  var hit=contentHits.get(row-4);if(localContent.stream().anyMatch(i->i.project().equals(hit.id()))){message="Already installed. Open Installed to see the file.";return;}modrinth.toggle(library.game(detail),new ProsperoModrinth.Selection(hit.id(),hit.title(),contentKind));contentQueue=modrinth.queue(library.game(detail));
 }
 private String[] desktopInput(int command){
  int tag=command>>>28;
  if(tag==1){
   int expected=(command>>>20)&255,kind=(command>>>16)&15,target=command&0x7fff;
   if(expected!=page)return state();
   boolean click=(command&0x8000)!=0;
   if(kind==0){if(click&&page!=6&&!(page>=7&&page<=11)&&page!=14)selectTab(target);}
   else if(kind==1&&page==0&&target>=0&&target<=library.instances().size()){selected=target;top=false;if(click)return tickModel(0x4000);}
   else if(kind==2&&page==6&&target<40){key=target;if(click)return tickModel(0x4000);}
   else if(kind==4&&click){int[] actions={0x1000,0x200,0x100,0x2000,0x8000,0x80,0x20,0x8000,0x1000};if(target<actions.length)return tickModel(actions[target]);}
   else if(kind==3&&target<32){row=target;top=false;if(click)return tickModel(0x4000);}
  }else if(tag==2){int key=command&255;
   if(key==1)return tickModel(page==6?0x8000:0x4000);
   if(key==2&&page==6){if(!keyboard.isEmpty())keyboard=keyboard.substring(0,keyboard.offsetByCodePoints(keyboard.length(),-1));}
   if(key==3||key==4){if(page==6)return state();if(page==7||page==9||page==11||page==14)row=1-row;else if(page==10||page==13)return tickModel(key==3?0x40:0x10);else return tickModel(key==3?0x800:0x400);}
  }else if(tag==3&&page==6&&!busy){char ch=(char)(command&127);if(ch>=32&&ch<127&&keyboard.length()<40)keyboard+=ch;}
  cached=null;return state();
 }
 private String[] tickModel(int buttons){
  if((buttons>>>28)!=0)return desktopInput(buttons);
  try{
   if(page==14){
    if(busy)return state();
    if((buttons&0x2000)!=0){page=12;row=uninstallReturnRow;pendingUninstall=null;}
    else{if((buttons&0x90)!=0)row=0;if((buttons&0x60)!=0)row=1;
     if((buttons&0x4000)!=0){if(row==0){page=12;row=uninstallReturnRow;pendingUninstall=null;}
      else{var instance=detail;var item=pendingUninstall;message="Uninstalling "+item.filename();runTask("UNINSTALL",attempt->{boolean cleaned=modrinth.uninstall(library.game(instance),item);var locals=modrinth.local(library.game(instance),contentKind);synchronized(this){if(!cancelled(attempt)){localContent=locals;contentTotal=locals.size();contentOffset=Math.min(contentOffset,Math.max(0,(locals.size()-1)/4*4));page=12;row=locals.isEmpty()?10:4;pendingUninstall=null;message="Uninstalled "+item.filename()+(cleaned?".":". Storage cleanup pending.");feedback("success");cached=null;}}});}
     }
    }if(buttons!=0)cached=null;return state();
   }
   if(page==13){
    if((buttons&0x2000)!=0){page=2;row=5;}else{if((buttons&0x10)!=0)row=Math.max(0,row-1);if((buttons&0x40)!=0)row=Math.min(22,row+1);if((buttons&0x80)!=0)row=Math.max(0,row-7);if((buttons&0x20)!=0)row=Math.min(22,row+7);if((buttons&0x4000)!=0){if(row==0){library.settings().controllerKeys=ProsperoInput.DEFAULT.clone();library.save();message="Default controller bindings restored.";}else{bindingIndex=row+7;int choice=ProsperoInput.CODES.indexOf(library.settings().controllerKeys[bindingIndex]);dropdown(7,Math.max(0,choice));}}}if(buttons!=0)cached=null;return state();
   }
   if(page==12){contentInput(buttons);if(buttons!=0)cached=null;return state();}
   if(page==10){int count=choices().size();if((buttons&0x10)!=0)row=Math.max(0,row-1);if((buttons&0x40)!=0)row=Math.min(count-1,row+1);if((buttons&0x80)!=0)row=Math.max(0,row-8);if((buttons&0x20)!=0)row=Math.min(count-1,row+8);if((buttons&0x2000)!=0){page=dropdownReturn;row=dropdownRow;}else if((buttons&0x4000)!=0&&count>0)choose();if(buttons!=0)cached=null;return state();}
   if(page==9){
    if((buttons&0x2000)!=0){page=5;row=6;}
    else if((buttons&0x4008)!=0&&busy){message="Wait for the current task before deleting an instance.";feedback("error");}
    else{if((buttons&0x90)!=0)row=0;if((buttons&0x60)!=0)row=1;
     if((buttons&0x4000)!=0){if(row==0){page=5;row=6;}else{boolean cleaned=library.delete(detail);detail=null;selected=0;page=0;tab=0;top=false;row=0;message=cleaned?"Instance and its worlds permanently deleted.":"Instance removed. Storage cleanup will finish on next launch.";}}}
    if(buttons!=0)cached=null;return state();
   }
   if(page==11){
    if((buttons&0x8)!=0){guideReturn=11;guideTab=tab;guideTop=top;guideSection=0;page=8;cached=null;return state();}
    if((buttons&0x80)!=0)row=1;if((buttons&0x20)!=0)row=0;
    if((buttons&0x2000)!=0){cancel();page=4;row=0;launchPrepared=false;awaitingTutorial=false;}
    else if((buttons&0x4000)!=0){if(row==0){library.settings().showControls=!library.settings().showControls;library.save();}else if(launchPrepared){awaitingTutorial=false;launch=true;}else message="Preparing Minecraft. Continue when loading is ready.";}
    if(buttons!=0)cached=null;return state();
   }
   if(page==7){if((buttons&0x80)!=0)row=1;if((buttons&0x20)!=0)row=0;if((buttons&0x4000)!=0){if(row==0){library.settings().showIntro=!library.settings().showIntro;library.save();}else{page=0;tab=0;row=0;}}if(buttons!=0)cached=null;return state();}
   if(page==8){if((buttons&0x2008)!=0){page=guideReturn;tab=guideTab;top=guideTop;}else if((buttons&0x20)!=0)guideSection=(guideSection+1)%5;else if((buttons&0x80)!=0)guideSection=Math.floorMod(guideSection-1,5);if(buttons!=0)cached=null;return state();}
   if(page==6){keyboard(buttons);if(buttons!=0)cached=null;return state();}
   if((buttons&0x8)!=0){guideReturn=page;guideTab=tab;guideTop=top;guideSection=0;page=8;cached=null;return state();}
   if((buttons&0xc00)!=0){selectTab(tab+((buttons&0x800)!=0?1:-1));return state();}
   if((buttons&0x2000)!=0){if(busy){cancel();message="Cancelled. Verified downloads are kept.";}page=tabPage();top=false;row=0;selected=0;cached=null;return state();}
   if(top){if((buttons&0xa0)!=0){selectTab(tab+((buttons&0x20)!=0?1:-1));return state();}if((buttons&0x4040)!=0){top=false;row=0;}cached=null;return state();}
   if(page==0){navigateCards(buttons);
    if((buttons&0x4000)!=0&&!top){if(selected==library.instances().size())createInstance();else{detail=library.instances().get(selected);page=4;row=0;}}
    if(buttons!=0)cached=null;return state();
   }
   if(page==5){
    if((buttons&0x80)!=0){if(row==3)row=2;else if(row==7)row=4;else if(row==6)row=5;}
    if((buttons&0x20)!=0){if(row==2)row=3;else if(row==4)row=7;else if(row==5)row=6;}
    if((buttons&0x10)!=0){if(row==0)top=true;else row=switch(row){case 1->0;case 2,3->1;case 4->2;case 7->3;case 5->4;default->7;};}
    if((buttons&0x40)!=0)row=switch(row){case 0->1;case 1->2;case 2->4;case 3->7;case 4->5;case 7->6;default->row;};
   }else if((buttons&0x10)!=0){if(row==0)top=true;else row--;}
   if(page!=5&&(buttons&0x40)!=0)row=Math.min(page==1?4:page==2?6:page==3?0:page==4?(ProsperoChannel.offline()&&offlineAccount!=null?3:2):page==5?6:2,row+1);
   int direction=(buttons&0x80)!=0?-1:(buttons&0x20)!=0?1:0;
   if(!top&&page==1&&direction!=0&&!busy){if(row==0&&!versions.isEmpty()){versionChoice=Math.floorMod(versionChoice+direction,versions.size());if(!customName)draftName=defaultName(versions.get(versionChoice).id());}if(row==3)draftIcon=Math.floorMod(draftIcon+direction,ProsperoLibrary.ICONS.length);}
   if(!top&&page==5&&row==1&&direction!=0)library.icon(detail,Math.floorMod(detail.icon+direction,ProsperoLibrary.ICONS.length));
   if(!top&&page==2&&direction!=0){var settings=library.settings();if(row==1)settings.workers=Math.max(1,Math.min(6,settings.workers+direction));if(row==2)settings.reducedMotion=!settings.reducedMotion;if(row==3){settings.snapshots=!settings.snapshots;versions=List.of();}if(row==4)settings.showIntro=!settings.showIntro;library.save();}
   if(!top&&page==2&&(buttons&0x1000)!=0){library.settings().vibration=!library.settings().vibration;library.save();}
   if(!top&&page==2&&(buttons&0x8000)!=0){dropdown(5,library.settings().background-1);cached=null;return state();}
   if((buttons&0x4000)!=0){
    if(!top&&page==1&&!busy){if(row==0){if(versions.isEmpty())catalog();else{dropdown(0,versionChoice);cached=null;return state();}}if(row==1){dropdown(6,draftLoader);cached=null;return state();}if(row==2)beginName(1);if(row==3){dropdown(1,draftIcon);cached=null;return state();}if(row==4){if(versions.isEmpty())throw new java.io.IOException("Choose a version first");detail=library.add(draftName,versions.get(versionChoice).id(),draftIcon,draftLoader==1?"fabric":"vanilla");selected=library.instances().size()-1;page=4;row=0;install(false);customName=false;draftName=defaultName(versions.get(versionChoice).id());}}
    else if(page==2){if(row==6){dropdown(8,library.settings().theme);cached=null;return state();}if(row==5){page=13;row=0;cached=null;return state();}var settings=library.settings();if(row==0){dropdown(3,settings.resolution);cached=null;return state();}if(row==1){dropdown(4,settings.workers-1);cached=null;return state();}if(row==2)settings.reducedMotion=!settings.reducedMotion;if(row==3){settings.snapshots=!settings.snapshots;versions=List.of();}if(row==4)settings.showIntro=!settings.showIntro;library.save();}
    else if(page==3&&row==0){if(session==null)signIn();else{cancel();session=null;avatar="";accounts.clear();message="Signed out. Saved account removed from this console.";}}
    else if(!top&&page==4){if(row==0){play();cached=null;return state();}else if(row==1){page=5;row=0;}else if(row==2)install(false);else if(row==3)playOffline();}
    else if(page==5){if(row==7){duplicateInstance();cached=null;return state();}if(row>=2&&row<=4&&!busy){openContent(ProsperoModrinth.Kind.values()[row-2]);cached=null;return state();}if(row==0)beginName(5);if(row==1){dropdown(2,detail.icon);cached=null;return state();}if(row==5){page=4;row=0;}if(row==6){if(busy){message="Wait for the current task before deleting an instance.";feedback("error");}else{page=9;row=0;}}}
   }
   if(buttons!=0)cached=null;
  }catch(Exception error){message=friendly(error);feedback("error");}
  return state();
 }
 private String[] state(){
  if(cached!=null)return cached;String[] f=new String[FIELD_COUNT];Arrays.fill(f,"");
  f[0]="Instances";f[1]="";f[2]=message;f[3]=code;f[4]=uri;f[5]=session==null?"Not signed in":session.name;f[6]=detail!=null&&developmentTest(detail.version,detail.loader)?"DEV TEST - PLAY":detail!=null&&!launchable(detail.version,detail.loader)?"COMING SOON":ProsperoChannel.tempGameTest()&&(session==null||!session.valid(System.currentTimeMillis()))?"PLAY - Sign in":detail!=null&&detail.ready?(ProsperoChannel.tempGameTest()?"PLAY":"PLAY DEMO"):"DOWNLOAD & PLAY";f[7]=page==8?"LEFT / RIGHT Pages     CIRCLE Back":page==11||page==7?"LEFT / RIGHT Choose     X Confirm":page==9?"X Confirm     CIRCLE No":busy?"CIRCLE Cancel":"L1 / R1 Pages     X Select     CIRCLE Back     OPTIONS Controls";f[8]=busy?task:session==null?"MICROSOFT ACCOUNT":"CONNECTED";f[9]=""+selected;f[10]=launch?"LAUNCH":"WAIT";f[11]=""+page;f[12]=""+tab;f[13]=""+library.instances().size();f[14]=""+(selected/8*8);f[15]=""+(top?-1:row);f[16]=detail==null?"":detail.name;f[17]=detail==null?"":detail.version+("fabric".equals(detail.loader)?" / Fabric":" / Vanilla");f[18]=""+(detail==null?1:detail.icon);f[19]=detail==null?"":detail.ready?"READY":"NOT DOWNLOADED";f[20]=""+(total==0?0:Math.min(1000,completed*1000/total));f[21]=total>1?String.format(java.util.Locale.ROOT,"%.0f / %.0f MB",completed/1048576.0,total/1048576.0):"";f[22]=draftName;f[23]=versions.isEmpty()?"Select to refresh versions":versions.get(versionChoice).id();f[24]=""+draftIcon;f[25]=ProsperoLibrary.resolutionLabel(library.settings().resolution);f[26]=""+library.settings().workers;f[27]=library.settings().snapshots?"ON":"OFF";f[28]=top?"TOP":"CONTENT";f[29]=keyboard;f[30]=library.settings().reducedMotion?"ON":"OFF";f[31]=""+key;
  var all=library.instances();int start=selected/8*8;
  f[13]=""+(all.size()+1);for(int i=0;i<8&&start+i<=all.size();i++){int at=32+i*4;if(start+i==all.size()){f[at]="";f[at+2]="-1";f[at+3]="ADD";}else{var instance=all.get(start+i);f[at]=instance.name;f[at+1]=instance.version+("fabric".equals(instance.loader)?" / Fabric":"");f[at+2]=""+instance.icon;f[at+3]=developmentTest(instance.version,instance.loader)?"DEV TEST":!launchable(instance.version,instance.loader)?"COMING SOON":instance.ready?"READY":"DOWNLOAD";}}
  if(page==10){List<String> options=choices();int first=row/8*8;f[82]=switch(dropdownKind){case 0->"Choose version";case 1,2->"Choose instance icon";case 3->"Game resolution";case 4->"Parallel downloads";case 6->"Choose loader";case 7->"Choose key or mouse button";case 8->"Color theme";default->"Animated background";};f[83]=""+options.size();f[84]=""+first;for(int i=0;i<8&&first+i<options.size();i++)f[85+i]=options.get(first+i);f[93]=""+dropdownKind;}
  if(page==14&&pendingUninstall!=null){f[82]="Uninstall this file?";f[85]=pendingUninstall.filename();f[96]=contentIcons.getOrDefault(pendingUninstall.project(),"");f[70]="Only this file is removed. Worlds and settings are kept. Mods that depend on it may stop working.";}
  if(page==13){f[82]="Controller keybinds";int first=row/7*7;f[83]="23";f[84]=""+first;for(int n=0;n<7&&first+n<23;n++){int index=first+n;f[85+n]=index==0?"Restore default controller bindings":ProsperoInput.ACTIONS[index+7]+"  :  "+ProsperoInput.label(library.settings().controllerKeys[index+7]);}f[70]="USB keyboard/mouse use Minecraft Controls. Controller menu controls stay available.";}
  if(page==1)f[82]=draftLoader==1?fabricLabel():"Vanilla";
  if(page==12){f[82]=contentKind.title;f[83]=""+contentTotal;f[84]=""+contentOffset;f[91]=""+contentQueue.size();f[92]=contentQuery.isEmpty()?"Search Modrinth...":contentQuery;f[93]=""+contentRows();f[103]=contentInstalled?"INSTALLED":"BROWSE";f[102]=activeContentIcon;for(int n=0;n<contentRows();n++){
   if(contentInstalled){var item=localContent.get(contentOffset+n);f[85+n]="[I] "+item.title();f[96+n]=contentIcons.getOrDefault(item.project(),"");}
   else{var hit=contentHits.get(n);boolean queued=contentQueue.stream().anyMatch(q->q.project().equals(hit.id())&&q.kind()==contentKind);boolean installed=localContent.stream().anyMatch(i->i.project().equals(hit.id()));f[85+n]=(installed?"[I] ":queued?"[X] ":"[ ] ")+hit.title()+"  /  "+hit.downloads()+" downloads";f[96+n]=contentIcons.getOrDefault(hit.id(),"");}
  }f[70]=contentInstalled?"Installed in this instance. RIGHT from Next switches back to Browse.":contentKind==ProsperoModrinth.Kind.MOD?"fabric".equals(detail.loader)?"Fabric mods for "+detail.version+". Required dependencies included.":"Mods need a Fabric instance. Create one with the Fabric loader.":contentKind==ProsperoModrinth.Kind.SHADER?"Vitrail: install the mod from Mods, then choose your pack in-game.":"Downloaded packs are available in Minecraft Resource Packs.";}

  f[80]=avatar;f[81]=session==null?"Sign in":session.name;f[94]=library.settings().showControls?"ON":"OFF";f[95]=page==12?"SHADOWS: "+shadowScale+"%":launchPrepared?"READY":"WAIT";
  f[77]=""+feedbackSerial;f[78]=feedbackCue;f[79]=library.settings().vibration?"ON":"OFF";
  f[104]=""+library.settings().theme;f[75]=""+library.settings().background;f[76]=BACKGROUNDS[library.settings().background-1];
  f[73]=ProsperoChannel.label();f[74]=page==8?""+guideSection:"";
  f[71]=ProsperoChannel.offline()&&offlineAccount!=null&&offlineAccount.valid(System.currentTimeMillis())?"OFFLINE":"";f[72]=offlineAccount==null?"":offlineAccount.name;
  f[69]=detail!=null&&developmentTest(detail.version,detail.loader)?"DEVELOPMENT":detail!=null&&supported(detail.version,detail.loader)?"SUPPORTED":"PENDING";if(page!=12&&page!=13&&page!=14)f[70]=versions.isEmpty()?"":snapshot(versions.get(versionChoice).id())?versions.get(versionChoice).id()+" / supported snapshot. Use a separate world.":draftSupported(versions.get(versionChoice).id())?(ProsperoChannel.tempGameTest()?versions.get(versionChoice).id()+" full game requires Microsoft sign-in.":versions.get(versionChoice).id()+" demo can launch on this build."):"Download available. Play support coming soon.";f[68]=library.settings().showIntro?"ON":"OFF";f[67]="Data and downloads: "+library.root;f[66]=lowercase?"LOWER":"UPPER";f[64]=busy?"BUSY":"IDLE";f[65]=detail!=null&&developmentTest(detail.version,detail.loader)?"Development test. Use a new disposable instance and world; console validation pending.":detail!=null&&!launchable(detail.version,detail.loader)?"Download available. Play support coming soon.":detail!=null&&snapshot(detail.version)?detail.version+" / native SDL gameplay":((detail==null?"26.3":detail.version)+(ProsperoChannel.tempGameTest()?" full game / native ":" demo / native ")+(detail!=null&&"26.2".equals(detail.version)?"GLFW/SDL gameplay":"SDL gameplay"));return cached=f;
 }
 synchronized String[] arguments(Path ignoredWork,Path ignoredAssets)throws Exception {
  if(!launch||detail==null||receipt==null)throw new IllegalStateException("No installed instance selected");
  if(offlineLaunch){if(!ProsperoChannel.offline())throw new java.io.IOException("Offline launch is unavailable in the Demo branch");offlineAccount=ProsperoOfflineAccount.load(library.root,System.currentTimeMillis());if(offlineAccount==null)throw new java.io.IOException("Offline profile needs verification");}
  boolean full=ProsperoChannel.tempGameTest()&&!offlineLaunch;
  if(full&&(session==null||!session.valid(System.currentTimeMillis())))throw new java.io.IOException("Your session expired. Sign in again before launching.");
  String player=full?session.name:offlineLaunch?offlineAccount.name:"PS5Demo",id=full?session.id:offlineLaunch?offlineAccount.id:UUID.nameUUIDFromBytes("OfflinePlayer:PS5Demo".getBytes(java.nio.charset.StandardCharsets.UTF_8)).toString();
  java.util.List<String> args=new java.util.ArrayList<>(java.util.List.of("--username",player,"--uuid",id,"--accessToken",full?session.accessToken():"0","--version",detail.version,"--versionType",snapshot(detail.version)?"snapshot":"release","--gameDir",library.game(detail).toString(),"--assetsDir",library.root.resolve("cache/assets").toString(),"--assetIndex",receipt.assetIndex,"--width",""+ProsperoLibrary.RESOLUTIONS[library.settings().resolution][0],"--height",""+ProsperoLibrary.RESOLUTIONS[library.settings().resolution][1]));if(!full){args.add(0,"--disableChat");args.add(0,"--disableMultiplayer");if(!offlineLaunch)args.add(0,"--demo");}  if("SDL".equals(receipt.window)||("26.2".equals(detail.version)&&"GLFW".equals(receipt.window)))java.util.Collections.addAll(args,"--graphicsBackend","vulkan");return args.toArray(String[]::new);
 }
 @Override public String toString(){return "ProsperoCraft launcher [credentials redacted]";}
}
