# Canonical resident filenames — candidate186

Physical185 failed check4 with `UnsatisfiedLinkError: PS5 resident library
unavailable: ps5clientgpu`. The [exact-run receipt](validation/client185-console-resident-2026-11-01.json)
records package/run identity and the saved startup report digest. JVM entry and
native launcher display/device closure/UI-thread join precede this exception;
no GL workload, JVM destruction or fresh return is established.

## Cause and repair

`PS5Library` opens its supplied name directly. The runtime registry recognizes
canonical `lib<group>.so` basenames; it does not map a bare group name. Ordinary
LWJGL `Library.loadNative` performs platform mapping, but this direct constructor
bypasses it.185 passed `ps5clientgpu` directly. The opt-in OpenGL Zink resolver
also passed bare `ps5zink` through `APIUtil.apiCreateLibrary`.

186 uses `libps5clientgpu.so` in its own diagnostic harness and
`libps5zink.so` in the opt-in module overlay. Runtime loader, registry rules,
default OpenGL/029 behavior and ordinary GLFW/Vulkan configuration stay unchanged.
No arbitrary loader, bare-name aliases, platform spoofing or new native allocation
policy is added. The effective-classpath repair from185 remains.

The previous host simulation provided permissive bare-name aliases and therefore
missed the target naming restriction. A new host-only boundary compiles the actual
`lwjgl_resident.c` PS5 JNI loader branch, registers its methods, accepts only four
explicit canonical resident basenames, and forwards them to genuine host native
libraries. It models registry naming rather than running the PS5 registry/driver.
The actual185 packaged fixture/classpath reproduces the exact reported exception;
the actual186 packaged fixture/classpath passes real Java GL rendering/readback,
cleanup and modeled rejection/resume controls. No extra fixture class shadows the
packaged harness. The host launcher barrier remains modeled, with no VideoOut,
native launcher UI or LoadExec claim.

Run `test_zink_handoff_host.py` with explicit compiler, graphics configuration,
host Vulkan library, `--app`, `--classpath-audit`, clean `--output-dir`,
`--fixture client/zink_handoff_resident/ClientStartup25.java` and
`--strict-resident`. For the185 package negative control, use its fixture/package
and add `--expect-resident-failure`. These manual graphics tests require explicitly
provisioned inputs; they are outside portable CI lanes.

## Exact186 console test

Install the complete **PPSA99874 /01.000.186** candidate ZIP. Wait for the real
native launcher **Run Zink handoff** card and press **X once**. Check for six
seconds of RGB/moving-white-bar rendering, followed by cleanup, diagnostic-only
DestroyJavaVM and the existing LoadExec barrier returning to a fresh page showing
**Stage2b PASS**. Confirm visible motion and the returned page separately.
If it fails/crashes, reopen **without pressing X** and leave the app open for the
read-only report service. No preset address/client filter is packaged.

`package_zink_jvm_resident.py` uses the explicit accepted179 ZIP/relink/build
inputs and exact183 component, runtime, JDK25, LLVM and LLD from the185 builder.
It writes `dist/candidates/zink-jvm-186` and refuses to overwrite an existing ZIP.
`test_client186_package.py` checks exact identity/hashes/classpath/constants,
resident groups, staged constructors, single combined graphics copy, signatures,
unchanged original dependency JARs and retained029 implementation.

Local16fast and7native checks and source-only outside-root16fast checks with an
empty dependency cache pass, as do genuine lavapipe/Zink host26.1,
26.1.1 and26.1.2 workloads and the default029 softpipe/PS5-dispatch regression
with the original unpatched GL failure control. Target compile/link/constructor/
resident/converter checks pass. Exact package metadata and hosted results are
recorded separately after packaging.

This remains a diagnostic harness, not ordinary account/instance/download or
original Minecraft Main. Physical186 handoff, original26.1/26.1.1/26.1.2 title,
world/save/audio/reopen/exit/relaunch, measured refresh/FPS, graphics regressions
and endurance remain pending. Game/root identity stays179, production26.1 stays
blocked. Preserve tested183 and every earlier candidate/symbol/validation,
original game/mod JARs, compatibility implementations and archived milestones.
No release, prerelease, Store change or new passing milestone is authorized.

The [exact186 build/validation record](validation/client186-zink-resident-2026-11-01.json)
records clean source `0848900`, package/symbol/component/classpath hashes and
verification limits. ZIP SHA-256:
`c2137f32840e8b22b971418f32fbc63c0e5838827872f717456f11a80b43cd2e`.
[Hosted source checks](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41294524073)
pass16fast checks on Ubuntu and macOS; completed job steps/logs were inspected.
The final packaged fixture and classpath also pass the strict host GL test.
Physical console acceptance remains pending.

## Console report — 1 November 2026

The user reports **exact186 Stage2b PASS**. Preserve the tested ZIP and symbols
unchanged. The [separate console receipt](validation/client186-console-stage2b-2026-11-01.json)
records the package/runtime/Mesa pins, independently observed current186 session
and limits. This supersedes the pending186 diagnostic status above; the original
build/host record remains unchanged. The session run is
`client-01.000.186-1793526812-811812711`; it is the open result-process session,
not independently established as the preceding graphics-run ID. Complete success
checkpoint logs and explicit visible-motion/refresh measurements were not captured.

Next is the plan's original Vanilla26.1 Main-to-title checkpoint through the normal
launcher/sign-in flow, in a new candidate. Do not reuse186's identity or infer
world/save/audio/relaunch or26.1.1/26.1.2/regression acceptance. Keep the existing
OSMesa/callback/runtime/native ownership workarounds, production gate and release/
Store hold. No full-game ALL PASS or archive freeze is established.
