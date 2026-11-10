# Minecraft 1.20 Java 17 verifier scratch test 019

PPSA99878/01.000.019 gives the legacy verifier access to the existing
PS5 HotSpot native allocation fallback. The prior run had an
unclassified OutOfMemoryError at aoi class initialization. No trace
identified its origin, so the verifier is a working hypothesis.
The probe recognizes verifier context without recording the original
exception message. The Java heap and original game assets stay the same.
Physical row 3 and title-screen validation are pending.

Java runtime source a006e1a passed the target build and its verifier-to-VM
link audit. The signed executable, archive and update passed verification.
The web host check timed out in the full run and passed on its own.
The remaining host checks passed.

Signed full ZIP SHA-256
`07a59545ee0abbbd3c8cf7819fccdd647f5a4082aef0aad3d31be007dc4e0ef7`.

The PS5 run crashed after entering original Main. The runtime logged a
libjava OOM request, and the fault address mapped to the application
array allocator's deliberate trap after malloc returned null. The
individual callers remain unconfirmed.
