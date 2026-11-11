# Minecraft 1.20 Java 17 crypto policy enumeration test 043

PPSA99878/01.000.043 uses
[Java 17 runtime c27856b](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/c27856b).
[Build 042](client-java17-bootstrap-042-build.md) reached the genuine
JCE directory stream open and failed there. Patch 0023 replaces the
PS5 NIO libc directory stream with descriptor-backed enumeration via
the PS5 kernel. Java still reads the original policies from disk.

The Java 17 target build and ordered patch checks passed. In a host
JNI fixture, JCE and JSSE initialized through the patched native
directory functions using a host adapter for the PS5 directory ABI.
Sanitizer checks covered native record boundaries, alternate ABI,
and descriptor ownership. Both signed binaries passed verification.
The eight update entries match the full archive. All 21 launcher host
checks passed.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `bb0239debee0200608503d7de64bb6b2cc8c99a6d985aed37b4a4af535d0bb65` |
| Update from 042 | `9a563c93427b60d93f7a96c3e384dbde2a495a708fd6d75aed49ddb5b592d3b9` |
| Matching symbol ELF | `009832b730b710542580152a6cce06de933b5b6586dbd47e7c9a5560b876a29d` |

Physical console testing is pending. Run rows 1–3 and check whether
provider initialization and the title screen complete. If the title
screen appears, quit normally and record whether the probe returns
to its menu or the title closes.
