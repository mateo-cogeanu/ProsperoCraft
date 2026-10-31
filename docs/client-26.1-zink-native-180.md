# Zink native implementation and stage-1 candidate 180

This continues the [26.1 plan](client-26.1-zink-plan.md). Genuine Mesa GL/Zink,
the private kopper display branch, GLFW context hooks and opt-in parent LWJGL
dispatch are now implemented and exercised on the host. **Minecraft 26.1.x is
still blocked in the production launcher.** No title/world/save or PS5 result
follows from these component checks. No release or Store update is authorized.

User reports **Stage1 PASS** for exact180. [Console receipt](validation/client180-console-stage1-2026-10-31.json)
records the scoped result; raw run reports have not been independently retrieved.
Presentation and JVM/game checks remain pending.

## First physical checkpoint

Local candidate **PPSA99874 / 01.000.180** is a dedicated native context probe,
not the normal launcher. It reserves version 180; use a later free identity for
the next full game candidate. It installs over the existing app because the
title identity is shared. Released179 and its exact package remain preserved.
The ordinary startup param and published root param remain179.

1. Install the candidate's complete PPSA99874 folder. Open it, then press **X
   once**. An initial blank screen and blank background during the test are
   expected: this stage creates offscreen GL contexts and does not present images.
2. Expect a system notification reporting **Zink180 stage1 PASS**, or a failure.
   Three actual 3.3+ core contexts each clear a distinct color, check 64 RGBA
   pixels and 128 guard bytes, unbind and destroy the context/final screen.
   Totals: 192 pixels and 384 guard bytes. GL_VERSION/GL_RENDERER and individual
   checkpoints go to the current-run reports, not an invented on-screen card.
3. Keep it open for read-only `http://<PS5-IP>:8765/` reports. `build.txt`,
   `session.txt`, `startup.log` and `vm-trace.log` identify the exact version/run
   and native stages. After a crash, reopen **without pressing X** to preserve
   the failed run. Native-only placeholder/absent Java/hs-error files are not VM
   results. Raw reports stay local.
4. Report the notification/outcome. A native context pass covers only this row;
   animated presentation/refresh/clean launcher return, original Main/title,
   world/audio, save/reopen/quit/relaunch for all three versions, existing Vulkan
   version regressions and endurance remain pending.

The probe uses the native003 CRT/link/converter path and existing hardware-name,
bounded input/present diagnostics and genuine reserved WSI worker. The worker
remains idle/process-owned in this stage. It includes **no JVM, JNI, GLFW, SDL,
OpenAL, Minecraft JARs or asset objects**. Its lighter native resource pressure
does not establish coexistence with the current Java runtime or a game heap.
App-data shader caching uses `/download0/ProsperoCraft/cache/zink` with checked
directory creation and environment setup. Console cache behavior is unvalidated.

## Native implementation

`build_zink_native.py` exports the SHA-256-pinned Mesa26.2 source archive, applies
the three Zink patches and all existing VideoOut patches0001–0010, and builds
RADV and GL/Zink in the **same Meson build**. Original tracked Mesa, the accepted
graphics build and SDK archives are unchanged. Compiler/JDK/SDK/host inputs are
explicit; GLSL requires Bison3+, selected with `--bison`. Offline mode verifies
shared pinned zlib source/adapter caches and forbids Meson downloads.
Reuse checks original exported file/link hashes plus patched/overlay hashes;
side edits fail instead of being reset. Overlay iteration updates only verified
previous generated overlays. No private game-cache discovery is performed.

The PS5 RADV archive already embeds NIR/SPIR-V/utilities. Linking every other
archive whole duplicates those definitions. The combined component keeps RADV
whole and uses normal archive resolution for GL/Zink additions, with no
allow-multiple-definition flag. Actual target link checks require one each of
the ICD entry, RADV instance/device, NIR shader creation and GL dispatcher.
Constructors remain genuine and run through the existing native CRT for180.
A later JVM package must retain the existing scoped graphics allocator/sync and
explicit-constructor integration; this unscoped object is **not** an additional
resident group to link alongside another RADV/Mesa copy.

- `0001-resident-vulkan-entry.patch`: PS5 uses the current layerless resident
  loader. Device lookup comes from the created instance. Desktop loader behavior
  stays intact. Screen creation returns an actual null pointer on driver failure.
- `0002-kopper-private-display-surface.patch`: generated VK_KHR_display support,
  new kopper surface/hash/extent branches and FIFO policy. The loader stores an
  owned callback/window payload rather than overflowing the old create-info
  padding. GLFW's adapter calls existing SDL display/plane selection with
  **Zink's instance**, creating no second device or presenter. Opaque ABI handles
  use checked64-bit copies between genuine Vulkan and GLFW's minimal types.
- `0003-constant-emulated-gl-tls.patch`: compiler-generated C dispatch and
  constant-initialized `__thread` context/dispatch storage on the PS5 path.
  Actual target glapi uses `__emutls_get_address`; no fs/GOTTPOFF GL dispatch or
  C++ lazy current-context wrapper is introduced. Existing emutls fallback and
  retirement policy remain runtime-owned.

`frontend.c` is a **private Mesa frontend, not EGL or OSMesa**. It creates real
core `st_context`s and Gallium/kopper drawables, queries Mesa's GL dispatcher,
validates resources before successful make-current, performs actual driver
flush/presentation, and releases real contexts/resources/screens. Ownership
refuses foreign-thread binding/destruction; explicit unbind permits transfer.
Caller thread-exit/orphan recovery and arbitrary contexts/mod behavior are not
promised. A failed surface callback is rejected under the host failure control.
Positive PS5 kopper presentation and swapchain failure/recreation remain pending.

GLFW retains genuine3.4 core and SDL input/window handling. The new optional
hooks support native desktop core context version/forward/debug hints,
make/get-current, proc lookup, real GL extension queries through generic GLFW,
swap interval and framebuffer callbacks. Original 26.1 hints are exercised.
Explicit EGL-source, shared/compatibility/no-error/robust contexts, stereo/MSAA
and requested sRGB default buffers fail rather than being fabricated. Absence
of the weak resident frontend keeps OpenGL unavailable and preserves no-API
Vulkan windows. A later app must register only the needed `ps5zink_*` ABI exports.

Parent GL Java dispatch selects this provider **only** when the consumer sets
`ps5.opengl.provider=zink` before GL initialization. It uses the existing resident
PS5Library and genuine `ps5zink_get_proc_address`, with no arbitrary loader or
new game classes. Defaults preserve029 OSMesa bootstrap for current Vulkan
clients. Original downloaded GL/game JARs are intact.

## Measured host checks

The new explicit `zink` research lane requires separately built native providers
and verified original publisher inputs. It is not a fresh-clone/hosted GPU lane:

```sh
python3 tools/run_host_tests.py --lane zink --cc /path/to/llvm/bin/clang \
  --graphics-config /path/to/local-zink-host-inputs.json
```

[Example input keys](../tests/zink-host-config.example.json) identify every path;
the runner does not fetch game/native inputs or search private caches. This
execution is macOS ARM64 lavapipe, not MoltenVK or PS5 RADV. Mesa GL/Zink is the
pinned26.2 implementation; an explicit wrapper uses the same real lavapipe ICD
boundary as124. Host `LIBGL_ALWAYS_SOFTWARE=true` selects that actual CPU Vulkan
device; it is not used for PS5. SDL dummy windows render to real offscreen Zink
drawables; no host VideoOut/window-surface presentation claim is made.

Measured results: native3 context cycles with GLSL triangle draw/clear/readback/
guard checks, resize, foreign ownership refusal, thread transfer and destruction;
refused real surface callback; actual rebuilt GLFW and LWJGL clear/draw/guard/
thread/lifecycle checks for **each26.1/26.1.1/26.1.2** (three cycles each);
missing-Zink refusal plus successful no-API window; and original GlBackend hints
and original GlDevice capability creation. The constructor test deliberately
stops at injected null debug options **after** capability creation: it is not an
original Main/title/full-GlDevice pass. The unchanged consumer OSHI overlay uses
explicit host fixture CPU metadata to avoid unrelated macOS IOKit/JNA telemetry.
The enum override is a host-only dispatch control, never a packaged OS spoof.

ASan/UBSan instrument the new frontend, GLFW and native test driver; JDK25 runs
Xint/XcheckJNI/full verification. Mesa's remaining code and external lavapipe use
ordinary builds. Test-only Unsafe deprecation warnings remain explicit. No JNI
check or sanitizer failure is accepted. Existing actual029 OSMesa dispatch and
negative control pass, as do existing GLFW/SDL event/allocator/lifecycle/refusal
regressions and the16 fast/seven native policy checks. [Ubuntu/macOS CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41235442939)
also passes all16 fast checks for source86a7d93; no hosted GPU or physical result
is inferred.

## Reproduce the component/candidate

```sh
python3 tools/build_zink_native.py --llvm-home /path/to/llvm \
  --lld /path/to/ld.lld --bison /path/to/bison3
# --offline verifies provisioned archive/zlib caches and forbids downloads.
# --archive can explicitly reuse the verified Phase A archive.
python3 tools/package_zink_probe.py --check-only \
  --runtime-workspace /path/to/runtime --llvm-home /path/to/llvm \
  --component /path/to/printed/ps5/zink-radv-unscoped.o
python3 tools/package_zink_probe.py \
  --runtime-workspace /path/to/runtime --llvm-home /path/to/llvm \
  --component /path/to/printed/ps5/zink-radv-unscoped.o
python3 tools/test_client180_package.py \
  --runtime-workspace /path/to/runtime --llvm-home /path/to/llvm
```

The existing pinned graphics SDK, Meson environment, host shader tools, native
converter/clean-room libc and upstream notices are prerequisites from the normal
graphics preparation. Host build additionally needs explicit `--host-vulkan`
entry-wrapper input and `--moltenvk-dir` headers on macOS (headers only here;
execution uses lavapipe). The test input config requires the rebuilt parent core,
OpenGL JNI, platform/module overlays, adapted GLFW and OSHI provider.

Packages are local under `dist/candidates/zink-context-180`; existing candidate
ZIPs are never overwritten. The [validation record](validation/client180-zink-native-2026-10-31.json) records
clean build source13ac084, package/ELF checksums and separate host/console scope.
The exact local ZIP is18,259,125bytes; SHA-256:
`0cefa6f5faf8013a1c98b1eff0a2c7621bd523d0c24fd2737526312c919e4881`. No release/prerelease is created.

Remaining work: positive kopper presentation/refresh/teardown;
JVM scoped one-copy/constructor/resident integration and package audit; ZINK
receipts, Vanilla development labels/arguments and adapted GLFW precedence for
every locked release, with Fabric26.1 blocked and Iris guarded; then exact-build
game/title/world/save/reopen/exit and existing26.2/26.3/snapshot regressions.
Preserve029 OSMesa, adapted callbacks, all existing allocator/TLS/sync/stack
fallbacks, immutable game downloads, frozen history and current release/Store
gates. No 26.1 compatibility README row or mod support is enabled here.
