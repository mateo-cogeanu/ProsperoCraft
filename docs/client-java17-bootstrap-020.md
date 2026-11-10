# Minecraft 1.20 Java 17 native scratch test 020

PPSA99878/01.000.020 uses Java runtime source a4ec5a3. ClassLoader-owned
buffers and JIMAGE-owned arrays now use the native allocation fallback
already available to the verifier. The 019 crash report identifies an
allocation trap and a preceding libjava OOM, but neither caller was
confirmed. Row 3 and the Minecraft title screen need physical validation.

The target build and shared allocator symbol checks passed. A host
sanitizer check exercised the actual JIMAGE array adapter with both
normal and forced native allocation fallback, and the JIMAGE file
mapping regression passed.

All 21 consumer host checks passed. The signed package and byte-for-byte
update comparison passed. The update contains no changed game assets.

Signed full ZIP SHA-256
`5eef46d1c036b77754b321ef04f0923ab5f982d0ca88dc8360849122144389f9`.

On the PS5, row 3 returned a pending Java exception after Main class
initialization. The native report could not classify it. DestroyJavaVM
returned successfully. The fault log did not grow, and the game log
was empty. The probe was still available over FTP with its display off.
