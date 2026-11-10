# Minecraft 1.20 Java 17 file I/O buffer test 025

PPSA99878/01.000.025 uses runtime source e101908. Large native file
read/write buffers now use the paired native scratch fallback.

Build 024 reported OutOfMemoryError at RandomAccessFile.readBytes
during JAR reading, with 38,494,032 bytes of Java heap in use.
The physical title screen and subsequent I/O need validation.

The Java 17 target, LTS patches and actual host file helper fixture
passed. Forced normal allocator refusal preserved identical large
file reads/writes and paired cleanup on EOF, bounds errors, a closed
descriptor and a Java array copy exception. The signed package and update comparison passed.

Signed full ZIP SHA-256
`86b98afb20d88383dd8c6d3a9ee3006139aefc84ec997c13bb8e9c0d74e6d752`.

All 21 consumer host checks passed.

The PS5 run crashed after original Main initialized. It logged native
pthread_create EINVAL for a detached 1024 KiB stack, then SIGABRT.
The preceding RandomAccessFile buffer OOM was absent. Exact abort
ownership and the cause of the thread refusal are unresolved.
