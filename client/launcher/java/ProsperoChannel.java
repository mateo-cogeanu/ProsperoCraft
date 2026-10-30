import java.nio.charset.StandardCharsets;

/** Build-selected release channel. Missing/invalid metadata always falls back to Demo. */
final class ProsperoChannel {
 static boolean offline(){
  try(var in=ProsperoChannel.class.getResourceAsStream("/prosperocraft-channel.txt")){
   return in!=null&&new String(in.readNBytes(32),StandardCharsets.US_ASCII).strip().equals("offline");
  }catch(Exception ignored){return false;}
 }
 static boolean tempGameTest(){
  try(var in=ProsperoChannel.class.getResourceAsStream("/prosperocraft-channel.txt")){return in!=null&&new String(in.readNBytes(32),StandardCharsets.US_ASCII).strip().equals("temp_gametest");}catch(Exception ignored){return false;}
 }
 private static final boolean FABRIC262_TEST=readFabric262Test();
 static boolean fabric262Test(){return false;}
 private static boolean readFabric262Test(){
  if(!tempGameTest())return false;
  try(var in=ProsperoChannel.class.getResourceAsStream("/prosperocraft-development.txt")){
   return in!=null&&new String(in.readNBytes(64),StandardCharsets.US_ASCII).equals("fabric-26.2-test-v1\n");
  }catch(Exception unavailable){return false;}
 }
 static String label(){return fabric262Test()?"DEV FABRIC 26.2":tempGameTest()?"TEMP GAMETEST":offline()?"OFFLINE BRANCH":"DEMO BRANCH";}
}
