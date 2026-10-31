# Zink181 first-frame failure and diagnostic182

The user reports181 crashed and was reopened without X. Safari read-only retrieval
identifies the open app as **01.000.181**, recorded run
`zink-01.000.181-1793477720-578006752`. Direct tool HTTP reported no route to host;
Safari reached the same console and saved the first native trace and startup tail
locally. The startup tail's final181 checkpoint agrees with the native trace/run.
The session file stopped at an earlier WSI image-import checkpoint; it does not
supersede the later startup entry. Raw reports remain local.

The console completed genuine SDL display inventory (1920x1080,119.880Hz selected),
Vulkan display-plane surface creation, swapchain framebuffer registration, and
actual GL4.6 core/Mesa26.2 Zink/RADV renderer reporting for cycle0. There is no
completed animation/readback/swap or teardown checkpoint. Neither selected refresh
nor registered buffers establishes visible presentation. `exceptions.log` and
`hs-error.log` are unavailable (errno2); this native-only process contains no JVM.
Old startup-history SHADERC faults belong to earlier runs, not181. No181 fault PC
was recorded. **The crashing operation and root cause remain unproven.**

The preserved history also independently confirms180 run
`zink-01.000.180-1793476965-942502413`: three actual GL4.6/Zink contexts, all192RGBA
pixels/384guard bytes, final destruction and Stage1 PASS. The original user-report
receipt and build record remain unchanged; this is supplemental retrieved evidence.
No game/full-milestone ALL PASS or release authorization follows.

## New local182 diagnostic

PPSA99874 /01.000.182 keeps the same native GL/Zink/RADV object and genuine
GLFW/SDL providers as181. It adds only bounded first-frame operation checkpoints
and the existing `client/ports/shaderc/fault.c` native recorder. The historical
**SHADERC FAULT** label is retained by that reusable consumer recorder; a record
with that label in182 is not evidence that shaderc executed. No shaderc or JVM is
linked. Its existing signal handling captures bounded raw context words and forwards
to the previous handler; it neither recovers nor changes the fault context. Bootstrap
requires four legacy handlers, all seven owned signal handlers and no query errors.
A native function anchor supports symbol/load-adjustment analysis against exact symbols.
No arbitrary context-layout or PC assumption is introduced.

First-frame checkpoints bracket monotonic time, GLFW event pumping, actual drawable
size, viewport, base clear, scissor clear, GL error, guarded readback, finish and
swap. Only the first frame of each of three cycles is detailed. This may affect
timing; no fix or unchanged failure timing is claimed.182 is a diagnostic candidate,
not a repaired-driver or console-pass claim.

Install the complete182 PPSA99874 folder, open and press **X once**. If it crashes,
reopen **without X** and leave it open for retrieval. If it completes, confirm both
three visible RGB/moving-bar cycles and the **Zink182 stage2a checks PASS** notification.
Initial/final blank screens are expected. Reports stay at the existing read-only
port8765 service, with exact182 and a unique run id. No preset address/client filter.

The [181 guide](client-26.1-zink-present-181.md) describes the rendering and repeated
native teardown test. Actual Java launcher handoff, JVM coexistence, original26.1.x
Main/title/world/audio/save/reopen/exit/relaunch, Vulkan-version regressions and
endurance remain pending. Preserve029 OSMesa, adapted callbacks, all allocator/TLS/
sync/stack workarounds, official JARs and frozen history. Current root/game launcher
stays179. No release/prerelease/Store action.

Local182 build/test tools are `package_zink_present_trace.py`,
`test_zink_present_trace_host.py` and `test_client182_package.py`; their explicit
arguments follow the181 tools. Outputs use `dist/candidates/zink-present-182`, never
overwriting181 or180. Host tests execute exact182 rendering on actual GLFW/Zink
lavapipe with SDL dummy offscreen, ASan/UBSan on frontend/GLFW/driver; no positive
VideoOut execution is implied. Target compile/link/converter and one-copy checks
pass. The [182 validation record](validation/client182-zink-diagnostics-2026-10-31.json)
records clean build sourcef34251a and exact checksums. ZIP SHA-256:
`f00b87e1bd1676238e1f1fbfdb427c04955ff7b7548fd87e0d88e94929af2635`.
The [181 crash receipt](validation/client181-console-crash-2026-10-31.json) keeps
the observed failure separate from182 pending console work.

Local16fast and7native checks pass, alongside actual host rendering and native
signal-recorder delegation/restoration tests. [Ubuntu/macOS CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41237946079)
passes16fast checks for sourcef34251a; it executes no graphics or PS5 code.
