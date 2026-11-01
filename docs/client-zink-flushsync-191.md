# Candidate-only synchronous Zink submission —191

190 exact run `client-01.000.190-1793541384-788775201` fails check4 after
`MESA: error: zink: Failed to create flush queue.` The
[run receipt](validation/client190-console-flush-queue-2026-11-01.json) pins package,
run and local raw-report hashes. Guard acquisition and context allocation complete;
Zink screen creation enters and returns failure. Original Main then returns without
successful startup, and the unchanged verifier correctly rejects clean shutdown.
No fatal report was captured(hs-error errno2). This is not a quit repair.

The pinned Mesa `zink_screen.c` calls `util_queue_init` for the asynchronous
`zfq` flush queue. That initializer can fail allocating queue storage or starting
its first worker;190's generic Mesa message does not distinguish those branches.
Do not claim a proven native thread quota, leaking owner or exact allocator cause.

## Supported upstream workaround

191 enables the existing **`ZINK_DEBUG=flushsync`** option before entering the normal
native launcher bootstrap, ahead of the first Zink screen. In the pinned upstream
code this sets `screen->threaded_submit=false`, skips the `zfq` initialization and
runs the real `submit_queue` function directly instead of enqueuing it on that
worker. Vulkan submissions, fences, waits and synchronous presentation remain real.
This does not silently convert a failed queue into success; the asynchronous queue
is not requested. No Mesa/game/mod implementation is replaced or JAR rewritten.

This is a **candidate-only workaround** for the observed failing queue. Existing
ZINK_DEBUG tokens are preserved with an exact-token/idempotent bounded setter;
configuration failure stops before launch. Missing/default builds retain their
policy. The same component and native API implementations as190 are linked.
Other queues, including shader/cache workers, remain required and can still fail.
Synchronous flush/present may affect throughput; there is no FPS/refresh or broad
native-allocation/stability claim. Render quality/settings are unchanged.

The optional host test `test_zink_flushsync_host.py` takes explicit compiler,
frontend and output paths. It uses the actual policy helper, real frontend GL
clear/draw/readback/guard/thread/lifecycle workload, and a host-only macOS native
thread-name observer. The default positive control creates genuine `zfq` workers;
the same workload succeeds under the candidate policy with **zero `zfq` workers**.
Interposition observes names and forwards native results; no worker success is
fabricated. This manual graphics test is outside portable CI and never packaged.
`test_zink_submit_policy.py` adds actual policy bounds/token/preservation/setter-
refusal checks under ASan/UBSan to the optional native lane.

## Exact191 PS5 test

Install complete PPSA99874 / **01.000.191**. Launch the same **Fabric26.1** instance
through the normal launcher. Report title/world/mod behavior separately. If it
fails or stays black, leave that screen open for current-run report retrieval.
Vanilla/Fabric26.1,26.1.1,26.1.2 remain Development tests; accounts, upstream
Fabric/Knot/Mixin, adapted GLFW and original OpenGL launch arguments remain.
Iris stays guarded. No 26.1.x version pass follows from another version's result.

**Quit-crash repair stays deferred.** Normal startup/session/restart sources match
187/188/189/190;191's wrapper only applies the upstream submission option and calls
that same bootstrap. Preserve every previous ZIP/symbol/receipt, current179
published identity, original JARs and frozen history. Retain029OSMesa, callbacks,
SDL/RADV ownership/reserves,shaderc/OpenAL/input/audio, runtime descriptor/ZIP/
ImageIO/JNA/aliases and allocator/scratch/verifier/emutls/network/sync/thread-stack
workarounds. No release/prerelease,Store update,archive freeze or full ALL PASS.

Build with `package_zink_fabric_sync.py` and explicit179 ZIP/relink/build inputs,
190component,runtime,JDK25,LLVM/LLD. Isolated output is `build/zink-jvm191` and
`dist/candidates/zink-jvm-191`; ZIP overwrites refused. `test_client191_package.py`
checks exact identity/hashes/classpath/canonical GL and diagnostic labels, relocated
staged guard init, normal original Main, candidate policy wrapper, original JARs,
shutdown-source preservation, one graphics copy/resident groups and signatures.
PS5 title/world/audio/save/reopen/lifecycle for all Vanilla/Fabric26.1.x releases,
26.2/26.3/snapshot Vulkan regressions, performance/resource reclamation/endurance
and the explicitly deferred quit issue remain pending.
