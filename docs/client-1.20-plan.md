# 1.20.x and Java 17/21 investigation

Maintainer direction, 2026-11-08: work upward from Vanilla 1.20 through 1.20.6,
then return to NeoForge. Investigate both Java 17 and Java 21 as possible runtime
options. Existing working releases and their runtime remain unchanged.

## Verified publisher inputs

| Releases | Publisher Java major | Publisher LWJGL | Modules |
| --- | --- | --- | --- |
| 1.20, 1.20.1 | 17 | 3.3.1 | 7 |
| 1.20.2, 1.20.3, 1.20.4 | 17 | 3.3.2 | 7 |
| 1.20.5, 1.20.6 | 21 | 3.3.3 | 8, including FreeType |

`client/1.20.lock.json` records original client, mappings, complete library
metadata and publisher metadata hashes, checked against the [original publisher
manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json).
These are research inputs, with no launcher availability or compatibility claim.
No downloaded game, library or foreign source files are included in Git.

Verify the metadata independently, including from outside this checkout:

```sh
python3 /path/to/ProsperoCraft/tools/verify_client_120.py --cache-dir /path/to/research-cache
# Repeat without network after provisioning.
python3 /path/to/ProsperoCraft/tools/verify_client_120.py --cache-dir /path/to/research-cache --offline
```

The required fast lane includes offline controls for each generation, incorrect
Java majors, changed client pins, invalid releases and coherent-but-wrong binding
inventories. Metadata verification does not execute Minecraft or native graphics.

## Comparison project review

Read-only review of tmghd272/ProsperoCraft at commit
`bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc`, rather than its changing main branch:

- [Build script](https://github.com/tmghd272/ProsperoCraft/blob/bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc/tools/build/build_jdk.sh)
  selects genuine OpenJDK 17, 21 or 25 source/build/image directories. Its Java 17
  input is OpenJDK jdk17u commit `3b0480102f8595deb241a666498f77644d5ec376`
  (module version 17.0.20); Java 21 uses jdk21u tag `jdk-21.0.12-ga`.
  The default VM variant is C1/client. `C2=1` selects the server/tiered variant.
- [Title packaging](https://github.com/tmghd272/ProsperoCraft/blob/bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc/tools/build/make_jvm_title.sh)
  links selected runtimes into one title with localized internal symbols and
  renamed entry points, and includes a separate class-library image for each.
- [Runtime selection](https://github.com/tmghd272/ProsperoCraft/blob/bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc/src/host/jvm_host.cpp)
  dispatches VM creation and native symbol lookup to the selected Java major.
  Heap, collector and compiler policy also differ from ours, so observed speed
  cannot be attributed to the Java major without a controlled comparison.
- [Java 17 patch script](https://github.com/tmghd272/ProsperoCraft/blob/bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc/tools/build/ps5_jdk_patch.py)
  includes direct-memory reservation/commit tracking, platform signal adaptation,
  resident native lookup and a shared metaspace lock for hidden class loaders.
  The latter reduces native synchronization-object demand while serializing those
  allocations. This is a design worth evaluating with ownership, contention,
  unloading and failure tests; its source comments alone do not establish our
  device's object limit or a performance improvement.
- [Java 21 patch script](https://github.com/tmghd272/ProsperoCraft/blob/bc7ce9cdb8f3a0a520eae76603cc0ee8897a23fc/tools/build/ps5_jdk_patch21.py)
  likewise ports platform services and memory behavior. Neither script is a
  drop-in runtime for our consumer. Foreign scripts were read, not executed.

No implementation has been copied. Separate Java versions require matching VM,
class libraries, native libraries, launcher compilation/API choices and resident
symbol ownership. Our Java 25 launcher and finalized FFM-dependent integrations
cannot simply be run on Java 17/21 unchanged. Reusable runtime implementation
belongs in ps5-java25-homebrew; version selection and game integration belong here.

## First compatibility findings and next work

The hash-verified original 1.20 client and mappings were downloaded locally.
Its Minecraft class is `enn`, singleton getter `N`, running field `aZ`, and
running query `q`, from the publisher mappings. Its JAR remains intact.

The existing classfile parser compared declared native method tuples
(class/name/descriptor/staticness) across verified publisher LWJGL JARs:

| Core module | Native declarations | Declarations absent from 3.3.3 |
| --- | --- | --- |
| LWJGL 3.3.1 | 1766 | 195 |
| LWJGL 3.3.2 | 2010 | 3 |

OpenGL 3.3.1 has 2235 declared native methods, all present in 3.3.3; 3.3.2 has
2237, also all present. This scoped comparison does not prove JNI-table layout,
generated function-pointer wrappers, native ownership or graphics compatibility.
In particular, it is insufficient to route all older core bindings through our
3.3.3 native table. Matched 3.3.1/3.3.2 integration needs review and validation.

Implementation sequence:

1. Establish a coherent 3.3.1 native binding group for original Vanilla 1.20.
   Audit Java linkage, callback ownership, shutdown and class-loader boundaries.
2. Build a local hardware candidate for 1.20. Validate menu, controller, world
   creation/exploration, save/rejoin, clean quit and shader behavior where supported.
   Continue upward only with scoped results, preserving supported versions.
3. Evaluate Java 17 first for 1.20–1.20.4, and Java 21 for 1.20.5–1.20.6.
   Port the required runtime services with default behavior and failure semantics
   preserved. Keep each candidate independently selectable for comparison.
4. Compare against Java 25 with the same original game, seed, mods, distances,
   heap limit, worker count and equivalent compiler/collector policy where possible.
   Record cold and warm startup, native/heap memory, chunk-generation time,
   frame-time spikes and world-save/quit behavior. Label unavoidable differences.

A smaller major number does not establish lower overhead, better chunk generation
or available collector support. Multi-runtime packaging can increase installed
size. No new Java runtime, 1.20 launcher build, PS5 pass or release is claimed by
this research change. Local free disk space was below 200 MiB during review. Removing eight duplicate
ELF outputs from previous 273/274 relink checks reclaimed about 965 MiB, with
release packages and canonical build artifacts retained. Full independent
OpenJDK builds still need substantially more working space.

## Local verification, 2026-11-08

All seven metadata hashes/generation checks passed against the saved publisher
inputs. The new test also passed from outside the project in a source-only copy
with no dependency cache. Regenerated PNG/SVG artwork was visually checked.
`python3 tools/run_host_tests.py` passed all20 checks in85.3seconds. An initial
run failed while creating the browser test ZIP because the host disk filled;
a complete rerun passed after the duplicate-output cleanup described above.
Native implementation was not changed, and no native lane or physical PS5 test
was performed for this research change. Hosted CI is separate evidence.
