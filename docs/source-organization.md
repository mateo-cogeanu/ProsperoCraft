# Active source and historical snapshots

The canonical runtime remains [ps5-java25-homebrew](https://github.com/mateo-cogeanu/ps5-java25-homebrew), with active source under `Development/`. Minecraft integration remains in [ProsperoCraft](https://github.com/mateo-cogeanu/ProsperoCraft). Frozen source is preserved in [ps5-homebrew-history](https://github.com/mateo-cogeanu/ps5-homebrew-history), pinned at `aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d` for this migration. Its manifest indexes original paths, commits, file modes, SHA-256 values, versions, title IDs and original console validation.

## Classification and dependency audit

The migration audited runtime commit `b1df916944e53dee39ee41f6681f1af3f7dc32a1` and ProsperoCraft commit `7254777e4004e10985578186acb0fd98a8a18035`. Both actual publication checkouts were clean, on `main`, and identical to fetched `origin/main`. The enclosing runtime workspace has an uncommitted local Git repository: source was already untracked there, while the public source of record was the clean publication checkout. No local changes were reset or discarded.

| Classification | Kept or moved | Evidence |
| --- | --- | --- |
| Current runtime build | Keep all `Development/java25`, `tools`, native/source/assets, Makefile and packaging metadata | Source bootstrap consumes all patches and pins; module/image/resident builders, JNI packager and native packager use these directories. No frozen top-level runtime folder is a build input. |
| Runtime tests and ongoing work | Keep every active regression, Java fixture, probe variant, compatibility patch and technical document | Tests read the patched OpenJDK cache and active fixtures. Disabled/default-off policies and unfinished console validation do not make implementations historical. |
| Current consumer build/development | Keep root `client`, `server`, `tools`, assets, metadata, docs, dependency pins and all compatibility implementations | `package_client_vulkan.py --startup` calls the root probe/module/native builders; it consumes root sources, not frozen client folders. Old variant builders remain useful diagnostic and compatibility coverage. |
| Testing/licensing/release compliance | Keep native source pins, patches, OpenAL corresponding-source/relink builders, notices, active validation and regression tests | Five frozen `validation.json` records are read by active package tests or staging cleanup; byte-identical copies remain under consumer `tests/fixtures/historical-validation`. Existing ignored compiled milestone packages remain regression inputs. |
| Frozen runtime history | Move nine complete top-level passing snapshots | `JVM_Startup`, `IO_Probe`, `ZIP_JAR_Probe`, `Network_Probe`, `LAN_DNS_Probe`, `Inbound_LAN_Probe`, `Advanced_Network_Probe`, `LAN_Endurance_Probe`, `Dependency_Probe`; active runtime has no source dependency on them. |
| Frozen consumer history | Move all 23 complete top-level `Client_*` and `Server_*` snapshot folders | Historical self-contained source duplicates; five required validation inputs retained separately. See the archive manifest for the exact list. |
| Temporary/generated/private | Keep out of Git | `.tools`, `build`, `dist`, logs, Python caches, credentials and downloaded JARs. Existing local caches and tested packages were retained. The untracked workspace migration prompt is outside the source allowlist. |

Source ownership did not change. In particular, Fabric 26.2, default-off runtime fallbacks, launcher prototypes, native input/audio/storage, SDL, Vulkan, JNA, ImageIO and all active source generators remain included. No implementation was removed because a feature is unavailable or awaiting validation. No Store action, application version change, branch merge, release mutation or history rewrite is part of this migration.

## Build entry points

Requirements are macOS, Python 3, Git, GNU make, LLVM 22.1.7 and a Java 25 host JDK. In a public clone, use `cd Development` before runtime commands. The runtime workspace used during migration is this directory directly, without the public `Development` wrapper.

```sh
# Prepares the revision-pinned native boilerplate and SHA-256-pinned SDK v0.42.
python3 tools/package_native.py --source java25/probe/main.cpp --param java25/probe/param.json
# Fetches the pinned FreeBSD OpenJDK commit and applies every active patch.
python3 tools/java25_source.py --build-hotspot --build-base
python3 tools/java25_audit.py
python3 tools/test_java25_native_library_names.py
```

Pre-existing incremental-build limitation: `java25_source.py` checks patches individually. On an already fully patched cache, it can reject patch `0009` because later patches changed the same lines. The migration's clean pinned-source application/configuration and complete build pass; do not reset a modified cache to work around the incremental check. For an already configured, current cache, `gmake CONF=ps5-bootstrap hotspot java.base-java java.base-libs` is the measured baseline command. Prefer an isolated fresh source cache for reproduction.

OpenJDK's source revision is pinned in `java25/upstream.json`; native SDK/archive and boilerplate pins are checked by `tools/package_native.py`. Consumer Maven/game artifacts are URL/size/hash-pinned in lock files; native libraries have source pins and checked patches in `client/ports` and their prepare/build tools. Online preparation may download artifacts into ignored caches; `--offline` requires those caches to be provisioned first and still validates them. No downloaded game or mod JAR is source controlled.

From an active ProsperoCraft checkout:

```sh
python3 tools/build_current_client.py --runtime-workspace /absolute/runtime/Development --java-home /absolute/jdk25
python3 tools/test_client_startup_package.py --runtime-workspace /absolute/runtime/Development
python3 tools/build_lwjgl_native.py --runtime-workspace /absolute/runtime/Development --java-home /absolute/jdk25 --host
python3 tools/test_client_startup_host.py --java-home /absolute/jdk25
```

The STB builder canonicalizes the verified dependency-cache path so compiler `__FILE__` assertion strings remain identical when that same cache is shared through a symlink. This preserves the strict frozen-object hash regression without changing the native implementation or relaxing tests. Arbitrary different source-cache locations can still change diagnostic path strings in legacy frozen native hashes.

The full consumer entry point first prepares pinned RADV/platform dependencies and generates the native graphics recipe, import declarations and upstream notices, then builds the current client. These were previously implicit prerequisites supplied by local build outputs. It retains current `01.000.153` metadata and produces a local build check, not a new accepted application version or a release. Do not upload verification binaries as replacements for released bytes. Older package regression tests also require preserved local packages under ignored `dist/milestones`, `dist/accepted`, `dist/failures`, `dist/published` and `dist/archives`, documented by their hash assertions; a source checkout alone does not contain those binaries. The published OpenAL source/relink ZIP is the durable reproducibility input for exact released native objects; do not substitute a current rebuild for its original source or inputs.

## Publication and recovery

`python3 tools/sync_github.py --message "..."` continues to publish only the explicit active runtime allowlist into `Development`, plus root maintainer instructions, README and banner. Historical folders are not allowlisted. `java25/github-publication.json` pins the archive commit and manifest checksum. Before retiring any legacy runtime folder, `tools/history_archive.py` independently fetches the archive, verifies its bytes and compares every original file; missing, changed or extra local files cause refusal before removal. Later syncs do not recreate snapshots.

Consumer changes are committed directly to ProsperoCraft. Historical source is maintained separately in the archive; freeze new snapshots there only after exact console acceptance. Keep original validation semantics and package checksums. The original repositories retain their Git history, historical tags and releases; removing files from the current tree does not shrink existing historical Git objects.

For recovery, clone the pinned archive, run `python3 verify.py`, then use its manifest to locate the original source commit and destination. Original release download URLs remain authoritative. Archived Markdown is byte-preserved, so old relative cross-repository links or historical absolute workspace paths may require consulting the provenance record. Active Markdown snapshot links point directly to the pinned archive. Raw console reports remain local.

See [migration validation](validation/source-history-migration-2026-10-30.json) for measured build results and remaining limitations. Compilation and host testing do not establish PS5 gameplay acceptance.

The consumer includes a hash-pinned subset of upstream toolkit documentation. Its 81 pre-existing relative links to omitted sample/runtime files remain byte-preserved with that upstream source input; consult the [complete pinned toolkit tree](https://github.com/mihawk-99/PS5_VKHomebrewUI/tree/2188642afbcc8d84d36149124f3d9e39dc1b1a05). These are distinct from maintained project/archive links, which resolve.
