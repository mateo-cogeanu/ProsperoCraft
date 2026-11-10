# Minecraft 1.20 demo test 014

The maintainer reported a crash on row 2 of build 013. This row creates
the Java VM, before the original Minecraft client is invoked. Build 014
restores the 128 MiB maximum heap from the console-passing build 012
and applies the logging and headless properties only when row 3
launches Minecraft. The 384 MiB heap remains a suspect rather than a
confirmed cause of the earlier crash.

Install PPSA99878 version 01.000.014 and run rows 1 and 2. If they pass,
run row 3 and wait for the title screen or a launch error. The smaller
heap may run out of memory during full client startup. If the app
crashes, reopen it once to make the retained report available.

The signed package and publisher payload stay local. PS5 validation
of JVM startup and the demo title screen is pending.

For a complete 013 installation, the local update ZIP contains only
the six files whose contents differ. Merge those files into the
installed PPSA99878 directory at their corresponding paths. Use the
full ZIP for a fresh installation.

Signed full ZIP SHA-256 `a1311c53d096321789d75f6bfe9095f97f4beb51de4f42497833496948a16db0`.
