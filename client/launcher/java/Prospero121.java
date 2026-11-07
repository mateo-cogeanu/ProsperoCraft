import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Set;

/** Explicit original121 release/native generation; Vanilla-only candidate resource. */
final class Prospero121 {
 static final Set<String> RELEASES=Set.of("1.21","1.21.1","1.21.2","1.21.3","1.21.4","1.21.5","1.21.6","1.21.7","1.21.8","1.21.9","1.21.10","1.21.11");
 private static final Set<String> RELEASED=Set.of("1.21.9","1.21.10","1.21.11");
 static boolean supported(String version,String loader){
  return version!=null&&RELEASED.contains(version)&&available(version,loader);
 }
 static boolean available(String version,String loader){
  if(version==null||!RELEASES.contains(version)||!"vanilla".equals(loader)||!ProsperoChannel.tempGameTest())return false;
  try(var in=Prospero121.class.getResourceAsStream("/prosperocraft-121.txt")){
   if(in==null)return false;String mode=new String(in.readNBytes(96),StandardCharsets.US_ASCII);
   return "vanilla-1.21-1.21.11-zink-v4\n".equals(mode)||
       (RELEASED.contains(version)&&"vanilla-1.21.9-1.21.11-zink-v3\n".equals(mode))||
       (("1.21.10".equals(version)||"1.21.11".equals(version))&&"vanilla-1.21.10-1.21.11-zink-v2\n".equals(mode))||("1.21.11".equals(version)&&"vanilla-1.21.11-zink-v1\n".equals(mode));
  }catch(IOException missing){return false;}
 }
 static String[] shutdownAccessors(String version)throws IOException{
  return switch(version){
   case "1.21","1.21.1"->new String[]{"fgo","Q","r"};
   case "1.21.2"->new String[]{"fmf","Q","r"};
   case "1.21.3"->new String[]{"fmg","Q","r"};
   case "1.21.4"->new String[]{"flk","Q","r"};
   case "1.21.5"->new String[]{"fqq","Q","r"};
   case "1.21.6","1.21.7"->new String[]{"fud","R","r"};
   case "1.21.8"->new String[]{"fue","R","r"};
   case "1.21.9","1.21.10"->new String[]{"fzz","W","v"};
   case "1.21.11"->new String[]{"gfj","V","v"};
   default->throw new IOException("Unknown1.21 shutdown contract");
  };
 }
}
