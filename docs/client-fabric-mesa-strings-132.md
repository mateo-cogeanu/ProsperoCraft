# Fabric26.2 Mesa option-string allocation, app132

Build131's native SDL reserve reports mutex0/condition0 (success) and passes
those stages. Reproduced131runs reach PS5 SDL video-driver initialization, then
abort. The retained trace records native abort caller0x2b52159 and preceding
strdup caller0x2b51f26 with NULL result. Exact131ELF symbols and the same anchor
load adjustment0x400000 resolve these to0x2752159 (driParseOptionInfo abort)
and0x2751f26 (xmlconfig.c389 option-name XSTRDUP). This is Mesa option-string
allocation failure during its display-query Vulkan instance setup, not a
repeated SDL lock failure. Underlying libc exhaustion/quota remains unproven.

The combined graphics link already scopes Mesa malloc/calloc/realloc/free to the
PS5 graphics heap, but left strdup/strndup on libc. App132 supplies consumer-owned
string duplication functions using that same graphics malloc provider, and
binds Mesa and graphics-native callers to them. Both functions produce ordinary
NUL-terminated copies with checked size and ENOMEM on allocation failure;
strndup never scans beyond the requested bound. Existing scoped free/realloc
owns these strings. SDK platform internals retain their existing original libc
string ownership; JVM/global libc behavior is unchanged. No Mesa source or
official game/modJAR is modified. A genuinely exhausted graphics heap can still
return NULL and cause the existing caller error; errors are not suppressed.

The graphics audit pins source/object hashes and strdup/strndup binding targets.
Target checks require both adapters in the final ELF and no raw strdup/strndup
references in the rebound Mesa object. Host ASan/UBSan extracts the actual Mesa
XSTRDUP macro, reproduces its abort with libc duplication refusal, and verifies
the new route, empty/UTF8 strings, bounded nonterminated input, zero/SIZE_MAX
bounds,10000cycles, allocation failure errno and complete paired cleanup.
The software OSMesa provider receives the same two binding changes. Its audit
requires all other fields and lifecycle/context objects to match the frozen
provider. Reapplying its old map to the unchanged raw object must reproduce
the frozen object checksum exactly; frozen artifacts are not modified.
Target/launcher/package checks are in the matching validation record.

This is consumer graphics-dependency integration in ProsperoCraft only. Runtime
130pins/compilerTLSpolicy,131native sync reservations and prior startup diagnostic
retention remain unchanged. No Java heap/GC/instance/settings/auth changes.
PS5 Fabric26.2 display initialization, render/world/input/audio/save/reload and
endurance remain pending. Preserve131/priorcandidates, accepted124vanilla and
Store121. No Store release/frozen milestone; raw reports remain local.
