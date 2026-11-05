# Local216 — primary shared content, reports and temporary files

User clarifies that `/data/ProsperoCraft` should hold everything, with download0
allowed only as fallback if transfer, loading or verification fails.216 supersedes
local215's permanently diagnostic download0 use and its fail-closed selection
policy. It also removes normal instance-card READY/DOWNLOAD badges, retaining
only Coming soon and DEV TEST.215's instance-settings Back repair remains.

## Layout and early native routing

The primary layout is `/data/ProsperoCraft/library` (instances/worlds/cache/settings/
private account), `reports` (native/JVM/Java/game log evidence) and `tmp`.
Native bootstrap proves directory/file descriptor access, write/read and rename
before Java/core constructors. It configures immutable process storage/report
roots and existing OpenAL local-path/HOME/TMPDIR environment values. It does not
add a mount, elevation helper, kernel patch or universal permission assumption.
If native shared access fails, existing legacy report/temp paths remain available
and Java opens only a readable original fallback library, with a notice.

JVM startup/JIT/GC/error files and bootstrap home/tmp/work options select the
verified root. Java exceptions and the custom Log4j appender/session-shutdown
reader use the same report root. SDL breadcrumbs use the selected immutable
environment root. A separately named, consumer-owned instance of the existing
shader-fault recorder uses that root; the original compiled shaderc group stays
retained. Its forwarding, original-handler ownership and preopened-fd signal
handler are unchanged. OpenAL's original env adapter remains byte-identical and
receives the selected local path through its existing override mechanism.
No active primary-path writer targets download0; legacy paths remain explicit
fallback strings and the old library is read for migration. Diagnostics and bulk
content can choose fallback independently when their specific operation fails.

The reusable HTTP log allowlist has constructor-free bootstrap root configuration
from runtime[39f71e1](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/39f71e103864ec79c5d64fb1e36d7aefd40099f8).
Its defaults remain unchanged for other consumers, configuration freezes at
listener start and URLs still cannot choose arbitrary filesystem paths.
`client/launcher/report-runtime.json` pins the changed header explicitly over the
older namespace pin's shared-header hash; genuine JNI/VM objects and the120Hz
presenter pin remain unchanged. Storage routing normalizes exactly back to the
retained204 native bootstrap for policy comparison; only the documented storage
syntax/setup and existing333 reserve blocks are excluded from that comparison.

## Verified copy, load and fallback

Copy-before-switch migration retains originals and the bounded215 hash/size/time,
second-source-walk, link/refusal and resumable private staging rules. The stage
now must also parse and validate its library before a single directory rename
publishes it. Existing shared metadata is validated before use. Receipt paths
are already relative; a copied host cache is reopened and hash-verified from its
new root, without any JAR or receipt transformation.

No selection marker is written to legacy storage. A fresh successful primary
selection creates no legacy library at all. Failed access/copy/metadata loading,
conflicting libraries or verification returns the readable original library with
an explicit fallback notice; shared files are retained. If neither library can
be verified, startup reports failure instead of constructing a replacement over
unknown worlds. The fallback copy may be older; no backup synchronization or
recovery of already failed saves is claimed. Original encrypted account/key
backups remain private and must never be distributed.

The app keeps a256MiB manifest request for diagnostics/fallback availability,
rather than214's32GiB request. Normal shared files grow as bytes are written;
there is no app-created fixed-size shared image. This does not shrink/reclaim an
already enlarged legacy container or delete retained originals. Actual loader
access, allocation and storage capacity remain physical-console checks. No raw
backing-image access, forced resize, uninstall or automatic old-data deletion.

## Cards and Back

Supported normal cards show neither READY nor DOWNLOAD. Play/install readiness
and detail actions remain unchanged. Enabled1.21 Vanilla development cards show
DEV TEST; unavailable rows show Coming soon. Existing26.1.x normal cards stay
unbadged despite using the same graphics route. Actual model assertions and
Vulkan previews cover the three cases. Circle/desktop Back from instance
settings returns to the same detail screen; Back from detail returns to the grid.

## Checks and console procedure

Host assertions cover copy/resume/account/world/cache verification, corrupt
shared metadata/access failure fallback, conflicts, no fresh legacy writes,
source mutation/links/commit retry, explicit roots and normal/dev/unavailable
badges. The new portable native fixture runs actual directory/report/temp choice,
SDL breadcrumb, shader-recorder file and existing OpenAL env adapter with isolated
host roots; its cross-repository report hook is injected. Actual relocated HTTP
bytes/archive/freeze and64KiB stack/collector tests run in the runtime repository.
Native/source-only/target/package/hosted results are distinct in
[validation](validation/client216-primary-shared-storage-2026-11-05.json).

Install the whole216 app folder over the closed existing title and refresh loader
metadata. On first start, allow the verified copy to finish. Check Settings shows
the shared library root; verify instances, settings/account, world save/reload,
card badges and settings Back. Check current-run reports from the unchanged LAN
URLs, then test16GiB-policy imports with a real large pack, cancel/interruption,
normal Play and clean Quit/relaunch. Failed shared access/copy must display the
legacy fallback notice and preserve both locations. These remain physical tests;
no full10GB PS5 transfer, actual shared access, clean quit or endurance is implied
by host/target checks. Released212 and local213/214/215 stay retained. No release,
prerelease, Store submission or frozen milestone is authorized for216.

Final local artifact: `dist/candidates/client121-216/PPSA99874.zip`,127519033bytes,
SHA-256 `ddffd1b389ed81a9b904d76aba172e4fd43b9b283047ad1985761c92f3ce1973`,
from clean source `40005ddc01c0284182b3610f9bef3eaca9e08f85`. Signed integrity and
independent static/source audit pass;1311158bytes uncompressed growth over204.
Both hosted policy and native jobs pass at the exact build source.

The user now reports [Vanilla/Fabric26.2 crashes](validation/client262-crash-report-2026-11-05.json)
on an unidentified installed build. Current FTP is unreachable; current reports
are requested. This report is unresolved and is not treated as an exact216
regression or a fix established by storage/UI/host changes.
