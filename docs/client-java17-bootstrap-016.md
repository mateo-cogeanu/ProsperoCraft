# Minecraft 1.20 memory diagnostic test 016

Build 015 reached original Minecraft code and returned a Java
OutOfMemoryError during static initialization at Main line 57. It
did not emit a new fatal VM error and DestroyJavaVM succeeded.
The error class alone does not establish which memory pool failed.

Build 016 tests a 192 MiB maximum Java heap, up from 128 MiB. On a
reported memory error, the Java diagnostic writes a fixed reason
label and heap usage, commitment and limit. The report omits arbitrary
exception messages. The native allocation fallback remains in place.

The FTP client showed an incomplete transfer for 015. Use the full
016 package if the installed title tree is uncertain. Install version
01.000.016 and run rows 1 through 3. The new heap size and Minecraft
title screen require PS5 validation.

For an intact build 014 installation, the local update ZIP contains
every file that differs from 014. Merge its contents into the title
directory at their corresponding paths.

Signed full ZIP SHA-256 `8fe8f47196206e011b1943eb346d849992e2f92cab7033d54478b8b2fafa45fa`.

[Build 016 crash and build 017](client-java17-bootstrap-017.md)
