# Local211 — whole-launcher120 target and UI refinement

Title **PPSA99874**, app **01.000.211**. [210 feedback](validation/client210-console-feedback-2026-11-04.json)
confirms the login fix while requesting better haptics, menu proportions, smooth
card opening/closing and120FPS across the launcher. Exact210 and earlier packages
remain retained.121 support stays Vanilla1.21.10/.11; all121 Fabric remains deferred.
No game JAR, game resolution, Java module image, VM/ZIPbudget8 or resident game
native-group policy changes. This is a local hardware-test candidate, not a release.

## Presentation and FPS

The launcher previously imposed a33ms redraw gate (about30FPS) and used the default
60Hz CPU presenter.211 redraws all launcher views and animated backdrops on every
presenter opportunity. It explicitly opts into the reusable runtime presenter at
commit64fe7c70821dfc94aa3566703011b751a86d2900. The existing manifest declares0x40;
the presenter queries native output support, requests mode15 on its own handle,
then measures six vblank intervals. Only a near120Hz median admits that mode.
Unsupported/refused/failed/slow output retains or restores60Hz. Restore failure
forbids game handoff; the old default presenter behavior remains unchanged for
other callers. No additional display owner or frame queue is introduced.

Opt-in fast tiling copies four adjacent RGBA pixels at once with the same layout,
pitch/bounds/refusal behavior. After unchanged full initial buffer publication,
subsequent frames copy8,847,360bytes of actual tiles instead of the unused16MiB
allocation tail. All allocations, two-buffer presentation and cleanup ownership
remain. The object replaces the old renderer exactly once; runtime implementation
and its build tool stay in the runtime repository, with a verified consumer pin.

**120FPS is a target, not a physical pass.** GPU draw/readback, CPU tiling/publication
and presentation still cost time. Native reports expose requested/selected Hz,
measured vblank period and two-second submitted FPS plus average draw/publish/wait
cost. Actual display refresh and delivered performance require the exact211 PS5
run. A120Hz output alone does not establish120rendered FPS.

## Menus, cards and adaptive triggers

Selection menus now fit their contents with moderate breathing room:600px minimum
width,64px row pitch,28px text and24px vertical panel padding, growing to fit longer
labels up to1100px. Theme/loader/resolution lists shrink vertically to their option
count; longer lists retain clipped continuous scrolling and a proportional thumb.
Measured text/title and the model’s longest label determine width; pointer hits use
the identical geometry and visual scroll position. Focus rings retain clip margin.

Instance entry and exit share the selected card’s bounds. Detail controls expand
in, and Back collapses them into the same card, retaining its library selection/page.
Library/detail opacity curves avoid a half-strength overlap of both text layouts.
A fading glass material uses the live animated backdrop; no opaque fixed-color
plate is swapped away at completion. Tabs and pagination retain their horizontal
motion. Startup notice and automatic-login focus fixes remain. Reduced motion
snaps transitions; whole-launcher presentation remains paced by the presenter.

Available L2/R2 page directions preload a light native mode2 detent in travel
zones2–3 with force2. It is localized adaptive feedback, not uniform resistance.
The pressed side releases as its button registers, stays free while held and
rearms only after release; unavailable directions and other menus remain free.
Thus hardware is ready before the page turn rather than warming up afterward.
The existing Vibration preference,250ms stale-poll watchdog, opt-out/disconnect/
joined shutdown reset and nonfatal API refusal remain. Physical feel/reset still
requires testing. No game adaptive-trigger policy changes.

## Checks and console run

The19fast/12native lanes include preserved automatic-login/notice behavior, card
return selection, menu geometry/hit tests, card opacity/bounds and the actual haptic
worker’s prearm/press/hold/release/boundary/stall/disable/refusal/shutdown controls.
Real Vulkan previews cover medium3/5/6-option menus and forward/reverse card frames,
alongside old page/scroll/mailbox/handoff checks. Runtime actual refresh policy,
old/fast full-pixel blit/padded/invalid-input ASan/UBSan controls and target presenter
build pass. Host VideoOut responses are fixtures, not PS5 FPS evidence.

[Validation](validation/client211-launcher-120-2026-11-04.json) records exact build,
package, source-only and hosted results. On211 check the display’s refresh readout,
all launcher screens/backgrounds and both transition directions, moderate menu
spacing, ready/press/hold/release adaptive detent, page boundaries, Vibration off,
static notice and automatic-login focus. Then test Play/quit/library return for
known-working1.21.10/.11 and26.x. Retrieve current native reports by FTP if FPS stays
low; selected output and measured draw/publish/wait costs distinguish causes.
Shader/endurance/exact-release gates remain; no release/prerelease/Store action.
