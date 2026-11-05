# Local214 — browser imports for packs above10GB

The user clarifies that1GiB is insufficient because packs can reach10GB.
214 supersedes local213 with a16GiB per-file cap, long HTTP lengths, genuine
bounded ZIP64 resource/shader validation and a32GiB title-local storage request.
Neither local candidate changes public212 or its Store listing. No release,
prerelease or frozen milestone is authorized for214.

## Transfer and metadata bounds

Uploads retain64KiB streaming, same-directory owned staging, sequential files,
progress/cancel and no-overwrite. Deadline scales with advertised size: at least
30minutes, otherwise size at512KiB/s plus5minutes; browser adds1minute. This is
an allowance, not measured throughput or a minimum speed guarantee. The16GiB
maximum permits about9hours11minutes;30second idle reads still time out. Browser
limit/label/deadline parameters derive from server constants. No full-file
buffering, extraction, game-JAR modification or automatic activation is added.
The existing15minute paired session is unchanged: a request admitted while
paired can finish, but a long transfer may require re-pairing before subsequent
requests. Closing management still cancels it.

Classic and ZIP64 pack directories are inspected with fixed small buffers before
ZipFile allocation. Check locator, single-disk identity,64bit nonnegative offsets,
record extent, classic/64bit agreement, directory non-overlap and100000entries/
16MiB metadata. Malformed, split, unbounded or inconsistent directories are
refused. Mod JARs retain8192entries/4MiB and ZIP64 refusal. A large archive does
not imply the pack will fit GPU memory or load with the selected game/shader mod.
See [PKWARE ZIP specification](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT),
sections4.3.14–16. No archive contents are extracted during validation.

## Persistent storage

The earlier4GiB request could not hold a10GB file plus game data.214 raises only
its requested `downloadDataSize` to32768MiB; title/content IDs and
`/download0/ProsperoCraft` remain. Startup diagnostics refer to the actual app
manifest, and full-volume messages no longer claim4GiB. There is no migration,
manual backing-image change, forced reformat, cleanup, elevated path or deletion.
This request is required by the user's explicit10GB pack goal. Actual expansion,
quota and usable capacity must be checked on the console; no free-space number
or successful resize is invented. The existing
[storage investigation](client-storage-080.md) and upstream
[loader/storage report](https://github.com/abhi245y/PS5LM-Plus#install) explain
why a full app/metadata update is needed and why drive free space alone is
insufficient. The latter reports growth on13.00, not acceptance of this console.

Install the whole214 app folder over the existing title while closed, preserving
its data. Refresh the loader's metadata and relaunch; do not uninstall, delete
app data or resize the image manually. Validate existing instances/worlds first,
then upload the large pack through the paired browser. If storage refuses the
write, preserve data and retrieve current diagnostics. Pack loading is a separate
compatibility/memory test, not established by successful transfer.

## Scoped verification

Actual129MiB resource and shader HTTP uploads run with64MiB heap and compare
exact bytes. A sparse ZIP64 fixture places a valid readable pack entry's central
directory above10GiB, exercising long seek/size/locator handling without writing
10GiB of host disk data. This is not a full10GiB network/disk transfer test.
Another ZIP contains65537entries. Mutated64bit offset/size/count/disk controls,
a max65535byte archive comment, cap+1 header refusal and an interrupted declared
10GiB body exercise bounds/cleanup. Injected elapsed time tests former-deadline
success and maximum-duration refusal. Existing auth, origin, path/link, duplicate,
ENOSPC and launcher lifecycle checks remain. No numeric throughput, PS5 storage
growth, large real-pack rendering or exhaustive endurance claim.

[Validation](validation/client214-browser-large-packs-2026-11-05.json) records the
exact candidate, source, host/target checks and remaining physical tests.

Final local214 artifact: `dist/candidates/client121-214/PPSA99874.zip`,
127478126bytes, SHA-256
`996d6650152340fe43604ca1b6c54b82c68f0428d058e1f73f681c913cffee17`.
Built from clean source `4c155c06c9673e258843ff95d245c10615810b01`.
19fast/12native checks and19source-only outside-root checks pass; target compile,
signed integrity, ZIP CRC and independent package audit pass. Both hosted native
jobs pass; hosted policy jobs were in progress when inspected. No physical214
10GB transfer/loader growth/pack loading or public release is claimed.
