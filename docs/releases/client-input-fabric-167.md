# ProsperoCraft 01.000.167

Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime. Java Edition ownership is required.

## Changelog

- Enable supported Minecraft 26.2 Fabric alongside 26.2 Vanilla and 26.3. Remove the development-test labels from Fabric26.2 instances, launch controls and creation choices.
- Fix Controlify controller detection and switching between controller and physical keyboard/mouse on 26.2 and 26.3 Fabric. Isolate its SDL connection-event handling so game keyboard/mouse events remain available.
- Add mouse and keyboard controls to the launcher: click buttons and instance cards, scroll, right-click or Escape to go back, navigate with arrows, confirm with Enter, switch pages with Tab, and type/edit instance names and searches. Launcher text entry currently uses US ASCII with Shift/Caps Lock.
- Add a rounded vector cursor matching the requested silhouette, with theme-colored fill and one continuous light outline. It follows all six saved launcher themes; controller navigation hides it until the mouse is used again.
- Fix 26.3 Controlify on-screen keyboard deletion and 26.2 Vanilla held-key typing. Preserve genuine upstream game/mod JARs and the existing controller, audio and rendering integration.
- Retain the native shader/audio/TLS startup and allocation repairs developed since 158.

## Install and compatibility

Install PPSA99874.zip through your usual homebrew workflow, or update through ProsperoStore once its catalog update is approved and deployed. The exact user-tested 167 package is published without rebuilding. Existing instances, worlds, downloads, settings and saved account data are preserved.

Minecraft 26.2 and 26.3 Vanilla/Fabric are supported. Supported26.4 snapshots 1–6 remain available, hidden by default; snapshot-specific Fabric and mod compatibility depend on matching upstream versions. Other versions and NeoForge are not newly enabled.

The user accepts the functionality and polish of exact 167 and explicitly requests release, following acceptance of 166’s Controlify handoff repair. Host input/model, six-theme Vulkan rendering, package integrity and exact native relinks pass. This is functional acceptance, not a measured per-device/per-feature regression matrix or long-session endurance result. Microphone capture is not included; no new shader-performance guarantee is made.

## Credits and source

GUI: **mihawk-99/PS5_VKHomebrewUI**, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: **MultiMC and Prism Launcher contributors**, with original licenses and attribution retained. Runtime: **PS5 Java 25**, with OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. Project thumbnails belong to their respective mod and pack authors; image decoding uses libwebp and STB.

Matching OpenAL corresponding source, relink materials, validation and SHA-256 checksums accompany this release. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
