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

## Runtime-first priority and disabled binding work —2026-11-08

The maintainer subsequently prioritizes a separate genuine Java17 runtime first,
then requests a Java21 comparison for1.21.x. No older-runtime performance benefit
or application compatibility is established by this change. Runtime source/build
work remains in the Java repository; the working Java25 application stays intact.

Initial independent consumer groundwork remains disabled: genuine publisher
LWJGL3.3.1 build7 inputs, a rebased PS5 dispatch overlay, and isolated native331
objects compile on host and target. The shared builder retains its default333
generation and gains explicit port/input parameters for331. OSHI6.2.2 compiles
against the original1.20 dependencies, omitting only a newer unsupported cache
API whose type is absent from that version. Original game/dependency JARs remain
unchanged. No launcher availability or package version was changed.

The actual331 JNI ownership fixture passes allocation/key-refusal controls,
foreign-table preservation,3200concurrent lifecycle cycles and paired destruction
under native sanitizers. All21 portable host checks pass in43.4seconds. These are
scoped library checks; no original1.20 graphics/game/world execution or PS5 pass
is claimed. The current331 bootstrap explicitly targets the Java25 JNI table;
matching Java17 headers/table validation will be needed for that runtime.

## Separate Java17/21 cross-build result —2026-11-08

Runtime commit `320fd6a` publishes the reusable, version-pinned baseline work:
[Java17/21 scope and reproduction](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/320fd6a/Development/docs/java-lts-runtimes.md).
Both genuine HotSpot server VMs (C1/C2), matching java.base classes/native libraries
and class-only core images build. Original target Object/Runtime/StrictMath image
bytes were read back and verified. These are not complete PS5 runtime ports or
installable consumer builds. Image/native lookup, sandbox properties, memory,
CPU/signals, threads/TLS, native packaging and a matching consumer bootstrap
remain pending before console testing. The current Java25 launcher uses APIs and
classfile generation unavailable unchanged on17/21; runtime selection requires
an explicit integration design. No version selector or default VM changed here.

The unchanged333 ownership fixture also passes after sharing its builder with331;
all13 native host-lane checks pass in14.1seconds. The earlier21 fast checks passed
in43.4seconds. These checks cover their stated scoped libraries/policies, not a
Java17/21 VM executing a world or shaders on the PS5. Full runtime build outputs
stay local; source changes are published separately to their owning repository.

## Isolated Java17 startup handoff —2026-11-08

Runtime commit `d503c83` adds the first local standalone startup candidate:
[Java17 startup probe002](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/d503c83/Development/docs/java17-startup-probe.md).
PPSA99876 version01.000.002 uses a separate title and matched Java17 VM/core
natives/image. Scoped host JNI, image failure/ownership, resident lookup,
register-context and source tests pass. Signed package/native integrity and CRC
checks pass. Physical VM creation, Java/JNI/worker execution and destruction remain
pending. No consumer availability, default runtime, Minecraft files, renderer,
settings or supported instance changed. Java21 startup follows scoped Java17
console results; no performance improvement is claimed from the native build.


## Java17 console pass and Java21 startup handoff —2026-11-08

The maintainer reported **ALL PASS** on standalone Java17 Startup PPSA99876,
01.000.002. Its four rows cover actual interpreter VM creation, Java arithmetic/
UTF16/StrictMath/exception/JNI checks, the joined Java worker and clean destruction.
[Exact package, complete source and checksums](https://github.com/mateo-cogeanu/ps5-java25-homebrew/releases/tag/Java17_Startup-v01.000.002)
are preserved; [frozen runtime source](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/279f6b84352064dd646864d3f59cd29c80422fee/runtime/Java17_Startup)
records source d503c8336d1b4e55faf9e4dc5f147ce596d3ab1d and original evidence.
The exact passing ZIP SHA256 is
c2241e10bb8c0cb895c7fc02a8490cdd50b2be670e54bc561c90e98c43776c29.
No C2, Minecraft, shader, endurance or performance acceptance follows.

Runtime source051cbf7 also supplies [Java21 startup001](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/051cbf7/Development/docs/java21-startup-probe.md),
PPSA99877, as a separate signed local candidate with matched21 classes/native
core. Actual host21 JNI/Java, image failure controls, resident registry, signal
layout/target IR and signed package audits pass. Physical-console four-row result
is pending; no unvalidated Java21 release was created. Its local ZIP SHA256 is
33598afb949733eedfc328695d4fffcc81091ed46d1ff92654dc3611cc5d2260.

Consumer launcher availability and default Java25 remain unchanged. Matching17/21
consumer bootstrap/JNI bindings, original game execution, worlds/save/rejoin/quit,
shaders and repeatable overhead comparisons are the remaining integration work.
This is a documentation-only consumer update; previous scoped21fast/13native
results are preserved and no new application build or console pass is claimed.


## Both LTS startup passes and Java17 JNI integration —2026-11-08

The maintainer reported **ALL PASS** for Java21 PPSA99877/01.000.001 immediately
after its four-row test handoff. [Verified passing package, complete source and checksums](https://github.com/mateo-cogeanu/ps5-java25-homebrew/releases/tag/Java21_Startup-v01.000.001)
and [frozen source](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/2468e3d5034b4c5122e14bf5a461fdc0db27ce0a/runtime/Java21_Startup)
are preserved. Runtime source `e84566965b02346bf1cd646cb43d77fab1ffda7b` records the exact result.
Both17and21 now pass interpreter startup/Java/JNI/joined-worker/destruction on
PS5. C2, game integration, shaders, virtual threads/FFM, endurance and performance
remain separate unvalidated scopes.

The next consumer boundary is implemented without enabling1.20: the331 builder
accepts explicit `--runtime-major 17` or21 (default25) and selects that major's
actual target JNI headers. Every native unit has a compile-time table-size check;
audits record the selected major and header hashes. The331 bootstrap checks real
Java feature/JNI version and full table slots:17=234,21=235,25=236. Wrong native
counts and foreign VM generations fail before the bootstrap is accepted.
Default333 and working25 selections stay unchanged. Original publisher JARs are
verified and retained, with a separate minimal source overlay compiled for Java8.

Example isolated17 build (use matching prepared runtime/SDK and pinned libffi):

```sh
python3 tools/build_lwjgl331.py --runtime-major 17 --java-home /path/to/jdk17 \
  --publisher-cache /path/to/verified-original-libraries --output-dir build/lwjgl331-j17 \
  --runtime-workspace /path/to/runtime --ffi-include /path/to/target-libffi/include \
  --cc /path/to/clang --lld /path/to/ld.lld
python3 tools/test_lwjgl333_ownership.py --generation 331 --runtime-major 17 \
  --java-home /path/to/jdk17 --build-dir build/lwjgl331-j17 \
  --output-dir build/lwjgl331-j17/ownership-host17 --cc /path/to/host-clang
```

All208target native units compile with Java17 headers. Actual host17/21/25
VMs validate their real table/version against the331 rule and reject wrong count/
generation. The existing native ownership fixture passes32threads/3200cycles,
attached callback allocation/key refusal, genuine native attachment/destructor,
foreign table preservation, failed allocation/key rollback and balanced frees
under ASan/UBSan/-Xcheck:jni. The host fixture alone uses256MiB heap and disables
compressed pointer layouts because older host VMs'1GiB class-space reservation
collides with ASan; no production VM/GC/heap policy changed. See the
[scoped build record](validation/lts-jni-bindings-2026-11-08.json).

A matching17 game bootstrap, resident/native integration and physical1.20
menu/world/save/rejoin/quit/shader checks are still required. No consumer package,
instance availability, default runtime or release/Store update is produced here.


The current333 source also rebuilds all209target units with25headers and passes
its unchanged ownership controls. A stale generated333 tree was encountered during
verification; the fixture now rejects an obsolete patch audit before executing
native code. Required21fast/13native checks pass, and all21fast checks pass again
from outside a source-only checkout with an empty dependency cache and explicitly
provisioned host pins. These remain scoped host/build results, not a game pass.


## First original1.20 Java17 bootstrap candidate —2026-11-09

[Standalone boot test001](client-java17-bootstrap-001.md), PPSA99878, now checks
extended genuine17modules, matched331JNI/native memory and unchanged1.20Main up
to its expected required-argument refusal, then VM destruction. It has no playable
menu/world yet. Host entry/package/21fast/13native checks pass; exact physical
four-row result is pending. The local ZIP contains verified publisher inputs and
is not a public release artifact. No launcher/default runtime/instance/world or
Store update is made. Matching full game/graphics/input/audio/bootstrap and
owned-account/provisioning remain next, followed by exact game/shader validation.


[Bootstrap002](client-java17-bootstrap-002.md) follows001's physical VM-create
crash after native image setup. It retains VM/image choices and adds runtime
phases plus scoped fault capture and targeted diagnostic read permissions. Cause
is unproven and original Minecraft was not reached; physical002results pending.


[003](client-java17-bootstrap-003.md) follows002's narrower init_globals failure.
It retains modules/bindings and tests128MiB maximum heap with finer runtime phases
and bounded fatal entry records. Heap cause and physical result remain unproven.


[004](client-java17-bootstrap-004.md) follows003's confirmed VM creation but row3
failure before a Java stage file. It adds JNI/native Java-entry markers and a
bounded fault scope around row3.128MiB/modules/331stay, cause/gamepass pending.
