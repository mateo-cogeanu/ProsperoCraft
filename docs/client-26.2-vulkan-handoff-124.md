#26.2Vulkan initialization ownership — candidate124

Build123run1793271764-318175786fails check4(codeFFFFFAE5). The current exception
report says original Main returned after failed startup, with no clean shutdown.
Safari showed the exception and Vulkan warning; its native UI save became
unavailable, so direct read-only LAN retrieval collected the complete current
Java/native reports. Raw reports remain local under ignored build/.

The callback repair works: execution reaches backend selection. Original
NativeLibrariesBootstrap.tryLoadingVulkan calls VK.create(), but our earlier
GLFW setup already called VK.getFunctionProvider(), triggering automatic VK
initialization before originalMain could set VULKAN_EXPLICIT_INIT. The second
create throws `IllegalStateException: Vulkan has already been created.` The
game catches it, records the Vulkan loader as missing, rejects Vulkan and then
fails the unsupported OpenGL fallback. Caught OSHI/fstab warnings are not causal.
The shutdown verifier correctly rejects this failed initialization and stays
unchanged.

124gets vkGetInstanceProcAddr directly from the existing resident PS5Library.
It calls genuine glfwInitVulkanLoader through its exported address using the
existing generic JNI call. This configures GLFW's native loader pointer without
initializing org.lwjgl.vulkan.VK or GLFWVulkan Java helpers. The resident handle
closes normally; its existing resident lifetime retains the pointer. Minecraft's
unchanged bootstrap owns VK.create().26.3and snapshot paths are unaffected.

New host regression uses actual GLFW bindings and native GLFW, a real lavapipe
ICD exposed by a tiny host-only standard-loader entry wrapper, and the original
26.2NativeLibrariesBootstrap.tryLoadingVulkan. It verifies VK remains
uninitialized after GLFW configuration, original bootstrap succeeds and global
Vulkan capabilities load, the duplicate-create guard reproduces the old cause,
and VK cleanup works. Host sanitizer/JVM signal options and custom LWJGL hash
warnings are recorded locally; no host test establishes PS5 rendering.

Existing26.2callback/ABI/install/loader/Main/startup and target/package checks
remain. Physical124PS5 title/menu, controls, Vulkan rendering/world, audio,
save/reopen and clean shutdown remain pending. Preserve exact123/122/public121.
No game JAR edits, runtime changes, new Store release or frozen pass.
