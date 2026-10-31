# Zink source pin and port design

This directory currently contains **research pins only**, not an implemented
PS5 Zink/EGL platform. The shared Mesa/RADV commit and downloaded source archive
size/SHA-256 are in `sources.json`. No second RADV or Mesa version is adopted.

Read [Phase A](../../../docs/client-26.1-zink-plan.md) before implementing numbered
patches. Use the existing PS5_Mesa tree and one combined RADV/Zink build, preserve
all existing VideoOut patches and graphics provider/constructor ownership, and
keep the 029 OSMesa provider. Port patches, build/export audits and Mesa notices
must be added before any resident Zink group or launcher enablement.

Mesa/Zink sources carry their original MIT notices; the pinned tree contains
`docs/license.rst` and per-file copyright/licenses. The archive stays in ignored
local build storage. No source/binary claim here changes the app's license or
OpenAL corresponding-source/relink obligations.
