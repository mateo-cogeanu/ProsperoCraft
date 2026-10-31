# Local177: prepare the AudioIn service before JVM/game pressure

The user reports176 leaving and rejoining works, while SVC still reports the
usual microphone-unavailable error. Safari retrieved the actual current176
session/native stderr and matching Java console. Both native capture opens are
48000Hz mono Float32 and fail at stage=init result=0x80260108. Neither reaches
sceAudioInOpen or creation of a capture worker. Java then falls back to the
unavailable Java Sound microphone provider. The176 first-init result rules out
claiming that remembered repeated initialization alone repaired the current run.
Raw reports/account/instance data stay local.

The open-source [shadPS4 error namespace](https://github.com/shadps4-emu/shadPS4/blob/860d73b7e99559106a3ffa3d3d69f0f9237e115e/src/core/libraries/audio/audioin_error.h)
names this numeric value OUT_OF_MEMORY. That supports terminology, not proof of
the PS5 service's internal allocation, native quota, leaking owner or ABI. The
observed first failing call and code are established; underlying resource refusal
is still unproven. No “already initialized” error is accepted as success.

## Change and privacy/lifecycle contract

Native startup calls client_ps5_capture_service_preinit before JNI_CreateJavaVM
and game/graphics resource use. It calls only the actual sceAudioInInit through
the same capture owner. It performs no user lookup, native port open, input read,
mute/gain/routing setter or capture enable. A successful service result is retained
for process lifetime, shared by launcher testing, enumeration and SVC opens.
This does reserve service resources even when Voice capture is OFF; it never
opens a microphone or reads samples. Default-off still gates actual OpenAL capture
and its enumeration. The explicit user-started launcher test remains separate.

Negative initialization is logged in the startup report/native stderr, stays
nonfatal for the launcher and remains eligible for a genuine later retry. No
arbitrary negative code becomes success, no fictional device is listed and no
capture route/profile changes. Actual open/read/worker errors continue to report
their fixed stage and returned code.176's retained worker/callback ownership,
failed-join pinning, disable handling, resampling and mute/reroute behavior stay.
No new capture worker is precreated: native read-thread creation under game load
still needs physical confirmation after service initialization succeeds.

This is a timing/ownership change motivated by the late-init refusal and earlier
launcher probe success, not a demonstrated PS5 cure. No heap-size/GC/global
allocator/runtime/socket/output/controller policy changes are included. The
original game/mod JARs and user's settings are preserved.

## Host controls and target audit

The capture-core test verifies failed-init retry, idempotent confirmed service
init, zero early user/open/read calls, and actual later open/pump/close without
another init. The real pinned OpenAL backend test adds three modes:

- Successful early service init with no capture enabled and no port/read, then
  force any late init to0x80260108. Three SVC-style open/read/stop/close cycles
  succeed with exactly one initialization.
- Failed early initialization remains a failure; later opens retry and propagate
  the same refusal before any port/read.
- With early initialization absent, injected late refusal still prevents open.
  The control verifies the test is not hiding init errors or fabricating capture.

The existing20playback/capture/SVC-order/failed-join modes remain required,
including the176 ASan ownership regression. Host native OS doubles establish
behavior, not actual speech or PS5 memory availability. The target package audit
requires the linked service-preinit symbol, its diagnostic and source order before
JVM entry. The actual target package audit passes, including runtime/source/import hashes
and signatures; both normal and replacement-OpenAL relinks reproduce the exact
native ELF. Fast15/native7 pass locally and from a source-only/outside-root checkout
with initially empty dependency cache. Linux/macOS hosted policy/native checks
pass on81dbd7d. [Validation and artifact checksums](validation/client177-audioin-service.json)
record these separately from pending physical-console results.

## Exact177 console checks

Install the exact177 local package and keep Voice capture enabled for SVC;
Java-microphone option stays OFF. First inspect the pre-JVM service result. On
success check that SVC progresses past init to actual port open/start and samples;
on failure retain the returned stage/code without treating the service as ready.
Compare launcher quiet/speech/hardware-muted input including silent-block counts,
then consenting remote two-way voice and simultaneous game audio. No recording.

Repeat capture stop/start and world/server leave/rejoin, verify saved state and
resource stability. Preserve176's successful user-reported transition behavior.
Actual mic route identity, hardware privacy/mute, speech quality, native worker
creation, SVC codec/transport and endurance remain pending. A reserved event-worker
warning also appeared for a transient loopback context in176; that is separate
from the established AudioIn init failure and is not repaired/claimed here.
No release/prerelease/Store publication or whole-build console pass.
