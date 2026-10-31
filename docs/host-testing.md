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

The eleven fast checks include discovery regressions and ten existing launcher
checks: auth state transitions/redaction, saved-login migration/refresh/sign-out,
local TLS refusal/body/redirect behavior, storage errors, instance persistence and
verified download/install/launch restrictions, Modrinth queues/recursive dependencies,
genuine Fabric version predicates and upgrade/rollback decisions, signed offline
ownership, deletion recovery, and duplicate isolation/cancellation. In-memory
transports, generated tiny JAR fixtures and temporary directories exercise actual
launcher code. HTTPS uses a disposable localhost TLS server and keytool certificate.
No real Microsoft/Modrinth request or Minecraft execution is part of assertions.
The instance test's formerly unsupported 26.2 fixture is now unsupported 26.1;
26.2/26.3 support remains explicitly checked without changing production policy.

The five optional native checks exercise actual scoped audio mutex/port/worker
implementations, desktop HID/model policy and resident-library JNI loading, with
controlled OS boundaries. They require no external graphics/audio library. They
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
