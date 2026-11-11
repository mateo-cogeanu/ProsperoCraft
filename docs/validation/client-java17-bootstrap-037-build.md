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

The maintainer reported that row 3 ran for a while before crashing.
All six reports were recovered, including HotSpot's fatal error log.
The trace identifies 037 and records two successful aligned 16 MiB
mappings. The third returned `ENOMEM` and the original reservation
path also failed. HotSpot reported the failure while defining a class
in Minecraft startup, about 38 seconds after VM startup. The core
dump path was skipped and the VM reached the abort hook. There was
no title-screen, row 3 completion or VM shutdown result.

The report shows 31.69 MiB of non-class metaspace committed across two
16 MiB nodes, about 5.13 MiB of class space committed out of 32 MiB
reserved, and 717 KiB of code cache used out of 48 MiB reserved.
The Java heap had about 126 MiB in use. The kernel resource that caused
`ENOMEM` remains unknown.
