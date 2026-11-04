# Local212 — selectors in place, live themes and icon grid

Title **PPSA99874**, app **01.000.212**. The user reports211 is extremely smooth;
[the feedback](validation/client211-console-feedback-2026-11-04.json) records its
scope and requested UI refinements. Exact211 and earlier packages remain retained.
The verified120 presenter/runtime pin, game resolution, original publisher JARs,
Java image/VM/ZIPbudget8 and resident game groups stay unchanged.121 remains
Vanilla1.21.10/.11 only. No release, prerelease or Store action.

Selectors now open over their original screen, with a short opacity reveal and
background dimming. They no longer slide to another page. Two bounded text-only
resident snapshots retain the parent and optional nested controller-binding menu;
no complete snapshot is placed on a native stack. Outside clicks cancel instead
of activating the dimmed screen. Existing moderate panel sizing and scroll geometry
remain. Returning from a nested picker preserves its parent overlay.

The theme selector is undimmed. Mouse hover or controller focus sets the transient
rendered theme, including the original screen. No setting is written until X/click
confirms. Circle/outside-click restores the saved theme. The existing active
account refresh and startup-notice behavior remain unchanged.

Icon pickers display all32 icons in an8x4 grid, with96px artwork,
128px cell pitch and no icon names. Controller arrows move spatially and pointer
hits share the same geometry. Confirmation alone writes the selected icon;
Cancel preserves it. Grid navigation replaces the old one-item-per-Down fixture
expectation deliberately; publisher/game install policy remains unchanged.

At the user’s request, the Modrinth and CurseForge logos are removed from the
picker, generated web pixels and packaged SVG/PNG assets. Original Amethyst and
Compass artwork replaces IDs4 and25, preserving saved selections and every other
icon ID. Upstream credits for retained artwork remain, with CC0 replacement
attribution. The package audit requires removal of all six inherited logo files
and verifies replacement assets against source.

The prearmed localized adaptive page detent increases native force2 to4 (of8),
retaining travel2–3, release while pressed, neutral rearm, unavailable-direction
freedom, Vibration preference and stale/disable/refusal/shutdown reset. Physical
feel remains pending. A late211 macOS CI failure came from assuming a worker
response within15ms.212 waits for actual state within a bounded deadline, while
refreshing the fixture poll only outside explicit watchdog tests. This changes
test scheduling tolerance, not production haptic timing or the watchdog policy.

The additional whole expanding-area glass quad is removed from card entry/exit.
It darkened that area during the transition. Animated backdrop and existing
control/card surfaces now remain continuous without that extra material pulse.
Exact PS5 disappearance of the reported flash remains a physical check.

## Validation and console check

The19fast/12native lanes cover transient preview/no-save/cancel behavior, invalid
hover rejection, spatial icon navigation/confirmation, all32 native hit rectangles,
existing login focus, game gates and stronger worker packet/lifecycle. Actual
Vulkan previews render dimmed selectors over their parent, all six undimmed theme
previews, the full icon grid and both card-transition directions. Actual pointer
callbacks target every icon. Source-only outside-root runs use a fresh explicit
dependency cache; hosted jobs and target/package audits are recorded separately.

[Validation](validation/client212-launcher-selectors-2026-11-04.json) records the
exact artifact. On212 check selector origin/dimming and nested Back, hover each
theme and Cancel/confirm, all icon rows and pointer/controller selection, stronger
page detents including Vibration off, and card entry/exit without a black flash.
Retest startup/account focus and Play/quit/library return. Keep actual FPS and
hardware acceptance distinct from previews, CI and positive subjective feedback.
