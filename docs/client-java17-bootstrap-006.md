# Java17 bootstrap006 explicit classpath

[005's result](validation/client-java17-bootstrap-005-result-2026-11-09.json)
shows filesystem initialization/Java log writing, basic Java/JNI/worker checks and
actual RuntimeMXBean identity now pass. Row3returns Java error-1708after management
before331; row4DestroyJavaVM succeeds. It is not another native crash. The retained
fault file is previous004data. The exception class was not captured by stderr's
partial output, so the exact directory/URL/classloader preparation cause is unknown.

006replaces directory scanning/sorting and File.toURI metadata probing with a
builder-generated `classpath.list` containing the exact47verified JARs in the
same deterministic numeric order, overlay first. Genuine Files.readAllLines reads
the manifest. Count2..128, unique names and an ASCII numeric-prefix JAR filename
rule reject path separators/URI syntax/traversal; only explicit file URLs are
constructed. This removes an unnecessary enumeration dependency, not a claim that
the whole directory API is broken or fixed. JARs retain their original hashes;
the manifest hash joins the package input audit. One loader/context still owns
the complete331and original game. No game class rewrite or native success stub.

Native failure reporting replaces ExceptionDescribe with fixed allowlisted class
labels (including nested causes only at depth0..2). It emits no exception messages,
stack text, user paths or authentication material. Unknown types are marked
unclassified. JNI pending exceptions remain visible as a failed check, then are
cleared for the diagnostic UI as before. Additional checkpoints distinguish
manifest read, parsing and loader construction.128MiB/chdirAllowed/image/331and
bounded fault scopes remain unchanged; runtime source is still2cb439a.

Install separate PPSA99878 **01.000.006**, run1,2then3and4if3passes. If it showsFAIL,
leave that screen open. If it crashes, reopen006once and leave it open without
repeating. Report the first failing row or all four boot results. No playable
menu/world/C2/shader/performance acceptance is established.

Local`dist/PPSA99878.zip` SHA256`d92dee967515b464dc9b627f00f1014b1fcb3210090250cd4c3fde5c7cc9b994`; see the
[build record](validation/client-java17-bootstrap-006-build-2026-11-09.json).
Host17entry with the manifest reaches original Main's argument gate; PS5specific
331is explicitly skipped on host. Target signatures/ZIP/image/manifest hashes pass;
exact006console result is pending. Previous candidate/frozen bytes and working25
are retained. No release/Store action; original publisher payload stays local.
