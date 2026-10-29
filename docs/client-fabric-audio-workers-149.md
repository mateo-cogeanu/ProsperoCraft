# Reserved OpenAL mixer workers, build 149

Build 148 reached the Minecraft menu, then the user reported an application crash
when pressing Down. The matching run is client-01.000.148-1793300736-257060851.
The input recorder saw mask 0x40, followed by four completed queue/fence/flip
cycles. No fatal signal, VM abort or fresh JVM error report identifies the later
exit. The previous JVM report is stale (18:18:19) and must not be used as this
run's cause. Raw diagnostics remain local. The menu-exit cause remains unproven.

A separate concrete audio failure is present: alcCreateContext reaches the PS5
backend, but std::thread creation throws error 35, Resource temporarily
unavailable. OpenAL rejects that context with error 0xa001. HRTF discovery also
reports directory_iterator ENOMEM, which OpenAL catches; it does not establish
that this was the fatal event. Native exception fallback-heap mutex errors are
secondary diagnostics, not proof of the later exit.

149 reserves two real pthread workers before JVM startup. Each has a 256 KiB
stack and a process lifetime. OpenAL assigns a device mixer to an idle worker
using an exclusive atomic lease. Pause/stop signals the original kill flag and
waits for job completion before releasing the lease or draining/closing the
AudioOut port. Idle workers never access a device. Reload/resume reuses workers;
there is no late worker creation or allocation. Initialization and pool exhaustion
produce real backend failures rather than fabricated audio success. Partial
initialization leaves already-created workers idle and reports the failure.
The worker poll interval is 1 ms; no FIFO scheduling guarantee is added.

The actual OpenAL mixer, channel/rate/buffer format, retained port, PCM output,
error handling and previous scoped lock changes remain. No game/mod JAR,
Controlify input, Java runtime pin, heap/GC policy, account, world or settings
changes are made. The LGPL relink export includes the new exact worker source.

Host checks exercise initialization errors, two simultaneous real jobs, exhausted
leases and 1,000 completion/reuse cycles while later thread creation is denied,
with ASan/UBSan. The real OpenAL backend test initializes the reserve before
opening devices and verifies nonzero mixed/resampled PCM, pause/resume, repeated
device reopen, retained ports and AudioOut errors. Package audits verify the
worker header, backend, bootstrap and native symbol hashes; the exact native ELF
must be reproducible by the exported relink kit. These are host/build checks.

Pending exact PS5 149 menu Down/input transitions, audible sound, world creation,
save/reopen, endurance and regression on working versions. The unreported menu
exit remains open until a console test or fatal evidence resolves it. Preserve
148 and all prior canonical packages/symbols, accepted 124, frozen milestones
and Store121. No Store release, merge or passing milestone.
