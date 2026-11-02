# Genuine management API for Iris shadow initialization —200

The [199 console receipt](validation/client199-console-shader-2026-11-02.json)
records original26.1.2Fabric/Iris world activity and real PS5 Zink/MesaGL4.6,
but a fatal Java linkage error when ComplementaryUnbound_r5.9.3 HIGH enters shadow
rendering: `NoClassDefFoundError: com/sun/management/HotSpotDiagnosticMXBean`.
Its cause is ClassNotFoundException. Shader compiler warnings are present but do
not establish this failure's cause. No shader, save/quit, FPS or endurance pass.

Original Iris1.11.4 `AdvancedShadowCullingFrustum.<clinit>` asks the standard
ManagementFactory for HotSpotDiagnosticMXBean, calls getVMOption("UseFMA"), and
sets its FMA_SUPPORT boolean from the returned value.199has java.management but
omits jdk.management; merely allowing the mod does not provide this dependency.

## Runtime-owned genuine implementation

The [runtime integration pin](../client/ports/management-runtime.json) references
runtime commit724896c9711bbb7ccb24e6eec5f4ff8120e6d9bf. The runtime offers default-off
`--management-extensions`, implying existing --management. It registers the actual
target OpenJDK management_ext native library with its real JNI load hook/JMM table,
flag/diagnostic/GC native methods and isolated resident symbols. Generic runtime
packaging recognizes explicit jdk.management module requests. No VM implementation
patch, Java replacement MBean, hardcoded UseFMA, global loader or game/mod rewrite.
[Runtime scope](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/724896c9711bbb7ccb24e6eec5f4ff8120e6d9bf/Development/docs/management-runtime.md).

200rebuilds the class/resource image from target-built modules, preserving every
baseline module and explicitly adding jdk.management. It copies the corresponding
target ELF/notices, embeds the actual native group, and opts into module resolution
before JNI VM startup. Default bootstrap behavior is unchanged without the200macro.
Original release metadata fields remain; MODULES is updated to the actual image.
No host/Linux native binary enters the PS5 image. Existing native inputs/objects,
module image, source pin and class presence are audited. The JVM/VM-flag policy,
3.4.3identity, Sodium test option and199graphics fixes remain unchanged.

The candidate's launcher-owned preflight obtains the genuine bean and reads
UseFMA before original Main, logging only a validated true/false value. It never
sets the flag. Full OS/sysctl/procfs telemetry, heap/thread dumps, diagnostic
commands, GC listeners and writable flags are not established by this integration;
upstream BSD fallback behavior remains. Reusable native/image tools stay in the
runtime repository; these game inputs, packaging and validation belong here.

## Verification scope

The runtime manual test compiles the genuine OpenJDK extension sources, patches
target-built jdk.management classes into a disposable host image, and replaces only
that image's management_ext library. Trace handles must resolve real Flag methods
to the rebuilt library. Child JVMs force actual UseFMA=false/true; unknown and
readonly options are refused, Xcheck:jni stays clean, and removing the rebuilt
library fails rather than silently loading an installed stock extension. Host core
java.management remains intentionally stock. No installed JDK changes.

`test_iris_management.py` takes explicit runtime/JDK/compiler and publisher/mod
caches. It verifies [original Iris](../tests/iris-management-pin.json), existing
Sodium pin and26.1.2publisher inputs, then invokes that forced-native test with the
**unmodified original Iris shadow-frustum class**. Its actual static initializer
and private FMA_SUPPORT value must match both real VM settings. Original JAR bytes
must remain unchanged. No test double, transformed game class, pack rendering or
physical-console compatibility is inferred. This manual check is outside portable
CI; its prerequisites are different from launcher policy/native lanes.

## Required release test

Shader loading/rendering on the exact PS5 build is now an explicit user-required
release prerequisite, in addition to existing physical confirmation and release
approval gates. Compilation, a host test, an active no-shader world or a shader
name in a crash report cannot satisfy it. No release/prerelease/Store upload.

Install PPSA99874 /01.000.200 and retry the same Iris instance and
ComplementaryUnbound_r5.9.3 HIGH pack. Confirm actual shader-enabled world rendering,
then enable/disable/reload behavior. Keep new failures open, or reopen after a hard
crash without starting another game. Save/reload, Quit Game/relaunch, world creation
timing, audio/haptics,26.2+Vulkan and endurance remain separate pending tests. No
new frozen milestone or broad pack compatibility claim.
