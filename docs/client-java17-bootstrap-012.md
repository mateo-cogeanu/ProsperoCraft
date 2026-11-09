# Java 17 OpenAL allocation test 012

Build 011 displayed the three colors and completed GLFW teardown on PS5.
The Java report stops at opening the default OpenAL playback device.
The native fault address, adjusted using the probe's linked anchor,
maps to the failure trap in aligned C++ array allocation. The exact
requested allocation and underlying native refusal remain unconfirmed.

Build 012 binds the pinned OpenAL object's C++ allocation and deletion
calls to paired SDK operators using the existing scoped graphics
allocator. OpenAL's existing C allocation calls use the same provider.
The application and JVM keep their existing operators. The target
audit checks that the OpenAL object has no direct unresolved references
to the process C++ allocation operators.

Install PPSA99878 version 01.000.012 and run rows 1 through 3. Look for the
three colors, the one-second tone and the result notification. If it
crashes, reopen the probe once so the retained logs are accessible.

The original Java class, runtime image and publisher inputs match 011.
Target packaging and a host check of paired aligned allocation and free
passed. AudioOut playback and the Minecraft title screen remain pending.

Signed local ZIP SHA-256 `9942be1469b05c258113014af725bac0265a597f361a1817d841d36c4ad77faf`.
