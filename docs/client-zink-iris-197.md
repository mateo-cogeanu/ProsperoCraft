# Iris testing, queue-drain lifetime and observation cost —197

The user reports **Vanilla and Fabric26.1,26.1.1and26.1.2 all work** on196,
but every combination crashes on Quit Game and world creation is slower than
usual. [The196 console receipt](validation/client196-console-six-versions-2026-11-01.json)
records the six results separately, matching exact196 package, current/retained
run identities and independent local report hashes. This is positive playtest
feedback, not a formal ALL PASS, measured performance or release authorization.
Exact196 and all earlier packages/symbols/history remain retained.

## User-authorized Iris testing

197removes the deliberate Iris block on the genuine **Zink/OpenGL** path. Normal
Fabric metadata/version/dependency, original-download hashes, account/ownership,
server-only mod and other launch checks stay active. The existing Vulkan renderer
continues to reject OpenGL-only Iris; it uses Vitrail. No game/mod JAR is rewritten,
shader pack installed, dependency substituted or compatibility pass inferred.

The native launcher shader help now points Zink users to matching Iris in a Fabric
instance; browser-upload help distinguishes Iris/OpenGL from Vitrail/Vulkan. Use
Mods to install a matching Iris build and its required dependencies, then select
packs in the original game. Modrinth's filters and dependency handling remain;
this unlock is permission to test, not proof of Iris/Sodium/pack rendering.

Host tests run actual launcher preparation for all three Zink Fabric releases with
an Iris manifest fixture, require unchanged JAR bytes/original GL arguments/Knot
selection/owned-account checks, and retain Vulkan and nested-Iris refusal controls.
Direct and nested Iris are permitted on Zink; genuine dependency conflict and
missing-library rules remain tested. No real Iris/game execution occurs in CI.

## Quit boundary and barrier repair

The retained26.1.1Fabric run logs Stopping and ends after real screen QueueWaitIdle
returns, at shader queue finish entry. Exact native refusal/wait is unproven.
An older retained26.1.1Vanilla startup section records VM EXIT:0 without a verified
gate result, so it cannot be classified as the same shader-drain failure. Current
and retained abort notes record no VM abort; no matching hs-error file exists.

Mesa `util_queue_finish_execute` originally destroyed its barrier from a worker
selected by `util_barrier_wait`. Other workers can still be returning from their
wait. The portable fallback returns true for every participant, making that
ownership particularly unsafe. `0007-resident-barrier-lifecycle.patch` moves
barrier destruction to the queue owner **after every real completion fence is
waited and destroyed**. Workers only wait; one owner destroys after all have left.
Queued shader jobs, real fences, the drain and eventual joins remain intact.

The optional combined Zink component also selects Mesa's existing portable
mutex/condition barrier implementation, so its explicit initializers use the
existing scoped graphics native reserves rather than late raw pthread_barrier
allocation. No new reserve/budget, spinning barrier, fabricated completion, skipped
job, detached worker or GPU wait bypass. Pool exhaustion, other queue/fence native
allocations and unrelated shutdown failures remain possible; the exact console
cause and197quit repair acceptance are not established by this source repair.

`test_zink_queue_barrier.py --source-dir <explicit generated Mesa source> --cc <clang>`
verifies the current pinned source/patch audit, extracts the actual portable barrier
and finish-worker bodies, and exercises them with the actual graphics reserve
adapter. Real native mutex/condition creation is refused after priming.1/2/4/8
participants run8192barrier generations with visibility checks, then1000reuse cycles;
all reserve leases must be released. ASan/UBSan are forced. The scoped host fixture
uses real-time barriers; Darwin's unused monotonic reserve initialization does not
establish monotonic-clock behavior. This source-dependent test is outside portable
CI lanes and does not execute PS5 scheduling or establish a physical quit pass.
The target u_thread object must have no pthread_barrier imports.

The clean System.exit audit remains.197adds fixed checkpoints for observer
registration, audit entry/armed/rejected state and native exit-gate outcome, because
captured Java stderr alone did not establish whether the audit ran. No native JNI
callback is made after VM termination and no unverified exit becomes a clean quit.
Host child-JVM tests cover the checkpoint sequence and failed checkpoint refusal.

## World-creation observation overhead

197turns off the **timed Java stack/resource sampler** via its isolated bootstrap
macro; it retains the clean-exit observer and bounded failure checkpoints.196was
producing repeated full thread snapshots during loading, so removing that known
overhead is justified. Native trace/fallback logging, synchronous Gallium context,
flushsync, four reported Java processors and existing heap/GC policies remain.
No unmeasured shader/world-generation speedup, new FPS target or allocator/GC repair
is claimed. Compare world-creation timing on the console; the exact cause of the
reported slowdown remains open.

## Exact test and preservation

`package_zink_iris.py` / `test_client197_package.py` use verified179 ZIP/relink inputs,
new exact combined component and normal launcher. Audits require observer=false,
Iris block removal only for Zink, retained Vulkan refusal, real barrier-drain code,
staged constructors, one graphics copy and original parent JARs. No old ZIP
rewrite, published179 identity, reusable Java runtime source/pin or frozen archive
change. Source changes belong to ProsperoCraft. No release/prerelease/Store action.

Install complete PPSA99874 / **01.000.197**. Test matching Iris/dependencies in a
Fabric26.1.x instance, then shader enable/disable and world behavior. Separately
repeat Quit Game, return to the normal launcher library and relaunch on Vanilla
and Fabric; leave any failure screen open or reopen after a hard crash without
starting another game. Compare world creation with the same version/seed/settings
and warm/cold state. Save/reload, all packs/mods, audio/haptics,26.2+ Vulkan, native
resource reclamation and endurance remain pending. No new passing milestone.
