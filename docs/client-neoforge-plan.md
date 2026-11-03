# NeoForge client integration — Phase A, 3 November 2026

Phase A research is recorded; implementation is paused at the explicit decision
point in the supplied `NEOFORGE_SUPPORT_PROMPT.md`, section 3. NeoForge remains
**Coming soon** for every version. No launcher/native/runtime code, application
identity, accepted package, release, Store listing or roadmap completion changed.
The [draft lock](../client/neoforge.lock.json) is research data, not an installer
receipt or a file currently consumed by the launcher. The
[validation record](validation/client-neoforge-phase-a-2026-11-03.json) separates
inspection/checks from unperformed installation, game execution and PS5 work.

## Baseline and supported versions

Research starts at ProsperoCraft `f43a6a782baa29d0357de2b6fb53681fdb4eef82`, clean
on `main` and equal to fetched `origin/main`. Public release 204 remains preserved.
The shared `client/startup/param.json` deliberately remains 179: release 204 is
built through `tools/package_save_headroom.py` and
`client/save_headroom/{bootstrap.cpp,param.json}`, retaining the shared base.
Do not downgrade 204 by building only the generic 179 entry point. The shared
launcher still calls 26.1.x a `developmentTest()` internally; 203 removed its
visible development labels. This is existing build selection, not evidence that
public 204 lacks those versions.

`ProsperoLauncher.supported()` explicitly allows 26.2, 26.3 and snapshots 1–6.
`ProsperoGraphics.release261()` adds exactly 26.1, 26.1.1, 26.1.2 when the existing
Zink resource is present. Snapshot choices retain Show Snapshots, default off.
The catalog's broader 26.x regex is a download boundary, not a launch allowlist.

## Upstream version enumeration

The complete [official Maven metadata](https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml)
and [versions API](https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge)
contained the same 1,856 version strings. The XML `lastUpdated` was
`20261101220411`; payload hashes and exact per-family lists are in the draft lock.
Only the selected five installers were fetched and inspected, not every historic
installer. Family membership for older builds is inferred from the observed
numbering; each selected installer's own `minecraft` and `inheritsFrom` confirms
the table. Future installation must validate those fields rather than infer them.

| Minecraft | Selected upstream candidate | Channel | Window / proposed renderer | Current NeoForge state |
| --- | --- | --- | --- | --- |
| 26.1 | 26.1.0.19-beta | Beta only | GLFW / existing Zink | Coming soon; decisions required |
| 26.1.1 | 26.1.1.15-beta | Beta only | GLFW / existing Zink | Coming soon; decisions required |
| 26.1.2 | 26.1.2.126 | Stable | GLFW / existing Zink | Coming soon; decisions required |
| 26.2 | 26.2.0.93 | Stable | GLFW / Mojang Vulkan | Coming soon; integration and validation required |
| 26.3 | 26.3.0.101 | Stable | SDL / Mojang Vulkan | Coming soon; integration and validation required |
| 26.4-snapshot-1 through 6 | None | No published matching family | Existing SDL / Vulkan policy | Coming soon; upstream build absent |

Observed release naming is `26.<game minor>.<game patch or 0>.<loader build>`.
For example, 26.1.2.126 identifies game 26.1.2, while 26.2.0.93 identifies 26.2.
Unsuffixed candidates are stable; `-beta` is explicit. Older catalog alpha entries
such as `26.1.0.0-alpha.10+snapshot-6` target the 26.1 snapshot cycle, **not** 26.4.
Select the numerically latest stable build for an exact validated game family.
Beta-only families require user opt-in and a visible Beta label, never automatic
fallback. Repair retains a chosen fully verified receipt version.

## Installer anatomy and patched output

All five SHA-1-sidecar-verified installers have `spec=1`, embedded `/version.json`,
`mainClass=net.neoforged.fml.startup.Client`, exact matching game inheritance,
26 launch libraries (27 for 26.3) and 30 install libraries (29 for 26.2).
Installers range from 3,608,527 to 11,322,753 bytes; propose a 16 MiB download
bound and separate bounded profile/version reads. Exact byte sizes, SHA-1,
SHA-256, embedded JSON hashes, all library pins and processor arrays are recorded.
The icon/base64 profile field is deliberately excluded from the draft.

All referenced library artifacts carry SHA-1 and positive size. Their download
hosts are exactly `maven.neoforged.net` and `libraries.minecraft.net`; restrict the
installer itself to the former. No library sidecars are needed for these profiles;
the installer uses its Maven `.sha1` sidecar. Ignore upstream mirror-list URLs,
reject redirects/foreign hosts, and do not broaden the general downloader's
allowlist for unrelated traffic.

The two processors are identical in structure across the candidates:

| Processor | Client applicability | Inputs and result |
| --- | --- | --- |
| `net.neoforged.installertools:installertools:4.0.12:fatjar` on 26.1.x, `4.0.17:fatjar` on 26.2/26.3; `EXTRACT_FILES` | Server only; skip | Server run scripts/JVM argument files; never execute/extract these for client setup |
| Same genuine processor; `PROCESS_MINECRAFT_JAR` | Both sides when `sides` is absent | Original client input, `--no-mod-manifest`, `--output {PATCHED}`, `--extract-libraries-to {ROOT}/libraries/`, `--apply-patches {BINPATCH}` |

Client `BINPATCH` is installer entry `/data/client.lzma`. `PATCHED` resolves to
`net.neoforged:minecraft-client-patched:<selected NeoForge version>`; the server
coordinate is separate and outside this task. `MCP_VERSION` contains the quoted
NeoForm version (26.1/26.1.1/26.1.2/26.3 `-1`, 26.2 `-2`), but this processor
invocation has no mapping argument. These unobfuscated client pipelines have no
separate mapping or client/server merge step. The upstream tool's
`ProcessMinecraftJar` applies binary patches and strips signature-related entries
from its **derived output**. It must never overwrite the official client input.
Its fatjar manifest entry point is `net.neoforged.installertools.ConsoleTool`.

**None of these processor objects declares an `outputs` hash map.** Do not invent
an upstream output checksum. Their patch implementation checks base-entry
checksums, but that is not an independently declared whole-output hash. After
approval, establish deterministic host outputs from verified publisher inputs,
record matching derived pins, and test target equality/reproducibility before
allowing Play. Locally computing and trusting a hash of an arbitrary pre-existing
cache file is insufficient. No processor was executed during Phase A.

Every derived file would live only under `cache/neoforge/`, using a validated
version-specific coordinate path. Preserve and reverify the original
`cache/versions/<game>/client.jar`. Disclose upstream NeoForge patching and its
runtime transformers; ProsperoCraft adds no game/mod bytecode hook or replacement
class and downloads original upstream loader/mod artifacts intact.

## JVM startup options and process design

Every inspected version JSON contains exactly this JVM argument array:

```json
[
  "-Djava.net.preferIPv6Addresses=system",
  "-DlibraryDirectory=${library_directory}",
  "--add-opens",
  "java.base/java.lang.invoke=ALL-UNNAMED",
  "--add-exports",
  "jdk.naming.dns/com.sun.jndi.dns=java.naming"
]
```

| Entry | Classification | Consequence |
| --- | --- | --- |
| `java.net.preferIPv6Addresses=system` | System property (a), potentially cached by networking | Set at NeoForge VM creation so launcher networking cannot initialize the previous value first; preserve existing IPv4-stack policy pending compatibility checks |
| `libraryDirectory` | System property (a) | Resolve only to the verified NeoForge library cache, not caller-provided text |
| `java.base/java.lang.invoke` open | VM creation option (c) | Launcher does not own `java.base`; public ModuleLayer APIs cannot grant this opening |
| DNS package export to `java.naming` | VM creation option (c) | Preserve upstream option; audit target image modules and actual requirement, do not silently omit it |

There is **no** `-p`, `--add-modules ALL-MODULE-PATH`, `legacyClassPath`,
`ignoreList`, named-module native-access option or BootstrapLauncher in these
profiles. FML itself builds its module layers. `ModuleClassLoader` in every
inspected FML 11/12 source reads `MethodHandles.Lookup.IMPL_LOOKUP` and binds
layers through it. This is upstream code, but proves the package opening cannot
be replaced by a `java.class.path` property update. Do not add our own reflective
module-opening hack or install global NeoForge options for Vanilla/Fabric.

Recommend a **NeoForge-only fresh-process handoff**, extending the existing
`--prospero-library` LoadExec process replacement. Before replacement, persist a
small launch request containing only schema, instance UUID, exact pinned NeoForge
version and receipt SHA-256; never tokens, auth arguments or free-form JVM options.
The next process verifies request bounds, instance/receipt correspondence, paths,
symlinks and all artifacts **before JNI_CreateJavaVM**. Derive a finite option set
from the verified profile and a compiled allowlist of exact module/package targets.
Use owned bounded storage for option strings throughout VM creation. A receipt
hash is a consistency binding, not authentication against malicious storage.
Clear/consume requests once; malformed/stale requests return safely to library.
Re-establish normal account/entitlement checks in the new JVM; do not persist
access tokens to carry sign-in across the handoff.

Keep the Vanilla/Fabric ordered option table and all bootstrap behavior unchanged,
with native assertions for requests absent/invalid and legacy paths. Retain genuine
classloader/module ownership: FML's module loader is child-first, so Fabric's
`systemLibraries` recipe cannot simply be copied. Prove FML delegates existing
parent LWJGL/OSHI and resident JNA correctly, or keep the row disabled. On clean
quit, observe the actual game content loader; preserve stopped-game/current-run/
SDL-zero/exit-status checks and OS replacement. FML closes owned resources only
on normal return; System.exit and parallel mod shutdown need distinct tests.

The upstream `Entrypoint` passes nullable `DevAgent.getInstrumentation()` to FML.
Production `create(instrumentation, args)` allows null and only creates its class
loading guardian when non-null. Do **not** infer that the separate self-attach
helper is required, add ByteBuddy, require a subprocess java launcher, or add a
javaagent without proving the need. No production agent is in the version JSON.

## Early display and graphics

FML 11.0.5 (26.1/26.1.1), 11.0.15 (26.1.2), 11.0.16 (26.2) and 12.0.12 (26.3)
all define `earlyWindowControl`. Their `ImmediateWindowHandler` skips provider
creation when false; the [upstream FAQ](https://docs.neoforged.net/user/docs/faq/)
also documents this configuration. Write a new per-instance `config/fml.toml`
with `earlyWindowControl=false` before first launch. Preserve an existing user
file: parse it safely; if the early window remains enabled, report the conflict
and refuse this integration rather than overwrite the setting. Java AWT headless
mode alone does not set FML's explicit `headless` launch argument.

26.2 upstream Window patch takes over the GL early window only when a controller
exists; disabling it leaves `GpuBackend` window creation intact. Its Main patch
retains the forced graphics-api field. The inspected 26.3 Window patch uses SDL
and a backend-created window; its RenderSystem additions operate on GPU pipelines.
FML12's early window itself uses SDL/OpenGL, so SDL does not make that early path
safe for Vulkan. All inspected ClientModLoader versions guard early-screen calls
for null. No core hard GL-only requirement was established with early display
disabled. The [upstream Vulkan issue](https://github.com/neoforged/NeoForge/issues/3257)
is historical beta evidence, not proof the selected stable releases work on PS5.

Thus **26.2/26.3 remain proposed Vulkan candidates**, with exact FML/window/renderer
handoff and render-hook validation still required. GitHub branch source snapshots
are pinned as context, not claimed byte-for-byte matches for the selected binary
patch bundles. Complete original-artifact host startup/graphics checks must settle
that gap after approval. Never silently switch those versions to Zink. If a real
hard GL dependency appears, leave the row Coming soon and ask separately.

All three 26.1.x versions need the existing Zink path. `all-loaders-26.1-zink-v2`
currently means Vanilla/Fabric only; preserve it and v1 exactly. Propose a new
explicit NeoForge-capable token, with early display disabled and the same pre-JVM
prepared screen, flushsync/direct context, scoped env/TLS ownership, real native
handoff and final SDL cleanup as 204. Do not extend the Fabric-only experimental
Sodium LWJGL check opt-out without inspecting the genuine NeoForge Sodium path.
The new loader's GL/render hooks and shutdown need their own PS5 acceptance.

## Mods and Modrinth

Use verified-receipt NightConfig TOML plus Maven `VersionRange`/`DefaultArtifactVersion`
from an isolated closed loader, following FML's own metadata implementation rather
than hand-writing TOML or Maven semantics. Receipt versions are 3.8.3/3.9.0 for
NightConfig and 3.9.9/3.9.16/3.10.0 for maven-artifact. Scan original
`META-INF/neoforge.mods.toml`, declared multiple mods/dependencies and
`META-INF/jarjar/metadata.json`; account for manifest-substituted versions rather
than comparing literal `${file.jarVersion}`. Builtins are minecraft, neoforge and
java 25. Respect required/optional/incompatible/discouraged and client/server side;
only required client/both dependencies become install requirements. FML remains
the final resolver, including ordering and jar selection.

Retain bounds: 128 KiB metadata, 16 MiB individual nested archive, 64 MiB aggregate,
depth at most 8, at most 1,024 modules and bounded archive entries. Reject links,
unsafe nested paths, duplicate/conflicting roots, unresolved placeholders and
unsupported metadata with a clear repair/manual-resolution message. Use loader
specific identification for upgrades and reject Fabric-only content in NeoForge
and the reverse. Never apply the Fabric API project `P7dR8mSH` rule to NeoForge.

[Modrinth search](https://docs.modrinth.com/api/operations/searchprojects/) uses
`categories:neoforge`; mod version queries use `loaders=["neoforge"]`, and returned
version records must explicitly include that loader and the exact game. Resource
packs and shader packs have content-loader tags such as minecraft/iris, not the
mod-loader tag: preserve correct content-kind filtering and validate the shader
engine separately rather than demand `neoforge` on every pack.

Official API observations (full query payload hashes and per-game version records
are in the draft, no mod JAR download/execution):

| Content | 26.1 / 26.1.1 / 26.1.2 | 26.2 | 26.3 |
| --- | --- | --- | --- |
| Controlify DOUdJVEm | 3.5.3+mc26.1, CCtUQSV4 | 3.5.3+mc26.2, VDw4mGkG | 3.5.3+mc26.3, fo76vL20 |
| Iris YL57xq9U | 1.11.4+26.1-neoforge, qE5Y7GrZ | 1.11.4+26.2-neoforge, k55HdONq; block on Vulkan | 1.11.7+26.3-neoforge, Ag5S66CF; block on Vulkan |
| Vitrail oSIKhgz3 | No matching build | 0.13.0-beta+mc26.2, jmyfnI6L | 0.13.0-beta+mc26.3, Q3nKuPKJ |
| Oculus GchcoXML | None | None | None |

Controlify records list both Fabric and NeoForge; this does not prove every
nested backend/dependency works on both. The 26.3 keyboard-layout workaround is
currently Fabric-only and exact-hash scoped; inspect the NeoForge artifact before
expanding it. Keep genuine resident SDL alias facade/path preflight, raw input,
haptics and controller/keyboard/mouse ownership. Default installation remains
one-time and respects later uninstall. No observed compatible content for the
supported 26.4 snapshots; there is also no matching NeoForge loader.

## Resource budget and runtime ownership

Retain 204's real policy: Java25, G1, 1,536 MiB heap maximum, 64 MiB compressed
class space, 96 MiB code cache, four active processors and genuine management
integration. MetaspaceSize=128m is a threshold, not a complete metadata budget.
FML has 26–27 launch library entries in addition to publisher libraries and a
patched game cache; those counts/byte sizes do not predict class-space use.
The processor holds archive entries and performs asynchronous patch work, adding
an installation peak independent of normal gameplay. Class-space/metaspace/code
cache and native quotas must be measured on the console; do not promise it fits.

FML `maxThreads` defaults to available processors (four under this VM table) and
also creates a separate sync worker; common-pool discovery and mods add more.
Propose `maxThreads=4` only in newly created FML config, matching the current CPU
policy. Do not treat it as a universal four-thread limit or increase heap/GC,
class space/code cache, or native reserve budgets speculatively.

Existing bootstrap setters already enable compiler-TLS direct fallback, libjava
scratch (three 64-slot/8 MiB units), independent libnet scratch, variable verifier
4 MiB reserve, 8,192 mutex/8,192 relative/2,048 absolute sync reserve and 64 MiB /
64-slot owned-stack budget. Carry those exact policies and check their native
results; they are bounded fallback mechanisms sharing native backing, not proof
of spare memory. Do not copy reusable implementations into the consumer.

204's wrapper selects **ZIP budget 8**, while the generic startup default remains
64. Preserve the accepted 204 headroom policy, immutable inputs and OPEN_DELETE
exclusion. Never restore 64 merely by copying an older Fabric guide, or describe
this as a whole-process FD cap. Patched libraries must remain immutable while
open; regeneration must not replace an in-use archive. Keep descriptor-first paths
and bounded file accounting. `java.management` is used directly by FML startup;
retain genuine `jdk.management`/management_ext for Iris and audit naming modules
required by the export. No new runtime fix is justified by metadata inspection.

## Licensing and implementation sequence after decisions

NeoForge/FML sources identify LGPL-2.1-only; NeoForge's pinned license is recorded.
InstallerTools 4.0.17's official POM also declares LGPL-2.1-only. FML's inspected
POM omits a license list, so its source SPDX notices remain necessary evidence.
Fatjar components have independent licenses; audit their transitive notices
before the actual feature ships.
Nothing new is redistributed by Phase A. The proposed console feature downloads
upstream artifacts at the user's request, so no loader/processor/mod/game JAR
needs to ship. Add this fact, upstream patching disclosure and source/license links
to NOTICE/third-party documentation when implementing download support; do not
relicense downloaded artifacts or assume one license covers every dependency.

After decisions: establish deterministic derived-output pins and original-artifact
host loading; implement a strict install/verify/receipt pipeline; then the bounded
fresh-process handoff and per-loader gates; then Modrinth/TOML/jarjar handling and
loader-specific input/shader guards. Leave graphics-unproven rows disabled. Assert
unchanged Vanilla/Fabric tables, requests, launch arguments and option bytes.
Keep the existing six 26.1.x combinations and 26.2/26.3/snapshot policies intact.

Run all deterministic fast tests, affected native tests and source-only/outside-root
checks; inspect actual hosted jobs after pushing. Build a new local identity only
after integration. Record package/title/runtime/lock hashes, audit signatures/CRC/
Java-native identity and preserve 204 exact bytes. No Phase A package is needed.

Physical checks remain entirely pending for NeoForge: installation/repair/cancel,
title, world create/load/play, save/reopen, Quit Game/library/relaunch, Controlify
and physical input/haptics/audio, one compatible mod install/uninstall, selected
shader pack/profile rendering and enable/disable, Vanilla/Fabric regressions for
each enabled version, descriptor/native pressure and endurance. Host results are
separate from PS5 acceptance. No release/prerelease or Store action until exact
physical confirmation **and explicit release authorization**, including the
required NeoForge shader check unless explicitly scoped out by the user.

## Required user decisions before Phase B

The supplied prompt explicitly says to stop after Phase A for these conditions:

1. Allow **NeoForge's own upstream patched client output** in its separate cache,
   with the original official client.jar intact and verified?
2. Allow the proposed **NeoForge-only fresh-process handoff**, preserving
   Vanilla/Fabric JVM option tables and normal authentication checks?
3. Include **26.1.x NeoForge through existing Zink** under a new explicit mode?
4. Include the **beta-only 26.1 and 26.1.1 loader builds** with a visible Beta label,
   or keep those two Coming soon and implement stable versions first?

No decision has been presumed. The plan and disabled draft can be published now;
implementation and physical validation remain outstanding.
