/** Build-selected development graphics policy; shipped game artifacts remain intact. */
final class ProsperoGraphics {
 static boolean release261(String version){return java.util.Set.of("26.1","26.1.1","26.1.2").contains(version==null?"":version);}
 private static String mode(){
  if(!ProsperoChannel.tempGameTest())return "";
  try(var in=ProsperoGraphics.class.getResourceAsStream("/prosperocraft-zink.txt")){
   return in==null?"":new String(in.readNBytes(64),java.nio.charset.StandardCharsets.US_ASCII);
  }catch(Exception unavailable){return "";}
 }
 static boolean enabled(){return java.util.Set.of("vanilla-26.1-zink-v1\n","all-loaders-26.1-zink-v2\n").contains(mode());}
 static boolean fabricTest(){return mode().equals("all-loaders-26.1-zink-v2\n");}
 static boolean zink(String version,String loader){return enabled()&&release261(version)&&("vanilla".equals(loader)||("fabric".equals(loader)&&fabricTest()));}
 static boolean glfw(String version){return "26.2".equals(version)||(enabled()&&release261(version));}
 static boolean vulkan(String version,String window){return "SDL".equals(window)||("26.2".equals(version)&&"GLFW".equals(window));}
}
