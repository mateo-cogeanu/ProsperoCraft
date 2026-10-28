# Development119: snapshot6 JNA bootstrap

The user reports snapshots1–5fully functional on118and snapshot6crashing. The reopened console reports118. Safari retrieved the previous crash from run client-01.000.118-1793199161-414730331; current launcher is a separate reopened run. Raw reports remain ignored/local, with bounded evidence hashes in the validation record.

## Concrete failure

Snapshot6introduced an early NativeLibrariesBootstrap.loadJNA call, which invokes Native.getLastError before the game window exists. The original com.sun.jna.Native initializer cannot load its PS5 native dispatch library. Its crash report identifies26.4-snapshot-6, no initialized window/graphics device, and the expected working PS5 CPU identity. This is not evidence of a shader/renderer failure or failed OSHI7CPU provider. No JVM fatal error or VM abort is captured in the matching previous-run reports.

The118host smoke test reached an unavailable LWJGL native on desktop, whose publisher JNA JAR includes a usable desktop native bridge. That test did not establish PS5 JNA support.119adds a direct test of the specific original loadJNA method with our newly built JNI bridge and forbids classpath native fallback.

## Repair

The reusable Java runtime tool builds genuine pinned JNA5.19.1 dispatch.c/callback.c using generated JNI headers and the authoritative native ABI7.0.4from upstream common.xml. It does not use stale native/Makefile generated version defaults. The consumer integrates its69JNI exports under resident library jnidispatch, sharing the existing compatible native libffi implementation. Default Java runtime libraries/images are unchanged.

For a selected instance containing the original JNA5.19.1dependency, the launcher uses JNA's supported system-library lookup and disables unpacking/classpath native extraction. JNA's own class loader loads the resident bridge when original code initializes it. Earlier JNA versions retain the previous launch policy. No replacement com.sun.jna.Native, patched Minecraft class, ignored native error or server/game JAR transformation is introduced.

The native implementation retains JNI memory/direct-buffer/error/call/callback code. JAWT and optional signal-interception protection are not enabled. Host memory/error/libffi tests pass, but this does not establish every JNA function, arbitrary dynamic-library loading, callbacks or native-thread attachment on PS5. The registry still only resolves configured resident groups; no arbitrary ELF loader is added.

## Checks and next console test

The genuine target dispatch/callback sources compile and link into119. The exact publisher JNA Java JAR passes forced-library native size/error/memory/string and real libffi host calls. The unchanged original snapshot6loadJNA method now returns successfully using that bridge on host.26.3instance/account/startup regressions and package checks pass.

Install119and retry the existing Vanilla snapshot6instance. Check the title screen, input/audio/rendering and a new world with save/reload. Snapshot6could reveal a later compatibility issue after this early failure is removed; no PS5success is claimed yet. Snapshots1–5have positive118feedback; do not replace that record with assumed119regression acceptance.119retains118/117packages and Store117. Microphone and performance tuning remain outside this repair.

Candidate119ZIP SHA-256: `de43986035602bcedc81ed904ec1db22b4148ec7b22001c95725ad2348c63c19`.

Runtime source: [genuine JNA builder](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/5b25cc2446f58bbbff2c2537b9310d3330007d99/Development/tools/java25_jna.py). JNA upstream: [pinned source](https://github.com/java-native-access/jna/tree/1a91122853f6ab6f1fb2a4a284a6cf2ed8af0a4d). See [console feedback](validation/client118-snapshot-console-feedback-2026-10-28.json) and [119validation](validation/client119-jna-bootstrap-build-2026-10-28.json).
