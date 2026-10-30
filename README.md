<p align="center"><img src="docs/readme-banner.svg" alt="ProsperoCraft: Minecraft Java on PS5" width="1200"></p>

# ProsperoCraft

**Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime.**

Download Minecraft on your console, keep separate instances for worlds and mods, and play with DualSense controls, native Vulkan graphics and game audio. ProsperoCraft includes Microsoft sign-in, a Modrinth content browser, controller remapping and six saved launcher themes.

**[Download 01.000.158](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.158)** · [Latest release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/latest) · [Changelog](CHANGELOG.md) · [Report an issue](https://github.com/mateo-cogeanu/ProsperoCraft/issues/new/choose)

ProsperoCraft handles Minecraft installation, accounts, input and game integration. Its [Native Java 25 Runtime](https://github.com/mateo-cogeanu/ps5-java25-homebrew) is maintained separately. Official Minecraft game JARs and asset objects are downloaded and verified from the publisher, rather than bundled with the app.

## What can I play?

Release **01.000.158** queries PS5/Pro hardware once in the native launcher and passes the cached model to the unchanged compact F3 CPU/GPU labels. [Implementation and pending console checks](docs/client-launcher-hardware-158.md). Published at the user’s explicit request; exact-console detection and regression checks remain pending.

The latest public release is **01.000.158**. Earlier builds have positive PS5 playtests; exact158 hardware detection, regression, audio and long-session checks remain pending.

| Minecraft version | Vanilla | Fabric |
| --- | --- | --- |
| **26.3** | Established playable PS5 baseline, including game audio and server joining. | Released, with positive console feedback. Mods still need individual compatibility checks. |
| **26.2** | Available in 158; working Vanilla play reported on development 124. | **Coming soon. Launch is blocked in 158.** Development reached the menu and Controlify input, but world, audio and stability validation is incomplete. |
| **26.4 snapshots 1–6** | Available; positive console feedback on 118/119. Use separate test worlds. | Selectable when matching loader/mod versions exist; snapshot-specific Fabric, Controlify and mod compatibility is not established. |
| **Other versions** | Downloadable 26.x entries may appear, but Play is blocked for versions outside the set above. | No additional compatibility claim. NeoForge is not enabled. |

Local development build **159** offers an explicitly labeled Fabric 26.2 test path and a scoped OpenAL discovery repair. It is **not a public support change or release**; the first exact159 Fabric 26.2 console run crashed during loading with a Render-thread XO violation; sound, Controlify features and world save/reload remain unvalidated. [Development evidence and console test sequence](docs/client-fabric262-development-159.md).

Snapshots are **hidden by default**. Enable **Settings → Show Snapshots** to list them; explicit saved preferences are retained. Future snapshots are not enabled automatically. See the [snapshot guide](docs/client-snapshots-118.md) and [119 console acceptance](docs/validation/client119-console-acceptance-2026-10-28.json).

Compatible displays can use output up to 120 Hz, with a 60 Hz fallback. A tester reported 119 FPS on build 097; release 100 received positive smoothness feedback. This is not a constant 120 FPS guarantee or fully uncapped presentation. [High-refresh details](docs/client-high-refresh-097.md).

Separate [Fabric and Paper server downloads](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Fabric-Paper-v01.000.108) have positive console playtests and their own [setup guide](docs/releases/fabric-paper-108.md). Server and client version counters are independent; server lifecycle and two-hour endurance checks remain incomplete.

## Install or update

You need a PS5 with a working homebrew app installation/launch workflow, an internet connection for initial downloads and sign-in, and a Microsoft account that owns Minecraft Java Edition with a Java profile for full-game play.

1. Back up important worlds before updating. Preserve **`/download0/ProsperoCraft`**, which holds instances, downloads, settings and saved account data.
2. Open the [latest release](https://github.com/mateo-cogeanu/ProsperoCraft/releases/latest) and download **`PPSA99874.zip`** from Assets. `SHA256SUMS` is available beside it for verification.
3. Extract the complete **`PPSA99874`** folder and install or replace the app through your existing homebrew workflow. Keep all files together. Launch ProsperoCraft from your homebrew launcher.
4. Follow the first-launch steps below. Existing instances and cached downloads are retained when their data directory is preserved.

The app requests 4 GiB of storage. **Client and server share title ID PPSA99874: installing one replaces the other.** Keep the server package separately if you want to reinstall it. ProsperoStore availability can lag GitHub releases. [Release notes and validation limits](docs/releases/client-native-compatibility-153.md).

### First launch

1. Open **Account / Sign in**. Scan the QR code or open the Microsoft link shown on screen on another device, then enter the displayed code and approve sign-in.
2. Return to ProsperoCraft. Full-game launch checks your Minecraft Java entitlement and profile. Successful sign-in opens **Instances**.
3. Select the **+** card. Choose a version, **Vanilla** or **Fabric**, a name and an icon. For a first playtest, use Vanilla 26.3.
4. Select the instance, choose **Download & Play**, and let the launcher download and verify its game files. Read the PLAY controls guide, confirm it, and create a new world or join a compatible server.

Updating from a build before 120 requires **one fresh sign-in**: release 120 switched to ProsperoCraft's approved Microsoft application. Later launches can restore saved sign-in; sign out clears saved credentials. Live sign-in and restoration with the new application still need broader PS5 validation. See [account migration and troubleshooting](docs/client-auth-approved-2026-10-29.md).

Instance Settings offers rename, icon selection, duplication and deletion. **Deleting an instance permanently deletes its worlds, mods and settings after confirmation; there is no Undo.** Duplicate Instance makes an independent copy for experiments. Settings also offers color themes, animated backgrounds, Reduced Motion and a resolution dropdown; actual display modes depend on the connected screen.

## Controls

Use the controller in the native launcher: **L1/R1** changes tabs, **D-pad or left stick** moves focus, **X** selects and **Circle** goes back. **OPTIONS** opens the full controls guide; a shorter guide appears before Play.

| Default fallback controls | Action |
| --- | --- |
| Left stick / right stick | Move / look |
| X / Circle / L3 | Jump / sneak / sprint |
| R2 / L2 | Mine or attack / use or place |
| Triangle / L1 / R1 | Inventory / previous hotbar slot / next hotbar slot |
| Right stick in game menus | Move the pointer; X or R2 clicks, L2 right-clicks |
| L3 in game menus | Open the on-screen text keyboard after selecting a text field |

These mappings use Minecraft's default keybinds. Change fallback gameplay bindings in **Settings → Input & Controller Keybinds**. The in-app OPTIONS guide is the current full reference; [the input guide](docs/client-fabric-input-105.md) explains remapping and hardware limits.

**Controlify** and required dependencies are installed once during setup of new Fabric instances. Existing instances and later uninstalls are respected. The fallback adapter hands over when a mod opens a controller. SDL3 integration and controller/haptic feedback are implemented, but adaptive-trigger feel, reconnect behavior and each game/mod version still need testing. [Controlify defaults](docs/client-default-controlify-unicode-115.md) · [Trigger limitations](docs/client-buttons-triggers-117.md).

Physical **keyboard and mouse input is implemented for gameplay**, with positive PS5 keyboard feedback. The native launcher remains controller-operated. Text input uses US ASCII; international layouts/IME, Bluetooth combinations and broader mouse/reconnect behavior are not fully validated.

## Mods, shaders and resource packs

Open **Instance Settings → Mods, Shaders or Resource Packs** to browse Modrinth, search, select downloads and use **Download All**. The launcher verifies downloads, resolves required dependencies and can upgrade managed dependencies when required. **Installed** lists show what is present and offer per-file **Uninstall** with confirmation. Install only content matching the instance's game version and loader. [Content guide](docs/client-fabric-modrinth-103.md) · [Dependency handling](docs/client-dependency-updates-111.md).

- **Shaders:** the game uses Vulkan. Use the Vitrail shader path; current Iris requires OpenGL and is blocked before launch. The earlier software OpenGL probe does not establish a hardware OpenGL game renderer. Pack compatibility and performance vary; no general shader-FPS target is validated. [Iris explanation](docs/client-iris-vulkan-110.md) · [Performance findings](docs/client-performance-investigation-117.md).
- **Distant Horizons:** a PS5 integration exists, but rendering and persistence compatibility remain work in progress. It is not a generally supported mod. [Integration and limits](docs/client-native-input-storage-112.md).
- **Resource packs:** browsing, verified downloads, safe Unicode filenames and uninstall are implemented. A successful download does not prove a pack renders correctly on every supported version.

NeoForge and `.mrpack` imports are not available. Fabric support does not imply that every desktop mod, native dependency or shader pack works on PS5.

## Known limitations and troubleshooting

- **LAN hosting is deferred.** Joining servers has earlier PS5 confirmation; Open to LAN is not established working.
- **Save/reload improved after the file-handle repair**, with positive world play/reload feedback on 114. Broader world lifecycle, long sessions and exact 153 regressions still need testing. Back up important saves. [World-access repair](docs/client-world-handles-114.md).
- **Performance and device coverage remain under testing:** shader frame times, audio across reloads, resolution/input alignment, account recovery, reconnect and repeated quit/relaunch are not exhaustively validated.
- **Microphone capture is not implemented.** Adaptive-trigger approximations are not identical to full native per-zone profiles.

If Play says Coming soon, compare the **version and loader** with the compatibility table above. For an Iris warning, uninstall Iris through Installed before retrying. For account problems after an older update, use a fresh sign-in. Report persistent problems through the [bug, mod or shader issue forms](https://github.com/mateo-cogeanu/ProsperoCraft/issues/new/choose), including app/game/loader/content versions and steps to reproduce. Working mods and shaders are useful reports too. Keep account tokens and private logs out of public reports.

## Roadmap

These are directions, without delivery dates or a promised order:

- **More playable versions:** complete Fabric 26.2 world/audio/stability testing and validate further 26.x releases and snapshots individually.
- **Smoother shader play:** measure frame-time costs and improve compatible shader workloads while retaining visual quality. The shader path already exists; consistent performance remains open.
- **More mod choices:** add NeoForge instance support and `.mrpack` imports so compatible mod setups are easier to install.
- **Faster access to favorites:** revisit the deferred Home page for saved worlds and servers. A [development 094 prototype](docs/client-home-library-094.md) exists; it was omitted from published builds.
- **Launcher atmosphere:** add custom menu music by CogiArt.

LAN hosting, microphone capture and fully uncapped presentation remain deferred or unimplemented. Older Minecraft support would also need Java 21/17 from the [separate runtime project](https://github.com/mateo-cogeanu/ps5-java25-homebrew) and game-specific compatibility work; those runtimes are not bundled here.

### Completed milestones

The table links each capability to its first public release. Initial development builds are noted where useful; three-digit build numbers abbreviate 01.000.xxx. Console limitations above still apply. See the [changelog](CHANGELOG.md) for the full milestone archive.

| Feature | First available version | What it enables |
| --- | --- | --- |
| Minecraft menu, then playable worlds | [Menu 062](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Menu-v01.000.062); [world 065](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_World-v01.000.065); [playable 066](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/Client_Playable-v01.000.066) | The first menu, world entry and responsive gameplay checkpoints; 066 did not yet have audible sound. |
| Native instance launcher and resolution selection | [Development 079](docs/client-instances-079.md) → [01.000.082](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.082) | Separate instances, resolution choices and quit/relaunch. Audio was confirmed on development 067 before this release. |
| Vulkan launcher and authenticated play | [Development 087](docs/client-toolkit-087.md) / [090](docs/client-temp-gametest-090.md) → [01.000.096](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.096) | Animated Vulkan UI and owned-account play; saved sign-in began in 091, permanent deletion in 094, both first public in 096. |
| CPU reporting and launcher vibration | [Development 086](docs/client-shared-fixes-086.md) / [089](docs/client-vibration-089.md) → [01.000.096](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.096) | Actual CPU identity/count, centered tab labels and optional launcher vibration. Expanded resolution dropdowns followed in development 091, also first public in 096. |
| High-refresh output | [Development 097](docs/client-high-refresh-097.md) → [01.000.100](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.100) | Up to 120 Hz on compatible displays; 098 remains a draft, and 100 delivers the accepted smoother policy. |
| Custom player skins and clearer game-menu controls | [01.000.101](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.101) | Owned skins, cursor-only menu selection and clearer account/navigation controls. |
| Fabric and Modrinth content | [Development 103](docs/client-fabric-modrinth-103.md) → [01.000.108](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.108) | Content browsing and dependency repair; installed lists began in 106, uninstall in 107, both first public in 108. |
| Remapping, physical input and Controlify integration | [Development 105](docs/client-fabric-input-105.md) / [106](docs/client-input-audio-installed-106.md) → [01.000.108](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.108) | Saved fallback bindings and keyboard/mouse gameplay; SDL3 integration for Controlify, with hardware/version limits above. |
| World-access repair, default Controlify and instance copies | [Development 114](docs/client-world-handles-114.md) / [115](docs/client-default-controlify-unicode-115.md) / [116](docs/client-duplicate-triggers-116.md) → [01.000.117](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.117) | Improved save/reload, one-time controller-mod setup and independent Duplicate Instance copies. |
| Six supported 26.4 snapshots | [Development 118](docs/client-snapshots-118.md) → [01.000.119](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.119) | Snapshots 1–5 worked on 118; 119 repaired snapshot 6. Visibility stays off by default. |
| Approved ProsperoCraft sign-in | [01.000.120](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.120) | Own approved Microsoft application and app-bound saved credentials; requires fresh sign-in from older builds. |
| Six color themes | [01.000.121](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.121) | Six saved palettes and a smoother fallback pointer; broader PS5 persistence/input checks remain pending. |
| Vanilla 26.2 | [Development 124](docs/client-26.2-vulkan-handoff-124.md) → [01.000.153](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/01.000.153) | Vanilla 26.2 play; Fabric 26.2 remains held. |

## Credits and license

- **GUI:** [Mihawk's PS5_VKHomebrewUI](https://github.com/mihawk-99/PS5_VKHomebrewUI), based on [BlackBearReloaded's ps5-homebrew-ui](https://github.com/blackbearreloaded/ps5-homebrew-ui).
- **Instance artwork:** [MultiMC](https://github.com/MultiMC/Launcher) and [Prism Launcher](https://github.com/PrismLauncher/PrismLauncher) contributors. Original authors and artwork licenses are retained in the [icon attribution](assets/launcher-icons/attribution.json). [Project artwork and provenance](assets/branding/README.md).
- **Runtime and native components:** [PS5 Java 25](https://github.com/mateo-cogeanu/ps5-java25-homebrew), OpenJDK, Mesa/RADV, SDL, LWJGL, OpenAL Soft and other upstream contributors. Mod and pack thumbnails belong to their authors; image decoding uses libwebp and STB.

Original ProsperoCraft code is **GPL-3.0-or-later**, copyright © 2026 mateo-cogeanu, ProsperoCraft. See [LICENSE](LICENSE) and [NOTICE](NOTICE) for redistribution, source and upstream notices. Upstream components and artwork retain their own terms. Releases include matching OpenAL corresponding source/relink materials and checksums.

Minecraft files and third-party trademarks are not relicensed by this project. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.

Frozen source snapshots now live in the [source history archive](https://github.com/mateo-cogeanu/ps5-homebrew-history). Active builds stay here; original release downloads and tags are unchanged. See [source organization and build verification](docs/source-organization.md).
