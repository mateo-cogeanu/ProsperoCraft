# Minecraft 1.20 title screen test 013

PPSA99878 version 01.000.013 starts the original Minecraft 1.20 client
in demo mode after the native display handoff. It uses the Java 17,
LWJGL 3.3.1, Zink and OpenAL paths from build 012. The local package
includes the original client and dependency JARs, asset index 5 and all
3,575 indexed asset objects verified by publisher hash and size.

The demo uses a fixed placeholder identity, disables multiplayer and
chat, and writes game files to the test title's own `mc120-demo` folder.
The startup test keeps interpreter mode and raises the heap limit from
128 MiB to 384 MiB for the full client. Both the new heap limit and
the title screen need physical PS5 verification.

Install the signed local ZIP and run rows 1 through 3. Allow time for
the interpreted client to load. Stop at the Minecraft title screen
for this test. If it hangs or shows an error, leave it open for log
retrieval. If it crashes, reopen the probe once. The game log is
`mc120-java17-game.log` in the test title's report directory.

Target compilation, signing, the host argument gate and asset
verification are build checks. The hardware test covers the original
client's title screen. World loading, save, rejoin and quit need
separate console checks. The signed package and publisher payload
are stored locally.

Signed local ZIP SHA-256
`604192a70317f49a8978b163684d3464fc9cd488ab19416086df4bba71bb5003`.
Every packaged asset and classpath input was checked against its
recorded digest. Both host lanes passed.
