# Local179: microphone enabled for play, no launcher microphone menu

The user confirms178 microphone/SVC functionality and explicitly asks for GitHub
and ProsperoStore publication with the launcher microphone menu removed and input
available by default. See [exact178 functional acceptance](validation/client178-console-acceptance-2026-10-31.json).
No full per-device/mute/route/endurance matrix is inferred from that report.

179 removes the instance-management Microphone action, its toggle/test page and
its native hit targets. Browser uploads fills that action row; Done/Delete stay
at the bottom. Controller/keyboard navigation has no invisible microphone focus
stop. No other page numbers or instance/world/account data are migrated.

The production launcher now always calls the same proven178 enable/preparation
path before starting supported gameplay. It does not consult the old saved
microphoneEnabled key. Gson ignores that obsolete key while preserving all other
settings, instances and worlds; later ordinary saves omit it. No native AudioIn,
worker, input-format, port-retention or hardware-mute implementation changes.
The app never calls an unmute or routing/gain setter. SVC activation/PTT/mute
configuration is not overwritten. Native capture remains unavailable until the
launcher prepares it for Play; automatic preparation is a product launch policy.

The underlying microphone probe/JNI and native enable API remain for focused
host/developer diagnostics. Removing the menu is not permission to discard the
working implementation or its lifecycle tests. A narrow injected Microphone
boundary lets deterministic host launch tests verify unconditional preparation
without using host microphone hardware or faking native PS5 success in production.
Tests cover legacy false settings and repeated launches plus the updated browser/
Done/Delete controller and mouse navigation. The target audit checks the actual
shipped settings/model bytecode and removal of the old native menu captions.

## Release/Store preparation and exact-build gate

178 is accepted for microphone functionality.179 is a modified package and must
receive its own physical-console confirmation before a release or prerelease is
created. This follows [AGENTS.md](../AGENTS.md): “No new GitHub release or prerelease
before the user confirms the exact build works on a physical PS5.” Source pushes,
local179 packages and prepared catalog metadata are authorized and continue.

A release/Store update is requested for this feature set. Preserve178 and all
older release assets/tags. Keep current root sce_sys/param.json and published
README release links at167 until179 is actually approved/published. Prepare exact
179 package/symbols/OpenAL source-relink materials/checksums and release notes;
never rebuild accepted179 bytes merely for publication. On approval, update the
published root identity, create the179 release with matching notices/validation,
independently download/hash the assets and verify both relink paths. Update only
the existing PPSA99874 catalog version/artifact URL/SHA; preserve description,
credits and icon. Release notes supply the changelog. Submit the catalog PR and
stop; do not monitor its CI/merge/deployment/liveStore after submission.

The smallest179 console check is: instance management has no Microphone page;
Play prepares input without a toggle, SVC speech still works, the physical
controller mic button mutes/unmutes correctly, and leaving/rejoining still works.
These exact modified-build results are pending at preparation time.

Fast15/native7, source-only/empty-cache/outside-root lanes, refreshed startup host,
actual179 package audit and both exact OpenAL relinks pass. Linux/macOS policy and
native Actions pass on25f987f. [Release preparation/asset checksums](validation/client179-release-preparation.json)
records these separately from console confirmation. The local catalog179 worktree
has only the existing app's version/URL/SHA changed;233catalog unit tests(2skipped)
and164offline records pass. No release, tag, catalog PR or Store availability is
claimed. All possible local preparation is complete before requesting the final
exact-build physical check.

## Exact179 gate satisfied

The user now confirms “179 works as requested” in response to the specified
automatic SVC input,physical mute/unmute,removed menu and leave/rejoin check.
See [179 acceptance](validation/client179-console-acceptance-2026-10-31.json). This
supersedes the preparation-time gate above for this exact package only. The
initial build/preparation validation remains an immutable pre-test snapshot.
Publish accepted bytes unchanged under the existing explicit release/Store
authorization; no formal ALL PASS/endurance or new milestone is inferred.

## Publication completed

The exact tested179 package is published in the [179 GitHub release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.179)
with corresponding-source/relink,build/console validation and checksums. All5assets
were independently downloaded and verified; both downloaded-kit relink paths match
the accepted ELF. [Store PR #991](https://github.com/darkxex/ps5-homebrew-catalog/pull/991)
is submitted with only version/URL/SHA changed and no post-submission monitoring.
[Publication record](validation/client179-store-publication-2026-10-31.json) preserves
checks,source provenance and the distinction between submission and live Store
availability. This supersedes preparation-time pending statements for exact179.
