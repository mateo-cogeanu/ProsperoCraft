# Minecraft 1.20 Java 17 classpath path conversion test 040

PPSA99878/01.000.040 uses
[Java 17 runtime d438478](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/d438478).
Patch 0021 uses paired native scratch for temporary platform string
conversion buffers before operations such as checking whether a JAR exists.
[Build 039](client-java17-bootstrap-039-build.md) reported an OutOfMemoryError
from the native file attribute lookup, then shut down the VM successfully.
The exact allocation refusal and the title screen remain unverified.

The host JNI fixture checked five encoding paths, a real UTF-8 file lookup,
forced allocation refusal and paired release. The Java 17 target build,
ordered patch checks and all 21 launcher host checks passed. Both signed
binaries passed integrity verification. The 12 update entries match the
full archive.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `3df49cc5dd872e1f3bf8baded24bd49e11204cade819d2c93fde91f46157d6c3` |
| Update from 039 | `af4ab534e5595f5d104a58d45d0c9f987f156b5359f6b11edd23dd777cf5047a` |
| Matching symbol ELF | `bc7330929c8b765106af6fa8eb012dca707c73c2ce0ee5f6c832abf858c8629f` |

The maintainer reported a crash. The build 040 logs reached original
Minecraft Main. Minecraft wrote its own crash report during game
construction. It shows that the default JSSE context could not
initialize, with an earlier initializer error in `Cipher.getInstance`
on the Yggdrasil key fetcher thread. The deepest provider cause is
absent from that report. The earlier native file attribute OOM did
not recur in the retained run.

HotSpot's exit hook logged status -1. The subsequent SIGSYS worker
stack includes `VM_Exit::doit` and the instruction immediately after
the libc `exit` import call in `os::exit`. The title screen and normal
VM destruction remain unverified.
