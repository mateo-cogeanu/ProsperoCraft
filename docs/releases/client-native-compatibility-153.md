# ProsperoCraft 01.000.153

Minecraft Java Edition running natively on PlayStation 5, powered by a Native Java 25 Runtime. Sign in, create separate instances, and play Minecraft Java 26.3 with native graphics, audio, DualSense controls and keyboard/mouse support. Java Edition ownership is required.

## Changelog

- Add Minecraft 26.2 Vanilla support through the native GLFW/SDL Vulkan integration. Fabric for 26.2 is marked Coming soon in instance creation, existing instances and launch controls while compatibility work continues. Existing worlds, mods and downloads are kept.
- Improve native allocation and synchronization handling during startup, including graphics, shader compilation and audio initialization.
- Reserve audio mixer and event workers before Java starts and improve OpenAL context/device synchronization. Broader audio and gameplay endurance testing continues.
- Separate the account name and player head in the top bar. Heads now sit centered in their own theme-colored tiles on both the top bar and account screen, keeping their original size and position.
- Remove the Experimental label from the supported 26.4 snapshots. Snapshots remain off by default; explicitly saved choices are retained.

## Install and compatibility

Install PPSA99874.zip through your usual homebrew workflow or update through ProsperoStore after catalog approval and deployment. Instances, worlds, downloads, settings and saved account data are preserved. Minecraft 26.3 and supported 26.4 snapshots remain available; Fabric 26.2 cannot launch in this release.

Host launcher policy, original 26.2 dependency/bootstrap, package integrity and native relink checks pass. Exact build153 console regression, account tile appearance and broader audio/lifecycle endurance remain pending. This release does not establish a new frozen passing milestone. Microphone capture is not included, and no new shader-performance improvement is claimed.

## Credits and source

GUI: **mihawk-99/PS5_VKHomebrewUI**, based on BlackBearReloaded's ps5-homebrew-ui. Instance icons: **MultiMC and Prism Launcher contributors**, with original licenses and attribution retained. Runtime: **PS5 Java 25**, with OpenJDK, Mesa/RADV, SDL, LWJGL and OpenAL Soft. Project thumbnails belong to their respective mod and pack authors; image decoding uses libwebp and STB.

Matching OpenAL corresponding source, relink materials, validation and SHA-256 checksums accompany this release. ProsperoCraft is unofficial and is not affiliated with Mojang, Microsoft or Sony.
