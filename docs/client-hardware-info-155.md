# 01.000.155 compact F3 hardware labels

Development test 155 shortens the hardware names from 154 and makes the GPU compute-unit difference explicit. Detection, logical CPU counts, the OSHI 6/7 providers and the PS5 Vulkan name-only integration remain unchanged. No new game/mod JAR change, renderer capability/driver/ID change, performance policy or Store release is included. All prior packages and frozen history remain preserved.

| Console | CPU name, after Minecraft's logical-count prefix | GPU name |
| --- | --- | --- |
| PS5 / Slim | AMD Zen 2, 8C16T (PS5) | AMD RDNA 2, 36 CUs (PS5) |
| PS5 Pro | AMD Zen 2, 8C16T (PS5 Pro) | AMD RDNA 2.x, 60 CUs (PS5 Pro) |
| Failed/unrecognized model | AMD CPU (PS5; model unknown) | AMD RDNA (PS5; model unknown) |

`8C16T` denotes the static 8 physical-core/16 hardware-thread specification. Minecraft keeps its actual logical-processor prefix, for example `16x AMD Zen 2, 8C16T (PS5 Pro)`. Neither OSHI's logical count nor Runtime.availableProcessors() is changed. The new names are shorter than the previous labels, but physical-console F3 line wrapping/readability still needs checking.

## Architecture and CU evidence

[Sony's official technical seminar announcement](https://blog.playstation.com/?p=399740) links [Mark Cerny's original PS5 Pro presentation](https://www.youtube.com/watch?v=lXMwXJsMfIQ). At approximately 2:46–3:29, he describes 18 workgroup processors in the base PS5, 30 in the Pro, and the Pro's hybrid base architecture as RDNA 2.x, between RDNA 2 and 3. The corresponding CU counts are 36 and 60 (two CUs per WGP). Sony's [base specification page](https://contents.sony.co.kr/sony/contents/2076/contents_26.html) explicitly pairs 18 WGPs with 36 CUs. This supports the requested 36 versus 60 distinction without using RADV's internal NAVI21 compiler target as hardware evidence. These are static hardware specifications, not measured activity or a claim that the driver exposes every hardware resource.

The Pro label uses RDNA 2.x rather than the requested RDNA 3 because the latter would misstate Sony's published hybrid architecture description. The presentation separately describes newer ray-tracing technology and custom ML enhancements; a single unqualified RDNA 3 label would conceal those distinctions. Clocks, TFLOPS and memory information remain omitted.

## Build, publication and validation

[Download 155](https://github.com/mateo-cogeanu/ProsperoCraft/releases/tag/client155-compact-hardware-test). It is a development prerelease under the existing PPSA99874 identity and replaces the installed client/server app. Stable/Store 153 and the Fabric 26.2 hold remain unchanged. Use the release's SHA256SUMS, build/console records and matching OpenAL corresponding-source/relink kit.

The model query and failure handling are those documented for [154](client-hardware-info-154.md), using separately published runtime helper db3048f. Unknown models remain explicit; no serial API, preset model override, firmware inference or graphics-codename inference is introduced. Explicit drirc device-name compatibility overrides still take priority.

`tools/test_hardware_labels.py` exercises the six actual compact labels, native string bounds/ASCII, unchanged CPUID/JVM counts, PS5/non-PS5 property sentinels/explicit overrides and all eight original supported Minecraft CPU/Vulkan name paths: 26.2, 26.3 and 26.4 snapshots 1–6. The full startup package suite verifies 155 identity, packaged source/helper/main/RADV object hashes, all six strings, native wiring, runtime/dependency/signature/CRC checks and preservation of prior package fixtures. Actual target compilation/link/signing and exact native ELF relink are checked separately from physical-console acceptance. See the matching build validation record.

Both physical-console results remain **pending**: on standard PS5/Slim check 36 CUs; on a real Pro check 60 CUs and the matching PS5 Pro CPU name. In a working Vanilla world, open F3, check both names fit, retain the genuine driver/backend line and unchanged logical prefix, and confirm normal rendering/input/save behavior. Host fixtures are not evidence of real Pro detection. No passing milestone is created.
