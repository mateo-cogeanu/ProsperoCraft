# Java17 bootstrap003 heap isolation and inner phases

[002's retrieved record](validation/client-java17-bootstrap-002-crash-2026-11-09.json)
shows VM arguments, ergonomics, OS init2 and VM globals complete; init_globals
never returns. Original game/Java module initialization is not reached. Although
the external fault recorder installed successfully, its file is empty, so no PC
or cause is established. All three reports download through FTP without repair.

003returns only this diagnostic test's maximum heap from512MiB to128MiB, matching
the already passing standalone17profile, while retaining the extended image and
331bindings. It is a controlled hypothesis test, not a proven fix or production
heap cap. Runtime17also brackets individual management/JVMTI/class-loader/code-
cache/CPU/stub/heap/interpreter phases. Its fatal entry records numeric ID/PC/
requested bytes/source line before ordinary formatting, bounded to four records;
no dynamic error messages, caller paths, allocations or recovery are added. The
original VM/error handling remains. Runtime source:`075c8f04febbb88cab761ee19d93e7d86e7295f0`.

Install standalone PPSA99878 **01.000.003**, run rows1and2, then3and4if2passes.
If it crashes, reopen003once and leave it at the test screen without repeating
the crashing row. This is still a boot test; no playable menu/world or C2/shader
acceptance. Report the first failed row or ALL PASS for these four checks only.

Local`dist/PPSA99878.zip` SHA256`9cebd2659c11b170d377b694db32f1fa7dac39a6b184dc6c3b9c677561a2afa8`. See the
[exact build record](validation/client-java17-bootstrap-003-build-2026-11-09.json).
Files/active FTP path remain as documented in[002](client-java17-bootstrap-002.md).
001/002packages/symbols and frozen17/21startup stay preserved; working Java25 is
unchanged. No release/Store publication; original publisher payload stays local.


The user reported003row3crash; retained logs confirm VM creation and module/language
initialization now return. See the[003record](validation/client-java17-bootstrap-003-crash-2026-11-09.json)
and[004row3diagnostics](client-java17-bootstrap-004.md). Complete boot/game behavior
is still unvalidated; original003bytes remain preserved.
