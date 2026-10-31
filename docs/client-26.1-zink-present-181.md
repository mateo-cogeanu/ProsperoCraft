# Native Zink presentation probe181 — stage2a

User reports exact180 **Stage1 PASS**. Its [console receipt](validation/client180-console-stage1-2026-10-31.json)
records context/readback/destruction only. Preserve its tested ZIP/symbols and
original build record unchanged.181 is a new independent native-only candidate,
PPSA99874 /01.000.181. Root/current game launcher remains179. No release or Store
action is authorized.

## Physical test

Install the complete181 PPSA99874 folder, replacing the current installed app.
Open and press **X once**. Expect three roughly four-second cycles, each showing
red, green, then blue backgrounds with a white bar moving left to right.
There may be a blank interval while the real context/swapchain/window is destroyed
and GLFW/SDL terminates and reinitializes. After all three cycles, expect a
**Zink181 stage2a checks PASS** notification. Confirm separately that all three
animations were visible and moving. Automated swaps do not establish visibility.

The final framebuffer is released, so the screen may become blank. Keep the app
open for read-only reports at `http://<PS5-IP>:8765/`. `build.txt`, `session.txt`,
`startup.log` and `vm-trace.log` identify exact181 and a unique run id. After a
crash reopen without X to retain failed reports. Raw reports stay local; no preset
address or client filter is included.

This candidate tests the positive GLFW/SDL/kopper path and repeated native
teardown/reacquisition. **It does not return to the actual Java launcher.** The
remaining part of console row2 is the real launcher ownership handoff, after
scoped JVM integration. No Main/title/world/audio/save/reopen/relaunch or Vulkan
game regression follows from181. The26.1.x production gate stays blocked.

## Implementation and checks

The [private frontend](client-26.1-zink-native-180.md) and combined Mesa/RADV object
are unchanged from180.181 adds the actual genuine GLFW/SDL native providers,
using their existing SDL display selector (up to120Hz with genuine60Hz fallback),
Zink's existing VkInstance, VK_KHR_display surface, kopper FIFO swapchain and
reserved WSI worker. No second game device/presenter or CPU framebuffer copy is
added. SDL's short-lived display-inventory instance is destroyed before creating
the Zink context; no second presentation owner is introduced.

Each animation uses real GL clear/scissor commands and real GLFW swaps, then
unbind/destroy/window termination. A single white pixel plus128guard bytes is
read before the first swap of each cycle. Timing is monotonic. Reports record
selected inventory refresh and completed swap counts; neither is a measured
physical scanout/FPS result. No high-refresh claim follows without console logs
and appropriate measurement. A completed teardown call does not alone prove every
asynchronous driver allocation was reclaimed; repeated cycles exercise reacquisition.
Failures stop rather than reporting success or proceeding with uncertain cleanup.

Bootstrap retains the existing genuine SDL mutex/condition/TLS initialization,
app-data cache checks and process-owned WSI worker reservation before provider use.
No JVM, Java/OpenGL JNI bindings, game JARs, asset objects or OpenAL is linked.
SDL's existing audio code may be linked as a dependency, but no audio subsystem
or port is initialized here. This is a lighter standalone native process and does
not prove JVM resource coexistence. The native CRT still runs actual constructors.

`tools/package_zink_present_probe.py` verifies actual combined/dependency/source
pins, privately renames the two genuine unused JNI initializers to avoid a symbol
collision, and garbage-collects unreachable native sections. A native-only local
visibility map prevents application exports unsupported by this converter. This
removes unused desktop SDL dependencies rather than adding success stubs. Mouse
imports use the same real system-library declarations as the existing app; import
stub bodies are never shipped. One-copy GL/RADV/NIR and GLFW/SDL exports are checked
in the symbols ELF. Target compile/link/converter checks pass.

`tools/test_zink_present_host.py` compiles the exact animation/lifecycle source
with a120ms test interval, actual rebuilt GLFW and Zink on macOS lavapipe. All
three guarded clear/scissor/swap/readback/teardown/reinit cycles pass ASan/UBSan
(frontend/GLFW/driver only; remaining Mesa/ICD ordinary builds). SDL dummy windows
are offscreen; this test does not exercise positive kopper/VideoOut presentation.
Inputs are explicit, including compiler and GL/GLFW headers. This research tool
is outside required portable CI lanes and searches no game cache.

```sh
python3 tools/test_zink_present_host.py --cc /path/to/clang \
  --glfw-library /path/to/rebuilt/libps5glfw.dylib \
  --frontend /path/to/rebuilt/libprosperozink.dylib \
  --glfw-headers /path/to/glfw/include --gl-headers /path/to/mesa/include
python3 tools/package_zink_present_probe.py --check-only \
  --runtime-workspace /path/to/runtime --llvm-home /path/to/llvm \
  --component /path/to/ps5/zink-radv-unscoped.o
# After checks/source commit, omit --check-only to create a new candidate ZIP.
python3 tools/test_client181_package.py \
  --runtime-workspace /path/to/runtime --llvm-home /path/to/llvm
```

Local output is `dist/candidates/zink-present-181`; existing candidate ZIPs are
never overwritten. Its matching validation record is added after packaging.
Preserve029 OSMesa, adapted GLFW callbacks, runtime allocation/TLS/sync/stack
fallbacks, original game JARs, frozen history and release/Store gates. Minecraft
launcher integration, all three26.1 release title/world/save cycles and existing
Vulkan game regressions remain pending.
