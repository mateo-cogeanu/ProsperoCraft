# Private Zink frontend and shared Mesa/RADV build

The numbered patches and `frontend.c` implement an opt-in private Mesa GL
state-tracker frontend. EGL/GLX are disabled. Zink uses the existing layerless
Vulkan loader and the same pinned Mesa/RADV tree, with one extracted archive
closure. The kopper callback uses genuine SDL/VK_KHR_display surfaces and FIFO;
positive presentation still needs hardware validation. Compiler-emulated constant
TLS avoids desktop GL dispatch TLS. The separate029 OSMesa provider is retained.

See [implementation, build commands and stage1 test](../../../docs/client-26.1-zink-native-180.md)
and the original [Phase A design](../../../docs/client-26.1-zink-plan.md).
`tools/build_zink_native.py` verifies the source archive, existing VideoOut patches,
new patches and original exported source inventory. The macOS research lane
executes actual Zink on lavapipe with rebuilt GLFW/LWJGL and verified original
26.1.x inputs. It does not execute PS5 RADV or establish game compatibility.
There is no production resident group, JVM integration or launcher enablement yet.

`sources.json` preserves the original Phase A source-pin receipt; its introductory
scope describes that pinning step. The implementation status is recorded here.
Mesa/Zink sources carry their original MIT notices; the pinned tree contains
`docs/license.rst` and per-file copyright/licenses. Archives and binaries stay in
ignored local storage. Existing project/component licensing and OpenAL source/relink
obligations remain unchanged. The native180 probe links no OpenAL or JVM.

Optional194 `ps5zink_prepare_screen` prepares the real shared screen/required
initial queues before JVM pressure. Context creation reuses it; existing last-
context destruction still owns cleanup. Default builders remain lazy. See
[194 preparation/lifetime limits](../../../docs/client-zink-prewarm-194.md).
