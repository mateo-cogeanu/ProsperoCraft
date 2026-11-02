# Native flag query and final SDL lifecycle —202

The [201 console record](validation/client201-console-native-query-quit-2026-11-02.json)
separates current shader black-screen and retained quit evidence. Original Iris
AdvancedShadowCullingFrustum now finds management and reaches Flag.getFlags, but
its later UseFMA query throws OutOfMemoryError from that native routine. The early
management and parent OpenAL preflights passed. Other missing-program messages,
getifaddrs ENOMEM and haptic invalid-device errors remain open; no universal cause
or shader render pass is inferred.

## Runtime0136: real small native queries without heap scratch

The [runtime pin](../client/ports/management-runtime.json) advances to
e579bdbda18dd3409cc8d35b0bedcbeed1c908ed, adding
[0136](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/e579bdbda18dd3409cc8d35b0bedcbeed1c908ed/Development/java25/patches/0136-ps5-management-small-query-stack.patch).
On PS5 only, the actual OpenJDK Flag.getFlags routine uses a per-call stack array
for up to16jmmVMGlobal records. Larger requests retain malloc/refusal. Every free
path distinguishes stack/heap ownership; no shared reserve, mapping, VM flag spoof,
Java class replacement or heap/GC change. Genuine JMM values/origins/writability
remain. Java/VM allocations may still fail; native libc refusal remains unresolved.

Forced runtime host tests compile the actual PS5 C branch with **only Flag.c malloc
refused**, exercising1/16record queries,17andfull-list refusal, real false/true
UseFMA,8threadsx1000queries, unknown/readonly behavior and Xcheck:jni. Trace handles
must use the rebuilt genuine native library; removal fails without stock extension
fallback. The original Iris initializer runs under the same allocator refusal.
Target management_ext rebuild passes. These are native query/initializer checks,
not shader rendering or general OS management acceptance.

## Main-thread SDL finalization before verified restart

The retained201quit log proves current stopping/no-fatal/game-stopped state but
SDLmask6210 remains after the grace period: AUDIO, JOYSTICK, GAMEPAD and EVENTS.
No VIDEO is live. The native Controlify event facade deliberately retains an
EVENTS reference for the process lifetime, so waiting cannot guarantee zero.
The missing piece is final process-session SDL cleanup, not a longer delay.

The202wrapper explicitly enables PROSPERO_GLFW_FINAL_SDL_QUIT=1. After genuine
GLFW termination destroys windows and releases its VIDEO/EVENTS reference, the
SDL-backed platform performs real SDL_Quit **on SDL's main thread**, but only if
the remaining mask is a subset of6210. Live VIDEO, unknown subsystems or a foreign
thread refuse cleanup. Zero requires no work. It checks the actual zero mask after
SDL_Quit. The real SDL lifecycle closes devices/objects and joins its workers;
no raw refcount edits, detached workers, fabricated completion or direct native
handle reclamation. Default builds do not enable this behavior.

Java still requires the same current marker, Stopping, no fatal marker, stopped
game and **SDLmaskzero** before arming; expected residual bits are not treated as
clean. The native VM-exit hook checks zero again, and refuses restart if nonzero.
A genuine host test showed VM-exit callback thread affinity is not SDL main, so
no SDL_Quit runs there. No JNI call is made after VM termination. Cleanup is
executed through GLFW's existing main-thread teardown before System.exit.

The manual real GLFW/SDL dummy-window ASan/UBSan test initializes audio/gamepad/
events and requires6210-to-zero finalization through glfwTerminate over3lifecycles.
The manual embedded genuine HotSpot/SDL test executes main-thread finalization
before real System.exit and verifies zero again in the native VM-exit hook before
host exec replacement. Required Java child-JVM tests still reject a6210residual,
VIDEO and unknown bits even with candidate property set, alongside existing
fatal/running/null/stale/nonzero controls. Target SDL/VideoOut/audio/haptic worker
behavior remains a physical test, not established by dummy drivers.

202retains the201binding ownership,200genuine management image and199real graphics
component. No game/mod JAR changes, VM/heap/GC policy edits or release179identity
change. Prior packages/symbols remain retained. Generic flag patch is runtime-owned;
GLFW/SDL policy, packaging and shader validation are consumer-owned.

Install PPSA99874 /01.000.202. Test same shader startup and actual enabled world
rendering, then shader disable/reload and Quit Game/relaunch with/without the pack.
Keep failures open or reopen without another launch after a hard crash. Physical
shader success remains mandatory before release. Save/reload/world creation timing,
audio/haptics/Vulkan regression/endurance remain pending; no release/Store/freeze.
