# Local210 — full launcher controls, account focus and card opening

Title **PPSA99874**, app **01.000.210**.209 animations received positive feedback,
but lower controls were cut off. [Feedback and causes](validation/client209-console-feedback-2026-11-04.json)
are recorded separately;209/208 exact packages remain retained. Game versions,
original publisher JARs, native groups, runtime pin and VM/ZIPbudget8 policy stay
unchanged. Only1.21.10/.11 Vanilla are enabled;121 Fabric remains deferred.

Signed ZIP SHA-256:
`f89a6b8bb6a784fefa9190d3a777fed17a25e2382a60c375a496324685618435`.
Size127,474,135bytes; exact clean source
`ddeb990264116266382e25c914318f3887b0395c`. Signed integrity and independent
package audit pass. Actual Ubuntu policy/native jobs pass; macOS jobs were queued
when inspected. Later documentation records do not rebuild these candidate bytes.

The209 global content scissor ended at925px, above existing keyboard buttons,
Settings’ last control and the startup notice bottom.210 extends it to1005px and
moves the footer fade below the controls. Existing list-specific clipping stays.
The startup notice is excluded from incoming/outgoing page turns and remains open
when saved-account refresh succeeds. Automatic refresh updates account data while
preserving the current page/tab/selection. Explicit interactive sign-in retains
its return-to-Instances behavior, with startup-notice preservation.

Opening an instance expands that selected card’s bounds into the content viewport,
revealing the actual detail UI inside the growing surface. Other cards remain
behind it during the expansion. It replaces the horizontal transition only for
instance entry; L1/R1 tabs and L2/R2 pagination retain horizontal movement. Startup
notice remains static. Reduced motion snaps all movement immediately.

A short low-force native trigger click is requested on the side used for an
accepted L2/R2 page change, not a rejected page boundary. It uses the existing
consumer native120-byte pad ABI and basic mode2, travel2–3/force2, for55ms. The
existing5ms haptic worker resets both sides after deadline, disable, stale polling,
disconnect or joined shutdown before pad close. API refusal is nonfatal and
attempts a reset; successful hardware reset on refusal is not fabricated. Existing
Vibration preference controls this effect. Exact tactile feel and PS5 behavior
remain pending; this is launcher-only and changes no game trigger policy.

## Verification and physical checks

The saved-login test injects a blocked refresh, navigates to Settings while it is
pending, then asserts page/tab/row preservation; it also verifies a successful
refresh leaves the startup notice visible. Existing rotation, ownership, credential
redaction, revocation and failure checks remain. Native haptic tests cover the
actual worker’s left/right ABI, timeout during stalled UI, disable/shutdown reset,
API refusal and no stale replay. This fixture now uses portable tool discovery
and is required in the native lane (twelve checks). Fast lane remains nineteen.

Actual Vulkan previews render restored Settings/keyboard bottoms, the untransformed
startup notice and growing card/detail checkpoints, alongside existing page/scroll,
pointer refusal and handoff tests. Images were visually inspected. Source-only
outside-root lanes use fresh explicit dependency caches. None of this establishes
PS5 presentation, native trigger feel or physical lifecycle acceptance.

[Validation](validation/client210-launcher-refinements-2026-11-04.json) records exact
package and hosted evidence. On210 check every lower control, notice completion
with a saved account, navigation while automatic login finishes, L1/R1 and L2/R2,
trigger click/disable/release, opening cards in both rows, reduced motion, and
Play/quit/library return. No release, prerelease or Store action.
