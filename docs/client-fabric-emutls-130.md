# Fabric26.2 compiler-TLS native abort, app130

Build129failedrun1793280668-685575193 retained native termination evidence on
reopen. The copied previous trace records abort caller0x2dffbc9, anchor0x42beb0,
preceding malloc caller0x2dfe551 and48requested bytes with NULL destination.
The exact129ELF termination symbol is0x2beb0: load adjustment is0x400000.
Resolved0x29ffbc9 is compiler-rt __emutls_get_address's abort return;
0x29fe551 is the scoped emutls allocator's malloc result check. The log includes
successful TLS address-array mapping and refused native key updates before the
worker abort. This proves a compiler-TLS allocation failure after ordinary
fallbacks, not a Java crash, a DNS-caused exit, or a shader compiler diagnosis
(the historical SHADERC FAULT label is shared by the startup fault recorder).

App130 explicitly enables the runtime-owned SDK emutls adapter's new direct
fallback before JVM creation. Default runtime behavior remains disabled. The
normal libc/anonymous routes stay first; only anonymous ENOMEM falls through
to the existing native direct ledger. Its shared256MiB/2048entry limits and
separate1536MiB heap purpose stay unchanged. Matching ownership/unmap/physical
cleanup remain in that implementation; failed growth keeps old storage/data.
Other SDK allocations, Java heap/GC and game/mod JARs are unchanged.

The reusable implementation is published in ps5-java25-homebrew d668c642.
ProsperoCraft pins hashes of the adapter header/source and existing direct
ledger header. Its build recompiles the runtime-owned adapter into the exact
backend object already consumed by resident linkage, and packages an audit of
that object and pins. Runtime source is not duplicated into this consumer.
Build129's bounded startup checkpoints and previous-native-tail retention stay.

Host ASan/UBSan exercises observed16bytepayload/48byteprefixed request with
libc/anonymous denied, defaultoff/optin, array growth/preservation, failed growth,
matching cleanup and800concurrent direct lifetimes. Existing1600map lifetimes,
actualkey/destructor/join lifecycle and directledger kernel-failure/budget/rollback/
concurrency tests pass. Target adapter compiles with-Wall-Wextra-Werror and no
compilerTLS or lazyguard. Consumer host/target/package checks are in the matching
validation record. Actual PS5 Fabric26.2 startup, world, input/audio, save/reload,
TLS cleanup and endurance remain pending. Underlying ordinary allocator/quota
pressure remains unproven. No Store release/frozen milestone; preserve129 and
accepted vanilla124. Raw reports stay local.
