# 01.000.158 launcher hardware snapshot (local test only)

157's live current-run report confirms model lookup never reached the native query: all recorded sceKernelDlsym name/NID attempts return 0x80020003. The app still reported model unknown. Raw console reports stay local.

158 moves detection into `client/launcher/hardware_identity.hpp`. The launcher calls ordinary libkernel's no-argument sceKernelGetMainSocId once, after starting log sharing and before creating UI/graphics/JVM workers. Only the cached model enum is consumed by OSHI CPU display and RADV's display-name callback. Neither consumer repeats detection. The build report fits the existing 512-byte writer and includes the numeric SoC ID for console verification.

The separately maintained runtime helper uses the native hardware split in [PS5Dev/Byepervisor-Reborn](https://github.com/PS5Dev/Byepervisor-Reborn/blob/main/main.c): 0x840fd0 means Pro, other PS5 SoCs mean standard. Our helper additionally rejects values outside 0x840fxx, including zero and error results. The no-argument unsigned 64-bit declaration matches [ps5-hwinfo](https://github.com/drakmor/ps5-hwinfo/blob/main/main.c). This is a PS5-only native API, not CPU brand, firmware, user settings or graphics-name inference. No kernel memory/exploit code is incorporated. The pinned SDK exports this query in ordinary libkernel; no libkernel_sys dependency or module loading is added. Exact application export availability and hardware values still require physical-console validation. A successful link alone does not establish those facts.

F3 strings are unchanged: `AMD Zen 2, 8C16T (PS5)` / `(PS5 Pro)` and `AMD RDNA 2, 36 CUs (PS5)` / `AMD RDNA 2.x, 60 CUs (PS5 Pro)`. Minecraft retains the genuine logical-count prefix, and genuine driver/IDs/capabilities remain unchanged. Unknown/error hardware keeps the explicit model-unknown fallback. No official game JAR is modified.

Runtime ASan/UBSan tests cover Pro, base-family and error/invalid native values. Consumer tests exercise the actual launcher header, one-time snapshot, unchanged CPU/GPU strings and actual short report. Original unmodified Minecraft CPU formatting tests cover 26.2/26.3 and snapshots 1–6 with OSHI6/7. The full packaged binary gate checks signatures, source/object pins, the exact153 DT_NEEDED set, no old model-name/dlsym imports, the new native query import and initialization before the frontend. Build/check outcomes and checksum are recorded in the matching validation record.

No release/prerelease or Store update is authorized until the user confirms this exact build works. Existing releases, frozen snapshots and earlier local candidates remain preserved. Install the local158 package, confirm launcher startup, then check Vanilla F3 and world/input/audio/save behavior. Standard PS5/Slim and Pro physical detection remain pending; no console pass is claimed.

## Publication authorization

On2026-10-30 the user explicitly requested publishing this exact build on GitHub and updating the existing ProsperoStore entry, with its description unchanged. That request authorizes158 publication without changing its recorded console-pending status. The existing ZIP is preserved without rebuilding; matching source/relink,checksums and build/console records accompany the release. Future releases retain the approval gate.
