# Minecraft 1.20 Java 17 runtime decompression test 024

PPSA99878/01.000.024 uses runtime source 0c4860d. The JIMAGE zlib
stream now uses the existing paired native scratch callbacks after
normal libc allocation refusal.

Build 023 identified zero magic in original Java method-handle classes.
The runtime decompression path can return invalid output after default
zlib allocation refusal in a release build. The exact refusal on the
PS5 remains unconfirmed. Physical startup and title-screen validation
are pending.

The Java 17 target and complete LTS patch checks passed. The actual
inflate function passed host sanitizer checks with forced normal
allocation refusal, repeated identical output and paired release on
success, corrupted input and short output errors.

All 21 consumer host checks passed. The signed package and update
comparison passed.

Signed full ZIP SHA-256
`c7691d14bc4660f7711efe4791fe1fdd3df8a234aa05fe02a40f0916a49d2675`.
