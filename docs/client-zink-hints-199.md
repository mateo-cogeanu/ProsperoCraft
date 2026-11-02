# Default fullscreen hint and genuine no-error context —199

The [198 console receipt](validation/client198-console-window-hint-2026-11-02.json)
records a current26.1.2Fabric failure card after original Main reaches window
initialization. Sodium's prior LWJGL version refusal is passed; actual LWJGL
still reports3.4.3+4. GLFW collects INVALID_ENUM for `0x00020010`, then the game
reports Driver does not support OpenGL3.3. This collected hint error is not proof
of missing actual GL3.3 support. The current native trace has no original game
context-create entry. Original Main returns and the existing session audit refuses
an incomplete/failed shutdown; no clean quit or rendered title/world is inferred.

## Exact default hint support

The pinned original LWJGL3.4.1 GLFW binding defines `GLFW_SOFT_FULLSCREEN` as
`0x00020010`. It comes from the
[LWJGL IME extension](https://github.com/LWJGL/lwjgl3/blob/8adda2367a10f0283ba7ac27a2222fcf7fc67212/doc/notes/3.3.4.md),
not the pinned unmodified GLFW3.4 core. The
[extension semantics](https://github.com/MojoLauncher/glfw/blob/7900e19fd2dbcad5abb4affc3b9d56c27e164c59/docs/window.md#window-hints)
call false the existing default and true nonexclusive soft fullscreen.

`0002-default-soft-fullscreen-hint.patch` recognizes this exact enum: false leaves
the current backend behavior unchanged; true reports `GLFW_FEATURE_UNAVAILABLE`.
Nonexclusive soft fullscreen is not implemented or advertised. Unknown enums still
report INVALID_ENUM; context validation/errors are retained. The current report
logs Controlify choosing exclusive fullscreen=true, but the actual hint value is
not directly recorded. If a mod/user requests true,199will refuse it explicitly.
No blanket error suppression, GL capability spoof or game/mod rewrite is used.

## Paired genuine Mesa no-error contexts

Original Sodium's WindowMixin may additionally request `GLFW_CONTEXT_NO_ERROR`
when its supported use-no-error-context option and workarounds allow it. This
request was rejected unconditionally by the old private GLFW adapter. This is a
source-discovered next boundary, not the observed198 INVALID_ENUM itself.

The private paired `ps5zink_config` appends `no_error`; GLFW forwards the request
and the real frontend passes Mesa's existing `ST_CONTEXT_FLAG_NO_ERROR` into
`st_api_create_context`. Mesa creates and reports the actual no-error context.
Default error-checking contexts remain unchanged. Debug+no-error is rejected by
both the adapter and direct frontend, and sharing/robustness/MSAA/sRGB and other
existing unsupported configurations remain refused. No fake GL/GLFW attributes,
no ignored context request and no change to normal GLenum error handling.

The header/frontend/GLFW must be rebuilt together. Actual output/header/source
hashes are checked; old packages/symbols are retained. This private flag is not a
new public loader or registry feature. The underlying Mesa/RADV pin, Java runtime,
original LWJGL binding/Version, account/dependency guards and game/mod JARs stay
unchanged.198's candidate-only upstream Sodium version-check option is retained;
no general ABI/Iris compatibility claim.197barrier drain, sampler-off, direct
Gallium context and synchronous flush policy remain. Quit/performance work is open.

## Verification and physical work

The real GLFW/SDL dummy-window ASan/UBSan test covers accepted false, explicit true
refusal, unrelated invalid enum, default-hint reset, existing input/window/monitor
lifecycle and missing-Zink OpenGL refusal. This is outside portable host lanes.
The real host Zink native fixture checks default versus no-error GL_CONTEXT_FLAGS,
draw/readback/thread-transfer/resize/destruction and direct debug+no-error refusal.
The original three publisher GlBackend/GlDevice host paths additionally check the
actual GLFW no-error window attribute and real GL flag in alternating contexts,
with default fullscreen hint, original capabilities and pixel rendering. These
are macOS lavapipe-backed tests, not physical PS5 RADV/Iris/pack execution.

Install complete PPSA99874 /01.000.199 and retry the same Fabric instance first.
Leave any failure card open, or reopen at the launcher after a hard crash without
starting another game. Actual Iris/shader enable/disable, world creation/timing,
save/reload, Quit Game/relaunch on Vanilla and Fabric, audio/haptics,26.2+Vulkan
and endurance remain pending. No release/prerelease/Store or new frozen pass.

## Exact built199 validation

Clean source `fdf42c8408f1c90bd1dc075212b62200f357db38` produced ZIP SHA-256
`4c61a71dc6bf77cd982dd96db1548f0f2081eca4d159427e6c4d6822885ca46c`. The [exact validation receipt](validation/client199-zink-hints-2026-11-02.json) preserves the matching package/symbol/build hashes and distinct test scopes. Local17 policy and11 native, clean source-only outside-root runs with an initially empty verified dependency cache, original Sodium checks, real GLFW/SDL controls, real host Zink default/no-error contexts, all three original publisher capability paths and independent exact199 package audit pass. Matching target component and GLFW are rebuilt together; Java JVM hash is unchanged from198.

[Hosted policy](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41501376662) passes17 checks on Ubuntu24.04/macOS15 at that source; actual jobs/logs were inspected. [Optional native CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41501390250) has Ubuntu success and macOS queued when inspected; completion remains pending. Early mixed host sanitizer runtimes were corrected by rebuilding both GLFW providers and tests with explicit matching LLVM22; final graphics tests pass. These host results do not establish exact199 PS5 launch/Iris/world/quit/performance acceptance. No release/Store upload.
