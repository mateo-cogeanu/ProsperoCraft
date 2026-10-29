# Optional larger HotSpot monitor reserve, app142

User reports141reaches the loading screen and approaches completion before
crashing. Safari retrieved failedrun
`client-01.000.141-1793294262-958074280`. The original JVM fatal report checks
`monitor mutex_init` with ENOMEM12. Its Java stack is in hidden class generation
for Controlify's SDL FFM downcall initialization. The retained prior VM tail
records matching configured attributes with all4096 mutexes initialized and
leased. This identifies pool exhaustion followed by failed native initialization;
it does not prove a leak. Raw console reports stay local.

The prior DNS exception is absent from this crash's Java report. Resource atlases
are created and Controlify initialization begins. These are concrete later
startup checkpoints, not world/gameplay acceptance.141also reports failure to
open an OpenAL device and diagnostic logging mutex exceptions;142does not claim
that separate audio issue repaired.

The reusable repair belongs to ps5-java25-homebrew patch0131. It adds an explicit
bootstrap-only extended synchronization policy. Defaults still initialize4096
mutexes/4096relative-clock conditions/2048absolute-clock conditions. When enabled
before priming, the request becomes8192/8192/2048. Fixed maximum metadata arrays
hold the expanded capacity even when disabled; extra native objects are created
only for the explicit mode. The setter rejects changes after initialization
starts. Actual successful priming counts remain authoritative. Pool exhaustion
still reaches the original native fallback and checked failure; native ownership,
blocking, attributes, condition clocks/deadlines and lease reuse remain unchanged.
Java heap/GC and global SDK synchronization policies are not changed.

Consumer142 pins the separately published runtime patch, checks the policy
setter before JVM startup, embeds rebuilt HotSpot objects, and packages the
matching libjvm.so plus object/library/source audit hashes. There is no copied
runtime implementation or game/mod JAR rewrite here. Earlier native allocation,
DNS, VMA, SDL/GLFW/compiler and RADV/presentation repairs are retained. Instances,
worlds, authentication and settings behavior remain unchanged.

Host ASan/UBSan exercises the actual native resource pools in separate default
and extended runs, denying late native initialization. It checks exact primed
counts, full mutex/relative/absolute exhaustion and reuse, native wait/signal/
timeout, busy-destroy rejection, custom attributes,8,000 concurrent lease
lifetimes, native cleanup and rejection of policy changes after priming. Target
IR verifies fixed storage/atomics without allocator/compiler TLS/lazy guards.
Actual HotSpot build, export, source/object/library hashes and consumer package
checks are recorded separately. These checks do not establish console acceptance.

This work can benefit other versions using these shared paths: bounded native
conversion buffers, ZIP descriptor lifetime, SDK TLS, native graphics locks and
HotSpot synchronization are not exclusively26.2game code. Which versions/mods
benefit still depends on their dependencies and actual PS5 tests; no broad
compatibility or full native-memory diagnosis is claimed.

Pending: exact142 native priming counts, Controlify FFM initialization,
Fabric26.2menu/presentation/world/input/audio/save/reload/endurance and working
vanilla26.2/26.3/26.4snapshot regression. Preserve141and earlier canonical
candidates/symbols, accepted124, frozen milestones and Store121. No Store release
or new passing milestone is created.
