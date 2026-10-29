# Original native C++ exception diagnostics, app135

Failed134run1793286316-41038613 progresses past previous queue condition creation
and reaches shaderc_compiler_initialize. Retained abort0x2de365c, anchor0x42beb0
and prior realloc0x2de362c/995bytes/NULL resolve with load adjustment0x400000 to
0x29e365c/0x29e362c in exact134symbols. Disassembly identifies libc++abi's Itanium
exception-name formatter aborting when its output-buffer realloc fails. Native
stderr also reports libunwind reader/writer-lock failures. This formatter failure
may obscure an earlier C++ exception; its original type/code is not captured.
The earlier queue condition reserve returns0. Do not claim the original throw
is identified or that another synchronization replacement fixes it.

App135 adds a consumer __cxa_throw wrapper at the final startup link. It emits
at most128best-effort records into existing startup history before forwarding
the unchanged object/type/destructor to the original ABI function. It records
call site, in-image load anchor, raw type_info name (not demangled), and the
native error_code value only for exact SDK libc++ std::system_error type. It
never calls what() or formats an exception name. Fixed stack buffer, bounded
literal metadata, partial writes/EINTR handling, paired close and errno restore
avoid depending on dynamic allocation. No exceptions are caught, suppressed or
converted. This applies to startup diagnostic integration; other probe variants
retain their prior link flags. There is no game/modJAR or Java runtime change.

Host ASan/UBSan forwards actual system_error and integer exception objects through
the genuine host C++ ABI. Catch handlers verify original type/code/message and
destructor behavior. Tests check failed logging, errno, partial writes/EINTR and
128event bound. Target/package checks confirm actual throw-call routing, source/
object hashes and emitted marker. Existing host launcher/fullpackage/frozenhistory
checks are recorded in validation JSON. This is a diagnostic candidate, not a
claimed fix for134's original exception. Existing allocation/synchronization fixes
are retained. No Store release or frozen milestone. PS5 original throw capture,
Fabric26.2 launch/world/lifecycle/endurance and working-version regression remain
pending; raw native/Java reports stay local.
