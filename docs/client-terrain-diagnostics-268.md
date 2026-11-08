# Build268: 1.21.4 Fabric terrain-loading diagnostics

On2026-11-08 the user reports build2671.21.4Fabric frozen on Loading terrain,
including the background animation, while the PS5 remains responsive. Current-run
reports retrieved through Cyberduck identify Fabric0.20.1 and Controlify3.0.1 LTS.
The integrated server completes spawn preparation in4196ms, logs player join and
later a block-entity warning. Last render message loads two advancements. Longest
captured JVM-wide safepoint is approximately4ms; no GC allocation stall is logged.
These observations do not establish the client blocking operation.

A preceding Controlify haptic task on Download-1 reports JNA Internal TLS error
from SDL_CreateAudioStream. Pinned JNA callback.c raises that message after its
pthread-specific storage setter refuses an allocated thread record. Netty also
reports getifaddrs allocation failure. These are genuine native failures, not
proof of Java heap exhaustion or the cause of the terrain freeze. The cumulative
startup report includes earlier process sessions; do not attribute old pthread
failures to this run. Raw paths/reports remain local.

268 extends the existing explicit ps5.world2612Observer selection to1.21.4Fabric.
Retain26.1.2Fabric selection,48Java/native snapshots at5second intervals, one
256KiB daemon and original Main. Vanilla/other versions remain excluded. No JAR,
GC,storage,allocation,graphics or JNA policy change is made. Sampling can perturb
performance; this is a diagnostic candidate, not a claimed fix.

Launch the affected world promptly so its wait falls in the roughly four-minute
capture window. Leave it open for retrieval; if live native traces remain denied,
reopen once to expose retained Java snapshots. Exact268 startup, terrain/world,
shader,save and endurance validation remain pending. Preserve released267 bytes;
no new release or Store update is authorized.
