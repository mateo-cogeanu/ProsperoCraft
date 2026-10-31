# Documentation migration — 31 October 2026

The [existing history archive](https://github.com/mateo-cogeanu/ps5-homebrew-history/blob/5b509375924ddf4664be3ab35087ce9f0c6dc96d/documentation-2026-10-31.md)
now indexes 83 historical launcher 075–092 host previews, nine original guides,
nine linked validation records, original AGENTS.md and three license/attribution
files. Original relative paths live under `prosperocraft/_documentation/2026-10-31/`.
Source commit: `2762970c88756c6179f585bf018bf000994d5872`; archive commit:
`5b509375924ddf4664be3ab35087ce9f0c6dc96d`. The
[migration receipt](validation/documentation-migration-2026-10-31.json) records
per-file provenance/bytes/mode/SHA-256 and references. A fresh network clone passed
the complete archive verifier and comparison of all 105 migrated files before any
active screenshot removal. Run the archive's `python3 verify.py` to reproduce it.

## What was classified

The starting tracked launcher previews totaled **39,171,064 bytes** (83 files;
21 referenced in nine guides). All tracked text, Markdown/HTML/relative links,
badges/READMEs, scripts/generators/tests, release docs and repository site/workflow
configuration were inspected. No GitHub Pages configuration or maintained site
consumer of these images was found. Preview generators write ignored `build/`
outputs and do not read the archived copies. Several unlinked images are scripted
UI states, not garbage; all are preserved with their preview family. Source and
visual/metadata inspection confirmed invented fixture profiles/device codes.
No private local file or raw report was copied.

All branding/icon assets, banners, current release illustrations, native/toolkit
fixtures, compatibility implementations, license/relink tools, original downloaded
artifacts in ignored caches and frozen validation records were retained. Nine
historical guides now point to their exact original archive versions, so existing
README/changelog links still work. Their linked validation stays active unchanged.
No release asset, tag, package or Git history was deleted or rewritten. Historical
source organization and its original pinned archive commit remain unchanged.

## Instruction audit and precedence

The original AGENTS was 135,365 bytes/1,960 lines. Its complete bytes are archived;
[the paragraph audit](validation/documentation-instruction-audit-2026-10-31.json)
indexes every prose paragraph with original line range, checksum, category and
current guidance destination. Current instructions are in [AGENTS](../AGENTS.md)
and [maintainer constraints](maintainer-constraints.md); the archived AGENTS is
historical narrative, not a work queue or authorization to publish old builds.
Technical guides and unresolved implementation obligations remain active.

| Original instruction family | Effective disposition |
| --- | --- |
| Consumer/runtime ownership and every-change publication | Mandatory in current AGENTS; integrate/publish fixes to both owners as affected |
| Frozen folder preservation | Preserve bytes, tags, validation and packages; latest source migration moves frozen source to existing archive, never recreate active folders |
| Original game/mod JARs and server migration debt | Intact originals, no expanded transformations; preserve required workarounds until validated replacements work |
| EULA, GPL and OpenAL rights/attribution | Consent retained; no automatic acceptance; exact source/relink/notice obligations remain mandatory |
| Server-before-client work order/two-hour prerequisite | Later user explicitly permitted client work and deferred endurance; test remains outstanding |
| Demo/Offline branch split and Temp_gametest-only work | Later authenticated main merge/branch retirement supersedes routing; preserve variant policies/history, do not recreate branches |
| No-token-persistence/old auth IDs | Later approved-client-bound refresh storage supersedes old persistence/ID plans; no bypass or credential relabeling, secrets stay local |
| Old Home/Undo/fixed1080p/version limitations | Later instances-only/permanent-confirmed deletion/enumerated display and accepted supported-version policy applies; old source/data retained |
| Snapshot default on | Later default off supersedes it; explicit saved choices retained and shipped policy checked |
| No managed dependency upgrades | Later explicit scoped verified-managed updates supersedes it; unknown/manual/conflicting/downgrade cases protected |
| Stutter hold and exact100/101/later acceptances | Each acceptance is build-scoped; preserve098 draft, pending long-session checks and quality goal; no blanket performance acceptance |
| Earlier unvalidated prerelease/publication permissions | Latest exact-build physical-console gate applies to every future release/prerelease; explicit historical exceptions do not carry forward |
| Store polling/old submission work orders | Later no-monitor preference applies after PR creation, unless newly requested; retain existing description/credits/icon |
|166/167 scoped acceptance and168 local packaging | Preserve accepted bytes/scope;168 remains pending with no release/Store authorization |
|122–150 and later native compatibility/diagnostics | All implementations, tests, bounded ownership/failure contracts and pending validations remain active |
| Portable host workflow and shared tooling | Current explicit lanes, portable discovery, clean-copy checks, bounded Actions and specialized audits remain required |

Repeated old "current handoff" directions are historical. Use current identity and
the relevant subsystem guide rather than resuming a superseded candidate. The
original requirement to append chronology is superseded by this explicit cleanup
request; no current operating requirement was dropped solely for age or length.

## Changelog, security and publication boundaries

CHANGELOG.md is intentionally retained byte for byte (224,891 bytes). It is useful
ordered build history with release qualifications; no arbitrary size target or
unjustified split was applied. README gains contributor/security/documentation
navigation, without a product/version/support claim change.

With explicit user authorization, GitHub private vulnerability reporting was
enabled and API-verified. [SECURITY](../SECURITY.md) links the actual private channel;
no contact decision remains outstanding. The unauthenticated LAN log-service
exposure has a separate [follow-up](security-follow-ups.md); runtime code/policy
was not changed. Runtime source did not change, so its sync allowlist needs no
modification. ProsperoCraft has no documentation sync script that recreates these
assets. A repeated runtime sync was inspected: it publishes only runtime workspace
allowlisted source, not this consumer tree.

This change improves the active tree, not historical Git disk usage. Tracked documentation/assets started at 56,858,218 bytes across 663 files;
83 historical image files alone account for 39,171,064 bytes. Current AGENTS is
129 lines (8,557 bytes), with detailed constraints and audit indexed separately.
Exact final tracked before/after totals and checks are in the migration receipt. No application rebuild
was needed: no packaging input or active fixture changed. No new console test is
required for documentation; physical validation of 168 remains pending. No GitHub
release, prerelease, Store release or branch merge is part of this migration.
