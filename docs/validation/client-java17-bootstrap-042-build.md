# Minecraft 1.20 Java 17 crypto policy directory test 042

PPSA99878/01.000.042 uses
[Java 17 runtime 85bb6e2](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/85bb6e2).
[Build 041](client-java17-bootstrap-041-build.md) isolated the failure to
the genuine JCE check for a readable policy directory. The original
policy files are in the signed package. The console report did not
identify which pathname call failed or its errno.

Patch 0022 retries following-stat and read-only access via a real
descriptor if the PS5 returns EPERM from the pathname operation.
The fallback checks metadata and close before accepting a regular file
or directory. The genuine JCE policy checks, provider preflight,
and the original game inputs remain in place.

A host sanitizer fixture exercised the actual fallback against real
files and directories, following symlinks, injected EPERM and EINTR,
and negative controls for missing paths, non-read modes, a FIFO and
close failure. The Java 17 target build, ordered patch checks and all
21 launcher host checks passed. Both signed binaries passed
verification. The eight update entries match the full archive.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `fd814bc32801179756e83cb6fd17c986feed12e898936a9aee9c7c90149c85bf` |
| Update from 041 | `cd8319af3692690d7f1a89a009dd7ecf5810bf8d0dcb373bfde2cdd561c50b8f` |
| Matching symbol ELF | `2e52bf91353d05cb8afb8038600c44fbb656a1c3ea2921d10153ca2e53453b80` |

Physical console testing is pending. Run rows 1–3 and check whether
provider initialization and the title screen complete. If the title
screen appears, quit normally and record whether the probe returns
to its menu or the title closes.
