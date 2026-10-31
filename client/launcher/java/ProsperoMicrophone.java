/* SPDX-License-Identifier: GPL-3.0-or-later */
/** Explicit opt-in prepares the system input port; only a deliberate test/mod reads samples. */
final class ProsperoMicrophone {
 private static boolean loaded;
 private static void load(){if(!loaded){System.loadLibrary("ps5openal");loaded=true;}}
 private static native void nativeEnable(boolean enabled);
 private static native String nativeProbe();
 static void enable(boolean enabled)throws java.io.IOException{try{load();nativeEnable(enabled);}catch(UnsatisfiedLinkError unavailable){if(enabled)throw new java.io.IOException("Microphone native integration unavailable");}}
 static String probe()throws java.io.IOException{try{load();return nativeProbe();}catch(UnsatisfiedLinkError unavailable){throw new java.io.IOException("Microphone native integration unavailable");}}
}
