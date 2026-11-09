# Java 17 OpenAL playback test 011

PPSA99878 version 01.000.011 adds real OpenAL playback after the graphics
handoff validated in build 010. The probe prepares the existing mixer
and event workers and reserves an AudioOut port before JVM startup.
It selects the PS5 playback backend and initializes the pinned OpenAL
library through its existing lifecycle entry point. The SDK iostream
constructor retains priority ahead of the OpenAL constructors. The
target audit verifies both native constructor ranges and an empty
automatic constructor range.

Run rows 1 through 3. Watch for red, green and blue, then listen for one
second of audio. Java checks that the source starts and stops, releases
its context and device, and the probe reports the result by notification
after JVM shutdown. Leave the app open if playback fails or the tone is
inaudible so the report can be retrieved.

Signed local ZIP SHA-256
`82cff4a67b99f940ae7c5c3b33bde3d47fec3314787ba7ce918577e60d9c227d`.
The Java image and publisher inputs match build 010. Target packaging,
the host original-game entry check and both host test lanes passed.
Console playback and the Minecraft title screen remain pending.
