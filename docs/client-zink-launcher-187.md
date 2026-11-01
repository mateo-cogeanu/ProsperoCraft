# Normal launcher and Vanilla26.1 Zink — candidate187

The user reports exact186 **Stage2b PASS** and requests return to the normal
launcher. Preserve [186 acceptance](validation/client186-console-stage2b-2026-11-01.json),
its exact ZIP/symbols and all prior artifacts.187 is a new, unvalidated build.

## Behavior

187 restores the actual `ClientStartup25` game launcher, full account/sign-in,
instance library, downloader, settings and original-Main path. It uses the same
combined single-copy Zink/RADV component, scoped providers, staged constructors,
GLFW callback binding and canonical resident GL filenames as186. There is no
six-second diagnostic card or diagnostic JVM-shutdown bypass in this candidate.
The normal current-session clean-Main/SDL shutdown and OS process-replacement
barrier remain mandatory;186 does not establish the full-game lifecycle.

An exact build resource enables only Vanilla26.1,26.1.1 and26.1.2 as
**Development test**. All three release metadata pins were checked against the
live publisher manifest on1November2026. Receipts from new installs record
`renderer=ZINK`; existing verified receipts remain usable via selected-version
policy. Adapted GLFW goes ahead of original downloaded modules. The original
OpenGL renderer gets no `--graphicsBackend vulkan` argument. Startup configures
the existing resident Vulkan entry for GLFW and selects the opt-in Zink GL resolver
before invoking original Main. Game/mod JARs and assets remain unmodified;
public app inputs include no original game JAR or asset objects.

26.2 retains GLFW/Vulkan,26.3 and supported26.4 snapshots retain SDL/Vulkan.
Default builds lacking the exact resource keep26.1 blocked. Fabric26.1 remains
blocked with a Vanilla-only message; Iris remains guarded. The ordinary full-game
Microsoft ownership/session checks remain. No account proof, credential, world,
preset instance, device address or inbound client filter is bundled.

## Exact187 console test

Install the complete PPSA99874 / **01.000.187** candidate ZIP. Expect the normal
ProsperoCraft launcher, existing library and normal sign-in status. Sign in if
required, create a **new Vanilla26.1 instance**, download/repair through the
launcher, and select **DEV TEST - PLAY**. Use a disposable instance/world for
bring-up. First report whether original Minecraft reaches its **title screen**;
this is Phase E row3. A successful download or normal launcher page alone is not
that pass.26.1.1/26.1.2 game testing follows after26.1 acceptance.

World creation/play/audio, save/reopen, quit/relaunch,26.1 patch releases,26.3
world regression and26.2/snapshot Vulkan regressions remain required later
checks. If startup fails/crashes, reopen and leave the launcher open without
starting another game so current/previous reports remain available. No measured
FPS/refresh/endurance or broad mod compatibility claim follows from this test.

## Build and checks

`package_zink_normal_launcher.py` takes the explicit accepted179 ZIP/relink/build
inputs, exact183 component, runtime workspace, JDK25, LLVM and LLD used for186.
It rebuilds the full canonical startup/launcher sources and native wrapper in
isolated `build/zink-jvm187`, then writes `dist/candidates/zink-jvm-187`. Existing
candidate ZIPs are never overwritten. Root/current published identity remains179.
`test_client187_package.py` verifies exact identity/hashes/classpath, actual normal
Main harness/build resource/full-game channel, canonical GL names, original JAR
preservation, resident groups, one graphics copy, staged constructors and signatures.

Portable instance tests now exercise the actual normal launcher with fake pinned
publisher files and an injected test-only account session: all three development
versions, binding precedence/missing binding, full-game GL arguments, absent/
expired account refusal, default/Demo/Fabric/future-version gates and retained
Vulkan policy. No real account request or game execution occurs in these tests.
Physical title/world/lifecycle validation remains separate from host/CI/SDK checks.

Keep029 OSMesa, native callbacks, runtime descriptor/ZIP and optional ImageIO/JNA/
resident aliases, allocator/scratch/verifier/emutls/network/sync/thread-stack
policies, SDL storage/workers, Mesa ownership/reserves, shaderc lifetime, OpenAL
and input/audio workarounds intact. No release/prerelease, Store update, archive
freeze or full-game ALL PASS is inferred. README support remains unchanged until
physical acceptance. Fabric/Sodium-on-GL/Iris/Distant Horizons are later milestones.
