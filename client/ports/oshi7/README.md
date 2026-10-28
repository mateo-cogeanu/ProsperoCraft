# OSHI 7.7.2 PS5 provider

Snapshot26.4-snapshot-6 uses oshi-common/core-ffm7.7.2 and the supported SystemInfoProvider service API instead of the6.9entry point. This small opt-in provider has priority100 and is available only after the existing native CPU handoff sets oshi.ps5. It returns actual CPU identity and OS-visible logical count through the shared Ps5Hardware implementation. Unsupported OS/load/memory/clock metrics throw; no readings are invented.

No OSHI7 or Minecraft class is replaced. The JAR contains only oshi.ps5 classes, a service registration and the upstream license. The original publisher JARs remain in the verified instance cache. Other OSHI providers and non-PS5 availability remain unchanged. Build with tools/build_oshi7_platform.py; sources.json pins the compile API JAR and MIT license. Shared project support source is GPL-3.0-or-later. Test with tools/test_launcher_snapshots.py. Physical console snapshot startup/debug output remains pending.
