# Prepare genuine Zink screen before JVM startup —194

The [exact193 console receipt](validation/client193-console-shader-queue-2026-11-01.json)
records the user's check4 failure and matching first local reports. Internal
checkpoints prove instance/physical-device/logical-device creation and dispatch
loading succeed. Resource/compiler/disk cache stages advance, then the required
`util_queue_init(cache_get_thread, "zcfq",8,4,...)` returns false. Screen creation
fails; original Fabric Knot/Main reports GLFW error19/ENODEV and returns early.
The existing clean-session audit correctly rejects that return; it is not a quit
test or failure of the new System.exit handoff. Exact queue allocation/thread/
primitive refusal and underlying native quota/allocator owner remain unproven.
192's sustained wait is a separate run and is not retroactively classified as
this exact refusal.

194 explicitly prepares the genuine Zink screen **before JNI_CreateJavaVM**,
after core constructors/native synchronization reserves and graphics constructor
initialization, before starting the native launcher display. It creates the real
Vulkan device, compiler/cache infrastructure and required initial shader worker
while native resources are available, then keeps that same screen for the first
original GL context. Mesa's queue defaults initially start one worker, despite a
maximum of four; later scaling remains upstream policy and can still fail/degrade.
No queue, fence, compiler, GL capability or GPU submission is replaced/bypassed.
No heap/GC/native budget change or official game/mod JAR alteration.

`ps5zink_prepare_screen` is an explicit optional native API, using the existing
real frontend guard. It returns success only for a real screen, is idempotent and
safe for concurrent prepare calls. Context creation shares the same guarded
helper. Existing last-context destruction still destroys that screen and joins
its actual queue workers; no new resource pool, thread reuse or changed TLS
cleanup semantics. The existing combined graphics provider scopes the new export.
Only194 defines `PROSPERO_PREPARE_ZINK_SCREEN`; default builders keep lazy screen
creation. Earlier exact packages/symbols/components remain retained.

A preparation refusal holds a fixed failure status for logs before Java/game
startup; it cannot report successful graphics or enter original Main. Successful
preparation does not create a GL context, window, surface or presentation owner.
The normal native launcher still creates/releases its own Vulkan resources and
hands off normally. This candidate keeps an extra real Zink device/initial workers
while accounts/downloads run, including if another renderer is later selected.
Memory/resource cost and26.2+ Vulkan coexistence therefore need physical regression
checks. This addresses the observed late queue initialization, not an established
root cause or a guarantee that other native allocations will succeed later.

194 retains193's candidate-only verified clean System.exit(0) LoadExec handoff,
192's genuine LWJGL environment allocation scoping,191's flushsync policy and190
bounded native diagnostics. Full launcher/accounts/downloads, all Vanilla/Fabric
26.1.x development gates, original backend and original JARs remain. No current179
identity, runtime pin, release/prerelease/Store or frozen archive change.

## Verification and physical test

The actual host frontend fixture prepares concurrently from four native threads,
checks idempotence, then runs real clear/draw/readback, refused surface, context
ownership/transfer/resize and destruction. `test_zink_host.py --prepare-screen`
additionally injects an explicit host-only native constructor into the genuine
Java executable: the real screen/queues are ready before launcher main/JVM startup.
Original26.1/26.1.1/26.1.2 GlBackend/GlDevice capabilities and rendering then use
that provider. This helper is not linked into PS5 or a replacement Java class.
Host and target/package results are recorded separately; no PS5 pass is inferred.

`package_zink_prewarm.py` / `test_client194_package.py` build and audit isolated194
from verified179 ZIP/relink inputs and the exact new component; they refuse ZIP
overwrite. Verify the actual ELF contains one scoped prepare export, genuine
constructor arrays, early preparation and retained original Main/quit policy.

Install complete PPSA99874 / **01.000.194**, then retry the same Fabric26.1
instance. If it fails, leave that screen open for reports. Report title/world/mod
behavior separately. Then test the previously working Vanilla26.1: title/world,
save, Quit Game, normal launcher library and relaunch.26.1.1/26.1.2, Fabric mod
shutdown,26.2+ Vulkan/audio/input, resource reclamation and endurance remain pending.

194 was built but not delivered for console acceptance. An extra missing-validation-
layer host test exposed an existing partial-screen teardown dispatch failure;
see [195 ordering repair](client-zink-early-screen-195.md). Do not treat194as
a successful early-refusal test or physical pass. Its exact package stays retained.
