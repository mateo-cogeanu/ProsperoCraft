# ProsperoCraft maintainer instructions

## Scope and publication

ProsperoCraft owns Minecraft client/server integration, launcher, artifact pins,
native consumer adapters, JVM launch policy and game validation. Reusable Java
runtime fixes, patches, registry/build/image/packaging tools belong in
[mateo-cogeanu/ps5-java25-homebrew](https://github.com/mateo-cogeanu/ps5-java25-homebrew).
Publish runtime fixes through that workspace's `python3 tools/sync_github.py
--message "..."`; carry the matching pin, rebuilt integration and validation into
this repository. Do not duplicate runtime implementations here.

The user authorizes public source publication after **every completed** source,
asset, documentation, configuration or script change: run relevant checks, commit
and push to ProsperoCraft before ending the turn, even with console tests pending.
Verify each push; report failures honestly and retry recoverable failures. Preserve
uncommitted/remote work; never force-push or rewrite history. Develop on `main`;
do not recreate retired `Temp_gametest`, `codex/demo` or `codex/offline` branches
or merge unrelated branches without a new request. The local checkout may still
be named `ps5-minecraft-java`; use canonical ProsperoCraft URLs.

Keep caches, downloaded game/mod JARs, generated builds/previews/logs, credentials,
account/session/key files and personal files out of Git. Public app artifacts omit
official game JARs **and asset objects**, using verified publisher provisioning.
Keep README status concise and accurate, banner/branding consistent, history in
CHANGELOG and scoped evidence in `docs/validation/`. See [documentation index](docs/README.md).

## Acceptance, history and releases

A host test, SDK build, package audit or human satisfaction report is not formal
ALL PASS. Record exact title/version/package SHA-256, dependency/runtime pins,
human console scope, independently retrieved evidence and pending checks separately.
Never infer FPS, stability, save/reload, complete teardown, broad mod/native support
or endurance from a narrower check. Do not rewrite frozen validation or infer
acceptance from `build-status.json`.

Preserve passing/failed candidates, symbols, exact packages, release assets/tags,
098 draft and original OpenAL relink inputs. Frozen source lives in the existing
[history archive](https://github.com/mateo-cogeanu/ps5-homebrew-history), not active
milestone folders. Do not recreate historical folders during sync. Freeze new
snapshots there only after exact-build human PS5 ALL PASS, with provenance,
checksums and original validation. Preserve active fixtures, unfinished/disabled
compatibility implementations and licensing tools. See [source organization](docs/source-organization.md).

**No new GitHub release or prerelease before the user confirms the exact build
works on a physical PS5.** Obtain explicit release/Store authorization for that
build; past authorizations are not permission for future candidates. Preserve
accepted bytes without rebuilding under the same identity. The specifically
withdrawn 154/155/156 hardware-test releases are historical exceptions, not a
standing deletion instruction; retain their local artifacts/source tags and all
other releases, including 153. Source pushes and local test builds remain authorized.

For an authorized binary publication, provide exact matching OpenAL corresponding
source/relink materials, notices, validation and SHA256SUMS; verify uploads by
independent downloads and exact normal/replacement relinks. Preserve GPL-3.0-or-later
rights, root LICENSE/NOTICE and upstream licenses/credits; add no advertising,
splash or noncommercial conditions. Credit mihawk-99/PS5_VKHomebrewUI and the
MultiMC/Prism icon contributors. No relicensing of game or upstream artifacts.

Store updates require explicit authorization. Update the existing PPSA99874
listing's version, artifact URL, digest and changelog; preserve its description,
credits and icon unless separately requested. Check applicable catalog rules and
artifact eligibility before submission. Submit and attach the catalog PR, then
**do not monitor** its CI, merge, deployment or live API unless newly requested.
Do not claim a submitted/merged PR is live Store availability. Root
`sce_sys/param.json` mirrors the published client; it need not match a newer local
candidate. No release, prerelease, Store action or branch merge is part of a
documentation cleanup.

## Compatibility, privacy and follow-through

Keep official game/mod downloads intact. Do not add or expand server-JAR rewrites,
bytecode hooks or replacement game classes. Existing derivative server work is
migration debt: remove it gradually only when validated runtime/harness/config
replacements work. Document remaining transformations; never silently drop a
required workaround or claim an original server while executing a derivative.
Use supported vanilla configuration/ops/administration for game policy. Disclose
upstream Fabric/Mixin behavior and Paper's separate upstream server accurately.
Retain EULA consent (`server/eula-consent.json`); the initial `--help` bootstrap
must not auto-accept it or claim server/world readiness.

Preserve the current constraints in [maintainer constraints](docs/maintainer-constraints.md).
Read the matching subsystem guide/validation before changing compatibility code;
its allocation, ownership, lifecycle and failure contracts remain requirements.
Do not treat old candidate holds, old app IDs or completed work orders as current
authorization. The [instruction audit](docs/documentation-history.md) records
supersession and archived context; unresolved work remains active.

When asked to retrieve probe logs, collect and inspect **current-run** reports,
then repair concrete issues within the authorized Java/Minecraft scope, check,
build as affected and publish to each owning repository. Keep causes unproven
until evidence establishes them. Use requested Safari/Cyberduck retrieval when
direct access fails; refresh stale listings and preserve first local retrievals.
Raw paths/reports stay local. Never log auth arguments, tokens/codes, responses,
headers or exception/cause text; diagnostics must be bounded and allowlisted.
Never publish refresh credentials, account-store keys, signed personal proofs or
private signing keys. See [security guidance](SECURITY.md) and [sanitized bug reporting](CONTRIBUTING.md).

## Checks and build discipline

Use [host testing](docs/host-testing.md), `tests/host-lanes.json` and
[host-test inventory](docs/host-test-inventory.md). For launcher/test-tool changes,
run `python3 tools/run_host_tests.py` (first use `--fetch-deps`); for affected scoped
native code also run `--lane native`. Python 3.10+ without optimization, complete
JDK 25, native host architecture and pinned host-only dependencies are required.
Use explicit options/JAVA_HOME/CC/CXX/LLVM_HOME/PATH/HOMEBREW_PREFIX; no private
cache fallback or developer-specific paths in supported lanes. Shared discovery
must be import-safe, fail usefully on missing tools, and never parse CLI at import.
Keep tests deterministic with injected transports/temp data, no real accounts,
secrets/live services/large game downloads. Keep required selection explicit;
file counts do not establish runnable coverage. Verify portability changes from
a source-only checkout, empty dependency cache and outside-root invocation.

Keep Actions read-only, bounded, SHA-pinned, without secrets, persisted checkout
credentials or `pull_request_target`. Inspect actual jobs for workflow changes;
report local, hosted and physical-console results separately. GPU/SDL/OpenAL,
SDK/package and downloaded-publisher checks have distinct prerequisites; one
Vulkan backend does not validate another. Do not rebuild the full app for docs
unless a build input changed. Run `python3 tools/check_documentation.py` and
`git diff --check` for documentation changes.

Current identity is read from `client/startup/param.json` via `tools/app_identity.py`;
keep dependency/runtime/probe/release identity distinct. Replace complete version
and label tokens, never bare digits that can alter historical hashes. Shared
bootstrap lives in `client/bootstrap`: retain explicit variant constants and
allocation-free initialization/lifecycle semantics. Keep legacy 122–150 wrappers
and specialized assertions in `tools/legacy_package_audit.py`; update migration
records/negative controls deliberately and include shared headers in future
source/relink exports. See [shared tooling](docs/tooling-sharing.md).


## Required shader release validation —2026-11-02

The user makes successful shader loading/rendering mandatory before release.
Preserve the existing exact-build physical-console and explicit-release gates.
Current199 reaches26.1.2Fabric/Iris world rendering but crashes entering
ComplementaryUnbound_r5.9.3 HIGH shadow rendering due to missing
com.sun.management.HotSpotDiagnosticMXBean. This is not shader acceptance.
Host tests, compilation logs or a working no-shader world do not satisfy the gate.
Record exact candidate/pack/profile and physical shader behavior; keep release,
prerelease and Store publication on hold until the required confirmation.

## Minecraft1.21.x research and generation isolation —2026-11-03

The user prioritizes1.21.x before NeoForge. Follow docs/client-1.21-plan.md and
client/1.21.lock.json; all twelve rows remain Coming soon until implemented and
validated independently. The supplied port prompt requires an explicit decision
before publisher-library Java overlays: original LWJGL3.3.3 cannot recognize PS5,
and unchanged333 Java/current343 JNI is incompatible. No approval is inferred
from source publication. Preserve current26.x bindings/groups/options and204.
Original game/library/mod JARs stay intact; no game remapping/transformations or
version/platform spoofing. Matching333 native groups need scoped JNI and a coherent
game/Fabric class owner, plus genuine platform/dispatch sources if approved.
Obfuscated clean-shutdown accessors must preserve the existing evidence/SDL/exit
gate. Older Controlify uses JNA SDL bindings: the26.x FFM property alone does not
establish controller/event isolation. Keep full-assets/Fabric/resource experiments,
actual package growth and PS5 validation explicit; retain204 ZIP budget8 and all
existing runtime/native ownership contracts. No new release/Store authorization;
exact-build physical shader acceptance remains mandatory unless scoped out.

## Approved1.21 Vanilla execution order —2026-11-03

The user approves the Phase A recommended matching333 natives and minimal genuine
PS5 Java platform/dispatch overlays. Implement and validate1.21.11 Vanilla first,
then the remaining1.21.x Vanilla releases. **Defer Fabric implementation/testing
until those Vanilla releases are good.** This supersedes the pending overlay
decision and Vanilla/Fabric-per-release sequence in the original research draft;
it does not imply hardware acceptance, shader scope-out or release/Store approval.
Publish reusable runtime isolation fixes first, then pin/integrate them here.
Keep original publisher JARs intact, all26.x decisions/native groups unchanged,
released204/frozen history preserved and each unproven release independently gated.


## Report transport and333 callback repair —2026-11-04

205physical1.21.11 initialization fails at original Callback.create: native closure
allocation returnsnull; Java heap exhaustion is not established. Reopened205HTTP
access also exits. Runtime report handler formerly reserves70,472bytes on every
request; fixed target frame5,704bytes,64KiB host fault/control tests pass. Shared
HTTP fix is runtime-owned. Consumer206 compiles a separate opt-in64page pre-JVM
closure reserve in333 only (1MiB at16KiB pages); mmapfirst, ENOMEMonly, real W->X/
libffi, pairedRW reset and failed-reset quarantine. Original343/provider objects,
heap/GC/ZIPbudget8 and original publisherJARs retained. Real x86_64 fault/3200
closure tests are host evidence; native allocation cause and exact206PS5startup/
HTTP/callback/world/save/quit/regression remain pending. No release/Store approval.


## Attached333 callback environments —2026-11-04

206 reaches original1.21.11 world creation/join, then fatal native state allocation/
key refusal in STB PNG write callback on a Java worker.207PS5 getEnv reuses genuine
JNI GetEnv for attached threads, retaining this group's async flag; no redundant
record/TLS setter there. Unattached native attach/destructor and foreign ownership
remain. Original PNG fault replay,64worker PNG cycles,own/foreign native attachment,
ASan/UBSan/XcheckJNI ownership and existing Zink checks pass. Exact207PS5world/save/
quit/endurance and26.x regressions remain pending. No new reserve/heap/GC/JAR policy,
release/Store approval or ALL PASS. See docs/client-1.21-207.md; raw reports local.


## Vanilla1.21.10 and selected-resolution candidate —2026-11-04

User reports2071.21.11 working and requests1.21.10 next. Preserve207 exact bytes;
positive feedback is recorded separately, not formal ALL PASS.208 enables only
1.21.10/.11 Vanilla; all121 Fabric and earlier releases remain gated. Genuine
OSHI6.6.5 CPU-only dispatch uses original interfaces/UNKNOWN, original JAR intact.
All Zink instances pass the launcher-selected size before SDL/GLFW initialization;
SDL query/surface honor it, with explicit refusal for unavailable inventory modes.
VideoOut additionally enumerates launcher720p/900p using existing buffer handling;
physical modes/presentation remain pending. Launcher keyboard navigation includes
all five action buttons; do not change ingame keyboard for this repair. Preserve
VM/ZIPbudget8/native333/343 ownership and existing release/Store/shader gates.
See docs/client-1.21-208.md and exact package validation before claims.


## Launcher page motion —2026-11-04

User reports208 working and requests horizontal page turns, theme side arrows,
continuous dropdown scrolling and L2/R2 pages.209 keeps vertical movement on each
instance page’s two rows, L1/R1 top tabs, L2/R2 previous/next pages. Preserve bounded
resident snapshots/list caches; never put a full Fields snapshot on a native stack.
Keep independent outgoing/current card state, visual-position pointer hits and
Reduced motion. Native launcher owns presentation/mailbox/lifecycle; no SDL/JVM or
game/native policy changes for this UI repair.208 exact bytes remain retained;
physical209 responsiveness/animation/input/game handoff is pending. Existing
release/Store/shader and Vanilla-before-Fabric gates remain.


## Launcher layout, refresh focus and card entry —2026-11-04

209 positive animation feedback also reports bottom clipping.210 content viewport
must cover existing controls through962px; fade begins below1005px. Startup notice
must stay out of page/card transitions and survive saved-account refresh. Automatic
refresh preserves current navigation; explicit sign-in keeps its existing return.
Instance entry expands the selected card into actual detail controls; L1/R1 tabs
and L2/R2 pages keep horizontal movement. Launcher-only trigger cue uses the existing
native ABI/basic effect and bounded haptic worker, honors Vibration preference and
resets before pad close; API refusal is nonfatal, physical feel/reset pending.
Keep game/native/runtime policies and all earlier gates/packages. See
 docs/client-launcher-refinements-210.md; native lane now includes portable haptics.


## Whole-launcher120 target and adaptive page detent —2026-11-04

User requests whole-launcher120FPS and moderate selection panels.211 removes33ms
redraw gating and opts into pinned runtime64fe7c7 native support/configure/vblank
verification plus fast tiled publication. Replace the old renderer once; preserve
manifest0x40, buffers/ownership and checked restore/handoff. Report measured FPS,
not a120pass inferred from refresh/host tests. Menus use moderate600px minimum,
64px rows/28px text/24px vertical padding and shared pointer geometry. Card entry/
exit use the same live backdrop with continuous glass/opacity curves, preserving
selected library card. Startup/login210 behavior remains. Adaptive page detents
prearm only available sides in a narrow native travel zone, release on press and
rearm on neutral; no uniform constant resistance or post-turn warmup pulse.250ms
stale watchdog/opt-out/refusal/shutdown remain. Exact211 PS5 FPS/feel/reset/visual/
game handoff pending; preserve210 and all release/shader/Vanilla-first gates.
See docs/client-launcher-120-211.md and matching validation.


## In-place selectors and live theme preview —2026-11-04

User reports211 very smooth.212 selectors retain/dim their source view instead of
page-turning; themes remain undimmed and preview hover/focus without saving until
confirm, Cancel restores. Icons use all32 icons in an8x4 named-free grid
with shared pointer geometry and spatial controls. Text-only resident snapshots
retain parent/nested menu state; no large automatic Fields copy. Adaptive detent
force4 retains localized travel/release/neutral/reset policy. Remove the extra
expanding-area glass quad to address black flash; do not regress the existing120
presenter/login/notice/game policies. Late211Mac haptic fixture failed a15ms wait;
212 uses bounded actual-state polling, not production timing changes. Exact212
PS5 visuals/feel/handoff remain pending. Preserve211 bytes and release gates; see
 docs/client-launcher-selectors-212.md and matching validation.

212 removes Modrinth/CurseForge logo assets and embedded pixels at user request.
Original CC0 Amethyst/Compass retain IDs4/25; preserve other icon IDs and upstream
notices. Package audit requires all six inherited logo assets absent.


## Authorized212 release —2026-11-04

User accepts the exact212 launcher and explicitly requests ProsperoStore release.
Publish retained212-final package SHA256
 d97e530ea67838ef806e8fa88731d399aa9ce1ae661b091daff5eaacfe3f75a7
without rebuild, with matching source/relink materials. Preserve existing listing
description/credits/icon; update version/artifact/digest and release changelog.
No exhaustive212 shader/game/device/FPS/endurance or formal ALL PASS is inferred.
Earlier202shader/quit and204release acceptance remain scoped; future candidates
retain explicit physical/release gates. Submit catalog PR, do not monitor after
submission. See docs/validation/client212-console-acceptance-2026-11-04.json.


## Larger streaming browser imports —2026-11-05

213 raises browser file limit to1GiB,30minute total/30second idle with64KiB
streaming. Derive browser size/label/timeout from server constants; retain owned
staging, no-overwrite, cancellation/ENOSPC/timeout cleanup and mutation ownership.
Resource/shader ZIP metadata bounds65534entries/16MiB; mods8192/4MiB unchanged,
ZIP64/split/path rejection retained. Host129MiB real uploads with64MiB heap and
injected deadlines are scoped evidence; physical large-pack transfers/loading
remain pending. No USB implementation or release/Store change; preserve212 and
future exact-build gates. See docs/client-browser-uploads-213.md.


## Explicit10GB browser pack request —2026-11-05

User requires more than1GiB, citing10GB packs.214 supersedes local213:16GiB cap,
long request lengths, size-scaled deadline (minimum30min;512KiB/s plus5min),
30second idle, bounded pack ZIP64 up to100000entries/16MiB; mods retain8192/4MiB
and ZIP64 refusal. Request32GiB title-local downloadDataSize for214, preserving
identity/data paths; no migration/elevation/deletion/image manipulation. This
supersedes the earlier4GiB request for this large-pack goal. Loader expansion,
actual10GB transfers/pack loading remain physical tests; sparse host10GiB offsets
are not full transfer proof. Preserve213/212 and release gates. See
 docs/client-browser-uploads-214.md.


## Shared storage and parent Back —2026-11-05

User rejects thick32GiB allocation, requests ordinary homebrew data folder and
identifies ShadowMountPlus.215 prefers /data/ProsperoCraft only after Java
write/read/rename/list/attribute/canonical probes. Authorize verified/resumable
copy-before-switch from legacy, retain all originals, bound traversal, reject
links/conflicts and fail closed if selected shared data later disappears. No
elevation/loader patch/backing-image manipulation/deletion.256MiB diagnostic-only
downloadDataSize replaces32GiB request; lowering does not reclaim existing
allocation. Preserve private account backups and never publish their files.
Circle/desktop Back from instance settings returns to the same detail page.
Physical migration/capabilities/worlds/large packs pending; preserve212 and all
local candidates/release gates. See docs/client-shared-storage-215.md.


## All primary storage and explicit fallback —2026-11-05

User clarifies all content/reports/tmp should prefer /data/ProsperoCraft, while
download0 fallback is explicitly allowed if transfer/load/verification fails.
216 supersedes215 fail-closed/always-legacy-diagnostic policy: native early proof,
shared library/reports/tmp, verified readable migration, no legacy marker writes,
readable original fallback with notice, all originals retained.256MiB fallback
request stays; no existing container shrink/deletion claimed. Runtime report-root
API is separately pinned39f71e1; defaults/VM/namespace/native game groups retained.
SDL breadcrumbs and separately named fault recorder route selected immutable
root; Log4j and shutdown evidence move together. User removes normal card READY
badges (only Coming soon/DEV TEST);215 settings Back remains. Physical shared
access/migration/reports/quit/large packs pending; preserve212 and all candidates/
release gates. See docs/client-primary-shared-storage-216.md.


## New26.2 crash report —2026-11-05

User reports both Vanilla26.2 and Fabric26.2 crashing while216 is prepared.
Installed build/phase/cause remain unknown. Current FTP endpoint is unreachable;
current address/enabled service and reopened launcher requested. Retrieve current
reports and proceed with concrete repairs when access is restored; do not use old
runs or host/static success as a26.2 fix. Preserve212 and exact local candidates.
See docs/validation/client262-crash-report-2026-11-05.json.
