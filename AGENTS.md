# Minecraft project scope

This repository contains Minecraft-specific PS5 homebrew work. Java runtime
fixes and acceptance probes belong in mateo-cogeanu/ps5-java25-homebrew;
reference that project instead of copying its runtime development here.

The human user authorized this public repository and publishing its README.
Keep README status accurate: Java probe passes do not establish a Minecraft
pass. Freeze a game milestone only after the user confirms its tests passed
on the actual PS5 for the exact build. Preserve passing snapshots and record
versions, dependencies, console evidence and package SHA-256 checksums.

Keep the README and its docs/readme-banner.svg consistent with project status.
Preserve the Java runtime link. Commit and push completed, authorized changes,
verify successful publication and report any failures honestly. Keep generated
builds, dependency caches, credentials, logs and unrelated files out of source
control. Passing compiled packages belong in release assets.

After every completed Minecraft source, asset, documentation, configuration
or script change, run the relevant checks, then commit and push to this
repository before ending the turn. Development can be published before
console validation; mark results pending. The user explicitly authorized
these updates. Verify each push. Runtime fixes must be published separately
to ps5-java25-homebrew using its sync script; do not mix source ownership.
Keep official downloaded JARs in ignored caches/local build packages,
with source-controlled artifact metadata and checksums for reproduction.
The initial --help bootstrap probe must not auto-accept the EULA or claim
world/server readiness from host success.

Server_Bootstrap is the frozen passing 01.000.002 snapshot. Do not modify it.
The human accepted the Minecraft EULA for the server test on 2026-10-14,
recorded in server/eula-consent.json. Development server-start code lives
in server/ and tools/. Retain passing full packages under ignored
dist/milestones before replacing the current build. Public releases omit
official game JARs and document local provisioning and separate checksums.

## Unmodified Minecraft server JAR direction

The user requires future compatibility fixes and features to live in the Java
port or the separately maintained Minecraft harness/configuration. Do not add
or expand server-JAR transformations, bytecode hooks or replacement game classes.
Keep the official downloaded server JAR intact. Existing local derivative
transformations are temporary migration debt, not the preferred architecture.

Gradually remove the existing transformations as working replacements are
implemented and validated. Move runtime compatibility into the Java port; use
vanilla configuration, ops.json and supported administration mechanisms for
Minecraft policy where possible. Do not silently remove required workarounds
or claim an unmodified server while a derivative is still executed. Record
each remaining transformation and console validation needed for its removal.
Preserve frozen passing snapshots; migrate development only.

## Work order requested on 2026-10-19

Prioritize smooth, stable server gameplay and completion of the migration to
the original unmodified server JAR. Establish actual PS5 startup, player save/
rejoin persistence and the requested two-hour baseline. Then work on server-side
mod loaders and individually validated mods for compatible pinned versions.
Client graphics, native bindings and input come after server mods work.
Track mihawk-99/PS5_Vulkan as a client graphics candidate; it is not an adopted
or validated project dependency. Keep game/mod/client plans in this repository.

## User work-order update on 2026-10-20

The user reports lag-free joined gameplay on083 and explicitly defers the
full two-hour run until later. Proceed with Fabric server/mod validation, then
Paper server/plugin validation, before client work. This overrides the earlier
requirement to finish the two-hour run before beginning server loaders. Keep
083 as a vanilla fallback and keep endurance/persistence limitations explicit.
Fabric/Paper are separate server flavors; use isolated worlds and pinned upstream
distributions. Do not add project-specific game-JAR rewrites or game replacement
classes. Standard upstream loader/Mixin behavior is part of the authorized mod
experiment and must be disclosed. Paper executes its own upstream server rather
than claiming to execute an unmodified Mojang server. No new passing milestone
is established by the083performance report alone.

## User work-order update on 2026-10-21

The user is satisfied with the Fabric experience and requests Paper next.
Validate the pinned upstream Paper distribution and a separate plugin on PS5;
once its exact candidate is confirmed passing, prepare and publish a proper
server release before client work. Do not infer a formal ALL PASS or full
two-hour completion from the satisfaction report. Preserve the Fabric094
candidate/package and vanilla083 fallback. Keep the two-hour test deferred.
Paper's upstream System.exit on shutdown is normal; report checked shutdown
evidence and distinguish a user-shortened play check from full endurance.

## User work-order update on 2026-10-22

The user reports Paper108 is much more than acceptable and by far the best yet,
after earlier satisfaction with Fabric094. The user now explicitly authorizes
client work while leaving the two-hour run pending, and requests a release
celebrating Fabric and Paper running before proceeding. Publish the accurately
qualified development prerelease and app-only artifacts; do not infer a formal
ALL PASS, completed lifecycle checklist or endurance result. Preserve exact
server packages/frozen milestones. Client work need not wait for those pending
server checks. Keep client code/artifact pins/graphics integration here and
reusable runtime fixes in the Java repository.

The user subsequently explicitly requested making Fabric-Paper-v01.000.108 a full
release, then continuing client work. Promote its GitHub release status without
inferring new console tests or ALL PASS. Keep endurance/lifecycle limitations
explicit and preserve the exact published app binaries and source tag.

The user requests reusing server title ID PPSA99874 and the same content identity
for client builds, but explicitly wants client versions to start at01.000.000
and advance independently of server versions. Do not continue the server build
counter for client packages.
Installing the client replaces the server app. Preserve tested server packages
and source snapshots for reinstalling; do not claim side-by-side installation.

Client_Foundation is the frozen passing client foundation milestone, PPSA99874
version01.000.000, user ALL PASS on2026-10-22. Preserve its source snapshot,
validation and matching compiled package. Its six foundation checks do not
establish game startup, GPU rendering, SDL/Vulkan/audio or controller gameplay.
Continue new client work in root client/, never inside Client_Foundation/.

Client_Native_Loading is the frozen passing client001 milestone, PPSA99874
version01.000.001, human ALL PASS for all seven rows on2026-10-22. Preserve
its source, validation and exact compiled package. It validates this resident
JNI loading/function-call integration, not full LWJGL/native graphics, arbitrary
ELF loading or Minecraft startup. Continue future work outside frozen folders.

Client_LWJGL_Core is the frozen passing client002 milestone, PPSA99874
version01.000.002, human ALL PASS for all eight rows on2026-10-23. Preserve
its source, validation and exact compiled package. It validates the tested
LWJGL native memory/JNI subset and PS5 resident provider; it does not establish
complete native bindings, arbitrary ELF loading, GPU/SDL/Vulkan or game startup.
Continue development outside frozen milestone folders.

Client_Native_Graphics is the frozen passing native-only client003 milestone,
PPSA99874 version01.000.003, human confirmation of all requested RGB/card checks
with no crash/corruption on2026-10-23. Preserve source, validation and exact
compiled package. It validates scoped RADV GPU clear/copy/readback and VideoOut
presentation, not Java/SDL integration, shader rendering, full Vulkan coverage
or game startup. No log retrieval was possible; evidence is the human report.
Continue development outside frozen folders.

Client_GPU_Integration is the frozen passing client004 milestone, PPSA99874
version01.000.004, user ALL PASS for all nine rows on2026-10-23. Preserve its
source, validation, exact package and symbols. It validates actual Java/LWJGL
plus resident JNI/RADV offscreen GPU copy/fill/readback, scoped provider/TLS
callback integration, three Vulkan session cycles and final JVM shutdown.
It does not establish full LWJGL Vulkan bindings, SDL/window integration,
shader/game rendering, full module cleanup or server endurance. Continue
development outside frozen folders.

Client_Vulkan_Bindings is the frozen passing client008 milestone, PPSA99874
version01.000.008, user ALL PASS for all ten rows on2026-10-24. Retrieved current-run
logs corroborate12 standard LWJGL Vulkan GPU transfers,3 instance/device lifecycles,
loader cleanup and DestroyJavaVM. Preserve source, exact package and symbols.
This validates the tested original LWJGL Vulkan command/struct/capability-table
path and diagnostic storage recovery, not complete Vulkan coverage, SDL/window
integration, Java presentation, shaders or game startup. Continue development
outside frozen folders; server two-hour endurance remains deferred.

Client_Shader_Pipeline is the frozen passing client009 milestone, PPSA99874
version01.000.009, user ALL PASS for all eleven rows on2026-10-24. Retrieved logs
confirm18 actual LWJGL/RADV compute shader dispatches, output/guard verification,
three shader/device lifecycles and DestroyJavaVM. Preserve source/package/symbols.
This is offscreen compute, not SDL/window integration, visible graphics/fragment
rendering, Java display presentation or game startup. Continue development outside
frozen folders; server two-hour endurance remains deferred.

Client_Graphics_Pipeline is the frozen passing client010 milestone, PPSA99874
version01.000.010, user ALL PASS on2026-10-24 after the twelve-row and colored
preview checklist. Retrieved logs corroborate9 graphics draws, full pixel/guard
checks,3 image/pipeline/device lifecycles, GPU readback publication and JVM stop.
Actual readback is displayed by the existing CPU menu; preserve this distinction
from SDL/window, Java-owned VideoOut/direct GPU swapchain presentation and game
startup, which remain unvalidated. Preserve exact source/package/symbols; continue
development outside frozen folders. Server two-hour endurance remains deferred.

Client_Direct_Presentation is the frozen passing client011 milestone, PPSA99874
version01.000.011, human automated-notification and explicit visual PASS on
2026-10-24. Retrieved logs confirm all12 checks,90 ordered direct graphics/FIFO
presents,36 pixel samples plus256 guards per frame and DestroyJavaVM. Native
GPU display/resources remain retained until app close; CPU display is not opened.
Preserve source/package/symbols. Teardown/handoff/resize/timeout recovery, SDL
window/input and game startup remain unvalidated. Continue outside frozen folders;
server two-hour endurance stays deferred.

Client_SDL_Window_Input is the frozen passing client014 milestone, PPSA99874
version01.000.014, human tiles/input acceptance and saved ALL12 PASS on2026-10-24.
Reports confirm real SDL3 PS5 window/Vulkan surface, physical DualSense events
and state for X/Circle/D-pad Left/left stick,537 graphics/sample/guard/FIFO frames
and DestroyJavaVM. Preserve exact source/package/symbols. SDL/native display
resources remain retained until app close; teardown/resize/focus/reconnect,
audio/callbacks/keyboard-mouse mapping and game startup remain unvalidated.
Continue outside frozen folders. Server two-hour endurance remains deferred.

Client_Runtime_Shader is the frozen passing client020 milestone,PPSA99874
version01.000.020,human nice pass on2026-10-24. Saved ALL13 PASS confirms actual
shaderc GLSL compilation/error controls across3 compiler lifecycles,18 real
runtime-SPIR-V RADV dispatches/full output+guards,SDL252frames/eventMask15/
stateMask15 and DestroyJavaVM. Preserve exact source/package/symbols. Consumer
app C++ operators use paired existing graphics heap providers; SDK/JVM/game/Java
JARs remain unchanged. Target dependency checkpoint patches and scoped fault
recorder remain disclosed. Includes/callbacks/HLSL/larger shader workloads,
textures/depth/blending/game startup/global teardown and server endurance remain
unvalidated. Continue development outside frozen folders.

Client_Texture_Depth_Blend is the frozen passing client021 milestone,PPSA99874
version01.000.021,human nice pass on2026-10-24. Saved ALL14 PASS confirms3real
texture uploads,combined sampled-image descriptors,D32 depth and alpha-blend
controls with disabled-feature comparisons,27draws/9full256x256images+guards,
existing runtime compiler baseline,SDL318frames/eventMask15/stateMask15 and JVM
shutdown. Preserve exact source/package/symbols. The texture workload is
offscreen,new graphics shaders compiled offline; visible SDL tiles remain the
baseline. No game/Java JAR or JVM/SDK changes. Visible textured scene,perspective/
vertex buffers,larger shaders,game startup,global teardown and endurance remain
unvalidated. Continue development outside frozen folders.

Client_Visible_Perspective_Scene is the frozen passing client022 milestone,
PPSA99874 version01.000.022,human all pass on2026-10-24. Saved ALL15 PASS
confirms real vertex-buffer/perspective-correct sampled scene27draws/9full
images+guards,actual verified GPU readback/upload/blit through SDL295FIFO
frames with physical event/state masks15,and JVM shutdown. Preserve exact
source/package/symbols. Static visible panel uses explicit readback/re-upload/
blit handoff,not continuous scene rendering directly into swapchain or camera
control. No game/Java JAR/JVM/SDK changes. Direct/continuous rendering,index
buffers/camera,larger workloads,game startup,global teardown and endurance
remain unvalidated. Continue development outside frozen folders.

Client_Continuous_Direct_Scene is the frozen client023 milestone,PPSA99874
version01.000.023,human PASS on2026-10-24 after explicit all15/direct scene
phase instructions. Current-run log endpoint refused connections;no session ID
or precise frame count independently corroborated. Preserve exact source/package/
symbols and distinguish human acceptance from pending log retrieval. Shared
renderer draws into each acquired SDL BGRA color attachment;requires minimum180
frames/all3phases,36samples+256guards/frame and physical masks15. No captured
scene upload/blit. Native display/renderer retained;camera controls/indexing,
larger workloads,game startup,global teardown and endurance remain unvalidated.
Continue development outside frozen folders.

Client023 follow-up:Safari native UI retrieved the saved reports on2026-10-24
while shell requests still returned No route to host. Run
client-01.000.023-1792846440-446670267 corroborates ALL15 PASS,494consecutive
direct frames/1482scene draws,all3phases,physical masks15 and JVM shutdown.
Keep the original frozen source/validation and four release assets unchanged;
docs/validation/client023-log-follow-up-2026-10-24.json and additive release
follow-up assets record this later evidence. Raw logs stay local. Camera,
game startup,full teardown and endurance limitations remain.

User work-order update2026-10-24:try actual original Minecraft client startup
now,before camera controls. Development024 calls unmodified26.3Main through
consumer harness,full5147original asset objects and supported demo arguments;
no credentials or game class transformations. Native client coverage remains
incomplete;four startup rows are not an automatic menu pass. Original game
Main return/process exit is diagnostic evidence,not menu/world acceptance.
Preserve frozen023/earlier packages and actual-console validation boundaries.

User update2026-10-24:work on genuine callbacks/libffi and OpenAL after025
reaches original Main and exits during native bootstrap.026 is a five-row
native acceptance candidate,not a game launch. Preserve original game JARs,
failed024/025 packages and frozen023. Host passes do not establish PS5 callback
ABI,mixer or shutdown;freeze only exact human console acceptance. Before a
public OpenAL-linked binary release,provide corresponding sources and exact
relink inputs/instructions with its LGPL notices. Speaker output,remaining
client dependencies and Minecraft menu remain unvalidated;endurance deferred.

Client_Callbacks_OpenAL is the frozen passing026 milestone,PPSA99874
01.000.026,human ALL5 PASS and retrieved run
client-01.000.026-1792852721-557017669 on2026-10-24. Preserve its exact
source,full package,symbols,validation and release assets.192real Java
callbacks across calling/native threads,3OpenAL loopback mixer lifecycles
with PCM/frequency/guard/silence controls,Vulkan loader/FFI bootstrap and JVM
shutdown pass. No PS5 speaker output,full callback coverage or game menu pass.
The release includes original OpenAL corresponding source and exact relink
objects/helper;unmodified relink reproduces the frozen native ELF. Original
game JARs are omitted publicly and reprovisioned locally. Continue development
outside the frozen folder;server two-hour endurance remains deferred.

Client_OpenGL_Provider is the frozen passing029 milestone,PPSA99874
01.000.029,human ALL5 PASS and saved session/startup for
client-01.000.029-1792919308-523542436 on2026-10-25. Preserve exact
source/package/symbols/validation and release assets.3real Mesa softpipe/OpenGL
JNI contexts verify192RGBA pixels/768guards and JVM shutdown. This validates
software GL bootstrap and tested PS5 dependency dispatch,not hardware OpenGL,
Minecraft startup or broad GL coverage. Vulkan remains the game renderer plan.
The release includes matching OpenAL source/relink materials;unmodified relink
reproduces the accepted native ELF. Game JARs remain original and are omitted
publicly. Continue development outside the frozen folder;endurance deferred.

Client_STB_Codecs is the frozen passing031 milestone,PPSA99874
01.000.031,human ALL5 PASS and matching saved session
client-01.000.031-1792921801-581678467 on2026-10-25. Detailed startup
download was incomplete;do not claim independent per-cycle log verification.
Accepted fixture covers3real PNG encode/read/decode/free cycles,768RGBA bytes/
384input guards,truncated PNG/invalid Vorbis controls,Perlin/native structs
and JVM shutdown. Preserve exact source/package/symbols/validation/release.
This is not valid Vorbis decode,font/resize/DXT/callback coverage or game startup.
Release includes exact matching OpenAL source/relink materials;unmodified relink
reproduces the accepted native ELF. Game JARs are omitted publicly and remain
original locally. Continue development outside the frozen folder;endurance deferred.

Client_FreeType_Fonts is the frozen passing033 milestone,PPSA99874
01.000.033,human ALL5 PASS and saved session/detailed current-run startup
client-01.000.033-1792924441-82563672 on2026-10-25. Preserve exact
source/package/symbols/validation/release.3real FreeType2.14.1 library/face
lifecycles verify9Abel glyphs at16/24/32px plus repeats,expected FNV64
fc260d7c9d8a2036,384guards,metadata/metrics,space/invalid font controls,
face/library cleanup and JVM shutdown. Other font features/formats,optional
compressed/color font dependencies,callbacks/concurrency/global teardown and
Minecraft startup remain unvalidated;server endurance deferred. Release includes
matching OpenAL source/relink materials reproducing the accepted native ELF.
Original game JARs remain intact locally and are omitted publicly. Continue
outside the frozen folder;next original Main retry must combine accepted natives.

Client_VMA_Allocator is the frozen passing035 milestone,PPSA99874
01.000.035,human ALL5 PASS and saved session/detailed current-run startup
client-01.000.035-1792926499-461213821 on2026-10-25. Preserve exact
source/package/symbols/validation/release.12real RADV copy/fill transfers across
3VMA3.4.0 allocator/instance/device lifecycles use two mapped65536-byte buffer
suballocations each;exact source/output/guards,NEVER_ALLOCATE controls,
map/flush/invalidate/unmap/free and JVM shutdown pass. Images,custom pools,
defragmentation,budgets,virtual allocations,allocation callbacks,concurrent/large
workloads/global teardown and Minecraft startup remain unvalidated. SPIRV-Cross
is still a known missing native bootstrap component;server endurance deferred.
Release includes exact matching OpenAL source/relink materials reproducing the
accepted native ELF. Original game JARs stay intact locally and are omitted
publicly. Continue outside the frozen folder;do not infer a Minecraft menu pass.

Client_SPIRV_Cross is the frozen passing036 milestone,PPSA99874
01.000.036,human ALL5 PASS and saved session/detailed current-run startup
client-01.000.036-1792927908-979234410 on2026-10-25. Preserve exact
source/package/symbols/validation/release.3contexts/9GLSL450-HLSL5-MSL translations,
exact fingerprints,SSBO set0/binding0,push8/local64 reflection,malformed SPIR-V
error controls,384guards,allocation/context cleanup and JVM shutdown pass.
One PS5 locale adapter selects the real native localeconv API;original game JARs
and runtime implementation remain unchanged. Translated shader GPU execution,
MSL compiler validation,other features/callbacks/concurrency/non-C or changing
locales/floating literals/global teardown and Minecraft menu remain unvalidated.
The next original Main retry must combine036SPIRV-Cross and035VMA with the
previous accepted natives,and set Configuration.SPVC_LIBRARY_NAME to
System.mapLibraryName("ps5spvc") before original Spvc initializes. The original
default is spirv-cross;no Java overlay/game JAR change is required. Matching
OpenAL source/relink materials reproduce the accepted native ELF;original JARs
are omitted publicly. Continue outside frozen folders;server endurance deferred.

User branding update2026-10-25:the app name is ProsperoCraft. Use the supplied
PNG preserved in assets/branding,with its512RGBA nearest-neighbour icon,for
future development client/server packaging via tools/apply_branding.py. Do not
regenerate the artwork,rename repositories or change PPSA99874/content identity.
Preserve frozen snapshots/releases and already-built038. Keep future candidate
versions distinct as usual. Catalog rename/description update is PR737;its
reservation icon_url remains null per catalog rules until downloadable release.

Client039 failed check4 in original VulkanInstance validation-layer enumeration,
VK_ERROR_LAYER_NOT_PRESENT;the previous SDL/LWJGL pointer rejection was absent.
Exact039package/symbols/status are preserved locally;public failure record hashes
full saved exceptions.log (session/startup/run ID retrieval unavailable).
Client040 development loader reports truthful zero installed instance layers,
rejects named-layer extensions/enabled-layer creation,and delegates actual GPU
commands to resident ICD. Host MoltenVK/UBSan regressions pass;PS5 instance,
window/menu/gameplay remain pending. Original game JARs remain intact;do not
claim validation layers,menu success or a new passing milestone from host checks.

User artwork selection2026-10-25 supersedes the initial no-regeneration preference:
use the approved generated ProsperoCraft-icon-v3-source.png (complete dark-green
P/C outlines) in the next development build after040. Active icon0.png is its
512RGBA packaging resize;branding.json pins both checksums. Keep original/user
artwork and v2/v3 masters,frozen snapshots and already-built040 intact. Existing
client/server apply_branding.py hooks automatically consume the new icon.

Client040 original Main selected PS5 RADV Vulkan and logged SDL window creation,
then failed4MiB ByteBufferBuilder off-heap malloc. Exact040package/symbols/status
preserved;full exceptions/startup reports hashed in public failure record with
matching run ID. Client041 scopes only MemoryAccessJNI/LibCStdlib native objects
to existing clientgpu title-heap malloc/calloc/realloc/free/alignment family,with
audit and pre-Main checked large-buffer allocation/cleanup. No game JAR or JVM
global allocator changes. Approved v3 icon included. PS5 allocation/preflight,
render buffers/menu/gameplay and memory/performance remain pending;no new pass.

Client041 progressed through resource reload/renderFrame after scoped allocation
repair,then repeatedly failed4K swapchain creation;human reported crash/reopened.
Saved VM trace ends in shader compilation without captured fatal fault/abort.
Exact041package/symbols/status preserved. Client042 unifies SDL display and Vulkan
surface selection with actual enumerated1080p <=60Hz preference,plane/capability
checks and logging. Driver offers1080p/1440p/4K;never claim invented720p scanout.
PS5 swapchain/menu and later crash remain unresolved;host inventory regression
is synthetic policy validation,not GPU acceptance. Preserve frozen snapshots.

Client042 selected matching real1080p59.94 SDL/Vulkan surface but continued
VK_ERROR_INITIALIZATION_FAILED swapchain errors and human-reported crash.
Full native VM trace ends DONE:Metadata zeroing with no captured fatal signal.
Exact042package/symbols/status preserved. Client043 is explicitly diagnostic:
bounded64-event native Mesa WSI checkpoints identify initialization guards,
registration,image layout and host import errors without changing results or
parameters. A private RADV archive replaces one native WSI object;original pinned
source/archive unchanged. Original game JARs and frozen passes stay intact.
Driver rejection/crash/menu remain unresolved pending next PS5 diagnostic run.

Client043 WSI diagnostics identify negative VideoOut open before framebuffer
registration/image allocation;extent/count/import callback are valid. Native raw
OS error not captured;VM trace has no fatal signal. Exact043package/symbols/status
preserved. Client044 adds0002 native WSI patch:caches nonnegative handles only,
one delayed retry after2s before any buffers/current swapchain,max2OS attempts,
retains success and logs raw OS errors. Permanent refusal remains failure.
Private native archive only;original game JARs/Mesa archive and frozen passes
unchanged. Host exact-function tests use synthetic OS responses/clock. Initial
refusal/crash/menu/presentation need actual PS5 validation;server2H deferred.

When incrementing build versions,replace complete version/label tokens rather
than bare digits;historical SHA-256 strings must remain exact and unchanged.

Prospero Store status verified2026-10-25:rename PR737 is MERGED;upstream
apps/PPSA99874.json now says ProsperoCraft with updated client/server/native-Java
description. Reservation release/icon/source fields remain null. Do not duplicate
the rename PR or assume a downloadable listing/live website update. Detailed
continuation prompt:docs/handoff-prosperocraft-client044.md.

Client044 retrieved session client-01.000.044-1792941998-299539155 records two
actual sceVideoOutOpen results0x80020023 (kernel EAGAIN/resource unavailable).
Retry executed but registration/images/menu remain blocked;no fatal signal/VM
abort captured. Do not infer the unavailable resource or a crash stack. Exact044
package/symbols/status/evidence preserved. Client045 adds read-only configured/
available flexible memory and largest direct range with raw query statuses before/
after the same bounded open calls;no extra output,allocation,heap/resolution change.
Original game JARs/private source boundary/frozen passes preserved. Actual PS5
resources/open/presentation/menu and later crash remain pending;server2H deferred.
See docs/client-startup-045.md and matching044failure evidence. The044handoff
is historical;current candidate045 supersedes its version/status directions.

Client045 reports confirm both opens0x80020023 with324MiB flexible available and
>11.5GiB largest direct ranges. Earlier ordinary thread creates fail EAGAIN/ENOMEM
and succeed with direct stacks;libc/service pressure is a hypothesis,not confirmed
VideoOut cause. Exact045 artifacts/evidence retained.046 initializes the same WSI
output after GPU provider constructors/before original Main,under existing lock/
once;later swapchain reuses retained handle including0. No separate preflight
output or ownership handoff. Negative result fails JNI_OnLoad before Main;no fake
success. Startup-only macro leaves other build modes unchanged. PS5 early open/
registration/presentation/menu/later exit remain pending;server2H deferred.
Current046 supersedes historical044/045candidate instructions.

Client046 human reports visible original Mojang loading screen then crash/reopen.
Matching run client-01.000.046-1792944398-207378114 confirms early open0x4e100100,
prepare0 and3successful WSI image imports. Preserve this working same-owner early
initialization. No menu/gameplay/ALL PASS or new milestone;exact046retained.
No fatal signal/VM abort captured.047 holds an outer existing fault-recorder
reference across original startup JNI call,including gaps between shader compiles.
Existing recorder implementation/delegation unchanged;historical SHADERC FAULT
prefix no longer implies compiler origin and signals can be JVM-handled normally.
Requires4handlers/descriptor;RAII restores on returns. PS5 capture/crash cause/
menu/stability pending;server2H deferred. Current047supersedes earlier candidates.

Client047 reports show outer fault recorder4 and retained successful VideoOut/
3image imports,but no signal/VM abort/fatal report. Crash cause unknown;last shader
return is not crash-location evidence. Exact047retained.048 adds real native
stderr capture before constructors and fixed current/previous download endpoints.
Native driver submission/timeout diagnostics previously went only to stderr;
no such GPU failure is established yet. Preserve early owner/outer recorder.
Reopen without X after failure;collect native-stderr.log with VM/build/session/
exceptions/abort/fatal reports. PS5 descriptor capture/crash resolution/menu pending;
server2H deferred. Runtime helper/server/collector changes publish separately.
Current048supersedes earlier candidate instructions.

Client048 black screen was diagnostic setup FAIL check1/code1 before JVM;matching
run client-01.000.048-1792946164-359674616/native header only. PS5 title dup2EPERM
is documented by inspected SDK source. Do not treat stale VM traces as048. Exact
048retained.049uses open/fdopen/unbuffered FILE then stderr pointer replacement,
no dup2/no pipe/thread;raw descriptor2 remains unchanged/not captured. Optional
capture failure now logs/notifies and continues startup. Preserve early WSI owner/
outer recorder/original artifacts. PS5 FILE capture/loading/crash/menu pending;
server2H deferred. Current049supersedes earlier candidate instructions.

Client049 matching run client-01.000.049-1792947461-290571136 confirms real native
FILE capture and1080p framebuffers registered set0/buffers0-4.048setup regression
passed;no GPU submit/timeout diagnostic or signal/VM abort captured.046/047/049
have390compile entries/returns each,last compile is not a known crash location.
Exact049retained.050adds first8present/fence/flip checkpoints plus raw failures,
within existing64event cap,in private WSI object. Behavior/results unchanged,
including existing failed-fence continuation (logged,not repaired/claimed success).
No new output/thread/timeout/resolution/heap change. PS5 frame progression/crash/
menu/stability pending;server2H deferred. Current050supersedes earlier candidates.

Latest continuation handoff:docs/handoff-prosperocraft-client051.md. It contains
current051package/source/checksum,latest retrieved051snapshots,all prior fixes,
Safari retrieval/publication boundaries and eventual release/store requirements.
050/044handoffs are historical. ProsperoCraft PR737 was verified MERGED;reservation
fields were null in that verified state. Do not infer a downloadable client listing.

Client050 human reports Mojang loading then crash;matching run
client-01.000.050-1792949111-939372034 confirms8successful fence waits/8accepted
native flips and390shader entries/returns,no captured signal/VM abort/driver error.
Cause remains unknown,not the last compile. Exact050package/symbols/status retained.
051 adds optional bounded startup Java thread-stack/heap snapshots:90samples/1s,
32printed threads/24frames,Main/resource workers first;one daemon requesting256KiB.
Setup/sampler failure disables diagnostics and continues original Main. Safepoints,
allocation and timing effects require PS5 validation. No game-JAR changes/menu pass/
new milestone. Current051 supersedes050 candidate instructions;see
docs/client-startup-051.md and050 validation record. Server2H remains deferred.

051retrieved run client-01.000.051-1792950523-73596505 confirms90complete snapshots
8-89147ms and normal observer completion. Samples63-90render waits in pipeline
future join while resource worker has changing RUNNABLE texture/font/model stacks.
This is not a proven deadlock/crash cause.390shader entries/returns,first8fences/
flips succeed;no captured fatal signal/VM abort/driver error/OOM. Allocation reserve
failures/null metadata attempts require retry/fallback context. No explicit human051
final visual outcome supplied;050Mojang/crash remains a separate report. No binary
changed for documentation handoff;051console/menu/crash mechanism remain unresolved.
See docs/validation/client051-startup-observations-2026-10-25.json and the current
051handoff before work. Preserve051exact artifacts before any changed052candidate.

Current continuation update:docs/handoff-prosperocraft-client053.md supersedes052
candidate instructions. Human confirms052Mojang loading near completion then crash
before menu fade around1½minutes. Matching reports end after91complete snapshots,
last94195ms,with render joining pipeline future and worker baking resource models.
No fatal context/OOM/driver error captured;cause unknown. Exact052retained before053.
053adds consumer native resource/handler-ownership observations around Java samples,
first120at1s then60at5s;no handler replacement,no speculative game/runtime/heap/GPU
repair. Console validation remains pending. Server2H stays deferred. Read prior051
complete release/store/provisioning/OpenAL requirements before any client release.

Current054update supersedes053candidate directions:see docs/handoff-prosperocraft-client054.md.
053crash/reopen reports contain98snapshots through97185ms and native pairs through
97186ms;pipeline wait resolves,Main entersMinecraft.run and language-resource apply.
No permanent deadlock/menu/crash cause is established. Four recorder handlers match,
flexible availability remains>=324MiB;raw RSS units/process policy unknown.054adds
read-only process limits/direct availability and dense transition sampling;no
limit/heap/graphics/game repair claimed. Exact053retained;054console pending.

Latest054retrieval/handoff update:docs/handoff-prosperocraft-client054.md is now a
complete self-contained continuation guide,with docs/fresh-context-prompt-client054.md.
054run client-01.000.054-1792954563-796299341 confirms120snapshots through96992ms,
120native phase pairs96993ms;pipeline join resolves,Main applies language resources,
worker idle. AS/RSSreported infinite,data32GiB,flexible>=324MiB,largest direct range
>=12124160000bytes;RSSunits unverified,no1GiBlimit/exhaustion diagnosis. No fatal
context/OOM/driver error. No explicit054human final outcome/timing supplied. This
handoff turn changes docs/evidence only,054binary unchanged. Preserve exact054before
changed055;read complete saved logs and establish actual outcome before assumptions.

## Client product goal clarified on2026-10-26

The user wants a polished,playable Minecraft Java client on native Java25forPS5,
including responsive controls,smooth rendering,working audio,world gameplay,
saving/reloading and stability. A working menu is an intermediate debugging
checkpoint,not the final product or sufficient full-client release acceptance.
Continue beyond startup while keeping exact-build console scope/results honest.

## User menu confirmation and GitHub release authorization — 2026-10-26

The user confirms the visible Minecraft Java menu on exact client01.000.062
and explicitly requests a polished GitHub release with no Prospero Store work.
Tested implementation f3349a1fb90a9304d7aa808b339bd37738607d14; full-local ZIP
26f31cc26bc960d3c7e35205c0280e8b83bc6e475a17b8383c778583cf952b88. Preserve
these accepted bytes/symbols/source. This accepts visible menu startup only,
not formal ALL PASS, menu interaction, world gameplay, speaker audio, save/reload,
full teardown or stability. Publish a full release accurately qualified to that
scope; retain server fallbacks. No Store/catalog changes are authorized here.
Do not rebuild or change the accepted binary under the same version. Public
app-only artifacts exclude original JARs AND asset objects; provision both with
verified publisher pins. Include exact startup OpenAL source/relink/shim inputs.

## User control and menu performance direction — 2026-10-26

After the062menu release, the user requests temporary functional controls and a
menu-lag fix. The user prefers upstream Controlify for the eventual modded client,
on an exactly compatible Fabric/NeoForge build. Do not treat desktop mod support
as PS5 acceptance. Temporary063SDL keyboard/mouse translation is opt-in through
PS5_TEMPORARY_CONTROLS and must hand off to real gamepad/mod support without double
input. Preserve the raw SDL joystick path. No game JAR rewrites/replacement classes.
The observed gradual idle slowdown has a supported vanilla AFK policy alternative;
GC stutter remains distinct. Preserve accepted062release bytes/tag and continue
candidates at063or later;no Store updates or new release without separate request.

## First world and performance work — 2026-10-26

The user confirms065world loads and punching works,but movement fails and severe
lag/verylongloading make it unplayable. They request a GitHub release of this exact
checkpoint and then a speed candidate. Publish accurately scoped fullworld-entry
release;do notinferformalALLPASS,playableperformance,movement,save/reload,audio or
stability. Preserve065accepted bytes/symbols/source/tag. No Store work.
Proceed with performance investigation and a new066candidate;guardedC1 and SDL
relative-input repair are in scope. Fullhardwareutilization is the goal,not a
claim justified by enabling flags. No gameJAR transformations/replacementclasses.

## Playable066release and audio work — 2026-10-26

The user confirms066is blazinglyfast,worldplayable,startuproughly30seconds,and
requests release then sound before further instructions. Publish exact066asfull
GitHubplayableworldrelease,accuratelyqualified humanresult—notFPS/ALLPASS/save/
audio/enduranceguarantee. Preserve exactZIP/symbols/source/tag. NoStorework.
Next067isrealPS5AudioOut/OpenALspeakerbackendplusbacked-upunmutingoflegacy
launcherdefaults. Keep gameJARs/assetsintact,working066fallback andspeedsettings.
No further performance-tuning scope beyond maintaining working C1 is requested.

## Audio confirmation and intermittent freezes — 2026-10-26

The user confirms067sound works beautifully on PS5 and now authorizes investigating
and fixing intermittent freezes. Preserve exact067package/symbols as the working
audio fallback. Current-run GC evidence confirms full pauses; do not assume every
freeze is GC or claim a latency pass from host tests. Continue at068or later,
retain working audio/input/C1 and untouched game files. No new release or Store
publication requested. Keep build history in CHANGELOG.md; README stays concise.

068follow-up:human reports escalating stutters then complete freeze. Same-run
reports confirm Java heap OOM and chunk-save failure, repeated499M->499MfullGC.
Preserve068as failed GC candidate; do not claim save success.069requests768MiB
heap/NewRatio3 using separate runtime0119bounded ceiling; console reservation/
headroom/sufficiency/stability pending. Current continuation:docs/handoff-prosperocraft-client069.md.

069follow-up:768MiBstartup works but stutters recur; retrieved console showsview16/
simulation12and continued fullGC/live-setgrowth.070uses backed-up once-only vanilla
options caps6/5, preserving lower values/later choices; heap/runtime unchanged.
Do not infer a stable live set or GCpass from hostchecks. Current070handoff applies.

Userclarification:target is smooth highsettings, not quality cuts as finalfix.
070was diagnostic only; userdidnoteditsettings, butreportsstill16/12andstutters.
071disablesactive070cap,preservesexistingconfiguration,andusesboundedretainedheap
diagnostics/runtime0120. No claim of a lower-distancecomparison orperformancefix.
Currentcontinuation docs/handoff-prosperocraft-client071.md.

071retentionfollow-up:3PS5histogramsconfirmgrowingchunk/longarraycategories,stable
modelquadcount;notleakproof.072preservesqualityandtestsG1/1536MiB/2GCworkers+
1concurrentworker/processorhint4,withoutdiagnostichistograms. Runtime0121bounded
heapceiling;actualPS5G1startup/nativeheadroom/pausespending. Current072handoff.

072follow-up:humanreportsverysmallstuttersbutnosound. PartialG1logs:92pauses,
median20.8335ms/max49.747ms/nofullGC;qualifiedimprovement,notformalpass. Audioinit
0x80260002failsbeforeportopen.073boundedBusyactual-portprobe/retry/AlreadyInit
handlingonly;preserveG1/heap/quality. AudiblePS5recoverypending. Current073handoff.

073audiofixfailed(all20Busy/NotInit),smallstuttersannoying.074testsAudioOutinit
onthenativestartupthreadbeforeVM/heap,validatesrealearlyresultandrealport;no
forcedservicereset. G1goal8/workers4anddefaultstackobserveroff;quality/heapretained.
ActualPS5audibility/initorder/GCworkers/latency pending. Current074handoff.

074humanconfirmation2026-10-26:verygoodsoundandbuttersmoothgameplay. Preserveexact
074package/symbols/testedsource72eca7fccf79c81c2cb7a057afdffcad51207b90; no rebuild
ofacceptedbytes. Subjectiveaudio/smoothnessacceptanceonly,nomeasuredFPS/save/
endurance/formalALLPASS. No newrelease or furtherimplementationrequested.

## Native launcher and MSA direction — 2026-10-26

The user requests a beautiful launcher with Microsoft account login and supplied
public application ID f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3. Candidate075 adds
native UI, device-code authentication and original Main session arguments. No
client secret or token persistence. One Vanilla26.3 instance; settings informational.
Host and target checks do not establish live authentication or display handoff.
Continue from docs/handoff-prosperocraft-client075.md. Preserve accepted074 bytes
and performance/audio/settings. No new release or Store publication requested.

076branding update: user supplies Downloads/ProsperoCraft2.png for packaged app
icon and ProsperoCraftTransparent.png for native launcher corner. Source copies
and hashes belong in assets/branding; generated bitmap from prepare_launcher_branding.py.
Keep075exact package/symbols preserved during MSA tests. Candidate076 changes
branding/version only; inherited live-login/display handoff checks remain pending.
Current guide docs/client-launcher-076.md. No release requested.

## Launcher startup separation — 2026-10-26

User reports GUI never loads (075/076exact version unspecified) and requires
separation from MC graphics.077native UI starts/presents before VM creation,
with account/model work on the JVM startup thread and mailbox-only UI exchange.
Defer artifact inventory/game native loads/C1/Main until Play. Preserve early
AudioOut init on original startup thread. See docs/handoff-prosperocraft-client077.md.
Host threading/JNI-table/order tests do not establish PS5 GUI/liveMSA/handoff.
Keep raw auth secrets out of diagnostics; preserve074/075/076packages. No release.

## Authentication rejection follow-through — 2026-10-26

077user passes public-client setup/code approval but returns to Not signed in
with generic REGISTRATION text. No full MSA/MC acceptance. Exact later endpoint
is unresolved; no proven Minecraft403.078preserves HTTP401bodies with bounded
bufferedPOSTs and adds endpoint/status UI errors and allowlisted diagnostics.
Never log raw responses, token/code values, headers or exception/cause text.
Read docs/handoff-prosperocraft-client078.md. Preserve077and earlier packages.
Use actual078PS5_AUTH logs to identify the failing stage before service changes.
No new release/Store publication or auth/entitlement bypass.

078follow-up: human reports [MINECRAFT HTTP403] after Microsoft approval. Upstream
Microsoft/Xbox/XSTS reached MC login, but entitlement/profile/fullgame auth remain
unvalidated. App allowlist rejection is a leading explanation, not a captured raw
server reason. Official https://aka.ms/mce-reviewappid form verified; request draft
at docs/appid-review-request.md. No submission or legal attestation performed.
Do not change to another app ID or bypass checks. Preserve exact078package bytes;
source docs only. Await human application review and/or safe current-run diagnostics.

Repository renamed by the user to https://github.com/mateo-cogeanu/ProsperoCraft.
Use that canonical GitHub remote and URL in current documentation. The local
checkout directory may remain .tools/github-publish/ps5-minecraft-java; do not
rename local paths or modify frozen validation snapshots for this URL update.

## Native library/instance redesign — 2026-10-26

User requests native top AddInstance/Settings/Account bar (L1/R1), instance grid,
large-icon detail/Play/settings, rename/icon editing, resolution and fluid UI;
selected26.xdemo must download on console, not be bundled.079implements the native
GUI/store/controller/download/loader foundation. Read docs/handoff-prosperocraft-client079.md.
No preset instances/gameJARs/assets in package. Isolated UUID game directories,
shared verified original cache, demo-only launch; account review still pending.
26.1/26.2use GLFW and need an unimplemented native path despite Java25; do not
claim playable all26.xor replace older selected game with26.3.26.3is the native
baseline. New downloader/loader/GUI need exact079PS5tests. Preserve078/074packages
and old world data. No release/Store update. Consumer-only source ownership.

080storagefollow-up: human079ENOSPCat212MBdespite382GBconsolefree. Source param
stilldownloadDataSize256;080requests4096MiBsame title and retains /download0/
ProsperoCraft. /data migration idea discarded after checking native template
sandbox docs; no migration/elevation/backingimage edits/cleanup shipped. Actual
mounted capacity and existing-volume expansion remain unverified. Completeparam
update+loaderrefresh/relaunch thenRepairDownloadpast212MBneedsPS5validation.
Capacity0fromunsupportedJavaqueriesisunknown,neverphysicalfree0. Read
 docs/handoff-prosperocraft-client080.md. Preserve079/074bytes; no release.

081userrequestspropertemporarycontrols,visiblejoystickcursor,quietroutine startup,
Instancesheading/fullversion,explicitpending-versionlaunchblockandsavedapproval/
roadmapnotice. See docs/client-controls-081.md and081handoff. Onlyexact26.3SDLdemo
allowed;nootherAppID/fullaccountbypass. Controller/cursor/textpickerhostfixtures
are notPS5pass. Preserve080bytesand074fallback;existingdataand4096MiBunchanged.
Runtimequietreadynotificationpublishedseparately;nofrozenmilestonereplacement.

082userrequestscompacthorizontalwelcomecheckbox,universalnativesticknavigation,
boundedfocus/pressanimationandrealgameQuitreturn. Read docs/client-launcher-082.md
and082handoff. Verifiedcleanreturnusescurrent-sessionlogmarker/stopping+original
stoppedsingleton+SDLquitthenOSLoadExecselfreplacementbeforefreshlibrary/JVM/
display;neverreinvokeMaininoldVMoropenCPUVideoOutunderretainedWSI. PS5LoadExec/
mount/devicecleanup/quit-relaunchremainpending;hostfixturesareNOTconsoleproof.
Exact081package/symbolspreserved;074andfrozenmilestonesunchanged. OriginalJARs,
4096MiBdataanddemo26.3SDLguardretained. NoAppIDbypass/release/Storeupdate.

User2026-10-26explicitlyrequestsProsperoStorepublicationofexact082("thisistheone").
Publish01.000.082GitHubreleasewithunchangedlauncherZIP,noMinecraftgamefiles,
matchingOpenALsource/relinkkitandchecksums;convertexistingPPSA99874reservation.
Thisoverridesearlierno-release/no-StorescopebutdoesnotestablishformalALLPASS.
Keep082quit/relaunch/consoleinput/audio/regressioncheckspendingandpreserveold
packages. Rootsce_sys/param.jsonmirrorsthebrandedpublishedmanifestforcatalog
updatechecks;keepitmatchedtothenextpublishedclient,notserverorfrozenversions.

Human082confirmation2026-10-26:"yes it all works. all the fixes you added."
Client_Launcher_Lifecycle freezes exact01.000.082 implementationa7b70ea, package
ab49cad8977736be2be72230743232a270dba9bd17fa70a66b64a93c48230820 and matching
symbols. HumanALLPASSscopedtofourrequested082fixareas,includingQuit/library/
relaunch;notexactcyclecount,independentlogs/handlecounts,FPSorendurance.
Preservefrozenfolderandcompiledbytes;continuedrootclientdevelopmentonly.
Addconsoleconfirmationassetstoexisting01.000.082releasewithoutreplacingold
assets. PR811updatedfromorigin/main;write-accessmaintainerapprovalstillrequired.

Store2026-10-26:atuserrequestclosedPR811andresubmittedidenticallistingasPR814
https://github.com/darkxex/ps5-homebrew-catalog/pull/814 onfreshbranch
codex/prosperocraft-082-resubmit fromupstream8566a5f. Track814asactive;no
releaseasset/package/sourceimplementationchanged. Resubmissiondoesnotitself
repairthecatalognewest-releaseorderinglogicorremovereviewrequirements.

User2026-10-26requestsGPLv3andclearforkcredit. Projectoriginalcode/buildscripts
areGPL-3.0-or-later,matchingexistingheaders. RootLICENSEisverbatimGPLv3;NOTICE
containsmateo-cogeanu—ProsperoCraftcopyrightandupstreamcredit. Distributedforks
mustpreserveapplicablenoticesandGPLrights;donotaddadvertising/splash/noncommercial
restrictionsoroverwriteupstreamlicenses. UpdateactiveStorePR814licensefield.
Preservefrozen082bytes/tag/snapshots;publishlicense/noticeasadditivereleaseassets.

User2026-10-26reportsStore082X/R2menuclicksmisalignedandrequestsfixed1080p.
Development083forces1920x1080launch/default/migrationandSDLlogicalwindow/resize/
enumerateddisplaymode;lockedSettingsrow. No gameJARpatchorinputadapterrewrite.
Read docs/client-resolution-083.md and083handoff. Exact083consolealignment/
demoworld/audio/quit-relaunchpending;hosttestsarenotPS5pass. Preserve082ZIP/tag/
frozenClient_Launcher_Lifecycleandhistoricalacceptance;newreportaddsresolution
limitation. PR814merged,currentStorerelease082;rootmanifestmirrorsthatrelease
untilnewpublication,client/startupmanifest083. Publishdevelopmentsource.

UserexplicitlyrequestsProsperoStore083releaseaftercandidatebuild. Publish
exact8fcbdc8cb9cc8065aa0eaac26457a834fffb15098725e987df1d33257a76444epackage
as01.000.083withfreshmatchingOpenALsource/relinkkit,checksumsandhonestpending
PS5click/demo-world/audio/lifecyclechecks. NonewALLPASS/frozenmilestone. Update
existingStorelisting083andGPL-3.0-or-later;preserveall082assets/source. Root
sce_sys/param.jsonnowmirrorsthepublished083brandedmanifest.

083publication:GitHub01.000.083public,exact8fcbdc8cb9cc8065aa0eaac26457a834fffb15098725e987df1d33257a76444e
ZIPwithmatchingOpenALsource/relinkandverifieddownloads. ActiveStoreupdatePR819
https://github.com/darkxex/ps5-homebrew-catalog/pull/819 . 814remainsmerged082
history. Track819for083deployment;physical083clicks/demo-world/lifecycle/audio
stillpending. DonotclaimStoreavailableuntilmerge/deployconfirmed.

## Verified personal offline account test — 2026-10-27

User explicitly requests using their locally owned account for offline launch
("lets use it!"). This overrides earlier demo-only scope for the verified offline
path. Candidate084 adds a separate Play Offline action; original demo and pending
appID/device-code flow remain. Read docs/client-offline-084.md. Export helper
checks current Minecraft token + Java entitlement + matching profile directly
with Minecraft Services, then signs a seven-day name/UUID/timestamp-only record.
No login tokens or private signing key go to PS5/GitHub/packages. Keep the local
RSA signing key ignored; only public key ships. No unverified profile/UUID override,
borrowed appID, online bypass or game-JAR edits. Full offline actual084PS5/world/
RSA/menu/controls/audio/lifecycle tests pending. Preserve published083and082,
frozen milestones and existing worlds. No new Store release is authorized here.

Human084feedback2026-10-27: "just reopned the app and play offline is there", then
"perfect it works really well!" after offline-play instructions. Record a scoped
PS5 offline profile/menu and launch/play success for exact candidate084, not formal
ALL PASS, measuredFPS, explicit save/reload, renewal/expiry or endurance. Preserve
a1e6774ba8bebe1faac0d9c36c4ff7cc17da1cf5622c2f9519bffc50eec57822 package and
2063966a99e5930773727b6bfd4a19523eb7a48792ecf326e311c772d507badf symbols in
local dist/candidates/ProsperoCraft-01.000.084. No new frozen milestone or public
release requested by this feedback. AppID approval remains pending.

## Demo / Offline branch split and shared instance deletion — 2026-10-27

User defines public Demo branch (ProsperoStore until appID approval) and personal
Offline branch (verified offline play, future mods/extra features). Shared fixes
must reach both. Main is shared with Demo default; codex/demo and codex/offline
are named Git branches. Only the Offline branch default channel pin differs at
this split. Future Offline experiments must not enter Demo implicitly.
Read docs/client-channels-delete-085.md. Startup packaging accepts explicit
--launcher-channel demo|offline (distinct from cached-dependency --offline).
085embeds channel identity and shows it in the launcher. Demo ignores personal
proofs and excludes the offline public key; no runtime override enables Offline.
Both variants use same title/data and replace each other, not side-by-side apps.

Both085channels add Instance Settings/Delete Instance with Cancel-first prompt,
complete instance/world/options archival to app-local Trash and Triangle Undo
from the grid, including restart. No shared cache/account deletion or automatic
purge. Roll back save failures/reconcile interrupted folder moves; reject symlinks
and overwrite conflicts. Preserve084candidate/package/human offline feedback,
published083/082and frozen milestones. Exact085PS5delete/undo/save/reload/input/
audio/lifecycle remain pending. Do not publish a new Store release from these
host checks alone; current request adds the feature to both development channels.

Store status checked2026-10-27:catalogPR819 merged2026-10-26T20:34:21Z for083.
085channel/delete candidates do not change that existing listing/release. Actual
Store refresh/deployment timing is external; no085Store publication is claimed.

## Shared top-bar / debug CPU fixes — 2026-10-27

User requests centered top-bar labels and CPU identity instead of unknown in F3.
086shared in main and both channel branches. Read docs/client-shared-fixes-086.md.
Consumer native UI centers actual glyph ink bounds in existing boxes. CPU uses a
pinned OSHI6.9.0dependency source overlay plus startup JNI CPUID/kernel hw.ncpu
snapshot. No game class/JAR edits or reflection writes; original debug entry calls
normal OSHI API. Unsupported metrics stay unsupported, no fake clock/load/model.
Counts do not change JVM ActiveProcessorCount4. Non-PS5 OSHI factories retained.
Package full OSHI port and MIT/source notices; original cached OSHI/game JARs intact.
Keep085/084candidates and published083/082/frozen milestones. Both086physicalPS5
centering/CPUname/GPU/regression/delete/undo/lifecycle tests pending. Publish shared
source to main,codex/demo,codex/offline; retain separate labeled candidate ZIPs.
Do not update ProsperoStore/release automatically from host tests.

## Vulkan toolkit launcher migration — 2026-10-27

Client087 adopts the actual PS5_VKHomebrewUI Vulkan backend at pinned revision
2188642afbcc8d84d36149124f3d9e39dc1b1a05. Read docs/client-toolkit-087.md and its
validation record. Consumer adapter/sources remain here; reusable checked
Canvas::blit_rgba lives in the runtime repository. Keep the Java model, signed
Offline policy, original game JARs, OSHI provider, data paths and title identity.
Launcher owns a private offscreen RADV device and the existing single native
VideoOut presenter; no launcher SDL/WSI/audio backend. Complete frame fences,
GPU/display cleanup and UI join gate game launch. Graphics constructors run
once before first use; toolkit glyph constructor is explicitly staged. Keep
clean original-Main return plus LoadExec; never re-enter the old process.
Readback/tiled upload cost and pre-JVM graphics compatibility require actual
087PS5validation. Host Vulkan fixtures and packages do not establish console
startup/performance/handoff/gameplay/audio/lifecycle/Delete/Undo success. Preserve
083/082public artifacts,084/085/086candidates and frozen milestones. Shared087
source reaches main,codex/demo,codex/offline; no Store/release asset replacement.

## Toolkit visual polish — 2026-10-27

User explicitly wants the existing layout with Aurora Shelf-style visual polish,
not a shelf-layout replacement.088 uses real animated toolkit backgrounds/glass,
GridView/Card entrances/focus/lift/glow, Dialog open/close, Painter switches and
ProgressBar motion. Read docs/client-motion-088.md. Settings Square cycles all10
pinned backdrop modes; additive settings.background persists and defaults to2
(Aurora). Previously unused mailbox75/76 carry validated mode/name; total80fields
and JNI thread ownership stay unchanged. Reduced Motion freezes/snap effects.
Keep shared Demo/Offline policy, original game/OSHI, data paths and LoadExec gate.
No toolkit audio backend. Continuous30Hz redraw request plus blur/readback needs
actual088PS5performance/startup/handoff/gameplay/lifecycle/Delete/Undo validation;
host motion clips are fixed-clock Vulkan readbacks, not consoleFPS evidence.
Preserve087and earlier candidates, public083/082and frozen milestones. Publish
sharedsource to main,codex/demo,codex/offline; no automatic Store/release update.

## Launcher vibration — 2026-10-27

User requests controller vibration inside the launcher.089 adds bounded semantic
focus/confirm/back/error/completion cues and a saved Settings Triangle vibration
preference (defaultON). Read docs/client-vibration-089.md. Mailbox77/78/79 carry
sequence/cue/preference within the existing80fields; no JNI on the motor worker.
A dedicated native worker owns motor writes and deadlines on the UI controller
handle; stop/join/zero attempt precedes PadClose and game handoff. Disconnect,
interception, generation change, stale input and opt-out cancel output; no stale
replay or idle/progress buzz. Keep API failure nonfatal and gameplay audio/input/
profile/world/lifecycle policy unchanged. Actual089PS5feel/strength/reconnect/
residual-rumble plus088performance/regression checks remain pending. Preserve
088and earlier packages/symbols/frozen milestones. Sharedsource goes to main,
codex/demo,codex/offline; no automatic release or ProsperoStore update.


## Temporary authenticated game branch — 2026-10-27

User explicitly requests a Git branch named Temp_gametest replacing codex/offline,
carrying the Mojang-ID login experiment, fixing instance deletion and enabling
full-game downloads/play. This supersedes the Offline branch-name/default rule
for this personal test line only. Publish this requested source branch; no new
ProsperoStore/GitHub release is authorized. Keep main/codex/demo on their own ID
and Demo policy. Preserve old Offline history/packages and frozen milestones.
Read docs/client-temp-gametest-090.md and the matching validation record.
User reports login works on private089 SHA256
ccf692aac72ed4eeb3d91d67bce7c2fad33e0de0ae0a634ff976d08c0c91949c;
no090 full-game/download/deletion/Undo console result is inferred. Temp builds
require --launcher-channel temp_gametest and cannot be mislabeled Demo/Offline.
Legacy Microsoft Live flow retains ownership/profile checks and memory-only tokens.
Full launch requires a valid Session and original Main receives the real profile
and access token without --demo; do not log arguments/tokens. Downloads remain
original publisher files with hashes. No bundled game payload or transformations.
Runtime patch0122 owns the directory move fix; keep Trash/Undo/recovery semantics.
090 includes the same089toolkit/haptics; actual console validation remains pending.


## Account/UI/network work — 2026-10-27

User requests Prism/MultiMC instance artwork with own transparent logo, link/QR,
persistent login, player heads/account-name button, all26.x/snapshot downloads,
dropdowns, adjustable resolution/alignment and multiplayer/LAN repair.
Continue Temp_gametest only; no Store/release publication. Read
 docs/client-account-ui-091.md and matching validation. Preserve090/089and older
candidates/frozen milestones.091uses96public mailbox fields. Refresh credentials
are app-local AES-GCM with adjacent local key and best-effort permissions;
access tokens remain memory-only. Do not claim hardware-backed storage or publish
account/key/session files. Refresh repeats ownership/profile validation. Sign out
erases saved credentials. Icons retain pinned original SVG/licenses/attribution;
Prism logo is replaced by user art. No game JAR/assets redistributed or transformed.
Snapshots default on for new libraries; all publisher26.xdownloadable; only26.3
launchable. Other versions explicitly warn. Resolution separates logical input
from actual framebuffer; physical modes depend on enumeration, not arbitrary
requested values. PS5alignment still pending. User clarifies Open to LAN fails;
server joining untested because text input is difficult. FTP2121/log service
unreachable with No route to host; current-run LAN exception unavailable. IPv4/
NIO and socket diagnostics are a candidate repair, never a confirmed PS5fix.
Host original-pinger/Netty success does not establish console hosting/discovery.


## PLAY launch follow-up and Waves — 2026-10-27

User reports091PLAY FULL GAME crash and requests PLAY, Coming soon wording and
Wavesdefault.092Temp_gametestimplements labels,mode5fallback and one-time persisted
background-default revision migration; later choices stay saved. Read
 docs/client-launch-followup-092.md and matching validation. User explicitly
requests Cyberduck computer use to retrieve logs; use it when directFTP has no
route. Browser refresh was necessary:initial mount listing was stale. Partial
retrieval succeeded despite550onotherfiles. Preserve first-retrieval local logs.
Actual091evidence passes auth/ownership/profile,UIhandoff,socketpreflight and Main
entry,then stops around Vulkan initialization; no faultPC was obtained. Do not
blame caught OSHImetricwarnings or the completed socketprobe.092repairs first-match
requested-mode selection that discarded<=60Hzranking and adds explicit legacy
refresh scope for the observed invalid_scope restoration response. Both actual
console crash recovery and refresh still require092validation; do not claim fixed.
Retain091packages/symbols and all older snapshots. No gameJARchanges or Store/release.


092startup feedback2026-10-27: user reports “MC starts now!” after receiving the
092candidate SHA256f9c1cd0a67c1229fdd08b29295acddaf2f0b79e3d0162dc199a1f8ef55e64610.
Record scoped PS5startup confirmation. Do not infer gameplay/lifecycle/refresh/
LAN/resolution tests, exact native fault cause, ALL PASS or a new frozen milestone.


093follow-up2026-10-27: user confirms092can join servers but cannot host.
Cyberduck current/previous Java reports corroborate saved refresh through profile;
raw logs stay local. Original26.3publishServer swallows IOException without logging.
Runtime0123 bounded socket diagnostics are opt-in and not a hosting repair.093
adds tiled in-game keyboard after successful presentation fence, sign-in actions,
shoulder page navigation, controller glyphs, clean welcome/footer and persistent
prelaunch controls tutorial. Preserve092and prior candidates; no new milestone,
Store or public binary release. Retest hosting and retrieve current-run trace;
console keyboard/input/resolution/overlay/lifecycle checks remain pending. See
 docs/client-keyboard-hosting-093.md and its validation for exact candidate hashes.


094work-order2026-10-27: user explicitly defers LAN hosting. Continue launcher UI:
Home left of Instances, automatic tab content focus, final plus add cards, saved
world/server favorites, permanent Yes/No deletion without Undo, essential PLAY
guide and paginated full OPTIONS guide. New deletions purge instance worlds and
pins; retain old Trash archives rather than silently deleting unrelated history.
A private deletion journal supports precommit rollback/postcommit cleanup only,
not user undo. Preserve093/older packages. Original NBT/game JARs remain unchanged;
quick-play uses original Main arguments. See docs/client-home-library-094.md and
matching validation. No ALL PASS, freeze, Store or public binary release inferred;
exact094 console UI, permanent deletion, discovery, favorites/quick-play and
lifecycle remain pending.


095steering2026-10-27 overrides Home inclusion for the current build: the user asks
not to have the Home menu for this build.095 opens Instances and exposes only
Instances/Settings/Account; preserve094source10906c5and exact package as deferred
Home work. Keep final plus card, single focus, permanent Yes/No delete and clearer
guides. No Home/favorite browsing or quick-play arguments in095. Keep existing
metadata/worlds/cache; no network/runtime changes and hosting stays deferred.
See docs/client-instances-only-095.md and matching validation. No new console pass,
freeze, Store or release publication; test095 navigation, guides, disposable-instance
deletion and lifecycle on PS5.


096steering2026-10-27: user requests normal-sized empty plus card and supplied
PS5 banner/title artwork before a later merge. User explicitly chooses banner
alone with system-rendered ProsperoCraft title. Preserve original banner bytes,
convert to pinned4KBC7DDS and package pic0/pic1; do not composite or package the
title PNG. No AI redraw. Home and hosting stay deferred. Preserve095/older exact
candidates. Source remains Temp_gametest; no main merge, Store/release upload or
console ALL PASS inferred. See docs/client-presentation-096.md and matching
validation. Actual PS5 selected/launch artwork and ordinary lifecycle pending;
shell presentation cache may need loader refresh, not catalog database edits.

## Authenticated096 release and merge — 2026-10-27

The user explicitly requests merging Temp_gametest into main and publishing its
exact dist/candidates/ProsperoCraft-Temp_gametest-01.000.096 package as a full GitHub
release and ProsperoStore update. This supersedes earlier branch-only/no-release
and Demo-default restrictions for this publication. Preserve Temp_gametest and
older Demo/server/frozen artifacts; main now carries the authenticated temp_gametest
channel honestly, without silently relabeling or rebuilding accepted bytes.
The user reports Minecraft running and login working, but no formal ALL PASS,
exact lifecycle counts, save/reload, hosting or endurance pass is inferred.
Credit mihawk-99/PS5_VKHomebrewUI for GUI and MultiMC/Prism contributors for icons
in the release description, retaining all underlying notices. Publish matching
OpenAL source/relink materials, checksums and scoped validation. No official game
JARs/assets or personal account/session/key files belong in public artifacts.

## Merged branch retirement — 2026-10-27

The user explicitly requests removing Temp_gametest and codex/demo after checking
that their history is fully contained in main. Both local and remote branch tips
passed ancestor checks against main before deletion. Continue development on main;
do not recreate those branches unless requested. Preserve historical commits,
frozen snapshots, release tags/packages and the exact096temp_gametest package label.
The user also marks controller vibration complete in the README roadmap. This
feedback does not establish unrelated console lifecycle/endurance acceptance.


## High-refresh candidate097 — 2026-10-27

User reports60/61FPS despite VSync off with120FPS target.097 enables startup
attribute3 bit0x40 and SDL fastest actual enumerated mode<=120Hz with60Hz fallback.
Pinned WSI already requires OS support/configure plus measured vblank before
advertising119.88Hz. FIFO-only presentation remains; do not claim true uncapped
VSync-off or console120FPS from host tests. Read docs/client-high-refresh-097.md
and its validation. Preserve exact096release/candidate and frozen milestones;
continue main/temp_gametest channel. No new public release/Store update requested.
Console output/F3FPS,controls/audio/quit-relaunch and60Hz fallback need validation.
Home, hosting and endurance remain deferred. Original game JARs are unchanged.


## Visible build identity — 2026-10-27

User reports097launcher footer still shows096and requests correcting this in the
next build. The native packager now passes PROSPERO_APP_VERSION from its selected
version; startup version comes from client/startup/param.json. Footer,session
identity and build note use that injected value. Host previews without the flag
say Development. Preserve exact097/096packages; this source correction awaits
the next candidate build and PS5 visible-version confirmation. Never change only
the folder name or rebuild existing accepted/published bytes under the same ID.


## 0.98 release authorization and119FPS report — 2026-10-27

User confirms097worked and reached119FPS, then explicitly requests public098
release on ProsperoStore and public-facing descriptions. Publish01.000.098with
the existing high-refresh path and automatic visible-version fix, matching
OpenAL source/relink/checksums,source and scoped validation. Preserve exact097/
096and frozen snapshots. The human119FPS report applies to exact097,not a formal
ALL PASS,endurance or independently logged frame-time result. Exact098console
regression remains pending. Mark supported120Hz ceiling removal complete while
keeping true uncapped VSync-off unimplemented/FIFO explicit. Public descriptions
must address players rather than narrating requests or private candidate history.


User asks Safari log review before098Store publication. Retrieved097native/GC
reports match current run;125safepoints over58.889s,median10.886ms/max23.792ms,
115over8.34ms;no fullGC. See docs/client-stutters-098.md and matching observation
JSON.098now removes verbose GC/safepoint/class diagnostics but retains info
summaries;no GC/heap/quality tuning. Preserve pre-review098local artifact under
before-log-review;it was never released/console accepted. Do not claim hitches
fixed. Safari connection lost before additional reports;raw logs remain local.
Release notes must disclose outstanding GC-related hitches and exact098tests.


## Explicit release/Store hold — 2026-10-27

User explicitly says do not do the Store update until they confirm the stutters
are fixed. This supersedes earlier098publication authorization. No098catalogPR
was created,pushed or submitted. GitHubuploadcompletedconcurrentlywiththehold;
098wasimmediatelyreturnedtodraftandverifieddraft. Keep098draftandStoreunchanged
until human confirms the stutter fix. Continue necessary diagnosis/repairs and
publish development source under normal ownership rules. Current098quieterlogging
is not a confirmed GC/stutterfix. Candidate hash5f2b9825c2692a7bc59a06517625727db16dc9fa0149e3c72093ec7fd24afeab.
ActualPS5comparison may require furthercandidatechanges;preserve098bytes and
097/096before newversions. See client098-publication-hold validation record.


## 098still stutters;099GCpolicy candidate — 2026-10-27

Human reports098still has essentially same short stutters. Safari current-run
098identitymatchesreports;steady120–213s301safepoints,8.257msmedian/25.769msmax,
144over8.34ms,no fullGC. Logging reduction is not an acceptedfix.099tests smaller
G1batches:4mspausegoal,G1NewSizePercent1(explicit experimental unlock),mixedGCtarget16.
Read docs/client-frame-pauses-099.md and matching098feedback/099build records.
Heap/quality/workers/C1/input/audio/120Hz/gameJARs unchanged. More frequent pauses
can worsen throughput;host results do not prove PS5improvement. Preserve098exact
bytes/draft and097/096snapshots. Do not publish binaries or Storeupdate until
human confirmsstutterfix.099is testcandidateonly;footer/GCcadence/gameplayand
lifecycle remain consolepending. Public development source still must be pushed.


## 099 partial improvement;100 remark isolation — 2026-10-27

Human reports much less stutter on099but some remains. Safari099session/GC
records agree:after60s median4.368ms,p957.522ms,max21.078ms;largesteventsG1PauseRemark.
Earlier097phase reports show class/code cleanup consuming much of remark,not
new099subphase proof.100adds only-ClassUnloadingWithConcurrentMark to099policy.
ClassUnloading remains enabled for fullGC. This can retain obsolete classes/code
and increase memory/code-cache pressure;not final long-session fix. Read
 docs/client-remark-cleanup-100.md and matching099feedback/100validation.
Preserve099exactpackage as partial-improvementfallback. No ALLPASS/newmilestone.
Keep098draft andStoreunchanged until human confirmsstutterfix.100localtestonly;
actualpause/improvement/memory/lifecycle requireconsolevalidation. Publishsource.


## Repository ownership reminder — 2026-10-27

Java runtime fixes belong in mateo-cogeanu/ps5-java25-homebrew; publish them
through tools/sync_github.py from the runtime workspace. Carry the corresponding
runtime integration, build references and validation into mateo-cogeanu/ProsperoCraft
so the Minecraft app actually receives the fix. Keep reusable runtime source in
the Java repository rather than duplicating it in the consumer. Minecraft-specific
code, launcher work, JVM launch-policy configuration and game validation belong
in ProsperoCraft. Publish the relevant changes to both repositories when a Java
fix requires consumer integration. Preserve frozen passing snapshots and the
existing release/Store hold until the user confirms the stutter fix.


## Accepted100 release authorization — 2026-10-27

Human is completely happy with100and reports it is much better,then explicitly
requests Prospero release. This lifts the prior release/Store hold for exact100.
Publish01.000.100asfullGitHubrelease and updateexistingProsperoStorelisting,
with public-facing notes,matchingOpenALsource/relink materials and checksums.
Use exact b905d80a3b21502c2c1c9672db7833cd38f3582c35835e13c087667a0a0e7f65
package without rebuilding. Preserve098draft and099/097/096/frozenmilestones.
Scope acceptance to subjective gameplay/stutter improvement,notformalALLPASS,
newfrozenmilestone,constant120FPS,endurance,orcomplete lifecycle/memory testing.
Disclose longerclass/code retention and pendinglong-session pressure checks.
Java runtime source remains inJava repo;these GC launch policies are consumer
configuration inProsperoCraft. Verifyreleaseuploads/relinks andStorePRstatus.


100publicationcomplete:fullGitHub01.000.100releasepreservesexactacceptedpackage;
all5uploads/downloads andOpenALrelinks verified. ProsperoStorePR861merged,
deployment40530933028SUCCESS,andliveAPIversion/content_version100withmatching
b905d80a3b21502c2c1c9672db7833cd38f3582c35835e13c087667a0a0e7f65verified.
098staysdraft,historicalsnapshotsintact. NoformalALLPASS/newfrozenmilestone,
constantFPS/endurance orcomplete memory/lifecycleacceptance inferred. See
 docs/validation/client100-store-publication-2026-10-27.json for evidence.


## Launcher/control/skin101 candidate — 2026-10-27

User requests Instances immediately after sign-in, snapshots off by default,
correctSignIn/SignOut visibility, cleareractive tabs,resolution dropdownonly,
cursor-onlygame menus andownedplayer skins.101 implements consumerUI/controls;
newlibrarysnapshotdefaultoff,savedprefs retained. D-pad/leftstick no longeremit
menuarrowkeys;keyboardoverlay/gameplay retained. Savedskin stackshowsEPERMfrom
Net.available;runtime0124inJava repo fixes deniedTCPavailabilityestimate. Consumer
101integrates rebuiltNet.o/libnio,officialgameJARunchanged. Read
 docs/client-launcher-controls-skins-101.md andmatchingvalidation.100releaseand
Store remainexact/unchanged;101notreleased/frozen. All101PS5UI,input,skin,reload/
lifecyclechecks pending. Publishruntimefix throughruntime sync;consumerhere.


## Accepted101 publication — 2026-10-27

Human reports all requested101functions work and explicitly requests a
ProsperoStore release. Publish exact01.000.101package
c784e08043314b02ff49cc9bb2a7c1643f558b35b1cee23ba278091a5d05e131,
without rebuilding,asfullGitHubreleaseandupdateexistingStorelisting. Retain
public-facingnotes,GUI/iconcredits,OpenALsource/relinkkitandchecksums. Acceptance
coversrequestedlauncher/account/input/skinfeatures,notmeasuredFPS/endurance or
exhaustivememory/lifecyclecoverage. Preserve100/older/frozensnapshots;098draft
unchanged. RecordJava0124skin-integrationacceptanceinJava repo andconsumerhere.
Verifyuploads/downloads,StorePRchecks/merge/deploymentandliveAPI honestly.


101publicationcomplete:fullGitHubreleasepreservesacceptedcandidatebytes;allfive
uploads/downloads andOpenALrelinks verified. ProsperoStorePR865merged,
deployment40539919062SUCCESS,andliveAPI101withmatching
c784e08043314b02ff49cc9bb2a7c1643f558b35b1cee23ba278091a5d05e131verified.
Humanreaffirmsallrequested101functionsaccepted. Java0124acceptancepublishedin
Javarepo7886291. Preserve100/olderreleases/frozensnapshotsand098draft. No new
endurance/memory/lifecyclemeasurements inferred from this acceptance.


## Fabric/Modrinth client direction — 2026-10-27

User requests Fabric now, NeoForge later; remove Forge from the current roadmap.
New-instance loader choice sits beneath Version. Instance Settings exposes Mods,
Shaders and Resource Packs, with popular downloads/search/check queues/Download
All through Modrinth. User selects Vitrail Shaders as the shader-engine test.
103 implements development integration and upstream Fabric/Knot/Mixin with intact
Mojang JARs. Keep parent LWJGL/OSHI providers shared through Fabric's supported
systemLibraries property. Host/live upstream results do not establish PS5 mod,
shader rendering, performance or lifecycle acceptance. Preserve exact101 release
and frozen passes; no Store/public binary release is requested. Read
 docs/client-fabric-modrinth-103.md and matching103build validation. Continue in
main development; the discarded PR2 CPU code/branch is not part of this change.


##103 logs and104 repairs — 2026-10-27

User confirms Fabric103 loads but reports large stutters and a shader crash.
Safari retrieves current/previous reports. Vitrail BSL noise decode fails missing
AWT/Disposer; JIT code cache32MiB approaches95percent and requests aggressive GC;
GC includes long metadata/System.gc full pauses. World saves show EMFILE.
104 integrates Java repo422e9a4's genuine optional ImageIO raster/Disposer/LCMS
subset,96MiB code cache/128MiBmetadata threshold/concurrent explicit GC,scoped
JAR resource streams,spatial launcher button navigation/secondary content buttons
and launcher-only QWERTY. In-game keyboard unchanged. See
 docs/client-stutters-shaders-controls-104.md and matching observation/build records.
Do not infer PS5 shader rendering/stutter/save repair from host tests. Keep exact
101/103 andfrozen passes; no Store/public release requested. Java source stays
in Java repo; consumer integration/policy/UI/diagnostics stay here. Raw logs local.


##105 Fabric recovery and issue3 input — 2026-10-27

User reports104Fabric fails to launch and asks mappable controls plus physical
keyboard/mouse.105 restores normal JAR URL caching after104uncached-resource
regression candidate;heavy allocation trace/no final exception do not prove root
cause or recovery.103EMFILE/world-save failures remain unresolved. Adds saved
controller-key remaps via Settings/Input and optional physical SDL HID backend
using known SceKeyboard/SceMouse system modules. US ASCII text only;native
launcher physical input and Controlify are not claimed. No105PS5hardware pass.
See docs/client-fabric-input-105.md and matching observation/build validation.
Preserve101/103/104,Java422e9a4integration and frozen milestones. NoStore/public
binary release. User wants issue3 and issue1 reply drafts in chat only,no posting;
issue1 draft states they do not ownPSVR2. Avoid em dashes in those replies.


##106 input/audio/content direction — 2026-10-27

Human retracts missing-content report;files were found.106adds read-only actual
Installed inventories,notice-style checkboxes and cached project/download PNG
icons. Preserve all existing content;do not claim a data-loss fix.105AudioOutopen
0x8026000d is intermittent;later105withControlify submits PCM,butmodcausality is
unproven.106reserves real port early,OpenALadopts once;directoptionalHIDimports/
earlyhandles/capturedlogs needPS5tests. Controlifyfails missingSDL3;consumeruses
Java explicitresidentalias SDL3=ps5sdl and waits for actuallyopenedgamepad before
fallbackhandoff. FFM/controllercompatibility is pending. Shaderspage offers
optional50/100percent shadowmapscale via supportedVitrailpacksettings withbackup,
otherqualitypreserved;noFPSclaim. See docs/client-input-audio-installed-106.md.
Keep101Store/release/frozenpasses;publishdevelopmentbothrepos,notpublicbinaries.


##107 content management — 2026-10-27

Human requests Uninstall in Installed and actual mod/shader/resource-pack icons,
notModrinthbranding.107adds selected-file uninstall confirmation/defaultCancel,
receiptcommit/rollback and noautomatic dependency cascade;worlds/settings/other
files preserved. RealModrinthicons includeWebP and4bitindexedPNGunsupportedby106.
Consumer-owned bounded thumbnailJNI uses pinnedscalarlibwebp1.6.0/STB withthe
existingemulatedTLS/providerbindings;notanImageIOdesktop/JPEGportorJavafix.
NoModrinthlogo fallback. Hostrealiconpixels/UI/uninstalltests do not establish
PS5pass. See docs/client-content-uninstall-icons-107.md. Preserve106exactcandidate,
101release/Store andfrozenpasses. Publishsourcehere;noStore/publicrelease requested.


##108 dependency candidate and keyboard feedback — 2026-10-27

User confirms keyboard works;currentSafari107native matches directkeyboardAPI
binding/handles. Do not infer mouse/Controlify/audibleaudio/lifecycleALLPASS.
RetainedpreviousFabricerror namesVitrail harddependency fabric-key-mapping-api-v1;
ModrinthoptionalAPI metadata missed thatrequirement.108reads originalFabric
manifests/nestedmodules,retainsrecursiveModrinthrequired downloads,adds verified
compatibleFabricAPIcandidate for missingAPImodules and repairsinstalledinstances
beforePlay. UpstreamFabricversionpredicates;boundednestedproviderselection;
conflicts/unmappedmissingdepsstopinlauncher,notgamebytecode. Neverrewritegame/mod
JARs,forceupgradeorremoveconflictingmods. Healthy/offlinecompleteinstancesneed
nodependencynetwork. See docs/client-auto-dependencies-108.md. Keep107/106 and
101release/frozenpasses;userwilltest108thenconfirmStorepublication. NoStore/public
binaryreleaseyet;publishconsumersourcehere,Javaunchanged42fe3a5.


##108 public release authorization — 2026-10-27

User explicitly authorizes ProsperoStore release now withmainNativeJava25Runtime/
MinecraftJavaNativePS5description,retainedcredits andnewfeaturechangelog.
Publishexact108545678bd4801cbf9e00b7209c25a89a9dfb0b3be7b645e3cd98f75633e455560,
notrebuiltbytes. This lifts prior108releasehold,notformalALLPASSor108dependency
acceptance. Recordkeyboardpositive107feedback andremainingconsolechecks honestly.
Preserve101/olderreleases/frozenpasses/098draft. IncludeexactOpenALsource/relinks,
checksums andvalidation;verifyuploads/catalogPR/deployment/liveStore. Javaunchanged.


108publicationcomplete:fullGitHubreleaseusesexact108candidate;all5assetsuploaded/
downloadedandhashverified;normal/replacementOpenALrelinksexact. StorePR872merged,
deployment40575375141SUCCESS,liveAPI108/contentVersion108/digest545678bd...and
NativeJava25Runtime/nativePS5descriptionwithGUI/iconcreditsverified. See
 docs/validation/client108-store-publication-2026-10-27.json. NoformalALLPASS/new
frozenmilestone;remainingconsoledependency/mouse/Controlify/audio/lifecycle/
save/endurancechecks stayexplicit. Preserveolderpackagesand098draft.


##109 Iris queue repair — 2026-10-28

Human reports108 empty-instance FabricAPI/Iris/Sodium queue fails with required
mod versions conflict. Exact Iris Modrinth dependency pins Sodium0.9.2 while direct
Sodium selection picks0.9.3beta.109 resolves the complete plan to exact required
pins irrespective of queue order, discarding obsolete version dependencies.
Genuine conflicting exact pins still stop before publication and name project/IDs;
existing installed mods stay protected. Host synthetic and original-JAR tests are
not PS5 Iris launch/rendering acceptance. See docs/client-iris-resolution-109.md.
Publish consumer source; no Java runtime fix. Preserve108Store/release and frozen
milestones. New109public/Store release awaits user direction after console testing.


##110 observed Iris OpenGL abort — 2026-10-28

Safari logs match109 run1793174236-428176634:Fabric loadsIris1.11.7/Sodium0.9.2/
FabricAPI;forcedVulkan renderer enters IrisSamplerLimits GL11C.glGetInteger with
noOpenGLcontext,LWJGLfatal then VMABORT in startup-tail.109downloadfix succeeded;
OSHI/storagewarnings are caught,notfatal.110consumer guard reads originalFabric
manifestIDs/nestedmodules before repair/launch and explains UninstallIris/use
Vitrail. Preservefiles;noGLimplementation/JARtransforms. Guard blocks currentIris
policy pending futurebackend support;host checks notPS5 acceptance. Publishsource,
provide110candidate;keep108Store/frozenpackages. See docs/client-iris-vulkan-110.md.


##111 explicitly authorized dependency upgrades — 2026-10-28

User now explicitly requests updating an installed older mod when another mod
requires a newer one. This overrides the earlier keep/remove-only policy within
this dependency scope.111consumer supports verified receipt-managed Fabric mod
upgrades,actual root ID and upstream newer-version comparison;prospective graph
checks exclude only replaced JARs. Installed root pins become preferences under
actual required metadata pins. Manifest-only known outdated deps/API can resolve
newer candidates;unknown/manual/modified/conflicting/downgrade cases stay protected.
Stage oldfiles privately,publish completeplan/save receipt once;precommit failure
or cancellation rolls back,postcommit cleanup may retain backups. No durable
power-loss recovery claim. Tests/docs in docs/client-dependency-updates-111.md.
Publish consumer source/provide111candidate;PS5 tests pending. Java source unchanged,
108publicStore/frozenmilestones preserved;no newStore release requested.

## Development112 native integration

The optional compression/database builder and descriptor diagnostics live in runtime commit 93b24126d915c8ee69e37b7f09871be5829a2995. Consumer namespace/group/alias references are in client/ports/distant_horizons/runtime.json. The Distant Horizons PS5 variant is a complete pinned upstream source build with an explicit platform enum, never an installed-JAR rewrite. Keep its pending PS5 rendering/save validation explicit. Audio reuse, native pad/actuator integration and partial download queue behavior are consumer-owned. See docs/client-native-input-storage-112.md. Public release/Store remain108 until separately accepted.

## Development113 save and rumble follow-through

112 console reports reproduce EMFILE for chunk reads/writes without DH installed. Do not blame DH or claim soft-limit adjustment solved it.113 integrates runtime0125 descriptor-first JNI canonicalization and native stat/accounting diagnostics from 0985f92f9c80459c8444b7383feb503e8b9beb07. Leak owner and PS5 recovery remain unresolved.113 adds actual compatible rumble probes/output and shared HD/compatible vibration-mode selection. Keep raw reports local; see docs/client-save-rumble-113.md. Public/Store108 and frozen passing packages stay preserved.

## Development114 world handle pressure

113user confirms haptics, but world validation/delete fail EMFILE. Live native inventory241regular files/261total,238tracked opens including many JARs,mostlybalanced counts. Do not claim an exact title quota or proven unbounded leak.114enables ps5.zip.maxOpenFiles=64 from runtime0126 commit ce7599d81f140aa7169c55e43558d0efe05a563b and packages its rebuilt module image. Immutable archive contract,OPEN_DELETE/non-ZipFile exclusions and reopen costs are documented in docs/client-world-handles-114.md. Actual world lifecycle/headroom/performance pending;preserve113haptics and public108Store/frozenpackages. Raw reports remain ignored.

## Development115 defaults and Unicode content

User confirms114world play/reload;matching feedback is in docs/validation/client114-console-feedback-2026-10-28.json.115adds one-time Controlify defaults for new Fabric instances using existing verified dependency installs. Preserve old instances/queues and later uninstall choices;failed setup stays pending. NeoForge default-project policy is prepared but loader/resolver remains disabled. Unicode pack filenames now share a safe single-component/180UTF8byte policy across downloads and receipts;C418contains§formatting. See docs/client-default-controlify-unicode-115.md. Runtime0126/haptics unchanged;115PS5tests pending,Store108 preserved.

## Development116 duplicate and trigger integration

User reports115works.116adds independent instance-folder duplication with marked journals/newUUID/name,publication rollback and best-effort recovery. Keep originals/account/cache intact;do not claim a durable power-loss snapshot or follow links. Instance Settings navigation/layout includes Duplicate above Done/Delete. SDL decodes original Controlify47-byte trigger packets into real120-byte native commands after OFF probe;never raw-forward arbitrary HID/calibration modes. Reset active effects on close/disconnect/interception;physical feel/coexistence pending. See docs/client-duplicate-triggers-116.md. Java runtime unchanged;public108Store/frozen snapshots preserved.


## Development117 buttons and trigger fallback

Instance Settings uses a 2x2 Mods/Shaders/Resource Packs/Duplicate grid and matching Java navigation. Common consumer controls share Settings-style glass/focus/press motion; Reduced Motion must snap without replaying stale presses. Original116 console logs show native per-zone mode4 returns0x80920001 while OFF succeeds. Retain full native modes when accepted; cache only this invalid-argument rejection and follow actual trigger travel with basic effects/hysteresis/dedup. This approximates per-zone effects; physical basic-mode acceptance and feel remain pending. Preserve haptic audio, gyro, accepted world-handle policy, runtime pins, prior candidates and Store108. See docs/client-buttons-triggers-117.md. No Java runtime source change.


##117 release authorization — 2026-10-28

User explicitly requests ProsperoStore117 now. Preserve the exact candidate ZIP52198449e6a623995e261b636a06ec847669af5321c9919a3932afbb1df804c5; no rebuild. Keep Store main description and credits byte-identical; update changelog via release notes plus required version/artifact/digest metadata. Include exact OpenAL corresponding source/relink kit, checksums and validation. This lifts the117publication hold, not formal ALL PASS: adaptive triggers/latest launcher/endurance pending; microphone explicitly deferred without code changes. Verify uploaded bytes, catalog PR/deployment and live API. Preserve108and all previous release/frozen assets.

117release published: all5downloadedassets match; normal/replacement OpenAL relinks exact. CatalogPR896 submitted with description/credits/icon unchanged. User explicitly says make thePR then do not monitor: do not poll its CI/merge/deployment/liveStore unless newly requested. Source117publication record records pending console tests, noformalALLPASS.


##117 acceptance and performance investigation — 2026-10-28

User confirms accepted Store117 reinstall works and second tester succeeds. Requested completed README ticks: Fabric/Modrinth content, SDL3Controlify, remapping. Investigate before performance changes; shadows100% is explicit, do not lower it. Safari current117baseline logs show full metadataGC167ms and recurring4–8msstops; startup history has synchronous rumble/compiler diagnostic traffic. No current Vitrail phase/GPU/frame timing is captured, so shader bottleneck remains unproven. See docs/client-performance-investigation-117.md and validation record. This turn is documentation only; no new build/runtime/release changes. Microphone deferred.


## Development118 snapshot integration — 2026-10-28

User requests26.4snapshots. Explicit1–6launch candidates only; original publisher hashes pin same26.3LWJGL ABI/Java25. Keep snapshot versionType/asset index and reject future Java. Snapshot visibility stays off by default. Existing6.9CPU overlay follows dependency; snapshot6uses OSHI7.7.2supported SPI provider (priority100, opt-in native CPU handoff), not replaced game/OSHI7factory classes. See docs/client-snapshots-118.md and client/ports/oshi7. Host real publisher installs/Main native-bootstrap/CPU fixtures are not PS5 acceptance. Preserve117release,64ZIPbudget, all old candidates; no Store/runtime/performance/microphone changes. Console snapshot menu/render/world save/reload pending.


## Development119 snapshot6 bootstrap — 2026-10-28

User confirms118snapshots1–5fully functional,6crash/reopened. Previous-run logs identify mandatory NativeLibrariesBootstrap.loadJNA -> missing PS5 jnidispatch before window, while CPU provider works.119uses runtime5b25cc2genuine JNA builder/nativeABI7.0.4/69JNIexports with existing libffi and resident jnidispatch. Supported loader policy only for original JNA5.19.1receipt; no game/JNA Java replacements. Direct original loadJNA host test forces new native and passes;119physicalretest pending, not full JNA compatibility. Preserve117Store,118candidate, accepted snapshots and64ZIPbudget; microphone/performance unchanged. See docs/client-snapshot6-jna-119.md.


##119 release acceptance — 2026-10-28

User reports119all good and explicitly requests Store release; snapshots remain off by default. Publish exactcandidate de43986035602bcedc81ed904ec1db22b4148ec7b22001c95725ad2348c63c19, no rebuild. Preserve Store description/credits/icon; update version/artifact/digest and release changelog. Keep saved explicit snapshot choices; default-off must be verified from shipped library classes. Include matching OpenAL source/relink materials/checksums/acceptance and verify uploads. Submit catalogPR, do not monitor afterward per user preference. Snapshot6functional feedback does not establish standalone JNA APIs/callbacks/endurance or new Java milestone. Preserve117/118and frozen packages.

119publicationcomplete: full release with five downloaded/hash-verified assets, exact normal/replacement OpenAL relinks and shipped-class snapshot-default checks. CatalogPR907submitted; description/credits/icon unchanged. No PR/checks/deployment/liveStore monitoring per user preference. See docs/validation/client119-store-publication-2026-10-28.json.


## Approved application authentication — 2026-10-29

User authorizes auth-only replacement with approved public client f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3. Use Microsoft consumers OAuth v2 device/token endpoints, XboxLive.signin offline_access and d=RPS ticket. Preserve Xbox/XSTS/Minecraft entitlement/profile checks. Legacy unbound refresh files and other-client v2headers must request fresh sign-in without any token network request; never migrate/relabel their credentials. New v2AES-GCM header authenticates the client ID; fresh-app rotation/restoration remain. Preserve instances/worlds/cache/settings and all unrelated behavior. Relevant host/HTTPS/migration tests pass; live PS5 approved-app sign-in/reopen restore pending. Source-only publication; no branch merge, new app build/version/binary release or Store update authorized in this task. See docs/client-auth-approved-2026-10-29.md. Java runtime unchanged.


##120 approved-auth test app — 2026-10-29

User subsequently requests installable app for e23a091auth migration.120packages it with next in-app version; no further auth/game changes. Preserve119release and candidates. Packaged class audits must check approvedID/v2endpoint/scope/client-bound cache and absence of legacyID/scope; host checks are not console sign-in acceptance. Fresh Microsoft sign-in then owned launch/profile/skin and reopen/restore remain pending. No Store/binary release or branch merge. See docs/validation/client120-approved-auth-build-2026-10-29.json. Runtime source unchanged.


##120 release authorization — 2026-10-29

User explicitly requests ProsperoStore120release with public changelog explaining previous Mojang applicationID, new approved ProsperoCraftID and mandatory fresh sign-in. This supersedes earlier auth-task no-release hold for exact120, not branch merges or console ALL PASS. Publish exact7977a4ba179dc28109bd837b9b4c357cc5e7a04199c0b39e1898bf6e9820e699 with matching source/relink/checksum/validation. Keep Store description/credits/icon unchanged and snapshot defaults off. No explicit live120auth/restore feedback is supplied; record pending validation honestly. Submit catalogPR without monitoring afterward per preference. Preserve119and all prior artifacts.

120publicationcomplete: all five public assets downloaded/hash-verified, both OpenAL relinks exact, live release body verified to explain Mojang-to-own-ID migration and required fresh sign-in. CatalogPR923submitted with description/credits/icon unchanged. No monitoring afterward; no new console auth/restore pass inferred. See docs/validation/client120-store-publication-2026-10-29.json.

## Development121 color themes and uniform Settings — 2026-10-29

User requests actual launcher color themes and a recognizable fallback game
pointer, then explicitly requests uniform Settings bars. Consumer-owned palette
and saved theme index provide Forest/Ocean/Amethyst/Rose/Amber/Graphite; retain
old defaults, independent backdrops, original textures/skins and positive Done
color. Main Settings uses seven identical1080x86bars with10pxgaps and shared
controls. Native/Java mailbox expands together to105fields. Cursor uses a vector polygon rasterized with4x4samples and a thin outline/shadow; retain WSI ownership/hotspot/lifecycle and
keyboard overlay. See docs/client-themes-cursor-121.md. Build/host checks do not
establish PS5 acceptance. Preserve120Store/older candidates/frozen snapshots;
no runtime source or Store publication change.


##121 release authorization — 2026-10-29

User explicitly requests ProsperoStore release121 after the cursor/theme preview
and announcement. Publish exact candidate3ae5d35308bc84119ed0285869630153b2ee9c8ce054e098ce58d0c6851dafaf
without rebuild. Keep Store description/credits/icon unchanged; update changelog
and required version/artifact/digest. Include exact OpenAL corresponding source,
relink materials, checksums/validation and verify all uploaded asset downloads.
Submit catalog PR and do not monitor afterward. Release authorization does not
establish formal ALL PASS; theme reopen/input/endurance remain pending. Preserve
120 and older release/frozen assets; no runtime source changes.

121publicationcomplete: full release with five downloaded/hash-verified assets,
exact normal/replacement OpenAL relinks and shipped snapshot-default checks.
CatalogPR924submitted; description/credits/icon unchanged. No PR/checks/deployment/
liveStore monitoring. See docs/validation/client121-store-publication-2026-10-29.json.
PS5 theme persistence/input/lifecycle/endurance remain pending; no frozen pass.

## Development122 original26.2 GLFW integration — 2026-10-29

User requests26.2after reporting all26.4snapshots work.26.2publisher usesGLFW/
LWJGL3.4.1andasset32,notSDLJava. Consumer genuine pinnedGLFW3.4core gets explicit
SDLPS5window/input/monitor/Vulkan backend viaNullselector; actualheadlesswindow/
monitor implementation is replaced in dispatch. RequireVulkan/NO_API,existing
residentICD, no arbitraryloader/OpenGLclaim/gameJARrewrite. Parent3.4.3nativeABI
936game-methodrefs/118GLFWsymbolschecked,notbroadcompatibility. OptionalIMEABI
retained with nativecompositiondisabled. EagerTinyFDJNI explicitly identifies
unavailabledesktopdialogs and returnscancel/null; neverfakeaccepted/path/upstream
version. See docs/client-26.2-glfw-122.md. Host/publisher/buildchecks arenotPS5pass.
Provide122testapp,publishconsumer source;noStore/frozenmilestone/runtimechanges.
Preserve121andpriorpackages,26.3/snapshotpaths/themes/cursor/auth/defaultsoff.


## Accepted26.4snapshot presentation — 2026-10-29

User explicitly requests removing Experimental labels because all six26.4snapshots
work. Remove the list annotation, EXPERIMENTAL status and stale pending-testing
text for the existing bounded1–6support set. Preserve [snapshot] type labels,
default visibility off, saved choices and future-version Coming soon gate. Source
change applies to next build; exact122candidate remains preserved/unchanged. No
new binary/Store release or runtime source changes.

##123 observed26.2callback repair — 2026-10-29

Safari prior122run1793270980-859997175crashes originalMain inGLFWErrorCallbackI:
Callback.Descriptor(Lookup,FFICIF)removed inresident3.4.3.936game refs missed
bindinginternalconstructor.123pinnedGLFW3.4.1source recompile adds ownClass to
26descriptorinitializers, packaged binding precedes originalGLFW only26.2;
missingbinding fails explicitly. Do not rewrite original game/downloads.26real
descriptors/native error+key libffi closure init/invoke/free checked onhost;
PS5 later startup/menu/world pending. Snapshot acceptedlabel update included.
See docs/client-26.2-callbacks-123.md;rawlogs staylocal. Preserve122/public121;
consumer source publication/testapp only, no runtime/Store/frozen pass change.

##124 observed26.2Vulkan ownership repair — 2026-10-29

Current123run1793271764-318175786passescallbacks but failscheck4after caught
VK.create duplicate: launchergetFunctionProvider initializedVKtooearly; original
bootstrapmarksloaderunavailable then Vulkan/OpenGLfallback fails. Keep shutdown
verifierstrict.124uses existingresidentPS5Libraryentry + genericJNI call directly
toglfwInitVulkanLoader,without touchingVK/GLFWVulkanJava; originalMainownsVK.create.
Host actualoriginal26.2bootstrap + realLavapipe demonstrates initownership/duplicate
reproducer/cleanup. See docs/client-26.2-vulkan-handoff-124.md;rawreportslocal.
PS5menu/render/world/input/audio/save/cleanquit pending; preserve123/122/public121.
Consumer source/testapp only;no runtime/Store/frozenmilestone changes.

##125Fabric26.2native-buffer pressure — 2026-10-29

UserconfirmsVanilla12426.2works,Fabricfails. Run1793272719-47498832loadsControlify/
API then157byteplatformstring malloc+anonymous16KiBENOMEMduringZipFilereopen;
~210MiBheapused/1176committed and132FDs,nativequota/ownerunproven. Java runtime127
defaultoffboundedcore temporarydirectscratchpublished separately;e92cdcepin.125
enablesbeforeJVM,packagesrebuiltlibjava/audit; normal allocatorsfirst;64slots/8MiB
perCunit(16MiBtotal),uncertaincleanupretainsownership. Noheap/GC/driverpolicychange.
Hostdirectheaderfailure/concurrency +actualdisabledJNItests/targetbasebuildpass;
PS5Fabricstartup/world/nativecleanup/endurancepending;noallmodsfitclaim. See
 docs/client-fabric-native-scratch-125.md. Preserve124Vanillafeedback and121Store;
noStore/frozenpass. Rawreportslocal,reusablesourceonlyinJava repo.

##126 Fabric26.2 verifier pressure — 2026-10-29

Failed125run1793273838-5548144 reachesMatrix4f then verifier4221/ENOMEM;native
reportshows24/26byte allocations failing after many16KiBsmallallocation mappings.
App126 explicitly enables runtime128 default-off16384x256byte verifier reserve
beforeJVM, keeps125core policy, rebuilds resident check_code.o and stagedlibverify.so
with pin/hash audits. Runtime source eb8b8cc published separately;no gameJAR,
heap/GC or instance edits. Host allocation/ownership/concurrency+targetbuild pass;
PS5Fabric startup/world/save/endurancepending. See docs/client-fabric-verifier-126.md.
Preserve125/accepted124Vanilla/public121;noStore/frozenpass;rawreportslocal.

##127 Fabric26.2 variable verifier buffers — 2026-10-29

Failed126run1793274682-683235147 Matrix4f verifier3560CCinit2048byteENOMEM shows
128single256byte slots inadequate.127pins runtime129fea0390 contiguous-unit
4MiB arena, retainsdefaultoffruntime/explicitconsumer policy/mallocfirst and
larger/exhausted anonymous fallback. ActualoriginalMatrix4f+fourJOMLclasses pass
legacy verifier withmalloc+mmapdenied;allocationcleanup/concurrency/targetnative
build checked. See docs/client-fabric-verifier-127.md;PS5Fabricstartup/world/save/
endurancepending. Preserve126/accepted124Vanilla/Store121;noStore/frozenpass.

##128 Fabric26.2 SDL lock initialization — 2026-10-29

Failed127run1793275520-7687009 passesverifier then originalMain crashesGLFW0x10008
PS5SDLpthread_rwlock_init failed;actualerrorcodeunrecorded. Consumer-onlyPS5SDL
backend nowbounded256allocation-free atomicRWlocks:parallel/recursive readers,
exclusivewriters,try/NULL,acquire/release,50usbackoff,noFIFO/writerpreference.
PS5CMakepatch only;otherSDLthreads unchanged;targetresident mustnotimport
pthread_rwlock. HostrealbackendASan/UBSan/contention/bounds passed;targetpackage
andPS5world validation explicit. See docs/client-fabric-sdl-locks-128.md. Keep
runtime129pins/candidates127/accepted124/public121;noStore/frozenpass.

##129 Fabric26.2 unreported native exit — 2026-10-29

Reproduced128run1793278503-673552755 endsrenderthreadSettinguser;nofatalJava,
abort/hs-error. DNSpublickeywarningnotprovenfatal.129consumerdiagnosticcandidate
addsboundedallocation-freeGLFW/SDLstartupbreadcrumbs andcopies64KiBpriorVMtail
intomarkedstartuphistbeforetruncation. Alsohandlesuncheckedbackendmonitor/mode
allocationfailure;actualhostforcedmonitorOOMcleanup+3normalcyclespass. Do not
claim128causefixed. See docs/client-fabric-startup-diagnostics-129.md. Runtime
pinsunchanged;preserve128/accepted124/Store121;PS5cause/worldvalidationpending.

##130 identified compiler-TLS abort — 2026-10-29

129failedrun1793280668-685575193 copiednative tail hasabortcaller2dffbc9,
anchor42beb0,prior48bytemalloccaller2dfe551NULL. Exact129symbolanchor2beb0gives
loadadjust400000;resolved29ffbc9compiler-rt__emutls_get_addressabort and29fe551
emutls_alloc::allocate. Runtime d668c642 defaultoffdirectledgerfallbackpublished
separately.130pins/recompilesruntimeownedadapterandexplicitlyenablesbeforeJVM;
existingnative256MiB/2048entrybudgetshared,normalallocatorsfirst,heap/GCunchanged.
See docs/client-fabric-emutls-130.md;hostfailure/lifecycle/targetchecks andPS5
startup/world/endurancepending. Preserve129/accepted124/Store121;noStore/frozenpass.

##131 SDL native synchronization reserve — 2026-10-29

Failed130run1793281245-258448706 gets pastTLSabort;actualMinecraftreport GLFWSDL
pthread_mutex_init failed insidevideo/eventsinit;JavaShutdownexit-1.131consumer
SDLPS5patch preinitializes256recursive nativemutexes/128conditions beforeJVM,
leases/recycleswithoutlateinit;originalpthreadlock/waitcodeunchanged. Native
preinitresultcodefailurestopsexplicitly. Actualpatchedhostbounds/lateinitrefusal/
recursion/exclusion/timedwait/signal/broadcast/10000reusepass. See
 docs/client-fabric-sdl-sync-131.md. Runtime130pinsunchanged;PS5preinit/startup/
world/endurancepending,preserve130/accepted124/Store121,noStore/frozenpass.

##132 Mesa option strings — 2026-10-29

131nativeSDLreserve mutex0/condition0 passes;videodriverinitaborts. Retained
abort2b52159/priorstrdup2b51f26NULLminus400000resolvesactualMesaXMLoptionparser
2752159/2751f26(xmlconfig389XSTRDUP).132scopesMesa/graphicsstrdup+strnduptothe
samegraphicsheapaspairedmalloc/free;SDKplatforminternals/JVM/libcunchanged.
ActualMesaMacrooldrefusalabort/newrouteASan/UBSan,strings/bounds/failure/10000
cleanupcyclespass;targetbinding/sourcehash/exports audited. See
 docs/client-fabric-mesa-strings-132.md. Java runtime unchanged;PS5display/world/
endurancepending. Preserve131/accepted124/Store121;noStore/frozenpass.

##133 GLFW mutex lease — 2026-10-29

132passesSDL/Mesadisplay/GLFWplatforminit,thenoriginalreportPOSIXFailedtocreate
mutex.133consumerGLFWprivatePOSIXmutexbackenddelegatescreate/lock/unlock/destroy
toexistingpreJVMreservedSDLnativepool;noextrastorage/init,leasesreturnandstate
clears,errorsonexhaustion. TLSandotherGLFWopsunchanged;26.2onlybackend. Actual
GLFW+reservedSDLASan/UBSan80kcontention/10kreuse andwindow/input/regressionpass.
See docs/client-fabric-glfw-mutex-133.md;PS5startup/world/working-versionregression
pending. Runtimeunchanged;preserve132/accepted124/Store121,noStore/frozenpass.

##134 RADV queue conditions — 2026-10-29

133GLFW/window/surface succeeds;currentMinecraftVulkandeviceVK_ERROR_UNKNOWN
andnativestderr vk_queue.c83cnd_initfailed.134preJVMreserves128nativeconditions;
RADV-onlysixpthreadconditionbindingsleasebyopaqueaddress,preserveoriginalMesa
C11returnmapping/nativewait+caller-mutex/timeout/signal/broadcast;destroyreturns
lease,holdsobjectprocesslifetime. SDK/SDL/GLFW/OSMesa/JVMglobalbindingsunchanged;
foreignattributes/staticobjectsretainnativefallback. ActualMesaC11+adapterhost
failure/bounds/wake/reacquisition/10000reusepass. See docs/client-fabric-radv-conditions-134.md.
Runtimeunchanged;PS5device/world/endurance/working-versionregressionpending;
preserve133/accepted124/Store121,noStore/frozenpass.

##135 original native C++ throw capture — 2026-10-29

Failed134run1793286316-41038613reaches shadercinit thenlibc++abidemangleOutputBuffer
realloc995bytesNULLabort;exact134symbols+400000loadadjustresolve29e365c/29e362c.
MayobscureoriginalC++exception;libunwindRWlockwarningsalsopresent.135diagnostic
consumerfinal__cxa_throwwraprecordsrawtype/caller/anchor/exactlibc++system_errorcode,
128cap/fixedbuffer/errnopreserve,forwardssameABIobject/type/destructor. No
caught/suppressedthrows/newruntime/gamepolicyfixclaim. See
 docs/client-fabric-native-throw-135.md;actualhostC++ABI/cap/IO tests,targetroute
andpackageaudits;PS5originalcause/startup/worldpending. Preserve134/Store121.

##136 shader compiler initialization locks — 2026-10-29

135capturedexactlibc++system_errorcode12atshadercinit,originalthrowhelpercaller
notoperationcaller. Targetshadercfirstcall/processmutex+glslanginit_lock useSDK
lazy stdmutex;136PS5dependencyexportpatches replaceonlythese withreservednative
SDLmutexshim,atomicfirstlease/returnedloserraces/nativeexclusion/lifecycle.
No bypassinitialization/refcounts;explicitfatalreserveexhaustion;originalthrow
recorderretained. Actualpatchedinitializerhost8000concurrentlifetimes/1000cycles/
80klockincrementspasswithlateinitrefused. See docs/client-fabric-shaderc-locks-136.md;
PS5compilercreation/realshaders/world/regressionpending. Runtimeunchanged;
preserve135/accepted124/Store121,noStore/frozenpass.

##137 monotonic RADV timeline conditions — 2026-10-29

136shadercinitreturns;actualsubmitVkSemaphoreerror/nativevk_sync_timeline123
u_cnd_monotonic_initfailed.134defaultonlyreservepassedexplicitclockattrs tolate
SDKinit.137adds128nativeCLOCK_MONOTONICconditionsalongside128realtime;RADV-only
init/setclock/destroyattribute64entrymetadata choosescorrectnativepool;invalid
clock/duplicate/capacityerrorspreserved,foreignnativepathsunchanged. Native
absolute deadlines/wake/mutex semanticsretained. ActualMesaPOSIXhosttestwith
macOSclockfixture+realtime regressionpass;PS5nativeclock/reserve/semaphore/world/
regressionpending. See docs/client-fabric-monotonic-137.md. Runtimeunchanged;
preserve136/accepted124/Store121;noStore/frozenpass.

##138 remaining mutex caller diagnostic — 2026-10-29

137bothclockreservesandshadercinitpass,thenanotherstdsystem_error12;genericthrow
helperdoesnotidentifyoperation.138startup-onlylibc++mutex::lockwrapgatedatshaderc
entryrecords256enter/returnIDs/caller/anchor/object;alloriginalcalls/throwsforward
unchanged. Separate64failednativepthreadmutexrecordscoverinlinedSDKcallswith
actualreturncode+caller. Exactknownsystem_errorwhatmessageaddedtothrowrecord,no demangle.
Weaklifecyclehookkeepsotherprobesunrequired. Actualhostblocking/throw/cap/IO/errno
andC++ABIregressionspass,targetcallrouteaudits. See
 docs/client-fabric-mutex-caller-138.md. Diagnosticnotconfirmedfix;PS5caller/world/
regressionpending. Runtimepolicyunchanged,preserve137/Store121,noStore/frozenpass.
