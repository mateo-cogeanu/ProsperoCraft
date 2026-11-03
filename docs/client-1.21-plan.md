# Minecraft 1.21.x — Phase A research, 3 November 2026

## Execution authorization —3 November2026

The user authorizes executing this plan, including the recommended genuine333
PS5 Java platform/dispatch overlays and matching native generation. **Implement
and validate all1.21.x Vanilla releases first; Fabric follows only once those are
good.** This supersedes the original proposed Vanilla/Fabric-per-version order
and the pending overlay decision below. The Phase A record retains its original
research limitations. Full-assets Vanilla/resource experiments, matching native
isolation, host/native checks and a new audited local candidate precede physical
tests. No release/Store authorization or console acceptance is inferred.

**All twelve releases remain Coming soon.** This is a disabled research draft,
paused at the supplied port prompt's explicit publisher-library overlay decision.
No launcher/native/runtime implementation, application identity, released204 bytes,
release or Store entry changes here. 1.21.x now precedes NeoForge. The separate
[NeoForge draft](client-neoforge-plan.md) remains preserved and paused.

[Draft lock](../client/1.21.lock.json) records full publisher library/rule/download
records, client/mapping pins, Java requirement, asset index, native classifiers,
three library generations and exact Fabric/Modrinth observations. It is not an
installer receipt or a production support table. [Validation](validation/client121-phase-a-2026-11-03.json)
distinguishes completed inspection from remaining experiments. In particular,
full-assets desktop acceptance, Fabric execution and comparative resource budgets
are **not complete**; this is not a claim that every Phase A experiment passed.

## Publisher inventory and ordering

The [official manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json)
contains exactly **1.21, 1.21.1, 1.21.2, 1.21.3, 1.21.4, 1.21.5, 1.21.6,
1.21.7, 1.21.8, 1.21.9, 1.21.10 and 1.21.11** as matching releases. All twelve
metadata bodies, original clients and official client mappings were independently
downloaded and publisher SHA-1/size verified in ignored `.tools/client121-research/`.
No publisher classes, mapping files, disassembly, mod JARs, assets or raw reports
are committed or bundled. Mapping URLs enable later on-demand local symbolization.

Every release requires **Java21**, has entrypoint `net.minecraft.client.main.Main`,
and uses GLFW/OpenGL with the same eight **LWJGL3.3.3** Java modules: core,
freetype, glfw, jemalloc, openal, opengl, stb and tinyfd. None has a Vulkan module
or the26.x Vulkan backend. Keep runtime identity truthfully Java25; explicitly
validate publisher major21 when implementing rather than relying on8–100 bounds.

| Library generation | Releases | OSHI | JNA / required native ABI | Assets |
| --- | --- | --- | --- | --- |
| A | 1.21 through1.21.3 | 6.4.10 | 5.14.0 /7.0.0 |17,18 |
| B | 1.21.4 through1.21.10 | 6.6.5 | 5.15.0 /7.0.2 |19,24,26,27 |
| C | 1.21.11 | 6.9.0 | 5.17.0 /7.0.4 |29 |

LWJGL native port work is **one3.3.3 generation**, not three copies. OSHI overlays
and other Java libraries still differ. The lock retains exact Netty, LZ4, log4j,
Gson, Guava and fastutil versions for each release, including Netty4.2.7/LZ4 fork
changes in1.21.11 and authlib6.0.54/55/57/58 versus7.0.61. Publisher-native entries
include all OS/architecture classifiers; the additional Linux-x64 list follows
the existing ordered-rule evaluation. Those are desktop choices, **not PS5 ELF
inputs**. The current installer deliberately excludes `:natives-` and classified
Netty transports. Preserve that boundary and the publisher host allowlist.

Start with **1.21.11 Vanilla**, then Fabric, then work backwards through renderer
and hardware generations. It shares the existing6.9 OSHI provider and is closest
to26.1 graphics. Every release is a proposed candidate; none is enabled or
promised to work. No publisher release is ruled out by inventory alone. Keep a
failed/unproven row Coming soon independently of other rows.

## Decisive LWJGL result and proposed decision

Original3.3.3 `Platform` recognizes Windows, Linux/FreeBSD/SunOS/Unix and macOS;
`os.name=PS5` throws `LinkageError`. The existing port adds explicit PS5 dispatch
in Java (`Platform`, `APIUtil`, `PS5Library`, GL and ALC), in addition to natives.
Therefore option(a), **a second native set alone with wholly original publisher
Java bindings**, cannot provide this platform. Do not spoof the OS or version.

Option(b), original3.3.3 Java plus current3.4.3 natives, is rejected. A read-only
classfile audit compares declared native name, JVM descriptor and staticness:

| Module | Original native descriptors | Parent3.4.3 | Missing/changed |
| --- | --- | --- | --- |
| core |2,027|2,276|209|
| OpenGL, including desktop WGL |2,237|2,278|10|
| STB |215|224|13|

Nine of the ten OpenGL differences are Windows-specific; the remaining real core
difference is `GL32C.nglDeleteSync(long)`. Core callback `getCallbackHandler` also
changes its parameter contract. Zero native declarations in ALC/FreeType/jemalloc
does not prove compatibility: they use core JNI/function pointers. This is
descriptor evidence, not a complete C export/calling-convention proof. It already
precludes claiming an unchanged ABI. Do not expand the26.1 Sodium check opt-out.

**Recommend matching3.3.3 resident natives plus narrowly scoped3.3.3 Java platform/
dispatch overlays, requiring explicit option(c) approval.** Keep downloaded
publisher JARs intact and hash checked; disclose which adapted upstream classes
take precedence. Do not replace game classes, upgrade every library to3.4.3,
rewrite mod JARs or suppress truthful LWJGL version identification. Port genuine
source with pins, patch files and licenses. Investigate the actual JNI-version
warning below; do not merely silence it to claim compatibility.

`ProsperoGameLoader` currently routes **every** `org.lwjgl.*` class to the parent,
and Fabric adds parent LWJGL to `fabric.systemLibraries`. A333 native set is not
enough while that rule remains. Design a closed per-generation game binding
owner and matching Fabric delegation. Startup's333 allocation/configuration/
callback calls must use that owner, while launcher343 and SDL resources retain
their existing owner. Assert no package/singleton mixing. Scope duplicate JNI
symbols and JNI initializers to distinct registry groups; an alias cannot change
a C signature. Keep26.x native groups and option-table bytes unchanged.

Share the existing real Mesa/Zink/RADV, GLFW platform, OpenAL and FreeType
providers where their **actual C APIs** suffice; do not duplicate whole Mesa/RADV
or add another VideoOut owner. Build only required333 JNI/core/callback/STB glue
and explicit generation routing. Jemalloc stays unselected under the existing
system-allocator policy; do not add a fake tinyfd dialog or native success stub.

### Size evidence and limits

Preserved204 ZIP is **127,056,881 bytes**; entries total **249,111,203 bytes**.
Its matching relink kit provides current reference objects. Allocated ELF section
sizes are206,919 bytes core,100,644 GLFW,112,719 OpenGL,399,700 STB,736,217 FreeType
and1,127 tinyfd; full relocatable object files total about3.69MiB. The first four
allocated sums are about0.78MiB. These are **current reference objects**, not
built333 objects or exact final executable growth. All eight original333 Java
JARs total2,588,828 bytes and remain publisher downloads, not app bundles.

Reserve a provisional **2–8MiB additional uncompressed app space** for glue,
overlays/tables/licenses and possible support code while sharing providers.
This is an estimate, not a measured ceiling, compressed ZIP delta or proof that
the4,096MiB app-data policy has headroom. Actual333 compilation, scoped link,
compression and target cache/asset accounting must replace it before enabling
Play. Stop again if the design needs duplicated providers or exceeds storage
policy. No333 package exists yet; no release identity is allocated.

## Original renderer inspection

Read-only `javap -c -p -constants` used official mapping names only to locate
original obfuscated classes. All twelve were inspected, with class and local
disassembly hashes retained in validation. No remapped game was generated.

| Renderer stage | Releases | Window request | Difference to cover |
| --- | --- | --- | --- |
| Legacy RenderSystem |1.21–1.21.4|3.2 core|ARB timer query; original mutable-buffer path |
| GpuDevice/GlDevice refactor |1.21.5|3.2 core|DSA, vertex-attrib binding, debug labels |
| BufferStorage refactor |1.21.6–1.21.8|3.2 core|ARB buffer storage and persistent maps |
| Raised context minimum |1.21.9–1.21.10|3.3 core|Same buffer strategy; no timer-query flag reference found |
| Anisotropic capability |1.21.11|3.3 core|Adds EXT texture-filter-anisotropic flag probe |

Window hints select OpenGL API, native context API, core profile and forward
compatibility. No explicit debug-context hint occurs in the inspected Window
creation sequence. Its shared-context argument is zero. Do not reinterpret this
as an EGL Java request. KHR_debug/ARB_debug_output callbacks use the real native
callback machinery. BufferStorage selects immutable storage only when the actual
ARB flag and game enablement permit it; persistent mapping is real. Keep mutable
fallback, error propagation, unmap/destruction and synchronous callback ownership.

The newest seven capability probes match26.1's set. Earlier releases also probe
`GL_ARB_timer_query`; audit real query creation/deletion/results. Full method and
extension references were collected from original classfiles; dynamic mod calls,
worker ownership and every capability path still require execution. A zero-share
Window site is not proof that arbitrary mods create no shared contexts.

Comparison with the hash-verified original26.1 client finds older static calls
absent from26.1's references:1.21–1.21.4 includes stencil/renderbuffer operations,
glMapBuffer, glGetTexImage, glDrawPixels and legacy uniform uploads;1.21.5 adds
glGetActiveUniform relative to that baseline;1.21.6–1.21.8 retains legacy uniform
uploads.1.21.9–1.21.11 has no additional method names under this comparison.
The validation stores the complete differences. It normalizes owner suffixC,
not inherited owners or overloads, so it is a screening inventory, not a native
ABI proof. In particular, glDrawPixels is a compatibility-era operation: establish
whether the original path is reachable under core rendering before claiming an
early release works. Do not fabricate its support or change the game's context.

Existing `gl_context.c`/frontend accepts core major3/4 and minor0–6, including3.2;
it still rejects shared/robust/MSAA/stereo/sRGB requests and incompatible debug/
no-error combinations. Reuse its native context/ownership/present/flush/lifetime
contracts and pre-JVM preparation. GLFW333 exposes `glfwInitHint`, platform/null
constants and clipboard/cursor/joystick APIs; it does **not** expose the newer
`glfwInitVulkanLoader` Java method. Current startup calls that function by pointer
for every GLFW selection: make backend initialization conditional when implementing.
Audit333 callback descriptors against genuine GLFW3.4, not merely integer hint
values. An OpenGL request must never gain `--graphicsBackend vulkan`.

## Java25 host execution and native-library observations

Original1.21,1.21.4 and1.21.11 Main ran on native macOS ARM64 OpenJDK25.0.4 with
original, publisher-verified desktop dependencies, Xmx1536m/class64m/code96m.
Each initialized LWJGL3.3.3+5 and created original texture atlases. Each was
terminated at30 seconds. Asset indices/objects were intentionally absent, so
missing icons/fonts/sounds and resource-index failures are expected. This proves
bounded original-Main/desktop-GL execution, **not** complete title/world startup,
audio, clean shutdown, Zink or PS5. The earlier `--help` experiment simply reached
the original parser and failed missing required options; it is not a startup pass.

Warnings include333 ThreadLocalUtil's unsupported JNI version, restricted
`System.load` from JNA, and deprecated Unsafe.objectFieldOffset from Guava/JOML.
Keep `--enable-native-access=ALL-UNNAMED` in the real VM startup options; this
does not fix missing JNI ABI methods or justify rewriting `java.version`.
These bounded runs found no Security Manager abort; that is not exhaustive
log4j/Netty/removed-API coverage. Native transport defaults, reflection and actual
Fabric startup on25 remain explicit checks.

OSHI6.4.10/6.6.5 have **no current PS5 overlay mapping**. Port genuine pinned
SystemInfo/processor-provider sources per version, preserving unsupported metrics
as unsupported and real CPU identity.6.9.0 can use the existing provider only
after actual original-Main coverage. No JNA platform spoofing or fake telemetry.

JNA versions advertise native7.0.0/7.0.2/7.0.4. All three original Java JARs pass
the runtime's genuine native-size/error/memory/string/ffi strlen/abs fixture
against the existing **5.19.1-built host dispatch7.0.4**, forced with nosys,
noclasspath and nounpack. Removing that library fails all three instead of
falling back. Thus **do not add three dispatch groups merely for the version
numbers**. Reuse is a scoped candidate, pending PS5 initialization, direct
registration, callbacks, structure/layout and SDL alias resolution. No runtime
implementation or default changes were warranted by these tests.

OpenAL Java calls use the C ALC/AL interface through core JNI; actual enumeration,
HRTF/device selection, source/stream lifecycle and callbacks must be checked
against the existing OpenAL-soft port. Do not infer audible audio from classfile
references or allocate a second device to satisfy a mod.

## Obfuscation, diagnostics and clean return

Audit sites in active launcher/startup sources:

- `ProsperoLauncher.gameMain` and `ProsperoInstall` Main check name the still
  public `net.minecraft.client.main.Main`; all metadata confirms it.
- `ProsperoSession.verifyCleanReturn` names `net.minecraft.client.Minecraft`,
  `getInstance` and `isRunning`. They are obfuscated in every121 client. Its
  direct parent SDLInit lookup is another333 owner boundary. Implement an
  exact-release validated shutdown accessor strategy or leave that row blocked;
  never remove the stopped-game/current-run/log/SDL-zero/exit-status checks.
- `ClientStartup25.StartupObserver.isLanguageApply` names Language.loadFromJson,
  LanguageManager.onResourceManagerReload and Minecraft.runTick. Its optional
  diagnostic trigger will miss obfuscated stacks. Use local official mappings
  for symbolization; this optional diagnostic must not become a launch hook.
- Startup names LWJGL Configuration/MemoryUtil/GLFW/SDL and PS5Library directly;
  these are library-owner concerns, not Mojang mappings. The management preflight
  names the real JDK HotSpotDiagnosticMXBean, which is unaffected by obfuscation.
- `ProsperoControlifyKeyboard` changes supported resource JSON only for the exact
  existing26.3 mod; it has no reflected game-class lookup. Keep it excluded on121.
  `ProsperoShaderSettings` edits Vitrail config; do not apply it to Iris/OpenGL.

Do not bundle official mappings or remap/transform game classes to make these
names exist. A local symbolization aid is not authorization to execute a derived
game JAR. Preserve upstream Fabric intermediary/Mixin behavior and disclose it.

## Fabric, mods and controller generation

Official Fabric Meta offers stable **0.20.1** and exact intermediary coordinates
for all twelve releases. Every queried release has Fabric API, Controlify,
Sodium, Iris and ModMenu results. The draft records exact IDs, files, hashes,
dependencies, query URLs and response digests; metadata availability is not
compatibility. Choose matching combinations, not independently newest files
without their actual required predicates (for example Iris/Sodium0.6/0.7/0.8).

Twenty-four unique original selected Sodium/Controlify/Iris JARs were size/SHA512
verified and their manifests inspected. Selected Sodium check classes reference
LWJGL3.3.3. Selected Controlify3.0.1+lts artifacts require Java>=21, loader>=0.18.0,
their exact game family and YACL>=3.8.0. Java25 satisfies the observed Java lower
bound; no Java upper bound was found in those Controlify declarations. The
existing genuine Fabric predicate resolver remains authoritative; this observation
does not authorize accepting arbitrary upper-bounded mods.

Critically, these Controlify artifacts embed **libsdl4j3.2.18 JNA**, not the
26.x FFM SDL backend. Its original `SdlNativeLibraryLoader` uses
`NativeLibrary.getInstance("SDL3")`/`Native.register` and exposes an explicit-path
load method. The existing FFM property alone does not configure this path.
Prove its real JNA registration/callback/structure ABI and handle-scoped three
event-facade bindings, or leave Controlify pending without breaking fallback
input. Preserve SDL global-filter separation, keyboard/mouse handoff, haptics,
existing-file sidecar and truthful errors. No arbitrary loader or replacement mod.

Iris remains permitted only on a real Zink context. Matching resource/shader packs
must use the instance's exact game version and normal metadata/configuration.
No claim that an advertised Iris build or Sodium JNI check establishes shader
loading/rendering on PS5. Distant Horizons remains out of scope here.

## Budget, authentication and remaining experiments

Retain204's Java25/G1 policy,1536MiB heap,64MiB compressed class space,96MiB code
cache, four active processors, genuine management integration and **ZIP budget8**.
The generic startup still defaults64; do not accidentally restore it by using the
generic179 builder. Retain the already enabled scratch/verifier/compiler-TLS/
extended-sync/64MiB-owned-stack policies and their real priming/failure checks.
No new reserve or heap/GC enlargement is justified by metadata.

**No comparable full-assets Vanilla/Fabric+Sodium+Controlify resource measurement
exists yet**, on121 or against26.1. The bounded incomplete-assets runs cannot
establish heap/metaspace/class-space/code-cache/thread/FD peaks or console fit.
Finish those experiments after agreeing the binding design; record exact inputs,
native/Java owner, allocation/descriptor peaks and joined cleanup. Keep raw data
local. Host macOS OpenGL is not the target Zink/RADV resource footprint.

All versions retain publisher `--accessToken`, `--uuid`, `--username`, `--version`
and account-type argument structure. Read-only inspection of all five authlib
versions confirms the same `joinServer(UUID, String, String)` declaration in
YggdrasilMinecraftSessionService; no authlib adapter is indicated by that surface.
Keep ProsperoAuth/approved OAuth client unchanged. No authenticated live session/
matching-version server join was performed; metadata is not confirmation that
all older authlib/HTTP/native paths work. Only matching121 servers are in scope
for joining; do not change the separate server downloads.

After approval, complete the remaining host experiments and symbol/owner/size
audits before per-release development gates. Add deterministic injected121
input/version/policy tests alongside the existing lanes; assert unchanged26.x
support, arguments, overlays and option bytes. Then build a new local candidate
through the204-derived preparation path, recording pins/checksums/size/identity
and exact package/native audits. No candidate is handed off by this draft.

Every enabled release then needs physical Vanilla followed by Fabric install,
title, world create/play, save/title/reload, Quit Game/library/relaunch, audio,
fallback/Controlify/keyboard/mouse, matching server, mod and resource-pack checks;
selected shader pack/profile loading/rendering is mandatory before release
unless explicitly scoped out. Regress26.1/26.2/26.3 Vanilla/Fabric and supported
snapshots on the same build. Preserve204 and archived snapshots. No new release,
prerelease or Store action without exact physical confirmation and explicit
authorization. NeoForge prompt support tables change only after121 acceptance.

## Reproduction, checks and decision

Use original metadata URLs/SHA1s in the draft, verify each body before consuming
its download pins, and fetch into an ignored isolated directory. Inspect unchanged
clients with the JDK25 `javap -c -p -constants -classpath <original-client.jar>
<binary-class>` command, locating names from locally downloaded official mappings.
The existing `tools/audit_client_261.py:class_info/jar_info` supplies the read-only
native descriptor parser used here. Compare tuples including descriptors and
staticness, not only method names. For JNA, compile the unchanged runtime
`java25/tests/JnaNativeProbe25.java` separately against each publisher JAR; force
the hash-verified5.19.1 host dispatch and require missing-library failure with
`jna.nosys`, `jna.noclasspath` and `jna.nounpack` enabled.

Local existing17 fast checks and source-only outside-root17 checks with an
initially empty dependency cache pass; documentation and diff checks pass.
Actual [Ubuntu/macOS jobs](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41700953629)
for research sourced91fdab were inspected; final results are recorded in the
matching validation. Native/graphics lanes were
not rerun for this research-only change; no native implementation changed.
No portable test code or launcher options changed. A fresh-cache source-only
outside-root check is recorded separately from local and hosted execution.

**Required user decision:** authorize the narrowly scoped genuine3.3.3 PS5 Java
platform/dispatch overlays plus matching isolated333 natives described above,
starting1.21.11 Vanilla then Fabric, with the provisional2–8MiB estimate replaced
by actual build measurements? Without that publisher-library overlay approval,
all twelve remain Coming soon: native-only integration cannot recognize PS5.
