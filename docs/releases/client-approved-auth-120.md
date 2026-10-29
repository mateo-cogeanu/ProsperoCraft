# ProsperoCraft 01.000.120

Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime. Sign in, create separate instances, and play Minecraft Java 26.3 with native graphics, audio, DualSense controls and keyboard/mouse support. Java Edition ownership is required.

## Changelog

- Previous releases used Mojang's application client ID for Microsoft sign-in. ProsperoCraft now uses its own approved Microsoft application.
- Everyone must sign in again once after updating. Refresh tokens issued to the old application will not be reused with ProsperoCraft's new client ID.
- New saved logins are encrypted and bound to ProsperoCraft's application ID. Saved-login restoration and refresh-token rotation continue after the fresh sign-in.
- Microsoft sign-in, Xbox/XSTS authentication, Minecraft ownership and profile checks remain in place. Instances, worlds, downloads and settings are preserved.
- Snapshots remain off by default; existing explicitly saved preferences are retained.

## Install and compatibility

Install PPSA99874.zip through your usual homebrew workflow or update through ProsperoStore once its catalog deployment completes. Preserve /download0/ProsperoCraft and back up worlds. Client and server use the same title ID, so installing one replaces the other.

The launcher downloads and verifies original Minecraft files on the console; official game JARs and assets are not bundled. Minecraft 26.3 remains the accepted baseline. The tester reports 26.4 snapshots 1–5 functional on build 118 and confirms build 119 works after the snapshot 6 repair. Other downloadable versions are not yet claimed launchable. Use separate snapshot instances and back up worlds before trying newer versions. NeoForge and LAN hosting remain planned.

This release preserves the exact build 120 package. Authentication, credential migration, local HTTPS transport, instance/account and package checks pass. Existing saved logins require a fresh Microsoft sign-in; no legacy token is submitted under the new client ID. Live PS5 authentication and reopened-session restoration have not been independently confirmed in this release record. Broader endurance, mod combinations and standalone JNA API coverage remain under testing. Microphone capture is not included. No new shader-performance improvement is claimed.

## Credits and source

GUI: **mihawk-99/PS5_VKHomebrewUI**, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: **MultiMC and Prism Launcher contributors**, with original licenses and attribution retained. Runtime: **PS5 Java 25**, with OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. Project thumbnails belong to their respective mod and pack authors; image decoding uses libwebp and STB.

Matching OpenAL corresponding source, relink materials, validation and SHA-256 checksums accompany this release. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
