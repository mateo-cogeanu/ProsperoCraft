# Color themes and pointer candidate 01.000.121

Settings now offers Color Theme with Forest (the existing default), Ocean,
Amethyst, Rose, Amber and Graphite. The choice applies immediately and is stored
in the existing library settings. Missing or invalid theme preferences use
Forest. Cancel leaves the saved choice intact. Background selection remains a
separate preference.

The consumer palette covers launcher panels, text, controls, focus indicators,
toggles, progress and procedural background colors. It does not recolor texture
assets or player skins. Warning colors retain their meaning and Done retains
its green positive fill. The vendored UI toolkit is unchanged.

Every bar in the main Settings screen uses the same two-line control layout:
1080 by 86 logical pixels, 10 pixel gaps, matching corners and focus/press
behavior. This includes Input & Controller Keybinds and Color Theme. The Java
model and native mailbox carry the same additional theme field.

The fallback in-game VideoOut pointer uses a vector polygon with a white arrow
head, an inward notch, a diagonal stem, thin dark outline and subtle shadow.
It rasterizes with 4x4 subpixel samples for smooth edges only when its image
changes, using the hardware cursor image format. Its upper-left tip remains the
hotspot. Existing WSI ownership, cursor visibility/position, retained 64 KiB
allocation, double buffering and keyboard glyph behavior are preserved.

Checks include all six selections through the actual Java Settings model,
persistence/cancel/legacy/invalid preferences and unchanged world bytes;
actual Vulkan rendering of every palette and uniform bar geometry; native
JNI/mailbox/display lifecycle fixtures; cursor image topology and lifecycle
under ASan/UBSan; target build/signing and packaged source/native audits.
The storage fixture now counts the existing Add Instance tile separately from
its one saved instance, and checks the saved instance title and world bytes.

Physical PS5 checks remain pending: select/reopen each theme, use settings and
content screens, verify readable focus/animations and equal bar sizes on TV,
and check pointer appearance/click alignment in menus without Controlify.
No new Store release is requested by this change; public 120 and earlier frozen
packages remain preserved. Runtime source is unchanged.
