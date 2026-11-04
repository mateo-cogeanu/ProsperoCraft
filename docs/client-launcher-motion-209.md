# Local209 — launcher page turns and continuous lists

Title **PPSA99874**, app **01.000.209**. The user reports208 works amazingly and
requests launcher navigation/animation improvements. [The208 feedback](validation/client208-console-feedback-2026-11-04.json)
records its scope;208 remains retained byte-for-byte. Game versions, native groups,
runtime pin, original JARs, resolution path and VM/ZIPbudget8 policies remain208.
Only1.21.10/.11 Vanilla are enabled; all121 Fabric remains deferred.

Final signed ZIP SHA-256:
`f0fedac2a287e8df8d72834e8f9acf13e488bcc3f9192597cfa86b6b435b5c07`.
Size127,473,739bytes,8,018bytes above208. Exact clean source is
`bf66e60c6691f722e1c5dfbc15a44385d7742cd9`. Signed integrity and independent
package audit pass. A pre-handoff209 draft is separately retained by checksum;
use this final checksum for the physical test.208 was not rebuilt or replaced.

## Navigation and presentation

The instance grid keeps Up/Down within the current page’s two rows. Up from its
first row goes to the top bar; Down at the bottom stays there. L2/R2 select previous/
next instance pages, preserving the slot where available. L1/R1 retain top-tab
navigation with the same directional page-turn animation and a gliding active-tab
underline, including controller wraparound. Horizontal traversal still walks the cards in order. Rounded vector
chevrons appear at the middle left/right edges only when that page exists; they
use the current theme and accept pointer clicks. L2/R2 also page content results
and the controls guide. The instance footer names both button pairs.

A280ms eased horizontal transition draws outgoing and incoming content together
under a fixed header/footer/background. It replaces the old vertical entrance.
Side arrows and the page indicator remain fixed. Independent previous/current
card grids prevent rebuilding both sets of items every animation frame. Snapshot
and32-row list-cache storage are bounded and resident; field exchange swaps arrays
in place, avoiding a large automatic snapshot. Modal and game handoff ownership
remain in their existing components. Pointer content clicks are blocked during
a page turn so a moving control cannot activate its destination accidentally.

Dropdowns and the controller-binding list now keep a continuous visible range,
advancing one row as selection reaches an edge. Clipped rows slide through a180ms
retargetable viewport with a proportional theme-colored thumb. Guard rows and the
bounded native cache retain neighboring text during animation. Pointer hit testing
uses the visual scroll position; keybinding dropdown return restores its caller’s
scroll range. Left/Right move one list item instead of replacing a whole block.
The existing Reduced motion setting snaps page/list movement immediately.

## Evidence and physical check

Local19fast and11native checks cover existing launcher policy plus two-row
navigation on multiple pages, trigger/side-arrow page selection, single-row list
ranges and actual native tween timing/retarget continuity/reduced-motion behavior.
Source-only outside-root19checks use an empty explicit dependency cache. Manual
Vulkan previews render page-turn checkpoints, clipped fractional scrolling and
both side chevrons in all six themes through the actual toolkit/lavapipe pipeline;
they also retain mailbox/JNI/presentation-failure and cleanup controls. Host
VideoOut calls are fixtures; no host image establishes PS5 smoothness or input.

[Validation](validation/client209-launcher-motion-2026-11-04.json) records build,
package and hosted evidence separately. On the physical209 build, create enough
instances for multiple pages; check Down reaches the second row before paging,
L2/R2 both directions, partial last page, arrows and six themes. Open long version/
key lists and hold Down/Up, use wheel/keyboard/pointer selection, confirm/cancel,
and toggle Reduced motion. Check launcher responsiveness and Play/quit/library
handoff for the existing1.21.10/.11 and26.x paths. No release/Store action.
