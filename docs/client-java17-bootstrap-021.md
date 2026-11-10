# Minecraft 1.20 Java 17 failure screen test 021

Build 020 returned a Java exception after handing off the probe display.
Its Java VM shut down, but the probe left the screen black while keeping
the process available for FTP.

PPSA99878/01.000.021 returns to the probe screen after Minecraft returns,
with row 3 and VM shutdown status visible. It terminates GLFW before
reopening the probe display. Java records the original throwable type
when possible. JNI copies a bounded class name into a stack buffer so
reporting does not depend on allocating a UTF copy under memory pressure.
Neither reporter prints exception messages.

The Java runtime stays pinned to a4ec5a3. The underlying launch exception
and physical display recovery remain pending.

The signed executable and the update comparison passed. A Java 17 host
check confirmed that the report records nested exception types and omits
exception messages.

Signed full ZIP SHA-256
`99daae9a8c18182f0bd92b2958e14552e595fba5e449b828ce460359882d7f16`.

The PS5 run stopped after the original Main class initialized. Neither
the JNI return nor the new Java failure report ran. The fault log is
byte-identical to 020 and supplies no current-run address. The cause
and display restoration remain unvalidated.
