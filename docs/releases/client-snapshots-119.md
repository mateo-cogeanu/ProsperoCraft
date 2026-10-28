# ProsperoCraft 01.000.119

Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime. Sign in, create separate instances, and play Minecraft Java 26.3 with native graphics, audio, DualSense controls and keyboard/mouse support. Java Edition ownership is required.

## Changelog

- Add Minecraft 26.4 snapshots 1–6 alongside the existing 26.3 baseline, with matching version arguments, asset indexes and verified original downloads.
- Keep Show Snapshots off by default. Enable it in Settings to see snapshot versions; existing saved preferences are preserved.
- Add a PS5 OSHI 7 provider for snapshot 6's CPU reporting, using its supported extension API and the existing native CPU information.
- Add genuine native JNA dispatch to fix snapshot 6's early startup crash. Original Minecraft and dependency JARs remain intact.
- Keep future, unreviewed snapshots blocked until their runtime and native interfaces have been checked. Mod and shader support depends on versions available for the selected snapshot.

## Install and compatibility

Install PPSA99874.zip through your usual homebrew workflow or update through ProsperoStore once its catalog deployment completes. Preserve /download0/ProsperoCraft and back up worlds. Client and server use the same title ID, so installing one replaces the other.

The launcher downloads and verifies original Minecraft files on the console; official game JARs and assets are not bundled. Minecraft 26.3 remains the accepted baseline. The tester reports 26.4 snapshots 1–5 functional on build 118 and confirms build 119 works after the snapshot 6 repair. Other downloadable versions are not yet claimed launchable. Use separate snapshot instances and back up worlds before trying newer versions. NeoForge and LAN hosting remain planned.

This release preserves the exact tested build 119 package. Host, native-bootstrap, package and matching OpenAL relink checks pass. Snapshots remain hidden by default, and existing saved choices are retained. Broader endurance, mod combinations and standalone JNA API coverage remain under testing. Microphone capture is not included. No new shader-performance improvement is claimed.

## Credits and source

GUI: **mihawk-99/PS5_VKHomebrewUI**, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: **MultiMC and Prism Launcher contributors**, with original licenses and attribution retained. Runtime: **PS5 Java 25**, with OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. Project thumbnails belong to their respective mod and pack authors; image decoding uses libwebp and STB.

Matching OpenAL corresponding source, relink materials, validation and SHA-256 checksums accompany this release. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
