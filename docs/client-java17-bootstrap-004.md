# Java17 bootstrap004 row3 diagnostics

003's[retained record](validation/client-java17-bootstrap-003-crash-2026-11-09.json)
confirms JNI_CreateJavaVM returned successfully at128MiB, after universe/global,
Java language and module initialization. Row3then crashed before its Java stage
file was created. The earlier fault scope ended after VM creation, explaining
why it could not capture this later boundary. No row3cause or complete game pass
is established; the512MiB failure's cause remains unproven.

004keeps the same128MiB/extended image/331policy. It brackets ClassLoader lookup,
DefineClass, native registration, method lookup and run()entry with native log
checkpoints. A consumer-owned nativeStage records Java entry and points before
Path.of/writer creation, management,331and original Main, without needing Java
file initialization to work first. The runtime helper's default-null callbacks
preserve original17/21probe behavior. Runtime source:`c850651f528eb3cb3f0412558cda8e29d6638e40`.

The existing diagnostic fault scope now also surrounds row3and exception printing,
forwarding the pre-existing VM handlers. An opt-in16report budget bounds normal
recoverable signal logging while forwarding continues after exhaustion; default
other consumers stay unlimited. No context rewriting/recovery, VM/GC/heap or
original game/JAR changes. A real host signal fixture proves20signals still reach
the previous handler with only2reports, and restoration works, under sanitizers.
It disables context capture only for host policy testing, not the PS5 build.

Install standalone PPSA99878 **01.000.004**, run1,2then3; finish4if3passes.
If it crashes, reopen004once and leave the test open without repeating the crash.
Report the first failed row or ALL PASS for these four boot checks only. There
is no playable menu/world/C2/shader/performance acceptance yet.

Local`dist/PPSA99878.zip` SHA256`6151dccd27cde0592101c064fa56b96f590d984d18ef79d3bea6ec3cdec2383e`; see the
[build record](validation/client-java17-bootstrap-004-build-2026-11-09.json).
The existing three native report paths and active FTP location are documented
in[002](client-java17-bootstrap-002.md). Raw reports remain local. Previous failed
candidates, frozen17/21startup and working25launcher are preserved. No release or
Store update; original publisher payload stays local.

The portable native lane now has14checks, adding the actual signal-budget/
forwarding/restoration fixture alongside all prior13. Required21fast and14native
checks pass; hosted CI and exact physical004results are separate evidence.
