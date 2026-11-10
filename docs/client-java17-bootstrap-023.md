# Minecraft 1.20 Java 17 class format diagnostics 023

PPSA99878/01.000.023 adds bounded native detail for the ClassFormatError
identified by build 022. The VM copies the source basename and up to
255 bytes of the existing ClassFormatError message into stack buffers.
This runs only under the explicitly enabled pending exception trace.
Raw report text stays local.

The target Java 17 build, complete patch application and idempotence,
and sanitizer checks of the trace helper passed. The helper checks
covered source basename isolation, bounded detail, control character
replacement, ClassFormatError selection and the record budget.

The rejected class, repair and physical title-screen acceptance remain
pending. This candidate gathers the missing failure reason.

Runtime source is 9a2aa63. All 21 consumer host checks passed, as did
signed package integrity and the update comparison.

Signed full ZIP SHA-256
`01d8811a6ea86704c42cd2d89ee6664a6a2c0a86cb8e6f6a9431b4f942b38ad3`.
