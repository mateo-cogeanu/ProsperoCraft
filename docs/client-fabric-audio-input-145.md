# Scoped audio locks and input/presentation diagnostics, app145

The user reports144Controlify responds to a button, updates the screen, then the
app closes. Safari's preserved run
`client-01.000.144-1793296414-601953825` confirms Controlify loads and connects
the DualSense through SDL. The last sampled Java render stack is processing GUI
TextureSetup equality/mesh state. It is a sample, not a fatal instruction or
proof Controlify caused the exit. No matching new JVM fatal report was obtained;
the retrievable HS report is from141and is excluded. Direct-memory diagnostics
record no allocation failure/budget rejection at their retained checkpoints.
Overall exit cause and world/save behavior remain unproven. Raw reports stay local.

The native output does identify a separate concrete audio failure: alcOpenDevice
catches `mutex lock failed: Cannot allocate memory`, including the PS5 backend
AudioState path. Logging itself also records the same SDK mutex failure.145
replaces only the OpenAL logging-callback mutex and consumer PS5 AudioState/
retained-port mutexes with fixed in-object nonrecursive atomic locks. They keep
acquire/release exclusion, try-lock semantics and standard C++ guard support,
with64short spins then a50microsecond native nanosleep backoff under contention.
They do not allocate, lazily initialize SDK mutexes or disable synchronization.
They provide no FIFO guarantee; recursive use remains outside their contract.
All other OpenAL/SDK/JVM synchronization stays unchanged. Native audio port,
format, actual OpenAL mixer, output pacing, worker lifecycle and error handling
remain in place. This is not a confirmed PS5 sound repair or crash repair.

The original pinned OpenAL sources/archive remain intact. A private logging.cpp
object uses the consumer mutex hook alongside the existing privately compiled
backend. Audit records identify all replaced members and source/object hashes.
The source-relink recipe exports the new header and exact modified logging
source so rebuilding does not silently lose the repair.

For the unreported exit, SDL's joystick update optionally calls a consumer-only
input-change observation hook. It does not change button/controller state. The
first8mask transitions arm at most8subsequent queue-present observations each;
existing in-flight flips can also be observed while that window is armed.
Fixed atomics bound/deduplicate activity without native initialization. Native
notes bracket queue entry/return and the original fence/flip results. Those
results and ordering are unchanged; no presentation fallback or fabricated
success is added. These notes use a dedicated bounded path, so the earlier
startup WSI probe quota cannot hide them. Existing stack/resource sampling and
extended signal recording remain enabled. Timing/diagnostic overhead can differ.

Host checks exercise actual audio locks with standard guards, try-lock behavior,
80,000contended increments, blocking/data visibility and trivial lifetime under
ASan/UBSan; retained-port ownership/reload/concurrency tests pass. The actual
pinned OpenAL library with the PS5 backend and new logging mutex passes real
mix/resample-to-PCM, pause/resume, close/join/port retention and failure controls
against a host AudioOut fixture. This is not audible console acceptance. Input
budget tests check repeated-mask deduplication,8x8queue budget, saturation,
concurrent duplicate input and shared consumption. Target/pin/source/object/
package/frozen-history checks are recorded separately.

Pending exact145 PS5 audio initialization/playback, Controlify/input-driven
screen transitions, native exit localization, Fabric26.2world creation/save/
reopen/endurance and working-version regression.144Controlify connection/input
feedback is recorded without claiming every feature or a world pass. Preserve
144and earlier canonical candidates/symbols, accepted124and Store121. No Store
release, new frozen milestone, Java runtime/pin/heap/GC change, game/mod JAR
rewrite or instance/world/auth/settings migration is introduced.
