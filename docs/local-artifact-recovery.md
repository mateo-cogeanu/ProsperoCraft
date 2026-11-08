# Recovering cold local artifacts

On 2026-11-08 the maintainer explicitly requested retirement of the complete
consumer `dist` directory after establishing recovery, including frozen packages.
The maintainer supplied a private NAS backup destination and required all existing
NAS contents to remain untouched. All writes were confined to one newly created,
uniquely named backup directory. No existing NAS files were replaced or removed.

## Complete private backup

The verified archive contains 46,949 original files, totaling 61,450,531,466 logical
bytes, including frozen full-local packages, debug symbols, corresponding source,
relink kits, candidate recovery archives, original validation and private cleanup
records. The compressed archive is 13,241,462,391 bytes. It is held off the Mac.
The archive and its detailed private inventory must not be uploaded publicly.

Before local deletion, the entire archive was read back over the network and
decompressed. Every file's SHA-256, size and mode, directory inventory and symlink
target were checked. All source file states were checked again before retirement.
The backup has its own `manifest.json`, `verification.json` and `RESTORE.txt`.

The exact private location is recorded locally in ignored
`build/dist-retirement-2026-11-08/backup-location.json`. The maintainer designated
the backup share; ask for that location if moving to another computer. Do not
create a public release to replace this private backup: full-local packages can
contain downloaded game files and private cleanup/key material.

To restore the complete original layout, run from the consumer repository root,
substituting the mounted private archive path:

```sh
set -o pipefail
zstd --long=30 -dc /mounted/private/backup/dist.tar.zst | tar -xpf -
```

For an individual historical regression, select only its recorded paths with
`tar -xpf - dist/milestones/EXACT_FOLDER/EXACT_FILE` instead. Compare restored
files with the private manifest and original validation hashes. Do not overwrite
newer local outputs; restore into an empty temporary tree first when paths already
exist. Optional historical package tests need their original cold artifacts
restored explicitly. A current rebuild does not replace the exact tested bytes.

## Public release copies

Some local files also have independent public recovery. The
[pinned public recovery manifest](validation/dist-recovery-2026-11-08.json)
records 664 original paths matching 231 published GitHub assets by SHA-256 and
size. Each download URL returned HTTP 200 with matching Content-Length during
the audit. Draft/unavailable assets were excluded. This is an uploaded-asset
digest and availability check, not a claim that every remote body was downloaded.

List known public copies without downloading:

```sh
python3 tools/restore_release_artifacts.py --list
```

Restore an explicitly selected public input, for example the old export baseline:

```sh
python3 tools/restore_release_artifacts.py --path dist/releases/client204/client204-openal-source-relink.zip
```

The helper streams to owned temporary storage, checks the written file's exact
size and SHA-256, and publishes it only on success. Different existing files are
preserved. Healthy existing copies need no network. Unlisted paths require the
private backup; app-only GitHub packages do not establish recovery of a different
full-local ZIP. There are no implicit bulk downloads.

## Verification and resulting local state

The local directory was left empty. Free space increased from 13,187,645,440 bytes
at backup start to 56,005,287,936 bytes after retirement: an observed gain of
42,817,642,496 bytes. Compression and APFS sharing explain why this differs from
the logical file total. Finder briefly recreated `.DS_Store` during removal;
that generated view metadata was removed after all backed-up artifacts were gone.

Source, Git history, remote releases/Store, runtime/toolchain caches and current
build trees were preserved. Both retained 274 and 279 link response files still
resolved all 109 absolute paths each and had no `dist` input dependency. This is
an input-presence audit, not a fresh application rebuild or PS5 validation.

All 21 portable host checks passed after retirement in 42.4 seconds. The new
recovery test passed from outside the project in a source-only copy without a
dependency cache. One actual public validation JSON was restored into a temporary
tree and rehashed. An earlier full host run hit an instance-worker timeout while
the backup was running; the post-cleanup full rerun passed without launcher changes.
No physical-console retest is required for this local storage/tooling change.
