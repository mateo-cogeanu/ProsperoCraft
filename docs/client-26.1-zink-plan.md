# Minecraft 26.1.x through Zink — Phase A, 31 October 2026

**Research and build design, not implemented support.** 26.1.x remains blocked
by the launcher. No new app identity, console candidate, release or Store action
is created by this work. Current identity is 01.000.179; the next available local
candidate must be checked again before packaging. No physical Zink test or hosted
GPU test has run. The 16-check fast lane passes locally, in a clean source-only
checkout and in actual [Ubuntu/macOS CI jobs](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41231493001). [Evidence](validation/client261-zink-phase-a-2026-10-31.json)
separates local host results from pending implementation and console tests.

## Original publisher inventory

The live [Mojang manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json)
contains exactly these release IDs matching `26\.1(?:\.\d+)?`. Snapshots are
excluded. [Draft lock](../client/26.1.lock.json) records each metadata URL/SHA-1,
Java major, asset index, client URL/SHA-1/size and exact LWJGL module list in the
same `versions` layout as the existing 26.2 lock. Metadata and all original client
JARs/dependencies were independently downloaded and hash/size checked in an ignored
research cache. Asset index 30 was verified; its 457,876,437 bytes of asset objects
were not requested for this source inspection.

| Release | Java | Assets | Client bytes | Metadata SHA-1 |
| --- | --- | --- | --- | --- |
| 26.1 | 25 | 30 | 38,113,398 | c4bfc5cc47b28f5dedcb9fac76d6dc1fd1f899a9 |
| 26.1.1 | 25 | 30 | 38,113,231 | 93b7256ce0ec537e8b803991b2b8cac0daaa7660 |
| 26.1.2 | 25 | 30 | 38,113,927 | 8f9f3c548c892ce41b78561138aeba112cba3490 |

All use **GLFW**, with LWJGL **3.4.1** core, freetype, glfw, jemalloc, openal,
opengl, stb and tinyfd. Unlike 26.2 they have no shaderc/spvc/vma/vulkan modules
and no Vulkan backend class. No Java-major/window-layer contradiction was found.
The parent launcher still owns its 3.4.3 native modules; this list does not change
that policy. Official JARs and assets remain unmodified and outside Git/packages.

## Read-only GL inspection

`javap -c -p -constants` of original classes establishes:

- `GlBackend.setWindowHints`: OpenGL API (`0x30001`), **3.3**, core profile
  (`0x32001`), forward compatible true and **native context creation API**
  (`0x36001`). This is not an EGL request. PS5's native implementation may use
  EGL internally, without changing the game or pretending the Java hint was EGL.
  These hints do not request a debug context.
- `Window.createGlfwWindow`: one `glfwCreateWindow` call site with a null shared
  context. No additional/shared window creation site was found in the original
  client. `GlDevice` makes that context current before `GL.createCapabilities`.
  `RenderSystem` records/checks its render thread. No worker-owned GL context was
  found; that static observation is not proof of every asynchronous lifetime.
  Context TLS, unbind/rebind and cross-thread ownership still need real tests.
- Seven probed `GLCapabilities` flags: `GL_ARB_buffer_storage`,
  `GL_ARB_debug_output`, `GL_ARB_direct_state_access`,
  `GL_ARB_vertex_attrib_binding`, `GL_EXT_debug_label`,
  `GL_EXT_texture_filter_anisotropic`, `GL_KHR_debug`.
- `BufferStorage.create` selects immutable storage only with actual
  `ARB_buffer_storage` and the game's enable flag; otherwise it uses mutable
  storage. The immutable path really requests persistent mapping (`0x40`),
  uses mapped buffers and unmaps them during destruction. Do not fake this
  extension or implement only capability creation and call it game support.
- Debug callbacks prefer KHR_debug, then ARB_debug_output, and may be
  synchronous according to game debug options. All callback arguments/lifetimes
  must use the real parent JNI/libffi implementation.
- `GlDevice.setVsync` calls `glfwSwapInterval(1 or 0)`; `presentFrame` calls
  `glfwSwapBuffers`. PS5 remains FIFO with the existing real mode/refresh policy:
  no true uncapped VSync-off or 120 Hz success claim follows from accepting zero.
- GLFW API/version failures become `BackendCreationException`, including
  driver-not-supporting-GL, GL-3.3 and context/window-creation failures. Keep those
  failures real and propagated; no successful-context stub is acceptable.

The 28 inspected GL/window classes have identical SHA-256 values across all
three clients. The audit records their hashes and saves disassembly locally;
publisher class bytes/disassembly are not committed as project source.

## Parent/instance and JNI ABI

[Read-only audit](../tools/audit_client_261.py) verifies explicit parent inputs
against the 26.3 lock, the rebuilt GLFW callback binding against its source/output
audit, and the existing PS5 OpenGL object against its source/object audit. No
native classes are initialized. Per release:

- All **331** unique original game LWJGL field/method references resolve.
- Adding internal references of the actual adapted GLFW binding yields
  **820 method + 324 field** descriptors, all resolved with return/field types.
  Inherited protected declarations are searched, not only public methods.
- Original 3.4.1 OpenGL has **2,236** core native descriptors; all occur unchanged
  in the parent's **2,270**. Static/instance status is compared. WGL/GLX native
  methods are excluded consistently with the actual target builder.
- All 2,270 parent OpenGL native methods have their actual short/overloaded JNI
  export in the existing target object, built from 193 generated units.

Reuse that object and the 123 adapted GLFW Java binding rather than rebuilding
3.4.1 GL JNI. Actual routing will retain the parent 3.4.3 GL Java+JNI pair;
the original instance's 3.4.1 GL JAR remains verified/intact. The callback binding
must precede original GLFW for **each** 26.1 release, as it already does for
26.2. Linkage inspection does not establish native callbacks, GL execution,
arbitrary mod ABI compatibility or an original-Main bootstrap pass.

## Pinned Mesa and feature evidence

Use the existing PS5_Mesa commit
`1ba9874f478657ccf6da72ce55f0260164cc0bd0` (VERSION **26.2.0**) for **both**
RADV and Zink in one build. The source checkout is clean at this commit.
The upstream source archive is pinned in
[Zink sources](../client/ports/zink/sources.json); it is not a second adopted
Mesa version. Preserve the separate 029 Mesa 24.3.4 OSMesa provider. There is
no OSMesa frontend in this 26.2 tree; the removed frontend cannot serve as Zink.

The pin's `docs/drivers/zink.rst` describes Vulkan 1.0 plus extension fallbacks;
its machine-readable `VP_ZINK_requirements.json` **GL 3.3 baseline profile uses
Vulkan 1.2**. Use the profile and actual generated device checks, not the prose
alone. It includes robustBufferAccess; logicOp/fillModeNonSolid/alphaToOne/
shaderClipDistance; independentBlend; depthClamp/geometryShader/
shaderTessellationAndGeometryPointSize; dualSrcBlend; 16 descriptor samplers;
maintenance1/5, create_renderpass2, timeline_semaphore, custom_border_color,
line_rasterization, swapchain_mutable_format, incremental_present,
border_color_swizzle, descriptor_update_template, dynamic_rendering,
transform_feedback, conditional_rendering, depth_clip_enable and
vertex_attribute_divisor, with the profile's alternatives/features/formats.

`radv_physical_device.c` advertises the above core booleans, the extensions and
customBorderColorWithoutFormat. `border_color_swizzle` is conditional on GFX10+;
the PS5 winsys supplies a GFX10 family. Timeline support is conditional on
`has_timeline_syncobj`, which the PS5 winsys sets true. Device limits and format
features must still be queried from the actual console device. The old prose
lists all stippled-line variants, but RADV returns false for rectangular/smooth
stippling; the current baseline profile only requires rectangularLines and its
Bresenham/non-strict alternative. Do not enable an absent feature to satisfy a
prose checklist or claim full GL conformance from these source tables.

Static-loader replacement site: `zink_screen.c:zink_internal_create_screen`
calls `util_dl_open(VK_LIBNAME)` and looks up both GetInstanceProcAddr and
GetDeviceProcAddr. `zink_instance.py` generates `zink_create_instance`, using
that instance resolver. Replace the PS5 load path with the existing
`client/vulkan/loader.c:vkGetInstanceProcAddr` (the layerless resident wrapper,
not a second loader/ICD). Resolve device procedures through its **created
instance**, not an assumed global ICD export or a fake null-instance result.
Desktop builds keep their loader path. No arbitrary dlopen is added.

## Presentation choice: K with a private frontend

**Choose Option K.** Zink owns the game's instance/device/swapchain and presents
through existing RADV PS5 VideoOut WSI. Existing SDL surface creation in
`client/ports/sdl/SDL_ps5video.c:PS5_Vulkan_CreateSurface` enumerates real display
modes/planes and builds a VK_KHR_display surface without creating another
instance/device. Factor/reuse that selection with Zink's instance; do not
create a presenter device just to copy Zink output.

Required new code is substantial and **not yet implemented**:

1. Add VK_KHR_display to Zink's generated instance-extension list (currently
   absent) and a PS5 kopper platform branch. Audit all platform switches:
   surface creation, displaytarget hash identity, size/recreation, insertion,
   removal and presentation. Current kopper only handles XCB/Wayland/Win32.
2. Do not memcpy a `VkDisplaySurfaceCreateInfoKHR` into current
   `kopper_vk_surface_create_storage`: it only reserves three pointer words
   beyond sType/pNext, too small for that create info. Use an explicitly sized,
   owned PS5 loader payload or a window callback with checked lifetime.
3. Provide a small PS5 EGL platform or private Mesa frontend linked to the real
   GL state tracker/kopper. Upstream `default_library=static` alone does **not**
   make EGL static (`src/egl/meson.build` explicitly uses shared_library), nor
   remove the DRI driver loader. Both must be addressed; enabling Meson EGL
   flags alone is insufficient. Do not use the legacy OSMesa API as a facade.
4. Extend genuine GLFW's platform context hooks and the parent GL function
   provider; absence of the resident Zink group must still fail cleanly.
   Preserve 029 OSMesa bootstrap for current Vulkan-version native bootstrap.
5. Keep patches 0001–0010 and all graphics provider scoping/constructor ordering
   from build_wsi_diagnostics/build_client_gpu, with one copy of common Mesa
   utilities and RADV. Do not merge a second whole Mesa/RADV object behind the
   existing graphics-support group. Resident aliases do not merge implementations
   or infer ABI compatibility.

Launcher `Surface.close` waits idle and destroys its private device/instance;
`ui_main` closes the native presenter and joins handoff before Main. The game
must not start after an uncertain UI close. On verified clean original game exit,
the current design returns through **process LoadExec self-replacement**, not
another Main call or immediate in-process reopening over retained WSI. Preserve
that rule. There may be sequential launcher/game instances; no simultaneous
second RADV instance/VideoOut owner or full-frame CPU copy is part of this choice.
The existing launcher-only CPU readback remains outside the new game path.

Option P is not selected: surfaceless EGL does not automatically share Zink's
device/images with a new presenter. That route requires explicit synchronization,
image ownership and same-device interop and offers no established simpler path.

## TLS and memory plan

Mesa 26.2 moved glapi to `src/mesa/glapi`; the 24.3.4 assembly-selection patch
does not apply literally. `glapi_priv.h` already selects assembly only with
REALLY_INITIAL_EXEC, normally glibc; a FreeBSD/PS5 build should use generated C
entries. Verify the actual object has no fs/GOTTPOFF native-TLS dispatch.
`src/util/u_thread.h` still uses C++ `thread_local` outside Apple, so add an
explicit PS5 constant-initialized `__thread` branch and compile with emulated TLS.
Audit `_mesa_glapi_tls_Dispatch`, `_mesa_glapi_tls_Context` and C++ accessors.
Use the existing emutls adapter/lifecycle and opt-in direct fallback. No lazy
C++ TLS wrapper, global pthread allocator change or invented current context.

Budget **estimates**, not measurements: one unaligned RGBA8 1080p image is
7.91 MiB, 4K is 31.64 MiB. Existing WSI registers five buffers per size set:
39.55/158.20 MiB before alignment, not merely the requested swapchain count.
Depth plus intermediate GL images add further multiples; old size sets can be
retained. Provisionally allow 64–256 MiB additional CPU-side GL/Zink/compiler
state for bring-up, with no guaranteed ceiling; actual game resources and NIR/
SPIR-V/ACO compile peaks require measured high-water accounting. No heap/GC/
metaspace/quality policy change is authorized by that rough allowance.

Keep current 1536 MiB Java heap policy and C1/G1 configuration. Mesa malloc
must share the existing scoped graphics heap, not accidentally bind to JVM
scratch/global libc. Its direct heap/VRAM allocations are distinct from the
runtime's **256 MiB/2048-entry** native-direct ledger. Compiler TLS and owned
thread-stack fallback can still compete for that ledger (currently consumer
opts into **64 MiB/64 stacks**). JVM sync opt-in is 8192 mutexes/8192 relative/
2048 absolute conditions; graphics separately has 320 mutex/256 condition
reserves. Zink queues/driver workers can pressure native threads, keys and those
graphics pools. Do not equate the JVM reserve with Mesa capacity. Measure
allocation/worker/TLS peaks and joined cleanup before enlarging any bound.

## Reproduction and remaining gates

```sh
python3 tools/prepare_client_261.py --check-manifest
python3 tools/prepare_client_261.py --offline
# --assets explicitly downloads original asset objects when bootstrap needs them.
python3 tools/audit_client_261.py --java-home /path/to/jdk25 \
  --parent-dir /path/to/verified-parent-cache \
  --glfw-binding /path/to/lwjgl-glfw-3.4.1-ps5-callback343.jar \
  --opengl-object /path/to/lwjgl-opengl.o --nm /path/to/llvm-nm
python3 tools/run_host_tests.py --fetch-deps
python3 tools/check_documentation.py
git diff --check
```

The audit requires explicitly prepared publisher inputs, existing binding/object
audit JSON and parent cache; it is **not** in the fresh-source CI lane. The new
fast-lane input test uses only temporary transport fixtures and a real JDK class,
with corrupt/truncated/hash/path/ordered-rule/native-descriptor controls.

Next implementation: one combined static Zink/RADV build, PS5 kopper/frontend,
GLFW context hooks and dispatch; then actual GLFW+LWJGL Zink/lavapipe clear/draw/
guard/readback/thread/destroy and missing-Zink controls, original Main capability
bootstrap, launcher policy tests and exact package identity/symbol/notices audit.
Only then enable every locked release as Vanilla **Development test** with a
ZINK receipt renderer, no Vulkan backend argument, adapted GLFW binding and clear
Fabric refusal. Retain all existing Vulkan versions/snapshots and the Iris guard.

All console rows remain pending: (1) context/version/renderer/readback/destroy,
(2) animated FIFO presentation/refresh/clean return, (3) original 26.1 title,
(4) world play/audio, (5) save/reopen/quit/relaunch, (6) repeat game rows for both
patches after 26.1 passes. Also require a 26.3 world regression and separate
26.2/26.4-snapshot checks on the same candidate. Record exact build/run/package
SHA-256 and runtime/Mesa pins before attributing results. No row is ready for a
user console test yet. Release/Store remain held until exact-console confirmation
and explicit authorization. README support stays unchanged until acceptance.

Retained workarounds: 029 OSMesa bootstrap for Vulkan clients, adapted GLFW
callback binding, existing RADV/WSI/SDL allocation/sync/TLS reserves and runtime
fallbacks. Proposed PS5 static loader, private kopper/EGL platform and emulated
GL TLS will need separate tests once implemented. Fabric 26.1, Sodium-on-GL,
Iris, Distant Horizons, Zink for 26.2+, performance claims and older Java majors
remain separate milestones; none is enabled here.
