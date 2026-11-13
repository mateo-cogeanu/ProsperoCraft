# Minecraft 1.20 Java 17 startup trace test 044

PPSA99878/01.000.044 uses the same
[Java 17 runtime c27856b](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/c27856b)
as [build 043](client-java17-bootstrap-043-build.md).
Build 043 initialized both providers on PS5 and entered the original
Minecraft Main call. The retained files did not identify a failure
inside Main.

The probe enables HotSpot class initialization and GC logging in
`java17-startup-044-<pid>.log` under the probe's report directory.
Uptime and thread IDs help correlate the last recorded events. The
VM print callback preserves dedicated file output and flushes each write.
This candidate adds diagnostics. The original cause remains unknown.

A host Java 17 run verified the unified logging option. A sanitizer
fixture checked that the actual print hook keeps dedicated streams
separate and redirects standard VM output to the bootstrap report.
The target package passed signed binary verification, and the four
entries in the update ZIP match the full archive.
All 14 native host checks passed. The fast lane timed out on the
instance worker on its first run, then passed all 21 checks on retry.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `6caa7554295bfc85edf79904aa6f3911d85c7747d426ca0dc00da52b7247a9f9` |
| Update from 043 | `b492160f7699e5e9f634b0601256642362c2d65518cea30bf49d32d108a3ab82` |
| Matching symbol ELF | `5394effcbad0c694403e35c8dcba8df022ee43cf1470b378f4c785bf4696ffbf` |

Physical console testing is pending. Run rows 1–3. If it fails again,
retain the startup trace and reopen the same probe at its menu if the
title closed.
