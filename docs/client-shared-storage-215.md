# Local215 — normal shared storage and instance-settings Back

The user rejects214's32GiB fixed reservation and asks to use the ordinary folder
used by other homebrew. They identify ShadowMountPlus as their launcher.215
prefers `/data/ProsperoCraft` for the entire library, cache, instances, worlds,
settings, account files and browser uploads after proving actual Java access.
This is ordinary file storage: the app does not create a32GiB backing image for
bulk content. The upload cap remains16GiB with214 ZIP64/deadline policy.

ShadowMountPlus1.7 source currently mounts `/data` into title sandboxes, but a
mount does not establish every Java metadata/directory operation. See
[source](https://github.com/drakmor/ShadowMountPlus/blob/cef1579a496240f14d0aad28397b02f283a25b7a/src/sm_fakelib.c).
No elevation helper, kernel patch, loader change or unconditional permission
assumption is introduced. The root selector rejects links and proves create,
write/read, rename, attributes, listing, canonicalization and cleanup in a
private temporary folder before choosing shared storage. Explicit
`ps5.launcher.root` overrides and host/test constructors remain available.

## Selection and migration

An existing download0 library is copied through64KiB buffers into an owned
`/data/.ProsperoCraft-migration` tree. Matching ownership is required for resume.
Existing copied bytes are reused only after hashes match. Every file is checked
against source size/time/SHA256; a second full source walk and destination hash
pass reject missing, additional or changed source content. Bound traversal to64
levels and262144entries; links/special files are refused. Account key and encrypted
session travel together with private file/directory permissions where supported;
no credentials or paths from the migration are printed or published.

A same-filesystem directory rename publishes only the complete verified tree.
The legacy tree is never deleted. Failed/interrupted copies retain original data
and resumable owned staging. Files that conflict with staging or two already
populated libraries are preserved and refused rather than merged. A precommit
failure leaves the original library active with a notice. Retried commit after
an interruption uses its verified marker. Power-loss durability is not claimed.

A small legacy marker records that shared storage became active. After that,
missing/unavailable shared storage fails closed instead of silently reopening
stale backup worlds or constructing an empty replacement. Before the first switch,
refused shared access leaves an existing legacy library available with a notice;
a fresh install requires shared access rather than downloading large game data
into the diagnostic container. Settings already displays the selected real root.
The original encrypted account backup remains in the preserved legacy tree; treat
that tree as private account/world data. Do not distribute it.

## Reservation and existing allocation

215 requests256MiB for the existing native/JVM diagnostic, temporary and small
selection-marker use of `/download0`, replacing214's32GiB request. Bulk game data
and browser uploads use shared storage after successful selection. Native reports
and their retention/retrieval paths remain unchanged.

Lowering the manifest request is **not** an automatic shrink or reclamation of an
already allocated download0 container. The user must not be told that existing
32GiB was freed. Upstream [storage notes](https://github.com/abhi245y/PS5LM-Plus#install)
also report no space reclaimed by lowering the value on13.00. No unmount, resize,
backing-image deletion, uninstall or automatic original-data cleanup is performed.
Reclamation requires a separate verified loader-supported procedure after console
migration acceptance and backups. Shared storage consumes actual written files
and retained migration copies; it is not a promise that the SSD has enough space.

Install the whole215 folder over the closed existing app, refresh loader metadata
and launch. Keep it open during the initial copy; native launcher presentation
continues independently. Check Settings' data root, instances/settings/account,
world bytes and save/reload before considering legacy cleanup. If copying cannot
finish, the notice identifies legacy storage as active. No physical215 access,
migration, reclaim, disk-space measurement or10GB pack-loading result is claimed.

## Back navigation and scoped checks

Circle and the desktop Back action from instance settings return to the same
instance's detail screen, with its Settings action selected. A subsequent Back
from detail still returns to the instance grid. Existing keyboard/picker/content
returns keep their immediate parent behavior.

Host tests exercise real proof/copy/hash/rename operations, injected partial copy,
resume, account decrypt/world preservation, source mutation, symlink refusal,
unowned staging, conflicting libraries, commit race/retry, sticky selection,
missing/inaccessible active storage and explicit override. Actual Java model tests
cover Circle/desktop Back and existing keyboard/selector transitions. Source-only,
target package/static ABI and hosted checks are recorded in
[validation](validation/client215-shared-storage-2026-11-05.json). Local215 only;
released212, all older packages, original JARs and game/runtime groups are retained.
No release, prerelease, Store update or new frozen milestone is authorized.

Superseded before delivery by [216](client-primary-shared-storage-216.md), following
explicit all-report/tmp routing and readable legacy fallback clarification.215
bytes remain retained; its fail-closed/diagnostic policy is not216 behavior.
