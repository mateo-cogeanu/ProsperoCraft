# Genuine GLFW core with a PS5 SDL backend

Pinned GLFW3.4core is built by tools/build_glfw_native.py. The private source
export changes only the Null selector's platform dispatch, backend state fields,
and Minecraft's optional IME input-mode routing. The selector is explicit; the
headless monitor/window backend is not used. ps5_platform.c implements real SDL
window/input/monitor operations; vulkan_bridge.c uses the existing SDL Vulkan
backend. modules.c refuses arbitrary module loading and supplies the resident
JNI initializer. GLFW's original license is retained in LICENSE.md.

The host-only PS5_GLFW_HOST_TEST switch removes the Vulkan window flag to allow
real SDL dummy-window/event tests. Production builds never use this switch.
See docs/client-26.2-glfw-122.md for validation and limitations.
