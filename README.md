<p align="center"><img src="docs/readme-banner.svg" alt="ProsperoCraft — Minecraft Java on PS5" width="1200"></p>

# ProsperoCraft

**Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime.**

Download Minecraft on your console, manage separate instances and play with DualSense controls, native graphics and game audio. Minecraft gameplay and account login have been tested on PS5. The high-refresh update reached 119 FPS in console testing; extended endurance remains under testing.

**[Download 01.000.117](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.117)** · [Install and release notes](docs/releases/client-controls-worlds-117.md) · [Changelog](CHANGELOG.md)

## Downloads

| Release | Includes |
| :--- | :--- |
| [**ProsperoCraft 01.000.117**](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.117) | Instance duplication, consistent animated controls, default Controlify, world-handle repair and improved dependency queues. |
| [**ProsperoCraft 01.000.108**](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.108) | Fabric, Modrinth content, dependency repair, input controls, larger icons and Uninstall. |
| [**ProsperoCraft 01.000.101**](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.101) | Clearer tabs, correct account actions, dropdown resolution, cursor-only game menus and custom player skins. |
| [Previous high-refresh release 01.000.100](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.100) | Smoother gameplay, up to 120 Hz output, 60 Hz fallback and the correct in-app version. |
| [Previous authenticated launcher 01.000.096](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.096) | Authenticated-play experiment, Vulkan launcher, instance downloads, saved sign-in, controller keyboard and refreshed presentation. |
| [Previous launcher 01.000.083](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.083) | Preserved Demo release and fixed 1080p baseline. |
| [Fabric / Paper servers 01.000.108](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Fabric-Paper-v01.000.108) | Separate server builds with positive console playtests; extended lifecycle/endurance checks pending. |

Install the release's **PPSA99874.zip** using your normal homebrew workflow. The launcher downloads and verifies original publisher files on the console; official Minecraft game JARs and asset objects are not bundled. A valid Java Edition entitlement/profile is required for authenticated full-game play.

The client and server share **PPSA99874**: installing one replaces the other. Back up your worlds and preserve `/download0/ProsperoCraft` when updating. Storage remains 4 GiB; existing instances and cache are retained. Instance deletion is permanent after confirmation, including that instance's worlds—there is no Undo for new deletions.

Development117 arranges Mods, Shaders, Resource Packs and Duplicate Instance in a 2×2 grid and shares animated Settings-style buttons across instance/content controls. It adds a trigger-travel fallback for the native per-zone effect rejection observed in116. Host checks pass; physical adaptive triggers and launcher behavior require PS5 testing. See [development notes](docs/client-buttons-triggers-117.md). Release117 is published; the Store update is submitted in [PR896](https://github.com/darkxex/ps5-homebrew-catalog/pull/896). The user confirms the Store update was accepted, reinstalled and works, with a second user also reporting success.

## Current status

- **26.3 is the playable native baseline.** Other 26.x versions and snapshots can be downloaded but are not claimed launchable.
- **Login and gameplay are console-tested.** The existing experimental authentication flow remains in use; a valid Java Edition entitlement/profile is required.
- **High-refresh gameplay:** up to 120 Hz output on compatible displays, with 119 FPS reported on build097. Release100 has accepted PS5 feedback for much smoother gameplay; sustained frame-time and long-session testing remain incomplete.
- **Native GUI:** animated backgrounds, instance icons, clear active tabs, state-aware account actions, dropdown resolution and optional vibration. Successful sign-in opens Instances; new libraries hide snapshots by default.
- **Controls:** temporary DualSense keyboard/mouse mapping, cursor-only game menus, in-game keyboard and PLAY/OPTIONS guides. Full Controlify support remains planned.
- **Known limits:** LAN hosting is deferred; save/reload, resolution combinations, reconnect/lifecycle regressions and extended endurance still need broader testing. Earlier server joining was confirmed.

Development continues on `main`, which contains the merged authenticated game-test work. The merged `Temp_gametest` and `codex/demo` branches have been retired. Release101 retains the existing `temp_gametest` package channel. The exact096 and097 packages remain preserved. Older Demo history, all frozen validation snapshots and public releases remain intact. Home/favorites are deferred; this release opens Instances, with Settings and Account beside it.

## Reporting issues

Use the [issue forms](https://github.com/mateo-cogeanu/ProsperoCraft/issues/new/choose) for bugs, mod compatibility and shader pack reports. Working mods and shaders are worth reporting too.

## Credits

- **GUI:** [Mihawk's PS5_VKHomebrewUI](https://github.com/mihawk-99/PS5_VKHomebrewUI), based on BlackBearReloaded's ps5-homebrew-ui. Thanks for the native Vulkan UI toolkit.
- **Instance icons:** [MultiMC](https://github.com/MultiMC/Launcher) and [Prism Launcher](https://github.com/PrismLauncher/PrismLauncher) contributors. Original artwork credits and licenses are retained in [the icon attribution](assets/launcher-icons/attribution.json).
- **Java runtime:** [PS5 Java 25](https://github.com/mateo-cogeanu/ps5-java25-homebrew), maintained separately from Minecraft integration.
- OpenJDK, Mesa/RADV, SDL, LWJGL, OpenAL Soft and other upstream contributors retain their respective notices; see [NOTICE](NOTICE).

## Roadmap

### Done

- [x] Screen resolution changing.
- [x] Launcher menu with instances, settings and instance management.
- [x] Microsoft login for official Minecraft downloads.
- [x] Delete instance.
- [x] Centered top-bar button text.
- [x] Controller vibration.
- [x] Unlock the 60 FPS cap on compatible 120 Hz displays — 119 FPS reported in PS5 testing. Fully uncapped presentation remains future work.
- [x] Fabric instances and Modrinth mods, shaders and resource packs.
- [x] SDL3 integration for Controlify.
- [x] Keyboard/mouse gameplay support.
- [x] Controller remapping.

### Coming next

- [ ] Higher-resolution crafting-table icon.
- [ ] All Minecraft 26.x releases, including snapshots.
- [ ] NeoForge instance support — coming soon.
- [ ] Performance sufficient for shaders.
- [ ] Custom menu music by CogiArt.
- [ ] `.mrpack` imports.
- [ ] JVM 21 for broader Minecraft support.
- [ ] JVM 17 for even broader Minecraft support.
- [ ] Custom AMD Ryzen Zen 2 8C/16T CPU identification.
- [ ] Home menu.
- [ ] Themes.

Broader account-refresh, save/reload and lifecycle validation continues alongside
these features. Client mod-loader support is separate from the existing server
milestones; each game/loader version needs its own validation.

## License

Original ProsperoCraft code is **GPL-3.0-or-later**. Copyright © 2026 mateo-cogeanu — ProsperoCraft. Preserve applicable notices and provide corresponding source when redistributing covered work. Upstream components and artwork keep their own licenses. Releases include matching OpenAL source/relink materials and checksums.

Minecraft files and third-party trademarks are not relicensed by this project. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
