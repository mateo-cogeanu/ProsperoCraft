# Local 207 — allocation-free PNG callbacks on Java workers

Title **PPSA99874**, app **01.000.207**, development Vanilla **1.21.11** only.
The user reports that 206 created a world and joined before crashing. Retrieved
206 reports confirm spawn generation, player login/join, advancement loading and
initial world buffer resizing. This is progress, not world/save/endurance acceptance.
Original 204/205/206 packages remain retained. Other 1.21 releases and Fabric stay
gated; no release, prerelease or Store action is authorized.

Signed ZIP SHA-256:
`06465d7debb74ad6652f8ca26c6d3a4bb0554d7a5768256822465edd8e5f8787`.
ZIP size: 127,438,253 bytes. Independent package audit passes. Exact build source is
`eaa0f2670fc654556a53cdeb6dcebf70e2ea00be`, with a clean source tree. Actual Ubuntu
and macOS policy CI jobs pass for that source. Later validation/documentation
updates do not rebuild the signed artifact; PS5 repair acceptance remains pending.

## Failure evidence and repair

FTP retrieved current startup history and preserved 206 Java/native reports after
reopening. The failed run is `client-01.000.206-1793811062-572846927`.
Its fatal stack is `LWJGL333 native thread state allocation/key refusal` in
`STBImageWrite.nstbi_write_png_to_func` on a Java thread-pool worker, while writing
the original game's image. The native fatal exits through VM abort. The combined
old message does not establish whether the tiny record allocation or TLS setter
failed; the underlying native allocator/quota owner remains unproved. There is no
basis to treat the later buffer-resize messages as a graphics fault.

The callback worker already belongs to the JVM. PS5 `getEnv` now asks genuine JNI
GetEnv for that thread's existing environment, without creating a redundant native
record or calling the native TLS setter. If this generation previously attached a
native thread, its existing async flag remains true. Foreign attached threads stay
foreign-owned. A genuinely unattached native thread still uses the original attach,
record/TLS/destructor path. That path now distinguishes record and setter refusal
in its fatal diagnostics; no failure is silently accepted.

No new reserve, heap/GC change, thread count, stack budget, provider, game class or
JAR transformation is added. The 206 closure reserve and bounded HTTP handler
remain. Bootstrap and original 343/provider objects remain exact 206/204 policy.
The complete 333 native group stays 209 target units (208 in the stock host build).

## Verification and limits

`test_lwjgl333_png_worker.py` uses the actual patched common_tools and original
STB PNG encoder/decoder, genuine libffi and original publisher 333 Java bindings.
Only record calloc/TLS setters are fault-injected. On 32 Java workers, 64 PNG
write/decode cycles pass with those operations forced to refuse, and assert that
neither operation was attempted. The historical native code reproduces the same
fatal refusal in this real PNG callback path. The helper/library/enum selection
are host fixtures and are never packaged as game classes.

The ASan/UBSan/XcheckJNI ownership fixture also passes allocation-free attached
callbacks, own native attach/reentry/destructor cleanup, foreign native attachment,
32 threads/3,200 foreign-table cycles and existing malloc/calloc/key refusal controls.
Genuine core/STB/1,600 callback lifetimes and three original 1.21.11 GlDevice/Zink
context cycles pass separately, including missing-Zink refusal. These are scoped
host checks; no host result establishes the repaired PS5 world lifecycle.

[Validation](validation/client121-vanilla-207-2026-11-04.json) records local, hosted,
target/package and physical evidence separately. First retry loading the existing
disposable world, then save/title/reload, input/audio, Quit/library/relaunch and
another new world. Preserve existing worlds on failure. Regress the existing 26.x
and shader paths on the same build. Exact-build shader loading/rendering remains
required before release unless explicitly scoped out. Native pressure, loopback/
interface warnings, resource peaks and endurance remain separate unresolved scope.
