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
