# Launcher and lifecycle candidate 01.000.082

PPSA99874 development082 continues consumer commit1a5a996 and runtime9afa03ad.
[Published release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.082)
and [frozen scoped console pass](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Launcher_Lifecycle/README.md). Install the complete folder,
including sce_sys/param.json. The app still requests4096MiB at
`/download0/ProsperoCraft`; instances, cache, options and worlds are preserved.
Only exact26.3 with an SDL receipt can launch in demo mode. Microsoft approval
for the existing public application ID remains pending. Original game JARs and
assets are unchanged;074 sound/performance and081 gameplay controls are retained.

[Build record](validation/client082-launcher-build-2026-10-26.json) ·
[OK focused](launcher/082/intro.png) ·
[Checkbox focused](launcher/082/intro-checkbox.png) ·
[Unchecked](launcher/082/intro-unchecked.png)

## Welcome and navigation

OK is focused initially. D-pad or left-stick LEFT/RIGHT moves between OK and
**Show next time**. X dismisses OK or toggles the compact tickbox. UP/DOWN does
not move between these horizontal controls. The existing saved preference,
older-library default ON and Settings → Startup notice remain. The approval
explanation, roadmap and full bottom-right01.000.082 version remain visible.

The native launcher now maps left-stick directions to the same navigation as
the D-pad across the grid, top bar, create/detail/settings/account and name
keyboard. Top-bar LEFT/RIGHT works alongside L1/R1; UP reaches it from the grid,
including an empty library. The controller guide has no selectable rows;
Circle/Options returns as before. Native stick navigation is separate from the
existing SDL gameplay/menu adapter, right-stick cursor and text picker.

Native input engages at56 of128 displacement and releases at28, holds the
selected axis against diagonal noise, repeats after400ms then every100ms and
requires neutral before initial/reconnected navigation. D-pad has precedence
over stick; identical directions emit once. Disconnect/interception/read errors
clear held state and pending events. Samples missing for250ms stop repeat.
Held entry actions require release before activation.

The existing focus interpolation now drives the outline's actual position and
size, with a110ms press response. It snaps when settled, redraws only during
changes/transitions, and Reduced Motion snaps immediately without press motion.
The idle welcome model reuses its cached state. Previews execute the actual
native draw code, not an HTML mockup.

## Quit and session ownership

The original081 photo shows FFFFFAE5, matching native-1307 after the wrapper's
unconditional IllegalStateException when Main returned. Current-run reports
could not be retrieved: the last documented console endpoint was unreachable
through both shell and browser. The photos do not establish every exit path.

Inspection of the pinned original26.3 bytecode establishes that normal Main
runs Minecraft, calls exitWorldAndClose, then starts its post-main watchdog.
SilentInitException also returns early; a plain Main return is insufficient.
Minecraft.close destroys sound/resources, closes GPU surface/renderer/window,
calls SDL_Quit and shuts down executors. SDL VideoQuit releases temporary
keyboard/mouse input and hides its cursor. The WSI retains its process-wide
VideoOut, scanout resources and cursor allocation. Minecraft static executors,
watchdogs and resident native libraries make another Main in the same JVM unsafe.

082 adds a fresh unique marker to the existing rolling game log before Main.
On return it requires a **current-session** Stopping! record, no recognized
fatal/startup/shutdown error, a non-null original Minecraft singleton with
isRunning=false, and SDL_WasInit(0)=0. Reads of original public lifecycle state
use reflection; there are no hooks, game class replacements or JAR edits.
A missing/ambiguous record, active SDL, early return or Java exception fails
explicitly. Existing crash/System.exit paths are not suppressed or converted to
successful quits. The gate checks logs across both rolling files and latest.log.

After verified cleanup, Java restores its streams and native JNI references
are released. The bootstrap invokes
`sceSystemServiceLoadExec("/app0/eboot.bin", {"--prospero-library", nullptr})`.
This is a process replacement, **not** a second display/VM in the old process.
The OS boundary retires retained WSI/cursor/audio resources, native and Java
threads, classloader and static state. Only the fresh executable starts the
native display, early AudioOut setup, controller and JVM. Its argument skips
the welcome once and opens the library without changing the saved preference.
Downloads/settings/worlds are reloaded from the same persistent paths. Account
credentials remain memory-only, so a fresh process starts signed out.

Any return from LoadExec is a distinct restart failure, logged/notified; the
old process never opens another output. PS5 support for this self-replacement,
argument delivery and visible return/relaunch behavior are covered by the user’s
confirmation that all082fixes work. Native handle/thread counts were not independently measured.
There is no manual close/free of WSI resources while it may still scan them out,
no thread jump, exit suppression or repeated JVM creation.
The community API shape is corroborated by the local native-app template's
LoadExec declaration and [Itemzflow's self-relaunch source](https://github.com/LightningMods/Itemzflow/blob/main/itemz-loader/source/main.c).
That reference supported the implementation; the later user report provides console acceptance.

## Checks and console work

Host checks cover the actual native navigation policy under ASan/UBSan,
welcome migration/persistence/horizontal navigation/Settings restore, fresh
launcher models and preserved worlds over repeated selections; current/stale/
rolling shutdown evidence and early/crash/active-SDL rejection; three actual
restart-bridge cycles through a host exec fixture and returned OS-call failure.
Actual draw/JNI fixtures check interpolation, settling, Reduced Motion, native
first frame and close → unmap → release → join ordering. Existing SDL input,
WSI cursor, auth, storage, audio and options preservation checks pass. Host Main
still only reaches its expected missing-native failure; it is not a menu pass.
Full target build/package audits check sources/bytecode, signatures/CRC,
launcher-only dependencies,4096MiB metadata and frozen package preservation.

The original exact082console test plan was:

1. Launch26.3 → Quit Game → native instance library → select and relaunch.
   Repeat at least three times, including quitting after world save. Confirm
   saved worlds/options/downloads and sound/smoothness survive every cycle.
2. Confirm clean shutdown/replacement/resume stages in current-run reports,
   no failure popup on normal Quit, no stuck cursor/frame/audio, and exactly one
   display owner. A rejected LoadExec is a failure requiring logs, not a pass.
3. Check stick navigation on every launcher page, hold/repeat/dead zone,
   D-pad+stick duplication, L1/R1, disconnect/interception and held X on return.
4. Check both checkbox states, horizontal focus, saved preference after app
   reopen, Settings restore and OK's initial focus. Check Reduced Motion,
   animation settling and TV readability.
5. Retest081 in-game cursor/buttons/text picker and the existing download
   completion check. Unsupported versions must remain blocked in the launcher.

Exact081 package/symbols are preserved locally under
`dist/accepted/Client_Controls-01.000.081`; accepted074 and frozen milestones
remain untouched. No console ALL PASS is inferred from photos or host tests.

## Human confirmation after publication

The user reports “yes it all works. all the fixes you added.” This is recorded as
human ALL PASS for the four requested fix areas in
[the additive console record](validation/client082-console-confirmation-2026-10-26.json).
It does not independently enumerate the test-plan cycle count, hardware resource
counts, measured FPS or endurance. Earlier build/host/photo records remain intact.
