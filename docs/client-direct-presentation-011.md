# Client Direct Presentation 01.000.011

Client011 tests the original LWJGL VK_KHR_display/VK_KHR_surface/VK_KHR_swapchain
path to actual PS5 VideoOut. It discovers a display/mode/compatible plane and
graphics/present queue, creates a bounded BGRA8 UNORM FIFO swapchain, renders
with real vertex/fragment shaders into acquired swapchain images and calls
vkQueuePresentKHR. No CPU renderer opens VideoOut.

The old CPU menu permanently owns its VideoOut handle. This probe avoids that
ownership conflict by starting from notifications and one explicit X press,
then executing twelve checks automatically. Checks1–10 cover the earlier
runtime/core/Vulkan/compute fixtures. Check11 exercises direct graphics/display;
check12 destroys the JVM. The separate010 offscreen/CPU-preview row is not run
in this app; its exact frozen milestone remains preserved.

## Run on PS5

Install **PPSA99874 01.000.011** from `dist/client-present/PPSA99874.zip`, also
copied to the runtime workspace's current `dist/PPSA99874.zip`. It replaces the
shared-ID client/server app.

1. Open the app and wait for **Client011 ready**. The initial screen may be blank; there is no CPU test menu.
2. Release X, then press X once to start all twelve automatic checks.
3. Near the end, expect full-screen colored tiles, a white diagonal and black border. The palette changes through three phases.
4. Wait for the **Client011 automatic checks PASS** notification. Confirm the pattern stays visible after that notification and JVM shutdown.
5. Keep the app open for reports. After a crash reopen without pressing X so the failed reports remain available. A failure notification identifies the check; leave it open for extraction.

If no completion notification arrives after about a minute, note what was visible
and reopen without pressing X to preserve the reports. First PS5 WSI setup and
graphics compilation times are not established. This is not the deferred two-hour
server test.

## GPU checks and lifecycle boundary

The target renders90 fullscreen triangles, three30-frame palette phases. Each
frame acquires a swapchain image, renders through a framebuffer/render pass,
copies36 grid samples into a mapped readback buffer and verifies their expected
BGRA values plus256 guard bytes before FIFO presentation. Only those samples,
not every full-resolution pixel, are verified in this probe. Frozen010 separately
checked every256x256 offscreen pixel.

One render-finished semaphore is retained per swapchain image; image reacquisition
provides its reuse boundary. The acquire semaphore is reused only after the
submission fence confirms its prior wait completed. Acquire/fence waits use a
five-second timeout. Pixel coordinates are scaled in the fragment shader using
phase/width/height push constants. Plane/mode inventories, extent and usage are
bounded/checked; selected output is limited to3840x2160.

The native instance/device/surface/swapchain/images/views/framebuffers/pipeline/
command/readback/sync resources are intentionally retained on success or failure
until app close. That preserves the last presented frame after DestroyJavaVM.
Teardown, CPU-menu handoff/reacquisition, resizing, timeout recovery and full
module/global destruction remain unvalidated. A failed run requires relaunch.

This is direct Java Vulkan presentation, not an SDL window backend or Minecraft
startup. Original game/Vulkan JARs and runtime implementation/SDK are unchanged.
Frozen000–004 and008–010 remain preserved; server endurance stays deferred.

## Build and host limits

```sh
python3 tools/package_client_vulkan.py --present --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25 --offline
python3 tools/test_client_vulkan_host.py --present --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25
python3 tools/test_client_vulkan_package.py --present --runtime-workspace /path/to/PS5_Homebrew
```

The host check compiles the actual target Java fixture, but executes a clearly
separate offscreen companion on MoltenVK because the Mac does not expose PS5
VK_KHR_display. That companion tests the presentation shaders,12-byte push
constants, BGRA output, full pixel/guard checks and three graphics lifecycles
under Java25 Xint/XcheckJNI/verification and real LWJGL core UBSan. It does not
exercise the target display discovery, surface, swapchain, acquire/present or
retained-display lifecycle. All twelve console checks and human full-screen
confirmation remain pending. Exact package/hash/checks are recorded in
`client/present/status.json`; no new passing milestone is created yet.

## Console acceptance

On2026-10-24 the user explicitly reports “PASS by notification and pass by my eyes.” Retrieved session confirms ALL12 PASS; every present frame0–89/sample+guard record is verified, followed by DestroyJavaVM complete. The native display remains retained by design. Exact tested source/package and evidence are frozen in [Client_Direct_Presentation](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Direct_Presentation/README.md).
