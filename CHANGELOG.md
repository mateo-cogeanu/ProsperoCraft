# Changelog

## 01.000.160 — local shader include lifetime repair

- Repair shaderc’s per-compilation include mutex after exact159 registers identify pthread_mutex_destroy with a code address in its handle slot. Use target-only in-object exclusion and scoped callback unlocking; preserve shader/include results and existing initializer reserves.
- Actual pinned-header forced-init-failure, lifecycle/concurrency and target/package checks are recorded separately from pending PS5 loading/menu/audio/Controlify/world validation. Fabric26.2 remains development-only; no release or Store submission. [Evidence](docs/client-shaderc-include-lifetime-160.md).

## 01.000.159 — local Fabric 26.2 development test

- Add an explicit package-only Fabric 26.2 test path with development labels; ordinary builds retain Coming soon and the genuine Fabric entrypoint/dependency checks.
- Route OpenAL HRTF enumeration through the existing resident directory provider, with scoped cleanup and preserved filtering/error reporting, after build158 Fabric26.3 recorded a caught EPERM.
- Record game/loader/window identity before Main. Preserve all existing runtime, audio, controller, UI and supported-version work. Host/target checks pass; exact159 console sound, Controlify features, world persistence and regression remain pending. The first exact159 PS5 run fails during loading; FTP ShadowMount confirms a Render-thread SYSTEM_XO_VIOLATION, with no fault address yet. Add a pinned title-only diagnostic capture builder; host handler/policy and target checks pass, actual capture pending. No release or Store submission. [Evidence and test sequence](docs/client-fabric262-development-159.md).

## Release 01.000.158

- Detect PS5 or PS5 Pro once in the native launcher and share the cached hardware identity with Minecraft’s F3 CPU/GPU display.
- Show compact CPU labels using 8C16T and PS5/PS5 Pro, with 36 CUs for PS5/Slim and 60 CUs for PS5 Pro. Preserve real logical processor counts and graphics driver information.
- Replace the unavailable model-name lookup with the native SoC query; preserve the existing F3 wording and report the launcher’s detection result for diagnostics.

Exact existing158 candidate published without rebuilding, at the user’s explicit request. Standard PS5/Slim/Pro detection and gameplay regression remain console-pending. Existing Store description, credits and icon are preserved.

## 01.000.157 — local model-resolution candidate

Try the model export directly by name/NID in already-loaded handles; remove the unrelated self-export prerequisite and accept bounded spaced retail suffixes. Add per-attempt status diagnostics. No new module load or release; console identification remains pending. [Details](docs/client-model-resolution-157.md).

## 01.000.156 — optional hardware query startup repair

Remove the mandatory libkernel_sys/model-query import added in154/155. Resolve an optional query from the loaded kernel after logging starts; missing exports use model unknown. New gates require the same library dependency set as153. Console launch recovery remains pending. [Evidence](docs/client-hardware-startup-156.md).

## 01.000.155 — compact F3 hardware labels

Use 8C16T and PS5/PS5 Pro names, and show 36 CUs versus 60 CUs. Pro architecture follows Sony’s hybrid RDNA 2.x description. Detection, logical processor counts and graphics behavior stay unchanged. Physical-console readability and model checks remain pending. [Details](docs/client-hardware-info-155.md).

## 01.000.154 — development hardware information test

Readable F3 CPU/GPU names use checked CFI model families from the native SDK query. Preserve the logical CPU prefix, Vulkan IDs/capabilities and driver information. Unknown models remain explicit. Host fixtures and target/package verification are recorded separately from pending standard PS5 and PS5 Pro tests. No Store release or new accepted milestone. [Details](docs/client-hardware-info-154.md).

Detailed client and server release history, console results, known failures and
frozen milestones. Older entries describe evidence available at that time and
may be superseded by later records. Client and server version counters differ.

[Project overview](README.md) · [Current roadmap](README.md#roadmap) ·
[Latest release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/latest)

## Documentation update: 2026-10-30

- Reorganize the README around compatibility, installation, first launch, controls,
  content and troubleshooting; link completed milestones to first public releases.
- Remove released themes/input/content features from upcoming work and distinguish
  available Vanilla 26.2 from held Fabric 26.2. CPU reporting is already implemented
  using real hardware data, not a planned fixed marketing string.
- Retire the old crafting-table icon request: later supplied app artwork and
  Prism/MultiMC instance icons superseded the original launcher artwork. Preserve
  its provenance in assets/branding/README.md and docs/client-account-ui-091.md.
- Preserve removed 122–150 development notes below in descending build order; their
  pending tests describe each historical stage. Add publication summaries for 119
  and 117 without rewriting their original development evidence.
- Refresh the README banner's stale 074 playtest label while retaining its artwork.
  No app build, binary release, Store update or new console validation.

## Release 01.000.153

- Add Minecraft 26.2 Vanilla support through the native GLFW/SDL Vulkan integration. Fabric for 26.2 is marked Coming soon in instance creation, existing instances and launch controls while compatibility work continues. Existing worlds, mods and downloads are kept.
- Improve native allocation and synchronization handling during startup, including graphics, shader compilation and audio initialization.
- Reserve audio mixer and event workers before Java starts and improve OpenAL context/device synchronization. Broader audio and gameplay endurance testing continues.
- Separate the account name and player head in the top bar. Heads now sit centered in their own theme-colored tiles on both the top bar and account screen, keeping their original size and position.
- Remove the Experimental label from the supported 26.4 snapshots. Snapshots remain off by default; explicitly saved choices are retained.

## Development builds 122–152: preserved pre-release notes

Moved from the README on 2026-10-30. These entries retain the console evidence
and pending tests recorded at each stage, rather than claiming that later fixes
were present earlier. Release 153 above is the public delivery point; earlier
public 121 and frozen snapshots remained preserved during this work.

### Development 152 and 151

Account heads gained separate framed tiles and then theme-colored backgrounds,
with the account name separated from the avatar. These visual changes are now
included in 153; exact 153 console appearance remains pending. See the verified
[151 commit](https://github.com/mateo-cogeanu/ProsperoCraft/commit/7a5b9be) and
[152 commit](https://github.com/mateo-cogeanu/ProsperoCraft/commit/79c6b0c).

### Development 150

Build 150 repairs the OpenAL context property/debug locks identified in 149's
loading crash and reserves async event workers before Java starts. The mixer
submitted real audio in 149; audible output and stable gameplay still require
PS5 validation. See [build notes](docs/client-fabric-context-locks-150.md).

### Development 149

Build 149 reserves OpenAL mixer workers before Java starts, addressing the
confirmed mixer-thread creation failure in 148. The later menu exit after Down
has no fatal report and remains unproven. Console audio, input and world tests
are pending; see [validation notes](docs/client-fabric-audio-workers-149.md).

### Development 148

App148 [OpenAL data-discovery lock repair](docs/client-fabric-data-search-148.md)
addresses147's recorded SearchDataFiles mutex allocation failure while retaining
audio/HRTF discovery. Host discovery/mixer checks and target packaging do not
establish PS5 startup/audio/world acceptance. Store121 remains preserved.

### Development 147

App147 [OpenAL HRTF lock repair](docs/client-fabric-hrtf-locks-147.md)
addresses146's recorded mutex allocation failure during spatialization-data
discovery. Native HRTF behavior remains enabled. PS5 startup/audio, Controlify,
world/save and regression checks remain pending; Store121 is preserved.

### Development 146

App146 [OpenAL device-state lock repair](docs/client-fabric-device-state-146.md)
addresses145's recorded native mutex failure inside alcGetString. The complete
native audio library is rebuilt with a consistent device layout. PS5 startup,
audio, Controlify/input and world/save regression remain pending; Store121 stays
preserved.

### Development 145

144Controlify connects and responds to the controller, but a later native exit
remains unresolved. App145 [repairs scoped audio mutex allocation failures and adds bounded input/presentation observations](docs/client-fabric-audio-input-145.md).
Host OpenAL mixer/locking checks pass; audible PS5 audio, screen transitions,
world/save and working-version regression remain pending. Store121 is preserved.

### Development 144

The user confirms143reaches the Fabric26.2menu. World creation remains blocked
by a native library-name allocation failure during compression initialization;
Controlify records the same loader error. App144 [integrates the runtime repair](docs/client-fabric-library-names-144.md).
PS5 world/save/Controlify/audio/regression checks remain pending; menu startup
is not ALL PASS. Store121 and previous candidates remain preserved.

### Development 143

App143 [native exit diagnostics](docs/client-fabric-native-exit-diagnostics-143.md)
improves signal recording, enables bounded stack/resource sampling and limits
repetitive shader trace detail after142closed without a fresh fatal report.
The cause remains unproven; PS5 retesting is needed. Earlier candidates and
Store121 remain preserved.

### Development 142

App142 [optional extended HotSpot synchronization reserve](docs/client-fabric-monitor-reserve-142.md)
addresses141's exhausted4096monitor-mutex reserve during Controlify FFM class
generation near loading-screen completion. Native pool host tests pass in
default and extended modes; PS5 priming/startup/gameplay/audio/regression remain
pending. Earlier candidates and Store121 remain preserved.

### Development 141

App141 [native DNS conversion scratch](docs/client-fabric-network-scratch-141.md)
integrates an opt-in Java runtime repair after140 reported native allocation
failure during an account-service DNS lookup. Host allocation/ownership and
target runtime checks pass; PS5 Fabric26.2 startup/gameplay and working-version
regression remain pending. Store121 and earlier canonical candidates remain intact.

### Development 140

App140 [native presentation reserves](docs/client-fabric-present-reserve-140.md)
addresses139's failed first VideoOut worker creation after VMA/shader/swapchain
startup. It reserves that native worker and RADV mutexes before JVM startup;
PS5 presentation, Fabric26.2 gameplay/audio/save and working-version regression
remain pending. Store121 and all prior canonical candidates are preserved.

### Development 139

App139 [VMA lock allocation candidate](docs/client-fabric-vma-locks-139.md)
uses VMA's supported custom lock hooks after138 recorded an allocation failure
in the shared-mutex path during GPU buffer creation. Host concurrency and real
GPU allocation/transfer checks pass; PS5 Fabric26.2 startup/world/save and
working-version regression remain pending. Store121 is preserved.

### Development 138

App138 [native mutex caller diagnostic](docs/client-fabric-mutex-caller-138.md)
adds bounded call-site tracing after137 passed shader compiler initialization
but encountered another native resource exception. PS5 diagnosis remains pending.

### Development 137

App137 [RADV timeline condition clock integration](docs/client-fabric-monotonic-137.md)
adds reserved native monotonic conditions after136 successfully created the
shader compiler. PS5 semaphore creation and gameplay validation remain pending.

### Development 136

App136 [shader compiler initialization lock candidate](docs/client-fabric-shaderc-locks-136.md)
uses reserved native SDL mutexes for targeted shaderc/glslang initialization
locks after135 captured native system_error12. PS5 validation remains pending.

### Development 135

App135 [native C++ exception diagnostic candidate](docs/client-fabric-native-throw-135.md)
records the original throw before low-memory exception formatting can hide its
cause. Build134's original exception remains unresolved; PS5 testing is pending.

### Development 134

App134 [RADV queue condition reserve](docs/client-fabric-radv-conditions-134.md)
addresses the explicit native condition-initialization error during Vulkan
device creation on133. PS5 launch/gameplay validation remains pending.

### Development 133

App133 [26.2 GLFW native mutex integration](docs/client-fabric-glfw-mutex-133.md)
uses the existing reserved SDL native mutex pool after132 progressed through
display initialization. PS5 launch/gameplay and working-version regressions
remain pending.

### Development 132

App132 [Mesa option-string allocator integration](docs/client-fabric-mesa-strings-132.md)
addresses the identified display-initialization abort after131's native lock
reservation succeeded. PS5 Fabric launch and gameplay validation remain pending.

### Development 131

App131 [PS5 SDL native synchronization reserve](docs/client-fabric-sdl-sync-131.md)
addresses130's explicit mutex-initialization failure by reserving native SDL
mutex and condition objects before JVM startup. Console validation is pending.

### Development 130

App130 [Fabric26.2 compiler-TLS allocation repair](docs/client-fabric-emutls-130.md)
addresses the native abort identified in129's retained trace. PS5 launch,
world and sustained-operation validation remain pending.

### Development 129

App129 [Fabric26.2 startup diagnostic candidate](docs/client-fabric-startup-diagnostics-129.md)
preserves the previous native trace tail and adds bounded GLFW/SDL startup
checkpoints. It also handles native monitor allocation failure cleanly. Build128's
unreported exit remains under investigation; PS5 validation is pending.

### Development 128

App128 [PS5 SDL reader/writer lock candidate](docs/client-fabric-sdl-locks-128.md)
addresses the GLFW/SDL lock initialization failure seen after127 passed class
verification. PS5 Fabric startup and gameplay validation remain pending.

### Development 127

App127 [Fabric26.2 variable-buffer verifier candidate](docs/client-fabric-verifier-127.md)
addresses the larger allocations that still failed on126. The actual failing
class passes host verification with ordinary allocators denied; PS5 validation
remains pending.

### Development 126

App126 [Fabric26.2 verifier allocation candidate](docs/client-fabric-verifier-126.md)
reduces native page waste observed in125's launch failure. Console Fabric
startup and world validation remain pending; vanilla26.2 was accepted on124.

### Development 125

The user confirms Vanilla 26.2 works on build 124. Development 125 addresses the native temporary-buffer allocation failure seen in Fabric 26.2; [diagnosis and pending validation](docs/client-fabric-native-scratch-125.md). Fabric retesting is pending.

### Development 124

Development 124 fixes early Vulkan-loader initialization on 26.2 after build 123 reached backend selection; [diagnosis and test notes](docs/client-26.2-vulkan-handoff-124.md). PS5 startup and gameplay retesting remain pending.

### Development 123

Development 123 repairs the 26.2 GLFW callback ABI failure observed on build 122; [crash and repair notes](docs/client-26.2-callbacks-123.md). PS5 retesting is pending.

### Development 122

Development 122 adds a Minecraft 26.2 test candidate using a genuine GLFW core with the existing PS5 SDL/Vulkan backend. The original game JAR stays intact. [Integration and test notes](docs/client-26.2-glfw-122.md); PS5 menu/world/input/save validation is pending. Public release 121 is preserved.

## Release 01.000.121

- Add six saved launcher color themes: Forest, Ocean, Amethyst, Rose, Amber and Graphite.
- Make all seven Settings bars uniform in size, spacing, corners and focus/press behavior.
- Redesign the fallback in-game cursor with a vector polygon, antialiased edges, thin outline and shadow; retain its click hotspot.
- Keep backgrounds separate from theme selection, original artwork/skins and snapshots off by default.
- Publish exact121 with corresponding OpenAL source/relink materials and verified checksums. Host/render/package checks pass; broader PS5 theme persistence/input/lifecycle checks remain pending.

## Release 01.000.120

- Earlier builds used Mojang's application client ID. ProsperoCraft now uses its own approved Microsoft application; everyone must sign in again once after updating.
- Bind encrypted saved refresh credentials to ProsperoCraft's client ID, preserving fresh-app restoration and rotation. Old-app refresh tokens are not reused.
- Preserve Microsoft/Xbox/XSTS/Minecraft ownership/profile checks, instances, worlds, downloads and settings. Snapshots remain off by default.
- Host/auth/HTTPS/migration/package and exact native relink checks pass. Live120authentication/restore remains unconfirmed in the publication record.

## Release 01.000.119

Publish the exact119 candidate after positive console feedback, carrying118's
snapshot1–6 choices and the snapshot6 JNA repair. Snapshots stay off by default;
existing explicit choices are retained. This is functional console acceptance,
not exhaustive mod/JNA/endurance validation. The earlier development entries
below retain their original pending-test scope. [Release notes](docs/releases/client-snapshots-119.md) ·
[Console acceptance](docs/validation/client119-console-acceptance-2026-10-28.json).

## Development 01.000.119

- Integrate genuine native JNA dispatch for snapshot6early bootstrap using the existing resident library mechanism and supported JNA loader settings. Keep original game/dependency JARs intact.
- Record user-confirmed functional snapshots1–5on118and the concrete snapshot6missing-native crash. Direct original-bootstrap/native host checks pass;119PS5retest pending. Public/Store117unchanged. See [details](docs/client-snapshot6-jna-119.md).

## Development 01.000.118

- Enable explicit experimental launch candidates for26.4snapshots1–6 with correct snapshot arguments and asset indexes; reject newer Java requirements and unreviewed versions.
- Select the existing PS5 CPU provider by dependency and add a separate OSHI7SPI provider for snapshot6, preserving original game/library JARs.
- Original publisher install/bootstrap/CPU and26.3regression checks pass. PS5 rendering/world tests remain pending; public/Store117preserved. See [details](docs/client-snapshots-118.md).

## Release 01.000.117

Publish the exact117 candidate with default Controlify setup, instance duplication,
world-handle repair, managed dependency updates and native input/haptic integration.
Earlier keyboard, haptic and114 world play/reload feedback is positive; adaptive
trigger feel and broader lifecycle/endurance checks remain pending. Later Store117
reinstall and second-tester success are recorded in the [performance review](docs/client-performance-investigation-117.md).
Microphone capture remains deferred. [Release notes](docs/releases/client-controls-worlds-117.md).

## Development 01.000.117

- Arrange Mods, Shaders, Resource Packs and Duplicate Instance in a 2x2 grid with matching directional navigation.
- Share Settings-style dark glass button faces, animated focus and press feedback across instance actions and content controls; give Done a distinct green fill and respect Reduced Motion.
- Handle the observed PS5 rejection of per-zone adaptive trigger resistance by following trigger travel with basic native effects, with hysteresis and redundant-update suppression. Physical effects still require PS5 validation.
- See [validation and limitations](docs/client-buttons-triggers-117.md). Public and Store remain108.

## Development 01.000.116

- Add Duplicate Instance with independent worlds/mods/packs/settings, unique names/IDs, progress, cancellation and staged publication/recovery.
- Translate Controlify adaptive-trigger packets to native feedback, weapon and vibration effects, including per-zone patterns. Reset on close/disconnect/interception; physical PS5 effects remain pending.
- Record positive115feedback. Host/native-protocol/UI-render and package checks pass;116console tests and Store update remain pending. See [details](docs/client-duplicate-triggers-116.md).

## Development 01.000.115

- Install Controlify and required dependencies once when setting up a new Fabric instance. Preserve existing instances, user queues and later uninstalls; retain a pending marker for failed/cancelled setup retries. NeoForge remains coming soon.
- Accept safe Unicode content filenames and installed receipts, fixing the section-sign formatting in C418 Songs Only. Preserve original names/bytes and reject unsafe path/control characters.
- Record successful114PS5world play/reload.115host/live-download checks pass; actual new-instance and formatted pack tests remain pending. See [details](docs/client-default-controlify-unicode-115.md). Public/Store remain108.

## Development 01.000.114

- Reserve filesystem room for world operations by enabling a64-handle cache for immutable, reopenable Java ZIP/JAR sources. Integrate runtime0126 and its rebuilt core image.
- Verify300logical archives plus deep write/read/walk/delete under a96-fd host cap; the omitted-option control fails from exhaustion. Actual PS5 world lifecycle and headroom remain pending.
- Record positive113haptics feedback and preserve that implementation. Public/Store remain108. See [details](docs/client-world-handles-114.md).

## Development 01.000.113

- Add native compatible two-motor rumble after a successful real capability probe; share vibration-mode selection with HD audio and log its first nonzero samples.
- Use checked descriptor-first canonical paths and native stat-based handle inventory after112 reproduced EMFILE chunk read/save failures. Add opt-in in-memory file accounting. The leak owner and PS5 recovery remain unproven.
- Host/native fixture and target package checks pass; console save and physical vibration testing remain pending. See [details](docs/client-save-rumble-113.md). Public/Store remain108.

## Development 01.000.112

- Continue independent queued downloads after failures and retain failed selections with detailed errors.
- Add native DualSense gyro and a separate Controlify actuator-audio endpoint, with real native capability probes. Physical PS5 input/haptic validation remains pending.
- Retain a healthy OpenAL output across resource reloads; raise the soft descriptor budget within its hard cap and improve exhausted-file diagnostics after observed save failures. Console save/audio validation remains pending.
- Integrate genuine native compression/database libraries and a separate full-source Distant Horizons PS5 test variant. Game launch/rendering and persistence remain pending. See [details](docs/client-native-input-storage-112.md).

## Development 01.000.111

- Automatically upgrade receipt-managed Fabric dependencies when a newly downloaded mod requires a newer resolved version, including known outdated requirements repaired before Play.
- Verify new downloads and the resulting mod dependency graph before replacing files. Restore old JARs on cancellation or write failure before receipt commit, and remove obsolete JAR filenames after successful updates.
- Preserve modified/manual files and reject incompatible combinations or automatic downgrades. PS5 update and launch validation is pending.

## Development 01.000.110

- Detect installed Iris before Vulkan game launch and show an OpenGL compatibility message with Installed/Uninstall and Vitrail guidance. Prevents the observed Iris initialization path from aborting the app.
- Check original Fabric manifests, including renamed and bundled Iris, while preserving files and the109 download fix. PS5 validation is pending.

## Development 01.000.109

- Resolve exact required dependency versions before downloading, allowing Iris and Sodium to be queued together in either order.
- Discard dependencies of superseded download choices and identify genuine conflicting project/version IDs. Existing installed files stay protected.
- PS5 download, launch and Iris rendering tests are pending; public Store release remains108.

## Development 01.000.108

- Check Fabric manifests and bundled modules alongside recursive Modrinth required dependencies; automatically add Fabric API when a required module is missing.
- Repair existing instances before launch. Healthy instances need no dependency network requests; version conflicts and unmapped missing dependencies stop in the launcher.
- Record positive PS5 keyboard feedback on107. Dependency108 console testing remains pending; Store stays unchanged until accepted.


## Development 01.000.107

- Add an Uninstall button beside each installed mod, shader or resource pack, with Cancel as the default confirmation action. Other files, worlds and settings are kept.
- Show actual project artwork for WebP, indexed PNG, RGB/RGBA PNG and JPEG icons. Replace the Modrinth-logo fallback with a neutral placeholder when artwork is unavailable.
- Preserve106's audio, physical input and Controlify candidates. PS5 validation remains pending.


## Development 01.000.106

- Reserve the actual audio port before JVM/GPU allocation; add direct optional HID imports, early handles and captured diagnostics.
- Share resident SDL as SDL3 for Controlify; retain temporary controls until a mod opens a controller. Console validation pending.
- Add actual Installed inventories for mods, shaders and resource packs, notice-style checkboxes and cached project/download thumbnails.
- Add an optional reversible Vitrail shadow-map scale control, preserving other settings. Shader FPS improvements are not yet measured.


## 2026-10-27 — Fabric recovery and input105

Restore standard cached Fabric resource reads after104startup regression reports.
Add persistent controller-key remapping and optional physical keyboard/mouse
input through normal SDL events,with safe releases and missing-device fallback.
US ASCII text;gameplay input only,native launcher remains controller-driven.
Host/sanitizer/target checks pass;PS5Fabric recovery,hardware input and save/load
remain pending.103descriptor/save errors remain unresolved. NoStore/public release.
[Guide and limits](docs/client-fabric-input-105.md).

## 2026-10-27 — Shader image runtime, modded pauses and launcher104

Captured103 shader failure is missing Java AWT/Disposer in Vitrail noise decoding.
Integrate the Java port's genuine ImageIO raster/LCMS subset; expand the pressured
code cache and use concurrent explicit GC. Scope JAR resource streams to reduce
FD pressure after captured world-save errors. Fix spatial launcher navigation,
secondary content-button styling and launcher QWERTY; in-game keyboard unchanged.
Host/target checks pass; PS5 shader rendering, stutters and save/reload remain
pending. Preserve101/103; no Store/public release.
[Evidence and test guide](docs/client-stutters-shaders-controls-104.md).

## 2026-10-27 — Fabric and Modrinth development candidate103

Create Vanilla/Fabric instances with a loader dropdown beneath Version; NeoForge
is visible as coming soon and Forge is removed from the roadmap. Instance Settings
adds searchable Modrinth Mods/Shaders/Resource Packs browsers ordered by downloads,
persistent checked queues and Download All with verified bodies/required mod
dependencies. Fabric uses official profiles/Knot/Mixin with shared PS5 native
providers and intact Mojang JARs. Vitrail26.3 and its required Sodium dependency
resolve/download/verify in a live host test; actual PS5 mod/shader compatibility
and performance remain pending. Preserve accepted101; no Store/public release.
[Guide and validation scope](docs/client-fabric-modrinth-103.md).

## 2026-10-27 — Accepted101 functional release

All requested101launcher,account,input andskin changes receive functional PS5
acceptance and explicit Store release authorization. Publish the exact tested
package as01.000.101 with matching OpenAL source/relink materials,checksums and
public notes. Preserve100and older releases;no rebuild. Java0124acceptance is
recorded separately in the Java repository. Broader endurance/memory/lifecycle
tests remain incomplete. [Release notes](docs/releases/client-launcher-skins-101.md).

## 2026-10-27 — Client101 account, controls and skin-stream candidate

Sign-in/restoration returns to Instances; account action follows signed state.
New libraries hide snapshots by default. Active tabs gain a persistent highlight;
resolution changes only through the dropdown. Game menus use cursor selection
without synthetic D-pad/stick arrow navigation, retaining text-keyboard controls.
Java runtime0124 addresses the captured skin-download availability-query denial;
no game JAR edits. Host/target checks pass, console behavior remains pending.
Published100 andStore assets stay unchanged. [Guide](docs/client-launcher-controls-skins-101.md).

## 2026-10-27 — Accepted100 smooth high-refresh release

PS5 feedback accepts100 as much better and requests public release. Preserve
its exact tested package and publish01.000.100 with matching OpenAL source/relink
materials, checksums and public notes. Update the existing ProsperoStore listing.
Acceptance covers subjective smoothness; no formal ALL PASS, measured100FPS,
long-session memory or complete lifecycle result is inferred. Earlier098draft
and all historical packages remain intact. [Release notes](docs/releases/client-smooth-high-refresh-100.md).

## 2026-10-27 — Client100 isolates remaining remark cleanup spikes

099 reduces reported stutters, with typical captured pauses near4ms; remaining
13–21ms spikes concentrate in G1 remark.100 retains099 collection batching and
turns off class/code cleanup during concurrent remarks, keeping full-GC class
unloading enabled. Unused class/code retention can increase memory pressure;
this is an isolation candidate with console/long-session tests pending. No
Store update or public release. [Guide](docs/client-remark-cleanup-100.md).

## 2026-10-27 — Client099 tests smaller G1 collection batches

098logging reduction did not fix the reported stutters. Same-run steady-gameplay
logs show repeated pauses above the120Hzframe budget.099tests4mspausegoal,
1percent minimum young generation and16mixedGCtarget,with heap/quality unchanged.
Host controls show smaller median but more frequent pauses;PS5improvement is
unverified. Keep098draft andStoreheld pending humanconfirmation. [Guide](docs/client-frame-pauses-099.md).

## 2026-10-27 — Review097stutters before098publication

Safari-retrieved same-run GC reports show125safepoints over58.889seconds,
10.886msmedian/23.792msmaximum;115exceed120Hzframe budget. No fullGC occurs.
MixedG1copy/evacuation pauses plausibly explain short hitches;frame correlation
and other causes remain unresolved.098retains info summaries and removes verbose
GC/safepoint/class logging;heap/collector/quality remain unchanged. Stutter relief
requires console comparison. [Findings](docs/client-stutters-098.md).

## 2026-10-27 — ProsperoCraft0.98 high-refresh release

Build097reached119FPS on PS5 with VSync disabled and a120FPS target, reported by
the tester. Release01.000.098 retains that high-refresh path and fixes displayed
build identity. Public notes describe supported120Hz output,60Hz fallback and
remaining FIFO pacing. Exact098console regression,frame-time measurements and
endurance remain pending; no formal ALL PASS or frozen milestone is inferred.
Full GitHub release and ProsperoStore update requested. [Release notes](docs/releases/client-high-refresh-098.md).

## 2026-10-27 — Correct visible version for the next build

097still displayed096in the launcher footer because that label was hardcoded.
The packager now injects the selected version into the native footer and startup
logs, reading startup version from its manifest. Host previews default to
Development. Existing097/096packages remain unchanged; this correction ships in
the next candidate and still needs PS5 visual confirmation.

## 2026-10-27 — Client097 requests supported120Hz output

The user reports60/61FPS with VSync disabled and a120FPS target. Enable the
existing VideoOut high-frame-rate manifest declaration and replace SDL's60Hz
preference with the fastest enumerated mode up to120Hz, retaining59.94Hz fallback.
The pinned backend verifies actual output/vblank before offering119.88Hz.
FIFO presentation remains; this does not implement uncapped VSync-off behavior
or guarantee120FPS. Host policy/fallback/input checks pass; target/package checks
are recorded separately and console FPS/output/lifecycle tests remain pending.
Preserve exact096release and all older milestones. [Guide](docs/client-high-refresh-097.md).

## 2026-10-26 — Client083 locks logical/display resolution to1080p

Store-installed082has a reported game-menu hit-test/pointer misalignment with
X/R2; the user identifies resolution mismatch.083replaces the720pdefault and
selectable sizes with fixed1920×1080launch, SDLlogical window/create/resize and
enumerated display-mode selection. Existing library settings migrate with backup;
worlds/downloads/options are preserved. Settings visibly marks the value locked.
Host/target/package audits pass; physical083clicks/demo-world/audio/lifecycle
remain pending. [Guide](docs/client-resolution-083.md). Published082and frozen
source/validation remain intact; no new milestone or Store release is inferred.

## 2026-10-26 — Client082 launcher/lifecycle fixes confirmed

The user confirms: “yes it all works. all the fixes you added.” Recorded as
human ALL PASS for exact082's saved/horizontal welcome checkbox, native stick
navigation, bounded focus/press animation and game Quit returning to the native
library with relaunch. [Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Launcher_Lifecycle).
The published package and symbols match the082build hashes and are retained
without rebuilding. The same release receives additive console evidence; old
validation assets and all earlier milestones remain unchanged. No exact cycle
count, measured FPS, independent current-run logs or two-hour endurance is inferred.

ProsperoStore PR811 is updated against current main; its checks pass. Required
write-access reviewer approval still blocks merge; the publishing account cannot
supply it.

## 2026-10-26 — Client081 controller layout and launcher polish

Adds sprint/sneak, hotbar cycling, offhand swap, drop, camera/player-list/debug
and utility bindings through normal SDL events. Menu right-stick pointer,
click/right-click/drag/quick-move/scroll and a compact ASCII text picker cover
more vanilla UI interactions. The WSI-owned VideoOut cursor uses64KiB retained
direct memory; original game files remain intact. A launcher Options guide
explains the layout. Full Controlify and mod shortcut coverage remain planned.

Changes the library heading to Instances, removes its subtitle and routine
system startup notifications, shows01.000.081at bottom right, blocks unsupported
versions before launch, and adds a saved startup approval/roadmap notice with
OK and Show next time. Only exact26.3SDLdemo is eligible to launch. The existing
4096MiBstorage request, worlds/cache and074audio/performance settings remain.

Host/controller/cursor/notice tests and target packaging are development evidence;
physical controls, cursor alignment, text entry, download completion and retained
PS5smoothness/audio need console validation.080human report says downloading,
not completed or gameplay accepted. [Guide](docs/client-controls-081.md).

## 2026-10-26 — Client080 increases the app-local download reservation

079downloads repeatedly stop at212MBwithENOSPCwhile the console reports382GBfree.
The app still inherited downloadDataSize256from the original probe.080requests
4096MiBusing the same title and keeps the existing /download0/ProsperoCraft data.
The normal app sandbox does not guarantee /data access, so no external relocation,
privilege helper, cleanup or reformat is introduced. Storage error categories and
app-local messages improve diagnosis; unsupported capacity queries remain unknown,
not zero. Existing instance/world/cache bytes and079package/symbols are preserved.

Install the complete folder including param.json, refresh loader metadata and
relaunch. Actual existing-volume expansion, downloads past212MBand completion/
26.3launch need console validation. [Guide](docs/client-storage-080.md) ·
[Build record](docs/validation/client080-storage-build-2026-10-26.json).

## 2026-10-26 — Client079 instance library, native redesign and on-demand demos

Replaces the fixed-instance home with a three-action top bar, L1/R1navigation,
paged instance grid, large-icon detail screen and Play/settings/download repair.
Adds controller name keyboard/case/clear controls, eight built-in icons, isolated
per-instance worlds/options, persistent resolution/download/motion/snapshot settings,
short settling animations and held-direction repeat. No sample instance is created.

Removes bundled Minecraft client/assets from the current app. The console installer
resolves the selected26.xpublisher metadata, verifies size/SHA-1, downloads original
client/Java libraries/index/assets into a shared cache, and commits only complete
installs. Bounded background workers support progress, cancellation, cache reuse
and repair. Desktop native classifiers are excluded; native bindings remain PS5
ports. Game classes load from the selected verified cache with a separate loader.
Play is explicitly upstream restricted demo while MSA app approval is pending.

Host fixture tests cover instance persistence/isolation/controllers/settings and
installer security/failure/cancel/repair behavior. Actual26.3publisher inputs verify
54originalJARs/5147assets/index34and correct loader separation. Native scenes/JNI
and package checks are distinct from pending PS5tests.26.1/26.2downloads are supported
but gameplay needs the unimplemented GLFW path; Java25alone is insufficient.
No customPNG/removal/archive support yet. Preserve078/074bytes; no new release or
Store update. [Guide](docs/client-instances-079.md) ·
[Build record](docs/validation/client079-instances-build-2026-10-26.json).

## 2026-10-26 — Repository renamed to ProsperoCraft

GitHub confirms the canonical repository is now `mateo-cogeanu/ProsperoCraft`.
Updated current documentation, release links, AppID review draft and generated
source references, plus the Git remote. Local checkout paths, frozen validation
snapshots and compiled packages remain unchanged. Minecraft Services403/app review
is still pending.

## 2026-10-26 — Client078 reaches Minecraft Services; review request prepared

Human reports `[MINECRAFT HTTP 403]` after Microsoft approval. This confirms the
upstream Microsoft/Xbox/XSTS flow reached Minecraft login; it does not establish
an authenticated Minecraft session, entitlement/profile success or game handoff.
App allowlisting is the leading explanation; the raw server reason is unconfirmed.
Verified the official AppID Review form and prepared a transparent project-owner
[request draft](docs/appid-review-request.md). No form submitted, app ID changed,
authentication bypass added or package rebuilt. App review remains pending.

## 2026-10-26 — Client078 preserves and identifies authentication rejections

Public-client registration initially returned401/invalid_client/AAD70002 on a
host service probe. The user enabled that setting and reached approval, then the
launcher returned to Not signed in with generic registration text. Exact later
endpoint/status remains unresolved; this is not proof of Minecraft403or ownership
failure.077did not record authentication errors sufficiently to identify the stage.

Fixes fixed-length streaming POST behavior that loses OAuth401error bodies in
OpenJDK25. Buffered bounded requests preserve these responses; endpoint/status
prefixes distinguish failures and safe PS5_AUTH diagnostics record only fixed/
allowlisted metadata. Minecraft403is labeled a services denial, with approval as
a possibility. Tokens, live codes, raw bodies and exception text stay excluded.

Real localHTTPS regressions cover old/new401handling,403nonJSON, redirect refusal,
body bounds, CA/hostname rejection and redaction. Auth pipeline tests include public
client and Minecraft denial cases. Real PS5 sign-in/rejection diagnosis remains
pending078. Native-first launcher, icons, original artifacts and074audio/performance
are retained;077package/symbols preserved. No release or Store work.

[Guide](docs/client-auth-078.md) · [Build record](docs/validation/client078-auth-errors-build-2026-10-26.json).

## 2026-10-26 — Client077 shows the native launcher before Java/game startup

The user reports the GUI never appears and requests separation from Minecraft
initialization. The old path invoked the native screen after VM startup, artifact
scan, native libraries and C1 warmup. Current console logs were unreachable, so
no specific crash location is established. This fixes the confirmed ordering.

A native UI thread presents its first frame before VM creation and stays responsive
while account services prepare. A bounded mutex mailbox carries public UI text and
ordered controller edges; JNI remains on the original JVM startup thread. Artifact
verification, game native loads, C1 warmup and Minecraft Main begin only after
Play/demo selection and successful native display cleanup/thread join. Java boot
failures retain a native failure screen for log collection.

User icons, MSA flow and074audio/performance settings are retained. Preserve exact
075/076candidates and074accepted bytes. Host native/bridge/order/auth tests and
build verification are recorded separately from pending PS5 GUI/MSA/handoff tests.
No new release or Store work. [Guide](docs/client-launcher-077.md) ·
[Build record](docs/validation/client077-native-first-build-2026-10-26.json).

## 2026-10-26 — Client076 user-supplied app and launcher icons

Uses the user's `ProsperoCraft2.png` for the packaged512x512 app icon and
`ProsperoCraftTransparent.png` for the native launcher's corner logo. Original
source PNGs are retained, with SHA-256 provenance in the branding manifest. A
small generated native bitmap preserves transparency against the sidebar without
adding a runtime image decoder. Packaging regenerates the artwork from sources.

This is a branding candidate; Microsoft login, game files, audio and performance
policies are unchanged. Exact075 package/symbols are preserved while the user tests
MSA. Console appearance and inherited live-login/display-handoff validation remain
pending. No release or Store update. [Build record](docs/validation/client076-branding-build-2026-10-26.json).

## 2026-10-26 — Client075 native launcher and Microsoft sign-in candidate

Adds a controller-operated native launcher with a forest palette, installed Vanilla
26.3 card, Microsoft account panel, device-code sign-in, and explicit demo fallback.
Uses the public application registration supplied by the user; no client secret.
Authentication checks Xbox identity, Minecraft entitlement and the Java profile
before passing the session to the unchanged original Main. Tokens remain in memory.
The first version has one installed instance and an informational settings page.

A reusable runtime renderer API closes VideoOut, unmaps and releases its buffers
before game handoff; a failed cleanup refuses launch. Existing074 audio/C1/G1 and
quality settings are retained. Original JARs/assets and accepted074 bytes remain
intact. Host auth/native UI/fault-injection/regression tests and target package
checks pass. Real login, native menu and display/audio/gameplay handoff still need
PS5 validation. No new release or Store publication.

[Guide](docs/client-launcher-075.md) · [Build record](docs/validation/client075-launcher-build-2026-10-26.json).

## 2026-10-26 — Client074 sound and smoothness confirmed

The user reports “very good sound and very butter smooth” on exact074. Its package,
symbols and tested source identity are preserved without rebuilding. This confirms
human-audible game sound and subjective smooth gameplay for this playtest; precise
FPS/GC metrics, save/reload and endurance remain unvalidated. No formal ALL PASS
or new public release is inferred. High-settings support remains the goal.

[Confirmation and exact hashes](docs/validation/client074-smooth-audio-confirmation-2026-10-26.json).

## 2026-10-26 — Client073 audio recovery failed;074 initialization/pacing

073stillhasnosound:all20lateinit/portprobesreturnBusy/NotInit. PartialG1snapshot:
99pauses,median18.082ms/max41.608ms,nofullGC; stackobserverThreadDumpmax8.927444ms.
074initializesAudioOutonthenativestartupthreadbeforeVM/heap,acceptsonlyactualearly
success/AlreadyInitandstillrequiresactualport/PCM. Failed earlyinit retainsbounded
laterecovery. G1pausegoal8ms/workers4andopt-instackobserver targetsmallhitches;
quality/heap/nativebudgetunchanged. Hostchecks/targetbuildpass;PS5audio/order/
workerheadroom/latency pending. No newpublicrelease.

[Guide](docs/client-audio-pacing-074.md) · [Evidence](docs/validation/client073-audio-stutters-2026-10-26.json).

## 2026-10-26 — Client072 tiny stutters/audio failure;073 recovery

Human reports tiny stutters on072but no sound. CapturedG1window has92pauses,
median20.8335ms/max49.747ms,andnofullGC;16/12qualityretained. This is qualified
feedback,notmatchedbenchmark/enduranceacceptance. NativeAudioOutinitfails twice
with0x80260002beforeanyportopen.073addsboundedBusyrecoveryrequiringrealportopen,
explicitAlreadyInit handling and failurepropagation;max10attempts/450mswait.
G1/heap/workers/quality/input remain unchanged. RealOpenALsanitizer/recovery/
PCM/lifecycle tests pass;PS5audibility/recovery/performancepreservation pending.
No newpublicrelease.

[Repairguide](docs/client-audio-recovery-073.md) · [Evidence](docs/validation/client072-g1-audio-2026-10-26.json).

## 2026-10-26 — Client071 retention evidence;072 G1 candidate

All3boundedPS5histogramsretrieved:chunkcontainers179k->252k,longarrays78MB->118MB,
while modelquadcountsremainstable. This supports substantialworldretention,not
leakproof. UnsampledSerialfullGC reaches933.366ms; sampledinspectionsadd257–285ms.
Actualoptions/gameconsoleconfirm16/12. Highqualitysettingsremainunchanged.

072usesG1with1536MiBmaximumheap,2parallel/1concurrentGCworkers,processorhint4,
30mssoftpausegoal and20percentG1reserve. Histogramsdisabled; C1/audio/input/game
filesretained. Runtime0121raisesonlyboundeduncompresseddirectheapceiling. Host
actualG1retention/churn andruntimeownershiptests pass;PS5reservation/G1workers/
auxiliarymappings/nativeheadroom/pauses/saveandreloadremainpending. No newrelease.

[Investigation](docs/client-g1-072.md) · [071evidence](docs/validation/client071-retained-heap-2026-10-26.json).

## 2026-10-26 — Client070 comparison invalid;071 retained-heap diagnostics

The user wants smooth highsettings and tried070only as a comparison. It briefly
felt responsive before heavy stutter. Reports still show16/12; the user didnot
change settings.070's intended6/5migration didnot establish effective6/5, and its
mechanism remains unresolved. Captured fullGC reaches917.602ms.

071preserves existing settings, disables the active070distance migration and logs
selected configuration beforeMain. Runtime0120adds opt-inbounded classhistograms
after existing fullGCs:retained>=512MiB,atmost3samples16eligibleGCsapart,top40rows
withall-class totals. This adds diagnostic overhead and is not a stutter fix.
Hostgate/output/options/startup checks and targetbuild pass; actualPS5inspection
and retainedcategories remain pending. No gameJARchanges or newpublicrelease.

[Investigation](docs/client-retention-071.md) · [070evidence](docs/validation/client070-stutters-2026-10-26.json).

## 2026-10-26 — Client069 continued GC pressure;070 distance profile

069starts successfully with768MiBonPS5but stutters recur. Captured logs show
allocationfullGC up to950.997ms,609MiBretained and view16/simulation12.070caps
supported vanilla distances to6view/5simulation once, with exact options backup,
preserving lower values and later edits. Heap/runtime/C1/audio/input/game bytes
stay unchanged. This trades horizon and active simulation area for a smaller
world workload. Actual memory plateau, pause improvement and save/reload remain
pending; no new public release.

[Investigation](docs/client-distance-070.md) · [Evidence](docs/validation/client069-stutters-2026-10-26.json).

## 2026-10-26 — Client068 heap exhaustion;069 headroom candidate

The user reports two stutters, escalating stutters and a complete freeze. Same-run
logs confirm Java heap OOM, failed chunk save and repeated fullGC499M->499M. The
larger code cache relieved earlier pressure, but068did not contain the live set.
069requests768MiBheap/NewRatio3 and retains32MiBcodecache, C1, working audio/input
and original game files. Runtime0119raises only the bounded direct-heap ceiling;
native budget and ownership gates remain. Host reservation/occupancy/C1/startup
checks pass; PS5 reservation, memory sufficiency, pause improvement and save
integrity remain pending. No new public release.

[Investigation](docs/client-heap-069.md) · [068evidence](docs/validation/client068-stutters-2026-10-26.json).

## 2026-10-26 — Native-port identity clarified

Made the README introduction explicit: Minecraft Java runs on the PS5-native
OpenJDK 25 port with native platform integration, without Wine or a Windows build.
No other projects are named or compared.

## 2026-10-26 — Later roadmap updated

Updated the README's Later list: custom **menu** music by CogiArt, `.mrpack`
imports, USB keyboard and mouse controls, themes, JVM 21 and JVM 17. These remain
planned work; the required store-release list is unchanged.

## 2026-10-26 — Client067 sound confirmed;068 freeze candidate

The user confirms beautiful game audio on PS5 in exact067, then reports random
freezes. Current-run reports capture15fullGCpauses, up to647.647ms, caused by
old-generation allocation pressure and actual compiled-code cache GC triggers.
The retained067audio package and symbols are preserved; this is human playtest
feedback, not formal ALL PASS or endurance acceptance.

068 keeps the512MiB SerialGC heap and working audio/input/C1, changes NewRatio
to7 and raises the code cache from16to32MiB. Host occupancy controls show modest
full-GC reduction with more young collections. Console startup, native memory
headroom and actual freeze improvement remain pending. Original game JARs/assets
and runtime implementation are unchanged. No new public release.

[Investigation and test guide](docs/client-gc-068.md) ·
[067 evidence](docs/validation/client067-audio-freezes-2026-10-26.json) ·
[068 handoff](docs/handoff-prosperocraft-client068.md).

## 2026-10-26 — Documentation refresh

- Simplified the README around the project, current status, downloads and setup.
- Preserved its detailed build history, validation notes and milestone index here.
- Added the store-release requirements and later roadmap to the README.
- Kept the existing project artwork and accepted release artifacts unchanged.

## History index

- [Client067: speaker audio candidate](#development067--native-speaker-audio)
- [Playable client066 release](#playable-world-release--01000066)
- [First world entry](#first-world-loaded--01000065)
- [First client menu](#first-minecraft-java-menu-on-ps5--01000062)
- [Client native dependency and graphics milestones](#client-spirv-cross--ps5-all5-pass)
- [Fabric and Paper release](#fabric-and-paper-release)
- [Milestones and release archive](#milestones--releases)
- [Early server diagnostics and fixes](#download-diagnostic-logs-01000009)

## Preserved development record

The following sections were moved from the README on **2026-10-26**, preserving
all recorded build details and links. Client and server version counters are
independent. These are historical entries: statements such as “current,” “next”
and “pending” describe the stage being documented and may be superseded by later
entries. The old roadmap below is retained as history; the active roadmap and
current project status are in the [README](README.md).

## The goal

Bring Java Edition's worlds and ecosystem to native PS5 homebrew through small, console-tested milestones.

| Direction | What we're aiming for |
| :--- | :--- |
| **Server first** | Start a vanilla server, create and reload a world, connect over the network and verify save integrity |
| **Server mods next** | Validate compatible server mod loaders and individual mods against pinned game versions |
| **Client afterward** | Bring up native bindings, a window, rendering, audio and controller input |

Graphics exploration includes OpenGL and Vulkan possibilities. Backend availability, native bindings and renderer-mod compatibility still need to be established on PS5.

## Runtime foundation

Minecraft needs a working Java runtime before the game can be brought up. That work lives in **[ps5-java25-homebrew](https://github.com/mateo-cogeanu/ps5-java25-homebrew)**.

The repositories have separate responsibilities:

- **Java port:** OpenJDK, PS5 platform adaptations, JNI and runtime acceptance probes.
- **This project:** Minecraft dependencies, launch flow, server/client integration, input, graphics and game-specific tests.

The runtime project has these **console-tested Java milestones** on PS5 firmware **13.60**:

| Runtime milestone | What passed | Source & results |
| :--- | :--- | :---: |
| **JVM startup** | Java 25 VM creation, arithmetic, Java thread start/join and shutdown | [JVM_Startup](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/JVM_Startup) |
| **File I/O** | Private-file creation, UTF-8 write/read, size and deletion | [IO_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/IO_Probe) |
| **ZIP / JAR** | Archive reads, manifest parsing, JAR class loading and UTF-8 resources | [ZIP_JAR_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/ZIP_JAR_Probe) |
| **Networking** | TCP/UDP IPv4 loopback, Java worker echo, nonblocking NIO channels and selector readiness | [Network_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/Network_Probe) |
| **LAN / DNS** | Outbound TCP/UDP echo between PS5 and Mac, forward DNS lookup and VM lifecycle | [LAN_DNS_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/LAN_DNS_Probe) |
| **Inbound LAN** | External IPv4 TCP accept and UDP receive/reply | [Inbound_LAN_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/Inbound_LAN_Probe) |
| **HTTPS / IPv6** | Verified HTTPS, IPv6 loopback and concurrent/repeated local traffic | [Advanced_Network_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/Advanced_Network_Probe) |
| **LAN endurance** | Actual IPv6 link-local LAN and 60-second external TCP/UDP workloads | [LAN_Endurance_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/LAN_Endurance_Probe) |
| **Dependencies / JNI** | Manifest-linked JARs, services/resources, system class path and real resident JNI calls | [Dependency_Probe](https://github.com/mateo-cogeanu/ps5-java25-homebrew/tree/main/Dependency_Probe) |

The runtime now has **nine passing console milestones**, including inbound IPv4, verified HTTPS, IPv6 loopback/link-local LAN, 60-second external load, manifest-linked dependencies, actual system class-path loading and resident JNI calls. The first Minecraft-specific bootstrap probe also now passes on PS5. Frozen passing builds use interpreter mode. Client066 now has a playable PS5 C1 performance report; full endurance and lifecycle validation remain pending.

ProsperoCraft brings Minecraft Java Edition client and server development to PS5,
powered by the native OpenJDK25 port. Vanilla,Fabric and Paper servers have
console playtests; the original client now has playable worlds on PS5.
[Project artwork](assets/branding/README.md).

## Product goal

ProsperoCraft aims to be a polished,playable Minecraft Java client running on
native Java25onPS5:responsive controls,smooth rendering,working audio,world gameplay,
saving/reloading and stability. Reaching the menu is an intermediate checkpoint.
Those full-client features still require actual exact-build console validation.

## Development067 — native speaker audio

A new OpenALPS5backend sends the real game mix to AudioOut at48kHz/stereoS16.
It retains066's guardedC1 and input fixes,and backs up/unmutes the old launcher
volume defaults once. Actual mixer/output/error/lifecycle tests pass on host;
**audibility and stability onPS5 remain pending**. Original gameJARs/assets stay
unchanged. [Audio candidate/test guide](docs/client-audio-067.md) ·
[Current handoff](docs/handoff-prosperocraft-client067.md).

## Playable world release — 01.000.066

The user confirms playable worlds,major responsiveness improvement and roughly
30second startup. ActualPS5reports confirm the C1correctness gate and playerjoin.
[Release and setup](docs/releases/client-playable-066.md). Sound remains absent;
this is not a formal full-client ALLPASS or a measured FPS/hardware-utilization claim.

## Implemented in066 — compile Java and repair captured input

The066build enables guarded C1 level1 compilation with one compiler and
an actual compiled-kernel correctness gate before Minecraft. It also supplies the
missing SDL software-relative mouse callback so the temporary mapping can switch
to WASD and right-stick look. Heap/runtime/game JARs/assets stay unchanged.

Host checks exercise the real SDL failure/fix and C1 gate. The user subsequently
confirmed playable worlds and fast loading on exact066; full stability remains
pending. This does not establish a full-hardware-utilization or measured FPS claim.
The published065world release remains available as an earlier checkpoint. [Candidate and test guide](docs/client-performance-066.md) ·
[Current handoff](docs/handoff-prosperocraft-client066.md).

## First world loaded — 01.000.065

The user confirms world entry and punching on PS5. Current-run reports corroborate
player join and actual world rendering. The512MiB direct-backed Java heap starts
successfully. **Very slow loading, severe lag and movement failure remain known
issues.** No useful frame rate,save/reload,audio or stability acceptance is claimed.
[GitHub release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_World-v01.000.065) ·
[Setup and scope](docs/releases/client-world-065.md).

## Development065 — direct-backed Java heap

064 failed before Minecraft: the PS5 refused its384MiB anonymous heap reservation.
The Java port now has a separately bounded direct-memory fallback for explicitly
uncompressed Java heaps. Candidate065requests512MiB with compressed object pointers
disabled;its512MiBheap allowance is separate from the unchanged256MiBnative budget.
This addresses the reservation path,while actualPS5startup/GC/worldloading remain
pending. No game JARs/assets/SDK changes;working controls/menu policy retained.
[Fix and test guide](docs/client-world-065.md) ·
[064failure](docs/validation/client064-startup-failure-2026-10-26.json) ·
[Current handoff](docs/handoff-prosperocraft-client065.md).

## Development064 — demo-world heap headroom

The user confirms063controls work and the idle menu behavior improved. Demo-world
loading then stalled. Current-run reports capture a **Java heap OOM in world
chunk generation**, followed by repeated spawn-preparation progress. The animated
loading screen does not establish continued world progress.

Candidate064raises the Java heap from256to384MiB and extends the bounded observer
for later world loading. Controls,game JARs/assets,interpreter,GC,runtime andSDK stay
unchanged. Host occupancy controls pass; **PS5heap reservation and successful world
loading are still pending**. The exact063package is preserved;062remains the public
menu release. [Investigation and test guide](docs/client-world-064.md) ·
[063console evidence](docs/validation/client063-world-failure-2026-10-26.json) ·
[Current handoff](docs/handoff-prosperocraft-client064.md).

## Development063 — temporary controls and idle menu policy

Candidate **01.000.063** adds temporary DualSense keyboard/mouse translation
through normal SDL events: D-pad/left stick navigate menus, X selects, Circle goes
back, Triangle sends Tab, and Square sends Backspace. It retains buffered taps,
releases held inputs on interruption, and hands off when SDL gamepads initialize.
The raw gamepad driver remains available for the user's preferred future
[Controlify](https://github.com/isXander/Controlify) integration.

The harness sets vanilla `inactivityFpsLimit:"minimized"`, backing up existing
options and preserving other settings. This targets the AFK-related gradual idle
slowdown; measured full-GC stutter remains separate. Heap, interpreter, game JARs
and assets are unchanged. Host/native/package checks pass. The user subsequently confirmed controls work
and menu lag improved;demo-world loading failed separately with a recorded heapOOM.
The public release remains062.
[Controls and test guide](docs/client-controls-063.md) ·
[Build record](docs/validation/client063-build-2026-10-26.json) ·
[Current handoff](docs/handoff-prosperocraft-client063.md).

## First Minecraft Java menu on PS5 — 01.000.062

**The loading screen now leads to Minecraft's menu.** On 2026-10-26 the user
confirmed the visible menu on the actual PS5 using the exact 062 package.
This is the first confirmed menu checkpoint after the native dependency and
rendering milestones. The game JARs and 5,147 original assets remain unchanged.

[Download the release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Menu-v01.000.062) ·
[Install guide and what's tested](docs/releases/client-menu-062.md) ·
[Human console confirmation](docs/validation/client062-menu-confirmation-2026-10-26.json).

The release preserves the tested executable and includes complete hash-pinned
JAR **and asset** provisioning, checksums, and matching OpenAL source/relink materials.
Official downloaded game files are restored locally rather than redistributed.
The client shares PPSA99874 with the server and replaces that installation.

062 supplies OpenAL with the explicit game-data directory, avoiding the ambient
current-directory lookup where 061's trace stopped. The exact prior crash mechanism
is still unproven. [Technical change](docs/client-startup-062.md).
The menu report does not establish playable worlds, controller navigation, speaker
output, save/reload, shutdown or endurance. This GitHub release is scoped to menu
startup; it is not a formal full-client ALL PASS. No Store submission is included.

## Client SPIRV-Cross — PS5 ALL5 PASS

Client **01.000.036** passes all five checks on the actual PS5. Saved session
and detailed current-run reports confirm3contexts/9GLSL450-HLSL5-MSL translations,
exact source fingerprints,SSBO set0/binding0,push8/local64 reflection,malformed
SPIR-V error controls,384input guards,context cleanup and JVM shutdown.
The PS5 locale adapter reads the native decimal separator;game JARs and the
Java runtime implementation remain unchanged. Host GLSL/HLSL outputs independently
recompile and pass spirv-val;translated-shader GPU execution is not established.

[Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SPIRV_Cross) ·
[Release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_SPIRV_Cross-v01.000.036)

The next original Main attempt must combine the accepted SPIRV-Cross,VMA,
FreeType,STB,OpenGL and existing providers,including the supported ps5spvc library
configuration. **Combined Minecraft startup/window/menu remains unvalidated.**
Other shader features,MSL compiler validation,callbacks/concurrency/global teardown
and server two-hour endurance remain unvalidated;endurance stays deferred.
[Build details and limitations](docs/client-spvc-development.md).

## Client VMA Allocator — PS5 ALL5 PASS

Client **01.000.035** passes all five checks on the actual PS5. The matching
saved session and detailed current-run log confirm12RADV GPU transfers,
3allocator/device lifecycles,guards/controls and JVM shutdown.
The accepted fixture uses original VMA3.4.0/LWJGL3.4.3 JNI for12real copy/fill
transfers across3allocator/device lifecycles,two mapped65536-byte buffers each,
with exact output/source/guards,NEVER_ALLOCATE rejection and native cleanup.

[Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_VMA_Allocator) ·
[Release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_VMA_Allocator-v01.000.035)

This addresses the missing VMA component in034. SPIRV-Cross is now independently accepted in036;the combined
native configuration still needs an original Minecraft startup/menu test.
Images,custom pools/defragmentation/budgets/virtual allocations,callbacks,
concurrent/large workloads and full native teardown remain unvalidated.
Original game JARs remain unchanged;server endurance deferred.
[Build details and limitations](docs/client-vma-development.md).

## Client FreeType Fonts — PS5 ALL5 PASS

Client **01.000.033** passes all five checks on the actual PS5. The matching
saved session and detailed current-run log confirm FreeType glyphs/guards and
JVM shutdown. The accepted
fixture verifies three real FreeType2.14.1 library/face lifecycles,nine Abel
glyphs at16/24/32px plus exact repeat renders,an exact bitmap fingerprint,
metadata/metrics,invalid font/space controls and384input guards.

[Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_FreeType_Fonts) ·
[Release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_FreeType_Fonts-v01.000.033)

This addresses the missing FreeType component in032;original Minecraft startup
still needs another console test with the accepted native dependencies combined.
Other font formats/features,VMA,SPIRV-Cross,remaining SDL paths and full native
teardown remain unvalidated. Game JARs remain unchanged;server endurance deferred.
[Build details and limitations](docs/client-freetype-development.md).

## Client STB Codecs — PS5 ALL5 PASS

Client **01.000.031** passes all five checks on the actual PS5. The matching
saved session reports STB PNG/codecs/JVM stop. Its accepted fixture tests three
real PNG encode/read/decode/free cycles,768exact RGBA bytes,384input guards,
truncated PNG and invalid Vorbis rejection,Perlin/native structs and JVM shutdown.
The larger startup download is incomplete;per-cycle output was not independently
retrieved. This distinction is preserved in the validation record.

[Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_STB_Codecs) ·
[Release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_STB_Codecs-v01.000.031)

031resolves the native STB component missing in030. Minecraft startup remains
unvalidated;032 combined031STB with029OpenGL but stopped at missing FreeType. [Build scope and test instructions](docs/client-startup-032.md). Valid Vorbis decode,
font/resize/DXT/callback coverage,large/concurrent workloads and full native
cleanup remain unvalidated. All original game JARs stay intact;endurance deferred.

## Client OpenGL Provider — PS5 ALL5 PASS

Client **01.000.029** passes all five checks on the actual PS5. Saved reports
confirm three genuine Mesa softpipe/OpenGL JNI context lifecycles,192RGBA pixels,
768guard bytes and clean JVM shutdown. The PS5 dependency-loader repair is
validated for this workload;all54original game/Java JARs remain unchanged.

[Frozen source and validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_OpenGL_Provider) ·
[Release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_OpenGL_Provider-v01.000.029)

This is software OpenGL bootstrap acceptance;Minecraft startup,hardware OpenGL,
broader GL workloads and full native-module cleanup remain unvalidated. Vulkan
remains the intended game renderer. Continue development outside the frozen
snapshot;server two-hour endurance remains deferred.

## Client Callbacks/OpenAL — PS5 ALL5 PASS

Client **01.000.026** now passes all five checks on the actual PS5. Saved reports
confirm192native-to-Java callbacks across calling/native threads,three real
OpenAL loopback mixer/context lifecycles with verified440Hz PCM/guards/silence,
no-argument Vulkan loader/callback bootstrap and JVM shutdown. This establishes
native callback and in-memory mixer acceptance;**speaker output and Minecraft
startup/menu remain unvalidated**. Original game JARs remain unchanged.

[Frozen source/validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Callbacks_OpenAL) and the [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Callbacks_OpenAL-v01.000.026)
include app-only artifacts,local JAR provisioning and an OpenAL corresponding-
source/relink kit. The kit reproduces the exact native ELF and accepts a
compatible rebuilt OpenAL object. Continue game startup in development while
preserving this exact026 snapshot. Server two-hour endurance stays deferred.

## Client Continuous Direct Scene — PS5 ALL15 PASS

Human **“PASS”** for client **01.000.023** is now corroborated by saved reports
retrieved through Safari. Run `client-01.000.023-1792846440-446670267` confirms
494consecutive direct FIFO frames:1,482scene draws,17,784pixel samples,
126,464guard-byte checks,all3phases,physical event/state masks15 and JVM shutdown.
The renderer draws into each acquired SDL color attachment;it replaces022's
captured-scene upload/blit handoff. No fault marker or fixture failure was found
in the retrieved current run.

Exact tested source/package are preserved in
[Client_Continuous_Direct_Scene](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Continuous_Direct_Scene/README.md),with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Continuous_Direct_Scene-v01.000.023).
The original frozen validation remains unchanged. An additive
[log follow-up](docs/validation/client023-log-follow-up-2026-10-24.json) records
the later corroboration;raw logs stay local. Camera controls,index buffers,
larger workloads,Minecraft startup and full teardown remain ahead;endurance
stays deferred.

## Client Visible Perspective Scene — PS5 ALL15 PASS

Client **01.000.022** passes all fifteen checks; the user reports **“all pass.”**
Saved logs confirm real vertex-buffer/perspective texture rendering,27draws/
9full-image checks with depth/blend controls,295SDL FIFO frames with physical
event/state masks15,and JVM shutdown. The visible static panel uses the actual
verified GPU readback,uploaded once and blitted to the swapchain. This handoff
remains distinct from continuous scene rendering directly into the swapchain.

Exact tested source/package and evidence are frozen in
[Client_Visible_Perspective_Scene](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Visible_Perspective_Scene/README.md),with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Visible_Perspective_Scene-v01.000.022)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Visible_Perspective_Scene/validation.json).
Continuous/direct rendering,camera movement,index buffers,larger workloads,
Minecraft startup and full native teardown remain ahead; endurance stays deferred.

## Client Texture,Depth and Blending — PS5 ALL14 PASS

Client **01.000.021** passes all fourteen checks; the user reports **“nice pass!”**
Retrieved logs confirm three real texture uploads,27draws and9full-image/guard
checks with depth-disabled and blend-disabled controls,followed by318SDL frames,
physical event/state masks15 and JVM shutdown. Runtime shader compilation also
continues to pass. The texture workload is offscreen; visible tiles remain the
existing SDL baseline.

Exact tested source/package and evidence are frozen in
[Client_Texture_Depth_Blend](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Texture_Depth_Blend/README.md),with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Texture_Depth_Blend-v01.000.021)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Texture_Depth_Blend/validation.json). A visible
textured scene,perspective/vertex buffers,larger workloads,game startup and full
native teardown remain ahead; server two-hour endurance stays deferred.

## Client Runtime Shader Compilation — PS5 ALL13 PASS

Client **01.000.020** passes all thirteen checks on PS5; the user reports
**“nice pass!”** Retrieved logs confirm three actual shaderc GLSL compilation
cycles with invalid-source diagnostic controls, runtime SPIR-V sizes1392/1000/
1392bytes,18 RADV output/guard workloads,252 SDL graphics/FIFO frames with physical
DualSense event/state masks15 and successful JVM shutdown. The app C++ allocation
route repair is validated for this workload; no game/Java JAR was modified.

Exact tested source, package and evidence are preserved in
[Client_Runtime_Shader](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Runtime_Shader/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Runtime_Shader-v01.000.020)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Runtime_Shader/validation.json). Native display
resources remain retained until app close. Textures/depth/blending, larger shader
workloads/includes/callbacks/HLSL, game startup, global teardown and server
endurance require separate validation.

## Client SDL Window/Input — PS5 automated, input and visual PASS

Client **01.000.014** passes all twelve checks on PS5. The user confirms
**“tiles nice, inputs all accepted.”** Retrieved reports verify physical
DualSense events and polled state for X/Circle/D-pad Left/left stick,537 rendered
frames with sample/guard checks, and DestroyJavaVM. Actual SDL3 PS5 video and
Vulkan surface hooks are exercised through original LWJGL SDL bindings. Tested
source/package are frozen as [Client_SDL_Window_Input](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SDL_Window_Input/README.md),
with a [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_SDL_Window_Input-v01.000.014)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SDL_Window_Input/validation.json).

SDL/native display resources remain retained until app close. Teardown/resize/
reconnect/focus, audio/callbacks, keyboard/mouse mapping and Minecraft startup
remain unvalidated. Original game/SDL/Vulkan JARs and JVM/SDK are unchanged;
prior passing snapshots are preserved. Server two-hour endurance stays deferred.

## Client Direct Presentation — PS5 automated and visual PASS

Client **01.000.011** passes all twelve automatic checks on PS5, and the user
explicitly confirms the full-screen result: **“PASS by notification and pass by
my eyes.”** Retrieved reports verify90 ordered graphics/FIFO presents, sampled
pixels/guards and DestroyJavaVM. Original LWJGL display/surface/swapchain calls
now drive actual RADV/VideoOut without the CPU display owner. The tested source
and exact package are frozen as [Client_Direct_Presentation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Direct_Presentation/README.md),
with a [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Direct_Presentation-v01.000.011)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Direct_Presentation/validation.json).

The display context remains alive until app close, preserving the final image
after JVM shutdown. Teardown/handoff/resize/recovery, SDL window/input and
Minecraft startup remain unvalidated. Original game/Vulkan JARs and runtime
implementation/SDK are unchanged; earlier frozen packages remain preserved.
Server two-hour endurance stays deferred.

## Client Graphics Pipeline — PS5 ALL PASS

The user reports **ALL PASS** for client **01.000.010** on **2026-10-24**, after
the twelve-row and colored-preview acceptance instructions. Retrieved PS5 logs
confirm nine actual vertex/fragment graphics draws, all256x256 pixels and guards,
three graphics lifecycles, readback publication and DestroyJavaVM. The source and
exact package are frozen as [Client_Graphics_Pipeline](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Graphics_Pipeline/README.md),
with a [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Graphics_Pipeline-v01.000.010)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Graphics_Pipeline/validation.json).

The preview displays actual GPU-readback bytes through the existing CPU menu.
SDL/window, Java-owned GPU swapchain presentation and Minecraft startup remain
ahead. Original game/Vulkan JARs and runtime implementation/SDK are unchanged;
frozen000–004 and008–009 remain preserved. Server endurance stays deferred.

## Client Shader Pipeline — PS5 ALL PASS

All eleven rows of client **01.000.009** pass on PS5, confirmed on **2026-10-24**.
Retrieved logs verify18 real compute-shader dispatches, every output/guard word,
three shader/device lifecycles and DestroyJavaVM. Original LWJGL Vulkan bindings
create the descriptors, push constants and pipeline; RADV compiles and executes
the shader on the PS5 GPU. The tested source/package are frozen as
[Client_Shader_Pipeline](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Shader_Pipeline/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Shader_Pipeline-v01.000.009)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Shader_Pipeline/validation.json).

This is offscreen compute. SDL/window integration, visible graphics/fragment
rendering, Java display presentation and Minecraft startup remain ahead.
Original game/Vulkan JARs and runtime implementation/SDK are unchanged.
Frozen000–004 and008 remain preserved; server endurance stays deferred.

## Client Vulkan Bindings — PS5 ALL PASS

All ten rows of client **01.000.008** pass on PS5, confirmed on **2026-10-24**.
Retrieved logs verify12 standard LWJGL Vulkan GPU transfers, three instance/device
lifecycles, loader cleanup and DestroyJavaVM. The original LWJGL Vulkan JAR now
uses actual RADV commands through its upstream structs and capability tables.
The source and exact tested package are frozen as
[Client_Vulkan_Bindings](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Vulkan_Bindings/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Vulkan_Bindings-v01.000.008)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Vulkan_Bindings/validation.json).

Bounded diagnostic history and sampled tracing also resolve the observed startup
storage failure in this run. Original game/Vulkan JARs, the runtime JVM and SDK
remain unchanged; the runtime adds opt-in diagnostic probe support. Frozen000–004
are preserved. Complete Vulkan coverage, SDL/window integration, Java presentation,
shaders and Minecraft startup remain ahead. Server endurance stays deferred.

## Client GPU Integration — PS5 ALL PASS

The user confirms **all nine rows of client01.000.004 pass on the actual PS5**
on 2026-10-23. The source and matching package are frozen as
[Client_GPU_Integration](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_GPU_Integration/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_GPU_Integration-v01.000.004)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_GPU_Integration/validation.json).

Java25 and actual LWJGL native buffers now drive RADV offscreen GPU copy/fill/
readback through a real JNI bridge. Java result/guard checks, error controls,
three Vulkan create/destroy cycles and final JVM shutdown pass. This is a narrow
fixture; full LWJGL Vulkan bindings, SDL/window integration, shader rendering
and Minecraft's menu remain ahead. Frozen000–003 packages stay preserved;
server endurance stays deferred. [Technical details](docs/client-gpu-integration-004.md).

## Client Native Graphics — PS5 ALL PASS

The human tester confirms client **01.000.003** displayed the RGB sequence and
legible result card with no crash or corruption on 2026-10-23. The source and
exact compiled package are frozen as [Client_Native_Graphics](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Graphics/README.md),
with a [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Native_Graphics-v01.000.003)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Graphics/validation.json).

The native Mesa/RADV path now performs GPU clear/copy/readback and VideoOut
presentation on PS5. This standalone test launches no Java, SDL, shaders or game.
Java002/LWJGL remains a separate passing baseline. The004 offscreen integration now passes; shader
rendering and Minecraft's menu remain ahead; server endurance stays deferred.
[Technical details and run instructions](docs/client-native-graphics-003.md).

## Client LWJGL Core — PS5 ALL PASS

All eight rows of client **01.000.002** pass on the actual PS5, confirmed by
the human tester on 2026-10-23. The matching source and package are frozen as
[Client_LWJGL_Core](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_LWJGL_Core/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_LWJGL_Core-v01.000.002)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_LWJGL_Core/validation.json).

Actual upstream LWJGL native memory/JNI operations and the PS5 resident function
provider now pass alongside the earlier runtime/JNI checks. The official game
JAR stays unchanged. Full Vulkan bindings, SDL/window integration
and Minecraft's menu remain ahead. Earlier frozen packages are preserved;
server two-hour endurance remains deferred. [Technical details](docs/client-lwjgl-core-002.md).

## Client Native Loading — PS5 ALL PASS

The user confirms all seven rows of client `01.000.001` passed on the actual PS5
on2026-10-22. The source and matching package are frozen as
[Client_Native_Loading](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Loading/README.md), with a
[release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Native_Loading-v01.000.001)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Loading/validation.json).

Standard JNI loading, OnLoad/discovery and scoped real native-function calls now
pass in this consumer probe. Full LWJGL native bindings, SDL/Vulkan presentation
and Minecraft's menu are still ahead. The earlier foundation and server packages
remain preserved; two-hour server endurance remains pending.

## Client Foundation — PS5 ALL PASS

The user confirms all six rows of Client Foundation `01.000.000` passed on the
actual PS5 on2026-10-22. The matching source and package are frozen as
[Client_Foundation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Foundation/README.md), with a
[release download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Foundation-v01.000.000)
and [validation record](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Foundation/validation.json).

This establishes runtime/artifact loading, explicit LWJGL PS5 platform handling,
real JNI direct-buffer handoff and VM shutdown. Native loading, SDL/Vulkan
presentation and Minecraft's menu/world remain next. Server endurance remains
pending. The client shares `PPSA99874` and starts its own build counter at zero.

## Fabric and Paper release

[Fabric and Paper running on PS5 — Fabric094 / Paper108](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Fabric-Paper-v01.000.108)
is the new full release, with separate app-only downloads, checksums
and local provisioning instructions. The user reports a satisfying Fabric
experience and describes Paper108 as the best build yet. See the
[release notes and setup](docs/releases/fabric-paper-108.md).

The two-hour run remains pending. The user has authorized moving into client
work; full server lifecycle acceptance remains tracked separately. No new
ALL PASS or playable client is claimed.

## Roadmap

### 1 · Prove the server foundation

- [x] Validate the Java runtime's TCP/UDP loopback and NIO selector probes on PS5.
- [x] Validate outbound Java LAN TCP/UDP and forward DNS on PS5.
- [x] Validate inbound LAN and multi-JAR/system class-path loading on PS5.
- [x] Pin official Minecraft 26.3 / Java 25 artifacts and inventory its 40 JARs.
- [x] Verify the inventory and official `--help` entry point on the host.
- [x] Pass the first Minecraft server bootstrap probe on PS5.
- [x] Launch a vanilla dedicated server and reach a ready state (observed in build057; the run then crashed during the save path).
- [x] Start a flat test world, save metadata and stop cleanly (build058 ALL PASS).
- [ ] Complete migration to the original signed server JAR and validate it on PS5.
- [ ] Reload a saved world and verify persistence.
- [ ] Connect from another device and verify sustained ticks and clean shutdown.

### 2 · Validate server mods

- [ ] Complete the unmodified-server baseline, save/rejoin checks and two-hour run.
- [x] Pin separate Fabric0.19.5 and Paper26.3build207 distributions; retain isolated worlds.
- [ ] Validate Paper startup, joining, plugin lifecycle and save/rejoin/stop on PS5.
- [x] Publish the Fabric094/Paper108 full release with qualified console feedback.
- [ ] Complete formal lifecycle/endurance acceptance before a new frozen ALL PASS release.
- [ ] Run individual server-side mods and verify joins, persistence, memory and latency.
- [ ] Publish exact tested loader/mod versions and reproducible results before larger sets.

### 3 · Bring up the client (authorized 2026-10-22; server endurance pending)

[Client bring-up status and commands](docs/client-bringup.md): official26.3 client
and53 Java libraries are pinned; actual host class preflight passes without
native initialization. Upstream LWJGL rejects the PS5 platform; the new source-built dependency port
adds explicit PS5/x64 identification. Its console foundation probe has
passed all six rows on PS5; native SDL/Vulkan integration remains ahead. No PS5 client launch is claimed.

- [x] Pin client artifacts and asset index; add isolated preparation and real-JVM class preflight.
- [x] Build a Client Foundation probe (`PPSA99874`,01.000.000): explicit LWJGL PS5 platform port and real JNI direct-buffer handoff; host/package checks pass.
- [x] Validate all six client-foundation rows on PS5:01.000.000 ALL PASS, frozen source/package and release (not a game/menu/graphics test).
- [x] Validate client001 resident JNI loading/scoped function lookup on PS5: all seven rows pass; source/package frozen.
- [x] Validate client002 actual LWJGL native memory/JNI core and PS5 resident provider on PS5: all eight rows pass; source/package frozen.

The client reuses server title `PPSA99874` at the user's request. Installing
the client replaces the server app; tested server packages remain preserved.


- [ ] Port native bindings and window/input interfaces for the selected client.
- [x] Validate the pinned PS5_Vulkan/Mesa RADV GPU clear/copy/readback and VideoOut path on PS5: native003 ALL PASS, source/package frozen.
- [ ] Integrate the validated native graphics path with Java/LWJGL, SDL and a shader renderer.
- [ ] Establish graphics/audio, reach the menu and load a vanilla test world.
- [ ] Add usable controller navigation/gameplay and measure console performance.

## First server bootstrap probe

**Passing snapshot:** `PPSA99874`, version `01.000.002`. [Frozen source](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Bootstrap/server/native/bootstrap.cpp) · [Pinned artifacts](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Bootstrap/server/26.3.lock.json) · [Validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Bootstrap/validation.json)

Run all five rows in order:

1. Initialize the embedded Java runtime.
2. Create the Java 25 interpreter VM (128 MiB maximum heap).
3. Verify all 40 official JAR hashes, the server’s Java 25 bytecode and representative dependency/module classes.
4. Invoke the real, unmodified Minecraft 26.3 `net.minecraft.server.Main --help` and check its option-parser output.
5. Destroy the VM.

No Mac networking helper is needed. This build does not accept the EULA, generate a world, listen for players or establish server tick performance. Long exception messages wrap and support D-pad left/right paging.

The official server bundle is downloaded from Mojang’s metadata-pinned URL. Its SHA-1, size and SHA-256 are checked; each contained library/server JAR is checked against the bundle’s SHA-256 inventory. Game files remain in ignored caches and local packages, rather than source commits. See the [official 26.3 release](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3).

## Current development: Paper timestamp candidate 01.000.108

The user reports 108 is much more than acceptable and by far the best build yet.
This is positive console playtest feedback; full validation and the two-hour run
remain pending. No frozen milestone or release has been created.

107 gets past optional extended attributes, then terminates at the timestamp
update during configuration copying. No current fatal report identifies the
exact native cause. See [evidence and validation](docs/paper-timestamp-crash-107.md).

108 routes ordinary PS5 file timestamps through the SDK's resident futimes and
utimes APIs. Real errors propagate; unsupported directory-descriptor/no-follow
modes fail explicitly. Timestamp precision is microseconds. Actual JNI/JVM tests
and the target library build pass; console availability remains unverified.
All game/probe/plugin JARs, Java module image and HotSpot remain unchanged.

Try CreateVM, VerifyJARs, then Play. Paper readiness, plugins, joined gameplay,
save/stop/reload and native-pressure stability remain pending. Circle requests
save/stop once running; reopen after expected app exit for logs. Full two-hour
test stays deferred. Fabric/Paper full release is published; client work
is now authorized while remaining server validation stays pending.


072captured a null function call through its new OS-random service import.
073fixes that concrete runtime failure using checked kernel entropy queries,
including return/count validation and a missing-API guard. The existing harness
and game derivative are unchanged. Actual PS5 kernel RNG/TLS/server startup and
the earlier071cause remain pending.


Build071failed before Minecraft initialization, during the first HTTPS/TLS setup.
072repairs the observed Unix-device entropy fallback by using the real PS5 OS
random service and adds explicit DRBG/TLS-factory gates. The exact process-crash
cause remains unresolved; all072console validation is pending. The existing
server derivative has no further bytecode changes in072.


Build070 crashed after respawn: the VM thread could not allocate4088native bytes
during GC, and even the minimum16KiB fallback mapping failed. Build071 reduces
native allocation bookkeeping and compresses the resident Java module image
(65562247 to28170800bytes) while retaining all modules. It enables Java25 compact
object headers and uses a176MiB heap, guarded C1 and SerialGC NewRatio7.
These changes require PS5 validation; they do not establish optimal latency.

The new normal terrain world, with structures, lives at
`/download0/mc-server-start/world-normal-v1`. The previous flat `world` folder is
preserved. View distance is4chunks and simulation distance3; the configured
player limit is20. Twenty-player capacity has not been tested. Online
authentication and the whitelist remain enabled. The explicitly requested
operator policy grants level4OP to all admitted whitelisted accounts through
vanilla APIs, preserving the20-player limit. Use `/gamemode creative` to avoid
mob damage, or `/difficulty peaceful` to remove hostile mobs.

The rows initialize/create the VM, verify upstream artifacts and actual C1
results, then start and monitor tick progress/saves. Paper exits the JVM when
it stops; its checked shutdown closes the app rather than completing a separate
DestroyJavaVM row. Reopen it for reports. The7200-second timer starts at the real `Done` readiness message, with checks
every30seconds and flushed saves every300seconds. A short gameplay/respawn check
comes before a full run. Follow the [endurance instructions](docs/endurance.md).
The human's EULA acceptance is [recorded](server/eula-consent.json). The frozen
[Server_Start058](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Start) snapshot remains the last passing milestone;
Fabric satisfaction is reported after094. Paper100 is pending actualPS5 validation; no new frozen milestone or completed two-hour run is claimed.

### Build and verify

With the pinned Java port/toolchain available:

```sh
python3 tools/package_server_probe.py --runtime-workspace /path/to/PS5_Homebrew --join-player YOUR_ACCOUNT --flavor paper
python3 tools/test_server_start.py --flavor paper --c1 --heap-mib 384 --chunk-radius 2 --endurance-seconds 60
```

The preparation script creates the class-path header and external probe specification under `build/`. The Java repository supplies the reusable runtime builder and extra target-built Java modules. No host native binaries are included. Optional module natives and server-specific native dependencies still need console validation.

Install the complete `PPSA99874` folder from the generated ZIP through ShadowLoader. Keep any existing app closed while replacing files.

## Milestones & releases

| Minecraft milestone | Console result | Snapshot | Release |
| :--- | :--- | :--- | :--- |
| **Playable world · 01.000.066** | Human playable world/major speed improvement,~30secstartup;C1gate/joinreports | [Scope/setup](docs/releases/client-playable-066.md) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Playable-v01.000.066) |
| **First world · 01.000.065** | Human world entry/punching,joined/rendered reports;severe lag and movement failure | [Scope/setup](docs/releases/client-world-065.md) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_World-v01.000.065) |
| **First Minecraft menu · 01.000.062** | Human-confirmed visible menu on actual PS5 / native Java 25; gameplay and stability pending | [Evidence & setup](docs/releases/client-menu-062.md) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Menu-v01.000.062) |
| **Client Launcher/Lifecycle · 01.000.082** | Human ALL PASS for requested checkbox/navigation, native stick, focus animation and Quit→library→relaunch fixes; no measured endurance claim | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Launcher_Lifecycle) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.082) |
| **Client SPIRV-Cross · 01.000.036** | PS5 ALL5 PASS,saved reports:9shader translations/reflection/error controls/guards and JVM stop | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SPIRV_Cross) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_SPIRV_Cross-v01.000.036) |
| **Client VMA Allocator · 01.000.035** | PS5 ALL5 PASS,human+saved reports:12RADV transfers,3VMA allocator/device cycles,guards and JVM stop | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_VMA_Allocator) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_VMA_Allocator-v01.000.035) |
| **Client FreeType Fonts · 01.000.033** | PS5 ALL5 PASS,human+saved reports:real FreeType glyph rasterization/guards and JVM stop | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_FreeType_Fonts) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_FreeType_Fonts-v01.000.033) |
| **Client STB Codecs · 01.000.031** | PS5 ALL5 PASS,human+saved session:real PNG/codecs/guards and JVM stop;detailed startup download incomplete | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_STB_Codecs) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_STB_Codecs-v01.000.031) |
| **Client OpenGL Provider · 01.000.029** | PS5 ALL5 PASS:3real software GL contexts,192RGBA pixels,768guards and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_OpenGL_Provider) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_OpenGL_Provider-v01.000.029) |
| **Client Callbacks/OpenAL · 01.000.026** | PS5 ALL5 PASS:192callbacks,3real loopback mixer lifecycles,Vulkan native bootstrap and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Callbacks_OpenAL) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Callbacks_OpenAL-v01.000.026) |
| **Client Continuous Direct Scene · 01.000.023** | PS5 ALL15 PASS:494direct FIFO frames/1,482draws,all3phases,input masks15 and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Continuous_Direct_Scene) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Continuous_Direct_Scene-v01.000.023) |
| **Client Visible Perspective Scene · 01.000.022** | PS5 ALL15 PASS:vertex-buffer perspective scene,verified image handoff,295SDL FIFO frames/input and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Visible_Perspective_Scene) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Visible_Perspective_Scene-v01.000.022) |
| **Client Texture/Depth/Blend · 01.000.021** | PS5 ALL14 PASS:3texture uploads,27draws/9full images+guards,depth/blend controls,SDL318frames and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Texture_Depth_Blend) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Texture_Depth_Blend-v01.000.021) |
| **Client Runtime Shader · 01.000.020** | PS5 ALL13 PASS: real runtime GLSL/error controls,18 GPU outputs,SDL input/display252frames and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Runtime_Shader) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Runtime_Shader-v01.000.020) |
| **Client SDL Window/Input · 01.000.014** | PS5 automated/input/visual PASS: actual SDL window/surface, physical gamepad events+state,537 GPU frames and JVM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SDL_Window_Input) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_SDL_Window_Input-v01.000.014) |
| **Client Direct Presentation · 01.000.011** | PS5 automated and visual PASS:90 direct GPU/FIFO presents, sample/guard checks and JVM shutdown with retained display | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Direct_Presentation) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Direct_Presentation-v01.000.011) |
| **Client Graphics Pipeline · 01.000.010** | ALL PASS on PS5:9 graphics draws, verified pixels/guards, GPU-readback CPU-menu preview and VM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Graphics_Pipeline) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Graphics_Pipeline-v01.000.010) |
| **Client Shader Pipeline · 01.000.009** | ALL PASS on PS5:18 compute dispatches, guarded readback,3 shader lifecycles and VM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Shader_Pipeline) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Shader_Pipeline-v01.000.009) |
| **Client Vulkan Bindings · 01.000.008** | ALL PASS on PS5: original LWJGL Vulkan commands,12 GPU transfers,3 lifecycles and VM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Vulkan_Bindings) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Vulkan_Bindings-v01.000.008) |
| **Client GPU Integration · 01.000.004** | ALL PASS on PS5: Java/LWJGL GPU copy/fill/readback, three Vulkan session cycles and VM shutdown | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_GPU_Integration) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_GPU_Integration-v01.000.004) |
| **Client Native Graphics · 01.000.003** | ALL PASS on PS5: RADV GPU clear/copy/readback and VideoOut presentation | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Graphics) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Native_Graphics-v01.000.003) |
| **Client LWJGL Core · 01.000.002** | ALL PASS on PS5: native memory/JNI core and resident function provider | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_LWJGL_Core) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_LWJGL_Core-v01.000.002) |
| **Client Native Loading · 01.000.001** | ALL PASS on PS5: standard JNI loading and scoped real-function calls | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Loading) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Native_Loading-v01.000.001) |
| **Client Foundation · 01.000.000** | ALL PASS on PS5: runtime, artifacts, platform and JNI buffers | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Foundation) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Foundation-v01.000.000) |
| **Server Start · 01.000.058** | ALL PASS on PS5: real readiness, saved metadata, clean stop and VM lifecycle | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Start) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Server_Start-v01.000.058) |
| **Server Bootstrap · 01.000.002** | ALL PASS on PS5 13.60: VM lifecycle, 40-JAR preflight and official server `--help` | [Frozen source & validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Bootstrap) | [Download](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Server_Bootstrap-v01.000.002) |

The public release contains the console-tested app/runtime, with official game/dependency JARs excluded. To provision those, run `tools/prepare_server.py --runtime-workspace /path/to/PS5_Homebrew`, then copy the generated `build/assets/java25/jars/` into the extracted app's `assets/java25/jars/`. The regular packaging command above produces the full local app automatically. Exact full-package and release-asset hashes are recorded separately in [Server_Start validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Start/validation.json) and [bootstrap validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Bootstrap/validation.json).

Earlier build failures remain recorded in [console results](server/console-results.json). The bootstrap snapshot establishes help only; Server_Start adds readiness and save/stop. Saved-world reload, player joins and sustained ticks are next.

## Follow the project

Runtime fixes and reusable tools are published to [ps5-java25-homebrew](https://github.com/mateo-cogeanu/ps5-java25-homebrew). Minecraft harnesses, artifact pins, preparation scripts and console results are published here. The current development probe attempts real server startup/save/stop with PS5 diagnostic compatibility; client and mod work follow their own prerequisites.

Build 01.000.007 reached block/registry initialization and reported an
OutOfMemoryError from the legacy verifier while checking JOML Matrix3f,
plus a separate logging configuration lookup failure. Build 01.000.008
uses an explicit 8 MiB code-cache reservation in interpreter mode, loads
the logging XML through the probe JAR URL, and includes native verifier
failure-site/errno/JNI-state diagnostics and Java heap counters. The host
server reaches ready/save/stop with about 1 MiB of code cache used. The
PS5 failure is not yet confirmed resolved.


## Download diagnostic logs (01.000.009)

Keep the probe open and visit **`http://<PS5-IP>:8765/`** from a browser on the
same LAN. Use the console's current IPv4 address; none is compiled into the app.
The menu shows listener status. This native service runs independently of the JVM
and serves the app's own files, avoiding FTP sandbox access restrictions. It stays
available while the server test is running. After a process crash, relaunch and
download the saved logs before running a new test.

Download **Startup log**, **Native VM trace**, **Full Minecraft console**,
**Last JVM abort**, and **Latest probe exception** as available. The Minecraft
console file is replaced per server attempt and capped at 32 MiB with an explicit
marker; the existing on-screen report remains bounded. Other logs retain their
existing append/truncation behavior. Missing files return 404.

To collect a ZIP with checksums, use the Java runtime workspace helper:

```sh
python3 /path/to/PS5_Homebrew/tools/fetch_probe_logs.py <PS5-IP> --output probe-logs.zip
```

The read-only page exposes only named logs, with no file browser, upload or
commands. It is unencrypted LAN access without authentication; keep it on the
intended network and do not forward port 8765. Nothing is uploaded automatically.
See the [runtime log-sharing documentation](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/main/Development/docs/probe-log-sharing.md).

The downloaded 01.000.008 startup log confirms native verifier allocation failure
at site 3586 with no pending JNI exception, and a missing native `management`
library. These remain unresolved in 01.000.009; this build improves collection.
**PS5 log downloads and server readiness/save/stop remain pending.**


Build **01.000.009 log sharing is confirmed working by the user**; the downloaded
console identifies native verifier scratch allocation failure during
`Matrix3f.rotateLocal`, with 58,800,432 Java heap bytes still free. Build
**01.000.010** includes the Java port's PS5-only method-scratch lifetime fix:
non-root verifier scratch blocks are released at each method reset instead of
retaining oversized allocations until class verification finishes. All bytecode
checks remain active. The patched complete verifier validates Matrix3f, Matrix4f
and Quaternionf through host JNI, and a constrained allocator sanitizer test
passes 600 methods where the original retention exhausts its budget. The packaged
target library was rebuilt and verified byte-for-byte.

This addresses a demonstrated native allocation pattern; **PS5 resolution is
pending**. The missing native management library and unsupported optional OS
telemetry are separate remaining issues. No ready server or world save on PS5 is
claimed. Log sharing remains available on port 8765 in this build.


The 01.000.010 console logs show progress past Matrix3f verification, followed
by another native scratch allocation failure in `MemUtil$MemUtilNIO.copy4x4`
(site 3600, no pending JNI exception), with 58,020,336 Java heap bytes free.
Build **01.000.011** keeps method scratch cleanup and adds a PS5-only fallback:
if libc refuses a verifier pool block, request real anonymous read/write OS pages.
Each block records its allocation backend and is released with `free` or `munmap`
as appropriate. If both backends fail, the verifier still reports OOM; no checks
are bypassed. The startup log records requested bytes, malloc errno, mapped bytes
and mmap errno for fallback attempts, even with verbose native tracing disabled.

Host sanitizer checks cover forced heap rejection, writable real mappings,
matching cleanup and both-backend exhaustion. The complete patched verifier
checks the actual MemUtilNIO class as well as Matrix3f, Matrix4f and Quaternionf.
The target library was rebuilt and verified against the packaged copy.
**PS5 validation is pending.** Management-library and OS-telemetry warnings remain
separate unresolved issues; the server has not yet reached ready on PS5.


## Current fixes in 01.000.012

- **JVM management:** the real target `libmanagement` is embedded and connected
  to HotSpot's management interface. Preflight now queries actual heap/non-heap
  memory and VM input flags rather than only resolving the class name.
- **Verifier memory:** the method scratch cleanup and real OS-page allocation
  fallback from 01.000.011 remain included, with allocation diagnostics in the
  startup log. Console confirmation is still required.
- **PS5 system reports:** unsupported OSHI hardware/software readings are marked
  explicitly unavailable. The accurate PS5 OS identity and real JVM memory/flags
  are retained; no physical hardware readings are invented or warnings globally
  hidden. Full OSHI support is not claimed.

The last item is a narrowly scoped **Minecraft diagnostic adaptation**. The
original signed server JAR remains unchanged and hash-verified. A separate local
unsigned derivative executes with only the two optional `SystemReport` telemetry
methods adapted; every other server class/resource is byte-identical. Original
desktop behavior is retained. No global signature checks are disabled. The
execution artifact is therefore not described as an unmodified signed server.
See [scope, provenance, and validation](docs/platform-diagnostics.md). Generated
game artifacts, including the diagnostic derivative, are not committed or
published as binary release assets. The frozen bootstrap release is unchanged.

Host management, diagnostic adaptation, restricted-module preflight/help, and
real server readiness/save/stop checks pass. **PS5 testing remains pending** for
management, the verifier fallback and real server ready/save/stop. Use the log
page on port 8765 to collect results after the attempt.


## Class loading and log identity in 01.000.013

The latest console attempt reached MobEffects initialization, then reported a
bare OOM through `ClassLoader.defineClass1`. Its startup tail ended in VM ABORT;
the supplied exception file still described the older MemUtilNIO attempt.
Build **01.000.013** adds PS5-only native class-byte/UTF scratch allocation
fallback to real anonymous RW pages, with matching backend cleanup. Bytecode
checks and JVM definition entry points remain unchanged. Startup diagnostics
record allocation sizes/results and distinguish failure after entering the JVM.
The exact origin of the console OOM remains unproven until this build is tested.

The log page now separates **Open app build** (`build.txt`) from **Recorded run
status** (`session.txt`). Relaunching preserves the failed run's logs; these
identifiers can differ after a crash. Initializing a new run archives the prior
exception, VM abort and server output before writing current-run placeholders.
Prior reports have their own download links. Archive failure preserves the
current source report and is recorded in session status. Startup history has
explicit build/run markers, and the ZIP collector includes build/session files.

The actual native class-loader host test loads and executes classes using heap
and forced mapping paths, exercises hidden/direct definitions and long UTF
sources, and checks cleanup after malformed input, invalid ranges and real OOM.
Log archive/collector checks also pass. **PS5 validation and real server readiness
remain pending.** If it aborts again, include `abort.txt`, `session.txt`,
`startup.log` and `server.log`; the current exception file may correctly state
that no Java exception was captured before the process aborted.

## Native worker in 01.000.014

The user confirms build 013 exits the whole app during row 4. Its latest startup log shows successful class-byte scratch mappings, but no current abort report, server output or console crash code. Those mappings do not identify what terminated the app.

Build **01.000.014** moves the long JNI call off the UI thread and supplies a dedicated 8 MiB pthread stack. The worker attaches to the existing VM and owns its `JNIEnv`; the creating thread keeps its own environment. The Java fixture sets the system context class loader before server initialization. The UI hides worker-written result/exception buffers until completion and join, then enables subsequent tests. It shows elapsed seconds once per second while the worker is active. Read-only log sharing on port 8765 remains available.

The actual server fixture reaches `Done`, saves `world/level.dat` and stops on a native-attached host worker at 192 MiB; the main loop continues during that test. Target linking, package integrity and library/JAR identity checks also pass. **PS5 validation is pending.** This change addresses UI blocking and stack ownership, but does not establish the original crash cause or isolate native fatal errors from the process.

For the attached-worker host regression, first build the fixture runner with `python3 tools/test_jni_worker.py` in the runtime workspace, then run here:

```sh
python3 tools/test_server_start.py --worker-runner /path/to/PS5_Homebrew/build/java25/jni-worker-test/jni-worker-check
```

Build 014 console follow-up: the user reports a whole-app crash at 19 seconds. Retrieved logs confirm worker attachment and contain a current signal 11 record matching the 014 handler address. The server console is empty, the current exception remains a placeholder and the abort endpoint is unavailable. The exact native fault site remains unresolved; this build has **not** passed startup/save/stop on PS5. Raw diagnostic files remain local.

## Native crash capture in 01.000.015

Build **01.000.015** repairs the missing native-call evidence in row 4. The harness previously disabled call tracing before invoking the server. It now uses quiet mode: caller, pointers, byte count and completion status remain in memory without per-call disk writes. Allocation wrappers also cover calloc, realloc and free while preserving the original functions.

The runtime stores call/stage/recursion state separately for each thread in a preallocated table. This prevents cross-thread overwrites without using allocating emulated TLS in an allocator wrapper or signal handler. Table exhaustion suppresses new capture and leaves existing records intact. The attached worker, live elapsed counter and read-only log sharing remain.

Host sanitizer tests, target code checks, the HotSpot rebuild and package integrity checks pass. **The underlying build 014 SIGSEGV is still unresolved; build 015 is awaiting PS5 validation.** It does not claim a completed native crash fix. Repeat the test sequence, then leave the probe open on its menu after relaunch so the current logs can be retrieved.

Build 015 console follow-up: quiet capture now records a completed 128-byte native malloc returning null. The retained caller resolves to HotSpot `os::malloc` in the matching 015 ELF. The same subsequent SIGSEGV remains, with no Java exception and an empty server console. This identifies an allocation failure, but does not establish the reason it failed or the later faulting instruction. Actual server startup/save/stop has not passed.

## Native allocation fallback in 01.000.016

Build **01.000.016** includes a Java runtime fix for the confirmed failed 128-byte HotSpot allocation. When libc refuses native storage, HotSpot now falls back to real writable anonymous OS pages. Small allocations share mappings through eight size classes; larger ones use direct mappings. Backend-aware resize/free preserves existing bytes on failure and releases mappings when no longer needed. The raw storage prefix also covers early NMT allocations so they remain compatible after initialization. Existing native-memory tracking checks and the 192 MiB Java heap setting remain.

The actual allocator passes sanitizer tests with forced failures, resize migration, alignment, pooled sharing, concurrency and complete cleanup. The actual HotSpot API bodies also pass checks against a narrow NMT contract model, including failed-resize header revival and allocation limits. Target rebuild and package/library identity checks pass. **PS5 validation is pending:** this addresses the observed allocation failure, but does not yet prove the subsequent SIGSEGV or server startup/save/stop is resolved.

## Bulk file-I/O buffer fallback in 01.000.017

Build 016 logs confirm successful HotSpot native-page fallbacks, then report
`OutOfMemoryError` in `RandomAccessFile.readBytes0` while loading a dependency
JAR. Its trace has no captured signal record and no abort report; this does not
prove the prior native crash is resolved. Server readiness/save/stop has not passed.

Build **01.000.017** consumes a separate Java runtime fix for bulk file-read/write
temporary buffers: libc first, then real writable OS pages, with matching
cleanup even after partial writes and exceptions. Both allocation failures
still produce the original error. JNI/UBSan host checks and target/package
checks are recorded in [build status](server/build-status.json).
**PS5 validation of build 017 remains pending.**

## Native platform strings in 01.000.018

Build 017 confirms the file-I/O mapping fallback works, then fails in
`FileInputStream.open0` while Java logging loads its configuration. The error
"requested array size exceeds VM limit" comes from a failed native platform-string
allocation and can occur for a normal-sized path. Build **01.000.018** consumes
the Java runtime's platform-string fallback: libc first, then real OS pages,
with matched normal/error cleanup and unchanged encoding/NUL checks.
The JNI/UBSan host checks and target/package validation are recorded in
[build status](server/build-status.json). **PS5 validation remains pending**;
no successful world readiness/save/stop or resolution of prior native crashes
is claimed.

## Verifier class-hash memory in 01.000.019

Build 018 logs confirm successful platform-string/file-I/O mappings, then
report verifier OOM at class-hash initialization for `org/joml/Matrix3fc` and
a separate native SeedGenerator thread-creation failure. Build **01.000.019**
extends the runtime fallback to all verifier-owned native allocations,
including the class-hash calloc arrays and their matched cleanup. Complete
host verifier checks pass with libc allocation refused and with mapping
failures injected during initialization. Thread creation now logs its exact
failure stage/return code; **the seed-thread cause remains unresolved**.
PS5 server readiness/save/stop and clean shutdown remain pending.

## Thread attributes and metaspace alignment in 01.000.020

Build 019 identifies the seed-thread failure as `pthread_attr_init` returning
ENOMEM before thread creation. Later native reservations fail while trying to
align another metaspace region, followed by a signal crash; the subsequent
fault's causal chain remains unproven. Build **01.000.020** consumes two Java
runtime fixes: a bounded, exclusively leased pool of real thread-attribute
objects initialized early, and exact-size non-replacing aligned mapping hints
before the larger metaspace reservation attempt. Security seed behavior,
verification and the 192 MiB Java heap setting remain.

ASan/UBSan host checks cover actual pthread creation/reuse and safe host mappings;
target/package checks are recorded in [build status](server/build-status.json).
**PS5 thread success, crash resolution and real server ready/save/stop remain
pending.** No completed Minecraft server milestone is claimed.

## Crash evidence and diagnostic overhead in 01.000.021

The user reports build 020 crashed and was reopened. Its logs confirm a
successful exact-size aligned metaspace reservation, but contain no captured
signal/abort and no server console output. The cause remains unrecorded.
Build **01.000.021** is a diagnostic build: routine metadata disk tracing is
sampled while every last-stage update remains in memory; native call tracing
uses quiet mode throughout VM/server execution. It adds thread startup phase
markers and a fixed-name HotSpot fatal report linked as `hs-error.log` on the
log page. Reports are archived before a new run; relaunch preserves them.
A report is available only if HotSpot generates it. Host/target/package checks
are recorded in [build status](server/build-status.json).
**The crash is unresolved; PS5 server ready/save/stop remains pending.**

## Stack discovery and thread initialization in 01.000.022

The 021 crash trace records successful native thread creation and child entry, then stops before stack recording/current-thread setup finishes. No signal or fatal report was saved. The remaining fresh attribute allocation in stack discovery now uses an early initialized query pool, separate from creation attributes so live stack addresses cannot contaminate new threads. Actual OS stack queries and real failures remain in place. Intermediate stack/TLS markers narrow any continuing failure. Host sanitizer stress and target compilation pass; **022 console validation and actual server ready/save/stop remain pending**. The exact 021 fault is unproven.

## Current-thread TLS in 01.000.023

The 022 trace confirms stack discovery succeeds, then the new child stops between compiler TLS assignment checkpoints. This target uses compiler TLS emulation, which may allocate on a thread's first access. Build 023 removes that dependency for HotSpot's current-thread pointer and uses its existing native pthread TLS backend, including guarded pre-init lookups and JNI destructor semantics. Host sanitizer tests cover 1600 concurrent initialization/clear cycles and signal lookups; target IR checks native key access without compiler TLS emulation. The trace provides no exact crash PC; **023 console validation and actual server ready/save/stop remain pending**.

## Native key failures and crash evidence in 01.000.024

Build 023 passes native TLS setup, handshake and Java thread entry before a later SIGSEGV. Its saved JVM fatal report is useful, but the reported registers are inconsistent; no exact crash location is established. Build 024 fixes ignored native key update failures in product builds: checked return/readback, a bounded allocation-free override for failed updates, explicit null on refused clear, and destructor handling that cannot resurrect a detached Thread. Normal native TLS remains the primary path. The fallback supports 1024 distinct failed thread identities per process and fails explicitly on exhaustion. New diagnostics record any actual key refusal and raw signal context without changing ABI offsets. **Native-key failure as the 023 cause, crash resolution, and real PS5 server ready/save/stop remain unconfirmed.**

## Direct native termination diagnostics in 01.000.025

The 024 console log confirms native pthread TLS returns ENOMEM and the fallback lets affected threads enter Java and later clear/return. The later whole-app crash produces no signal or current fatal report. Build 025 adds direct linked `abort`/`exit`/`_exit` hooks that save caller/status and previous native context, then preserve original termination behavior. This is a diagnostic build; kernel kills and calls internal to separately loaded modules can still bypass the hooks. **The later crash cause and real PS5 server ready/save/stop remain unconfirmed.**

## Progress and resource logs in 01.000.026

The 025 capture has no native termination or fatal signal marker, so the exact cause remains unknown. Its current startup log contains 272930 verifier mapping messages (over 21MiB). Build 026 samples repetitive successful messages while retaining mmap failures; allocation/verification behavior is unchanged. The log page adds **Class loading progress** and **Native resource samples**, archived on a new run. Native samples use actual OS getrusage without JNI and report raw counters or an explicit query error. Raw maximum RSS is not available memory or a proven container limit; the last loaded class is progress evidence. **All PS5 rows, diagnostic evidence and real server ready/save/stop remain pending.**

## Compiler TLS allocation repair in 01.000.027

Build 026 crashed after approximately 46 seconds. Its native termination trace and matching executable identify an abort in compiler-rt's emulated TLS setup after a 128-byte address-array allocation returned null. Build 027 uses the Java project's scoped compiler-TLS allocator adapter: libc first, then actual OS RW pages, with matched growth and release. The Java heap remains 192 MiB. This fixes the confirmed allocation path; console execution must establish whether later startup succeeds.

The harness also honors the JVM print hook's requested FILE stream. Build 026 redirected class-loading output into startup.log and left class-load.log empty; build 027 preserves separate class/fatal log files while retaining console capture. Resource samples remain available. Compiler-TLS native key update failures now have a distinct diagnostic marker; its setter semantics are unchanged, so a refusal remains a separate issue. **All five rows and real server readiness/save/stop require PS5 testing.**

## Compiler TLS key retention in 01.000.028

Build 027 confirms that mapped TLS allocation works, but its native key setter returns ENOMEM. That loses the storage pointer and repeats allocation: 247 refused key updates and 495 mappings precede another compiler-rt abort. Class loading is now captured separately as intended.

Build 028 pins a Java runtime repair that retains compiler-rt's canonical array independently of the native setter. Native destructors use the current array instead of a potentially stale native pointer. Thread creation/join adapters reclaim retained storage after actual thread death, with generation checks protecting reused identities. A detached or unjoined thread with refused native registration retains its array until identity reuse or process exit. Host sanitizer tests cover real pthread destructor order, stale pointers, concurrent isolation, failure paths and cleanup. The heap remains 192 MiB. **All five PS5 rows and actual server ready/save/stop remain pending.**

## Verifier repair and synchronization checks in 01.000.029

Build 028 closed around 20 seconds. The capture ends during a child thread's startup handshake; no signal, abort, fatal report or Java exception identifies the fault. Class loading reached JOML Matrix4x3f. Testing that class with the actual verifier reproduced signed-shift undefined behavior, now corrected by the Java runtime. That finding does not prove the PS5 crash cause.

Build 029 also records native synchronization errors in the product VM instead of compiling those checks away, and adds parent/child monitor-handshake checkpoints. Host sanitizer regressions cover the verifier, decoding boundaries and failed native synchronization initialization. The Java heap remains 192 MiB. **The crash cause, all five PS5 rows and actual ready/save/stop remain pending.**

## Native synchronization allocation in 01.000.030

Build 029 captured `pthread_mutex_init` returning ENOMEM, followed by a signal during fatal reporting. No Java exception or completed fatal report was captured. Build 030 uses the Java port's bounded early pools of real native mutexes and conditions, with exclusive stable-address leases and separate relative/absolute clock attributes. Exhaustion still attempts real native initialization and preserves failures. The Java heap remains 192 MiB. Host sanitizer checks pass with late initialization refused, native wait/signal/timeout behavior and 8,000 concurrent lease lifetimes. **All five PS5 rows and actual server ready/save/stop remain pending.**

Build 030 target compilation, signed-container integrity, ZIP checks and target-library identity checks pass. Package SHA-256: `04abef711724a49249dbf306f5bcba32f3dc7c49d70a561c4ff2c40852c24bca`. PS5 testing remains pending.

## Mutex reserve follow-up in 01.000.031

Build 030 initialized every early pool entry successfully, but still closed after a later mutex-init ENOMEM. Its capture does not record pool occupancy or identify the constructor. The generated-class workload can require additional metadata locks, making the 512-mutex reserve a plausible bottleneck. Build 031 expands the runtime mutex reserve to 4096 and reports exact pool occupancy, attribute matching and caller on native init failure, plus distinct event/parker/monitor labels. Condition capacities and the 192 MiB Java heap are unchanged. Host sanitizer checks cover all 4096 entries, exhaustion/reuse, incompatible attributes and the actual emitted failure fields. **This is a capacity adjustment and diagnostic build; PS5 server ready/save/stop is still unvalidated.**

Build 031 target compilation, signed-container integrity, ZIP checks and target-library identity checks pass. Package SHA-256: `5817e19dfe2405a911d70e5cc9db031ef341b1249470243efd85835952b66a43`. PS5 testing remains pending.

## Condition reserves in 01.000.032

Build 031 initializes all 4096/512/256 native primitives and reaches 12,884 class records, compared with 4,245 in build 030. Its later failure is native condition initialization ENOMEM; no mutex fallback failure is recorded. Build 032 expands relative/absolute condition reserves to 4096/2048 and records occupancy, requested clock domain and caller on failed native initialization. Event/monitor condition checks have distinct labels; parker retains relative/absolute labels. Mutex capacity 4096 and Java heap 192 MiB remain. Host tests cover each full condition reserve, exhaustion/reuse and the actual failure fields. **PS5 startup/save/stop remains unvalidated; condition-pool exhaustion is not established by the 031 capture.**

Build 032 target compilation, signed-container integrity, ZIP checks and target-library identity checks pass. Package SHA-256: `8e758fd3d6c76419b48d7f5913ae5bc907b626fca3d30374016439f76c78ae33`. PS5 testing remains pending.

## World metadata blocker in 01.000.033

Build 032 reaches the official server's world-directory validation, which fails reading `/download0/mc-server-start/world` attributes with Operation not permitted. The pinned server bytecode uses `NOFOLLOW_LINKS`. The native trace records no synchronization-init failure in this capture; a later signal occurs on another Java thread, whose exact crash cause remains unresolved.

Build 033 pins the Java port's nofollow descriptor-metadata repair: genuine file/directory attributes and missing-path errors, while final symlinks remain rejected when native lstat cannot describe them. The official validator is unchanged. The harness checks the required root/world metadata operation before loading Minecraft, allowing an early contextual failure. Shared exception/session reports use descriptor IO, with write failures recorded in the native trace. Heap and synchronization reserves are unchanged. **All five PS5 rows, actual ready/save/stop and resolution of the later native crash remain pending.**

Build 033 target compilation, signed-container integrity, ZIP checks and target-library identity checks pass. Package SHA-256: `d808a0cdd89f0828eb6265ea5bd4d265f7cf1405e93caf37df5c7b91995fe9f2`. PS5 testing remains pending.

## Signal recovery and vanilla assets in 01.000.034

Build 033 passed the earlier world metadata blocker, then reported native realpath EPERM while mounting the vanilla asset JAR. The complete native trace also exposed a signal ABI mismatch: HotSpot read a stack address as the interrupted PC because the SDK outer context lacks 48 reserved PS5 bytes. Runtime patches correct register reads and continuation writes, and add a descriptor-verified path fallback after EPERM. Link-dependent paths remain refused when native realpath cannot resolve them; the official game validator is unchanged.

Build 034 adds early preflight checks that catch a Java null access and mount/read the actual vanilla asset JAR through ZipFS. Its log page offers a compact startup tail (last512KiB), preserving full historical downloads. Host replay, actual JNI/ZipFS tests, HTTP tests, target compilation and package integrity/library checks pass. **Live signal recovery, all five console rows and actual ready/save/stop remain pending.** Heap remains192MiB. Package SHA-256: `848e02fc6672db599c851cfdd5045eee2a0a533335afb04808d1299ea2a4b7b1`. No new passing milestone is claimed.

## Null preflight crash in 01.000.034

Build034 crashes during the deliberate Java null check in row3, before verifying JARs or mounting assets. The console confirms corrected interrupted-PC reads, but no continuation is recorded. The inherited FreeBSD signal handler queries desktop kernel stack-gap controls before exception handling; disassembly confirms the linked procctl uses a raw desktop syscall. The exact terminating instruction is still unknown.

Build035 excludes that desktop-specific workaround on PS5 while preserving JVM stack guards and normal exception selection. Additional checkpoints narrow any remaining failure to stack triage, state/interpreter classification or continuation selection. The null preflight stays enabled. Actual-block host regressions and the target rebuild/package checks pass; **PS5 exception recovery, all five rows and real server ready/save/stop remain pending**. Package SHA-256: `17d71f2c4a4fe50407670a2ca46fdbfab3ffbfc5f90f4a38eeefba24bcc2572a`.

## Signal recovery confirmed; asset lookup in 01.000.036

Build035 confirms normal implicit Java null exception recovery on the PS5 and passes all40 pinned JAR checksum stages. It then crashes in the combined vanilla asset canonicalize/mount stage without a subsequent signal record. The new register layout and desktop stack-gap exclusion therefore have direct console evidence, but a full server pass is still unestablished.

The previous path fallback called an SDK openat function that issues a raw desktop syscall. Build036 pins a runtime repair that verifies each unelided path component with resident open/close, refusing link-dependent fallback paths and preserving actual errors. Optional desktop directory-at capabilities are no longer advertised on PS5; a secure anchored directory backend remains unported. Native realpath/fallback/component checkpoints and separate canonicalization/mount/read/close stages narrow any next failure. Heap remains192MiB.

Actual host JNI/ZipFS tests, capability checks, target compilation and package integrity/library checks pass. **All five PS5 rows and actual ready/save/stop remain pending.** Package SHA-256: `dfe1565747b98ffa1bed235c38bb8ca72fe57fc2281040bba729861afd40f772`.

## Java failures without app termination in 01.000.036

Build036 survives both verification and server-start failures, with the log service still available. The asset JAR canonicalization completes. Verification then reports EPERM during ZipFS mounting; server startup reports EPERM enumerating the existing world through the official DirectoryValidator. World readiness/save/stop remains unestablished.

Build037 pins resident libkernel directory enumeration with bounded record parsing and actual errors, plus descriptor-based read/write access checks after native EPERM. Execute/search permissions are never inferred; official world validation remains unchanged. Preflight separates readable-access, actual directory iteration and ZIP mounting. Verification and server exceptions now have separate links on the log page, preserving both when subsequent tests run. They are archived/reset for an explicitly initialized new run and retained on relaunch.

Host actual JNI/directory/ZipFS tests, malformed-record sanitizer tests, HTTP/archive checks, target compilation and package checks pass. **All five PS5 rows and real server ready/save/stop remain pending.** Package SHA-256: `f081c082bdc1a1f0c872935207cc21756e8a3ccde37e8bbb80f651d58f1ba343`.

## Directory ABI and native compression in 01.000.038

Build037 confirms readable asset access and canonicalization. Verification fails directory iteration with Invalid argument. The server reaches datapack loading, then native Inflater.init throws OutOfMemoryError through compressed ZipFS input. This is a native allocation path; the Java heap still reports free space. Minecraft service discovery also reports a separate DNS failure, which remains unresolved. Independent verification/server reports are now captured successfully.

Build038 tries the alternate resident directory API only after an initial unsupported-call response and successful rewind, with no entries delivered; it never replays after delivery. PS5 Inflater/Deflater stream and private zlib allocations gain a libc-first mapped fallback with overflow checks and matched cleanup. Both backends failing remains genuine OOM. Preflight now checks a real native compressed roundtrip before assets. Heap remains192MiB; authentication, game code and archive checks remain intact.

Actual JNI/zlib/ZipFS and sanitizer tests, target compilation and package checks pass. **All five PS5 rows, actual server ready/save/stop and the discovery DNS result remain pending.** Package SHA-256: `12dbc7f95c20837c314af3950e7c5780e8eb956f089fadcb8b564ee850985e25`.

## Native crash evidence in 01.000.039

Build038 fails directory verification with Invalid argument after the early compression check, and the user reports a whole-app crash59seconds into server startup. The saved trace records a native-state signal with PC and fault address0x100026c946 outside the app image, then another signal during error handling. The prior completed memset record is not the faulting call. No completed fatal report or native caller stack was available. The server page begins with discovery DNS failure; full server/startup files could not be saved this turn.

Build039 separates directory bytes into a dedicated page-aligned64KiB mapping and records which directory API enters/retries/fails. This removes a buffer-layout assumption; alignment/size is not yet proven the cause of EINVAL. New signal diagnostics sample saved stack words and monotonic frame links within the actual thread bounds, with nested-signal sampling skipped. They are bounded best-effort evidence, not protection from every corrupt/unreadable stack page. **The native crash cause remains unresolved; this is a diagnostic development build.**

Host sanitizer/target-code tests, target rebuilds and package checks pass. All five PS5 rows, directory enumeration, native caller capture and real ready/save/stop remain pending; DNS remains separate. Heap stays192MiB. Package SHA-256: `f6c68ef2fcadbcccb7f6547f79af1b5ee0ecfd2f92e760e015b1ae419cb2f506`.

Build039 console update: verification now **passes on PS5**, but flat-world startup still crashes. The reopened session records a native VM abort for run `01.000.039-1792229683-675501422`. The full native trace has not yet been retrieved because Firefox’s Save dialog is disabled; the caller and a repair remain unresolved. This establishes verification progress only; server readiness, save and stop remain unvalidated.

## Native OOM and fatal-reporting repair in 01.000.040

Build039 verification passes on PS5. Its saved native frame chain identifies a native allocation failure in the class dictionary, followed by a signal in the desktop core-path query during fatal reporting. Small allocations were refused64KiB slabs; the console memory limit remains unknown.

Build040 pins a runtime repair that reports no desktop core path on PS5, allowing normal fatal reporting to continue, and retries a minimal real mapped slab when the64KiB request is refused. If both mappings fail, native OOM remains a real failure. Actual-body host sanitizer tests and target compilation pass. **PS5 startup, real readiness/save/stop and failure-report survival require retesting.** No heap increase or game validation changes are included.

The subsequently saved039 trace confirms native OOM followed by a current-directory query fault during fatal reporting. Build040 package SHA-256: `42caf2dc57df38b7b8348f3bafdcda0abb0c8f4c81391b1a92d05d5560e17502`. Console results remain pending.


## Build040 console failure and build041 follow-up

The user reports a crash on flat-world startup in040. Retrieved current-run
reports identify `01.000.040-1792230582-556842474`. The server console reports
`OutOfMemoryError: PS5 class-byte scratch allocation failed (malloc and mmap)`
while defining a command lambda during datapack loading. A later native request
for8256bytes fails its16384-byte mapping with ENOMEM, then the VM aborts. This
trace has no signal marker; the previous secondary fatal-query crash did not
recur in this capture. Native resource capacity and the final allocation site
remain unknown. The last resource sample is58s, `maxrss_raw=504352`; its units
and the console's limit are not inferred. Service discovery also still reports
`UnknownHostException`. No ready/save/stop milestone passed.

Build041 supplies explicit flat-world biome/layers, correcting the independent
`No key layers in MapLike[{}]` configuration error. Server-thread lookup now
enumerates platform threads without requesting every thread's native stack
trace during readiness/failure cleanup. This removes avoidable native work;
it does not establish that stack collection caused the abort. The runtime pin
adds raw native fatal size/file/line/type/detail diagnostics before the full
error reporter. Heap size, online authentication and official datapack checks
are retained. Existing worlds are preserved; generation settings apply when
creating a world.

Host tests pass for a real Done/stop/saved level.dat run at192MiB without the
missing-layers error, plus absent/live/exited thread lookup with more than64
threads. Runtime fatal-entry ASan/UBSan contract test and target build pass.
**Build041 remains an experimental follow-up: PS5 native resource exhaustion,
all console rows and actual readiness/save/stop require validation.**

Build041 package SHA-256: `d95e4458cc35bf2cd3009bbaca15268a3c4b9df10c98e7157538c93d7bb90df2`.


## Build041 console failure and build042 allocator mitigation

The current-run reports for `01.000.041-1792232186-809546025` confirm a failed
16-byte native AllocateHeap request. Both64KiB and minimal16KiB slabs were
refused with ENOMEM; fatal-site tracing identifies `allocation.cpp:42`. A second
16-byte fatal request and24-byte refusal precede VM ABORT/_exit1, without a
captured signal. The startup tail also records a failed433-byte class scratch
allocation. The server reached new-world creation without the previous
missing-layers error, but never reported Done. Discovery DNS remains unresolved.
Last resource sample:57s, `maxrss_raw=504576`; units and process limit remain
unproven. Raw logs are retained locally.

Build042 pins a runtime mitigation: after mapping refusal, a small allocation
may borrow an available slot from a larger compatible size class. Ownership,
free/realloc behavior and real exhaustion failure are preserved. Complete
failure now records mapped bytes/live/free slots for each fallback class.
These counters cover fallback slabs only. Build041 does not establish that
compatible spare slots existed at its failure; this addresses a concrete
allocator limitation and needs console evidence for its effect. It is not a
confirmed fix for overall native exhaustion. Heap remains192MiB.

Actual-header ASan/UBSan tests pass for forced mapping refusal with larger-slot
reuse, exhaustion, owner-first release, undersized-slot rejection, failed resize
and concurrent lifetimes; os.cpp/NMT contract-model checks and target build pass.
The consumer Java harness is unchanged from the host-tested041 source.
**All042 console rows and real server readiness/save/stop remain pending.**

Build042 package SHA-256: `3005ff93a3d8098148e3232e6419480877a293ada83381959d805abd94332a48`.


## Build042 returned failure; build043 class scratch mitigation

The human reports042 failed at58 seconds without crashing. Current-run session
`01.000.042-1792232967-506149971` records a returned server-row FAIL. The server
console still identifies class-byte scratch OOM while generating an ExecuteCommand
lambda during datapack loading. Its native trace records115 successful compatible
larger-slot borrows, then normal worker return, with no captured fatal OOM,
VM ABORT or signal marker. The short server-exception report is BootstrapMethodError;
it does not supersede the detailed console cause. No ready/save/stop pass.

Build043 pins a PS5 runtime change that uses a bounded4KiB native stack buffer
for small byte-array class definitions, including hidden generated classes.
Larger files retain libc/mmap scratch and genuine allocation failure. JNI copying,
range checks, JVM class definition and bytecode verification remain enabled.
Each active definition uses4KiB more stack; recursive stack demand and later
metadata/native exhaustion remain console concerns. Heap192MiB and worker8MiB
stack are unchanged. This removes the observed temporary-buffer mapping need,
not a claim that the native resource limit is solved.

Actual ClassLoader.c JNI tests with UBSan and full host bytecode verification
pass small ordinary/hidden classes with BOTH backends denied, large heap/mmap
success and OOM, zero/4096/4097 boundaries, malformed/range cases, long UTF
source and direct-buffer cleanup. Target build passes. **All043 PS5 rows and
real readiness/save/stop remain pending.** Discovery DNS remains unresolved.

Build043 package SHA-256: `f523a0dceb4fc068fcee45af35dd6a3304b30c396c7751a42b3be92eb6bf761c`.


## Build043 medium class scratch failure; build044 reusable storage

The user reports043 failed without crashing. Live session
`01.000.043-1792234015-586564080` confirms a returned server-row failure.
Its saved console advances beyond the earlier lambda-definition failure to
`ExecuteCommand.addConditionals`, where an ordinary class triggers class-byte
scratch OOM. The startup tail records20257bytes with a refused32768-byte mapping
(ENOMEM). The wrapper then reports a Java fixture exception; server readiness,
save and stop did not pass. Full native trace was not retrieved for this run.
The separate discovery DNS failure remains.

Build044 pins four exclusive reusable32KiB scratch leases in the PS5 classloader.
Libc remains first; after refusal, eligible requests try an atomic lease before
mmap. Pool exhaustion and >32KiB requests retain real mmap and OOM behavior.
The4KiB local small-class buffer remains. This adds about128KiB fixed BSS plus
headers; recursive/concurrent definitions cannot share an active lease. Normal
JNI copy/range checks and JVM verification are retained. Native resource limits,
BSS backing on console and later metadata exhaustion remain unproven.

Actual-helper ASan/UBSan tests cover simultaneous20257-byte leases, exclusivity,
exhaustion, actual mmap fallback, size boundaries, reuse and concurrent ownership.
Actual JNI UBSan/full-verification tests execute medium ordinary/hidden classes
with both backends refused and retain >32KiB allocation/OOM checks. Target build
passes. **All044 PS5 rows and real readiness/save/stop remain pending.**

Build044 package SHA-256: `9c617614a4f4e2627521e255181d9319574848e7bc8f9542f4701c8c75e91bd9`.


## Build044 native arena abort

The user reports044 crashed and relaunched. Current saved run
`01.000.044-1792234674-244574062` records VM ABORT. The full native trace
identifies a32752-byte allocation refusal in `arena.cpp:186`, `Chunk::new`;
the raw backend requested49152 mapped bytes and received ENOMEM. The process
then aborts and exits1, without a captured signal marker. Saved server output
ends at new-world creation, without a class-byte scratch OOM or real Done.
This does not establish scratch-pool success or its causal role; overall native
capacity remains unknown. Discovery DNS remains unresolved.

The allocator adds a32-byte ownership header. The near32KiB arena request
therefore crosses a16KiB page boundary and needs48KiB. Runtime patch0071
increases the PS5 arena sizing allowance so a default chunk plus real Chunk,
raw header and optional NMT overhead fits32KiB. Existing growth, ownership,
alignment and real OOM propagation remain. This corrects measurable page
waste without establishing sufficient total console memory.


Build045 reduces only the default arena payload by88 bytes so its allocation
fits32KiB including backend/tracking overhead. Tiny/initial/medium sizes remain
unchanged. A target static assertion checks actual layouts. Actual allocator
and os.cpp API sanitizer tests use the exact arena enum, a Chunk layout/NMT
contract model and16KiB pages: the revised request succeeds with a32KiB mapping
cap and the old32752-byte request fails. This is host evidence, not a console
pass. Heap192MiB, worker8MiB and prior scratch fixes remain unchanged.
**All045 PS5 rows and actual ready/save/stop remain pending.**

Build044 resource measurements end58s at `maxrss_raw=504784`; units and the
console memory limit are not inferred. The arena overhead correction does not
establish that overall native exhaustion is solved.

Final target rebuild and package checks pass. Initial compile was restarted after
a source-header edit invalidated its precompiled header; the final rebuild passed.
Build045 package SHA-256: `f59d9ffedfc4e1e9548b01dc18bf4c8f430997ef4be93dc0e20a38f599d6d754`.


## Build045 saved read failure and build046 bounded native reads

The human reports045 crashed and relaunched. Preserved session
`01.000.045-1792235749-802431410` instead records a returned server-row FAIL;
its full saved native trace ends at a Java fixture exception without VM ABORT,
fatal OOM or native termination markers. Saved SIGNAL records select and resume
implicit-null continuations. These reports do not explain a later app exit or
disprove the human report; that discrepancy remains unresolved.

Firefox inspection of the current server.log tail identifies datapack-loading
OOM at `RandomAccessFile.readBytes0`, through ZipFile/Inflater fill and JAR class
loading into `Commands.<init>:236`. Full server-log saving was disabled; the
local cause record is a transcription of the visible tail, not a raw download.
The short exception file cannot format its Java text. Real Done/save/stop did
not pass. Overall native capacity and discovery DNS remain unresolved.

Build046 pins PS5 readBytes to the existing8KiB stack buffer after validating
the original full caller array slice. It returns one genuine short read;
Java stream/readFully callers continue from the returned count. This removes
large bulk-read scratch allocations without changing writes, increasing stack
size, pinning Java arrays or bypassing class/ZIP checks. More native read calls
may be needed. The earlier arena sizing and class-scratch changes are retained;
heap192MiB and worker8MiB remain unchanged.

Actual JNI-body UBSan/-Xcheck:jni tests pass full-content short-read loops,
EOF/null/bounds/closed/error paths and unchanged write allocation/OOM cleanup.
Real host RandomAccessFile.readFully and ZipFile reads also pass with the actual
capped body installed in that test process and both storage backends refused.
Target rebuild passes. **All046 PS5 rows and readiness/save/stop remain pending.**

Build046 package SHA-256: `bf498ad48ca257bd9ed5550e25e3b3248cbcb39392215ac7edd44a366cb7d3b7`.


## Build046 exhausted slabs; build047 lower Java heap budget experiment

The human reports046 crashed/relaunched. Saved session
`01.000.046-1792236273-725851607` confirms VM ABORT. Its full native trace
identifies a160-byte AllocateHeap failure at `allocation.cpp:42`. At failure,
all eight fallback classes have zero free slots, with21905408 mapped bytes and
184103 live slots. Later24/16-byte refusals and a second fatal OOM precede
abort/exit1. These figures measure fallback slabs only; they do not establish
total native usage, the process limit or a memory leak. The visible server tail
ends at new-world creation; full Save was disabled. No Done/save/stop pass.

The current host flat-world harness passes real readiness/save/stop at160MiB
in interpreter mode. Build047 therefore tests a smaller Java max heap ceiling,
160MiB instead of192MiB, while retaining the same runtime pin and all prior
fixes. Initial heap16MiB, worker stack8MiB, code cache8MiB and two processors
are unchanged. The32MiB ceiling reduction is a controlled budget experiment,
not a claim of32MiB additional available native storage. It may trade native
pressure for Java heap exhaustion or more GC; actual PS5 benefit is unproven.
The historical128MiB host OOM remains recorded and is not contradicted by this
160MiB run. No additional runtime allocator change is included.

**All047 PS5 rows and real readiness/save/stop remain pending.** Discovery DNS
and overall native resource capacity remain unresolved.

Build047 package checks pass; SHA-256: `bb7193b2526bdb77b04c91af81f6f82a6750dfe2a014a061f9bbd690b229bb90`.


## Build047 external-address signal; build048 native-preparation diagnostics

The human reports047 crashed/relaunched. Preserved run
`01.000.047-1792245216-254595165` remains marked RUN server worker, while its full
native trace ends in an unresumed SIGSEGV at `pc=fault=0x100026c946` with thread
state4 (native). There is no captured native fatal OOM, VM ABORT or termination
marker. The handler anchor matches the exact retained047 ELF with load offset
`0x400000`. Raw stack words map into native-call preparation, interpreter/link
resolution and class initialization; they do not establish the active callee.
The top resident-library return/external target are not symbolized. The full
server console ends at new-world creation. Discovery DNS remains unresolved.
No ready/save/stop pass; lower heap benefit and total capacity remain unproven.

Build048 retains160MiB and adds runtime diagnostic checkpoints before native
preparation, after lookup and after signature handler installation. Bounded
stack formatting records holder/name/signature, thread identity and resolved
native address without Symbol string allocation. Native lookup/signature
behavior remains unchanged. Preparation is not a complete invocation trace:
a previously prepared native method can run again without a new event, and
nested preparation may replace the latest context. This is a diagnostic build,
not a confirmed repair for the external-address fault.

Actual formatter ASan/UBSan tests and target build pass. **All048 PS5 rows,
trace usefulness, native fault resolution and readiness/save/stop remain pending.**

Build048 package checks pass; SHA-256: `c4b44bf6871d7c8023b7cb8c8a8c09a4bced523e5b5139e616bc51619cc0a74a`.


## Build048 identifies JFR default-directory query; build049 repair

The user reports048 crashed/relaunched. Run
`01.000.048-1792246886-523251605` remains marked RUN; the full downloaded trace
captures an unresumed native signal. Its latest same-thread native preparation
is `jdk.jfr.internal.JVM.setDumpPath(String)` with target0xa2f590. Exact048 ELF
symbols confirm the0x400000 load offset and native jfr_set_dump_path address.
The null/empty setter branch calls os::get_current_directory; its dump buffer
symbol maps to the captured0x2a43860 argument and the captured0x401 length
matches1025bytes. Fault PC0x100026c946 is outside the app. There is no captured
native fatal OOM or VM ABORT. Preparation alone is incomplete call tracking;
matching target, arguments and disassembly identify this default cwd query.

Build049 pins a runtime repair that defaults PS5 JFR emergency dumps to the
real application-visible `/download0`, covering both the setter and empty-global
fallback. Explicit nonempty paths and normal file-open/write failure behavior
are retained. The helper does not create a directory or disable JFR. Other
platforms retain their cwd lookup. Native diagnostics and160MiB heap remain.

Actual JFR path helper/get/set ASan/UBSan tests pass null/empty/default fallback,
explicit/max/oversize paths, buffer bounds and desktop behavior. Target rebuild
passes; its JFR emergency-dump object has no cwd-query dependency. **All049 PS5
rows, JFR initialization/output and real readiness/save/stop remain pending.**
Overall native capacity and discovery DNS remain unresolved.

Build049 package checks pass; SHA-256: `9a4407ef9da7b47bd05f43c5767b34c101df30d103b99bf5790223e41a8e98b9`.

### Build050: generated JFR metadata in the runtime image

Build049 returned server-row FAIL without a reported crash. The full saved
server log identifies a null resource stream in `MetadataLoader.createTypes`,
through `FlightRecorder.register` and Minecraft JFR profiler initialization.
This reaches beyond the prior default dump-path query; JFR dump output itself
remains unvalidated. Target Java compilation had omitted the generated
`jdk/jfr/internal/types/metadata.bin` resource.

Build050 pins runtime `496ea846b7b960441dba6f1e77b68808db39cd07`. The image builder runs requested modules'
target data generators, including JFR and desktop data, and verifies the JFR
resource SHA-256 across target output, JMOD and linked image. No host metadata
is copied. The extracted target JFR classes/resources load the metadata and
create238 types on the host JVM; this is not PS5 registration evidence.
Signed-container integrity, package CRC/version, native/image identities and
retained symbols pass. Heap160MiB and prior native repairs remain.
**All050 PS5 rows and real readiness/save/stop remain pending.** Discovery DNS
and overall native capacity are unresolved.

Build050 package SHA-256: `a4c1bfa3dc45b5c11bff656eeaecbecd85865b3802a9aeb2ffcabe64dddfc904`.

### Build051: identify network interface startup OOM

Build050 returned FAIL at one minute without a reported crash. The full saved
console gets past JFR initialization, loads1866 advancements, starts the server
and reaches listener setup on `*:25565`. Netty's `DefaultChannelId` initialization
then fails with an `OutOfMemoryError` rooted in `NetworkInterface.getAll()`.
The later `NoClassDefFoundError` wraps this initialization failure. This is
server-thread failure before readiness, not evidence of a one-minute timeout.
The server logs stopping/saving; no real `Done` or successful saved-world check
was reached. The exception report has18874592 free Java heap bytes after failure;
this does not identify peak heap availability or rule out heap OOM.

The full native trace records fixture failure, no VM ABORT/native fatal OOM, and
three implicit-null signals that each resume. Discovery DNS still fails.
The exact allocation inside interface enumeration/conversion remains unknown.

Build051 pins runtime `e09a729f7eba8156d7d5108ac128cdd826dfe6cb` with bounded PS5 native diagnostics for
interface enumeration, counts, native checked allocation failure and Java
array/object conversion failures, including exact conversion source lines.
It preserves the real interfaces, allocation paths and exception behavior.
**This is a diagnostic build, not a confirmed OOM repair.** Actual-body writer
and getAll host tests with narrow JNI/enumeration stubs pass ASan/UBSan; target
HotSpot/java.base native build, signed containers, native/image identities,
version/heap/diagnostic labels, ZIP CRC and retained symbols pass. Heap160MiB,
worker8MiB and target JFR metadata remain. **All051 console rows and real
readiness/save/stop remain pending.**

Build051 package SHA-256: `6ae273e10141baf6f996626c4405157c0e2888bccb6a4b02fcd2de28efa0fc9d`.

### Build052: retry resident interface enumeration ENOMEM

Build051 returned FAIL after the reported1m3s. Its full saved trace records
three earlier successful interface-list calls, each returning two Java
interfaces, then **IPv4 `getifaddrs()` fails with errno12 before native addif
or Java object conversion**. This identifies the resident platform operation;
it does not identify an internal allocator or kernel-query failure. The
server again reaches TCP listener setup and fails Netty channel-ID
initialization. Three implicit-null signals all resume; no VM ABORT/native
fatal OOM marker is recorded. There is no real `Done` or saved-world proof.

Build052 pins runtime `af1f51b913a373a061ee725d95cfe46b88cbbbe0`. The
[runtime repair](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/main/Development/docs/java25-interface-query-fallback.md)
keeps successful resident getifaddrs calls and non-ENOMEM errors unchanged.
On ENOMEM, it obtains fresh kernel route/interface data into owned mappings
with bounded parsing and matching cleanup. This covers IPv4/IPv6 enumeration
and MAC lookup, preserves real names/flags/addresses/masks/scope/link data, and
returns real errors on persistent query/map failure or unsupported records.
No cached addresses or invented interfaces are supplied.

Actual fallback/parser host BSD fixtures pass ASan/UBSan, including query/map
failures, size races, truncation/mutation and cleanup. Target native build and
package integrity/native-image identity checks pass. **Host fixtures and
target SDK compilation do not establish PS5 kernel route ABI or permissions.
All052 PS5 rows and real readiness/save/stop remain pending.** Heap160MiB,
worker8MiB and target JFR metadata remain. Overall native capacity and discovery
DNS are unresolved.

Build052 package SHA-256: `8ad63066a7f9564eca2e8c4e91feb11f1d67db9e734db269cb31c242e093bec3`.

### Build053: distinguish route-query and parser EINVAL

Build052's live session returned server-row FAIL. Browser inspection of the
current native trace shows resident ENOMEM triggering the route fallback,
then EINVAL and a null interface list with pending exception. The server
tail again identifies Netty initialization OOM through NetworkInterface.getAll
at listener setup. Firefox Save As was disabled and direct-link download
unavailable; this result uses UI observations, not full downloaded logs.
No whole-trace absence claims are made. DNS remains unresolved; stopping/saving
messages are not evidence of readiness or a verified saved world.

Build053 pins runtime `b8fc4881e0ea207224af3205f61126c1fd1c9e28` and adds precise
size/data query failures, lengths, SDK header sizes, mapping/retry diagnostics,
parser rejection line/offset and up to2048 bytes of rejected route data in
bounded hex rows. Query failure before data arrives produces no byte capture.
The actual snapshot passes byte reconstruction/cap/errno sanitizer tests along
with existing fallback/parser regression tests. Target build, signed containers,
package version/heap/diagnostic labels, native/image identity and retained
symbols pass. **This is diagnostic development; no EINVAL or startup repair
is confirmed. All053 PS5 rows and readiness/save/stop remain pending.**
Heap160MiB, worker8MiB and JFR metadata remain.

Build053 package SHA-256: `744786c43edb36a6ad339f680818677f9a723773b941baa1b406b4be2d91113b`.

### Build054: correct captured PS5 route header layout

Build053's full downloaded native trace identifies the fallback failure.
The kernel query succeeds with1320 bytes; parser line90 rejects offset0.
All captured bytes were reconstructed locally: four248-byte interface-info
records place link sockaddrs at byte192, while the SDK declares168. Reading
at168 interprets statistics as an invalid sockaddr length1. Address-message
headers remain20 bytes with8-byte sockaddr alignment. The server again fails
Netty initialization at listener setup; no real readiness/save proof. Three
native signals all resume, with no captured VM ABORT/native fatal OOM.

Build054 pins runtime `95964447de52acbc8017e6282f887d88e327c95c` and fixes this confirmed parser mismatch.
It skips the observed192-byte header and copies only stable bitmap/flags/index
fields, with target layout assertions. All prior bounds/errors/ownership and
resident-success behavior remain. Actual local1320-byte replay through the
parser and mapped fallback produces eight records: four link, two IPv4, two
IPv6. Mapping cleanup and prior regression checks pass ASan/UBSan; synthetic
fixtures now use the actual PS5 wire header and IPv6 family value. Raw route
data and logs remain local.

Target build, signed-container integrity, ZIP CRC/version/heap/header labels,
native/image identities and retained symbols pass. **All054 PS5 rows, live
fallback completion/Java conversion and actual readiness/save/stop remain
pending.** Resident ENOMEM's internal cause, overall native capacity and
discovery DNS remain unresolved. Heap160MiB/worker8MiB/JFR metadata remain.

Build054 package SHA-256: `6b671effa946902950f8327c81e63fc8704501bc7254aeb313fd926e1d53200a`.

### Build055: mapped internal interface nodes

Build054 confirms the route header repair on PS5: its full saved trace reports
successful parsing of eight records and IPv4 getifaddrs completion. The next
64-byte address-node malloc in addif fails. The matching server console now
reports `OutOfMemoryError: Native heap allocation failed` at Netty initialization.
Three signals resume; no captured VM ABORT/native fatal OOM. No real readiness
or verified saved world; discovery DNS still fails.

Build055 pins runtime `f7a692f2d7a7f6e2a78aef5901eaef92c942b53c` and adds a PS5-only libc-first mapped
fallback for internal interface/address nodes, with aligned ownership prefixes
and matching recursive cleanup. It also releases an unlinked address if a new
parent node cannot be allocated. Both backend failures retain real OOM.
Each mapped node uses at least one16KiB page; this does not establish a repair
for the overall native capacity limit. Route snapshot ownership remains separate.

Actual allocator/addif/freeif sanitizer tests pass libc/mapped/mixed ownership,
real address copies, virtual interfaces, every partial failure/cleanup, complete
refusal, boundaries/alignment and errno. JNI OOM/kernel flag/index calls are
narrow host stubs. Target build and package integrity/native-image identities
pass. **All055 PS5 rows, node mapping/Java interface conversion and real
readiness/save/stop remain pending.** Heap160MiB/worker8MiB/JFR metadata remain.

Build055 package SHA-256: `316164ac6f84c7b705de4e28b5ff378bf3cd4e26039e80db6691e6b366a6af59`.

### Build056: resident query errors after successful node mappings

Build055's full downloaded trace confirms route parsing and four mapped IPv4
list nodes. The following IPv6 resident getifaddrs call fails with errno13,
which the old ENOMEM-only retry did not cover. Earlier libc refusal logs also
carry13 after ioctl; without clearing errno, the trace cannot distinguish
a fresh error from a stale value. Netty initialization still fails; no real
readiness/save proof. Three signals resume and no VM ABORT/native fatal OOM
is captured. Discovery DNS remains unresolved.

Build056 pins runtime `2d251667e4de560306f3e6de073ab7492ef632ec`. It clears errno before resident query
and node malloc, records the returned resident error, and extends live route
retry to EACCES and errno-less failure. Success restores prior errno. Other
resident errors and actual kernel-query denials/errors remain failures.
Sanitizer tests cover these cases, stale errno isolation, actual route replay
and mapped/node cleanup. Target build and package integrity/native-image
identity checks pass. **All056 PS5 rows, IPv6/Java conversion and real
readiness/save/stop remain pending.** Heap160MiB/worker8MiB and previous fixes
remain; overall native capacity is unresolved.

Build056 package SHA-256: `f1f400feb87cb90ca760f0aa8d4635774c93258a8563d4ddcc246aef7c9c59e8`.


### Build057: interface flags and error preservation

Build056's full reports confirm both resident queries fail with fresh errno0;
fresh route queries and six mapped nodes succeed, and getAll creates two Java
interfaces without a pending exception. The next failure is isLoopback0 during
Netty MAC/channel-ID initialization. Three signals resume; no captured VM ABORT
or native fatal allocation marker. No actual readiness/save proof; DNS persists.
Reports were preserved through menu-only restart and retrieved locally.

Build057 pins runtime `c0650c9b6bf69dfae4a4faaf5bf3264be61c459c`. Denied interface flag ioctls retry through
fresh route records with actual flags; unrelated errors and real lookup failures
remain errors. New diagnostics identify the failed substage and preserve errno
across cleanup. The056 trace does not prove a denied flags ioctl: this is a
repair candidate supported by earlier ioctl errors. The short native diagnostic
suffix now uses stack storage so libc scratch refusal cannot hide the underlying
SocketException. Long messages and Java allocation errors retain real failures.

Actual flag-query/parser tests pass ASan/UBSan with denial, correct flag bits,
missing interfaces and failure propagation. Real JNI error-formatter tests pass
-Xcheck:jni/UBSan for PS5 and desktop controls, exact text, boundary sizes,
injected scratch refusal and cleanup. Target build, signed containers, ZIP,
native/image identities and retained symbols pass. **All057 PS5 rows, flags
resolution and actual readiness/save/stop remain pending.** Native capacity and
DNS remain unresolved. Heap160MiB/worker8MiB and earlier fixes remain.

Build057 package SHA-256: `9bc62068b7c1a151bb706a4915dbe17c71ff19ab67667a40e2acfc2caa8a4ea0`.


### Build058: mount-query boundary after real readiness

Build057 reaches Minecraft's real `Done (2.070s)` readiness message, then starts
saving chunks for all three dimensions. The user reports crash/relaunch; the
saved session remains RUN and no completed save/stop verification is recorded.
The flags repair works: ten denied ioctls have ten real route resolutions.
This readiness evidence does not freeze a passing milestone.

The full native trace ends at BsdNativeDispatcher.getfsstat preparation; the
exact057 target matches the retained ELF and its linked getfsstat invokes raw
desktop syscall395. No final fault PC is captured, so the precise crash site is
not proven. Three earlier signals resume; no captured VM ABORT/native fatal
allocation marker. A separate fatal report was not retrieved. Four relative
ban/ops/whitelist stream opens also report Invalid argument. DNS persists.

Build058 pins runtime `aab0d2fa8ad58ba8ceb58561a33a9a5fe50fd583`. PS5 mount enumeration now reports ENOSYS
before allocation or an unvalidated syscall; mounts/free capacity remain
unimplemented and Java mount lookup can report IOException. Consumer handling
needs console validation. Relative java.io stream opens now use the existing
File.getAbsolutePath/user.dir policy. Absolute/empty paths and real errors are
retained; descriptor constructors and other java.io File operations are outside
this change. Heap160MiB/worker8MiB and network fixes remain.

Actual native-body tests with real JNI/-Xcheck:jni and UBSan pass stream
resolution/I/O against a different process cwd, unchanged desktop behavior,
mount ENOSYS without native query/allocation, and desktop query/failure/cleanup.
The host fixture injects mount calls/exception transport and uses ASCII path
transport; target compilation uses real UnixException/platform conversion.
Target builds, package integrity/native/image identities and retained symbols
pass. **All058 PS5 rows, relative writes, handling of unavailable mount queries
and verified save/stop/thread exit remain pending.** Native capacity and DNS
remain unresolved.

Build058 package SHA-256: `2dc0dd46c2238aa8cfa1136f0ab291650736229d180370e9754697fd22c7e5bb`.


### Server_Start frozen: build058 ALL PASS

On 2026-10-18 the human confirmed all five PS5 rows passed for the exact058
package above. This validates runtime initialization, VM creation, artifact/asset
preflight, real readiness, stop/server-thread exit, nonempty saved level.dat and
VM destruction. The report's ten hours describes development effort, not an
endurance measurement. Source and package checksums are frozen in
[Server_Start](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Server_Start); the exact full package is preserved locally.

The [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Server_Start-v01.000.058)
omits official/game-derived JARs while preserving all remaining tested bytes.
Provision locally using the frozen README instructions. No saved-world reload,
player join, performance or endurance pass is claimed; mount discovery/capacity
remain unavailable and discovery DNS is not separately confirmed repaired.


### Build059: two-hour server endurance

The human requested a two-hour run after058 ALL PASS. This development build
retains the validated runtime and memory limits, disables empty-server pause,
checks fresh advancing game-time replies every30 seconds and requests an
acknowledged flushed save every five minutes. After7200 seconds it requires a
final flush, clean stop/thread exit, nonempty saved level.dat and VM destruction.
New server-thread errors, timeouts, stalled ticks and early exits fail the row.
Java heap/elapsed/check/save counters are persisted in the existing shared
console log. The menu timer includes startup; the endurance phase starts at
readiness. This no-player test does not establish client/gameplay performance.

[Run instructions and limitations](docs/endurance.md). **All059 PS5 rows and
the full two-hour result remain pending.** The passing058 source/package and
release remain frozen.

Build059 package SHA-256: `594da5c2eb0ce9b20d936cedfb5e263008e89fe3e15f4eeec9a91b8370b01bb9`. Host75-second regression passes36 advancing game-time checks and18 flushed saves with clean stop/persisted metadata; full two-hour PS5 validation remains pending.


During059's active run, a LAN join reaches the server but is rejected because
discovery.minecraftservices.com raises UnknownHostException, leaving the
SESSION/verify endpoint unavailable. This does not establish an authentication
service outage. Native DNS cause and whitelisted online admission remain
unresolved. The collected snapshot shows advancing ticks through120seconds;
the full two-hour result remains pending. See [endurance notes](docs/endurance.md).


### Build060: online readiness before the two-hour run

Build059's login attempt exposed a discovery DNS failure. Build060 adds scoped
SDK DNS result allocation fallback and native resolver-stage diagnostics. The
exact059 native failure was not captured, so this is a candidate repair that
still needs PS5 validation. It retains all real resolver errors, normal
certificate checks, online-mode=true and the whitelist.

Before launching the server, a new preflight verifies HTTPS discovery, the
configured account's official profile, the session-profile endpoint and
nonempty authentication public keys. It provisions that verified UUID/name in
the whitelist while preserving existing entries. If these checks fail, the row
fails with the exact stage instead of starting an unjoinable endurance run.
A real authenticated player join is still required to validate admission.

The account name is supplied to the local packager using --join-player, written
into an ignored generated asset and excluded from source Git. The delivered
local package is provisioned for the account observed in the user's login.
The two-hour clock starts at real server readiness as requested, whether or
not a player has joined. Tick/save/deadline/clean-stop checks remain in place.
An occupied run can be recorded as player-connected only with actual join
evidence; client load/performance is not established by startup alone.

**All060 PS5 rows, online authentication/admission and the full two-hour result
remain pending.** The passing058 milestone and original package stay frozen.

Build060 pins runtime `8114dc2547966ea998cce13fade563594ba638aa`. Package SHA-256: `522c0d6252e769e2a92b285038131a837d0dffac481468f540f4d2f3f247f1a9`. Native sanitizer/target/package checks and real host online preflight plus75second endurance pass; authenticated PS5 joining and7200seconds remain pending.


### Build061: trust-store metadata and relative whitelist discovery

Build060 confirms native DNS success and reaches TLS, then fails before server
launch with an empty trustAnchors error. The packaged store contains111 roots.
Standard JSSE selects its store through java.io.File metadata; those queries
still used desktop stat/access. A host injected-denial test reproduces zero
roots and obtains111 from the same store after genuine descriptor fallback.
The060 native trace does not independently record those metadata query errors.

Build061 adapts java.io metadata/readability after PS5 EPERM, retaining actual
file/descriptor failures and all other errors. Relative File metadata now uses
user.dir under the existing PS5 property, matching streams/NIO so Minecraft
can discover the preflight-generated whitelist. TLS preflight reports file
metadata and real default trusted-issuer count. Certificate validation and
online authentication remain enabled; no trust-all context is introduced.

Actual JNI/JSSE regression passes with111 roots, exact file attributes and
failure controls. Real HTTPS discovery/profile/session/key fetches and account
provisioning succeed under the same injected denials with target cacerts.
Actual patched relative-File policy, target Java/native build and package
identity/integrity checks pass. **All061 PS5 rows, authenticated admission and
the full two-hour result remain pending.** The058 snapshot/package stay frozen.

Build061 runtime pin: `b990691af0d1e5067928dc056eee09697c53b88a`. Package SHA-256: `372ad9df77581d719a4e72a85d80e8857d4ff376cff3572eaa4339f240ba112e`.


### Build062: retain the native DNS pool for authentication discovery

Build061 confirms111 trusted roots, verified HTTPS preflight, real server
readiness and the first tick check. Minecraft's own discovery thread then
fails DNS; joining receives the authentication-servers-down message. Native
trace records late SceNetPoolCreate ENOMEM. No completed061 endurance or
clean final stop was captured; the retrieved session still reported RUN.

Build062 retains one real16KiB DNS pool/resolver pair from early preflight
until app exit. Serialized leases reuse it for fresh platform DNS queries,
avoiding late native pool allocation. Real query and initialization errors
remain failures. This introduces no preset addresses or answer cache.
The harness also rejects Minecraft discovery failures before the timed phase
and during health/final checks, including when nobody attempts to join.

The runtime400-query allocation-denial/concurrency regression passes ASan/UBSan.
The real host online40second test passes20 advancing checks,10 flushed saves
and clean stop at160MiB with zero discovery/auth errors and zero player joins.
Target compilation, package identity/integrity and preserved058 checks pass.
**All062 console rows, authenticated player admission and the full7200second
result remain pending.** Online authentication, certificate validation and
whitelisting remain enabled; the timer still begins at actual server readiness.

Runtime pin: `b9b4cfe783a111d85ee1a278745bae0bfe07a9c9`. Package SHA-256: `a1f139c46e5187cadadcc335a476599f15f80a2e741bb86ca98d0112f726639f`.


### Build 063: memory headroom during authenticated configuration

Build 062 authenticated the online session, then failed while encoding
`clientbound/minecraft:update_tags`: Netty could not allocate a 32 KiB native
buffer. Native trace confirms ENOMEM for its 48 KiB mapping, followed by class
loading and thread failures and a VM abort. Five tick checks reached 120 seconds;
no completed player admission or endurance pass was recorded. Raw reports stay local.

Build 063 lowers the Java heap ceiling from 160 to 144 MiB, sets Java thread
stacks to 512 KiB and selects Netty's existing unpooled allocator. This leaves
more native headroom and reduces retained buffer storage. Network buffers still
use real direct allocation. `MC_NETWORK_MEMORY_OK` checks allocator selection
and 64 KiB growth/readback/release. Netty packet errors now fail endurance even
without an authentication or server-thread error. An intermediate 128 MiB
configuration exhausted Java heap during chunk stress and was rejected.

Validation passes 20 actual update_tags codec roundtrips of 116,901 encoded
bytes each, comparing every decoded tag and ID and releasing each buffer. At
144 MiB / 512 KiB stacks, the real host online 60-second test with 49 forced flat
chunks passes 25 advancing tick checks, 14 flushed saves, persisted region data
and clean stop. Target compilation and exact package integrity checks pass.
**PS5 memory fit, authenticated world entry and the full two-hour result remain
pending.** Authentication, TLS and whitelist checks remain enabled; the timer
starts at real server readiness. Frozen build 058 remains unchanged.

Package SHA-256: `f80168f2fdb82487ba37d98a131cf36b0eabeb9094cb73f6e31ac8169556a3f3`.
Runtime pin: `b9b4cfe783a111d85ee1a278745bae0bfe07a9c9`.


### Build 064: reduce native allocation/tracing overhead; measure gameplay

Build 063 confirms authenticated world entry and gameplay. Its measured rate
falls to about 11 ticks/second, with overload warnings over 13 seconds. The
human reports eating repeatedly animates with hunger below full, without
consuming food or displaying an error. The captured log has no food-specific
exception. A player-data save warning on disconnect also remains unresolved.
This is partial admission validation, **not ALL PASS or an endurance milestone**.

064 reuses at most one idle native slab per class (512 KiB bound), trims idle
pages under mapping pressure and samples successful phase logs while preserving
failure/crash context. Memory-call tracing resolves each thread context once
per entry/exit while keeping every call record. Actual-header/wrapper sanitizer
tests pass: 10,000 short allocation lifetimes use one mapping, pressure cleanup
and failure semantics remain intact, and quiet memcpy uses two identity lookups.
Target HotSpot/native compilation and package integrity checks pass.

Health output now includes observed tick rate and actual GC counter deltas.
Read-only vanilla commands record connected players' hunger, saturation and
exhaustion; these remain in local console logs. They do not modify food rules.
The host 40-second online test with nine forced flat chunks passes 18 tick
checks, nine saves, telemetry/command dispatch, persisted region data and clean
stop. **Eating is not yet fixed or validated, and no PS5 speedup is claimed.**
The runtime still uses `-Xint`; JIT performance remains unvalidated.

Retest ordinary gameplay and eating first, with hunger below full, and leave the
probe open for log collection. The configured 7,200-second readiness-anchored
phase is retained, but a full-duration pass is not the immediate acceptance
criterion. Keep the frozen 058 snapshot/package unchanged.

064 runtime pin: `bf394d0a8ca3dba37cae7b61277b8b1f728dd6d7`. Package SHA-256: `bf31e0effa895f0b2f24dd543c03c475c45a1916b4a93f499ca95a24617ebf0d`.


### Build 065: fix java.io directory listing during legacy conversion

064 passes online preflight but fails before readiness: the official
OldUsersConverter receives null from File.listFiles and dereferences it.
The remaining java.io directory implementation used desktop SDK enumeration;
NIO already used the resident PS5 reader. The original native errno is not
captured, so the precise opendir refusal cause is not established.

065 uses the same resident directory helper for PS5 java.io listing. Real names,
empty directories and actual failures remain distinct; partial failures are
rejected and resources are released. Native diagnostics identify open/read/close
errors. A read-only legacy-player directory preflight reports the listing before
the official converter consumes it. No legacy files are removed, fabricated or
silently skipped by this change; official migration behavior stays intact.

The actual-JNI regression passes 351 filenames, array growth, Unicode, symlink,
empty/missing/file paths and injected open/read/partial-read/close/mapping
failures with SDK opendir denied. The real host server also runs through that
rebound PS5 method with an existing legacy-player directory: online preflight,
Done, 30 seconds / 14 tick checks / eight saves and clean stop pass. Target build
and exact package checks pass. The full host run emits nonfatal optional macOS
OSHI/JNA JNI-check warnings; the isolated listing regression has only the
expected native re-registration warning. **All 065 PS5 rows remain pending.** 064 never
reached gameplay, so the earlier speed/eating issue is still unresolved. The
064 optimizations and GC/TPS/hunger diagnostics remain included. Frozen 058 is
unchanged; no new ALL PASS or full-duration result is claimed.

065 runtime pin: `60ab50e4694bf42c8874c6f96fb609b8c7735322`. Package SHA-256: `696c39011917599f37ca31af1e65b0b97fde47cb763dab8f652ce9a900712da1`.


### Build 066: guarded C1 performance candidate and food-use traces

065 reaches readiness and admits the authenticated vanilla client. It still
runs poorly: joined samples drop to roughly 10–13 TPS, with several seconds of
GC per interval. Chicken and mutton reach the client burp but do not consume or
restore hunger. FoodLevel 18 and 16 confirm hunger is below full. A death between
samples explains the temporary reset to 20; it is not evidence of eating.
The exact consumption failure remains unresolved.

066 enables mixed-mode C1 at level 1 with one compiler and the existing 8 MiB
code cache. A correctness gate requires this run's actual kernel compilation
and checks deterministic results before accepting the preflight. This is the
first C1 performance candidate, **not a PS5 JIT pass**. Heap stays 144 MiB and
Java stacks 512 KiB; native compiler memory and compiled exceptions need testing.

A read-only observer runs at the final server tick return. It records use state,
remaining ticks, held/use stack counts, hunger, saturation and tick/wall duration.
It changes no food, inventory or game rules. The local derivative now adapts
SystemReport telemetry plus this single MinecraftServer observer; the verified
original stays intact. An audit preserves every existing method opcode and
invocation. All other classes/resources remain byte-identical except the unsigned
manifest. Inspect `MC_ITEM_USE` and `/jit.log` alongside TPS/GC and native usage.

Host C1 validation reaches Done and passes 30 seconds, 15 tick checks, seven
saves and clean stop with nine forced chunks, online preflight and the observer
initialized. No host player joined, so this proves neither eating nor mob speed.
Package integrity checks pass. All 066 console rows, gameplay, player persistence
and the full two-hour phase remain pending. The timer still starts at server
readiness. Frozen 058 remains preserved.

066 runtime pin: `335443815712c132db69f36e6d4e099490e6c20b`.
Package SHA-256: `93a41b45355fb2ee7cd6d06d7c775b166d77201ee2f885b9a807e458b0e30bb4`.


### Build 067: native library allocation during management verification

066 fails verification with a bare OutOfMemoryError at the combined management
check. It does create the VM and record about 800 C1/native compilations, but
never completes the explicit correctness gate, starts the server or begins the
timer. The trace stops before management implementation classes load, immediately
beside a 17-byte platform-string fallback consistent with libmanagement.so.
The exact failing allocation is not captured.

Runtime patch0090 repairs a concrete remaining weakness in that path: the
library-name copy and JNI symbol-name buffers still used raw malloc and threw
a message-less OOM on refusal. Scoped PS5 allocation now falls back to mapped
scratch storage and releases the correct backend. Library/symbol lookup and
JNI initialization/version validation stay intact. If both allocation backends
fail, the error remains. This is a candidate repair pending the console retest.

The actual JNI regression exercises allocation/mapping failures for both buffers,
unknown/short/oversized/null names, Java-string failure, load/unload symbols and
512 lifetimes without leaks under -Xcheck:jni/UBSan. The unchanged desktop body
reproduces bare OOM with malloc denied. Target native rebuild, full host C1
preflight through real management and compiled-kernel checks, official --help,
derivative audit and exact-package checks pass. The host symbol resolver is a
fixture; it does not establish PS5 library discovery or ABI correctness.

067 reports separate checkpoints for management native-library initialization,
heap, nonheap, runtime flags and C1 warmup. Gameplay traces and all C1/memory/
online settings remain. All console rows, hungry eating/mob performance,
player persistence and the full two-hour phase still need validation. Frozen
058 is unchanged.

067 runtime pin: `69271a6058c45c44bf50a89ad32188dd2b4870bb`.
Package SHA-256: `354464f68b299277716fc8c2813247b8d8fb0c133d3fc65ff3b64f51dfa1e183`.


### Build 068: C1 native memory and code-cache pressure

067 passes management verification and reaches authenticated gameplay, then
aborts after the user reports less than ten seconds of laggy play. The fatal
report names C1 CompilerThread0: a 32,664-byte Chunk::new allocation and its
32,768-byte mapped fallback both fail. Native resource maxrss_raw reaches
512096; exact units and the title ceiling remain unconfirmed. This is a VM
native-allocation abort. The client's connection reset is its consequence.

The 8 MiB cache has 6,576 KiB used and full_count=0, but its GC threshold causes
repeated full collections. The last joined sample averages 20 TPS while spending
4.292 seconds in GC across the interval, so average TPS hides interruptions.
Food samples show hunger16 and a changed main-hand stack, but no active-use
transition or hunger restoration; eating remains unresolved.

Runtime0091 retains at most eight unused chunks per standard arena size class,
frees excess immediately and clears unused pools before one real allocation
retry. Live chunks remain intact. The previous cache retained arbitrary bursts
until its five-second sweep; its exact contribution to this crash is not
measured. 068 also uses a 16 MiB code cache, compilation threshold scaling4 and
a 2 MiB per-compilation arena limit with level1/one compiler. Heap144MiB and
Java stacks512KiB stay the same. GC/code-cache reasons join the JIT log.
This is a candidate mitigation, not a demonstrated fit in the console budget.

Actual pool-path ASan/UBSan tests, existing native allocator/NMT/layout tests,
target rebuild, full host C1 preflight and derivative audit pass. The new host
configuration runs60seconds with49forcedchunks,28checks,14saves,online preflight
and clean stop. Host code-cache peak is6391KiB with one threshold-GC event.
No host player joined; these results do not validate PS5 latency or consumption.
All068 console rows, hungry chicken/mutton use, native peaks, player persistence
and full two-hour completion remain pending. Frozen058 is preserved.

068 runtime pin: `056d6a7084fadf35a51d2d5d5069d05be925a7dc`.
Package SHA-256: `8f2097509fd7942122341578c593aa3e83d2f8130f2ee6b803b85c040899bf82`.


### Build 069: smaller metadata reservations at gameplay protocol setup

068 reaches readiness and online authentication but aborts while completing
configuration before player admission. The server thread cannot reserve16MiB
for non-class metadata while initializing GameProtocols. Non-class metadata
has79.06MiBused in80MiBreserved; the separate class region has17MiBused of32MiB.
Its last idle sample is20.03TPS with one173msGC. This does not establish joined
performance, but the earlier repeated code-cache GC storm is not seen there.
No logged-in player or active food-use transition is recorded.

Runtime0092 uses a PS5-only4MiB metadata root and13 buddy levels down to the
same1KiB leaf. Non-class metadata grows in4MiB nodes with4MiB alignment instead
of16MiB reservations. Actual byte sizes in the growth policies are preserved.
Single PS5 metadata allocations are now limited to4MiB; total space still grows
across nodes. Desktop geometry stays16MiB/15levels. This avoids a large growth
cliff but does not prove the full workload fits the native budget.

The harness also initializes the real serverbound/clientbound GameProtocols
templates after Done and reports MC_GAME_PROTOCOL_OK. It loads the exact path
from the fatal stack during host testing without claiming a client joined.
The readiness timer is not reset. Existing memory, C1, online and gameplay
trace settings remain.

Actual geometry/level-fitting/settings checks, reservation-path tests,
ASan/UBSan and target rebuild pass. Host gameplayprotocol initialization and
60seconds with49forcedchunks,28checks,14saves andcleanstop pass. The host JVM
uses desktop geometry and no player joins; PS5 metadata behavior, native peaks,
food/mob performance, player persistence and full two-hour completion remain
pending. Frozen058 stays preserved.

069 runtime pin: `1c5bb584b9ddb8a1f1a148d463601b66cef7d443`.
Package SHA-256: `8332caa2965f5e8002e7aa7b7c29e184963867551edab80f708ad56e560f8820`.


### Build 070: reduce promotion pressure after working food in 069

069 is a partial gameplay success: the human reports much faster play and
working food. The actual use trace confirms two chicken consumptions, count2->1
and1->0 while hunger rises15->17->19. This is not an ALLPASS or two-hour result.
The user reports a recovered freeze aroundfive seconds and remaining lag.

GC remains expensive: one30second interval spends9.639seconds across45collections.
The captured individual maximum is273.684ms, so these reports do not establish
the exact cause of the five-second freeze. Repeated full Allocation Failure
collections retain117–121MiB. This is consistent with old-generation pressure under the existing layout;
the occupancy model below tests that explanation.

070 uses SerialGC NewRatio7 under the same144MiB Xmx cap to give the old generation
more room. Nursery size and usable survivor geometry change; total configured
heap does not grow. An explicit host occupancy model with108MiBlong-lived arrays
and512MiBtransient churn hits heapOOM at NewRatio2 but completes with preserved
data and onefullcollection at NewRatio7. This supports testing the layout;
it is not a player workload or PS5 performance result.

MC_TICK_GAP samples end-of-tick wall gaps every100ticks, reporting meanMicroseconds,
maximumMilliseconds and gaps over100ms. These include scheduler/GC/IO/CPU time;
they help separate server stalls from client/network symptoms. The existing
read-only hook changes no game rules. Host60second/49chunk/29check/14save run,
real protocol preparation, tickgap output, preflight and packagechecks pass.
No host player joined. All070 console performance, freeze diagnosis, otherfoods,
playerpersistence and full two-hour completion remain pending. Frozen058 stays
preserved;069 remains a partial result. The069 console run was not interrupted.

070 uses unchanged runtime pin `1c5bb584b9ddb8a1f1a148d463601b66cef7d443`.
Package SHA-256: `8b8b5005c48c62c17af76398ff1b7e9db3b7ee7d8cd09dffebc03999d257f9e0`.


### Build071: native headroom, compact objects and normal terrain

The retrieved070 run aborts184seconds after VM startup during
SerialCollectForAllocation. It follows player death/respawn; exact native GC
subcaller and any fixed title memory ceiling are not established. Native
4088byte allocation and minimum16KiB anonymous mapping both fail.070 does reduce
observed GC time versus069, but average20TPS still hides individual gaps.

Runtime0093 reduces the raw allocator prefix to16aligned bytes. Actual allocator
regression/profile models pass under ASan/UBSan; the16-byte alignment model
saves4MiB for261080live blocks, not a console savings guarantee.0094 makes the
ZIP decoder available to the PS5 resident image reader and links its standalone
target dependency. The module image saves37391447resident bytes before decoding
individual resources. Actual reader/TLS/JFR/desktop byte-identity, failure
controls, target rebuild and target-JFR host checks pass. Compression adds decode
CPU work; console startup/memory tradeoffs remain unmeasured.

Normal-world force-load attempts at169chunks/144and160MiB and81chunks/160and176MiB
without compact object headers fail with JavaheapOOM on the host. These are
recorded failures, not console results.071 enables Java25 compact object headers
with176MiB, view4/simulation3, a separate normal world with structures, max20and
the user's explicit level4OP-for-admitted-players policy. OP is applied on the
server thread through vanilla APIs, persisted to ops.json, and never bypasses
the configured player limit. The tick hook is therefore no longer wholly
read-only. Authentication/TLS/whitelist and the real readiness-based7200seconds
remain. Twenty-player load, console respawn/food/mob latency and full endurance
remain pending. Current checks are recorded in [build status](server/build-status.json).

Final071host check: normal terrain/structures at176MiB with compact headers,
81forcedchunks,60seconds from readiness,26advancing checks,14flushed saves and
clean persisted-world stop pass. Actual ops.json grants level4without player
limit bypass; old-flat-world sentinel survives. No player joined. Initial chunk
generation still records a5897ms gap before approximately20TPS steady ticks, so
optimal speed is not established. Package integrity/identity and frozen058hash
checks pass. Runtime pin: `8686aee246e3c1928f5fb3f52ab1a3e05c567e8f`.


### Build072: real OS entropy and explicit early TLS stages

Current071reports stop before Minecraft Main/listening/Done, with no Java
exception, abort/fatal report or signal trace. Trust initialization and DNS pass;
seeding falls back to ThreadedSeedGenerator with repeated native thread creation
and about8seconds of work, then TLS factory class progress stops. These logs do
not establish a memory failure or the precise process-crash cause.

Runtime0095 supplies NativeSeedGenerator with the actual PS5 system random
service in bounded64-byte stack batches. A native OS failure throws and never
accepts substitute seed material. Other Unix platforms retain URL seeding.
The actual Java/JNI routing, batches, failures and real DRBG pass host JNI/UBSan
checks against a mocked OS boundary; actual console service/ABI remains pending.
The harness now marks real DRBG initialization and verified default TLS factory/
unconnected socket initialization separately before HTTPS discovery. Certificate
validation, authentication, whitelist and071world/OP/heap settings remain.
No additional game-JAR transformations are added. Exact original crash cause,
normal-world startup/respawn and full endurance remain unresolved until retest.
Runtime pin: `584cde37723c3b7863d6349632c1215565ab5b70`.

Final072host actual DRBG/TLS-factory/HTTPS, C1preflight/help, derivative opcode
audit, compressed image resource/JFR checks pass. Normal-world81-chunk30second
run completes8checks/5flushed saves and clean stop with no hostplayer. Initial
generation still shows12663ms max tick gap; this is not optimal performance.
Package checks confirm OS-service dependency/new JNI/linked seed code, all
target artifacts, both signed containers and frozen058checksum. The existing
game derivative's entries remain byte-identical to071. Console OS entropy/TLS
startup and the original crash cause remain unvalidated.


### Build073: captured RNG import failure and kernel entropy repair

072stops at MC_TLS_RANDOM_BEGIN before server initialization. The recorded
SIGSEGV has PC0. Matching-ELF signal anchor and stack return identify the
instruction immediately after the direct sceRandomGetRandomNumber call; its
GOT relocation identifies the unresolved import. This establishes the072cause,
not the earlier071cause or a Javaheap shortage.

Runtime0096uses kern.rng_pseudo through the kernel sysctl interface with bounded
64-byte scratch storage. Return code and actual byte count are checked before
Java transfer; missing API, failed/insufficient/oversized responses throw
ProviderException. Scratch is cleared through volatile writes. No optional RNG
service import/module dependency remains. Actual Java/JNI concurrency, batching,
DRBG, errors/null-import and desktop-control tests pass with JNI checking and
UBSan against a mocked kernel boundary. Target native rebuild passes.

The Minecraft Java harness and all game-derivative entries remain unchanged
from072; the consumer change is version/runtime pin and status only. Actual PS5
kernel entropy/TLS/startup, earlier071cause, normal-world/respawn, optimal latency,
20-player capacity and the full7200seconds remain pending.
Runtime pin: `83453c5db0cdd89c4795b4e53cbcd8fa8e2440c7`.

Final073package verification passes CRC/version/flags, exact target native/module
identity, retained seed JNI/kernel marker and checked kernel pointer, absence of
the direct RNG import/module dependency, matching ZIP/symbol copies and both
signed containers. Frozen058checksum and all game-derivative entry bytes remain
unchanged. Actual PS5 startup is still pending.


### Build074: native Java image decoding after DRBG success

073fails without crashing: MC_TLS_RANDOM_OK confirms DRBG completion, followed
by ClassFormatError for sun/security/ssl/DTLSInputRecord (magic0x07000f0c) during
TLS factory setup. No real server readiness or endurance phase was reached.
The exact inflate status was not logged, so a specific failed allocation is not
proven. Source inspection identifies missing PS5 zlib callbacks in native full
inflate and ignored image-decode errors in release builds.

Runtime0097uses the existing matched libc/page-backed zlib adapter and checks
complete/exact output. Image read/decode failure returns0 and HotSpot raises a
resource-named IOException. Reader ownership now starts at refcount0; sanitizers
exposed the uninitialized count during repeated open/close tests. The actual
native ZIP body and release-mode reader pass ASan/UBSan for DTLS/SSL/JFR/desktop
byte identity, libc fallback, both-backend refusal, corrupt/truncated/wrong-size
errors, untouched caller bytes on compressed failure, cleanup and recovery.
The previous image reader test used host libzip;074tests the native inflater.
Target HotSpot/java.base native rebuild passes.

Java harness and all game-derivative entries remain unchanged. Normal-world, OP,
20-slot limit and7200seconds from readiness remain. Console image/TLS/startup,
earlier071cause, gameplay/respawn, sustained performance and20-player capacity
remain pending. Runtime pin: `82e1a264def3e0c3629d0ad7e4c6dc9756fcb1e5`.

Final074package checks pass exact ZIP/version/flags, seven target native-library
and module identities, embedded inflater/error markers, signed containers and
matching ZIP/symbol copies. Frozen058hash and game-derivative entries remain
unchanged. No additional host game run was performed: the Java harness is
unchanged and the new native reader/inflater path is tested directly above.
Actual PS5 TLS/server readiness and sustained gameplay remain pending.

### Build075: locate the remaining HTTPS startup crash

074 reports confirm real DRBG, default TLS factory and runtime DTLS class loading
complete. DNS for discovery returns success; the last class load is
HttpsURLConnection$DefaultHostnameVerifier. No fatal signal or exception was
captured for the process exit, so this does not establish a C1, memory, network
or class-decoder root cause. An earlier implicit-null signal was handled and
execution continued. Raw logs remain local.

075 adds flushed setup/request/body/cleanup phase markers with Java heap values.
No game transformation, heap/JIT option, world/OP policy or TLS security change
is introduced. Host checks and package verification are recorded in
[build status](server/build-status.json). PS5 startup, short join/respawn and
performance checks must precede the full two-hour run.

### Build076: scoped native image-resource buffers

075stops at connection_begin after dns_ok/url_ok. Java heap sample is
63995904committed,51544168free,182255616maximum. Last class load is the default
HTTPS hostname verifier; no fatal location is captured. This does not identify
a C1, OS memory or decoder crash cause.

Runtime[patch0098](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/main/Development/docs/java25-image-resource-buffer-allocation.md)
extends checked PS5 allocation fallback to image-resource temporary buffers,
previously ordinary C++ new[]. A terminal decode no longer speculatively reads
another header. Actual release-reader ASan/UBSan tests cover independent buffer
allocation refusal/fallback, unchanged caller output on failure, cleanup/recovery,
exact HTTPS/DTLS/TLS/resource bytes and1/8/28byte terminal resources. Target
HotSpot/java.base native rebuild passes. Existing zlib controls remain passing.

076retains075HTTPS diagnostics and every existing game derivative entry. Actual
PS5 startup, normal-world gameplay/respawn/food/mob latency and full7200seconds
remain pending. No optimal-speed or20-player capacity claim is made.

### Build077: address stutter and expose player-save failures

076 progresses through TLS, online discovery, real readiness and authenticated
player admission; the human reports much better gameplay. The current
[performance review](docs/performance-076.md) records74full GCs,354ms maximum
GC pause,567ms maximum tick gap, near20TPS interval averages and three player-save
warnings. None establishes completed endurance or20-player capacity.

077tries NewRatio15 with the same176MiB cap; host results do not establish an
improvement and PS5 comparison is required. Its harness tests vanilla compressed
NBT SYNC file writes and safe replacement/backup/readback, printing a named
phase and actual exception on failure. Player-save warnings fail acceptance
even if Minecraft acknowledges a world save. No new game-JAR transformations
are introduced. Frozen passing snapshots are unchanged.

### Build078: index-only Java module image after native C1 OOM

077's user reports near-perfect speed before a crash. The fatal report identifies
C1CompilerThread0:32664native bytes for Chunk::new, method
SerializableChunkData.read808bytes,97.573seconds elapsed. A32KiBfallback mapping
fails with ENOMEM even after unused chunk pools are pruned. The generic JVM
physical-memory summary and maxrss_raw do not establish a hard process limit.

Runtime0099uses the upstream index-only image path on PS5, retaining all modules
and verified compressed resources. It removes27082752bytes(25.8MiB) of persistent
anonymous copy from the current image. Partial/EINTR/resource-read errors are
checked. Native ASan/UBSan, exactresources/cleanup/refusal and target build pass.
No consumer helper/game derivative changes are introduced;176MiBheap/NewRatio15/
C1 settings remain. Actual PS5 latency, memory headroom, gameplay/save persistence
and7200second stability are pending. See[details](docs/native-memory-077.md).

### Build079: complete the index-only image transition

078passes all40pinned JAR checksums, then fails withExceptionInInitializerError
when opening the server class stream. Runtime0100fixes the Java/native map-mode
mismatch introduced by0099. Host integration with the actualJava/native/JNI
reader reproduces the oldJarFile/Unicodeinitializer failure and passes the fixed
reader and desktopcontrol. Native sanitizer controls and Java/native target
rebuild pass.079includes up to8nested causes in future preflight reports.

Memory saving, allmodules, JARverification and existing gameplayconfiguration
remain. No game-JAR transformation is added. PS5verification/startup/native
headroom/gameplay/savepersistence/full7200seconds remain pending.

### Build080: defer premature code-cache-triggered full GC

079fixes verification and admits a player, but repeated full-GCpauses remain.
The capturedCodeCacheGCThreshold pauses occur five times within17.149seconds
and total1.029seconds, at37–57percent codecacheoccupation.080sets the existing
SweeperThreshold50flag while retaining aggressive10percentfreecleanup and
flushing. Heap/codecache sizes and all gameplay/security settings are unchanged.

Two sequential short hostcontrols pass world/NBTsave/tickmonitor/stop checks,
with code-triggerGCs2to0. OtherGCpauses and initialgenerationstalls remain; this
is not proof of freeze-freeplay. Actual PS5pausefrequency/maximumtickgaps,
nativeheadroom and7200seconds require validation. See[review](docs/pauses-079.md).

### Build081: remove the server-JAR derivative

Both active transformations are removed: SystemReport telemetry wrappers and
MinecraftServer tick injection. The original signed server JAR is the execution
artifact; all40official pins and signatures are retained. OP policy now prepares
vanilla ops.json before startup. Runtime whitelist changes need vanilla op
administration or a restart; no hidden game hooks remain. Tick/data/time commands
and JVM counters retain monitoring, while injected food-use/per-tick-gap metrics
are intentionally retired. Frozen older adaptations remain historical.

Host original-JAR, telemetry/error-handling, OP-policy/vanilla-list-load,
preflight/help and normal-world81-chunk30second save/stop checks pass.080moblag
still includes allocation-pressurefullGC; this migration is not a proven latency
fix. Validate081onPS5before claiming vanilla-console acceptance or full endurance.
Server mods precede client work, with PS5_Vulkan retained as an unvalidated
client graphics candidate. See[migration](docs/vanilla-081.md).

### Build 082: defer metadata-triggered collections

081 now has console evidence of original-server readiness and authenticated
admission. The current capture still has visible full-GC pauses.082 changes only
the initial metadata GC threshold to128MiB, without preallocating that amount or
changing the game heap. The original signed server JAR and policy remain intact.
See[measurements and limitations](docs/pauses-081.md). Further heap-pressure and
code-cache pauses, persistence and two-hour stability remain unvalidated.

### Build 083: more heap headroom after joined-play GC saturation

The082capture has79heap-pressure full GCs, with repeated164–170MiB retained
inside an approximately174MiB effective heap.083tries192MiB maximum heap and
adds shared read-only process-limit reports. Original game bytes and policies
remain unchanged. Host81-chunk/60-second save-stop validation passes, with full
GCs and an initial chunk-generation stall still present. Actual PS5 memory and
latency comparison remains pending; no new passing milestone or two-hour pass.
See [measurements and limitations](docs/pauses-082.md).

### Build084: first Fabric loader/mod candidate

User reports lag-free083play and asks to try Fabric, then Paper, before the client,
with the two-hour run deferred.084packages hash-pinned Fabric Loader0.19.5 and
its dependencies plus a separate server-only smoke mod. Require actual mod
entrypoint execution and the Fabric target classloader; NBT/protocol checks use
that loader. Original game artifacts and the vanilla fallback remain intact.
Host preflight/readiness/save/stop checks pass; PS5 startup/mod execution/joined
play and real third-party mods remain pending. No ALL PASS milestone or sustained
capacity claim. See [Fabric details](docs/fabric-084.md).

### Build085: bounded native direct-memory fallback

084executes Fabric/mod entrypoints and admits a player on PS5, then aborts in C1
with a refused32KiB native allocation.085adopts runtime0101 while keeping all
084game/loader/probe/mod bytes and192MiB heap/C1 policies unchanged. Actual raw
allocator/direct-ledger host fault tests and exact target package checks pass;
PS5 kernel/cache/headroom/stability remain pending. No C1 OOM bailout or universal
native-allocation guarantee. See [evidence and limits](docs/native-memory-084.md).

### Build086: native ZIP/image allocation during saves

085raw direct mapping/release works on PS5, but chunk-save Deflater native
allocation fails and the server stops. Player-save and cold image decode errors
follow.086uses runtime0102shared-ledger fallback for ZIP/image buffers, with
unchanged heap/C1/game/loader/probe/mod artifacts. Actual JNI/ZipFS/shared-direct
and image controls pass on host; actual PS5 save/rejoin/stability remains pending.
The menu labels short compatibility work as Server play test, while full
endurance stays deferred. See [details](docs/save-memory-085.md).

Local disk usage: [storage policy and verified duplicate cleanup](docs/local-storage.md).
