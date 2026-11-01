# JVM Zink / actual native launcher handoff — diagnostic184

User reports [183 Stage2a PASS](validation/client183-console-stage2a-2026-11-01.json).
Its exact native-only package/symbols remain preserved.184 is a separate local
PPSA99874 /01.000.184 diagnostic, not a Minecraft launch candidate. Current game
launcher/root identity stays179;26.1.x game support stays blocked. No release or
Store action is authorized.

## Physical checkpoint

Install the complete184 PPSA99874 folder. The **actual native launcher UI and
Vulkan toolkit renderer** start before a real JVM, as in the existing app. A
small diagnostic Java mailbox page replaces only our own `ClientStartup25`
harness class, not an original game class or normal account/install policy.
It shows one **Run Zink handoff** card. Press **X once**.

Expected sequence:

1. Native launcher closes its real VideoOut presenter and offscreen GPU device,
   closes input/haptics and joins its UI thread. A failure prevents GL testing.
2. Actual JVM runs the rebuilt resident GLFW and LWJGL OpenGL JNI code, with
   real PS5 platform dispatch and the explicit Zink resolver. Expect one roughly
   six-second RGB/moving-white-bar sequence and guarded pixel readback.
3. GL finishes, unbinds and destroys the real context/window; GLFW/SDL quits.
   Only normal return with verified diagnostic cleanup enables the existing
   native bootstrap restart flag. All checks must succeed; the diagnostic-only bootstrap branch explicitly requires
   real `DestroyJavaVM` success before replacement. The normal game path keeps its
   existing policy and does not enter this branch.
4. The **existing OS LoadExec process replacement** is the retained WSI/worker/
   native-resource ownership barrier. A new process starts the actual native
   launcher and a fresh JVM. Its diagnostic page says **Stage2b PASS** and remains
   visible; it does not automatically repeat the test or open Minecraft.

Confirm the visible animation and the returned native result page separately.
There is no new system PASS notification requirement. If it crashes, reopen
without X and leave the diagnostic card open for current/previous reports at
read-only port8765. Existing log retention and session/run identity remain.
No preset console address or client-IP filter is added.

This validates an actual native UI/JVM/GL/OS replacement seam, **not the ordinary
account/instance/download/original-Main flow**. This diagnostic reads no account,
world or instance data, and ships no original game/asset objects. It is not a
full launcher feature or broad game/regression pass. The resumed result page uses
the existing self-replacement resume argument; no general recovery or Main-clean-
shutdown guard is relaxed in the production launcher.

## Integration

`build_client_gpu.py` accepts an explicit combined Zink/RADV component and separate
output directory. Defaults retain the existing Vulkan-only build. It verifies
component, Mesa pin, frontend/patch/WSI header identities, then applies the existing
private graphics allocator/libc/thread/provider bindings, genuine native mutex/
condition reserves, string allocation and C++ exception/TLS integration. It scopes
the **actual combined build's zlib** symbols against the JVM and preserves029's
already private OSMesa instance. There is one RADV/NIR copy, shared by the native
launcher and later Zink; launcher devices are destroyed before game-side ownership.
SDL's display inventory may create its normal short-lived query instance.

All GL/Zink/RADV constructors are retained in the existing explicit graphics
constructor array, executed once before native launcher use. Toolkit constructors
remain separately staged; core JVM constructors and all existing native fallback
policies remain. No automatic graphics constructor, global allocator, arbitrary
loader or platform spoof is added. GLFW calls the same scoped private frontend.
The known **ps5zink** resident group exports only the genuine GL procedure resolver
and an initializer forwarding to the existing graphics once-initialization.

The accepted179 package and exact179 OpenAL relink kit are explicit, hash-verified
baseline inputs. Existing native group objects are checked against its resident
receipt; inherited link objects/layouts against its relink manifest. Only the
combined graphics support, GLFW and resolver/registry, toolkit/main objects and
our Java module/diagnostic overlay change. The actual direct class bytes read by
native DefineClass and the JAR copy are both replaced and independently compared.
Original parent dependency JARs remain intact; default029 OpenGL dispatch stays
available. The actual183 component and current registry are not linked alongside
a second older RADV. Existing OpenAL and raw JVM policies are retained.

`package_zink_jvm_handoff.py` requires explicit runtime, accepted179ZIP/relink,
baseline workdir, component, JDK25, LLVM and LLD inputs. Missing/stale inputs fail;
there is no game-cache fallback. The baseline workdir supplies only checked native
relink inputs/generated classpath, not a historical source folder. Runtime registry
build outputs are regenerated; no reusable runtime source/default is changed.
Outputs use `dist/candidates/zink-jvm-184` and do not overwrite179 or183 packages.
A future release would require exact updated OpenAL relink material and explicit
release authorization; this is an unpublished local candidate only.

## Verification boundaries

`test_zink_handoff_host.py` executes the **unchanged diagnostic Java workload** on
macOS lavapipe with actual rebuilt GLFW/LWJGL/Zink, under XcheckJNI/Xverify and
native frontend/GLFW sanitizers. It covers real GL rendering/readback/guards and
teardown. Host JNI controls model only the launcher barrier: rejection prevents
GL/restart, and the resume branch remains on its result page without GL. A host-only
PS5 enum dispatch control is never packaged. Native UI, VideoOut and LoadExec do
not run on the host; those remain physical184 tests. Warnings from test-only Unsafe
and pinned SDK/Java8 compilation remain recorded locally, not silently hidden.

`test_client184_package.py` independently checks the exact ZIP/source/identity,
matching direct/JAR diagnostic class, resident groups/resolver, one-copy RADV/NIR,
explicit constructors,029 presence, original parent JARs and native signatures.
Target compile/link/converter checks pass with the actual JVM and launcher code.
Local fast/native/hosted checks are recorded separately after completion.

Remaining work after this checkpoint: exact184 physical transfer/return and
resource coexistence; production launcher ZINK receipts/development gates and
arguments; original26.1 Main/title/world/audio/save/reopen/exit/relaunch for every
locked patch; current Vulkan version regressions and endurance. Preserve029,
adapted GLFW callback ABI, all runtime allocator/TLS/sync/stack workarounds, official
JARs, prior packages/symbols and frozen history. No full-milestone ALL PASS implied.
