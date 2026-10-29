# Unreported native application exit, app143

The user reports142finished loading then closed with a PS5 application error,
without reaching the menu; it was not a user-closed freeze. Safari retrieved
run `client-01.000.142-1793295111-54984214` and matching preserved native stderr.
The last shader checkpoints stop at parser/linker diagnostic formatting. Java
output stops during the resource reload. The abort report explicitly records
no VM abort. No fresh matching JVM fatal report was obtained; a local previous
HS report is from141and must not be reused as142evidence. Process-usage output
has only its header because stack/resource observation was disabled. Actual
extended HotSpot priming counts are not retained in these saturated tails.

This does not identify a fatal instruction, signal, allocation failure or leak.
The last shader message is a checkpoint, not proof that shaderc caused the exit.
142does retain OpenAL logging mutex ENOMEM exceptions; their relationship to
this hard exit remains unproven. Raw reports remain local. No crash repair is
claimed from this evidence alone.

143repairs a concrete diagnostic weakness: the scoped signal recorder guarded
its state with an SDK static pthread mutex and ignored lock/unlock results.
Under the observed native allocation pressure that lock can fail. The guard
now uses fixed atomic state without native initialization or allocation. The
recorder additionally covers SIGFPE, SIGTRAP and SIGSYS alongside SEGV/BUS/ILL/
ABRT, forwarding each signal/context unchanged to the previous handler. Existing
four-signal return/status APIs preserve their legacy semantics; a separate
extended-status API reports the seven-bit ownership/query mask. Startup records
that mask and query failures without claiming unsupported signals installed.
No fault recovery, context rewriting or swallowing of native failures is added.

143explicitly enables the existing startup stack/resource observer. It takes
bounded snapshots at the existing schedule (initially1Hz), including native
resource queries and signal ownership. This is a diagnostic run and may change
timing/overhead. Detailed shader/compiler/parser success/progress messages are
limited to256with one suppression notice, using a saturating atomic counter.
Failure stages and unrelated checkpoints always remain visible. This prevents
repeated shader traces from crowding out the finite preserved VM/startup tails.
The new native sources and source/object audit hashes are packaged.

Host tests exercise actual signal registration/delegation/restoration, masks,
external handler displacement, legacy/extended ownership,8,000 concurrent nested
scope leases and signal forwarding for ILL/FPE/TRAP/SYS and SA_SIGINFO SEGV.
They keep the outer startup scope alive across compiler calls. Host context tests
use four raw words; PS5 retains its existing pinned96-word context capture.
The shader-stage test runs80,000 concurrent calls and checks exactly256records,
one suppression notice and a saturating counter while every failure/unrelated
stage remains visible under ASan/UBSan. Existing native observer and launcher
checks, actual target build and full package/preservation checks remain required.

Reusable Java runtime patches/pins, heap/GC, game/mod JARs, instances, worlds,
settings and authentication remain unchanged. This is consumer-only diagnostics,
not a confirmed fix for142. PS5 exact143signal/stack/resource evidence and the
underlying exit cause remain pending, alongside Fabric26.2menu/world/audio/save/
regression testing. Preserve142and earlier canonical candidates/symbols,
accepted124and Store121. No Store release or new passing milestone.
