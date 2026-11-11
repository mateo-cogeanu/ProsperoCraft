# Minecraft 1.20 Java 17 TLS initialization and title exit test 041

PPSA99878/01.000.041 uses
[Java 17 runtime d438478](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/d438478).
[Build 040](client-java17-bootstrap-040-build.md) reached game construction
and reported a default TLS context initialization error. The earlier
failure at the classpath file check did not recur in the retrieved run.
The underlying provider exception remains unknown.

The probe now checks the default Java cipher provider and JSSE context
before calling original Main. This uses genuine JCE and JSSE, requires
no network request, and records the first error's class and bounded
stack frames without printing its message. Minecraft retains its normal
TLS and authentication behavior.

After a terminal HotSpot exit, the probe logs the original status and
requests title exit through `sceSystemServiceLoadExec`. If the platform
call returns, the probe logs its status and holds for report retrieval.
Normal Main return still follows the existing JNI return and VM
destruction path.

Host Java 17 passed provider initialization and reproduced a first
initializer error with a deliberately missing crypto policy, without
logging the policy path. The host exit-hook fixture verified the exit
request and refusal handling with stubbed PS5 APIs. The target ELF links
the system-service import. Both signed binaries passed verification.
The six update entries match the full archive. All 21 fast and 14
native host checks passed.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `60356617d1c5e9424438cb8bd3283d3e7cbdec94fb5d4e36bd7a1a2dba9b5d05` |
| Update from 040 | `5d69b582674ef018e833948c7a6b89fb6be504c6ddecc79c1a3405d02c17f4c3` |
| Matching symbol ELF | `d84944610d9954fef68b6e91335888eb845bec112765f6d86aaee7f3c8412eb8` |

Physical console validation is pending. Run rows 1–3. If the title screen
appears, quit normally and report whether the probe menu returns or the
title closes. If row 3 fails, preserve the probe menu and retained reports.
