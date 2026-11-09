# Java 17 graphics handoff test 009

PPSA99878 version 01.000.009 keeps the Minecraft 1.20 argument gate from
build 008 and adds a separate graphics check afterward. Row 3 closes the
probe's VideoOut session before running Java on the same thread. The
existing PS5 SDL, GLFW and Zink/RADV objects then back a real LWJGL 3.3.1
OpenGL window. Java checks the renderer and submits red, green and blue
frames for about one second each, checks for GL and GLFW errors, and
tears down the window. The native harness attempts VM shutdown
automatically and keeps the process open for report retrieval.

Install the signed local ZIP and run rows 1, 2 and 3. Report whether all
three colors appeared in order. Leave the app open after the colors or a
black screen so the startup report can be retrieved. If the app crashes,
reopen it once and leave it at the probe screen.

The package SHA-256 is
`7aa5ddfdcb4d2d9c5a485426898ad950adc9998513fb552e175972d66d9a90a8`.
The Java image and all 47 JARs plus the classpath manifest match 008.
The target link contains one Java VM, GLFW and Zink/RADV implementation
and a nonempty graphics constructor range. PS5 conversion, signing,
package checks and the host original-game argument gate passed. PS5
display handoff, visible output and shutdown are pending. OpenAL
initialization and the actual Minecraft title screen are subsequent checks.

The builder takes the exact object and stub paths through repeated
`--graphics-input NAME=PATH` options and verifies each against
`client/java17_bootstrap/graphics-pins.json`. The original game inputs
and signed test ZIP stay local.
