# OpenAL HRTF native locks, app147

146failedrun `client-01.000.146-1793299213-131825017` fails during loading.
The bounded C++ recorder shows caller0x19bd95e and mutex0x74e1a90, followed by
system_error12 (mutex lock failed: Cannot allocate memory). The exact146symbols
with0x400000load adjustment resolve the caller to EnumerateHrtf and the mutex
to EnumeratedHrtfLock at0x70e1a90. The later SIGABRT/realloc995failure occurs in
exception-name formatting and obscures the original failure. This is concrete
native evidence, not an inference from a sampled Java shader stack. Raw logs
stay local. The old Device::StateLock failure is not this recorded caller.

147changes the two HRTF globals LoadedHrtfLock and EnumeratedHrtfLock to the
existing allocation-free, nonrecursive ps5audio::Mutex in the private pinned
OpenAL source tree. These globals use ordinary exclusive guards, not native
condition-variable waits. Acquire/release protection, all HRTF discovery/loading/
cache contents and format/filtering behavior stay in place. No mutex failure is
ignored or success fabricated; HRTF/audio is not disabled. The same small atomic
state/64spin/50usnative backoff and no-FIFO/lifetime limitations apply as145/146.
Other OpenAL/SDK/JVM locks remain unchanged.

The original upstream cache stays pristine. Target and host use the same private
source edit, with exact original/patched HRTF and mutex-header hashes in the native
audit. The full library build keeps the previous Device::StateLock layout
consistent. The LGPL source-relink export includes the exact HRTF source and its
mutex header alongside the Device headers and other modified sources.

Tests rebuild real host OpenAL and run the PS5 backend's actual mixer/resampling/
PCM, pause/resume, port retention/join/error controls with a host AudioOut fixture.
Existing actual mutex concurrency and retained-port tests remain applicable.
The target HRTF object must have no SDK std::mutex lock reference; its exact
source must differ from pinned input only by the two locks and required include.
Target package/runtime/source/pin/CRC/signature/frozen-history checks and exact
native ELF relink reproduction are recorded separately. Host PCM results are
not audible PS5 acceptance or a console crash pass.

Pending exact147startup/audio, Controlify/input-screen changes, world generation/
save/reopen/endurance and working-version regression. This repairs the identified
146HRTF-lock failure; no claim is made that144's unreported later exit or every
native allocation issue is resolved. Java runtime/pins/heap/GC, game/mod JARs,
instances/worlds/settings/auth remain unchanged. Preserve146and earlier canonical
candidates/symbols, accepted124, frozen milestones and Store121. No Store release
or new passing milestone.
