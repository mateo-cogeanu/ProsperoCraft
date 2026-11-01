# Vanilla and Fabric26.1.x testing — candidate188

The user reports [187 Vanilla26.1 works, but crashes on quit](validation/client187-console-gameplay-2026-11-01.json).
They then explicitly request continuing **without fixing quit yet**.188 retains
187 shutdown behavior byte-for-byte in startup, session verification and native
GLFW/Zink code. The uncommitted shutdown experiment was removed from active
sources. Quit-crash cause remains unproven: console reports could not be retrieved.
Preserve exact187 and earlier candidates unchanged.

An exact candidate resource `all-loaders-26.1-zink-v2` enables Vanilla **and Fabric**
for all currently enumerated releases:26.1,26.1.1,26.1.2. The live publisher manifest
was rechecked on1November2026. This is an exact allowlist, not future-version or
snapshot support.187's Vanilla-only resource still refuses Fabric; default builds
without either resource remain gated. All new paths remain **Development test**.

Normal accounts/sign-in, verified original downloads, isolated instances and
upstream Fabric profile/Loader/Knot/Mixin are retained. Existing verified loader
choices remain pinned on repair; genuine Fabric dependency checks precede launch.
All26.1.x paths use adapted GLFW and original OpenGL arguments through Zink,
without `--graphicsBackend vulkan`.26.2+/supported snapshots keep Vulkan. Official
game/mod JARs are not rewritten. Iris remains blocked with a Zink-specific testing
message; this does not establish Sodium, Iris or general mod compatibility.
Existing default Fabric content, including Controlify, remains unchanged.

Install complete PPSA99874 / **01.000.188**. Use the normal launcher to create a
new disposable instance, choose26.1/26.1.1/26.1.2 and Vanilla or Fabric, download
and select **DEV TEST - PLAY**. Start with Fabric26.1; report title/world/mod
entrypoint behavior separately. **Quit may still crash**, as requested. Do not
infer save/reopen/relaunch, other versions, audio, performance or endurance from
a title screen or earlier187 report. Preserve worlds and existing instances.

Build using `package_zink_launcher_fabric.py` with the explicit179 ZIP/relink/build
inputs,183 component, runtime,JDK25,LLVM/LLD used for187. It writes isolated
`build/zink-jvm188` and `dist/candidates/zink-jvm-188`, refusing ZIP overwrite.
`test_client188_package.py` audits exact identity, full launcher/channel/resource,
canonical GL resolver, classpath, single graphics copy, staged constructors,
original JAR preservation and signatures. Host tests exercise genuine pinned
Fabric install/repair/dependency predicates and Knot selection for all releases
using injected publisher data; no actual game or account execution is implied.

Keep029 OSMesa, GLFW callbacks, runtime descriptor/ZIP/ImageIO/JNA/aliases and
allocation/scratch/verifier/emutls/network/sync/thread-stack policies, scoped
SDL/RADV reserves/ownership,shaderc lifetime,OpenAL/input/audio implementations.
Quit repair, actual188 Vanilla/Fabric title/world/save/reopen/relaunch, later
Vulkan regressions and endurance remain pending. Root/published179 identity and
release/Store hold remain; no release/prerelease or archive freeze.
