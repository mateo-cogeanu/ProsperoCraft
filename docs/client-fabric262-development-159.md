# Fabric 26.2 development test, build 159

Build **01.000.159**, title **PPSA99874**, is a local development candidate. Fabric
26.2 remains unsupported in the public launcher. No GitHub release or Store
submission is authorized by this work. Exact console validation is pending.

## Evidence collected on 2026-10-30

Safari downloaded the read-only log index and 15 current/previous reports. Raw
reports, account information and paths remain in ignored local logs.

- Open app/session: `client-01.000.158-1793368545-389412510`, build 158,
  launcher/library running. Native stderr contains no game launch in this run.
  Abort endpoint explicitly says no abort captured. Resource snapshot reports
  50 open descriptors (30 regular, four sockets), not an EMFILE event.
- Previous native stderr: `client-01.000.158-1793367551-443154304`. The user
  identifies this as **Fabric 26.3**, not Fabric 26.2. It records first PCM
  submission, drain and retained silent AudioOut port. Matching startup history
  records clean game shutdown/process replacement. Neither audibility nor
  gameplay/persistence acceptance follows from these messages.
- That previous run catches HRTF `directory_iterator` **EPERM** on an existing
  local data directory, then creates its audio context and submits PCM. It is a
  concrete discovery failure, not the fatal cause of this run.
- Retained previous JVM fatal report has timestamp **2026-10-29 18:18:19**,
  elapsed 36.117181 seconds, native monitor mutex initialization ENOMEM. It is
  older than the current build-158 runs. Do not attribute it to build 158.
- The [149/150 record](client-fabric-context-locks-150.md) remains the exact
  historical evidence for debug/property locks, mixer progress and event-thread
  creation failure. The unexplained later 148 exit and underlying native
  allocation/synchronization limits remain unresolved. No new fatal address was
  resolved against unrelated symbols.

## Changes

OpenAL's out-of-line libc++ directory iterator bypasses the existing scoped
resident directory provider. Target helper imports confirm the old implementation
called libc++ `directory_iterator`; the provider's own pinned source explains
that the title's ordinary `opendir` is refused. The new private helper uses
explicit `opendir/readdir/closedir`, rebound to the existing consumer provider.
It keeps path discovery, regular-file checks, case-insensitive extensions,
symlink behavior, sorting and exception reporting. RAII closes the stream on
EOF, read failure or a subsequent allocation failure. It does not invent HRTF
entries, disable discovery, alter the SDK globally or change audio output policy.
PS5 discovery must still be verified, including any remaining ENOMEM.

`--fabric262-test` packages an exact development marker, accepted only with
`--startup --launcher-channel temp_gametest`. Missing/malformed markers, Demo,
Offline and a Java property alone do not enable it. Public `supported()` still
rejects Fabric 26.2. The separate launch permission retains normal entitlement,
artifact verification, dependency repair and genuine upstream Knot. Cards,
loader choice, detail title and channel explicitly identify development testing.
No loader, world, mod, account or settings migration is performed. The marker is
read once, not on each menu frame. Ordinary builds omit it.

A bounded launch identity checkpoint records the selected game version, loader,
window backend, development permission and verified Fabric Loader version before
entering Main. It contains no account, instance name or private path.

## Current integration map

| Area | Active implementation and evidence boundary |
| --- | --- |
| Fabric launch | `ProsperoLauncher` verifies publisher receipts and `ProsperoFabric` profile/library hashes; genuine Knot/Mixin owns game loading. Prior verified loader is retained during repair. `ProsperoModrinth` installs compatible genuine Controlify and required dependencies using version predicates and persisted URL/size/hash pins. Console-selected mod versions still need current-run correlation. No game/mod JAR rewrite. |
| Runtime | Existing compiler-TLS direct fallback, libjava string/ClassLoader/library-name scratch, verifier contiguous reserve, libnet scratch and extended 8192/8192/2048 synchronization reserve are explicitly enabled by bootstrap. Optional policies remain runtime-owned; no new runtime pin, heap/GC or budget changes in 159. Host checks do not establish native quota ownership. |
| Windows/graphics | 26.2 uses original LWJGL GLFW bindings and genuine GLFW core with SDL PS5 window/input/Vulkan backend. 26.3/snapshots retain SDL. Existing RADV, shader, native condition, allocation and presentation repairs remain. |
| Controlify | Resident `SDL3=ps5sdl`, genuine FFM/libffi, SDL joystick/sensor/effect entrypoints and consumer native input remain. Native gyro samples, compatible rumble and translated Controlify DualSense trigger packets are implemented. Host packet/ABI and platform lifecycle tests pass; physical 26.2 detection/input/rumble/triggers/gyro are pending. |
| Ownership/haptics | Existing gamepad/fallback arbitration, trigger reset and gyro/rumble shutdown remain. The separate four-channel SDL actuator-audio endpoint is preserved; ordinary rumble is not HD haptics. No competing always-on trigger effect is added. |
| Audio | Genuine pinned OpenAL Soft 1.25.2, process-lifetime pre-JVM two-mixer/two-event worker reserves, scoped exclusive locks, original event FIFO/kill/drain, completion before release, real stereo AudioOut and retained-port reload remain. Host PCM/callback/transition/failure tests pass; 149 and the previous 158 run submitted PCM, which is not audible/endurance acceptance. |
| World storage | Existing descriptor-first canonicalization, native file accounting, opt-in ZIP budget 64 and original runtime compression remain. ZIP budget is not a universal descriptor cap or unlinked-inode guarantee. Earlier EMFILE/Deflater initialization failures remain historical failures requiring exact 26.2 retest. |
| Public gate | Fabric 26.2 stays Coming soon in normal builds. The explicit local candidate enables only that combination as development testing. Vanilla 26.2, 26.3 and supported 26.4 snapshots retain their launch policy. |

## Reproduce and validate

From the active consumer checkout, use the existing configured runtime and JDK25:

```sh
python3 tools/build_current_client.py --runtime-workspace /absolute/runtime/Development --java-home /absolute/jdk25 --fabric262-test
python3 tools/test_client_startup_package.py --runtime-workspace /absolute/runtime/Development --fabric262-test
python3 tools/test_launcher_fabric262_pending.py
python3 tools/test_launcher_fabric262_development.py
python3 tools/test_openal_directory.py
python3 tools/test_openal_startup_boundaries.py
python3 tools/test_openal_ps5_audio.py
```

The measured target build used the already-prepared graphics inputs and
`package_client_vulkan.py --startup --launcher-channel temp_gametest
--fabric262-test --offline`. Full package checks validate original runtime/native
pins, resident symbols, CRC/signatures, source/object hashes, no bundled official
game JARs, frozen package hashes and the exact development marker. The exact
package, symbols, OpenAL corresponding sources/relink inputs and checksums are
retained locally under `dist/candidates/ProsperoCraft-Fabric262-01.000.159`.
Both ordinary and replacement-object relinks reproduce the candidate ELF.

[Build validation and checksums](validation/client159-fabric262-development.json).

## Console test sequence — all pending for exact 159

1. Install the local candidate through the existing workflow. Create a **new
   disposable 26.2 / Fabric instance**, leaving existing worlds untouched. Its
   card says **DEV TEST**, detail title **Development test**, channel **DEV FABRIC
   26.2**. Sign in normally and let compatible Controlify/dependencies install.
2. Reach the menu repeatedly. Confirm audible menu sounds and Controlify
   detection, navigation, held/released buttons. At the first failure, leave the
   log server open for retrieval; do not replace the app before correlating it.
3. Create a disposable world; record seed/world settings. Verify movement/look,
   new chunk access, blocks, entities/inventory, positional block/mob/footstep
   sounds and music when available. Record actual session duration/actions.
4. Test Controlify rumble, intended adaptive-trigger actions and gyro
   activation/calibration/motion. Report physical behavior separately from API
   success. Check fallback arbitration, disconnect/reconnect, trigger reset and
   any existing HD-haptics path separately.
5. Place an identifiable block marker and record coordinates. Save to title,
   reopen and verify it. Repeat world/menu/another-world transitions and resource
   reload; sound/input must continue. Record descriptor/resource observations.
6. Close and reopen the application; load that same disposable world and verify
   the marker again. Retest an existing compatible **disposable copy**. Never
   overwrite a real user world for this test.
7. Check Vanilla 26.2, Fabric/Vanilla 26.3 and the relevant supported 26.4 snapshots
   for regressions. Record actual versions, mod versions, time and results.

No menu-only, host build, native output success or single world entry establishes
completion. Public support stays held until the requested console lifecycle is
accepted. Release/Store publication still requires the user's explicit request.

## Exact159 console failure follow-up

The user reports a complete application crash during Fabric26.2 loading. Failed
run `client-01.000.159-1793369122-102204771` explicitly identifies Minecraft26.2,
Fabric Loader0.20.1, Controlify3.5.3+mc26.2, Fabric API0.161.0+26.2,
YACL3.9.7+26.2-fabric and SDL Java release-3.4.14-7. The next run is
`client-01.000.159-1793369171-829600882`, reopened at the library.

Cyberduck FTP retrieved ShadowMount's updated debug log. Its15:06:02 console-log
entry records PID121, **Render thread**, **0xa0020328 SYSTEM_XO_VIOLATION**.
The15:06:11 relaunch matches the next run. The system error-history record
00000127.json confirms PPSA99874 and **CE-108255-1**. These reports contain no
fault PC/backtrace. Raw logs/system-history private fields remain ignored/local.

The last Java/native observer sample is around17seconds after Main; GC/JIT
continue until39.9seconds after VM startup. The early progress update's17seconds
was the last stack sample, not an established crash time. No matching VM abort,
C++ throw or signal context was captured. Recoverable OSHI/storage/telemetry
warnings and the final shader checkpoint do not identify the fatal instruction.
Static disassembly found no direct RIP-relative data read into the candidate's
executable segment; indirect accesses and loaded-module code remain unproven.
No allocation-budget/heap/GC/JIT change is justified by these observations.

A separate title-scoped diagnostic payload is built with
`tools/build_client_crash_capture.py`, from pinned GPL
[PS5 DevTools](https://github.com/griches/PS5_DevTools/tree/e225e022565ae43afacfecdd272037f1752d2803).
It samples/attaches only PPSA99874, regardless of watch.txt. Deliberate fault,
HTTP deletion and all-title error-history routes are disabled. GET diagnostic
reports and POST quit/detach remain. Target compilation and the actual adapted
HTTP handler/title policy pass ASan/UBSan host controls. It is not loaded by the
build script and is not an application repair or console-validated capture.

The user must load `ps5devtools-prosperocraft.elf` through the existing ELF loader,
open unchanged159 at the library, and wait for confirmed attachment before
reproducing. Do not run competing debuggers. Stop through quit/detach rather than
killing an attached debugger. Registers/backtrace and an ELF code-hash match are
required before attributing a fatal native address. No160 game build or release
is created just to guess at the failure. Fabric26.2 remains development-only.
