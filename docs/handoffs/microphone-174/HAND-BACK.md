# Microphone repair handback to Codex — local175

Claude specialist result, 31 October 2026. **Local only: by the user's explicit
instruction nothing was pushed to GitHub** (no sync, no push, no release,
prerelease or Store action). The consumer checkout is 1–2 local commits ahead of
`origin/main`. Codex decides whether and when to publish.

## Result and scope

- **Before/after:** no physical174 or175 result exists. Behavior change is host-verified only.
- **Root cause of the173 "SVC doesn't see a mic": not demonstrated.** Sanitized evidence:
  - Original SVC2.6.27 (`ALMicrophone`, inspected by bytecode) opens with the configured
    name `""`, then falls back to `null`; it does **not** enumerate first. The retained173
    native log shows exactly two "Opening default capture device" attempts, mono Float32,
    48000Hz, 960/960, each failing inside our `Ps5Capture::open` (the `capture.open()` branch,
    since the "disabled or unavailable" message did not appear). Format, enable flag and
    name matching are therefore excluded.
  - Most likely (medium–low confidence): a repeated `sceAudioInInit` after AudioIn was already
    initialized earlier in the same process (by a launcher Test input or an SVC
    device-list enumeration, which in173 had no logging). 174 already fixed that repeated
    init. Contrary/unknown: no173 native code; an external component initializing AudioIn
    first, or a port/route refusal, would look the same. 174/175 log `PS5 AudioIn stage=… result=0x…`,
    which will settle it.
- **Scope:** stayed within microphone capture. Runtime0135, socket/title-screen, output
  playback, UI, controller and memory policy were not changed.

## Concrete defects repaired (review targets from 01-IMPLEMENTATION)

1. **Unchecked `pthread_join` (target 2).** New `ps5audio::WorkerOwnership` in `ps5_capture.hpp`.
   A failed join marks the worker uncertain, logs `stage=worker-join result=0x…`, never re-joins,
   refuses restart, and the destructor leaves the global lease pinned without closing the port.
   Previously the destructor would close the port while a producer might still be inside `pump()`.
   Code risk, not a demonstrated crash cause.
2. **Enable OFF during active capture (target 4).** The capture worker checks the flag before
   each read; when OFF it clears queued samples, stops reading, logs
   `stage=disabled-during-capture` and disconnects the OpenAL capture device. No mute/gain/routing call.
3. **Enumeration while capture is live.** Previously SVC's device list (e.g. opening its settings
   mid-game) returned empty because the lease was held. Now a healthy live owner is listed without
   touching the port; a pinned/unhealthy lease still lists nothing and logs `stage=lease-unavailable`.
4. **Error fidelity (target 5).** Short positive reads now report `stage=input-short` with the actual
   count (previously `-1`). Invalid initial user with rc0 is `stage=initial-user-invalid` (no user id logged).
   Worker creation failure logs its pthread return code. Reroute-open close-error replacement is unchanged.

Target 3 (blocking native read / stop waits for the read) was reviewed and left unchanged. No
close-from-another-thread race was added.

## Exact source and integration

- Consumer `main`, base `e78d2de` (handoff docs). Local commit
  `d0d76570a70c035234b1331be712bf3d848ba117` plus this HAND-BACK commit. **Not pushed.**
- Changed: `client/ports/openal/ps5_capture.hpp`, `client/ports/openal/ps5_backend.cpp`,
  `client/startup/param.json` (01.000.174 → 01.000.175 only), `tools/test_microphone_capture.py`,
  `tools/test_openal_ps5_audio.py`, `tools/test_client_startup_package.py`, `CHANGELOG.md`.
- Runtime/output dependency needed from Codex: **none**.
- No unrelated user edits were present or touched.

## Verification (host Mac, JDK25.0.4)

| Check | Command/build | Result | Limitation |
| --- | --- | --- | --- |
| Focused capture core | `python3 tools/test_microphone_capture.py` | PASS (ASan/UBSan): short-read, invalid user, active state, join-failure pinning, plus all previous cases | Host OS doubles |
| Genuine OpenAL backend | `python3 tools/test_openal_ps5_audio.py` | PASS all 19 modes. New mode101 uses SVC order: launcher probe, then `""`/null opens with no enumeration ×3, live enumeration, stop drains to 0, enable OFF disconnects/drops samples, reusable lease, single init | Host AudioIn source, no speech |
| Negative controls | Reverted live-enumeration and enable-OFF changes individually | mode101 failed each time; source restored | — |
| Host lanes | `run_host_tests.py` / `--lane native` | 15/15 and 7/7 PASS | — |
| Package audit | `test_client_startup_package.py` | PASS01.000.175; also asserts new capture diagnostics are in the linked ELF | No device |
| Relink | normal + replacement-OpenAL `relink.py` | Both reproduce the exact ELF hash | — |
| Docs | `check_documentation.py`, `git diff --check` | PASS | — |
| Hosted CI | — | Not run (nothing pushed) | — |
| Physical launcher input / SVC / mute & route / stop-reopen | — | **Not performed** | No console access this session; console IP was not available |

## Local artifact

- Version/title: 01.000.175, PPSA99874 (local candidate; supersedes nothing; 174 artifacts untouched).
- `dist/local-tests/client175/PPSA99874.zip`: SHA-256 `8965235df19666ecadea1874c8be51742549ff65536f1aa5fdaf6cba75694f62`
- `dist/local-tests/client175/bootstrap-01.000.175-symbols.elf`: `bb6cb94ea9cbb91c95d4983c115a22302164cd6fc1b68794bb4532508b6a11c8`
- `dist/local-tests/client175/client175-openal-source-relink.zip`: `92ab53e8deffd4e79752b11e8168073d1af19ed2123bbd891cab2842f3dc435f`
- The expanded `relink-kit/` (368MiB) is retained. It may be discarded after a ZIP/file-hash match per the storage guide.
- The build also refreshed `dist/client-startup*/PPSA99874.zip` and `build/` with 175 outputs.
- No physical test has used this package. No release, prerelease or Store action was taken.

## Remaining work for Codex

- **Smallest next physical test (175):** enable Voice capture, keep SVC's Java-microphone option OFF, join
  a world, then retrieve `/native-stderr.log` (and previous) and grep `PS5 AudioIn`. A failing
  `stage=init result=0x…` on the first open means AudioIn is already initialized externally or refuses
  init. That needs evidence before accepting any specific code. `stage=open` points at port/route.
  No line plus no ALSOFT open failure means open succeeded: then check SVC speech, mute and route.
- Then: launcher Test input while quiet vs speaking vs hardware-muted (report silent-blocks); toggle
  Voice capture OFF in-game if reachable (expect `disabled-during-capture`); world leave/rejoin ×3.
- Known unverified: real read pacing/blocking on stop; physical mute/privacy behavior; DualSense route
  identity; SVC codec (native Opus/RNNoise/Speex validation fails on173; Java Concentus path untested on
  console); UDP transport/two-way voice; whether SVC tolerates the enable-OFF disconnect gracefully.
- Publication of these commits is Codex's decision; the user asked Claude to keep this work local.
