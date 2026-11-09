# Contributor host checks

The supported host lanes use Python 3.10+ (stdlib only), a complete **JDK 25**,
and macOS or Linux on the host's native ARM64/x86_64 architecture. CI installs
Python 3.12 and Temurin 25 explicitly on `ubuntu-24.04` and `macos-15`.
Windows, cross-architecture JNI loading and other JDK majors are not supported
by these lanes. There is no PS5 SDK, account, token or game download prerequisite.

```sh
# From a fresh clone: download two small, pinned libraries, then run assertions.
python3 tools/run_host_tests.py --fetch-deps
# Subsequent runs are offline; missing/corrupt dependencies fail.
python3 tools/run_host_tests.py
# Optional actual native code tests: Clang/Clang++ with ASan/UBSan and pthreads.
python3 tools/run_host_tests.py --lane native --fetch-deps
```

`tests/host-lanes.json` is the explicit required selection; no test discovery or
missing-dependency skips. Each process has a 180-second bound; workflows have
12/15-minute limits. Python optimization (`-O`/`PYTHONOPTIMIZE`) is rejected because
existing checks use assertions. Imports of `host_toolchain.py` do no discovery,
argument parsing or downloads. Individual migrated test entrypoints remain usable.

The twenty-one fast checks include the seven-release 1.20 input/generation failure controls and 1.21 publisher failure controls, Vanilla-only gates, coherent333/343/SDL ownership and mapped shutdown evidence, alongside real child-JVM clean System.exit observer/refusal checks, 26.1 publisher-input/class-parser failure controls, three bootstrap/audit/identity checks, discovery regressions, pinned release-artifact recovery failure controls and ten existing launcher
checks: auth state transitions/redaction, saved-login migration/refresh/sign-out,
local TLS refusal/body/redirect behavior, storage errors, instance persistence and
verified download/install/launch restrictions, Modrinth queues/recursive dependencies,
genuine Fabric version predicates and upgrade/rollback decisions, signed offline
ownership, deletion recovery, and duplicate isolation/cancellation. The additional local-web check exercises real loopback sockets, pairing/session/origin rules, staging/format/path boundaries, interrupted/full-volume failure cleanup and service ownership/restarts. In-memory
transports, generated tiny JAR fixtures and temporary directories exercise actual
launcher code. HTTPS uses a disposable localhost TLS server and keytool certificate.
No real Microsoft/Modrinth request or Minecraft execution is part of assertions.
The 26.1 input test uses temporary hash/transport/rule/path fixtures and a real
JDK-generated class; no publisher downloads, native object or game cache is used.
The separate `audit_client_261.py` needs explicitly provisioned original publisher
JARs, pinned parent modules and rebuilt GLFW/OpenGL components. It is outside
the portable lanes and does not execute GL or establish a console result.
The instance test's formerly unsupported 26.2 fixture is now unsupported 26.1;
26.2/26.3 support remains explicitly checked without changing production policy. The same instance test also checks the exact
187 Zink build-resource gate, normal owned-account launch policy, all three26.1
Vanilla development versions, adapted GLFW priority, original OpenGL arguments
and unchanged default/Demo/Fabric/Vulkan boundaries with injected publisher data.

The native runner forces UBSan errors to fail (`halt_on_error=1`), including local runs.
The fourteen optional native checks exercise actual scoped audio mutex/port/worker
implementations, desktop HID/model policy and resident-library JNI loading, with
controlled OS boundaries. The microphone check runs the actual bounded capture core with injected AudioIn calls, including silence/route changes, conversion, failure ownership and concurrent producer/consumer cleanup. It does not capture host or PS5 speech. The context-error check covers generation reuse, thread isolation, bounded context capacity and refused native-key setters. The Zink guard check combines the actual frontend guard body and existing mutex
reserve under late-init refusal, contention, unprimed/exhausted pool and exact
error controls. It models a PS5 allocation boundary, not driver execution. These
checks require no external graphics/audio library. The candidate Zink submission
policy test checks actual bounded flushsync/direct-context environment setup, exact-token idempotence,
existing flags and setter-refusal ownership. It does not execute graphics. The clean-exit gate check exercises actual atomic status/ownership policy with concurrent consumers and native sanitizers; it does not execute PS5 LoadExec. The embedded-VM check runs genuine HotSpot shutdown hooks, the native gate/exit hook and existing restart bridge with a host exec fixture, including unarmed/nonzero exits and Xcheck:jni. They
do **not** exercise OpenAL rendering, SDL, RADV, MoltenVK, Vulkan or a PS5 driver.
The JNI test uses platform headers, `.dylib`/`-dynamiclib` on macOS and
`.so`/`-shared -fPIC` plus libdl on Linux. Linux loads Clang's shared UBSan runtime
from the selected compiler's runtime directory. No target architecture is forced;
the JDK and compiler must target the same host architecture.

## Discovery and overrides

- JDK: `--java-home` > `JAVA_HOME` > resolved `javac` on `PATH`. The Apple
  `/usr/bin/javac` shim uses `/usr/libexec/java_home -v 25`. Both `java` and `javac`
  must be major 25, with `keytool` available; errors identify unsupported/incomplete
  installations. JNI tests additionally require `include/jni.h` and
  `include/{darwin,linux}/jni_md.h`.
- Compiler: `--cc`/`--cxx` > `CC`/`CXX` > `LLVM_HOME/bin/clang[++]` > `PATH` >
  `HOMEBREW_PREFIX/{opt/llvm/bin,bin}`. Overrides name one executable, not a command
  with embedded flags. Explicit invalid overrides fail instead of falling back.
  `LLVM_HOME` is an installation prefix; discovery does not invoke Homebrew or
  assume `/opt/homebrew`, `/usr/local`, ARM64 or Intel. A usable LLVM_HOME candidate
  takes priority; otherwise normal PATH discovery continues.
- Host libraries: `--deps-dir` > `PROSPERO_HOST_DEPS` > repository-local
  `.tools/host-tests`. Relative option paths resolve against the caller's working
  directory. Every access checks size and SHA-256 from `tests/host-dependencies.json`.
  Only `--fetch-deps` permits provisioning downloads: Gson 2.14.0 (313,604 bytes)
  and Fabric Loader 0.20.1 (1,988,880 bytes, used for genuine version predicates).
  Existing game/private caches are never searched. Existing corrupt files fail;
  remove the identified file before fetching again. No downloaded JAR enters Git.

```sh
# Works from outside the repository; replace these example installation paths.
python3 /path/to/ProsperoCraft/tools/run_host_tests.py \
  --java-home /path/to/jdk25 --deps-dir /tmp/prospero-host-deps --fetch-deps
LLVM_HOME=/path/to/llvm JAVA_HOME=/path/to/jdk25 \
  python3 tools/run_host_tests.py --lane native
```

The portable discovery contract applies to the listed lanes, not every older
package builder or regression script. [The inventory](host-test-inventory.md)
records the other tooling and its prerequisites. Intentional PS5 SDK/runtime
inputs and historical validation records are unchanged.

## CI boundaries

`host-policy.yml` runs for relevant pushes and pull requests and can be dispatched
manually; `host-native.yml` is manual only. Both use read-only repository permission,
cancellation, SHA-pinned official actions, checkout without persisted credentials,
no secrets, no credential/dependency cache, and no `pull_request_target`.
The JDK patch version follows Temurin's supported 25 line; action code and host
library inputs are pinned. Runner images/toolchains receive hosted updates.
Actions selection follows official [setup-java](https://github.com/actions/setup-java)
and [checkout](https://github.com/actions/checkout) documentation; there is no
assumption that a runner's preinstalled JDK is Java 25.

Full SDK-dependent package checks remain local. With separately provisioned
runtime/SDK and pinned game/native build inputs, use:

```sh
python3 tools/build_current_client.py --runtime-workspace /path/to/runtime --java-home /path/to/jdk25
python3 tools/test_client_startup_package.py --runtime-workspace /path/to/runtime
```

See [source organization](source-organization.md) for preparation requirements.
Never upload restricted SDK inputs. Existing host GPU probes specifically use
MoltenVK/Metal on macOS; Mesa lavapipe would be a different backend, and neither
establishes RADV/PS5 behavior. Those probes are excluded, rather than relabeled.
Host CI proves only these assertions on those hosts. PS5 startup, controllers,
audio, GPU, world/save lifecycle and endurance still require the exact build on
physical hardware. No application package, runtime pin, game/mod JAR, release or
Store listing is changed by this workflow.

Measured results: [2026-10-31 validation](validation/host-portability-ci-2026-10-31.json)
records clean-source verification and successful Ubuntu x86_64/macOS ARM64 Actions
runs for both lanes, including the repaired initial UBSan fixture failure.

See [shared tooling](tooling-sharing.md) for bootstrap equivalence, auditor migration,
current identity and the separate SDK/physical-console boundaries.

## Optional Zink research lane

`--lane zink --graphics-config /path/to/config.json` runs actual macOS lavapipe
Zink, rebuilt GLFW/LWJGL and original publisher capability-boundary tests. Copy
`tests/zink-host-config.example.json` and supply every verified input explicitly.
This lane requires separately built native libraries, matching Clang sanitizer
runtime, publisher inputs and overlays; it is outside portable CI and fresh-clone
fast/native prerequisites. No game/native cache is searched or downloaded by the
runner. SDL dummy windows are offscreen, so this proves neither kopper presentation
nor PS5 RADV nor Minecraft Main/title/world. See
[build instructions and evidence](client-26.1-zink-native-180.md).


## Optional matched333 research checks

`tools/test_lwjgl333_host.py` and `tools/test_lwjgl333_ownership.py` require explicit
pinned333 source/build inputs; they are outside portable CI. Host Zink additionally
requires actual matching frontend/GLFW libraries and sanitizer compiler, and the
original-client option requires verified publisher inputs plus the genuine OSHI
provider. See [local205 evidence and limitations](client-1.21-205.md). The fast lane
uses injected temporary fixtures and downloads no game files.

Launcher210 adds the portable actual haptic-worker fixture to the native lane: its
bounded motor/trigger deadlines, disable/shutdown, refusal and no-replay controls
use injected native pad calls. Saved-account tests additionally block a refresh
while navigating and assert that intro/page/tab/selection remain in place. Physical
trigger feel, reset and console layout still require exact-build testing.

The storage native fixture injects only the cross-repository report-root hook;
actual consumer path selection, SDL/fault writes and OpenAL env adapter run with
isolated host roots. Runtime HTTP/root tests are separate. See [216](client-primary-shared-storage-216.md).


### Explicit LTS binding checks

Required fast/native lanes still require JDK25. Specialized331 tools may explicitly
select17or21 with `--runtime-major` plus a matching `--java-home`; the default is25.
Discovery rejects a mismatched major rather than substituting another JDK. Target
binding builds require the matching runtime's generated JNI headers and record
hashes/major, with a compile-time native-table check. See
[1.20 integration instructions](client-1.20-plan.md). The separate downloaded-input
ownership fixture currently uses macOS ASan integration and is outside portable
CI lanes; it does not establish target graphics/game compatibility. Its host-only
small heap/uncompressed layout avoids older-JDK ASan address reservation conflicts.


The fault-budget check sends20real host SIGFPE signals through the existing
scoped recorder with a2report budget, verifies all20prior-handler forwards and
post-scope restoration under ASan/UBSan. It disables raw context copying solely
because host signal frames differ from PS5; it does not validate target frames.
It requires no SDK/JDK/game cache and passes from outside a source-only checkout.
