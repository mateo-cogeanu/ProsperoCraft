#!/usr/bin/env python3
"""Exercise actual device/Xbox/Minecraft auth state machine without live credentials."""
from pathlib import Path
import subprocess,json,tempfile
ROOT=Path(__file__).resolve().parents[1];jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
cp=':'.join(str(ROOT/'.tools/client'/r['file'])for r in json.loads((ROOT/'client/26.3.lock.json').read_text())['artifacts'])
source=r'''
import com.google.gson.*;import java.util.*;import java.util.concurrent.atomic.*;import java.nio.file.*;
public class AuthCheck {
 static final String MSA="SECRET_MSA",XBL="SECRET_XBL",XSTS="SECRET_XSTS",MC="SECRET_MINECRAFT",DEVICE="SECRET_DEVICE";
 static ProsperoAuth.Reply reply(int status,String json){return new ProsperoAuth.Reply(status,JsonParser.parseString(json).getAsJsonObject());}
 static class Clock implements ProsperoAuth.Clock {long now=1000;List<Long>waits=new ArrayList<>();Runnable after=()->{};public long millis(){return now;}public void sleep(long ms){waits.add(ms);now+=ms;after.run();}}
 static class Script implements ProsperoAuth.Transport {
  ArrayDeque<ProsperoAuth.Reply> q=new ArrayDeque<>();List<ProsperoAuth.Endpoint> endpoints=new ArrayList<>();
  public ProsperoAuth.Reply send(ProsperoAuth.Endpoint e,String method,String type,String body,String bearer){
   endpoints.add(e);
   if(e==ProsperoAuth.Endpoint.DEVICE||e==ProsperoAuth.Endpoint.TOKEN){
    Map<String,String> fields=new HashMap<>();for(String pair:body.split("&")){String[] kv=pair.split("=",2);fields.put(java.net.URLDecoder.decode(kv[0],java.nio.charset.StandardCharsets.UTF_8),java.net.URLDecoder.decode(kv[1],java.nio.charset.StandardCharsets.UTF_8));}
    if(!"f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3".equals(fields.get("client_id"))||fields.containsKey("client_secret")||body.contains("00000000402b5328")||body.contains("MBI_SSL"))throw new AssertionError("registered public client");
    if(!method.equals("POST")||!type.equals("application/x-www-form-urlencoded"))throw new AssertionError("OAuth request format");
    if(e==ProsperoAuth.Endpoint.DEVICE){if(!fields.keySet().equals(Set.of("client_id","scope"))||!fields.get("scope").equals("XboxLive.signin offline_access"))throw new AssertionError("registered device scope");}
    else if("refresh_token".equals(fields.get("grant_type"))){if(!fields.get("scope").equals("XboxLive.signin offline_access")||!fields.containsKey("refresh_token"))throw new AssertionError("refresh scope/credential");}
    else if(!fields.get("grant_type").equals("urn:ietf:params:oauth:grant-type:device_code")||!fields.get("device_code").equals(DEVICE))throw new AssertionError("device grant");
   }
   if(e==ProsperoAuth.Endpoint.XBOX&&!body.contains("\"RpsTicket\":\"d="+MSA+"\""))throw new AssertionError("registered-app RPS ticket");
   if(e==ProsperoAuth.Endpoint.XSTS&&!body.contains(XBL))throw new AssertionError("Xbox token");
   if(e==ProsperoAuth.Endpoint.MINECRAFT&&!body.contains("XBL3.0 x=hash;"+XSTS))throw new AssertionError("identity");
   if(e==ProsperoAuth.Endpoint.LICENSE||e==ProsperoAuth.Endpoint.PROFILE){if(!MC.equals(bearer))throw new AssertionError("bearer missing");}
   else if(bearer!=null)throw new AssertionError("bearer sent to wrong endpoint");
   if(q.isEmpty())throw new AssertionError("unexpected endpoint "+e);return q.removeFirst();
  }
 }
 static class View implements ProsperoAuth.View {String all="";public void stage(String s){all+=s;}public void code(String c,String u){all+=c+u;}}
 static Script standard(){Script s=new Script();s.q.add(reply(200,"{\"device_code\":\""+DEVICE+"\",\"user_code\":\"ABCD-EFGH\",\"verification_uri\":\"https://www.microsoft.com/link\",\"expires_in\":120,\"interval\":5}"));s.q.add(reply(200,"{\"access_token\":\""+MSA+"\"}"));s.q.add(reply(200,"{\"Token\":\""+XBL+"\",\"DisplayClaims\":{\"xui\":[{\"uhs\":\"hash\"}]}}"));s.q.add(reply(200,"{\"Token\":\""+XSTS+"\",\"DisplayClaims\":{\"xui\":[{\"uhs\":\"hash\"}]}}"));s.q.add(reply(200,"{\"access_token\":\""+MC+"\",\"expires_in\":86400}"));s.q.add(reply(200,"{\"items\":[{\"name\":\"game_minecraft\"}]}"));s.q.add(reply(200,"{\"id\":\"0123456789abcdef0123456789abcdef\",\"name\":\"PlayerOne\"}"));return s;}
 static void expect(Script s,Clock c,String code){try{new ProsperoAuth(s,c).signIn(new View(),()->false);throw new AssertionError("accepted failure");}catch(ProsperoAuth.Failure f){if(!f.code.equals(code)||f.toString().contains("SECRET"))throw new AssertionError(f.code);}}
 public static void main(String[]args)throws Exception {
  if(!ProsperoAuth.Endpoint.DEVICE.address.equals("https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode")||!ProsperoAuth.Endpoint.TOKEN.address.equals("https://login.microsoftonline.com/consumers/oauth2/v2.0/token"))throw new AssertionError("consumer OAuth v2 endpoints");
  Script s=standard();Clock c=new Clock();View view=new View();List<ProsperoAuth.Reply> list=new ArrayList<>(s.q);s.q.clear();s.q.add(list.get(0));s.q.add(reply(400,"{\"error\":\"authorization_pending\"}"));s.q.add(reply(400,"{\"error\":\"slow_down\"}"));s.q.addAll(list.subList(1,list.size()));
  ProsperoAuth.Session session=new ProsperoAuth(s,c).signIn(view,()->false);if(!session.name.equals("PlayerOne")||!session.id.matches("[a-f0-9]{32}")||!c.waits.equals(List.of(5000L,5000L,10000L))||!s.q.isEmpty())throw new AssertionError("flow/poll");
  s=standard();list=new ArrayList<>(s.q);list.set(1,reply(200,"{\"access_token\":\""+MSA+"\",\"refresh_token\":\"SECRET_FRESH_APP_REFRESH\"}"));s.q=new ArrayDeque<>(list);var fresh=new ProsperoAuth(s,new Clock()).signIn(new View(),()->false);if(!new ProsperoAuth().refreshCredential(fresh).equals("SECRET_FRESH_APP_REFRESH"))throw new AssertionError("fresh sign-in refresh retention");
  if(view.all.contains("SECRET")||session.toString().contains("SECRET")||reply(200,"{\"secret\":\"SECRET\"}").toString().contains("SECRET"))throw new AssertionError("secret disclosure");
  for(String error:new String[]{"authorization_declined","expired_token","invalid_client"}){s=standard();list=new ArrayList<>(s.q);s.q.clear();s.q.add(list.get(0));s.q.add(reply(400,"{\"error\":\""+error+"\",\"error_description\":\"SECRET_MINECRAFT\"}"));expect(s,new Clock(),error.equals("authorization_declined")?"DECLINED":error.equals("expired_token")?"EXPIRED":"REGISTRATION");}
  s=standard();list=new ArrayList<>(s.q);list.set(0,reply(401,"{\"error\":\"invalid_client\",\"error_codes\":[70002],\"error_description\":\"SECRET_ERROR\"}"));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"PUBLIC_CLIENT");
  s=standard();list=new ArrayList<>(s.q);list.set(4,reply(403,"{\"error\":\"Forbidden\",\"errorMessage\":\"SECRET_ERROR\"}"));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"MC_DENIED");
  s=standard();list=new ArrayList<>(s.q);list.set(5,reply(200,"{\"items\":[]}"));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"OWNERSHIP");if(s.endpoints.contains(ProsperoAuth.Endpoint.PROFILE))throw new AssertionError("ownership bypass");
  s=standard();list=new ArrayList<>(s.q);list.set(3,reply(200,"{\"Token\":\"SECRET_XSTS\",\"DisplayClaims\":{\"xui\":[{\"uhs\":\"wrong\"}]}}"));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"RESPONSE");
  s=standard();list=new ArrayList<>(s.q);list.set(6,reply(200,"{\"id\":\"invalid\",\"name\":\"PlayerOne\"}"));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"PROFILE");
  s=standard();list=new ArrayList<>(s.q);list.set(0,reply(200,list.get(0).json.toString().replace("https://www.microsoft.com/link","https://evil.example/link")));s.q=new ArrayDeque<>(list);expect(s,new Clock(),"RESPONSE");
  s=standard();AtomicBoolean cancelled=new AtomicBoolean();c=new Clock();c.after=()->cancelled.set(true);try{new ProsperoAuth(s,c).signIn(new View(),cancelled::get);throw new AssertionError();}catch(ProsperoAuth.Failure f){if(!f.code.equals("CANCELLED")||s.endpoints.size()!=1)throw new AssertionError("cancel poll");}
  s=standard();s.q.removeFirst();ProsperoAuth.Session resumed=new ProsperoAuth(s,new Clock()).resume("SECRET_REFRESH",new View(),()->false);if(!resumed.name.equals("PlayerOne")||!new ProsperoAuth().refreshCredential(resumed).equals("SECRET_REFRESH"))throw new AssertionError("resume/profile/refresh retention");
  s=standard();s.q.removeFirst();s.q.removeFirst();s.q.addFirst(reply(200,"{\"access_token\":\""+MSA+"\",\"refresh_token\":\"SECRET_ROTATED\"}"));var rotated=new ProsperoAuth(s,new Clock()).resume("SECRET_REFRESH",new View(),()->false);if(!new ProsperoAuth().refreshCredential(rotated).equals("SECRET_ROTATED"))throw new AssertionError("refresh rotation");
  s=standard();s.q.removeFirst();s.q.removeFirst();s.q.addFirst(reply(400,"{\"error\":\"invalid_grant\"}"));try{new ProsperoAuth(s,new Clock()).resume("SECRET_REFRESH",new View(),()->false);throw new AssertionError("revoked refresh accepted");}catch(ProsperoAuth.Failure f){if(!f.code.equals("DECLINED"))throw new AssertionError(f.code);}
  System.out.println("PASS actual auth pipeline/poll pending/slowdown/decline/expiry/clientfailure/ownership/hash/profile/URI/cancel/redaction; no live account used");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-auth-')as folder:
 w=Path(folder);(w/'AuthCheck.java').write_text(source)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'AuthCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'-cp',str(w)+':'+cp,'AuthCheck'],check=True,timeout=30)
