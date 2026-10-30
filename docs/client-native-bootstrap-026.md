# Client026 — real callback and OpenAL acceptance candidate

026 follows025's observed native-bootstrap failure. It adds actual
[libffi3.8.0](https://github.com/libffi/libffi/releases/tag/v3.8.0) and pinned
[OpenAL Soft1.25.2](https://github.com/kcat/openal-soft/releases/tag/1.25.2)
implementations to the consumer's resident libraries. The separately built
LWJGL VK/ALC module platform overlay is activated for this probe. No original
Minecraft/Java artifact is rewritten;the54 original JARs remain hash-identical.
The reusable JVM/runtime image,SDK libraries and frozen milestones are preserved.
No game menu,PS5 sound output or completed Minecraft startup is claimed.

The new five-row test initializes the embedded runtime,creates a real128MiB
interpreter JVM,verifies original client artifacts,executes native acceptance,
and destroys the JVM. Press X once at the ready notification;no old graphics
input checklist is needed. No window or audible sound is expected. Keep the app
open for reports;after an exit,reopen without pressing X. The log server binds
available interfaces without preset IP addresses or client filters.

The acceptance fixture calls the normal no-argument VK.create path,including
its genuine allocation-callback class initialization. Its provider is the real
resident RADV loader on PS5. It then allocates three real LWJGL/libffi closures.
Each cycle invokes Java32times on the calling thread and32times from a new
native pthread,checking all arguments,return values and192total invocations.
The native thread exercises real JNI daemon attachment/detachment via upstream
LWJGL TLS,joins before closure release,and does not outlive the fixture.
The tested callback signature uses integer/pointer arguments;floating-point,
aggregate/variadic callbacks and broad callback coverage are not established.

OpenAL Soft's genuine upstream loopback device and mixer process a4800-frame
440Hz source into stereo16-bit PCM. Three real device/context lifecycles check
non-silence,unclipped peak,frequency via zero crossings,128guard samples,and
silence after source stop and a block drained for its normal fade/filter tail.
The compiled physical output backend is upstream Null. This is real in-memory
mixing,not speaker support or simulated AL entry points. The background music
remains absent. No fake export,success stub or game-class replacement is added.

Target libffi uses the PS5 x86-64 SysV ABI and SSE2. Unsupported Windows ABI
forwarding is disabled in an explicit dependency-source patch;the corresponding
LWJGL ABI constants report unavailable. All original JNI/upcall units are
pinned by commit,size and SHA256. Autoconf probes use the same clang/SDK SysV
headers and actual SDK import libraries without ignoring unresolved symbols;
final units compile as x86_64-sie-ps5. The standard libffi code prepares/calls
functions;only closure allocation/protection is adapted. Each closure has one
bounded page,prepared RW then changed to RX;release uses munmap. Allocation,
preparation and protection failures remain failures. Re-preparing an RX closure
is rejected. Microsoft ABI/closure-table/re-entry cases are outside this port.

OpenAL is built with real C++20 exceptions and RTTI,upstream bundled fmt/GSL,
SSE/SSE2,loopback and Null;desktop device backends are disabled. Its15 actual
initializers are retained separately and invoked by its resident JNI_OnLoad
after VM/GPU/compiler initialization. No automatic application-start constructors
run. Allocation/thread references use the existing scoped graphics providers;
JVM global wrappers and implementation are unchanged. The allocator/SDL/RADV/
shaderc baseline remains intact. Full module-unload/global teardown is not tested.

Host checks use actual pinned libffi,original LWJGL callback code and OpenAL
mixer under Java25 Xint/XcheckJNI/verification and UBSan. They run both normal
host dispatch and the actual patched PS5 enum branches using real MoltenVK and
host OpenAL providers. The enum selector is a host-only fixture,never packaged;
these are not PS5 GPU/ABI results. Both runs pass192 callbacks and three mixer
lifecycles. A separate adapter test executes generated native code on actual
RW-to-RX mappings,checks map/prep/protect/overflow/NULL/re-prep failures and
5/5 mapping releases. Its preparation test double is explicitly scoped to
allocation/protection testing;it does not establish target libffi ABI correctness.
Actual PS5 closure execution,thread attachment,mixer output and shutdown remain
pending for exact026. Do not freeze a milestone before human console acceptance.

Build tools/sources/audits live in this consumer repository. Downloaded source
archives,caches,JARs,logs and compiled output stay ignored. Local packages include
upstream license texts. OpenAL is LGPL;before public binary-release distribution,
include corresponding pinned source plus the exact relocatable/relink inputs and
instructions. Preserve current local link inputs for that future release. This
candidate is not published as a release asset. No test results license game data
for public rehosting. The server two-hour run stays explicitly deferred.

After actual026 acceptance,retry original Minecraft startup with these native
ports. OpenGL is also unconditionally loaded by the original native bootstrap;
STB,FreeType,VMA,SPIRV-Cross and other SDL callbacks remain incomplete. No menu
promise follows from passing this targeted dependency test.

Current local package: runtime workspace `dist/PPSA99874.zip`,consumer
`dist/client-native_bootstrap/PPSA99874.zip`. SHA-256: `e158f9fd76ce91f16091b6e9ee2c54a4cbaf11863f08bf77853204b6ef984d82`.
Target/package checks pass;actual PS5 result remains pending.

Console follow-up2026-10-24:human ALL5 PASS is corroborated by saved run
client-01.000.026-1792852721-557017669.192callbacks,3loopback mixer/context
lifecycles with peak5957/crossings43/guards+silence,and DestroyJavaVM pass.
[Client_Callbacks_OpenAL](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Callbacks_OpenAL) preserves exact tested
source/package/symbols/validation. The release includes OpenAL source/relink
materials;both exact ELF reproduction and edited-source library relinking pass.
Speaker output,remaining native coverage and Minecraft startup stay unvalidated.
