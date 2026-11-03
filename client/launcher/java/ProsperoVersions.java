/** Bounded publisher/instance id validation; release acceptance is a separate gate. */
final class ProsperoVersions {
 static boolean legacy26(String id){return id!=null&&id.matches("26\\.[0-9][A-Za-z0-9._-]{0,70}");}
 static boolean release121(String id){return id!=null&&id.matches("1\\.21(?:\\.\\d{1,2})?");}
 static boolean valid(String id){return legacy26(id)||release121(id);}
 static boolean catalog(String id,String type,boolean snapshots){return release121(id)?"release".equals(type):legacy26(id)&&("release".equals(type)||snapshots);}
}
