# Host tooling inventory — 2026-10-31

This inventories active `tools/test_*.py` entrypoints by inspected dependencies,
not by alleged test coverage. Only the explicit portable lanes are run by CI.
Other rows describe prerequisite boundaries found in source, not verified execution
or a promise that old paths/expectations are current. A file count includes aliases,
artifact audits and optional probes; it is not a runnable-coverage metric.

Portable lanes have no SDK/game/cache prerequisite: the runner provisions only
Gson and Fabric Loader by size/SHA-256. See [commands and discovery](host-testing.md).
Existing numeric package/release audits remain active regression fixtures, even
when their packages are unavailable in a public clone. Do not move or delete them
as historical-only tooling. Frozen milestone-only tools/sources live in the
[history archive](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft).
Historical validation JSON retained under `tests/fixtures/historical-validation`
is still an input to active package checks. This task does not migrate the archive.

Graphics distinctions: existing `test_client_gpu_host.py`, `test_client_vulkan_host.py`
and `test_vma_bootstrap_host.py` select macOS MoltenVK, not target RADV or lavapipe.
OpenAL/SDL/bootstrap probes require their prepared providers; OSMesa/OpenGL probes
require their corresponding built providers. No hosted GPU coverage is claimed.
The manual native lane instead tests scoped native implementations against fixtures.

## Verified portable lanes

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_audio_native_mutex.py` | Clang/Clang++, ASan/UBSan; desktop needs Gson/JDK; JNI needs platform headers; required native |
| `test_audio_port_retention.py` | Clang/Clang++, ASan/UBSan; desktop needs Gson/JDK; JNI needs platform headers; required native |
| `test_client_library.py` | Clang/Clang++, ASan/UBSan; desktop needs Gson/JDK; JNI needs platform headers; required native |
| `test_fabric_dependencies.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_host_toolchain.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_auth.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_auth_migration.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_content.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_delete.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_desktop.py` | Clang/Clang++, ASan/UBSan; desktop needs Gson/JDK; JNI needs platform headers; required native |
| `test_launcher_duplicate.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_https.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_instances.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_offline.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_launcher_storage.py` | Python + JDK25 + pinned Gson/Fabric; temporary deterministic fixtures; required fast |
| `test_openal_mixer_workers.py` | Clang/Clang++, ASan/UBSan; desktop needs Gson/JDK; JNI needs platform headers; required native |

## Retained package and release regressions

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client096_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client098_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client100_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client101_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client108_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client117_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client119_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |
| `test_client120_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |
| `test_client121_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |
| `test_client122_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client123_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client124_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client125_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client126_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client127_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client128_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client129_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client130_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client131_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client132_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client133_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client134_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client135_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client136_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client137_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client138_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client139_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client140_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client141_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client142_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client143_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client144_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client145_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client146_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client147_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client148_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client149_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client150_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, hardcoded JDK |
| `test_client153_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |
| `test_client167_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |
| `test_client_freetype_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_gpu_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_menu_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_client_native_bootstrap_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_opengl_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_spvc_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_startup_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_stb_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_vma_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_client_vulkan_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded Homebrew, runtime option |
| `test_launcher_store_release.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests |
| `test_temp_gametest_package.py` | Exact local build/dist/accepted or published artifacts and recorded hashes; many need runtime objects/LLVM/JDK; not fresh-clone tests; observed: hardcoded JDK |

## Additional Java/Python/source checks

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client099_g1_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client100_remark_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client104_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_client_audio_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_configuration_observer.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_distance_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_g1_workload.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_gc_layout.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_heap_069.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_client_world_heap.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_distant_horizons_ps5.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_glfw_callbacks.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_heap_layout.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded Homebrew |
| `test_launcher104_controls.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher105_input.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher_account_ui.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher_backgrounds.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher_centering.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: Pillow |
| `test_launcher_fabric262_development.py` | Compatibility aliases execute test_launcher_desktop.py; not independent coverage |
| `test_launcher_fabric262_pending.py` | Compatibility aliases execute test_launcher_desktop.py; not independent coverage |
| `test_launcher_home.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher_themes.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded JDK |
| `test_launcher_toolkit_packages.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_launcher_toolkit_shaders.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_lwjgl_platform.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_menu_policy.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_network_memory.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded Homebrew |
| `test_offline_export.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable |
| `test_presentation_assets.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: Pillow |
| `test_server_thread_lookup.py` | Inspect entrypoint: often JDK/Gson, generated build/configuration or runtime fixture inputs; not selected/verified as portable; observed: hardcoded Homebrew |

## Downloaded game/mod or populated cache checks

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client_artifacts.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane |
| `test_content_icons.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_controlify_keyboard.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_controlify_triggers.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_default_controlify_live.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_fabric_dependencies_live.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_262.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_content_live.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_fabric_bootstrap.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_network.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_publisher.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_launcher_snapshots.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_server_probe.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded Homebrew |
| `test_server_start.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded Homebrew |
| `test_snapshot6_jna.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded JDK |
| `test_vanilla_server.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded Homebrew |
| `test_world_metadata.py` | Verified publisher/game/mod JARs or prepared build/cache fixtures; live variants may contact services; excluded from offline lane; observed: hardcoded Homebrew |

## Additional host-native fixtures

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client_bridge.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: JNI darwin only |
| `test_client_crash_capture.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_client_relative_mouse.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_client_startup_vm_output.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: JNI darwin only |
| `test_controlify_event_isolation.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew, hardcoded JDK |
| `test_controlify_ffm_lookup.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew, hardcoded JDK |
| `test_cpu_identity.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded JDK |
| `test_glfw_platform.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_glfw_reserved_mutex.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_graphics_string_alloc.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_input_present_trace.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_keyboard_overlay.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_launcher_haptics.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded JDK |
| `test_launcher_lifecycle.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded JDK |
| `test_launcher_navigation.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_libffi_closures_wx.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_lwjgl_core.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: JNI darwin only, runtime option |
| `test_lwjgl_tls.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: JNI darwin only |
| `test_native_exception_trace.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_native_mutex_trace.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_openal_directory.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_openal_ps5_audio.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_openal_startup_boundaries.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_paper_shutdown.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_present_worker_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_ps5_cursor_ownership.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_ps5_haptic_audio.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_ps5_hid_native.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_ps5_input_handoff.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_ps5_temporary_input.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_ps5_usb_input.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_radv_condition_reserve.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_radv_monotonic_reserve.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_radv_mutex_reserve.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_sdl_display_mode_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_sdl_fixed_resolution.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_sdl_pad_platform.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_sdl_ps5_rwlock.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_sdl_sync_reserve.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_sdl_thread_storage.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_shader_stage_budget.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_shaderc_fault.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_shaderc_include_mutex.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_shaderc_reserved_mutex.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded Homebrew |
| `test_startup_boundary.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_startup_native_observer.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_startup_openal_trace.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_tinyfd_unavailable.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing; observed: hardcoded JDK, JNI darwin only |
| `test_videoout_cursor.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_videoout_early_owner_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_videoout_high_refresh_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_videoout_present_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_videoout_resources_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_videoout_retry_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_vm_print.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_vma_inline_mutex.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |
| `test_wsi_diagnostics_host.py` | Host C/C++ compiler; may need prepared SDL/OpenAL/PS5_Mesa/shaderc/VMA headers/source or source extraction; not claimed fresh-clone passing |

## Runtime/PS5 SDK or target build checks

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client_c1.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: runtime option |
| `test_client_cpp_allocation.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: runtime option |
| `test_client_graphics.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: hardcoded Homebrew, runtime option |
| `test_controlify_alias_table.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: hardcoded Homebrew, runtime option |
| `test_hardware_labels.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: runtime option |
| `test_model_lookup_report.py` | Explicit runtime workspace, SDK source or built target artifacts; local provisioning required, not public CI; observed: runtime option |

## Graphics/audio/native integration

| Entrypoint in `tools/` | Dependencies and boundary |
| --- | --- |
| `test_client_gpu_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, JNI darwin only, MoltenVK, runtime option |
| `test_client_native_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: JNI darwin only |
| `test_client_startup_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test |
| `test_client_vulkan_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, JNI darwin only, MoltenVK, runtime option |
| `test_content_images_native.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded JDK, Pillow |
| `test_freetype_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test |
| `test_glfw_vulkan_handoff.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, hardcoded JDK, JNI darwin only |
| `test_launcher_toolkit.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew |
| `test_lwjgl_module_platform.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, MoltenVK, runtime option |
| `test_lwjgl_opengl_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test |
| `test_opengl_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew |
| `test_osmesa_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew |
| `test_sdl_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, JNI darwin only, runtime option |
| `test_sdl_loader_identity_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, MoltenVK |
| `test_spvc_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew |
| `test_stb_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test |
| `test_vma_bootstrap_host.py` | Prepared native/JNI libraries and upstream source/JAR caches; backend-specific, not an interchangeable Vulkan test; observed: hardcoded Homebrew, MoltenVK |

