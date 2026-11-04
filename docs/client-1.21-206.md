# Local206 — report transport and first callback repair

Title **PPSA99874**, app **01.000.206**. This repairs two failures reported on205;
only1.21.11 Vanilla remains enabled for development testing. Other121Vanilla and
all121Fabric entries stay Coming soon. Accepted204, original205 and frozen history
are retained. No release, prerelease or Store action is authorized.

Signed ZIP SHA-256:
`c630521c465a97678d12aeb5d4ed9b21b9ed751eb399c5544380843019b34a73`.
ZIP size127,437,975bytes (+381,094 versus204); uncompressed growth1,125,220bytes.
Independent package audit passes. Build source is
`ea4ebb1cb595b6a10069b33a88fdaa289430ded6` with a clean source tree. Subsequent
auditor/documentation updates do not rebuild the signed artifact.

## Retrieved evidence

The user reports a game crash, reopening, and another exit when accessing reports
through Safari. After a fresh reopen, Cyberduck FTP retrieved the startup history,
game log and original crash report. Some root reports returned550permission denied;
retrieval was partial and raw reports remain local. The original1.21.11 crash is
`OutOfMemoryError` at `org.lwjgl.system.Callback.create`, creating the first GLFW
error callback. Its throw site means `ffi_closure_alloc` returnednull. The recorded
Java heap still has substantial free space; native mmap errno/quota and owner are
not proved by that Java exception. The unchanged clean-exit audit correctly rejects
this startup failure and preserves the nonzero exit.

The shared512-row HTTP diagnostic added a64KiB automatic array to `serve`. Exact
204/205 target disassembly reserves70,472bytes at entry, even for the index.
An actual64KiB x86_64 pthread reproduces a fault with the historical optimized
header. The repaired target frame is5,704bytes; real64KiB worker tests pass.
The PS5 fault address and actual thread-stack size were not retrieved, so this
strong reproduction does not itself establish physical repair acceptance.

## Repairs and ownership

Runtime commit/pins in [runtime.json](../client/ports/lwjgl333/runtime.json) provide
the shared handler fix: fixed BSS full-snapshot storage, nonblocking atomic owner,
503 on overlapping snapshots and4KiB request-buffer reuse for file streaming.
No stack enlargement, heap/TLS allocation, URL allowlist or listening-interface
change. Other report endpoints can continue while a full snapshot is busy.

The333 native group now includes its own closure allocator, sharing genuine libffi
prep/call C implementations. It primes64independent RW pages before JVM creation.
At the PS5 page size this reserves1MiB. Ordinary mmap remains first and only ENOMEM
may use the reserve. This is a bounded targeted fallback, not a diagnosis or a fix
for the underlying native allocator refusal. Priming failure stops initialization
with a report; a partial pool is never published. Closure preparation still makes
its page RX, and free must reset RW before reuse. Failed reset keeps the backing
quarantined; exhausted/non-ENOMEM paths still fail. Native callback/free lifetime
remains the caller's responsibility. Original343 ffi and all other native provider
objects remain exact204 bytes. Original game/library JARs remain intact.

Bootstrap's only native policy addition is the explicit333 reserve prime. Packaging
strips exactly its two guarded blocks and checks the remaining bootstrap source
against204. Existing heap/GC/reserve options, ZIP budget8, controller/auth/shader
policies, clean-return and26.x paths remain. Matched333 target is209source units;
host333 tests without this target allocator remain208units.

## Checks and physical retest

[Validation](validation/client121-vanilla-206-2026-11-04.json) records separate local,
hosted, target/package and physical results. Real x86_64 libffi tests force mmap
ENOMEM, exhaust/reuse64pages, execute3,200concurrent closures and check unprimed,
non-ENOMEM, RX failure and RW-reset quarantine under ASan/UBSan. The test uses the
genuine dynamic-trampoline x86_64 configuration; stock Apple ARM64 uses trampoline
tables and is a different backend. No genuine FFI implementation or success stub
is substituted. Original333 Java callback/STB/Zink coverage remains separate from
this allocator fixture. Their combined host evidence is not PS5 integration proof.

Run `tools/test_libffi_reserve.py --ffi-source-dir <pinned-source> --llvm-home <llvm>
--output-dir <work>` with explicit `--x86-64` on ARM Macs with Rosetta. The source
must carry the pinned source-commit marker from the existing libffi builder.
The test compiles the real upstream backend and the actual allocator adapter;
it is outside portable CI. Standard19fast and11native lanes remain required.

First leave206at the launcher and verify the report index plus startup/full file
snapshot downloads survive. Then retry the existing disposable1.21.11Vanilla
instance: title/world/input/audio/save/reload/Quit/library/relaunch. Retrieve
current-run reports on failure. Regress existing26.x and shader paths on this same
build. Exact-build physical shader loading/rendering remains a release prerequisite.
