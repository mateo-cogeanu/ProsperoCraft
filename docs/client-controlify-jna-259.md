# Local build 259 · 1.21.x Controlify startup and removable defaults

Build 258's 1.21.11 Fabric game log shows Controlify 3.0.1 LTS and ends at
“Pre-initializing Controlify.” The game session with bare Fabric reached its
startup path. The recovered native report is from a later launcher-only
session. The fatal instruction and exact pre-initialization operation are
unconfirmed. Original Controlify calls its optional HID4Java service during
pre-initialization, before SDL initialization. The inspected HID4Java bundle
has no PS5 native binary.

Build 259 gives 1.21.x JNA one owner. Fabric delegates its original JNA and
JNA Platform JARs to the game launch class loader, alongside LWJGL and OSHI.
The LTS mod's own `controlify.debug.sdl_natives_override` selects the
resident SDL3 handle. For a selected 1.21 Fabric instance with Controlify, the
startup check calls the real SDL version function via JNA and compares the
three Controlify event symbols with the existing scoped FFM lookup. The
`PS5_CONTROLIFY_JNA` checkpoints distinguish JNA bootstrap, SDL library
lookup and verified symbol resolution from later mod pre-initialization.
The app uses the original game and mod JARs.

Fabric setup installs Controlify and its required dependencies by default.
Existing instances whose default setup was pending also get this on online
Play. A copy the user installed themselves is kept. Uninstall through the
instance's Mods → Installed screen records the removal with the mod receipt,
including when initial setup had been interrupted. Users can install
Controlify again manually.

On PS5, retry the same 1.21.11 Fabric instance and check that Controlify
reaches the title screen, takes over from built-in controls, works in a world,
and returns to the launcher on Quit Game. Check removal and Repair Download
on a fresh instance. Physical startup and controller behavior are pending.

See the [build validation](validation/client259-controlify-jna-2026-11-07.json)
for the exact package and host checks.
