# Prospero Store reservation — ProsperoCraft

The existing PPSA99874 reservation was added by mateo-cogeanu in
https://github.com/darkxex/ps5-homebrew-catalog/pull/353 and merged on2026-10-17.
The catalog repository URL now resolves under darkxex/ps5-homebrew-catalog.

On2026-10-25 the user selected ProsperoCraft and requested the supplied app icon,
name and updated Minecraft Java client/server/native-runtime description.
The reservation update is submitted at:

https://github.com/darkxex/ps5-homebrew-catalog/pull/737

Status:MERGED2026-10-25 (PR737,mergedAt12:49:50UTC). Verified during the
client044handoff:upstream apps/PPSA99874.json contains ProsperoCraft and the
description below. Live store/website propagation was not independently checked.
Only apps/PPSA99874.json changed.

Name:ProsperoCraft

Description: Minecraft Java Edition client and server on PS5, powered by native OpenJDK 25; vanilla, Fabric and Paper server playtests, with client startup under development.

The161-character description stays within the catalog's200-character limit.
It distinguishes server playtests from the still-unvalidated client startup/menu.
Reservation status remains unchanged:source_repo,artifact_url,sha256,icon_url,
version and license stay null. No full game package or development artifact is
uploaded to the catalog. Current reservation rules require icon_url null and
show the shared Coming soon art;the supplied ProsperoCraft icon is used in future
local app packages and project branding,not forced into an invalid reservation.
A later downloadable listing can supply its pinned public icon and release data.

Local python3 -m catalog check passes with138valid records and0errors/warnings/
notices. The update branch is codex/prosperocraft-branding in the user's catalog
fork. The original reservation belongs to this same account.

Consumer artwork/name live in assets/branding and tools/apply_branding.py.
Future client/server packagers apply them while preserving title/content identity
and build versions. Frozen validation/release assets and already-built038 stay
intact. Branding changes do not establish client/menu acceptance.

## Client050 continuation and eventual release

PR737MERGED and the upstream ProsperoCraft record were reverified via GitHub
on2026-10-25 during the050handoff. All six optional release/source/icon/license
fields remain null. This check does not establish live website propagation.
See [the complete050handoff](handoff-prosperocraft-client050.md) for current logs,
repair steps and release readiness. A downloadable listing must follow actual
accepted client behavior,verified public app-only release artifacts,pinned icon/
checksum,and working provisioning for omitted original JARs AND startup assets.
Existing milestone JAR-only provisioning is not yet complete startup provisioning.
Provide exact matching OpenAL source/relink materials for the accepted binary;
do not publish the full local game-containing development ZIP. Re-read current
upstream submission/artifact/versioning rules before converting this reservation.

## Downloadable launcher082 — 26 October 2026

The user explicitly requested Store publication of exact082. Release
[01.000.082](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.082)
is public, with an installable app-folder ZIP, matching OpenAL corresponding
source/relink kit, validation records and SHA256SUMS. No game JARs/assets are
bundled: the native launcher downloads verified originals on the console.
The existing reservation conversion is
[PR811](https://github.com/darkxex/ps5-homebrew-catalog/pull/811); no new title ID
or duplicate listing. Only its apps/PPSA99874.json record changes.

Local catalog check passes for144records with0errors/warnings. Online verification
passes for the exact public ZIP digest,01.000.082 content version and pinned icon,
with0errors/warnings. All five assets were downloaded and hashes rechecked; the
downloaded relocated OpenAL kit reproduces the exact packaged ELF. See the
[publication record](validation/client082-store-publication-2026-10-26.json) and
[release guide](releases/client-launcher-082.md). Remote CI/merge/deploy is tracked
on PR811; this paragraph records submission, not a claim of live propagation.

Only26.3SDLdemo is enabled; Microsoft approval/full-account access remain pending.
Exact082PS5quit/relaunch,input,checkbox/world persistence and audio/performance
regression checks remain pending. The publication request does not establish
a formal ALL PASS or replace frozen milestones. The earlier reservation-only
paragraphs above describe historical state and are superseded by this submission.

Final remote check: submission validation, static release scan and offline tests
all PASS. PR811 is OPEN and awaiting maintainer review; the live Store page still
shows Coming soon. The bot declined auto-merge because its first-release API
ordering selects older065, despite /releases/latest correctly returning082 and
082having the newest publication timestamp. Evidence is in the PR body. Upstream
push permission is unavailable; reviewers were requested by its workflow. No
older release was removed/replaced and no catalog automation was bypassed.

## Fresh submission814

At the user's explicit request, PR811 was closed and replaced by
[PR814](https://github.com/darkxex/ps5-homebrew-catalog/pull/814), from fresh branch
`codex/prosperocraft-082-resubmit` based on current upstream8566a5f. Only
apps/PPSA99874.json changes; it is byte-identical to the previous submission.
The exact082release/assets remain unchanged. Local catalog validation passes
for144records with0errors/warnings. The new PR reruns the automated checks; a
fresh PR does not itself change the catalog's release-ordering logic. This
submission supersedes earlier PR811 references as the active Store request.

PR814's fresh submission validation, release scan and offline tests all PASS.
The bot again reports “the release is not the newest of
mateo-cogeanu/ProsperoCraft” and leaves the PR for a maintainer. Recreating the
PR did not resolve the release-order issue. Current state is REVIEW_REQUIRED;
darkxex and Marice are requested reviewers. Original packages/assets unchanged.

## GPLv3 and fork credit

At the user's request, ProsperoCraft's original code/build scripts are now
explicitly GPL-3.0-or-later, consistent with the existing source headers. Root
LICENSEcontains the standard GPLv3 text;NOTICEidentifies copyright
“mateo-cogeanu — ProsperoCraft” and retained upstream credits. Distributed forks
must preserve applicable copyright/license notices and meet GPL source and
modification-notice requirements. No advertising or splash-screen condition is
added. Upstream code keeps its own license; official game files are not relicensed.

GitHub detects GPL-3.0 and activePR814now declaresGPL-3.0-or-later instead of
Unlicensed. The existing082ZIPalready includes the fullGPLv3text; its bytes,tag
and frozen validation remain unchanged. Separate license/notice/checksum release
assets accompany the explicit project grant. This follow-up supersedes earlier
Unlicensed metadata while preserving its historical validation records. See
[license publication record](validation/client082-license-2026-10-26.json).

## Fixed1080p release083

The user explicitly requested Store publication of083after the reported082
resolution/click issue. [Release01.000.083](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.083)
is public with the unchanged083candidate ZIP, fresh matchingOpenALsource/relink
materials, validation records and SHA256SUMS. ProjectGPLv3and attribution notices
are included in the ZIP. The existing Store listing update is
[PR819](https://github.com/darkxex/ps5-homebrew-catalog/pull/819), replacing082with083
and declaringGPL-3.0-or-later. This is an update of the listed app;814remains merged.

All five upload hashes/sizes match; downloaded assets and exact native relink
are verified. Local catalog144records and online083digest/version/icon checks
pass with0errors/warnings. RemoteCI/merge/deploy is tracked on819.
See [publication record](validation/client083-store-publication-2026-10-26.json)
and [release guide](releases/client-resolution-083.md). Exact083PS5clickalignment,
demo-world,retainedaudio/smoothnessandquit/relaunchremainpending. No newALLPASS
or frozenmilestone is claimed;082andallhistoricalreleaseassetsremainunchanged.

PR819remote follow-up: submission validation, release scan and offline tests all
PASS. The bot left it for a maintainer under its release/newest-release eligibility
notice. Current state OPEN/REVIEW_REQUIRED;darkxex and Marice requested.083is
public onGitHub;Storeavailability is not claimed before merge/deployment.

## Authenticated096 update — 2026-10-27

The user requested exact096publication after merging Temp_gametest into main.
Release: https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.096
Existing-listing update: https://github.com/darkxex/ps5-homebrew-catalog/pull/859

This supersedes the historical coming-soon submission. The083listing is already
released;096requires this update's approval/deployment. Local format and online
digest/contentVersion/icon checks pass. See the096publication record for asset
digests, package preservation, human feedback and pending console tests. GUI and
icon credits are included in both descriptions.

PR859merged on2026-10-27 at13:55:45UTC. Upstream deployment is queued; the live API still returned083when checked afterward. Do not equate the merged record with a completed Store deployment.


## 098 held for stutter validation — 2026-10-27

No098catalogPRwascreated,pushedorsubmitted. User requires confirmation that
stutters are fixed before Store publication. GitHub098uploadcompletedwhilethe
holdarrived;098immediatelyreturnedtoDRAFTandverifiedasdraft. Uploaded asset
hashes match; no new publicStoreavailability is claimed.096remains the published
release. See validation/client098-publication-hold-2026-10-27.json and
client-stutters-098.md. Quieterlogging alone is not a confirmedGCfix.


## Accepted100 release and Store update — 2026-10-27

Build100received explicit acceptance for improved gameplay smoothness and a
request to release. This supersedes the prior hold for exact100. Full GitHub
release01.000.100preserves the tested package bytes and includes matchingOpenAL
source/relink materials,validation and checksums. All5uploads and downloaded
assets match;downloadedkit reproduces the exactacceptednativeELF.

Existing-listing update: https://github.com/darkxex/ps5-homebrew-catalog/pull/861
Release: https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.100

147recordformatchecks,227offline tests(2skipped),onlineartifactdigest/version/icon
checks pass. PR861wasOPENwithremotechecks pending atinitialinspection;Store
availability requiresmergeanddeployment. PublicnotesretainGUI/iconcredits and
state long-sessionmemory/lifecyclelimitations.098draftandolderreleasesunchanged.
See validation/client100-store-publication-2026-10-27.json for currentstatus.


PR861 merged2026-10-27at15:26:03UTC as68b9b53d0ed2521d9166eabd7445864decf0b8c3.
Submissionvalidation,release-scan,offlinechecks,developer-bumpeligibility andmerge
allPASS. CatalogdeploymentCI40530933028isrunning;liveAPIstill096atthelastcheck.
Merge alone is not confirmation of liveStoreavailability.


DeploymentCI40530933028completedSUCCESS. Canonical liveProsperoStoreAPI and a
fresh-query request both nowreturn version/content_version01.000.100,release100
andSHA256b905d80a3b21502c2c1c9672db7833cd38f3582c35835e13c087667a0a0e7f65.
The Store update is live;this is independent verification aftermerge/deployment.


## Accepted101 functional release — 2026-10-27

The tester confirms all requested101account,launcher,input andskin fixes work
and requests Store release. Full GitHub01.000.101preserves the exactacceptedZIP.
All5uploaded/downloaded assets match;downloadedOpenALkit reproducesacceptedELF.
Java0124source/acceptance are published inJava repo;consumerrelease remainshere.

Release: https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.101
Existinglistingupdate: https://github.com/darkxex/ps5-homebrew-catalog/pull/865

147records and230offline tests(2skipped)pass;onlineartifactdigest/contentVersion/
iconchecks pass. PR865initialstateOPEN,submission/offlinePASS,releasescanstill
running. LiveStore availability requiresmerge/deployment. Currentevidence:
validation/client101-store-publication-2026-10-27.json.100andolderassetsunchanged.


PR865merged2026-10-27at16:20:17UTC as0fef2c99b789b04b83769742370635ddc0270268.
Allrequiredsubmission/release-scan/offline/developer-bump/mergechecksPASS.
DeploymentCI40539919062running;liveAPIstill100atlastcheck. Awaitactualdeployment
beforeclaiminglive101availability.


DeploymentCI40539919062completedSUCCESS. The liveProsperoStoreAPI nowreturns
version/content_version01.000.101and exacttestedpackageSHA256
c784e08043314b02ff49cc9bb2a7c1643f558b35b1cee23ba278091a5d05e131.
101is live,independentlyverifiedaftermergeanddeployment. Humanreaffirms all
requestedfunctionsaccepted;broaderendurance/memory/lifecycletests remain scoped.


##117 publication — 2026-10-28

Exact117release is public, with five downloaded/hash-verified assets and matching OpenAL source/relink materials. Existing description and credits are unchanged; only catalog version/artifact/digest are updated, with release changelog. Catalog PR: https://github.com/darkxex/ps5-homebrew-catalog/pull/896

User requested no PR monitoring. Checks, merge, deployment and live Store availability are deliberately uninspected. See validation/client117-store-publication-2026-10-28.json. No new console ALL PASS or frozen milestone is inferred.


##119 snapshot release — 2026-10-28

Exact accepted119is public with five downloaded/hash-verified release assets and matching OpenAL source/relink kit. The exact shipped library classes verify snapshots off by default/missing setting and preservation of saved choices. Description, credits and icon stay unchanged; version/artifact/digest and release changelog update the existing listing.

Catalog PR: https://github.com/darkxex/ps5-homebrew-catalog/pull/907

No monitoring of CI/merge/deployment/liveStore is performed, per user preference. See validation/client119-store-publication-2026-10-28.json. Functional feedback is recorded without inferring full JNA/endurance coverage or a new Java milestone.


##120 approved-app authentication release — 2026-10-29

Exact120 is public with five downloaded/hash-verified release assets and matching OpenAL source/relink materials. Changelog explains the switch from Mojang's application ID to ProsperoCraft's own approved app and the required one-time fresh sign-in. Store description/credits/icon remain unchanged; snapshots stay off by default.

Catalog PR: https://github.com/darkxex/ps5-homebrew-catalog/pull/923

No PR/check/merge/deployment/liveStore monitoring is performed per preference. No new live120auth/restore result or ALL PASS is inferred from release authorization. See validation/client120-store-publication-2026-10-29.json.
