# OpenAL device state lock, app146

145failedrun `client-01.000.145-1793297205-488924696` closes during the loading
screen. The new signal recorder captures SIGABRT. The native throw record reports
`mutex lock failed: Cannot allocate memory` and a direct caller at0x1956f4d.
Using the exact145symbols and0x400000load adjustment resolves that caller to
alcGetString's `dev->StateLock` operation. Disassembly shows the device-field
address and call to the actual SDK std::mutex lock. The subsequent abort is
exception-name formatting realloc995bytes failing, which obscures the original
exception. The last Java sample in shader compilation is not this fatal caller.
Raw reports remain local; the signal/context/name data do not enter source Git.

145repaired the logging/PS5 backend state/retained-port locks but did not change
OpenAL's own Device::StateLock.146uses the same existing allocation-free,
nonrecursive ps5audio::Mutex for that one field. State exclusion, lock guards,
try/unique-lock behavior and explicit unlock ordering remain intact; this field
is not passed to condition-variable waits. Other Device locks and SDK/JVM native
synchronization remain unchanged. There is no exception suppression or fake
OpenAL/device success.

Because this changes a shared native structure, the builder exports the pinned
OpenAL source to a private build tree, changes only Device::StateLock and its
header inclusion, and compiles the complete library consistently against that
header. The private ALC/helper/logging/backend objects also use the same tree.
Original pinned source/cache remains pristine. Audit hashes identify original/
patched Device headers and mutex source. The LGPL relink source export includes
the exact Device header and mutex header so the original layout can be rebuilt.
No game/mod JAR, Java runtime/pin, heap/GC, instance/world/auth/settings change.

Checks include an actual host OpenAL rebuild with the modified Device layout,
actual OpenAL PS5-backend mixer/PCM/lifecycle/error tests, existing80,000operation
mutex contention and port-retention controls, target full library rebuild and
source/object/ELF/package audits. Host AudioOut is a fixture, not proof of audible
PS5 output. Console146menu/audio/Controlify/input transitions/worldcreation/save/
reopen/endurance and working-version regression remain pending. This addresses
the concrete145device-lock failure; it does not prove144's unreported later exit
fixed. Preserve145and earlier canonical candidates/symbols, accepted124, frozen
milestones and Store121. No Store release or new passing milestone.
