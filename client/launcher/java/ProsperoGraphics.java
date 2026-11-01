/** Build-selected development graphics policy; shipped game artifacts remain intact. */
final class ProsperoGraphics {
 static boolean release261(String version){return java.util.Set.of("26.1","26.1.1","26.1.2").contains(version==null?"":version);}
 static boolean enabled(){
  if(!ProsperoChannel.tempGameTest())return false;
  try(var in=ProsperoGraphics.class.getResourceAsStream("/prosperocraft-zink.txt")){
   return in!=null&&new String(in.readNBytes(64),java.nio.charset.StandardCharsets.US_ASCII).equals("vanilla-26.1-zink-v1\n");
  }catch(Exception unavailable){return false;}
 }
 static boolean zink(String version,String loader){return enabled()&&release261(version)&&"vanilla".equals(loader);}
 static boolean glfw(String version){return "26.2".equals(version)||(enabled()&&release261(version));}
 static boolean vulkan(String version,String window){return "SDL".equals(window)||("26.2".equals(version)&&"GLFW".equals(window));}
}
