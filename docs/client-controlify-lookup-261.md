# Build 261 native callback lookup ownership

The user's build 260 report confirms the checked JNA loader errors now reach
Controlify's optional HID exception handler. Minecraft then reports
OutOfMemoryError while installing the mouse-button callback, with about 810MiB
of Java heap still free.

The retained native trace records the exact LibFFI JNI entrypoint selected by
HotSpot. After the verified image adjustment, it matches the parent LWJGL
entrypoint in the retained exact-build symbols. The distinct namespaced 333
entrypoint and its pre-JVM callback-page reserve are present in the same image.
The selected Callback handler itself belongs to 333. The lookup therefore mixes
the two native generations despite a coherent original 333 Java class owner.

Other builtin JNI libraries sharing that Java class loader received the process
handle. This let a native method resolve through the parent group's exports
before reaching its actual 333 group. Build 261 explicitly requests restricted
resident handles for jnidispatch, ps5glfw and ps5openal, alongside the existing
namespaced 333 handle. The generator and the reused NativeLibraries handle hook
belong to the Java repository. Consumer pins and independent package audit require
all three selections. The fix changes lookup ownership, using the existing
callback allocator and its existing 64 reserved pages.

Runtime tests execute generated tables for explicit unrenamed handles, aliases
and rejection of another library's exports, with and without symbol prefixes.
The actual patched JNI load-body tests cover publication and initializer failures.
No-options generated registry output compares byte for byte with the previous
published generator. Physical 261 callback dispatch, title screen, controller
handoff, world play/save and quit remain pending. The broader native allocation
pressure remains unresolved.
