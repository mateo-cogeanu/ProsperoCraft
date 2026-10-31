#!/usr/bin/env python3
"""Exercise actual auth HTTPS transport with a private local TLS fixture, no account."""
from pathlib import Path
from host_toolchain import java_home, launcher_classpath
import subprocess,json,tempfile
ROOT=Path(__file__).resolve().parents[1];jdk=java_home()
cp=launcher_classpath()
source=r'''
import com.sun.net.httpserver.*;import javax.net.ssl.*;import java.io.*;import java.net.*;import java.nio.file.*;import java.security.*;import java.util.concurrent.atomic.*;
public class HttpsAuthCheck {
 static AtomicReference<String> route=new AtomicReference<>("/401");static AtomicInteger redirected=new AtomicInteger();static SSLContext context;static int port;
 static HttpsURLConnection connection(URL ignored)throws Exception{var c=(HttpsURLConnection)URI.create("https://localhost:"+port+route.get()).toURL().openConnection();c.setSSLSocketFactory(context.getSocketFactory());return c;}
 public static void main(String[]args)throws Exception{
  KeyStore store=KeyStore.getInstance("PKCS12");try(var in=Files.newInputStream(Path.of(args[0]))){store.load(in,"fixture-only".toCharArray());}
  var keys=KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());keys.init(store,"fixture-only".toCharArray());var trust=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());trust.init(store);context=SSLContext.getInstance("TLS");context.init(keys.getKeyManagers(),trust.getTrustManagers(),null);
  var server=HttpsServer.create(new InetSocketAddress("127.0.0.1",0),0);server.setHttpsConfigurator(new HttpsConfigurator(context));
  server.createContext("/",exchange->{try{
   exchange.getRequestBody().readAllBytes();String path=exchange.getRequestURI().getPath();int status=200;String body="{\"result\":\"SECRET_RESPONSE\"}";
   if(path.equals("/401")){status=401;body="{\"error\":\"invalid_client\",\"error_codes\":[70002],\"error_description\":\"SECRET_ERROR\"}";exchange.getResponseHeaders().set("WWW-Authenticate","Bearer");}
   if(path.equals("/403")){status=403;body="SECRET_NON_JSON";}
   if(path.equals("/302")){status=302;exchange.getResponseHeaders().set("Location","https://localhost:"+port+"/redirected");}
   if(path.equals("/redirected"))redirected.incrementAndGet();
   if(path.equals("/large"))body="X".repeat(1024*1024+2);
   byte[] bytes=body.getBytes(java.nio.charset.StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","application/json");exchange.sendResponseHeaders(status,bytes.length);exchange.getResponseBody().write(bytes);
  }catch(IOException stopped){}finally{exchange.close();}});server.start();port=server.getAddress().getPort();
  var diagnostics=new ByteArrayOutputStream();PrintStream previous=System.err;System.setErr(new PrintStream(diagnostics,true,java.nio.charset.StandardCharsets.UTF_8));
  try{
   // Reproduce why the previous fixed-length POST hid the real401JSON.
   var old=connection(null);old.setRequestMethod("POST");old.setDoOutput(true);old.setFixedLengthStreamingMode(1);
   try{old.getOutputStream().write('x');int status=old.getResponseCode();if(status!=401||old.getErrorStream()!=null)throw new AssertionError("old streaming failure not reproduced");}catch(HttpRetryException expected){}finally{old.disconnect();}
   var net=new ProsperoAuth.Net(HttpsAuthCheck::connection);var auth=new ProsperoAuth(net,new ProsperoAuth.Clock(){public long millis(){return 0;}public void sleep(long ms){throw new AssertionError();}});
   try{auth.signIn(new ProsperoAuth.View(){public void code(String c,String u){throw new AssertionError();}public void stage(String s){}},()->false);throw new AssertionError();}catch(ProsperoAuth.Failure failure){if(!failure.code.equals("PUBLIC_CLIENT")||!failure.getMessage().startsWith("[DEVICE HTTP 401]"))throw new AssertionError(failure);}
   route.set("/403");var reply=auth.request(ProsperoAuth.Endpoint.MINECRAFT,"POST","SECRET_REQUEST",null);if(reply.status!=403||reply.json.size()!=0)throw new AssertionError();try{ProsperoAuth.success(reply,"REGISTRATION");throw new AssertionError();}catch(ProsperoAuth.Failure f){if(!f.code.equals("MC_DENIED")||!f.getMessage().startsWith("[MINECRAFT HTTP 403]"))throw new AssertionError(f);}
   route.set("/302");reply=auth.request(ProsperoAuth.Endpoint.DEVICE,"POST","SECRET_REQUEST",null);if(reply.status!=302||redirected.get()!=0)throw new AssertionError("redirect followed");
   route.set("/ok");reply=auth.request(ProsperoAuth.Endpoint.DEVICE,"POST","SECRET_REQUEST",null);if(reply.status!=200||!reply.json.has("result")||reply.toString().contains("SECRET"))throw new AssertionError();
   route.set("/large");try{auth.request(ProsperoAuth.Endpoint.DEVICE,"POST","X",null);throw new AssertionError("unbounded response");}catch(ProsperoAuth.Failure expected){}
   var badHost=new ProsperoAuth(new ProsperoAuth.Net(url->{var c=(HttpsURLConnection)URI.create("https://127.0.0.1:"+port+"/ok").toURL().openConnection();c.setSSLSocketFactory(context.getSocketFactory());return c;}),null);
   try{badHost.request(ProsperoAuth.Endpoint.DEVICE,"POST","X",null);throw new AssertionError("hostname verification bypassed");}catch(SSLException expected){}
   var untrusted=new ProsperoAuth(new ProsperoAuth.Net(url->(HttpsURLConnection)URI.create("https://localhost:"+port+"/ok").toURL().openConnection()),null);
   try{untrusted.request(ProsperoAuth.Endpoint.DEVICE,"POST","X",null);throw new AssertionError("CA validation bypassed");}catch(SSLException expected){}
   var broken=new ProsperoAuth(new ProsperoAuth.Net(url->{throw new IOException("SECRET_EXCEPTION");}),null);
   try{broken.request(ProsperoAuth.Endpoint.DEVICE,"POST","X",null);throw new AssertionError();}catch(IOException expected){}
   String log=diagnostics.toString(java.nio.charset.StandardCharsets.UTF_8);
   if(log.contains("SECRET")||!log.contains("endpoint=DEVICE event=HTTP status=401 oauth=invalid_client aad=70002")||!log.contains("endpoint=MINECRAFT event=HTTP status=403")||!log.contains("category=TLS")||!log.contains("category=IO"))throw new AssertionError("unsafe or missing diagnostics");
  }finally{System.setErr(previous);server.stop(0);}
  System.out.println("PASS real HTTPS401 streaming regression/fixed buffered OAuth body, distinct Minecraft403, redirect refusal, body bound, TLS hostname/CA rejection and diagnostic secret redaction; local fixtures only");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='prospero-https-')as folder:
 w=Path(folder);(w/'HttpsAuthCheck.java').write_text(source)
 subprocess.run([str(jdk/'bin/keytool'),'-genkeypair','-alias','test','-keyalg','RSA','-keysize','2048','-validity','1','-dname','CN=localhost','-ext','SAN=dns:localhost','-keystore',str(w/'fixture.p12'),'-storetype','PKCS12','-storepass','fixture-only','-keypass','fixture-only','-noprompt'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run([str(jdk/'bin/javac'),'--release','25','--add-modules','jdk.httpserver','-cp',cp,'-d',str(w),*[str(p)for p in (ROOT/'client/launcher/java').glob('*.java')],str(w/'HttpsAuthCheck.java')],check=True)
 subprocess.run([str(jdk/'bin/java'),'--add-modules','jdk.httpserver','-cp',str(w)+':'+cp,'HttpsAuthCheck',str(w/'fixture.p12')],check=True,timeout=40)
