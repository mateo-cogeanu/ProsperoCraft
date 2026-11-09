# Java 17 Minecraft 1.20 bootstrap 007

On PS5, build 006 read the verified classpath manifest, created the game
classloader and passed the actual LWJGL 3.3.1 native allocation, read, write
and free check. Row 3 then returned error -1708. The exception chain was
InvocationTargetException → ExceptionInInitializerError → IllegalStateException.
The captured run ends at the row 3 failure. The retained native fault report
matches the earlier report byte for byte.

Build 007 separates initialization of Minecraft's original Main class from
invoking its main method. A checkpoint marks successful class initialization.
On unexpected entry failure, the Java report records class and method names
and line numbers for up to eight frames per cause and up to five cause levels.
It filters names to bounded ASCII identifiers and omits exception messages
and source filenames. The original exception still fails the probe. The exact
source of the initializer failure is pending a console report.

Install PPSA99878 version 01.000.007, run rows 1 through 3 and leave the probe
open if a row fails. Run row 4 if row 3 passes. This test stops at the original
required argument check before menu or world startup.

The signed local ZIP SHA-256 is
`0e5e67a57f140185fcf7ef5d7c21731062bde92f107abc69f6e10f48e0cf5818`.
Its runtime and publisher inputs match 006. The host Java 17 entry check
reaches the original argument gate with the PS5 binding check skipped, and
a focused host check verifies nested exception locations and message/path
redaction. Physical validation of 007 is pending.

[Build 007 result and ZIP filesystem fix](client-java17-bootstrap-008.md)
