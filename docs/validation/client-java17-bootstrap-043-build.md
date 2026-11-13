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

The maintainer reported a crash. The retained build 043 reports show
that both genuine JCE and JSSE initialized, and the probe reached
the original Main call. There is no row 3 return, row 4 result or
VM exit status for this run. The game log is empty. The fault and
fatal JVM reports did not grow, and the game crash directory contained
only the earlier build 040 report. The failure boundary within Main
and the cause remain unknown.
