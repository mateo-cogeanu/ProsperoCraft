# Early frontend mutex lease — candidate189

188 Fabric26.1 fails check4 in exact run
`client-01.000.188-1793539492-635300548`. The
[console receipt](validation/client188-console-fabric-window-2026-11-01.json)
records matching package/run and locally saved Java/startup/native/VM report hashes.
Actual upstream Fabric0.20.1/Knot, mods and original Main execute; native launcher
handoff and SDL/GLFW init/display/window allocation complete. Original game rejects
OpenGL creation with `PS5 Zink context operation failed (16)` and returns. The
clean-session verifier then correctly refuses process replacement. This is a
startup failure, not the explicitly deferred quit-crash repair.

## Scoped change and uncertainty

The private frontend's static `PTHREAD_MUTEX_INITIALIZER` guard bypasses the
existing graphics mutex reserve: that adapter leases only explicit
`pthread_mutex_init` owners. A first lock after Fabric/native allocation pressure
can therefore still use lazy native allocation. The same run shows native
allocation and pthread creation refusals, but exact quota/allocator cause is
unproven.188 maps **all guard-lock errors to EBUSY(16)**, also used for cross-thread
context ownership refusal, so its reports do not establish which branch failed.
The unsupported window hint0x00020010 is separately observed; causality is unproven.
No captured native fatal report exists (hs-error unavailable errno2).

189 explicitly initializes that one frontend guard in its constructor, which the
existing combined graphics pipeline retains and runs once **before JVM startup**,
after priming the same256normal/64recursive graphics mutex reserve. In the scoped
target build this explicit init leases one real reserved native mutex. No GL
context, screen, Vulkan instance/device or extra presentation owner is created by
priming. The guard stays process-resident, matching its protected shared state.
An initial failure blocks access; exact native init/lock return values propagate
with bounded stage diagnostics. Context owner checks remain, with a separate
ownership-refusal diagnostic. Pool sizes, native lock semantics and runtime/global
allocator policies are unchanged. This addresses a real reserve gap but requires
physical validation before attributing188 solely to it or claiming a fix.

`test_zink_guard.py` extracts the actual guard implementation and combines it with
the existing real mutex-reserve implementation under controlled native-init
refusal. It checks explicit leasing,80000contended increments, no late native init,
unprimed/exhausted reserve failures and original error propagation under ASan/UBSan.
It models PS5 lazy-allocation refusal; it does not run the PS5 kernel/driver.
This is added to the optional native host lane. The graphics host fixture also
uses the canonical `libps5zink.so` name directly, matching the resolver repaired186.

## Exact189 test

Install complete PPSA99874 / **01.000.189**, then use the normal launcher and the
same **Fabric26.1** instance. Download/repair as needed and select **DEV TEST - PLAY**.
Report whether Minecraft reaches title/world and actual mod functionality.
If check4 fails, leave that screen open for reports; do not start another run.
Vanilla/Fabric26.1,26.1.1,26.1.2 remain available for development testing.

**Quit-crash repair remains deferred.** Startup, session verification and restart
sources are unchanged from187/188. Original game/mod JARs, upstream Fabric/Mixin,
account guards and adapted callback bindings remain. Iris stays guarded. Full
Vanilla/Fabric/version/title/world/audio/save/reopen/relaunch,26.2/26.3/snapshot
Vulkan regressions, measured physical refresh/FPS/resource reclamation and
endurance remain separate pending checks. No full-game ALL PASS, release,
prerelease, Store update or archive freeze.

Build with `build_zink_native.py` for the pinned component and
`package_zink_fabric_guard.py` with the same explicit179 ZIP/relink/build inputs,
runtime,JDK25,LLVM/LLD as188 and the rebuilt component. Outputs use
`build/zink-jvm189` and `dist/candidates/zink-jvm-189`; ZIP overwrites are refused.
`test_client189_package.py` checks exact metadata/hash/classpath, staged
constructors/resident groups/single combined graphics copy, guard diagnostics,
unchanged shutdown sources, original dependency JARs and signatures. Preserve
exact188/187/186/183 and earlier ZIPs/symbols/receipts; previous combined183 native
component and host binary copies were retained locally before component rebuilding.

Retain029OSMesa, all SDL/RADV allocation/mutex/condition/TLS/ownership workarounds,
shaderc/OpenAL/input/audio behavior, runtime descriptor/ZIP/ImageIO/JNA/resident
aliases and scratch/verifier/emutls/network/sync/thread-stack policies. Default
published identity179 and noncandidate launcher gates remain unchanged.

[Exact189 build/validation](validation/client189-zink-fabric-guard-2026-11-01.json)
pins build source `56a01d9` and component/package/runtime hashes.
ZIP SHA-256: `8e58ed81335732fc0b0dc731c11359af2a960df1e2bba576c4622900421eb753`.
Local16fast,8native,source-only16fast/8native, actual host GL and target/package
checks pass. The audit resolves PIE relocation addends to prove the guard init
function is in the actual staged GPU constructor array.
[Hosted policy](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41311489057)
and [hosted native](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41311503039)
pass on Ubuntu and macOS at test-source `a19cb11`; completed job logs inspected.
Initial Ubuntu native compilation required explicit POSIX feature declarations;
that host-only correction and the PIE audit correction change no packaged code.
PS5 repair acceptance and the deferred quit issue remain pending.
