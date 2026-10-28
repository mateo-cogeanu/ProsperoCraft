# Build117 performance investigation, 28 October 2026

The user confirms the Store117 download works and reports a second user also succeeded. This records functional acceptance, not a new Java milestone or measured shader performance. The README now marks Fabric/Modrinth content, SDL3 Controlify integration and controller remapping complete. Shader performance remains open. User requires shadows at100%; do not lower quality to mask performance costs.

This pass changes documentation only. No tuning, replacement game/mod classes, shader edits or new app package. Release117 bytes are preserved.

## Evidence from the console

Safari retrieved current build/session and GC/JIT/native/game reports. The open app identifies117 and run client-01.000.117-1793191418-735785727. Raw files remain in ignored local build storage. GC/JIT files have no separate run header, so their uptime is not a frame-by-frame correlation or proof of a particular scene. The game console is in exceptions.log; server.log is only a header. Native resource samples are also header-only because the startup observer is disabled in performance runs. The current mod list includes Fabric, Controlify, Fabric API, Mod Menu and Sodium, with no Vitrail. It is useful baseline evidence, not a shader-enabled117 benchmark.

| Observation | Implication and limit |
| --- | --- |
| One metadata-threshold full GC at364.538seconds,167.130ms | A definite JVM stop, large enough for an obvious hitch. Loading/transition context remains uncorrelated; do not call this a recurring steady shader stall.128MiB initial metadata threshold has not eliminated all such events. |
| Whole report:2489GC pauses, median3.964ms, p955.805ms, max167.130ms | Collection can materially consume the8.33ms budget at120FPS.19GC pauses exceed8.333ms. A4ms target is a soft goal, not a cap. |
| Whole report:2490safepoints, p957.203ms,47exceed8.333ms | Total stop time includes reaching/leaving the safepoint and can exceed the GC body. No recorded frame timestamps establish which visible hitches coincide. |
| Last300seconds:139GC pauses, median3.995ms, max7.445ms; max total safepoint8.004ms | Smaller pauses persist during later play. Staying below one whole frame does not mean no missed deadline when the rest of the frame already consumes its budget. |
| 1625GC pause records between300–600seconds;144between1600–1915seconds | Heavy transient allocation/loading phase differs sharply from later play. Do not average loading and steady play into a single performance claim. |
| Late JIT work continues:156compilation records after1600seconds | First encounters still introduce compiled code. C1-only compilation, one compiler thread and threshold scaling4are deliberate existing compatibility policies; their CPU/warmup cost needs measurement before changing them. No code-cache-full/compiler-disabled message found in this capture. |
| Rumble logging prints every native submission and flushes startup.log through client_sdl_diagnostic/log_stage | Concrete avoidable diagnostic I/O on the output path. The512KiB startup tail contains702rumble lines and4886shaderc/glslang checkpoint lines. This log includes historical runs, so counts are not current-run rates. Disk write latency and a causal frame stall are not measured. |

## Shader-specific leads

Earlier105/106 console observations showed BSL3072×3072 shadow targets redrawn each frame, with user feedback around60FPS moving/80still. That makes shadow rendering, terrain submission and the additional full-screen shader passes plausible costs. Resolution alone does not prove GPU saturation, and old logs cannot diagnose117's current pack/preset. Keep100% shadow scale. A comparable same-world/same-camera run with shadows100% is needed before selecting an optimization.

The locally inspected Vitrail source snapshot7a3cdcbe1dfd7e04fb2b3021ee8352d341e7647e has optional GPU pass timing in common/src/main/java/dev/vitrail/render/timing/PassTimings.java, controlled by vitrail.passTimings seconds. It reads timestamp results after several frames without waiting and reports pass/span/frame intervals. This offers a way to separate shader-pass GPU time from CPU/presentation gaps, The locally pinned0.13.0-beta+mc26.3 JAR also contains the PassTimings class; the console-installed version and PS5 timestamp support still need verification. Do not turn a timing-property suggestion into a compatibility claim. Reference: [Vitrail source](https://github.com/avpbynf/Vitrail-Shaders/tree/7a3cdcbe1dfd7e04fb2b3021ee8352d341e7647e).

The same snapshot implements optional shadow-terrain reuse, but changes visual freshness and excludes voxelising packs. Do not enable it as a supposedly free optimization. Shader/glslang diagnostic calls also synchronously flush startup output; investigate compiler/pipeline cold paths separately from steady GPU rendering. Shader compilation completion does not itself measure every driver's pipeline build or prove an ongoing compile stall.

## Investigation order before performance changes

1. Measure same-world stationary and walking frame times with shaders off, then the selected shader/preset at100% shadows. Record render/simulation distances, pack/mod versions and output refresh. Separate first traversal from revisiting loaded terrain.
2. Align monotonic frame-time samples with GC/safepoints, JIT and bounded I/O timing. Establish whether the frequent small baseline hitches coincide with JVM stops, chunk work, pipeline work or rumble diagnostics.
3. Validate GPU pass timing on PS5 and use nonblocking results to rank shadow, terrain and composite passes. CPU frame minus GPU time is only a lead until queue overlap/presentation is accounted for.
4. First candidate for a narrowly scoped fix is repeated successful-rumble diagnostic writes; preserve first-use/errors/reset diagnostics and compare the same replay before attributing a benefit. No output behavior needs to be removed.
5. Profile metadata growth/allocation hot spots and ZIP reopen/lock costs before changing JVM flags. The64-handle ZIP pool fixed console world operations and must stay enabled; no observed current EMFILE evidence warrants undoing it. Its reopens/global synchronization could cost time with many archives, but no contention measurements exist.

No claim is made that any one lead explains all stutters. New performance changes should be tested in development while the accepted117release stays intact. Microphone work remains deferred. See [bounded measurements and local-file hashes](validation/client117-performance-investigation-2026-10-28.json).
