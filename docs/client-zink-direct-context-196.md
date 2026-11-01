# Owned prepared screen and direct Gallium context —196

[Exact195 current-run evidence](validation/client195-console-context-refusal-2026-11-01.json)
shows the real screen, initial shader queue and timeline semaphore initialize
before JVM startup. Native launcher Vulkan initialization/handoff succeeds and
the game reuses the prepared screen. Then `st_api_create_context` returns NULL;
195does not log its error enum/internal failing step. The Render thread remains
inside genuine GLFW.glfwCreateWindow from original Fabric Knot/Main. The exact
subsequent stalled operation and underlying native refusal remain unproven.
No title/world/mod/quit success or full ALL PASS follows from screen readiness.

## Prepared ownership on refusal

195automatically destroys the whole screen when context creation fails and no
contexts exist, even after explicit pre-JVM preparation established its owner.
196records that explicit owner. On failed context creation it retains the real
screen/state-manager in the frontend, frees the temporary frontend context owner,
returns the actual error and releases the guard. It does not attempt whole-screen
teardown in that branch. One prepared screen remains owned until a later successful
last-context destruction or the existing OS process-replacement/close barrier.
This is bounded retained ownership, not universal cleanup, orphan recovery or a
claim that opaque failed upstream allocations are reclaimed. Ordinary lazy creation
without explicit preparation keeps its original failure cleanup. Successful last-
context teardown still destroys the actual screen/queues and clears the prepared
flag. No rendering result is fabricated and no in-flight GPU resource is freed.

A real host negative fixture uses the supported host-only Mesa version override
to request4.6 against3.3, requires actual BAD_VERSION/ENOTSUP, then creates3.3on
the same retained screen, clears/reads a real red pixel and destroys the context.
It requires exactly one screen creation and the retained-owner checkpoint. The
override is confined to that native child process; it is not a game/runtime setting.

## Supported synchronous context mode and diagnosis

Only196calls `enable_synchronous_context` before the original bootstrap, setting
upstream `GALLIUM_THREAD=0`. Actual `threaded_context_create` then returns the real
Zink pipe context instead of allocating its optional wrapper and gdrv worker queue.
GL commands execute through genuine Mesa/Zink on the owning render thread. Vulkan
commands/fences/submission and shader queue/compiler behavior remain; existing
flushsync also remains. No worker-success stub, skipped GPU operation, heap/GC/
budget increase, native TLS reuse, game class replacement or JAR mutation.

The optional gdrv queue is a plausible further late-native allocation dependency,
but it is **not established as195's failing site**. This candidate policy may
change throughput; FPS/endurance/physical repair acceptance remain pending. The
normal builder does not call the setting helper. Its actual host policy test
covers absent/default state, idempotence, preserved unrelated Zink flags and a
refused native setter without changing the previous value.

`0006-context-refusal-checkpoints.patch` adds fixed labels through genuine Mesa
initialization, pipe/context allocation, GL state/debug/version setup, Zink initial
buffers/descriptors/batches, optional threaded wrapper/queue and screen cleanup.
A separate128-record atomic limit preserves errno. The frontend records only the
error enum and bounded numeric requested version/flags before temporary cleanup;
no paths, pointers, arguments, credentials or exception text. Ordinary return/error
and cleanup decisions in those upstream functions remain unchanged. Refusal/early
cleanup diagnostics are not broad error-recovery or native quota proof.

## Exact build and physical test

`package_zink_direct_context.py` / `test_client196_package.py` use verified179
ZIP/relink inputs, the new exact single combined component, retained canonical
classpath/resident env ownership, staged constructors and original parent JARs.
196retains195early real screen/queue preparation and instance-refusal dispatch
ordering,192LWJGL allocation scoping and193candidate clean System.exit handoff.
The full launcher/account/downloader and all Vanilla/Fabric26.1.x development gates
remain. Other renderers, native UI/device coexistence and retained prepared resources
still require physical regression checks. No current179identity, runtime source/
pin, old package/symbol, archive milestone or release/prerelease/Store change.

`test_zink_host.py --prepare-screen --check-preparation-refusal --synchronous-context`
checks the genuine direct-context marker, concurrent/idempotent real preparation,
prepared-context refusal/retry, original26.1/26.1.1/26.1.2 GL capabilities/rendering,
context ownership/transfer/resize/destruction, missing provider and early validation-
layer refusal. Host graphics and exact target/package checks are recorded separately;
they do not execute PS5 RADV or original Main/title/world/save.

Install complete PPSA99874 / **01.000.196**, and retry the same Fabric26.1
instance. Leave any failure/black screen open for current logs. Report title/world/
mods separately. Then test Vanilla26.1 title/world/save/Quit Game/normal launcher
library/relaunch.196startup and retained193quit candidate require physical
confirmation; patch releases, Fabric shutdown,26.2+ Vulkan/input/audio, resource
reclamation and endurance remain pending.

[Exact196 build/validation](validation/client196-zink-direct-context-2026-11-01.json)
pins clean source `0e8903a` and matching package/runtime/native hashes.
ZIP SHA-256: `256c029462a453eeb3ea53a0dc58ed69c01cca27fdbd44ab2dd7fd3b7d6c5f9a`.
Source-only outside-root17fast/11native, actual host direct-mode preparation/reuse,
refused-version/retained-screen/retry/render/destruction, original26.1.x GL checks,
missing provider/early instance refusal and exact target/package audits pass.
[Policy CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41330816577)
passes17checks and [native CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41330887776)
passes11checks on each Ubuntu/macOS host; completed jobs/steps/logs inspected.
Physical196startup, exact195refusal cause and quit/relaunch acceptance remain pending.
