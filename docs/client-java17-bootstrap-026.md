# Minecraft 1.20 Java 17 thread attribute test 026

PPSA99878/01.000.026 uses runtime source 7a5e810. The PS5 Java 17
thread paths now use genuine, preinitialized pthread attribute objects
with separate creation and stack-query pools. Initialization and
detach-setting failures are checked before native thread creation.

Build 025 logged pthread_create EINVAL for a detached 1024 KiB stack
before a native SIGABRT. The exact abort and whether attribute
allocation caused the refusal remain unresolved. Physical startup
and the title screen need validation.

The Java 17 target and LTS patch checks passed. The actual attribute
pool passed host refusal, exhaustion, separate ownership, cleanup
and 800 concurrently created pthread checks.

All 21 consumer host checks passed, as did signed package integrity
and the update byte comparison.

Signed full ZIP SHA-256
`4a416c1406d9cc92e4b0e5ed2a202d6a6a3b7c30d0214d820ee40b2a980a3b88`.

Two PS5 runs reached original Main and faulted at the same native
SIGBUS address. Neither run logged the preceding build's thread
creation refusal. The retained signal context does not identify the
application caller.
