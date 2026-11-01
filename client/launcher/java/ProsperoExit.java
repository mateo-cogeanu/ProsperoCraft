/** Launcher-owned shutdown observer; original game and VM shutdown run normally. */
public final class ProsperoExit implements AutoCloseable {
 @FunctionalInterface public interface Checked {void run() throws Exception;}
 private final Thread hook;
 public ProsperoExit(Checked verify,Runnable arm,java.io.PrintStream report){this(verify,arm,report,stage->{});}
 public ProsperoExit(Checked verify,Runnable arm,java.io.PrintStream report,java.util.function.Consumer<String> checkpoint){
  hook=new Thread(()->{
   try{checkpoint.accept("PS5_SESSION SYSTEM_EXIT_AUDIT_ENTER");verify.run();arm.run();checkpoint.accept("PS5_SESSION SYSTEM_EXIT_AUDIT_ARMED");report.println("PS5_SESSION SYSTEM_EXIT_CLEAN; awaiting VM exit status");}
   catch(Throwable failure){try{checkpoint.accept("PS5_SESSION SYSTEM_EXIT_AUDIT_REJECTED");}catch(Throwable ignored){}report.println("PS5_SESSION SYSTEM_EXIT_REJECTED reason="+failure.getClass().getSimpleName());}
   report.flush();
  },"Prospero clean exit audit");
  Runtime.getRuntime().addShutdownHook(hook);
 }
 @Override public void close(){Runtime.getRuntime().removeShutdownHook(hook);}
}
