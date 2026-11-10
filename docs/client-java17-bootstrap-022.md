# Minecraft 1.20 Java 17 pending exception test 022

PPSA99878/01.000.022 uses runtime source 058856a. It enables the explicit
VM pending exception trace at the original Main checkpoint and disables
it when JNI returns. Up to 128 VM exception installations record a
bounded class name and source line with fixed buffers. This aims to
capture failures before the Java and JNI reporters.

Build 021 stopped after Main initialized. Its fault report did not grow.
The exact failure is unresolved. Physical row 3 and title-screen
validation are pending.

The Java 17 target build, complete LTS patch application/idempotence and
local sanitizer checks of the actual trace helper passed. The helper
checks covered default-off, bounded class names, byte sanitization,
the process-wide record budget and toggle behavior.

All 21 consumer host checks passed. The signed package and update byte
comparison passed.

Signed full ZIP SHA-256
`08354e31bcf8fc59a65db62725240150f352d7b90a6d6cfaee202c839e7a56de`.
