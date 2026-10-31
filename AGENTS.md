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
