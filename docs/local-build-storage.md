# Local build storage cleanup —2026-10-31

The user explicitly requested removal of obsolete local test builds to recover
disk space.103 old candidate/local-test/withdrawn hardware-test directories were
removed. Historical notes saying those local binaries are retained describe the
state at the time of those tests; they do not establish current local availability.
Existing validation records remain preserved, rather than rewritten.

Retained working copies are local candidate173 (package, matching symbols,
corresponding OpenAL source/relink ZIP, checksums and validation) and accepted
launcher167 as recovery. Frozen passing snapshots in accepted/milestone/history
storage, original GitHub releases/assets/tags and project source were preserved.
No release, Store change, game/mod transformation or runtime behavior change was
made. Worlds, account data and key material were preserved; small local build
records/key files from discarded folders remain under ignored cleanup-records.

Duplicate baseline files were removed only after comparing full SHA-256 with the
canonical workspace copy. Extracted relink kits were removed only after every
file matched a retained ZIP with valid CRC. Original ZIPs remain; extract the
corresponding source/relink ZIP into a temporary folder when needed. Old generated
test/preview/relink-check caches were discarded and may need regeneration before
running optional prepared-build audits. No full app rebuild was run for cleanup.

macOS transparent compression and independent copy-on-write clones compacted
retained symbols and old logs while preserving logical bytes and filenames.
Final checks compare affected retained files with their original SHA-256 values.
Metadata operations on compressed clones must preserve the compression flag;
clearing that flag without decompression can hide the data fork. The cleanup
caught/restored this flag on affected clones and verified their original hashes.
Always verify final bytes after all metadata operations, not only before them.

The detailed filesystem journal remains local and ignored. No raw logs, personal
files, dependency caches, private keys or game assets were uploaded. This was a
one-time cleanup, not an automatic retention job. Future builds can recreate
caches; avoid copying entire build/dist trees for test baselines when a source-only
checkout and protected-input hashes suffice.

## Substantial cleanup —2026-11-08

At the maintainer's request, a further local cleanup recovered approximately
12 GB of actual free space, leaving about 13.4 GB free at verification. The
initial `df` report was about 1.1 GiB free. APFS sharing and delayed reclamation
mean logical file totals and phase-by-phase free-space deltas do not add up to
physical savings. The former approximately 63 GiB `dist` total mixed generated
staging with retained packages, symbols and compliance materials; it was not a
single disposable cache.

- Removed 27 obsolete generated 249–273 build trees after preserving small build
  recipes/audits and verifying matching retained symbols. One differing symbol
  file was retained separately rather than discarded. Build 274 onward remains.
- Archived six 249–254 candidate trees into a local compressed archive. Every
  file was checked against its original SHA-256 before loose generated binaries
  and staging were retired. Original checksums/audits and recovery pointers remain
  beside the candidate folders. This archive includes duplicate extracted files;
  it is not itself a frozen milestone or a public release.
- Removed five extracted release source/relink kits only after all their files
  matched retained original ZIP contents. Release ZIPs and current 274/279 kits
  remain. Optional old relink checks may require extracting their retained ZIP.
- Replaced 1,815 byte-identical generated files with independent APFS clones.
  Full SHA-256, mode, flags and extended attributes were checked; original mtime
  was retained. These are independent files on write, not shared mutable hardlinks.
- Retired the two obsolete failed-client binary archives covering builds 024–061.
  Their inventory/checksum manifests and all contained diagnostic JSON/text were
  retained locally. These failed binaries are no longer recoverable locally from
  those archives. Passing/frozen packages and GitHub releases were not retired.

Final checks verified 114 retained release-asset checksums, 22 passing full-package
hashes against their validation records, and build 279 package/source-ZIP CRCs.
Each deduplicated file was also verified after replacement. The current source,
canonical runtime/toolchain caches, release assets on GitHub, frozen history,
worlds, accounts and keys were preserved. Unrelated Downloads and application
caches were inspected for size only and left unchanged.

An initial whole-batch candidate archive exceeded temporary free space and was
removed incomplete, with its originals intact. Subsequent batching verified the
six-candidate archive described above. Further candidate archiving was not used
as the primary cleanup method because shared APFS data can make a new compressed
archive consume more physical storage than the loose copies it replaces.

Detailed hash inventories and recovery information remain ignored under local
`build/storage-cleanup-2026-11-08`; candidate recovery archives remain under
`dist/candidate-archives`. No game/runtime behavior, app version, GitHub release
or Store listing changed, and no physical-console retest is needed for this
local-file cleanup. Only this maintenance record is published.

## Complete dist retirement after verified NAS backup —2026-11-08

The maintainer then explicitly requested recovery of the entire output folder,
including frozen builds once recoverability was established. All 46,949 files
(61.45 GB logical) were backed up to a new private NAS directory, with full
network read-back and per-file SHA-256/size/mode verification before deletion.
The local `dist` directory is now empty. The observed additional free-space gain
was 42.8 GB; the Mac had about 56 GB free afterward. Existing NAS contents were
untouched. Exact frozen bytes and private recovery archives remain in that backup.

This supersedes the earlier local-availability statements above. Restore cold
packages explicitly before historical prepared-package audits; see
[artifact recovery](local-artifact-recovery.md) for private-backup instructions,
pinned public recovery and validation. Source and current build inputs remain
local. No remote release, Store listing or game/runtime behavior changed.
