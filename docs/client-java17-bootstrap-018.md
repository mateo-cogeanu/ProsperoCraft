# Minecraft 1.20 memory diagnostics test 018

On the PS5, 017 passed JVM creation and destruction. The original
Minecraft Main failed during class initialization at aoi line 113.
The error was unclassified. Java heap use was 55,340,048 bytes with
83,509,248 committed and a 194,641,920 maximum. Those figures alone
do not establish the failing memory resource.

PPSA99878/01.000.018 uses Java runtime source 3207e67 and retains the
017 heap and metaspace settings. The consumer distinguishes an empty
OOM detail and the fixed HotSpot C heap and allocation messages.
The runtime traces its first reported HotSpot OOM, bounded commit
refusals and bounded libjava OOM requests. Original game inputs remain
intact. If row 3 fails again, retrieve the stage, bootstrap and VM trace
logs from that run. Physical title-screen validation is pending.

The Java 17 target build, 21 consumer host checks, signed container
integrity, and update byte comparison passed. The update retains the
017 game assets.

Signed full ZIP SHA-256
`975c7cf3b09cb17b89e8db6e56532305e5555ffef12c1c0872ff9151f70d7931`.

On the PS5, 018 reproduced row 3 at the same frame and heap usage.
The trace recorded none of the new OOM or commit refusal markers.
