# Build 266: scoped 26.1.2 Fabric loading diagnostics

User reports build 265 now launches after Repair download, retaining worlds and
mods, but 26.1.2 remains frozen on the world loading screen. Current-run and
retained reports retrieved on 2026-11-08 identify Fabric 0.20.1, Sodium 0.9.2,
Iris 1.11.4 and Controlify 3.5.3. Iris reports no valid shader pack selected.
The integrated server logs player join and later occasional 6–8 second lag
warnings; the last render checkpoint grows the Dynamic Transforms UBO.
That checkpoint does not establish the blocking operation or identify Sodium
as the cause. Available GC logs show short safepoints, not a collection pause
matching the persistent frozen screen. Raw logs remain local.

FTP denies live native stderr and VM trace reads. Reopening once exposes the
retained native stderr but no exception or thread stacks explaining the freeze.
Build 266 therefore enables the existing bounded StartupObserver only for
26.1.2 Fabric using the explicit ps5.world2612Observer property. Other versions
and Vanilla retain disabled sampling. No game/mod JAR rewrite, shader, distance,
GC, allocation, storage or library-owner policy change is made.

The retained observer takes at most 48 Java/native snapshots at five-second
intervals on one daemon with a requested 256 KiB stack. Sampling can affect
performance and is diagnostic evidence, not a performance comparison or fix.
The original Main executes unchanged. Start the affected world promptly after
launch to capture its loading wait within the roughly four-minute window.
Leave the frozen run open for report retrieval; if live FTP reads are denied,
reopen once to preserve the Java snapshots in previous-java25-exceptions.log.

Physical reproduction, blocking stack identification and a repair remain pending.
No release, prerelease or Store update is authorized for 266. Preserve exact265.
