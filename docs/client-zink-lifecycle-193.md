# Clean System.exit handoff and screen wait diagnostics —193

The user reports192 stays black, and now authorizes quit-crash work. The
[192 console receipt](validation/client192-console-black-2026-11-01.json) records
exact package/run and independently retrieved report hashes. Native output stops
inside `zink_create_screen`; repeated Java snapshots remain in genuine
`glfwCreateWindow` from original Fabric Knot/Main. Native resource observation
continues past724seconds. Current-run notes record no JVM abort/probe exception;
there is no hs-error file. Earlier thread refusals do not identify the stalled
operation. No JNI-copy repair, title/world/mod pass or underlying quota is inferred.

193 adds fixed internal screen-creation labels around instance locking/creation,
physical-device selection/properties, submission queue, logical-device creation,
resource/compiler/cache/worker initialization and timeline semaphore creation.
The64-record bound preserves errno and original control flow. No driver success
is fabricated, queue skipped, allocation budget increased or game JAR modified.
192's genuine scoped LWJGL environment ownership and191 flushsync remain.
This is diagnostic progress on the black screen; its cause remains unproven.

## Original26.1 quit path

The pinned original26.1 `Minecraft.destroy` logs Stopping, closes the game, then
calls `System.exit(0)` (including a finally path). It cannot return to the launcher's
existing clean-Main-return branch. Real HotSpot VM_Exit completes cleanup then
invokes the configured exit hook; the old consumer hook only logged and returned,
so HotSpot continued into process exit. The187 user report has no independently
retrieved quit crash PC; this mismatch is concrete, but the reported crash's exact
instruction remains unproven.

Only193 enables `PROSPERO_CLEAN_SYSTEM_EXIT`. A launcher-owned Java shutdown
observer runs the existing ProsperoSession audit: current marker plus Stopping,
no fatal/startup/shutdown failures, stopped original Minecraft singleton and no
live SDL subsystem. It reads the original render thread's current classloader,
including Fabric's later Knot transition. A verified audit arms a native atomic
one-shot gate. Error/unknown audits log only the exception class and do not arm.
A normal Main return unregisters the observer and retains the existing path.
No exit interception, SecurityManager, replacement Minecraft class, bytecode hook,
new game cleanup or manual JNI call during VM termination is introduced.

After genuine Java hooks/HotSpot cleanup, the native exit hook consumes the arm.
Only status0 invokes the existing LoadExec library restart; nonzero/unarmed exits
retain their original behavior. A returned LoadExec error is logged and held for
retrieval, without falling through into libc exit. OS process replacement remains
the ownership barrier for the one JVM, resident driver state and retained resources.
The ordinary builder's native query returns false; exact prior candidates remain
untouched. A clean audit is not proof that other mods' parallel shutdown hooks
succeeded or that all saves completed; physical lifecycle checks remain necessary.

## Verification and console work

`test_launcher_system_exit.py` runs real child JVM System.exit for clean, stale,
fatal, running/null singleton, live SDL and failed-arm cases, observer removal and
nonzero status preservation. Diagnostics exclude exception message text.
`test_session_exit_gate.py` runs the actual native gate under ASan/UBSan, checking
unarmed/nonzero refusal, consuming an error arm, one-shot reuse and concurrent
ownership. `test_session_vm_exit.py` additionally embeds genuine HotSpot through
JNI_CreateJavaVM, runs the real Java observer/native arm/VM exit hook, and
executes the existing restart bridge into a fresh host process. Unarmed/nonzero
exits preserve their status; Xcheck:jni reports no warnings. These join the portable fast/native lanes; neither executes PS5 LoadExec.

`package_zink_lifecycle.py` and `test_client193_package.py` retain verified179
ZIP/relink inputs, original parent JARs, full launcher/account/download policy,
all Vanilla/Fabric26.1.x development gates, original renderer and single combined
RADV/Zink. Build193 is isolated; no old ZIP overwrite/current179 identity change.
Target compile, exact package audit and host graphics results are recorded in the
matching build receipt when complete. No release/prerelease/Store/archive action.

On exact193, first retry the same Fabric26.1 launch; leave a black/failure screen
open for reports. Separately test the previously working Vanilla26.1: title,
world/save, Quit Game, return to the normal launcher library and launch again.
Report each result separately.26.1.1/26.1.2, Fabric/mod cleanup,26.2+ Vulkan,
OpenAL/input, resource reclamation and endurance remain pending. Preserve all
runtime compatibility policies, historical snapshots and exact prior candidates.
