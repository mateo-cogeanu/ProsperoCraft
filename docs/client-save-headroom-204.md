# Save descriptor headroom — build 204

The [retrieved failure record](validation/client202-vanilla263-save-emfile-2026-11-02.json)
confirms file-descriptor exhaustion during saving. The latest captured startup
identifies build 202 running Vanilla 26.3. The live native snapshot reports 269 open
handles, including 248 regular files, despite a much larger advertised soft limit.
This does not establish the exact title quota or the leaking owner.

The growing exception log was only partially retrieved over FTP. Its captured
prefix contains repeated `Too many open files` errors for save directories,
`raids.dat`, `world_border.dat` and chunk IO/error reporting. The ordinary tracked
handle view shows only 24 paths, mostly JARs. Original 26.3 RegionFileStorage can
retain up to 256 cache entries per storage; arbitrarily closing writable handles
or rewriting the game cache is outside this change.

## Headroom candidate

Build 204 selects the existing immutable ZipFile pool's minimum budget,
`ps5.zip.maxOpenFiles=8`, instead of 64. Generic bootstrap and runtime defaults
remain unchanged. Existing synchronized eviction/reopening and identity checks
preserve logical ZIPs, streams and indexes. OPEN_DELETE and non-ZipFile channels
stay outside the cap. Game/mod JARs and world files are unchanged.

This can release at most 56 retained descriptors compared with a full 64-handle
pool. It is **not a universal descriptor cap or a proven complete save fix**.
Mutable region caches and other owners may still exhaust the title. Additional
archive reopening can affect startup and performance.

The runtime-owned [diagnostic pin](../client/ports/save-headroom-runtime.json)
adds the read-only `/file-activity-all.txt` endpoint: up to 512 tracked entries in a
fixed 64 KiB worker stack buffer, without opening another file. The original
24-entry view remains. Tracking stays opt-in. Unwrapped native opens may be absent,
paths are 112-byte prefixes, and larger inventories exceed the view. This is not
a complete kernel handle inventory. Raw reports remain local.

## Checks and exact package

The [build receipt](validation/client204-save-headroom-2026-11-02.json) records the
clean source commit, full build audit and console limitations. Package SHA-256:

```text
89167d01c7da0ece733b0dd8b7871a05ee38ff5f79ee45b4ce9beefc5d4c14a0
```

Local launcher policy and clean source-only verification each pass all 17 checks.
The full PS5 build, link, signatures and independent package audit pass. The JVM
hash matches 203; diagnostic headers are recompiled into the consumer. The accepted
202 and candidate 203 packages and symbols remain retained.

The actual patched ZipFile implementation passes budget 8 under a real host
96-descriptor limit: 300 logical archives, concurrent reads, world-like filesystem
operations, identity rejection, OPEN_DELETE, failure cleanup and reclamation.
The omitted-option control reproduces EMFILE. ASan/UBSan instrumentation and HTTP
log-share regression checks pass. These tests do not establish PS5 save success.
[Hosted policy CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41515775488)
was inspected: Ubuntu passed; macOS remained queued when this record was written.

## Required console test

Install PPSA99874 version 01.000.204. First test a new or copied world in the
affected 26.3 instance: explore, save, leave, reopen and verify actual persisted
chunks. Repeat after longer exploration. If errors recur, retrieve
`resource-status.txt` and `file-activity-all.txt` while the failure is present.
Existing save failures mean recent edits might not have persisted; no recovery
of already failed writes is claimed.

Exact-build 26.1.x shader/quit regression, other versions/loaders, performance,
audio/haptics, Vulkan and endurance remain pending. The user's 202 shader/quit
confirmation is not assigned to 204. No release, prerelease, Store update or
frozen milestone is created.

## Accepted release — 2026-11-03

The physical tester reports that the exact 204 package works very well and
explicitly requests ProsperoStore release. The preceding pending checks describe
the original candidate handoff; this functional confirmation permits publication
without implying an exhaustive matrix or new formal ALL PASS.
[Console acceptance](validation/client204-console-acceptance-2026-11-03.json) and
[publication verification](validation/client204-store-publication-2026-11-03.json)
record the scope. The unchanged tested package is public in
[release 01.000.204](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.204).
[Catalog PR 1094](https://github.com/darkxex/ps5-homebrew-catalog/pull/1094) is submitted;
its checks, merge, deployment and live availability are not monitored.
