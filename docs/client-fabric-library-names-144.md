# Native library-name fallback, app144

The user confirms143reaches the menu. Current-run Java snapshots corroborate
ongoing renderFrame/runTick calls. This is menu-startup evidence, not full
acceptance: the user also reports world creation remaining on Loading terrain.
The live report identifies Starting integrated server failing before a server
thread is started: Deflater could not initialize after an earlier bare
OutOfMemoryError in NativeLibraries.findBuiltinLib while compression support
loaded. Controlify records the same native lookup error while loading its SDL
resident library. These concrete failures share a temporary library-name
allocation path; this is not evidence of slow terrain generation or a save pass.
Raw reports, account data and instance paths remain local.

The reusable repair is published in ps5-java25-homebrew commit
`b1df916944e53dee39ee41f6681f1af3f7dc32a1`, patch0132. NativeLibraries.c already
tries libc then anonymous pages for temporary name/symbol buffers. It now uses
patch0127's bounded mapper and matching release, under the existing default-off
JNU_PS5SetDirectScratchEnabled policy, which the consumer explicitly enables.
Direct mapping is a final option only after anonymous ENOMEM. The new translation
unit has64entries/8MiB; libjava's three temporary scratch units total24MiBmaximum.
The independently gated libnet ledgers remain separate. Failed cleanup retains
bounded ownership; exhaustion still fails. No library search/registry/alias,
JNI lifecycle, class recovery, game/mod JAR, heap/GC or global allocator change.

144pins that runtime commit/patch, embeds the rebuilt NativeLibraries.o and
matching libjava.so, and audits their hashes with the original temporary-buffer
objects. Reusable runtime implementation stays in the Java repository. Previous
runtime/graphics fixes and143diagnostic sampling/recording remain. A fresh app
process is required: this does not clear an already failed class initialization
inside143's running JVM. Existing instances/world data/settings/auth remain.

Runtime tests execute the actual native lookup/symbol-construction bodies under
a real host JVM with Xcheck:jni/UBSan. Default-off libc/mapped/refusal, malformed/
null/unknown names, JNI OnLoad/OnUnload lookup, Java string failure and512repeat
cleanup controls pass; opt-in direct lookup succeeds under simultaneous libc
and anonymous refusal. Direct syscalls are host fixtures. Existing actual scratch
mapper bounds/slots/concurrency/rollback/failed-cleanup ownership checks and the
genuine PS5 java.base-libs build/object refs/hashes are recorded separately.
Consumer launcher, target, package/pin/source/library/CRC/signature/frozen-history
checks are required before handing over the exact candidate.

143's OpenAL device and diagnostic mutex failures remain unresolved;144does not
claim audio repaired. Pending PS5 exact144 Controlify/FFM, compression/integrated
world creation, save/reopen, input/audio/endurance and working-version regression.
143menu feedback does not establish ALL PASS, new frozen milestone or a public
release. Preserve143and prior canonical candidates/symbols, accepted124, frozen
milestones and Store121. No Store release or branch merge.
