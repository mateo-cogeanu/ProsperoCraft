# Client bring-up

The user authorized client work on 2026-10-22 after positive Fabric094/Paper108 console feedback, explicitly leaving the two-hour server test pending. The Fabric/Paper release is now a full release at the user's request. This changes the work order; it does not add a formal ALL PASS or endurance result. Server packages remain preserved and client preparation uses a separate build directory.

## First completed stage: pinned artifacts and class preflight

`client/26.3.lock.json` pins the official 26.3 client plus 53 unconditional Java libraries, metadata and the asset index by published size/SHA-1 and locally checked SHA-256. The official client JAR is unchanged. All 61 conditional desktop artifacts are recorded but excluded from PS5 staging, including LWJGL platform binaries and desktop Netty transports. Some unconditional JARs themselves contain desktop native resources (JNA:26, LZ4:8, counted by native-file suffix); those signed JARs remain intact and their native resources are not initialized/extracted by the preflight. No desktop binary is claimed to be PS5-compatible.

The current official metadata differs from the server's earlier metadata snapshot only in the asset index. Client JAR bytes are identical: SHA-1 `e877b6a07acd633fb3bb475002175cec036e7b87`. Client preparation pins the newer asset index without changing server pins. Asset index34 is verified; its roughly485MB of asset objects are not yet fetched. No account tokens or credentials are requested or stored by these tools.

Prepare locally:

```sh
python3 tools/prepare_client.py
```

Artifacts stay in ignored `.tools/client/` and `build/client/`. `--offline` requires the complete verified cache and makes no download requests. A cached size/hash mismatch is an error. All inputs are checked before the separate client staging directory is replaced. The working server asset directory and current package are untouched.

Run the host preflight with an actual Java25 toolchain:

```sh
python3 tools/test_client_artifacts.py --java-home /path/to/jdk25
```

The real JVM runs with `-Xverify:all`, verifies all54 JAR hashes, and loads the original main client, window, SDL event, RenderPearl Vulkan backend/instance and LWJGL SDL/Vulkan classes with initialization disabled. The probe does not invoke Minecraft, native initialization, login, a GPU call or rendering. A deliberate same-size client-JAR corruption is rejected before class loading and restored afterward. No class or bytecode transformation is applied.

A separate real-JVM control initializes the original LWJGL Platform class under `os.name=PS5` and reproduces `LinkageError: Unknown platform: PS5`. This is the first known dependency port boundary, not a solved client-launch test. No OS identity override is used to make the game run.

## Graphics and native integration

The inspected official client already contains a Vulkan renderer and SDL integration. Its original VulkanInstance bytecode requests Vulkan1.2 and calls `SDL_Vulkan_GetInstanceExtensions`; the Java/backend classes alone do not establish driver, surface or feature compatibility. A renderer replacement is not assumed necessary at this stage.

[PS5_Vulkan](https://github.com/mihawk-99/PS5_Vulkan/tree/f410e67a0241b3e8edcdbcd2a9b285dfc4a412ed) remains an evaluation candidate. `client/graphics-candidates.json` records its inspected source revision and the Mesa/SDK revisions named by its upstream build scripts. Those are source-evaluation pins, not built or validated dependencies. The upstream RADV/VideoOut claims are not console results from this project. Do not replace the working runtime SDK globally while evaluating this separate stack.

Next work is actual dependency platform support and native bindings, with a small native presentation test and Java-to-SDL/Vulkan bridge before attempting the client menu. LWJGL core/native invocation, SDL window/events/Vulkan surface creation, allocator integration, shaderc/SPIRV-Cross/VMA, text/image resources, OpenAL and controller input each require supported PS5 implementations and validation. Bundled JNI libraries must not silently fall back to desktop binaries. Preserve the official game JAR and keep compatibility in the Java port, dependency ports or external harness.

No PS5 client app, graphics frame, menu, world or controller result is claimed yet. Server endurance and remaining lifecycle checks remain pending separately.

## Client Foundation 01.000.000: shared-title console probe

At the user's request, the client now uses server title `PPSA99874` and its exact content identity. Client builds start at01.000.000 and advance independently of the server build counter, as explicitly requested by the user. Installing this client probe replaces the installed server app; the tested server packages and source snapshots are retained for reinstalling. The user reports ALL PASS for all six rows on2026-10-22; the source/package is now frozen as Client_Foundation. This remains a foundation test, not a playable client. Local package: `dist/client/PPSA99874.zip` (also in the runtime workspace's `dist/`). The package hash is recorded in `client/build-status.json` and the local `SHA256SUMS`.

The initial untested ClientFoundation000/PPSA99875 and shared-title109 candidates are superseded and preserved locally. The six foundation rows and dependency/native bridge are unchanged; only application identity/version and documentation change.

Run all six rows in order:

1. Initialize the embedded core runtime.
2. Create the Java25 interpreter VM (128MiB heap, compact headers).
3. Verify the original54 client/Java JAR hashes and load selected original client/SDL/Vulkan classes with initialization disabled.
4. Run the source-built LWJGL PS5/x64 platform check. This row requires the native function resolver to report its explicit unported error; its PASS means platform identification and honest capability handling, not native library loading or graphics.
5. Run actual registered JNI direct-buffer writes, checking zero-length and sliced buffers, guard bytes, checksums, and heap/null/read-only rejection. The native call borrows the buffer synchronously; no pointer escapes and no allocation ownership transfers.
6. Destroy the VM and retain the UI for reports.

There is no login, network client, Minecraft main invocation, GPU driver, SDL window, OpenAL initialization or frame rendering. The UI uses the existing native probe renderer. The log server listens on available interfaces at port8765, without preset addresses or client filters. Reports include build/session identity, startup history, VM trace and the current exception. Keep the app open after the rows; reopening preserves reports until another initialization.

The dependency port lives in `client/ports/lwjgl/`: original source archive hash and license, source patch, build script and output audit. It appends an explicit PS5 enum after existing platform ordinals, uses `ps5/x64` resource paths and `.so` library naming, and makes unresolved PS5 function loading fail explicitly. Only the Platform/APIUtil source units are recompiled with Java8 class format; all other original dependency JAR entries remain byte-identical. Eleven generated classes change/add; the port adds its retained BSD license. This is a disclosed dependency port, not a game-JAR rewrite. Original LWJGL and official Minecraft artifacts remain intact. The new port is activated only for this foundation probe, not for game execution.

Host verification passes in isolated real-JVM processes for PS5 amd64/x86_64, non-x64 refusal, unchanged FreeBSD/Linux/macOS/Windows selection, original ordinals, target names/resource paths and explicit native-loader failure. The JNI bridge runs against a real host JVM with XcheckJNI/UBSan. Package checks cover CRC/signatures, title/version, original54 artifacts, exact dependency delta, current target libraries/module image, symbol/package copies, options, silence and unchanged Fabric094/Paper108 packages. These are not console results.

Build and check:

```sh
python3 tools/package_client_probe.py --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25
python3 tools/test_lwjgl_platform.py --java-home /path/to/jdk25
python3 tools/test_client_bridge.py --java-home /path/to/jdk25
python3 tools/test_client_package.py --runtime-workspace /path/to/PS5_Homebrew
```

The packaging flow currently uses the runtime workspace's macOS toolchain. Native presentation, PS5 LWJGL function resolution/core bindings and SDL/Vulkan integration remain next. Server two-hour endurance stays pending separately.

## Console acceptance and freeze

The user reports **ALL PASS** after the exact shared-title000 package on2026-10-22. All six foundation rows are accepted on the actual PS5. The tested package hash is `e2eb90a727fc670418437937b292b152c5177e3e02077aa114049bc6c9c11fbf`.

The frozen [Client_Foundation source/validation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Foundation/README.md) and [release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Foundation-v01.000.000) preserve this milestone. Public packaging excludes54 original upstream JARs without rebuilding retained binaries; the attached helper restores all tested bytes from hash-verified local preparation. Native LWJGL loading, GPU/SDL/Vulkan presentation, audio, controller gameplay and actual Minecraft startup remain unvalidated. Continue future development outside the frozen folder. Server endurance remains deferred.

## Development001: resident JNI loading

[Client Native Loading001](client-native-loading-001.md) is the next seven-row milestone, reported ALL PASS on the PS5 on2026-10-22. It adds actual JVM library/native symbol discovery and scoped function calls through a consumer-owned resident library. Frozen000 is retained;001 is now frozen as [Client_Native_Loading](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Native_Loading/README.md). This advances native-loading infrastructure without claiming full LWJGL native bindings, arbitrary ELF loading or GPU rendering.

## Development002: actual LWJGL core and resident provider

[Client LWJGL Core002](client-lwjgl-core-002.md) adds the eighth row for real upstream native memory/JNI APIs and a PS5 SharedLibrary implementation. Host and target-package checks pass; console validation is pending. Frozen000/001 remain untouched. Driver presentation, SDL/Vulkan and game startup remain ahead.

## Client002 console acceptance — 2026-10-23

The human tester reports ALL PASS for all eight rows of PPSA99874 client01.000.002. The actual LWJGL native memory/JNI subset and resident provider are frozen as [Client_LWJGL_Core](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_LWJGL_Core/README.md), with the exact package hash and source/runtime pins. GPU presentation, SDL/Vulkan, complete native coverage and Minecraft main remain unvalidated. Server endurance remains deferred.

## Native Graphics003 — console pending

After002 ALL PASS, [native003](client-native-graphics-003.md) isolates the pinned
Mesa/RADV driver and its platform SDK for actual GPU clear/copy/readback and
VideoOut presentation. It uses the same PPSA99874 identity with version01.000.003,
but launches no JVM or game. Console confirmation of the RGB sequence, final
card and automated checks is pending. Existing passing milestones are preserved.

## Native Graphics003 acceptance — 2026-10-23

The tester reports the result card, then confirms all requested RGB/card checks
passed with no crash or visual corruption. Client_Native_Graphics003 is frozen
with its exact package/source pins and published as a native-only milestone.
The PS5 log server was unreachable; console evidence is the direct human report.
Java/SDL integration, shader rendering, GPU teardown/recreation and game startup
remain unvalidated; server endurance stays deferred.

## Client GPU Integration004 — PS5 pending

[Client004](client-gpu-integration-004.md) combines the actual LWJGL memory/core
with a resident JNI bridge and scoped RADV offscreen GPU commands in one JVM
process. Java verifies GPU copy/fill results, guards and error controls across
three actual create/destroy cycles. Physical-host-GPU/XcheckJNI/UBSan and target
package checks pass. All nine PS5 rows remain pending. The original runtime
SDK, JVM source and game JARs are unchanged; the combined title explicitly
connects the shared SDK C++ ABI's real TLS callback to the scoped GPU platform.
Full LWJGL Vulkan bindings, SDL/shader/game integration remain ahead.

## Client004 console acceptance — 2026-10-23

The human user reports ALL PASS for all nine rows of PPSA99874 client01.000.004.
Client_GPU_Integration freezes the exact package/source and records Java/LWJGL
GPU copy/fill/readback, negative controls, three Vulkan session lifecycle cycles
and final DestroyJavaVM. Console evidence is the direct user report. Full Vulkan
bindings, SDL/window integration, shader/game rendering and module-global cleanup
remain unvalidated; server endurance stays deferred.

## LWJGL Vulkan Bindings005 — PS5 pending

[Client005](client-vulkan-bindings-005.md) uses the unchanged upstream Vulkan JAR's
standard structs, instance/device capability tables and generic JNI commands.
Supported VK.create(FunctionProvider) uses the resident PS5Library; one native
standard loader entry forwards to the real RADV ICD. Host physical-GPU/XcheckJNI/
UBSan and target package checks pass; all ten PS5 rows remain pending. No game
or Vulkan Java bytecode transformation is introduced. SDL/window integration,
shader rendering and game startup follow separate validation. Frozen000-004 remain.

## Client005 failure and006 correction — 2026-10-23

The tester reports ClientVulkan25 UnsatisfiedLinkError: PS5 resident library
unavailable: ps5clientgpu on row9. The registry key is libps5clientgpu.so; the
fixture passed System.loadLibrary's logical name directly to PS5Library.
[Client006](client-vulkan-bindings-006.md) applies System.mapLibraryName before
that provider open. No alias/driver workaround or Vulkan/game JAR change is
introduced.005 package/symbols are preserved as a failed candidate. Host GPU
and corrected package regression checks pass; all ten PS5 rows remain pending.
