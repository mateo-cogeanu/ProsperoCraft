import com.google.gson.*;
import javax.net.ssl.HttpsURLConnection;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Device-code public client. Secrets never appear in diagnostics or toString. */
public final class ProsperoAuth {
 public static final String CLIENT_ID="f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3";
 public static final String SCOPE="XboxLive.signin offline_access";
 public enum Endpoint {
  DEVICE("https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"),
  TOKEN("https://login.microsoftonline.com/consumers/oauth2/v2.0/token"),
  XBOX("https://user.auth.xboxlive.com/user/authenticate"),
  XSTS("https://xsts.auth.xboxlive.com/xsts/authorize"),
  MINECRAFT("https://api.minecraftservices.com/authentication/login_with_xbox"),
  LICENSE("https://api.minecraftservices.com/entitlements/license"),
  PROFILE("https://api.minecraftservices.com/minecraft/profile");
  final String address;Endpoint(String address){this.address=address;}
 }
 public static final class Failure extends Exception {
  public final String code;
  Failure(String code){this(code,null,0);}
  Failure(String code,Endpoint endpoint,int status){super((endpoint==null?"":"["+endpoint.name()+(status>0?" HTTP "+status:"")+ "] ")+message(code));this.code=code;}
  static String message(String code){return switch(code){
   case "CANCELLED"->"Sign-in cancelled.";case "EXPIRED"->"Code expired. Select Sign in to try again.";
   case "DECLINED"->"Microsoft sign-in was declined.";
   case "PUBLIC_CLIENT"->"Enable Allow public client flows in the Microsoft app registration.";
   case "MC_DENIED"->"Minecraft Services denied this app. App approval may be required.";
   case "REGISTRATION"->"Microsoft app setup needs attention. Check public client flow and service approval.";
   case "OWNERSHIP"->"This account does not have a playable Minecraft Java entitlement.";
   case "PROFILE"->"Minecraft Java profile unavailable. Complete setup in the official launcher.";
   case "XBOX"->"Xbox profile or account permissions need attention.";
   case "NETWORK"->"Cannot reach sign-in services. Check your connection and try again.";
   default->"Sign-in could not be completed. Please try again.";};}
 }
 public static final class Reply {
  final int status;final JsonObject json;final Endpoint endpoint;
  Reply(int status,JsonObject json){this(status,json,null);}
  Reply(int status,JsonObject json,Endpoint endpoint){this.status=status;this.json=json;this.endpoint=endpoint;}
  @Override public String toString(){return "Auth reply HTTP "+status+" [body redacted]";}
 }
 interface Transport {Reply send(Endpoint endpoint,String method,String type,String body,String bearer)throws Exception;}
 interface Clock {long millis();void sleep(long millis)throws InterruptedException;}
 public interface View {void stage(String message);void code(String code,String uri);}
 public static final class Session {
  public final String name,id;private final String token;private final long expiresAt;private String refresh="",skin="";
  Session(String name,String id,String token,long expiresAt){this.name=name;this.id=id;this.token=token;this.expiresAt=expiresAt;}
  boolean valid(long now){return now+60_000<expiresAt;}
  String accessToken(){return token;}
  @Override public String toString(){return "Minecraft session [credentials redacted]";}
 }
 interface Connections {HttpsURLConnection open(URL url)throws Exception;}
 static final class Net implements Transport {
  private final Connections connections;
  Net(){this(url->(HttpsURLConnection)url.openConnection());}
  Net(Connections connections){this.connections=connections;}
  public Reply send(Endpoint endpoint,String method,String type,String body,String bearer)throws Exception {
   String address=endpoint.address+(endpoint==Endpoint.LICENSE?"?requestId="+UUID.randomUUID():"");
   HttpsURLConnection c=connections.open(URI.create(address).toURL());
   c.setConnectTimeout(15000);c.setReadTimeout(20000);c.setInstanceFollowRedirects(false);c.setAllowUserInteraction(false);c.setUseCaches(false);
   c.setRequestMethod(method);c.setRequestProperty("Accept","application/json");
   c.setRequestProperty("User-Agent","ProsperoCraft/078");
   if(bearer!=null)c.setRequestProperty("Authorization","Bearer "+bearer);
   try{
    if(body!=null){c.setDoOutput(true);c.setRequestProperty("Content-Type",type);byte[] bytes=body.getBytes(StandardCharsets.UTF_8);if(bytes.length>256*1024)throw new Failure("RESPONSE");
     // These small POSTs must be buffered: JDK streaming mode disconnects on
     // HTTP401 before getErrorStream can preserve the OAuth error response.
     try(OutputStream out=c.getOutputStream()){out.write(bytes);}}
    int status=c.getResponseCode();InputStream input=status<400?c.getInputStream():c.getErrorStream();
    if(input==null){if(status>=300)return new Reply(status,new JsonObject());throw new Failure("RESPONSE");}
    byte[] bytes;try(input){bytes=input.readNBytes(1024*1024+1);}if(bytes.length>1024*1024)throw new Failure("RESPONSE");
    try{
     JsonElement parsed=JsonParser.parseString(new String(bytes,StandardCharsets.UTF_8));
     if(parsed.isJsonObject())return new Reply(status,parsed.getAsJsonObject());
    }catch(JsonParseException invalid){/* Never log raw JSON or parser text. */}
    if(status>=300)return new Reply(status,new JsonObject());
    throw new Failure("RESPONSE");
   }finally{c.disconnect();}
  }
 }
 private final Transport transport;private final Clock clock;
 public ProsperoAuth(){this(new Net(),new Clock(){public long millis(){return System.currentTimeMillis();}public void sleep(long ms)throws InterruptedException{Thread.sleep(ms);}});}
 ProsperoAuth(Transport transport,Clock clock){this.transport=transport;this.clock=clock;}
 static String str(JsonObject o,String key)throws Failure {
  if(!o.has(key)||!o.get(key).isJsonPrimitive()||!o.get(key).getAsJsonPrimitive().isString())throw new Failure("RESPONSE");
  String value=o.get(key).getAsString();if(value.isEmpty()||value.length()>65536)throw new Failure("RESPONSE");return value;
 }
 static long number(JsonObject o,String key,long min,long max)throws Failure {
  try{long value=o.get(key).getAsLong();if(value<min||value>max)throw new Failure("RESPONSE");return value;}catch(RuntimeException invalid){throw new Failure("RESPONSE");}
 }
 static JsonObject json(String text){return JsonParser.parseString(text).getAsJsonObject();}
 static String form(String... fields){StringJoiner out=new StringJoiner("&");for(int i=0;i<fields.length;i+=2)out.add(URLEncoder.encode(fields[i],StandardCharsets.UTF_8)+"="+URLEncoder.encode(fields[i+1],StandardCharsets.UTF_8));return out.toString();}
 static String safeOAuth(JsonObject json){
  try{return switch(str(json,"error")){case "invalid_client","unauthorized_client","invalid_scope","authorization_pending","slow_down","expired_token","authorization_declined","access_denied","invalid_grant"->str(json,"error");default->"OTHER";};}catch(Exception ignored){return "NONE";}
 }
 static String aadCodes(JsonObject json){
  StringJoiner codes=new StringJoiner(",");
  try{JsonArray values=json.getAsJsonArray("error_codes");if(values!=null)for(int i=0;i<Math.min(values.size(),4);i++){
   JsonElement value=values.get(i);if(value.isJsonPrimitive()&&value.getAsJsonPrimitive().isNumber()){
    String digits=value.getAsString();if(digits.matches("[0-9]{1,9}"))codes.add(digits);
   }
  }}catch(RuntimeException ignored){}return codes.length()==0?"NONE":codes.toString();
 }
 static String issue(Exception error){
  if(error instanceof javax.net.ssl.SSLException)return "TLS";
  if(error instanceof UnknownHostException)return "DNS";
  if(error instanceof SocketTimeoutException)return "TIMEOUT";
  if(error instanceof ConnectException)return "CONNECT";
  if(error instanceof HttpRetryException)return "HTTP_RETRY";
  if(error instanceof InterruptedException)return "INTERRUPTED";
  if(error instanceof IOException)return "IO";
  if(error instanceof Failure)return "RESPONSE";
  return "OTHER";
 }
 Reply request(Endpoint endpoint,String method,String body,String bearer)throws Exception {
  System.err.println("PS5_AUTH endpoint="+endpoint.name()+" event=BEGIN");
  try{
   Reply raw=transport.send(endpoint,method,endpoint==Endpoint.DEVICE||endpoint==Endpoint.TOKEN?"application/x-www-form-urlencoded":"application/json",body,bearer);
   System.err.println("PS5_AUTH endpoint="+endpoint.name()+" event=HTTP status="+raw.status+" oauth="+safeOAuth(raw.json)+" aad="+aadCodes(raw.json));
   return new Reply(raw.status,raw.json,endpoint);
  }catch(Exception error){System.err.println("PS5_AUTH endpoint="+endpoint.name()+" event=FAIL category="+issue(error));throw error;}
 }
 static void success(Reply reply,String phase)throws Failure {
  if(reply.status>=200&&reply.status<300)return;
  String code=phase;
  if(reply.endpoint==Endpoint.DEVICE&&Arrays.asList(aadCodes(reply.json).split(",")).contains("70002"))code="PUBLIC_CLIENT";
  if(reply.endpoint==Endpoint.MINECRAFT&&reply.status==403)code="MC_DENIED";
  throw new Failure(code,reply.endpoint,reply.status);
 }
 static void active(BooleanSupplier cancelled)throws Failure {if(cancelled.getAsBoolean()||Thread.currentThread().isInterrupted())throw new Failure("CANCELLED");}
 static String hash(JsonObject object)throws Failure {
  try{return str(object.getAsJsonObject("DisplayClaims").getAsJsonArray("xui").get(0).getAsJsonObject(),"uhs");}catch(RuntimeException bad){throw new Failure("RESPONSE");}
 }
 public Session signIn(View view,BooleanSupplier cancelled)throws Failure {
  try{
   active(cancelled);view.stage("Connecting to Microsoft");
   Reply device=request(Endpoint.DEVICE,"POST",form("client_id",CLIENT_ID,"scope",SCOPE),null);success(device,"REGISTRATION");
   String secret=str(device.json,"device_code"),code=str(device.json,"user_code"),uri=str(device.json,"verification_uri");
   URI verification=URI.create(uri);String host=verification.getHost();
   if(!"https".equals(verification.getScheme())||verification.getUserInfo()!=null||verification.getPort()!=-1||!("microsoft.com".equals(host)||"www.microsoft.com".equals(host)||"login.microsoftonline.com".equals(host)))throw new Failure("RESPONSE");
   if(!code.matches("[A-Za-z0-9 -]{4,24}"))throw new Failure("RESPONSE");
   long lifetime=number(device.json,"expires_in",1,1800)*1000,deadline=clock.millis()+lifetime;
   long interval=device.json.has("interval")?number(device.json,"interval",1,60)*1000:5000;
   view.code(code,uri);view.stage("Approve sign-in on your phone or computer");String msa,refresh="";
   while(true){
    active(cancelled);if(clock.millis()+interval>=deadline)throw new Failure("EXPIRED");clock.sleep(interval);active(cancelled);
    Reply token=request(Endpoint.TOKEN,"POST",form("grant_type","urn:ietf:params:oauth:grant-type:device_code","client_id",CLIENT_ID,"device_code",secret),null);
    if(token.status>=200&&token.status<300){msa=str(token.json,"access_token");refresh=optional(token.json,"refresh_token","");break;}
    if(!token.json.has("error"))throw new Failure(token.status==401||token.status==403?"REGISTRATION":"RESPONSE",Endpoint.TOKEN,token.status);
    String error=str(token.json,"error");
    if(error.equals("authorization_pending"))continue;
    if(error.equals("slow_down")){interval=Math.min(60_000,interval+5000);continue;}
    throw new Failure(switch(error){case "expired_token"->"EXPIRED";case "authorization_declined","access_denied"->"DECLINED";case "invalid_client","unauthorized_client","invalid_scope"->"REGISTRATION";default->"RESPONSE";},Endpoint.TOKEN,token.status);
   }
   return complete(msa,refresh,view,cancelled);
  }catch(Failure failure){throw failure;}catch(InterruptedException stopped){Thread.currentThread().interrupt();throw new Failure("CANCELLED");}catch(Exception ignored){throw new Failure("NETWORK");}
 }
 public Session resume(String refresh,View view,BooleanSupplier cancelled)throws Failure {
  try{active(cancelled);Reply reply=request(Endpoint.TOKEN,"POST",form("grant_type","refresh_token","client_id",CLIENT_ID,"refresh_token",refresh,"scope",SCOPE),null);success(reply,"DECLINED");return complete(str(reply.json,"access_token"),optional(reply.json,"refresh_token",refresh),view,cancelled);}
  catch(Failure failure){throw failure;}catch(InterruptedException stopped){Thread.currentThread().interrupt();throw new Failure("CANCELLED");}catch(Exception ignored){throw new Failure("NETWORK");}
 }
 static String optional(JsonObject o,String key,String fallback){try{return str(o,key);}catch(Failure absent){return fallback;}}
 String refreshCredential(Session session){return session.refresh;}
 String skin(Session session){return session.skin;}
 private Session complete(String msa,String refresh,View view,BooleanSupplier cancelled)throws Exception {
   active(cancelled);view.stage("Connecting your Xbox profile");
   JsonObject body=new JsonObject(),props=new JsonObject();props.addProperty("AuthMethod","RPS");props.addProperty("SiteName","user.auth.xboxlive.com");props.addProperty("RpsTicket","d="+msa);body.add("Properties",props);body.addProperty("RelyingParty","http://auth.xboxlive.com");body.addProperty("TokenType","JWT");
   Reply xbox=request(Endpoint.XBOX,"POST",body.toString(),null);success(xbox,"XBOX");String xboxToken=str(xbox.json,"Token"),uhs=hash(xbox.json);
   active(cancelled);body=new JsonObject();props=new JsonObject();props.addProperty("SandboxId","RETAIL");JsonArray tokens=new JsonArray();tokens.add(xboxToken);props.add("UserTokens",tokens);body.add("Properties",props);body.addProperty("RelyingParty","rp://api.minecraftservices.com/");body.addProperty("TokenType","JWT");
   Reply xsts=request(Endpoint.XSTS,"POST",body.toString(),null);success(xsts,"XBOX");if(!uhs.equals(hash(xsts.json)))throw new Failure("RESPONSE");
   active(cancelled);view.stage("Checking Minecraft Java access");body=new JsonObject();body.addProperty("identityToken","XBL3.0 x="+uhs+";"+str(xsts.json,"Token"));
   Reply minecraft=request(Endpoint.MINECRAFT,"POST",body.toString(),null);success(minecraft,"REGISTRATION");String access=str(minecraft.json,"access_token");long expires=clock.millis()+number(minecraft.json,"expires_in",120,172800)*1000;
   active(cancelled);Reply license=request(Endpoint.LICENSE,"GET",null,access);success(license,"OWNERSHIP");boolean owns=false;
   try{for(JsonElement item:license.json.getAsJsonArray("items")){String name=str(item.getAsJsonObject(),"name");if(name.equals("game_minecraft")||name.equals("product_minecraft"))owns=true;}}catch(RuntimeException bad){throw new Failure("RESPONSE");}
   if(!owns)throw new Failure("OWNERSHIP");
   active(cancelled);Reply profile=request(Endpoint.PROFILE,"GET",null,access);success(profile,"PROFILE");String name=str(profile.json,"name"),id=str(profile.json,"id");
   if(!name.matches("[A-Za-z0-9_]{1,16}")||!id.matches("[a-fA-F0-9]{32}"))throw new Failure("PROFILE");active(cancelled);
   Session session=new Session(name,id,access,expires);session.refresh=refresh;
   try{JsonArray skins=profile.json.getAsJsonArray("skins");if(skins!=null&&!skins.isEmpty())session.skin=str(skins.get(0).getAsJsonObject(),"url");}catch(Exception absent){}
   return session;
 }
}
