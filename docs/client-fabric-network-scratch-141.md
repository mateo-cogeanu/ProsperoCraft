# Native DNS conversion-node scratch, app141

Safari retrieved build140 failed run
`client-01.000.140-1793293545-800526367` after reopening. Both the native worker
and RADV mutex/condition reserves report success. The original Minecraft26.2
report now fails during initialization with
`OutOfMemoryError: Native heap allocation failed` from
`Inet4AddressImpl.lookupAllHostAddr`, on the account-service HTTPS path. The JVM
heap report still has considerable free space; this identifies a native
conversion-node allocation failure, not a Java heap exhaustion diagnosis.
The raw reports stay local. This does not establish that140 presented frames
or passed gameplay; the new failure can occur before that test point.

The reusable fix is published in ps5-java25-homebrew, commit
`ee5f2561c30ee493e6a96628a888aa62ff6fac66`, patch0130. It adds an independent,
default-off libnet node scratch policy and reuses the bounded temporary mapper
from0127. Libc and anonymous allocations remain first. Only anonymous ENOMEM
permits the opt-in direct mapping path. Each of Inet4AddressImpl,
Inet6AddressImpl and NetworkInterface owns64entries/8MiB (24MiB aggregate).
Aligned node prefixes and exact allocator-specific release remain in place;
failed direct cleanup retains bounded ownership. DNS answers, retry policy,
authentication, heap/GC and global allocators are unchanged. It is not a general
native-memory shortage fix or proof that every mod can fit.

Consumer141 pins the runtime patch/source commit, calls its explicit setter
before JVM startup, embeds the rebuilt libnet native objects, and packages the
matching libnet.so and source/object/library audit hashes. No reusable Java
implementation is copied into this repository. Original game/mod JARs,
instances/worlds/downloads/settings/authentication behavior remain unchanged.
Previous VMA, shaderc, SDL/GLFW, RADV and native worker changes are retained.

Runtime host ASan/UBSan checks cover the actual node header, mapper and policy
getter/setter with default off, libc/anonymous precedence, forced malloc/mmap
ENOMEM, direct node data/errno, overflow/64slot bounds, map rollback,8,000
concurrent allocations and matching cleanup. Existing actual SDK DNS/results/
ownership/IPv4/IPv6 conversion and direct scratch cleanup-failure tests pass.
Direct-memory syscalls remain host fixtures. Actual target java.base-libs build,
policy exports, patch application and native object/library hashes are checked.
Consumer checks cover launcher behavior, explicit pre-JVM enablement, target
link/signing, exact packaged runtime/pin hashes, CRC/source/licenses and frozen
history. Host results are not PS5 acceptance.

PS5 DNS/HTTPS/account lookup, Fabric26.2 startup/presentation/menu/world/input/
audio/save/reload/endurance and working vanilla26.2/26.3/26.4 snapshot regression
remain pending.140also reports OpenAL diagnostic mutex failures; this candidate
does not claim those are repaired or establish working audio. Preserve140/139
and all previous canonical candidate packages/symbols, accepted124, frozen
milestones and Store121. No Store release or new passing milestone is created.
