# OpenAL data-discovery lock, app148

147failedrun `client-01.000.147-1793299926-481499524` fails during loading.
The native recorder shows std::mutex caller0x19b7939 and mutex0x74e1a30 with
ENOMEM12. The exact147symbols and0x400000load adjustment identify SearchDataFiles
and gSearchLock0x70e1a30. A subsequent SIGABRT is the known exception formatter's
995byte allocation failure, secondary to the lock failure. This is a different
lock from147's HRTF cache locks. Raw run reports stay local.

148changes only the private OpenAL data-discovery gSearchLock to the existing
allocation-free ps5audio::Mutex, with its required include. The lock is exclusive,
nonrecursive and used with ordinary guards, not native condition-variable waits.
The search functions, local/XDG/global paths, results, ownership and error
handling remain intact. Previous nonthrowing-current-directory and HRTF discovery
behavior remain enabled. No audio/discovery bypass, fabricated success or JVM/
SDK-wide mutex change is introduced. Existing64spin/50usbackoff and no-FIFO
semantics apply. Device and HRTF lock repairs remain unchanged.

Pinned upstream source remains pristine. Target/host export the same private
helpers source; the separately patched boundary/helpers object is built against
that private source. Audit identifies the original/private source hashes. The
LGPL source export already includes the exact boundary helpers source and mutex
header; native relinking must reproduce the original ELF exactly.

Host actual OpenAL tests explicitly query HRTF specifier counts and available
names, exercising the real discovery path, alongside actual mixer/resampling/
PCM, pause/resume, retained-port/join and error controls using a host AudioOut
fixture. Target helper object must have no SDK std::mutex lock reference; exact
source differs only by gSearchLock and its include before existing boundary
patching. Package/source/pin/CRC/signature/frozen-history checks remain required.
These checks are not audible PS5 or stable gameplay acceptance.

Pending148menu/audio, Controlify/input transitions, world creation/save/reopen,
endurance and working-version regression. Overall native peak/owner and144's
unreported later exit remain unproven. Java runtime/pins/heap/GC/game/mod JARs,
instances/worlds/settings/auth remain unchanged. Preserve147and earlier canonical
candidates/symbols, accepted124, frozen milestones and Store121. No Store release
or new passing milestone.

Replacing the final global helpers mutex also removes its SDK mutex destructor
registration initializer. OpenAL now has 14 explicit constructors instead of 15;
the package check requires that exact count. Other constructor groups are unchanged.
