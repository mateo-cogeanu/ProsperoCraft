# Zink presentation preparation — candidate183

182 run `zink-01.000.182-1793478154-873101690` is preserved in retrieved
Safari session/native/startup reports. Direct tool HTTP still reports no route to
host. First native/startup downloads stay local. The signal recorder installed
four legacy handlers and owned all seven, with no query errors. The final
main-thread checkpoint is first `glfwPollEvents` enter; a signal can be received
on another thread, so this does not establish an input-driver fault.

The native trace captures **SIGSEGV11/code1, fault address0x48**. The recorded
function anchor is0x4020d0; exact182 symbols place `zink_present_run` at0x20d0,
giving load adjustment0x400000. Context word28 is0x8cfd69; adjusted0x4cfd69 maps
into `vk_device_copy_semaphore_payloads`, inlined `vk_semaphore_get_active_sync`.
The exact instruction reads0x48 from the semaphore pointer; this is consistent
with the captured0x48 fault and a null wait semaphore. This analysis cross-checks
the raw context candidate against instructions and the independent anchor; it
does not assume every context word's register layout. GLFW's unchanged context
attribute initialization already clears/swaps once before returning the window,
and kopper can queue presentation asynchronously. The last main-thread event
checkpoint therefore does not exclude a presentation-worker failure.

The [182 fault receipt](validation/client182-console-fault-2026-10-31.json)
records exact package/symbol/report hashes and interpretation limits.

## Concrete frontend omission and fix

The private frontend calls `st_context_flush(...ST_FLUSH_END_OF_FRAME...)` and
then `screen->flush_frontbuffer`, but omitted the callback used by the pinned
Mesa DRI/kopper frontend (`notify_before_flush_cb` in `dri_drawable.c`). That
callback calls `pipe->flush_resource` on the presentation texture **after pending
GL vertices are emitted and before the batch flush**. Zink uses it to establish
`ctx->swapchain`/`needs_present`, perform the PRESENT layout transition and create
the signal semaphore at batch end. Without it, the later kopper queue can receive
a null presentation semaphore; release-build assertions do not guard that path.
This is a concrete contract violation consistent with the captured fault.

183 adds the same callback ordering for a real window texture. Offscreen behavior
is unchanged. It does not suppress null-semaphore errors in Vulkan, fake completion,
remove event polling, change threading policy or add a CPU presentation copy.
Actual PS5 repair is still pending; no console pass follows from this diagnosis.

`test_zink_present_order.py` compiles the **actual port callback/present functions**
against a modeled pipe boundary. It checks GL emission -> resource preparation ->
batch end -> presentation, error propagation, missing textures, offscreen and
recursion behavior under ASan/UBSan. Replacing the callback with182's omission
fails the window case. This is a contract regression, not a real swapchain test.
Separate host tests execute real rebuilt Zink/lavapipe/GLFW rendering and183
animation/lifecycle; SDL dummy is offscreen and cannot establish positive VideoOut.

## Physical test

Install complete PPSA99874 /**01.000.183**, open and press **X once**. Expect
three RGB/moving-white-bar cycles, then **Zink183 stage2a checks PASS**; confirm
visible motion separately. If it crashes, reopen **without X** and keep it open
for current-run reports. Initial/final blank screens are expected.183 retains182's
bounded first-frame checkpoints and existing forwarding native fault recorder.
Its historical SHADERC FAULT label does not mean shaderc is linked or executed.

This remains a standalone native presentation/teardown probe. Actual Java launcher
handoff, JVM integration, original26.1/26.1.1/26.1.2 title/world/audio/save/reopen/
exit/relaunch, existing Vulkan-version regressions and endurance remain pending.
Current game/root identity stays179 and26.1 production launcher stays blocked.
Preserve exact180/181/182ZIPs/symbols,029 OSMesa, adapted callbacks, runtime
allocator/TLS/sync/stack fallbacks, original JARs and frozen history. No release,
prerelease or Store action. Raw reports stay local.

Build `tools/package_zink_present_fix.py`, host-check with
`test_zink_present_fix_host.py`, and independently audit with
`test_client183_package.py`; explicit arguments follow182. Local output is
`dist/candidates/zink-present-183`; existing candidate ZIPs are never overwritten.
Exact source/checksum/host/console receipts follow packaging.
