# Build270: 1.21.2 Fabric long-freeze capture

User reports recurring5+second freezes on1.21.2, with one already10seconds long.
Current-run reports retrieved on2026-11-08 identify Controlify2.4.1, YACL3.6.6 and
Sodium0.6.13+mc1.21.3 on genuine Fabric0.20.1. The server completes spawn in5046ms,
logs player join, and the renderer starts one worker/loads advancements. Later
Saving and pausing messages are present. No captured long safepoint or GC allocation
stall explains the freezes; longest JVM-wide safepoint approximately6.7ms.

A Controlify haptic task reports JNA Internal TLS error on Download-2. This matches
the earlier1.21.4native setter failure; it does not establish render blocking.
The current logs have no sampled render stacks. Synchronous Zink compilation is
an existing possible source of first-use latency, not a proven diagnosis. No
changes to GC, resolution, world distances, shader policy, JNA or official JARs
are justified by this capture alone. Raw reports remain local.

270 extends the existing bounded observer to1.21.2Fabric, retaining26.1.2/1.21.4
Fabric selection. At most48Java/native snapshots on one256KiB daemon, five-second
interval, roughly four-minute capture window. Other versions and Vanilla keep
sampling disabled. Tests verify selection boundaries; diagnostic sampling may
perturb timing and is not a performance comparison or fix.

Enter the same world promptly, keep the same mods, and reproduce the long freeze
within that window. Retrieve current Java snapshots before another run; if native
FTP is denied, reopen exactly once for retained reports. Compare multiple captured
stacks before selecting a repair. Exact270startup/world/controller/save/shader and
endurance remain pending. Preserve released267 and candidate269 bytes. No release
or Store update authorized.
