/* SPDX-License-Identifier: BSD-3-Clause */
package org.lwjgl.system.ps5;
import java.nio.ByteBuffer;
import javax.annotation.Nullable;
import org.lwjgl.system.Library;
import org.lwjgl.system.MemoryUtil;
import org.lwjgl.system.SharedLibrary;

/** Resident PS5 export registry; no arbitrary ELF or OS-module loader. */
public final class PS5Library extends SharedLibrary.Default {
    private boolean closed;
    static { Library.initialize(); }
    public PS5Library(String name) { super(name,open(name)); }
    private static long open(String name) {
        if(name==null)throw new NullPointerException("library name");
        long handle=nOpen(name);
        if(handle==0)throw new UnsatisfiedLinkError("PS5 resident library unavailable: "+name);
        return handle;
    }
    private void alive() {if(closed)throw new IllegalStateException("resident library is closed");}
    @Override public @Nullable String getPath() {return null;}
    @Override public synchronized long getFunctionAddress(ByteBuffer name) {
        alive();if(name==null)throw new NullPointerException("function name");
        if(!name.isDirect()||!name.hasRemaining()||name.get(name.limit()-1)!=0)throw new IllegalArgumentException("NUL-terminated direct function name required");
        return nFind(address,MemoryUtil.memASCII(name,name.remaining()-1));
    }
    @Override public synchronized long getFunctionAddress(CharSequence name) {
        alive();if(name==null)throw new NullPointerException("function name");return nFind(address,name.toString());
    }
    @Override public synchronized void free() {
        if(!closed){if(nClose(address)!=0)throw new IllegalStateException("resident handle close failed");closed=true;}
    }
    private static native long nOpen(String name);
    private static native long nFind(long handle,String name);
    private static native int nClose(long handle);
}
