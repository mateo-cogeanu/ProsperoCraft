# Save descriptor headroom and complete-enough owner diagnostics —204

The [retrieved save-failure record](validation/client202-vanilla263-save-emfile-2026-11-02.json)
confirms EMFILE rather than a shader-specific failure. The user's26.3andother
versions report failed chunks; retrieved startup history ends in202Vanilla26.3.
HTTP cannot open its session/log files (errno24), but the allocation-free native
snapshot reports269open descriptors,248regularfiles,4sockets,0unknown and a much
larger advertised12555soft/hardlimit. This does not measure an exact titlequota.

FTP recovers startup and exception data. The growing exception stream transfer
was incomplete; its captured prefix includes repeated Too many open files on
save directories, raids.dat/world_border.dat and chunk IO/error reporting. These
are current title save failures, not inferred from older probes. Wrapped accounting
has244live entries but its ordinary view shows only24paths, mostly JARs. Native
library opens can be absent and paths are112byte prefixes. The leaking owner or
complete distribution is not proven. Original26.3RegionFileStorage can retain up
to256cacheentries per storage; it is not safe to arbitrarily close those writable
handles or silently rewrite the game cache.

## Narrow headroom change

204selects `ps5.zip.maxOpenFiles=8`, the existing runtime0126pool's minimum, instead
of64. Generic bootstrap still defaults64 unless the wrapper opts in. The runtime
core defaults remain unchanged. The genuine immutable ZipFile read-only descriptors
are evicted/reopened by the existing synchronized pool with identity checks;
logical ZIPs, entry streams/indexes remain. OPEN_DELETE and non-ZipFile channels
stay outside the cap. No game/mod JAR or world-file change, no fabricated save
completion, no arbitrary mutable descriptor eviction or unsafe retry after writes.

This reduces maximum retained ZIPpool descriptors by56only when the old pool was
full. It is **not a universal process/file cache cap or a proven full save fix**.
Mutable region caches and other users may still exhaust the title. Archive reopen
I/O/serialization can increase;26.1.xstartup/shader/quit and performance need exact204
regression despite202's confirmed results. Preserve202and203exactpackages/symbols.

The runtime-owned [diagnostic pin](../client/ports/save-headroom-runtime.json)
adds `/file-activity-all.txt`: up to512existingtrackedentries in a fixed64KiBworker
stackbuffer, without opening a new file. The original24entry endpoint remains.
No handle ownership/close/allocation-policy change, no preset device address or
client filter. Native internal opens may be absent,112bytepathprefixes can truncate,
more than512entries can exceed the view; it is not a full kernelhandle inventory.
Raw paths/reports stay local. The defaultdisabled instrumentation stays disabled.

The actual target-built ZipFile test runs budget8under a real96descriptor host cap:
300logicalarchives, stored/deflated bytes,6concurrentreaders, partialstreams/shared
refs, deepworld-like write/read/walk/delete, changed-archive refusal, OPEN_DELETE,
constructorfailurecleanup and poolrelease. Omitted-option control really fails
EMFILE. This is real Java filesystem/ZIPbehavior, not original game save or PS5
capacity acceptance. Host instrumentation test verifies extended300entry output,
legacytruncation/concurrency and non-owning realhandle behavior with ASan/UBSan.

## Required console test

Install PPSA99874 /01.000.204 and first retest the affected26.3instance: create/save,
leave/reopen and verify actual persisted chunks after movement/exploration. Collect
resource-status.txt and file-activity-all.txt while errors are present. Existing
save failures mean new edits might not persist; no recovery of already failed
writes is claimed. Repeated save/reload, longerworldtravel, quit/relaunch,26.1.x
shader and audio/haptics/Vulkan/performance/endurance remain pending. Existing
worlds stay untouched by packaging. No release/prerelease/Store or freeze.
