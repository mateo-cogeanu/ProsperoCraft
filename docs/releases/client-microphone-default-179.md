# ProsperoCraft 01.000.179

The exact179 package is confirmed on PS5 for automatic SVC microphone input, the
physical mic mute/unmute button, removal of the launcher microphone menu and
leaving/rejoining. Published bytes are unchanged from that tested package.

## Changes

- Add working PS5 system microphone input for compatible Simple Voice Chat,
  following the user's successful178 and179 microphone tests. Prepare input automatically
  when launching gameplay; remove the launcher microphone menu and toggle.
- Use the DualSense physical mic button or PS5 system mute to mute input. The app
  does not unmute the system microphone or change the selected route.
- Retain the input port across healthy SVC stop/reopen cycles, with conservative
  ownership when native cleanup fails. Preserve game/voice output and the socket
  lifecycle repair for leaving worlds.
- Keep Browser uploads in instance settings and Done/Delete at the bottom.
- Include launcher-style browser uploads, case-insensitive auto-hyphen pairing,
  mods/resource packs/shaders/schematics handling and the existing runtime fixes
  developed since167. Original game/mod JARs and saved data stay intact.

## Scope and credits

Minecraft26.2/26.3 Vanilla/Fabric support is retained; actual mod compatibility
depends on matching upstream versions. No universal mod/native-code compatibility,
new supported-version expansion, formal endurance or per-device claim. Exact179
acceptance is the user's functional confirmation, not a formal ALL PASS matrix.

GUI: mihawk-99/PS5_VKHomebrewUI, based on BlackBearReloaded's ps5-homebrew-ui.
Instance icons: MultiMC/Prism contributors with original attribution/licenses.
Runtime: Native Java25/OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. GPL-3.0-or-later
and upstream rights/notices remain unchanged; matching OpenAL corresponding
source/relink material and checksums accompany authorized binary publication.
Java Edition ownership is required. ProsperoCraft is unofficial and not affiliated
with Mojang, Microsoft or Sony.
