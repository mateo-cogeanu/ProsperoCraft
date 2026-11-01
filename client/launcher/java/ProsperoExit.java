/** Launcher-owned shutdown observer; original game and VM shutdown run normally. */
public final class ProsperoExit implements AutoCloseable {
 @FunctionalInterface public interface Checked {void run() throws Exception;}
 private final Thread hook;
 public ProsperoExit(Checked verify,Runnable arm,java.io.PrintStream report){
  hook=new Thread(()->{
   try{verify.run();arm.run();report.println("PS5_SESSION SYSTEM_EXIT_CLEAN; awaiting VM exit status");}
   catch(Throwable failure){report.println("PS5_SESSION SYSTEM_EXIT_REJECTED reason="+failure.getClass().getSimpleName());}
   report.flush();
  },"Prospero clean exit audit");
  Runtime.getRuntime().addShutdownHook(hook);
 }
 @Override public void close(){Runtime.getRuntime().removeShutdownHook(hook);}
}
