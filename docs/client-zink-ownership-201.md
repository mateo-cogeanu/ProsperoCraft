# Packaged LWJGL ownership and concurrent shutdown audit —201

The [200 console record](validation/client200-console-startup-quit-2026-11-02.json)
separates the user's startup-with-shader failure and later no-shader quit crash.
Both game attempts successfully query the genuine diagnostic UseFMA=false, so
200's missing-management-API repair has narrower positive console evidence; it
is not shader or complete runtime acceptance.

The original time-correlated initializing-game crash report identifies an
IllegalAccessError: ALC10 is defined by an instance URLClassLoader, while ALC is
defined by app. ALC10 cannot access package-private ALC.getICD across that loader
boundary. The shader-associated load order exposed this OpenAL ownership failure;
the report does not establish a shader compiler failure or why the parent lookup
missed ALC10. Official JARs remain intact.

## Consistent native binding owner

ProsperoGameLoader delegates every org.lwjgl class exclusively to the packaged
parent owner. Ordinary game/Fabric classes retain normal URLClassLoader behavior.
If a parent binding is missing, it propagates ClassNotFoundException instead of
loading a publisher copy that splits native singletons/package-private callers.
This applies consistently to vanilla/Fabric instance loaders. The packaged adapted
GLFW binding still comes first; other original parent LWJGL3.4.3 modules remain.
No child JAR rewriting, class replacement or false3.4.1 identity is introduced.
Unpackaged LWJGL modules fail explicitly; no arbitrary native support is implied.

Before original Main, a finite non-initializing preflight loads ALC/ALC10/ALC11,
AL/AL10/AL11 and their capability classes through the MemoryUtil parent owner.
It checks identity and caches those classes before later mod/pack loading pressure;
it makes no OpenAL call and cannot prove device/audio compatibility. The root
cause of any transient parent lookup failure remains open.

The manual `test_binding_ownership.py` takes explicit actual package and verified
publisher cache/JDK. Genuine parent3.4.3 plus original publisher OpenAL3.4.1 reproduce
the old split when the parent module is removed. New loader policy refuses that
fallback; complete parent bindings and preflight share one owner. Inputs remain
unchanged. This is class linkage/ownership coverage without native execution.

## Preserve checks while allowing concurrent cleanup

The actual launcher-owned latest.log has the current marker and Stopping with no
fatal entry for the later run. Native shader queue fences/barrier destruction
complete. The Java audit rejects before VM EXIT:0 and the unarmed native exit
faults; exact remaining game-running/SDL-state condition was not recorded. Haptic
invalid-device errors remain unresolved and are not assigned as the quit cause.

Java shutdown hooks run concurrently. The clean-exit observer previously checked
once, so a real cleanup hook could still be completing.201retries the **same**
current-session/Stopping/no-fatal/game-stopped/SDLmask-zero audit for a2second grace.
A fatal audit state fails immediately. Reflection/I/O failures do not become
success, and permanent incomplete states still fail. The grace bounds retry time,
not a potentially stalled filesystem/native call. Nothing stops threads, quits
SDL, destroys resources or bypasses real cleanup on the observer's behalf.
Final failure records only bounded booleans and the actual SDL bitmask; no paths,
credentials or exception text. Native gate still requires a verified zero exit.
This is a concurrency repair candidate plus diagnostics, not a physical quit pass.

The required child-JVM System.exit test uses a latch so another real shutdown hook
cannot start delayed SDL cleanup until the audit enters. Only eventual real zero
state arms exit. Stale/fatal/running/permanently-live-SDL/null/checkpoint/arm failure
controls remain rejected; nonzero VM exit remains refused by the native gate.

201preserves200's genuine management image/native integration and199graphics
component. The package builder forwards its explicit JDK to runtime image tools.
Prior packages/symbols stay retained. Reusable runtime source/pin remains unchanged;
these loader/launcher-policy changes belong in ProsperoCraft.

Install complete PPSA99874 /01.000.201. Restore the same shader pack through the
normal flow, retry startup and actual shader-enabled world rendering, then test
Quit Game and relaunch with and without shaders. Leave failures open or reopen
without starting another game. Shader rendering remains a mandatory exact-build
physical release check; quit/save/timing/audio/Vulkan/endurance remain pending.
No release/prerelease/Store action or new frozen milestone.
