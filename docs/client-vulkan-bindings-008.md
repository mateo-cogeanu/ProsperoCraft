# Client Vulkan Bindings 01.000.008 — diagnostic storage recovery

Client007 failed row2 before JNI_CreateJavaVM. The saved session is
`client-01.000.007-1792832478-845195428`, code `0000001C` (ENOSPC).
Its startup tail ends after core-image validation; the checkpoint trace is empty.
The preflight trace-header write therefore failed before entering the JVM.
The exception report still identifies006 and is stale, not a007 Java exception.

The shared startup history was58,035,442bytes. Full startup history and available
failure reports have been saved locally; earlier006's66.2MiB VM trace was already
archived before007 reset it. Storage exhaustion is confirmed, although total
volume usage and other contributors have not been measured.

Client008 uses an opt-in reusable runtime probe helper to retain the last512KiB
each of startup history and the old VM trace when the user explicitly initializes
a new run. A menu-only relaunch preserves reports. The helper reads the tail into
caller-provided memory, truncates the same file to free old blocks and rewrites
the tail without needing a second on-disk copy. If IO fails, the probe stops and
reports the error; a write failure after truncation can leave a partial tail.
Only these two diagnostic files are selected. World/save files, configurations,
original game/Vulkan JARs and frozen milestones are untouched. Existing007
checkpoint sampling and quiet native-call context remain enabled.

The helper passes host real-file exact-tail/inode/idempotence/small/missing/
invalid-input checks under ASan/UBSan. It is diagnostic probe support, with no
JVM implementation or SDK change. The original006 Vulkan stall still requires
console validation; host GPU success does not establish its resolution.

Install **PPSA99874 01.000.008** from `dist/client-vulkan/PPSA99874.zip`, also
copied to the runtime workspace's `dist/PPSA99874.zip`. Run all ten rows in order.
Report any failure and leave the app open for logs; after a crash reopen without
running rows. All ten rows, storage recovery and completion of the Vulkan row
remain pending on PS5. Server two-hour endurance remains explicitly deferred.
Package SHA256 and completed host/package checks are recorded in
`client/vulkan/status.json`. No passing milestone or release is created.

## Console acceptance

All ten008 rows pass on2026-10-24, confirmed directly by the user. Retrieved logs corroborate12 standard GPU submissions,3 lifecycles/loader cleanup and final DestroyJavaVM. Frozen source, exact tested package and scope are recorded in [Client_Vulkan_Bindings](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Vulkan_Bindings/README.md).
