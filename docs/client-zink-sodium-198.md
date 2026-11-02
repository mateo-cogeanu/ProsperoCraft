# Sodium version-check testing —198

The [197 console record](validation/client197-console-launch-crash-2026-11-02.json)
identifies a launch failure on26.1.2Fabric0.20.1 with original Iris1.11.4 and
Sodium0.9.2. Sodium explicitly refuses LWJGL3.4.3+4 because its compiled version
check expects3.4.1. This occurs before original game GL context creation. The
subsequent rejected shutdown audit, nonzero VM exit and native signal are retained
as a separate error-exit failure; no clean quit is inferred. Two real launcher
queue drains/barrier destroys complete during handoff, which is narrower than a
game Quit Game result. All-six196 quit crashes and slow world creation remain open.

## Explicit experimental policy

198uses Sodium's upstream `sodium.checks.issue2561=false` configuration only when
an exact candidate resource is present, the development channel enables Zink,
and the selected game is26.1/26.1.1/26.1.2Fabric. It is applied before original
Knot/Main initializes Sodium. Missing/invalid resources, Vanilla, released channel,
26.2+Vulkan and other versions do not change that property. Existing caller
properties are untouched outside scope. All other Sodium checks stay unchanged.
The marker is packaged only by `package_zink_sodium.py`; old candidates and normal
packages retain their policies.

[Upstream PreLaunchChecks](https://github.com/CaffeineMC/sodium/blob/dev/common/src/boot/java/net/caffeinemc/mods/sodium/client/compatibility/checks/PreLaunchChecks.java)
uses the exact-version gate and
[BugChecks](https://github.com/CaffeineMC/sodium/blob/dev/common/src/boot/java/net/caffeinemc/mods/sodium/client/compatibility/checks/BugChecks.java)
exposes the individual system property. Upstream warns that LWJGL internal ABI
can change; opting out is permission for an experimental test, not a compatible
ABI guarantee. Actual original mod bytecode is checked separately below.

LWJGL **continues to identify as3.4.3+4**. No Version replacement, spoofed3.4.1,
mod/game JAR transformation or derivative Sodium/Iris is introduced. A genuine
matching3.4.1 port would require separate Java/native binding integration and
validation; this candidate does not provide one. Original mods remain downloaded
through normal version/dependency/hash checks; none are bundled in the app.
No runtime source/pin, release179 identity, Store listing or frozen archive changes.
197's real drain/lifecycle changes, clean-exit audit, sampler-off, direct context
and synchronous flush policies remain. Do not classify an error exit as successful
shutdown or assume this solves the reported performance issue.

## Checks and console work

The required policy lane tests all three candidate versions, missing/invalid
resource, Vanilla, Vulkan, channel and caller-property boundaries. Launcher
fixtures still verify untouched Iris JARs, original GL/Knot arguments and account
ownership. They do not execute Iris.

`test_sodium_lwjgl_version.py` requires explicit mod cache, platform core, SLF4J
and JDK25. [Pinned original Sodium inputs](../tests/sodium-lwjgl-test-pins.json)
come from official publisher Modrinth artifacts, with size/SHA-256/SHA-512 checks.
It executes the genuine BugChecks and PreLaunchChecks from Sodium0.8.7/26.1,
0.8.9/26.1.1 and0.9.2/26.1.2 in separate child JVMs. Defaults retain the version
check; opt-out returns through the original checkEnvironment; other four checks
stay enabled and real LWJGL3.4.3+4 still fails the private exact-version predicate.
Original mod bytes remain unchanged. This manual test is outside portable CI;
no native library, Iris, game, graphics or ABI acceptance is established.

Install complete PPSA99874 /01.000.198 and retry the same Fabric instance first.
Leave a new failure open, or reopen at the launcher after a hard crash without
launching again. Iris/shader enable/disable, world creation/timing, save/reload,
Quit Game/relaunch on Vanilla and Fabric, audio/haptics,26.2+Vulkan and endurance
remain physical-console work. No release/prerelease or Store publication.
