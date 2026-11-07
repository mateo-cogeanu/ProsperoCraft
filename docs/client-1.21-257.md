# Local build 257 · Vanilla 1.21 through 1.21.8

Build 01.000.257 enables all nine older Vanilla releases as DEV TEST. Create a
separate instance for each of 1.21.8, 1.21.7, 1.21.6, 1.21.5, 1.21.4, 1.21.3,
1.21.2, 1.21.1 and 1.21. The already released 1.21.9–1.21.11 retain normal
status. Fabric for 1.21.x stays Coming soon.

All nine use GLFW/OpenGL through the existing Zink path and honor the launcher's
selected resolution. Vanilla 1.21–1.21.3 select the shared CPU provider compiled
against genuine OSHI 6.4.10. The same SystemInfo patch applies to both OSHI
generations, and the compiled overlay bytes match the 6.6.5 overlay. Each is
packaged under its own versioned name with its build provenance. The game and
publisher libraries remain verified downloads. Build the older overlay with
`tools/build_oshi665_platform.py --version 6.4.10` and the explicit source and
publisher cache options, then supply it to the packager via `--oshi6410-build`.

Start each new version with a fresh world. Check title-screen startup, world
creation, controls, audio, save to title, reopening the world and Quit Game back
to ProsperoCraft. If a run crashes or freezes, record the exact version and phase.
The older releases request an OpenGL 3.2 core context and use several different
renderer paths. Rendering, saving, rejoining and shutdown remain physical PS5
checks for each version.

See [build validation](validation/client257-vanilla-1.21-2026-11-07.json) for the
exact package and host evidence.
