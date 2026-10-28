# Development118: 26.4 snapshot launch candidates

The user requests26.4snapshot support after accepting Store117.118preserves the accepted117release and all previous packages. It is a development candidate, with no new Store release or formal ALL PASS. Java runtime0126and the world ZIP-handle budget remain unchanged. Performance tuning and microphone work are outside this change.

## Publisher checks and launcher behavior

The official Mojang version manifest fetched28October2026 lists release26.3and latest snapshot26.4-snapshot-6. All six currently published26.4snapshots require Java25, retain the net.minecraft.client.main.Main entry point and use exactly the26.3LWJGL artifacts and hashes. The explicit candidates and original client/metadata hashes are pinned in client/26.4-snapshots.lock.json. Future snapshots are not automatically enabled. Other downloadable versions remain blocked from Play.

| Version | Java | Asset index | PS5 hardware integration |
| --- | --- | --- | --- |
| 26.4-snapshot-1 | 25 | 35 | 6.9.0 overlay |
| 26.4-snapshot-2 | 25 | 35 | 6.9.0 overlay |
| 26.4-snapshot-3 | 25 | 36 | 6.9.0 overlay |
| 26.4-snapshot-4 | 25 | 36 | 6.9.0 overlay |
| 26.4-snapshot-5 | 25 | 36 | 6.9.0 overlay |
| 26.4-snapshot-6 | 25 | 36 | 7.7.2 SPI |

The launcher previously blocked every version except26.3.118allows these six snapshots as experimental choices, passes the selected ID, snapshot version type and matching asset index, and retains original SDL/Vulkan arguments. A receipt requiring a newer Java runtime is refused before launching. Snapshot visibility remains off by default; enable Show Snapshots in Settings to list them. Existing instance folders and26.3worlds are not migrated or replaced.

Snapshots can change world formats. Create a separate Vanilla instance and a new test world first. Existing instance duplication remains available to make an independent backup, but this build does not expose version-switching on an existing instance. Fabric/Controlify/mod/shader compatibility is separate and depends on versions published for each snapshot; no26.3mods are forced into a snapshot. NeoForge remains disabled.

## OSHI dependency compatibility

Snapshots1–5still use OSHI6.9.0. The existing CPU provider now follows the installed dependency rather than a hard-coded26.3version check. Snapshot6changes to OSHI7.7.2, including its FFM backend and supported service-provider API. The new dependency integration registers oshi.ps5.Ps5SystemInfoProvider using the upstream SPI with priority100. Availability requires the existing validated native CPU handoff; unsupported telemetry remains unsupported rather than fabricated. The shared CPU implementation adds the two OSHI7overloads while retaining6.9behavior.

No game/mod JAR or OSHI7factory class is transformed. The dedicated provider JAR ships beside the existing6.9overlay, with pins/source/license/audit; the game loader chooses the matching provider from its verified dependency filenames. Newer Netty/authlib/datafixer/JNA dependencies remain original publisher downloads. This is consumer-specific integration, not a Java runtime patch or full OSHI/FFM native-platform port.

## Checks

- Real installer runs on all six original publisher metadata/client/library/asset inventories, verifying hashes and receipts. Shared dependencies and assets are reused in the immutable cache; native classifiers are excluded by existing policy.
- Each selected Main class comes from its intact downloaded client JAR; LWJGL dispatch remains in the launcher parent. Snapshot arguments contain the correct selected version/type/asset index. Java26receipts and unreviewed snapshot IDs remain blocked.
- The actual original CPU debug entry returns the fixture CPU identity/count through the matching6.9or7.7provider for all six snapshots. OSHI7SPI selection and disabled-on-desktop behavior are checked, and unsupported OS metrics throw.
- Actual Main startup for each snapshot reaches the expected unprovided host LWJGL native-library failure. This validates loading/bootstrap progress only; it is not a PS5 menu, GPU or gameplay pass.
-26.3publisher/instance/account/CPU regressions and target package checks pass. No successful console snapshot run is claimed before testing.

## Console test

Install the complete118candidate, enable snapshots in Settings, create a separate Vanilla26.4-snapshot-6instance and download it. Check sign-in, title screen, controls, rendering, audio, new-world creation/play/save and reload. Test older snapshots separately if desired. Start with Vanilla to keep unavailable snapshot-specific mods from obscuring native issues. Preserve117as the accepted fallback and collect current build/session/native/Java logs if launch fails.

Candidate ZIP SHA-256: `333ba0d079f3bc4cf479f7a30a3549b367b47c3def2feebce0e8513e1de0c328`.

Primary metadata: [Mojang version manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json). Hash-verified library/source API inspection is recorded by the tests and pins. Hardware and graphics behavior still require actual PS5 testing.


Follow-up: user reports snapshots1–5fully functional, while snapshot6crashes in its newly mandatory JNA native bootstrap before creating a game window. See [119repair](client-snapshot6-jna-119.md) and the matching console feedback record.118remains preserved.
