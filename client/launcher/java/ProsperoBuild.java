/* SPDX-License-Identifier: GPL-3.0-or-later */
import java.io.IOException;
import java.util.Properties;

/** Packaged identity; source-only host/development runs explicitly use development. */
final class ProsperoBuild {
 static final String VERSION=version();
 static final String USER_AGENT="mateo-cogeanu/ProsperoCraft/"+VERSION+" (github.com/mateo-cogeanu/ProsperoCraft)";
 private static String version() {
  try(var input=ProsperoBuild.class.getResourceAsStream("/prosperocraft-build.properties")) {
   if(input==null)return "development";
   var properties=new Properties();properties.load(input);
   String version=properties.getProperty("app_version","");
   if(!version.matches("[0-9]{2}\\.[0-9]{3}\\.[0-9]{3}")||!properties.getProperty("title_id","").matches("PPSA[0-9]{5}"))throw new IOException("Invalid packaged ProsperoCraft identity");
   return version;
  }catch(IOException invalid){throw new ExceptionInInitializerError(invalid);}
 }
 private ProsperoBuild(){}
}
