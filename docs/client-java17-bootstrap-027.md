# Minecraft 1.20 Java 17 native fault test 027

Build 026 reached original Main twice, then received SIGBUS at the same
native instruction address. Neither run recorded a thread creation
refusal. The native caller and failure mechanism remain unresolved.

PPSA99878/01.000.027 enables probe-only stack reporting in the existing
signal recorder. It records executable image offsets found in up to
64 aligned words within the registered upper main-stack window. The
offsets are candidates for symbol lookup. Setup logs selected native
entry addresses for correlation with the fault address. The handler
continues to forward the original signal to its previous owner.

The Java 17 runtime uses 7a5e810. Target packaging, signed archive
integrity and update byte comparison passed. A sanitizer fixture
checked the stack scan against out-of-range and unaligned inputs,
the 64-word limit and filtering to image addresses.
Physical capture, native attribution and title-screen validation
remain pending.

Signed full ZIP SHA-256
`131e5b6e0329c5f4246d7ad4e65c7bc3ceec21d5ce40076d8ecc42ffe713b2ee`.

All 21 launcher host checks passed. The scoped signal forwarding and
report budget check passed. The full native lane stopped at a haptics
timing assertion on the first run and an OpenAL worker timeout on the
isolated retry.

The PS5 fault capture identified an application return address directly
after pthread_mutex_lock in HotSpot. Further candidates resolve to
class metadata allocation, including ConstantPool and ClassFileParser.
The native initialization status was not captured.
