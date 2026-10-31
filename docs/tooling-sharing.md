# Shared bootstrap, audits and current identity

The baseline is ProsperoCraft `c418d9b92026364b61455a96d546f3a179774ddb`.
The active publication checkout was clean and matched fetched `origin/main`.
The enclosing Java workspace's pre-existing untracked source was left alone.
This change builds on the existing portable host lanes and does not change
runtime/dependency pins, game/mod JARs, performance policy or console acceptance.

## Duplication audit and build inputs

| Classification | Inputs and entry points | Treatment |
| --- | --- | --- |
| Current launcher | `build_current_client.py` → graphics preparation/package → `package_client_vulkan.py --startup` → `package_client_gpu_link.finish`; `client/startup/bootstrap.cpp` | Keep separate: early AudioOut, native mutex/condition/TLS/worker reservations, constructor staging, launcher/model and physical display/input handoff differ from acceptance probes. |
| Active acceptance/regression variants | `package_client_vulkan.py --native-bootstrap`, `--opengl-bootstrap`, `--stb-bootstrap`, `--freetype-bootstrap`, `--vma-bootstrap`, `--spvc-bootstrap` (see `--help`) | Six wrappers now supply a `constexpr prospero_acceptance::Config` to `client/bootstrap/acceptance_impl.hpp`. Preserve their original diagnostic versions, fixture names and all messages. |
| Other active native/JNI variants | `client/{native,gpu,graphics,vulkan,shader,render,present,sdl,runtime_shader}/bootstrap.cpp`; `package_client_probe.py`, `package_client_gpu.py`, `package_client_graphics.py`, other Vulkan switches | Keep: different constructor groups, JNI fixtures, row counts, GPU resources/presentation and cleanup/retention. Shared line count alone does not establish matching semantics. |
| Server | `server/native/bootstrap.cpp`, `package_server_probe.py` | Keep server-specific lifecycle/configuration and reservation behavior. |
| Legacy staging regression audits | `test_client122_package.py` through `test_client150_package.py` | Thin commands delegate to `package_audit.run_legacy` and `legacy_package_audit.audit_legacy`. These originally combined versioned symbols with **mutable current staging files**; they do not independently audit immutable release packages. That limitation remains explicit. |
| Current package audit | `test_client_startup_package.py` | Keeps every specialized assertion; adds Java/native identity gates and derives its current ELF version. |
| Immutable artifact audits | `test_client167_release.py`, other named release tests and historical-validation fixtures | Keep original versions, acceptance facts, object/package hashes and assertions. Current identity must never rewrite them. |
| Archived source | `ps5-homebrew-history` pinned migration commit `aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d` | Untouched; no top-level milestone folders recreated. |
| Generated/local material | ignored `build`, `dist`, `.tools`; isolated refactor verification copy | Never canonical implementation inputs merely because they contain copied source. No tracked bootstrap was proven unused. Remove only specifically verified disposable scratch; preserve original package/symbol/relink/dependency inputs. |

The six shared variants match in initialization/constructor order, JNI registration,
thread behavior, VM options, error codes, native trace ownership, preflight,
cleanup and retained-display behavior. Configuration contains only pointers to
string literals, with constant initialization and no allocation. Prefix comparison
uses the configured prefix's length. The no-argument pass-state `snprintf` uses
`"%s"` to retain strict compiler format checks. Legacy text (including the026
512MiB diagnostic) is preserved rather than silently correcting behavior/text.
Other bootstraps remain readable in their own source files.

`tests/bootstrap-migration.json` pins each original source hash. The host check
reconstructs all six original files from the shared body/configuration, proving
all nonconfiguration source is retained. Optional target comparison compiles both
forms in a fresh temporary directory and compares **all allocated code/data/BSS,
unwind state, relocations and symbol ABI/binding/visibility**. It normalizes only
local string-pool numbering/layout; raw object bytes differ for that reason.
The existing exported JNI/C symbols and static constructor behavior are retained.

## Assertion migration map

`tests/audits/migration.json` maps `check_000`…`check_112` to applicable build
numbers, original file SHA-256s and complete normalized AST fingerprints. Matching
comments in `tools/legacy_package_audit.py` locate every shared statement. The
29 effective ordered programs preserve 1,718 expanded assertion nodes. Only the
selected ELF filename and printed build labels become parameters; historical
artifact paths, checksums, comparison values and assertions remain exact.

| Important old checks | New location |
| --- | --- |
| Required118GLFW functions, Vulkan/IME/TinyFD exports, packaged sources/CRC, callback binding JAR | Opening blocks of `legacy_package_audit.audit_legacy`; distinct122/123+ branches retained |
| libjava/libverify runtime pins, object hashes, verifier/direct scratch enables | `scratch` blocks for125 and126+; native-symbol assertions retained |
| Emutls direct mapper/ledger, SDL rwlock/sync, RADV allocators/conditions, exception forwarding | Corresponding named audit/object/ELF blocks in the same function, with original applicability lists |
| Shaderc exact constructor order/no lazy guards, RADV fence/wait locks, VMA and native reservations | Original constructor/relocation/disassembly/source assertions in the shared function |
| Native library scratch, OpenAL Device/Context/HRTF/search/log locks and worker ownership | Later feature blocks through150, including exact replacement-source equality and undefined-symbol checks |
| Resident aliases/Controlify sidecar and handle lookup, dependency boundaries, snapshot defaults, auth migration, runtime integration and license pins | Existing specialized current package and host tests remain intact; the current alias-table checker derives its current ELF version |
| Exact released167 checksums, default policy, corresponding source and relink inputs | Unchanged `test_client167_release.py`; never converted to current-build metadata |

`tests/audits/legacy-builds.json` is strict JSON data selecting known legacy
profiles. Unknown/missing fields, invalid schema/kind, duplicate JSON keys,
duplicate/unordered builds, booleans, unknown builds and code-shaped values fail.
No manifest supplies executable code. Assertions cannot be disabled with `-O`.
`package_audit.checked_zip` provides CRC, duplicate-name, unsafe-path and optional
SHA-256 gates. `audit_current_identity` checks actual packaging metadata, the
native identity marker and both Java resource copies. Corrupt CRC/JAR/checksum,
missing/wrong native/Java identities and malformed manifests have negative tests.
Shared mechanics supplement rather than replace specialized checks.

## Current identity contract

`client/startup/param.json` is the canonical **current application** title/version.
`app_identity.current_identity` validates it. Packaging derives the native
`PROSPERO_APP_VERSION`, current symbol ELF filename, Java resource and generated
status from this identity. The existing native launcher's development fallback
remains explicit. Acceptance variants retain their own original `param.json`
versions; server, dependency/runtime versions and historical releases are distinct.

`app_identity.write_probe_jar` packages the compiled classes with reproducible
`prosperocraft-build.properties` and writes the same resource to exploded classes.
`ProsperoBuild` reads it for the auth/install/download User-Agent. A missing resource
in source-only host/development execution yields `development`; malformed packaged
identity fails initialization. OAuth IDs, endpoints, scopes, tokens and auth flow
are unchanged. JAR resource/channel metadata now uses deterministic ZIP timestamps.

`build-status.json` is emitted only after link/package/identity checks succeed.
It records application identity, package SHA-256, source commit/tree state,
`compilation=passed` and `console=pending`. A source export without Git records a
null commit/unavailable state. It never derives ALL PASS or carries console
acceptance from an earlier artifact. No application version is incremented here.
Old167 packages naturally lack the new resource: use their immutable release audit,
not the new current-build identity gate. Do not replace released bytes.

## Verification and corresponding source

```sh
python3 tools/run_host_tests.py --fetch-deps
python3 tools/run_host_tests.py --lane native
# Optional SDK-dependent target compilation/equivalence (no package overwrites):
CXX=/path/to/llvm22/bin/clang++ python3 tools/test_bootstrap_sharing.py \
  --runtime-workspace /path/to/runtime
# Complete current build needs independently provisioned SDK/native/game inputs:
python3 tools/build_current_client.py --runtime-workspace /path/to/runtime --java-home /path/to/jdk25
python3 tools/test_client_startup_package.py --runtime-workspace /path/to/runtime
```

The three new fast checks run in the existing read-only Linux/macOS CI lane.
Source-only verification with an empty host dependency cache and outside-root
invocation remains required. SDK/package checks stay separate from host CI.
`build_client_openal_relink.export_consumer_bootstrap` includes both the selected
wrapper and shared headers in future corresponding-source kits, with original
notices retained. The host check verifies exact exported source bytes for all six
variants. Existing exact release kits and relink inputs remain unchanged.

Measured results and outstanding package/PS5 limits are recorded in
[validation](validation/tooling-sharing-2026-10-31.json). New resource/User-Agent
behavior and all newly built artifacts require exact physical-console startup,
auth/download, controller/display handoff, audio/world/save/lifecycle regression
before acceptance or release. No GitHub release, prerelease or Store change is
part of this work.
