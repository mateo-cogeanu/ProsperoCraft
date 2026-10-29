# OpenAL context locks and event workers, build 150

149 failed run client-01.000.149-1793301493-600091835. The pre-JVM mixer
reserve succeeded and the native report confirms the first real PCM block was
submitted. That repair progressed past the previous mixer startup failure.

The original fatal lock error is traced to alEnable's context property lock:
caller 0x1952f55 minus load adjustment 0x400000 resolves alEnable_; disassembly
locks context+0x1b8, matching recorded mutex0x200621dff8 and context0x200621de40.
Earlier, caller0x192bfaf identifies alDebugMessageControlEXT_ and its debug lock
at context+0x200. Both throw ENOMEM12. A subsequent SIGABRT while formatting an
exception is secondary. Raw reports and account-specific paths remain local.
The separate OpenAL async event thread creation failed with error35; HRTF
filesystem enumeration ENOMEM was caught and remains an unresolved discovery
limitation. No HRTF data or discovery is disabled.

150 changes all five Context exclusive nonrecursive locks and the remaining
three Device buffer/effect/filter locks to the existing allocation-free mutex.
This covers the same allocation-sensitive audio API family, including the two
proven failures. Device StateLock and previous global HRTF/data locks retain
that implementation. None of these fields is paired with a native condition
wait. All users are rebuilt from one private source tree with matching layouts;
the debug method's explicit unique_lock type matches its new lock type.
No SDK/global/JVM lock interception or error suppression is introduced.

Two event workers are reserved before Java starts, independently of the two
mixer workers, using the same tested 256 KiB process-lifetime worker mechanism.
An event worker runs the original EventThread function. The original async FIFO,
notifications, kill event and drain sequence remain; completion is awaited
before releasing the worker/context. Pool exhaustion is reported just as the
upstream thread-creation failure was, with no invented delivery success. The
bound is two active event contexts. Idle worker polling is 1 ms. No FIFO
scheduling guarantee is added. Existing mixer/AudioOut semantics stay intact.

Host tests run actual debug-message control and source-distance-model enable,
actual asynchronous source-state callbacks, PCM/resampling, pause/resume,
repeated context/device reload and error paths. Native audits check the matching
source hashes and that debug/state/event objects no longer reference SDK mutex
lock. Exact source/worker headers are included in the LGPL relink export.
Target compilation and host tests are not console acceptance.

Pending exact150 PS5 loading/menu input, audible sound, async events, world
creation/save/reopen, endurance and working-version regression. 148's later
unreported menu exit remains unproven. Preserve149 and earlier canonical
packages/symbols, accepted124, frozen milestones and Store121. No Java runtime
pin/heap/GC/game/mod JAR/auth/settings/world changes, Store release or merge.
