# Launcher keyboard and mouse — 01.000.167

The user accepts exact166 (“nice 👌, all works”) after the controller detection and
Controlify handoff repair. The matching166 package, symbols, source/relink archive
and checksums remain preserved locally. No additional endurance duration or
individual rumble/gyro/save measurements are inferred from that report.

167 removes the Fabric26.2 development gate and labels it supported in normal
instance cards, details and creation choices. The published158 app is unchanged.
The old packaging flag is retained for command compatibility but writes no
experimental marker; it does not affect support policy.

The native launcher reads the existing PS5 keyboard/mouse APIs directly while
it owns its display. It uses the existing bounded mailbox, with all Java/model
changes on the JVM caller thread. Controller navigation is preserved. Each mouse
command carries its expected page so queued clicks cannot activate a new screen.
Moving the mouse reveals the cursor; controller navigation hides it. Left click
selects/activates visible controls, right click or Escape goes back/cancels, wheel
moves selection. Arrows navigate; Enter confirms, Tab/Shift-Tab change launcher
pages (or choices in modal lists), F1 opens Controls. Name/search fields accept
US ASCII keyboard text with Shift/Caps Lock, Backspace/Delete, Enter to save and
Escape to cancel. This is not an international keyboard-layout/IME implementation.
The on-screen keyboard also has clickable Backspace, Space, Case, Cancel and Done.

The cursor follows the user’s supplied rounded silhouette, using sampled cubic
Bezier geometry with no pointed corners. It uses vector polygon geometry through the existing Vulkan draw list,
with theme-colored fill, a single light outline. Its rounded top
tracks the logical1080p hit point. No bitmap cursor or new renderer is used.
All six saved palettes apply immediately. Device handles close on launcher exit
before game input ownership. Reconnect/read failure clears held state; keys/buttons
held on attach are blocked until release. Only navigation, text and editing keys
repeat with fresh device packets; confirm/cancel never repeat.

The native event queue remains bounded64, device packets16 per port, four ports
per kind. No raw typed text is logged. Existing original game/mod JARs, SDL
Controlify isolation, runtime pin and game input mappings are preserved.

Validation results and exact package checksums are recorded in
[the validation record](validation/client167-launcher-desktop.json).
Physical167 checks still required: six-theme cursor visibility, click/scroll,
name/search typing/edit/save/cancel, keyboard-only navigation, controller/mouse
switching, USB reconnect, then Vanilla26.2/26.3 and Fabric26.2/26.3 Controlify input
handoff after launch. No release or Store update until the user approves this build.


## Acceptance and publication

The user subsequently accepted exact167 ("Im Happy!, lets release!!! its so polished!")
and requested release. The exact tested ZIP was published without rebuilding.
[Publication record](validation/client167-store-publication-2026-10-30.json).
This supersedes the release hold above for exact167; individual measurements and
long-session endurance were not supplied.
