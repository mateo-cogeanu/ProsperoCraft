# Local178: prepare the opted-in input port before game loading

The177 console run now logs AudioIn pre-JVM service init result0x0. SVC still
shows its generic microphone-unavailable message, but both native attempts now
fail at stage=open result0x8026010b, before a capture worker starts. Format is the
expected48000Hz mono Float32. Matching Java output confirms OpenAL open fails,
then Java Sound fallback cannot supply a microphone. Raw reports stay local.
The actual failing stage is established; the internal PS5 allocation/quota owner
is not. Do not treat this code as successful initialization or a usable device.

## Opt-in and ownership

When Voice capture is enabled, client_ps5_capture_enable now acquires the same
exclusive lease and attempts a genuine native port open. The existing launcher
calls enable(true) while applying a saved ON choice in prepareLaunch, before
Minecraft is launched; toggling ON in the microphone panel also prepares the port.
Default-off never prepares or opens it.177's pre-JVM service-only initialization
is retained separately and opens no input port.

Preparation opens the real current profile and validates its reroute counter,
without any AudioInInput call. The launcher copy now says ON prepares system
input and OFF releases idle input. No microphone unmute/gain/routing setter, new
permission, browser microphone, fake audio source or game/mod JAR transformation.
A prepared native input handle remains open while Voice capture is ON; no input
samples are requested by this code while it is parked. A deliberate launcher
test or mod capture starts actual reads. This is a changed resource lifetime,
not a claim that an open hardware device is physically powered down.

A healthy port is parked after the producer has stopped/joined, clearing this
app's queued samples and interpolation history. Its next logical open claims the
same handle without late native allocation; counters/history reset. Enumeration
of a confirmed prepared port returns the genuine device without an additional
open or input read. The explicit input test similarly returns a healthy port to
prepared state while ON; when OFF it actually closes after the requested test.

OFF acquires and closes an idle prepared port. It never closes a live or uncertain
producer's port. Active capture sees OFF at the existing worker boundary, stops
reading/disconnects and its eventual confirmed stop/close releases the handle.
An already-blocked native read can still delay stop. Failed join keeps176's static
worker state and detached callback, pins ownership and refuses reuse. Failed
native close also pins the handle/lease and is never retried speculatively.
Unhealthy read/route failure is not retained as a usable prepared device; actual
cleanup errors propagate. No recovery success is invented.

If launcher preparation fails, log PS5 AudioIn prepare stage and returned code;
SVC can make a genuine later attempt, with the normal stage diagnostics. The ON
setting is permission to try, not proof of availability. A competing preparation
cannot steal an active/pinned lease. Enable-state changes and the release decision
are serialized: OFF cannot miss a just-parked port, and ON during a native close
waits and prepares a replacement after that close completes. Turning OFF after a failed close and then ON
does not reset uncertain ownership or fabricate a device.

## Verification

The actual capture core tests park/reclaim20times without another native open or
close, clears queued samples, and checks final explicit close. Real upstream
OpenAL + backend tests retain all prior23modes and add three actual-boundary modes:

- Enable ON prepares exactly one real input port with zero reads. Force all
  subsequent native opens to0x8026010b. Five SVC-style read/stop/close/reopen cycles
  succeed by reusing that port. Enumeration of a parked port makes zero open/read
  calls. OFF closes it; re-enable under continued refusal genuinely fails and
  enumeration does not invent availability.
- Force native close failure on OFF. Ownership stays pinned; a new open/probe/
  enumeration cannot read, reopen or retry that close. This is conservative
  failure ownership, not a cleanup-success claim.

- Block a native close during OFF and concurrently request ON. ON waits until the
  close completes, then prepares exactly one replacement with zero reads; final
  OFF closes that replacement. The setting cannot silently miss preparation.

Target package audit requires the new preparation diagnostics and matching source
hashes, in addition to177 early-service order and176 exclusion of host-only join
injection. Fast15/native7 pass locally and from a source-only/outside-root checkout with
initially empty dependency cache. All26actual OpenAL modes pass; removing only
the capture-policy lock guards causes the blocked-close/ON race assertion to fail,
and restoring the source makes all26pass. Target package/signature/source/import
checks and both exact relink paths pass. Linux/macOS policy and native Actions
pass on7ba83f5. [Validation and checksums](validation/client178-audioin-port.json)
record these separately from pending physical-console tests. Host OS doubles do not establish the PS5 resource-lifetime behavior.

## Physical acceptance still needed

Install178 with Voice capture ON before Play; keep SVC Java microphone OFF.
Inspect service init and prepare-port-ready logs, then confirm SVC progresses to
worker start/sample delivery and actual speech. If preparation already fails in
the launcher, preserve its stage/code instead of inferring success from the ON
label. If open succeeds but native worker creation fails, preserve that returned
pthread code; no capture worker was precreated speculatively in this build.

Compare deliberate quiet/speech/hardware-muted tests including silent-blocks,
then consenting remote two-way voice alongside game audio. Verify headset versus
DualSense system route and repeated stop/reopen/world/server transitions and
saves. Application ring/history clearing is checked; it is not proof of an OS
input-buffer flush. No unverified null-buffer native flush call was added. Input
freshness/latency and hardware-mute behavior across parked intervals need physical
checks, as do driver resource release and endurance. No audio recording is saved.
Existing user-reported176 leave/rejoin behavior must remain. No release/prerelease/
Store or whole-build console pass is implied by this local candidate.
