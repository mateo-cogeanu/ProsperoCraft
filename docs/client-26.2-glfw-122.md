# Minecraft26.2 candidate122

The original26.2publisher client uses Java25, LWJGL3.4.1, GLFW and asset index32.
26.3 and the accepted26.4snapshots instead use SDL and LWJGL3.4.3.26.2already
includes Vulkan, so this integration preserves its original JAR and selects its
supported `--graphicsBackend vulkan` option.

## Window and input

The new resident `ps5glfw` library contains pinned genuine GLFW3.4core, with an
explicit consumer SDL3PS5 platform backend selected through GLFW_PLATFORM_NULL.
The selector does not run GLFW's headless monitor/window implementation: window,
monitor modes, events, keyboard state/Unicode callbacks, mouse, capture, clipboard
and Vulkan surfaces use actual SDL calls. The same accepted SDL VideoOut/input
port and resident Vulkan loader are reused. OpenGL context requests are rejected;
no new OpenGL support or arbitrary module loader is introduced. The SDL video
and event references are balanced without globally quitting other SDL users.

The original instance GLFW Java JAR delegates to the launcher's existing native
core/Vulkan/etc. All936original game LWJGL method references resolve against this
actual parent/instance boundary without native initialization. All118required
GLFW core symbols, Vulkan surface functions and used optional IME ABI exports
are linked in the target app. This is evidence for the checked ABI, not complete
3.4.1/3.4.3native compatibility or broad mod compatibility.

Ordinary Unicode text is supported. PS5 has no native IME composition service;
its mode remains disabled, while callback/rectangle ABI is retained. GLFW's
joystick interface remains unsupported; Controlify uses the existing separate
SDL interface. Other desktop-only window/display features remain subject to
SDL's PS5 limitations.

## Desktop dialogs

26.2's original NativeLibrariesBootstrap also loads LWJGL tinyfd eagerly.
The consumer JNI adapter explicitly identifies itself as a PS5 adapter with
**desktop dialogs unavailable**. It returns cancel/null for dialog, file/folder
or color requests and logs the unavailable operation, without a shell, blocking
prompt, invented filename or accepted confirmation. It does not claim to be an
upstream TinyFD implementation. Original TinyFileDialogs JNI tests verify these
results. Minecraft's own in-game screens and launcher content browsing remain
separate. Desktop file selection is not added by this candidate.

## Scope and validation

Only26.2is added to the explicit launch list.26.1and future/unlisted snapshots
remain unsupported.26.2uses its own verified original libraries, asset index,
instance folder and release versionType. Existing26.3/snapshot routes, auth,
world data, themes/cursor, saved preferences and snapshots-off default remain.

Checks: real GLFW+SDL dummy window under ASan/UBSan, three init/teardown cycles,
keyboard state and callbacks, Unicode including emoji, mouse/button/scroll,
optional IME ABI/rectangle, close handling, and explicit OpenGL rejection;
original26.2publisher install/hash/CPU-provider/launch policy and original Main
reaching expected absent host-native bootstrap; all six snapshot regressions;
target build/signing and package/native/source audits. The host TinyFD check
uses a custom-built native core, for which stock LWJGL prints a hash mismatch
warning; its explicit JNI contract assertions pass. That warning is not a PS5
result or full native-version compatibility proof.

Physical PS5 validation remains pending. Create a **new Vanilla26.2instance**,
check title screen, menu cursor/controller/keyboard, world creation and play,
block/audio output, save/quit/reopen and clean application return. Keep existing
26.3/26.4worlds separate from this older version. Fabric/Controlify/mod26.2and
long-session behavior need separate console validation after Vanilla.

No Store release or new frozen milestone is authorized by this work. Public121
and its exact package remain preserved. Runtime source is unchanged; this is
consumer dependency and launcher integration.
