# Local213 — larger browser uploads

The user supplied screenshots of the128MiB browser cap after a resource/shader
pack import report and requests a fix.213 increases each file limit to1GiB,
with30minutes total transfer time,30seconds idle-read tolerance and a31minute
browser deadline. Browser label, local file check and timeout are generated
from the server constants to prevent drift. Multiple files remain sequential
and each retains progress/cancel. No USB import implementation is included.

The existing64KiB file stream and owned same-directory staging remain. No full
file buffering, overwrite, extraction or automatic pack activation is added.
Cancellation, disconnect, deadlines and full-volume errors remove staging and
release the launcher mutation lock. Actual target free space is unknown; writes
remain authoritative. Upload permission is checked when the request starts;
the existing15minute browser session is unchanged and may require pairing again
after a long transfer. Successful upload does not establish pack compatibility.

Resource/shader pack directory bounds increase from8192entries/4MiB to65534entries/
16MiB before ZipFile construction. This bounds metadata allocation; it is not a
64KiB total-memory claim. Mod JAR directory bounds remain8192/4MiB. ZIP64/split and
unsafe paths remain refused. Archives stay intact and are not extracted.

Host verification streams actual129MiB ZIPs through real HTTP to resourcepacks
and shaderpacks with only64MiB Java heap, then compares exact file bytes. A9001
entry resource pack succeeds; the same archive exceeds unchanged mod limits.
Mutated ZIP64 sentinel/directory-size controls are refused before allocation.
An injected sink advances elapsed time past the former2minute deadline and
succeeds, then beyond30minutes and confirms408/no install/no staging/lock release.
Existing pairing, origin, malformed bodies, duplicate/no-overwrite, full-volume,
path/link and lifecycle checks remain. These are host results, not PS5 storage,
Wi-Fi throughput, browser/device or game pack-loading acceptance.

213 retains released212 UI/runtime/native groups, original game JARs and Vanilla
1.21.10/.11 gates. Earlier1.21 and all1.21Fabric stay deferred. Build213 is a local
console candidate only;212 release/Store assets remain unchanged. No release,
prerelease, Store update or new frozen milestone without exact console acceptance
and explicit authorization. Check a real pack above128MiB, progress/cancel,
interrupted cleanup, existing files, subsequent game loading and library return.

[Validation](validation/client213-browser-uploads-2026-11-05.json) records exact
source/package checks and pending physical tests.
