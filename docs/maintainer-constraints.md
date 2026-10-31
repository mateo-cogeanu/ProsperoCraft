# Current compatibility constraints and open work

This is current maintainer guidance alongside [AGENTS.md](../AGENTS.md). The
chronological original is [archived and audited](documentation-history.md).
Historical observations retain their exact build scope; a later success does not
retroactively turn every prior candidate into a pass. Existing technical guides,
regression assertions and validation records remain authoritative for the scoped
implementation contracts below. Preserve those implementations even when disabled
or awaiting console acceptance.

## Current candidate and deferred goals

Published 167 was accepted for functionality/polish and explicitly released; broader
device/lifecycle/endurance coverage was not measured. Local 168 packages shared
tooling at source `8d9874ddda9a3c468d8f2dc5b1a64147b76a26f0`, SHA-256
`f069b642d326624a839b6ea5521e8042eec3d876fd4ceb089abba4af455c41d8`.
SDK, current-package/native-Java identity and both OpenAL relink checks passed.
**168 has no physical-console acceptance or release/Store authorization.** Preserve
its exact package/symbols/relink kit and accepted 167. See [168](client-shared-tooling-test-168.md)
and [167 acceptance](validation/client167-console-acceptance-2026-10-30.json).

The product goal remains polished playable Minecraft Java: responsive controls,
smooth rendering, audio, world play, persistence and stability. Menu startup is
an intermediate checkpoint. High settings are the goal; distance caps were only
diagnostic, not a final performance fix. Keep shadow quality at the user's explicit
100% setting; do not lower quality to claim a repair. Preserve working C1/G1,
audio/input and supported-version behavior. [Performance investigation](client-performance-investigation-117.md)
has no proven shader bottleneck; partial GC improvements are not endurance/leak
proof. Class/code retention under the [remark policy](client-remark-cleanup-100.md)
still needs long-session pressure checks. Keep098 draft unchanged.

Server two-hour endurance remains explicitly deferred; do not block authorized
client work on it or mark it complete. Home/favorites/quick-play and LAN hosting
remain deferred, preserving their source/data. Joining success is not hosting
acceptance. Microphone work remains deferred. Fabric precedes NeoForge; Forge is
not on the current roadmap. [Server endurance](endurance.md),
[instances-only policy](client-instances-only-095.md), [LAN diagnostics](client-keyboard-hosting-093.md),
[Fabric/Modrinth](client-fabric-modrinth-103.md).

## Identity, artifacts and branding

PPSA99874/content identity is shared by client/server, so installations replace one
another. Client versions began independently at 01.000.000; do not continue the
server counter or claim side-by-side installation. Preserve vanilla 083 and
Fabric 094/Paper 108 server fallbacks, earlier accepted client packages and archived
milestone scopes. Public packages provision original downloads on console rather
than bundling game payloads or preset instances. Keep isolated UUID game directories,
shared hash-verified cache and old worlds/settings. Unsupported capacity queries
mean unknown, not zero physical free space; `/download0/ProsperoCraft` and existing
4096 MiB data policy do not authorize migration/elevation or deletion.

Use approved artwork and pinned branding metadata via existing preparation and
`apply_branding.py` hooks. Retain all original/v2/v3 masters and supplied corner
logo. System presentation uses the supplied banner alone plus system-rendered
title, pinned 4K BC7 DDS/pic0/pic1; no AI redraw or composited title PNG. Preserve
the independent saved themes/backdrops and later user choices. [Presentation](client-presentation-096.md),
[themes](client-themes-cursor-121.md). Old fixed1080p and old Demo-only restrictions
were superseded by actual enumerated modes and supported authenticated/version
policy, not permission to invent arbitrary scanout or launcher support.

## Accounts and data safety

Use approved ProsperoCraft public client `f0c7635e-8d50-4d7e-afa3-d15db4a0a3d3`,
Microsoft consumers OAuth v2 device/token endpoints, `XboxLive.signin offline_access`
and `d=RPS` ticket. Preserve Xbox/XSTS, entitlement and matching-profile checks.
No borrowed app ID, auth bypass or unverified profile/UUID overrides. Legacy
unbound/other-client refresh files require fresh sign-in **before any token request**;
never relabel credentials. Keep the client-bound v2 AES-GCM header, fresh-app key
rotation/restoration and sign-out erasure; access tokens remain memory-only.
App-local adjacent-key encryption is not hardware-backed security.
[Approved auth](client-auth-approved-2026-10-29.md), [account storage](client-account-ui-091.md).

Retain the separate verified personal offline policy: token/entitlement/profile
verification by the local export helper; signed seven-day name/UUID/time proof;
only the public verification key may ship, never the private signing key/token.
Preserve Demo exclusions and explicit channel identity when exercising historical
channel variants, without recreating retired branches or treating old Demo
restrictions as today's authenticated main. [Offline](client-offline-084.md),
[channels](client-channels-delete-085.md).

Instance deletion now uses permanent Yes/No confirmation, precommit rollback and
postcommit cleanup; retain old Trash archives instead of purging history. No
current user Undo or durable power-loss guarantee. Duplication uses independent
folders/new UUID/marked journals, refuses links and preserves originals/account/cache.
[Deletion](client-home-library-094.md), [duplication](client-duplicate-triggers-116.md).
Content uninstall is explicit per-file with Cancel default and receipt rollback,
without automatic dependency cascades. Required updates are allowed for verified
managed Fabric dependencies; protect manual/unknown/modified/conflicting/downgrade
cases and roll back precommit failure. Do not force arbitrary upgrades, rewrite
mods or remove conflicts. Healthy offline instances need no dependency network.
Use the common safe Unicode single-component filename policy. [Uninstall](client-content-uninstall-icons-107.md),
[dependencies](client-auto-dependencies-108.md), [updates](client-dependency-updates-111.md),
[Unicode/defaults](client-default-controlify-unicode-115.md).

## Native ownership and supported behavior

Keep launcher presentation before JVM, mailbox-only UI exchange and staged game
native loading/C1/Main after Play. Preserve early audio reservation on the original
startup thread and actual same-owner successful VideoOut initialization. Launcher
uses private offscreen RADV plus its single native presenter, no toolkit audio or
launcher SDL/WSI backend. Require fences, cleanup and UI join before game handoff.
Only verified current-session original-Main clean shutdown plus SDL quit permits
OS LoadExec self-replacement; never invoke Main again in the old JVM or open CPU
VideoOut over retained WSI. [Toolkit history](client-toolkit-087.md),
[lifecycle history](client-launcher-082.md), [audio](client-input-audio-installed-106.md).

Physical mode selection follows real enumeration and supported refresh, with 60 Hz
fallback and FIFO-only presentation; no true uncapped VSync-off claim. Preserve
raw SDL joystick input, temporary-control opt-in and exactly-once handoff to real
Controlify to avoid double input. Launcher keyboard/mouse handles close before
game ownership. Semantic rumble cancellation/join/zero precedes close/handoff;
respect disconnect/interception/generation/opt-out, no stale replay. Preserve
haptic/gyro/audio and actual accepted trigger modes; approximate per-zone fallback
is disclosed and only follows the observed rejection, not arbitrary raw HID.
[Refresh](client-high-refresh-097.md), [controls](client-launcher-controls-skins-101.md),
[rumble](client-vibration-089.md), [triggers](client-buttons-triggers-117.md),
[desktop input](client-launcher-desktop-167.md).

Keep the scoped three-event Controlify SDL frontend, bounded connection queue and
explicit overflow failure; it is not full SDL isolation or a general API sandbox.
Use the original backend's existing-file handle lookup with exact resident SDL
sidecar/preflight matching all three facade pointers; do not restore the failed
missing-path assumption or class-loader-wide lookup. Retain original mod/game JARs.
[Event facade](client-controlify-event-isolation-164.md), [lookup](client-controlify-lookup-165.md),
[path/preflight](client-controlify-path-166.md), [keyboard layout override](client-controlify-keyboard-162.md).

Keep original Fabric/Knot/Mixin, shared parent LWJGL/OSHI systemLibraries and the
specific supported versions.26.2 Fabric became supported after 166/167 acceptance;
older pending warnings are historical. Snapshots default off while explicit saved
choices persist; reject unsupported future Java/ABI versions. Preserve real OSHI
6.9 overlay and 7.7.2 SPI provider, honest unsupported metrics and real CPU identity,
not fake clock/load or rewritten game factories. Iris/Sodium OpenGL requires a
context and remains guarded under the Vulkan renderer; keep files and recommend
supported Vitrail rather than pretending an OpenGL implementation. Distant Horizons
is a pinned upstream-source PS5 variant, never an installed-JAR rewrite; its own
render/save acceptance remains scoped. [Snapshots](client-snapshots-118.md),
[JNA](client-snapshot6-jna-119.md), [Iris](client-iris-vulkan-110.md),
[DH/native](client-native-input-storage-112.md).

## Runtime integration and unresolved evidence

Preserve descriptor-first canonicalization, native stat/accounting and opt-in 64 ZIP
handle budget with immutable-source/OPEN_DELETE exclusions and reopen costs.
EMFILE was reproduced without DH; exact title quota/leaking owner are unproven.
Accepted114 world play/reload does not prove every save lifecycle or universal FD
cap. [Save diagnostics](client-save-rumble-113.md), [ZIP budget](client-world-handles-114.md).

Keep genuine optional ImageIO raster/Disposer/LCMS, JNA/libffi, known resident aliases
and explicit alias-symbol scoping. No arbitrary loader/platform spoofing, complete
AWT/GUI/fonts/printing/JPEG, broad JNA/FFM/mod compatibility or blanket shader-pass
claim. Native thumbnail WebP/STB subset is consumer-owned. Reusable implementation
and default-off runtime fallback policies remain runtime-owned; consumer enables
only documented integration. Do not change heap/GC/global allocators or registry
defaults merely to address a specific scoped failure.

Retain every active 122–150 compatibility repair and diagnostic, including GLFW
original Vulkan ownership/callback bindings, bounded scratch/verifier/compiler-TLS/
network/sync fallbacks, SDL lock/storage failure handling, Mesa strings/RADV timeline
and mutex reserves, VMA locks, shaderc include lifetime, reserved presentation/mixer/
event workers and OpenAL Device/HRTF/discovery/Context ownership. Their paired
release, failure rollback, bounded/exhaustion, clock/attribute, wait and retained
ownership contracts remain mandatory in matching `docs/client-fabric-*.md`,
`client/ports`, tests and [legacy audits](tooling-sharing.md). Do not remove them
because an old work order says a feature was pending. Normal/replacement OpenAL
relinks, packaged source/header hashes and original publisher JAR controls remain
release-compliance checks. Read [SDL storage](client-sdl-thread-storage-161.md)
and [shaderc lifetime](client-shaderc-include-lifetime-160.md) before adjacent changes.

Diagnostics remain bounded, optional where specified, honest on failure and
separate from a fix. Preserve current/previous reports and exact run/build identity;
a stale trace or last shader return is not a captured crash PC. Do not infer a
resource quota/GC leak/native abort cause without evidence. Current and historical
validation caveats remain in `docs/validation/`; they are not archived completions.
The [LAN log-service follow-up](security-follow-ups.md) requires a separate runtime
policy decision; this cleanup does not change listener behavior.
