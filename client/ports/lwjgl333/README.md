# Matched LWJGL 3.3.3 PS5 integration

Development only: original publisher JARs remain intact. The separate overlay
contains genuine pinned Platform/APIUtil/Library/ThreadLocalUtil/GL/ALC sources,
PS5 resident dispatch and a consumer bootstrap. Version stays **3.3.3+5** and the
runtime stays Java25. No game classes, mappings, Vulkan binding or version spoofing
are bundled. See [candidate205](../../../docs/client-1.21-205.md).

`sources.json` pins genuine upstream source archives, compile-only annotations and
licenses; `runtime.json` pins the separately published runtime integration.
The three patches disclose every upstream adaptation. BSD and embedded STB notices
are retained here and in the local package; bootstrap integration is GPL-3.0-or-later.

The child game loader owns the entire333 binding namespace and bootstrap. Missing333
classes never fall through to343. SDL bindings remain in the launcher owner.
The runtime opt-in namespace prefixes **all definitions**, including data and
compiler TLS, while original lookup names resolve through a selected builtin handle.
Original343/native providers stay linked unchanged. Process-wide lookup still has
first-match behavior; this is generation routing, not a security boundary.

209 target native source units provide genuine333 core/callback/JNI/OpenGL/STB plus a generation-owned closure allocator, the
existing resident bridge and three bootstrap diagnostics. Actual libffi ABI guards
follow the chosen headers. C APIs share existing real GLFW/Zink/RADV/OpenAL/FreeType;
there is one graphics provider and VideoOut owner. Jemalloc is unselected under the
system allocator. Windows/GLX/platform-specific bindings are excluded. SharedLibraryUtil,
LibCErrno, LibCLocale and LibCStdio natives remain unavailable; no343 ABI fallback.
The existing TinyFD adapter remains explicit desktop-dialog unavailability/cancel;
its eleven333 native descriptors are checked, without adding a fake dialog.

Java25 JNI table size is checked against actual headers and GetVersion. Missing-call
tables are private. The native owner never frees a foreign generation's JNI table,
accepts TLS key0, propagates allocation/key refusal, rolls back partial ownership,
and detaches only its own attached threads. The shutdown hook retains the upstream
late-detach guard. These contracts are exercised with real JVM failure injection.

`tools/build_lwjgl333.py` takes explicit publisher cache, compiler, runtime and ffi
inputs; dependency downloads require `--fetch-deps`. Host and target outputs are
separate. Host generated JNI uses UBSan except function-type checking because
upstream function-pointer bridges deliberately cast C ABI signatures. Ownership
fixtures additionally use ASan/UBSan and XcheckJNI. No host result establishes PS5
startup, callback lifetime, rendering, audio, save/reload or clean shutdown.


Build206 compiles the existing closure W->X adapter separately inside the333
namespace, with an explicit64-page pre-JVM reserve. Ordinary mmap remains first;
only ENOMEM may borrow a reserved page. Each closure owns an independent page and
retains the real libffi prep/call ABI. Free resets a reserve page to RW before reuse;
failed reset quarantines that page with its backing retained. Partial bootstrap
priming retains bounded ownership but fails initialization and never publishes a
partly ready pool. Other failures remain real. At the PS5 page size this is1MiB,
not a larger heap or native allocator budget. The original343 ffi group remains
exact204 bytes. See [repair206](../../../docs/client-1.21-206.md).

The reserve's real x86_64 libffi ASan/UBSan fault/concurrency test is separate from
the original333 Java callback host tests. Apple ARM64's stock libffi uses trampoline
tables and is not a valid W->X adapter test backend; the explicit x86_64 test uses
its genuine dynamic trampoline branch, under Rosetta on ARM Macs. No ARM table
adapter or PS5 callback/console pass is implied.


Build 207 reuses genuine JNI GetEnv for already attached PS5 callback threads,
without allocating another native EnvData record or setting TLS. Existing own
native attachments retain their async flag and destructor; foreign attachments
remain foreign-owned. Unattached native threads still require the real original
attach/record/TLS path, with separate refusal diagnostics. See the
[world-entry PNG repair and tests](../../../docs/client-1.21-207.md). No extra reserve
or game transformation is introduced by this change.
