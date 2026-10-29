# Remaining native mutex caller diagnostics, app138

Build137 failedrun1793290330-927421401 initializes both realtime/monotonic RADV
condition pools and successfully returns from shaderc_compiler_initialize. It
then records another libc++ std::system_error code12 (ENOMEM), followed by the
known low-memory exception-name formatter abort. The generic throw helper's
caller does not identify the original operation, and no claim is made that
this is the same initialization lock repaired in136.

App138 adds a bounded consumer startup std::mutex::lock ABI wrapper. Shaderc's
native initialization entry enables it; the first256calls after that point
record enter/return IDs, calling address, in-image anchor and mutex address.
An additional64record bound captures failed native pthread_mutex_lock calls
with their direct callers and actual return codes, including inlined SDK mutex
operations; this failure bound is independent of normal-call logging.
All calls, including those after the logging limit, forward to the original
libc++ lock implementation. An original throw naturally leaves an unmatched
enter record; no catch, skipped lock or alternate lock is introduced. Fixed
stack buffers, best-effort partial-write/EINTR handling and saved errno avoid
new heap dependencies. Recording remains capped during gameplay. Earlier native
trace/exception records remain enabled, with exact known std::system_error's
existing what() message now included (no demangling or new message construction).
This helps distinguish the failed native operation as well as its error code.

The shaderc lifecycle enables tracing through an optional weak hook so other
probe variants do not require or activate the startup wrapper. This is only
consumer diagnostic integration, no Java runtime source/pin or synchronization
policy change. Existing allocation/sync/clock/compiler repairs are retained.

Host ASan/UBSan tests actual recorder code against genuine host mutex blocking/
exclusion, errors propagated as the same system_error, unmatched-enter behavior,
unchanged errno, disabled gating, partial writes/EINTR, open failure and the
256call bound while all lock calls still forward. Actual C++ exception ABI
forwarding/destructor/type/code/message tests also pass. Target disassembly must
show std::mutex lock call routing through the wrapper and forwarding to the
original implementation; source/object/package audits record the exact build.
Target inspection also verifies inlined SDK mutex calls route through the native
failure recorder. Existing launcher/fullpackage/frozenhistory checks are recorded separately.

This is diagnostic138, not a confirmed repair for137's remaining exception.
PS5 original caller identification, Fabric26.2 render/world/input/audio/save/
reload/endurance and working-version regression remain pending. Preserve137/
priorcanonicalcandidates, accepted124vanilla and Store121. No Store/frozenpass.
No officialJAR, auth/settings/instance/world or Javaheap/GC change. Raw logs local.
