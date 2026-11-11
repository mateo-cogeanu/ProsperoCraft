# Minecraft 1.20 Java 17 metaspace reservation test 037

PPSA99878/01.000.037 uses [runtime cd756dd](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/cd756dd)
with patch 0020. Java 17 tries an anonymous mapping for a new metaspace
node with its final size and required alignment. The normal reservation
path is retained if the PS5 refuses the request or does not honor the
alignment. The VM trace records the outcome. This probe also passes
`-XX:-CreateCoredumpOnCrash` to skip the native core dump path check
while retaining its fatal error log. Heap settings, class image,
Parker leases and original publisher inputs are unchanged from 036.

[Build 036](client-java17-bootstrap-036-build.md) initialized original
Minecraft Main and hit a native mapping OOM at the 16 MiB metaspace
node reservation. The subsequent SIGSEGV included core dump reporting
frames. The exact kernel refusal is unknown.

The Java 17 target build and LTS patch replay passed. The extracted
mapping helper passed ASan/UBSan checks with a real anonymous mapping
and controlled kernel responses for success, refusal, ignored alignment
and cleanup refusal. The host Java 17 VM accepted the core dump flag.
All 21 launcher host checks passed. The signed binaries passed integrity
verification, and all eight update entries match the full archive.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `054de15a31ae59cf0e710db649fe56570ffc360676ab6eee1902e1f926236a9d` |
| Update from 036 | `665a3d51896b1c7df94880f81758eb870d2173a4bcc67f71b7d9d5ca1cc556f9` |
| Matching symbol ELF | `bd47857abd5ec2bc995f31dc6ddeed9b627e64700a5eb3214696c0b02a44759b` |

Physical console validation is pending. Run rows 1–3. If the title
screen appears, quit normally and check row 4. If row 3 fails, reopen
the same build at its menu to preserve the reports.
