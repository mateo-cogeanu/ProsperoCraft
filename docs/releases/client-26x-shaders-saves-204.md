# ProsperoCraft 01.000.204

## Changes

- Add normal launcher support for Minecraft 26.1, 26.1.1 and 26.1.2, both Vanilla and Fabric. These entries now use the regular Play and Ready states.
- Repair shader startup/rendering and Quit Game cleanup for the 26.1.x graphics path, including genuine runtime management support and main-thread SDL finalization.
- Reduce retained immutable archive handles to give world saving more file-descriptor headroom after reported 26.3 save failures. Add a larger read-only handle report for troubleshooting.
- Retain 26.2/26.3 play, launcher uploads, Microsoft sign-in, controller controls, themes and automatic Simple Voice Chat microphone preparation. Use the controller's physical mic button or PS5 system mute.

## Validation and compatibility

The physical tester reports that the exact 204 package works very well and explicitly authorizes this release. Published app bytes are unchanged from that package. Earlier 202 testing explicitly confirmed shader rendering and Quit Game; the implementation is retained in 204. Host and package checks pass, with matching OpenAL corresponding source/relink materials and checksums.

Compatibility still depends on matching game, loader, mod and shader versions. This is functional acceptance, not an exhaustive shader/device/version or endurance matrix. The archive-handle budget is not a universal file-descriptor cap; long-session save behavior and world-creation performance remain areas to test. Already failed saves are not recovered by the update.

Java Edition ownership is required. Original game/mod JARs and game asset objects are not included; the launcher downloads verified originals. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.

## Credits and source

GUI: mihawk-99/PS5_VKHomebrewUI, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: MultiMC/Prism contributors, with original attribution and licenses. Native Java 25/OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft retain their upstream notices and rights. ProsperoCraft is GPL-3.0-or-later. Exact corresponding source and OpenAL relink/replacement materials accompany this release.
