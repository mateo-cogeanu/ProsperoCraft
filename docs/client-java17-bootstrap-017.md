# Minecraft 1.20 metaspace reservation test 017

Build 016 crashed during row 2 in HotSpot universe initialization.
The PS5 trace records a 64 MiB OOM_MMAP_ERROR at the non-class
metaspace node reservation. Build 017 uses the Java 17 runtime from
commit 59da807, which allocates these nodes in 16 MiB increments on
PS5. The Java heap stays at 192 MiB. The target object audit confirmed
the new reservation size and the signed package passed verification.

Install PPSA99878 version 01.000.017 and run rows 1 and 2. If both
pass, run row 3. For a complete 016 installation, merge the local
update ZIP into the existing title directory. Physical VM startup
and the Minecraft title screen still need validation.

Signed full ZIP SHA-256
`aec349e4b501b45318dfa9a0f34553fcb4dfad35afc0c84afa254236decf327b`.

On the PS5, 017 passed VM startup and clean shutdown. The original Main
failed at `aoi.<clinit>` line 113 with an unclassified OutOfMemoryError.
The Java heap showed 55,340,048 bytes used, 83,509,248 committed and
194,641,920 maximum. The failing resource was not identified.
