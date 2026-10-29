# ProsperoCraft 01.000.121

Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime. Sign in, create separate instances, and play Minecraft Java 26.3 with native graphics, audio, DualSense controls and keyboard/mouse support. Java Edition ownership is required.

## Changelog

- Choose from six launcher color themes in Settings: Forest, Ocean, Amethyst, Rose, Amber and Graphite. Themes change panels, buttons, text, focus indicators and background colors, and your choice is saved.
- All seven Settings bars now share the same size, spacing, rounded corners and focus/press animations, including Keybinds and Color Theme.
- Redesigned the fallback in-game cursor with a vector shape, antialiased edges, a thin outline and a subtle shadow. Its click hotspot is unchanged. This pointer is used when Controlify is absent.
- Background selection remains independent from color themes. Player skins and artwork retain their original colors.
- Snapshots remain off by default; existing explicitly saved preferences are retained.

## Install and compatibility

Install PPSA99874.zip through your usual homebrew workflow or update through ProsperoStore once its catalog deployment completes. Instances, worlds, downloads, settings and saved account data are preserved. Client and server use the same title ID, so installing one replaces the other.

The launcher downloads and verifies original Minecraft files on the console; official game JARs and assets are not bundled. Minecraft 26.3 remains the accepted baseline, with the previously reported 26.4 snapshot support retained. Use separate snapshot instances and back up worlds before trying newer versions. NeoForge and LAN hosting remain planned.

This release preserves the exact build121 package. Target compilation, host Settings persistence, actual Vulkan theme rendering, uniform control geometry, cursor image/lifecycle and package checks pass. Physical PS5 theme persistence, cursor/input alignment and broader endurance remain pending in the validation record; release authorization does not establish a new frozen milestone. Microphone capture is not included. No new shader-performance improvement is claimed.

## Credits and source

GUI: **mihawk-99/PS5_VKHomebrewUI**, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: **MultiMC and Prism Launcher contributors**, with original licenses and attribution retained. Runtime: **PS5 Java 25**, with OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. Project thumbnails belong to their respective mod and pack authors; image decoding uses libwebp and STB.

Matching OpenAL corresponding source, relink materials, validation and SHA-256 checksums accompany this release. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
