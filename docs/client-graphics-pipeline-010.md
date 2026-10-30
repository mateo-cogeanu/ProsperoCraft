# Client Graphics Pipeline 01.000.010

Client010 adds actual vertex/fragment graphics rendering after the frozen009
compute baseline. The original LWJGL Vulkan JAR creates an optimal-tiled256x256
RGBA8 image/view, render pass/framebuffer, two shader modules and a graphics
pipeline. vkCmdDraw emits a fullscreen triangle; the fragment shader produces
colored tiles, a black border and white diagonal. Three push-constant phases
change the palette, helping detect stale output.

Every image is copied from the GPU to a mapped readback buffer. Java checks all
65,536 pixels against the CPU reference and all256 guard bytes after the image.
Three normal image/pipeline/device sessions produce nine draws, with explicit
image/buffer barriers, flush/invalidate and five-second fence waits. An incomplete
submission retains resources until relaunch. This does not establish timeout
recovery or full module/global cleanup.

GLSL is compiled offline to SPIR-V with glslang and validated with spirv-val for
Vulkan1.1. The build records compiler version and source/module hashes. RADV
performs actual GPU compilation during vkCreateGraphicsPipelines on the PS5;
this does not exercise runtime shaderc or launch Minecraft.

## Visible result and its boundary

After Java verifies the final image, a small consumer JNI callback copies those
actual readback bytes into the existing CPU-menu preview. A colored256x256 tile
pattern with black border and white diagonal should appear at the lower right,
under **GPU readback / CPU display**, and remain after JVM shutdown. The preview
is not a CPU recreation of the reference pattern: it displays GPU-produced bytes.
The CPU reference is used only to validate those bytes.

This tests graphics shaders and a visible readback path. It does not introduce
SDL, a window backend, Java VideoOut ownership, direct GPU swapchain presentation,
input/audio integration or Minecraft startup. The existing CPU renderer remains
the display owner. Native003's separate GPU presentation snapshot stays preserved.
Frozen000–004 and008–009 are unchanged; server two-hour endurance remains deferred.

## Run on PS5

Install **PPSA99874 01.000.010** from `dist/client-render/PPSA99874.zip`, also
copied to the runtime workspace's current `dist/PPSA99874.zip`. The shared app
identity replaces the previous client/server app.

Run **all twelve rows in order**. Row10 repeats the compute shader test; row11
is graphics rendering/readback/preview; row12 destroys the JVM. Confirm both all
rows passing and the visible colored preview. Keep the app open for logs. After
a crash reopen without running rows. If a row stalls for about a minute, record
its displayed stage and reopen without running more rows so reports are retained.
First graphics compilation time on PS5 is not established.

## Build/check

```sh
python3 tools/package_client_vulkan.py --render --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25 --offline
python3 tools/test_client_vulkan_host.py --render --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25
python3 tools/test_client_vulkan_package.py --render --runtime-workspace /path/to/PS5_Homebrew
```

The real MoltenVK Mac GPU passes nine draws/all pixels+guards/three graphics
lifecycles with Java25 Xint/XcheckJNI/verification and actual LWJGL core UBSan.
Its captured readback is `build/render-host-010/readback.png`. Host success does
not establish PS5 graphics correctness or preview integration. Target package
checks, exact package hash and console status are recorded in
`client/render/status.json`. Original game/Vulkan JARs, the Java runtime
implementation and SDK are unchanged. No new passing milestone is created
before acceptance on the actual PS5 for this exact package.

## Console acceptance

The user reported ALL PASS on2026-10-24 after instructions to run all twelve rows and confirm the colored preview remains after JVM shutdown. Retrieved current-run reports confirm9 draws/all pixels+guards/3lifecycles/readback publish/DestroyJavaVM. Visual acceptance is the user response to that combined checklist, not an inference from logs alone. Exact tested bytes and scope are frozen in [Client_Graphics_Pipeline](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Graphics_Pipeline/README.md).
