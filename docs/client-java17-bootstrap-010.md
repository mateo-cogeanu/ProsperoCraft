# Java 17 graphics reserve test 010

Build 009 closed the probe display, completed GPU constructors and passed
the original Minecraft 1.20 argument gate. GLFW then returned failure at
initialization. No color frames appeared and DestroyJavaVM succeeded.
The pinned GLFW uses SDL mutex leases, which were unavailable because
the probe had skipped SDL reserve initialization.

Build 010 prepares the existing VideoOut worker, RADV mutex and condition
pools, SDL mutex and condition pools, and SDL thread ID TLS before JVM
startup. Row 1 reports a failed reserve before any display handoff.
A native GLFW error callback records a bounded description during the
graphics test. After handoff, a PS5 notification reports the outcome
and the app stays available for FTP retrieval.

Install PPSA99878 version 01.000.010 and run rows 1 through 3. Look for
red, green and blue frames and the final notification. Leave the app
open for log retrieval.

Local signed ZIP SHA-256: `bf739a2d8951f0477b8e69ba68c72af13ce0216c3372f1e5e6a6eb7d49d57672`.
The package passed target linking, signing and verification. Physical
graphics, teardown, audio and the Minecraft title screen remain pending.
