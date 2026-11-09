# Java17 bootstrap005 default filesystem mode

[004's retained record](validation/client-java17-bootstrap-004-crash-2026-11-09.json)
confirms the VM, class definition, native registration and actual Java/nativeStage
entry succeed. The last marker precedes the first Path.of expression, which also
looks up the root property, before any Java stage file. SIGSEGV is captured but its
PC has not been assigned to a generated/resident code region. The exact underlying
function/cause is unproven; management,331and original Minecraft were not reached.

005tests standard upstream `-Dsun.nio.fs.chdirAllowed=true` in this standalone
harness. UnixFileSystem then always resolves native relative paths against its
configured Java default directory instead of comparing native getcwd. It does not
invent a cwd, change native filesystem answers/capabilities, replace game classes
or disable real I/O/errors. The existing configured Java default directory and
absolute probe report paths remain unchanged. This is a targeted workaround test;
there is no proof yet that getcwd is the faulting function or that005fixes it.

Runtime17source `2cb439a76ab79b13d0cff39cea9c56c51704e859` adds fixed native markers at UnixNativeDispatcher init/
completion and getcwd entry/return. Native behavior/defaults are preserved. These
markers plus the existing JNI/native Java-entry scopes distinguish the next boundary.
128MiB/image/331/SerialGC/interpreter and bounded fault capture stay unchanged.
The exact host17consumer bootstrap with this mode reaches genuine management and
original Main's argument gate; PS5specific331initialization is explicitly skipped
on host. Required21fast checks pass. Actual PS5 result is pending.

Install separate PPSA99878 **01.000.005**, run1,2and3, then4if3passes. If it crashes,
reopen005once and leave it at the test screen without repeating the crashing row.
Report the first failed row or all four boot results. No playable menu/world or
C2/shader/performance acceptance is established.

Local`dist/PPSA99878.zip` SHA256`258e21ebf133d977c10b840d62dc09b9af91a01892f2374428f678974d4738f5`; see the
[build record](validation/client-java17-bootstrap-005-build-2026-11-09.json).
Retained report paths and active FTP mount are in[002](client-java17-bootstrap-002.md).
All prior candidates/symbols and frozen17/21startup remain; working25launcher is
unchanged. No binary release/Store action; original publisher payload stays local.
