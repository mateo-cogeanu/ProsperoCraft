# Build 267: automatic launch-cache recovery

Build 265 reports missing cache receipts following a Store reinstall. A full
Repair download restored launching and retained worlds/mods. The exact cause of
the missing receipts, and any relationship to the user's uninstall method, remain
unproven. The separate 26.1.2 Fabric loading-screen freeze remains unresolved;
267 retains 266's scoped diagnostic sampler, not a claimed freeze fix.

## Recovery behavior

Play first verifies the selected receipt's client/libraries and asset index as
before. Missing, malformed, wrong-version or failed verification triggers one
bounded quick recovery, followed by normal launch preparation. Quick recovery
reconstructs the receipt from publisher metadata: prefer the saved catalog and
checksum-matched saved version metadata; obtain missing metadata online. Offline
Play can recover with sufficient cached metadata/files and never requests network
access. Missing prerequisites produce a connect-online message.

Quick recovery hashes all launch JARs and the asset index. Assets receive one
no-follow presence/size check per file, reusing checked parent directories instead
of repeatedly walking all ancestors. Missing/truncated files are retrieved through
the existing bounded 1–6 worker pool, verified against publisher hashes before
publication. Unchanged assets are not read end to end. This is deliberately not a
full asset-integrity scan; same-size asset corruption requires Full repair.

Repair download opens the existing in-place selector with Quick refresh as the
first choice and Full repair as the second. Cancel restores instance focus. The
existing full path hashes every asset and retains cancellation/staging cleanup.
Its progress says Checking and repairing rather than claiming every completed MB
was downloaded. Quick progress counts structural/verification checks, with an
allocation for both phases so it cannot reach completion before launch checks.
Fabric cache validation runs before dependency resolution; invalid loader cache
uses the existing verified Fabric installer online. A valid Fabric cache is kept
without fetching a profile. Offline missing Fabric cache requires online repair.

Only shared cache metadata/payloads and the instance ready flag are updated.
Worlds, user mods, resource packs, configurations and accounts are not reset.
Existing cache-root/rollback selection is retained: no new storage migration,
cache purge, root switch or blind cross-root merge. If uninstall removed actual
payloads, they must be downloaded again; permission/full-disk failures remain real
errors. Recovery cannot recreate erased world data.

## Verification and remaining acceptance

Injected actual launcher/installer tests cover missing/malformed receipts without
network, missing/corrupt metadata, offline refusal, selective code/asset repair,
cancellation, same-size corruption via Full repair, both selector actions and
Cancel, automatic Play recovery and preservation of world markers/original mod
bytes. No private game cache or live account is used by host checks.

Physical 267 cache refresh, recovery after reinstall, normal/offline launch and
267's inherited world-loading diagnostic capture remain pending. No release or
Store update follows from host checks. Preserve released265 and local266 bytes.
