# Local176: primary review of the microphone handback

The primary maintainer reviewed Claude's [175 handback](handoffs/microphone-174/HAND-BACK.md)
and exact source changes. The three175 artifact SHA-256 values match the handback.
Its useful changes remain: original-SVC-order capture tests, live capture listing,
stop/disconnect when disabled, invalid-user/short-read diagnostics and conservative
failed-join ownership. No physical174/175 result was provided. The original173
SVC open failure still has no proven native cause; the successful launcher input
counts do not establish speech, mute or two-way voice.

## Demonstrated review defect

175's failed pthread_join leaves the global port/lease pinned, but its worker
retains a Ps5Capture pointer. OpenAL can destroy that backend/device anyway. If a
blocked native read then returns an error, the worker dereferences the destroyed
backend for mDevice/kill. A new actual-OpenAL host failure fixture reproduces
heap-use-after-free in Ps5Capture::run under ASan. This is a demonstrated host
lifetime defect, not proof that it caused the173 console failure.

176 keeps the producer's stop flag and callback gate in process-lifetime state.
The worker never retains a backend pointer. Stop requests cancellation before
joining. Both successful and failed join paths detach the device callback under
an allocation-free mutex; detach waits for any in-flight callback to finish.
Only then can the logical backend/device be destroyed. After uncertain join, the
port/lease and worker state stay pinned until process restart; enumeration lists
nothing, sample access refuses, and a new open cannot reclaim that owner. Late
native input completion accesses only retained core/worker state. No premature
native close, speculative rejoin, descriptor reuse or recovery claim is added.

A failed competing open has no lease and must not stop/detach/clear the active
capture. The new global worker state therefore has an explicit lease-owner guard
on stop. The real SVC-order test checks a refused second open while first capture
continues delivering samples. The callback-gate unit test holds a callback while
detach waits, destroys its target, then attempts a late notification safely.

## Verification boundaries

The actual upstream OpenAL + PS5 backend host fixture has a capture-only join
injection at compile time. Target builds reject that option and use the real
pthread_join. Its102mode blocks native input, forces join EINVAL, destroys the
OpenAL device, confirms no native close/lease reuse/enumeration, then permits a
late input error and joins the test thread through the fixture for clean testing.
With175 backend source the original test first detects incorrect pinned-device
listing. Omitting only listing assertions lets execution reach the late callback,
where ASan reports heap-use-after-free. Source is restored after each negative
control; all20host modes pass with176. No test hook is included in target builds.

Local fast15/native7 pass; the latter includes the actual callback gate test under
ASan/UBSan. Physical read blocking/pacing, hardware privacy/mute/route, SVC codecs,
UDP/two-way speech and console cleanup remain unverified. Original173 cause is
still unknown. Target package/relink results and checksums are recorded after
build completion in the matching176 validation. No release or Store change.

## Console test

Use the exact176 package with Voice capture ON and SVC's Java-microphone option
OFF. Check default/named device selection, intentional speech versus quiet and
hardware-muted input, then consenting remote two-way voice with game audio. Read
PS5 AudioIn stage/code diagnostics if an open or worker fails. Stop/start and
world/server leave/rejoin repeatedly and verify saved state. A true failed join
must make capture unavailable until restart; do not reset a pinned owner to hide
it. A native input call that never returns can still delay stop: no unsafe close
from another thread was introduced. The existing runtime0135 title-screen repair
is retained unchanged and still requires its own console acceptance.
