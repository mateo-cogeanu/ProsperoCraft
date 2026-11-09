# Minecraft 1.20 with Java 17, bootstrap 008

On PS5, build 007 passed Main class initialization. During the original
Main method, its utility initializer threw an IllegalStateException when
it could not find an installed `jar` filesystem provider. The original
client bytecode and a host run with the same restricted module list confirm
the failure. Adding `jdk.zipfs` on the host reaches the original required
argument check.

Build 008 uses an image with the genuine target-built OpenJDK `jdk.zipfs`
module, which supplies that provider. The image contents and package were
checked, including all 47 packaged JARs and the classpath manifest
against build 007. The runtime image tooling is published at f9b5c6d in
ps5-java25-homebrew.

Local signed PPSA99878 ZIP, version 01.000.008, SHA-256
`c20840a332bbf5f94d23d90d6860d2b96989b442e256d0388455f7bbd0acd00c`.
The maintainer reported all four rows passed on PS5. The original game
reached its required argument check after ZIP filesystem provider discovery,
and the JVM shut down successfully. See the
[console record](validation/client-java17-bootstrap-008-console-2026-11-09.json).
Menu, rendering and world startup are the next validation steps.
