# Original1.20 / Java17 bootstrap001

Standalone **PPSA99878**, **01.000.001**, is the next local test after exact
Java17 startup002 and Java21 startup001 console passes. It preserves both frozen
runtime packages and the working Java25 launcher. Physical acceptance is pending.

Install the separate **ProsperoCraft1.20 - Java17 Boot Test** title and run all four
rows in order with D-pad and X:

1. Initialize matched Java17/core/management/LWJGL331 constructors.
2. Create genuine Java17 in interpreter mode with a512MiB maximum test heap.
3. Check original Java/JNI/thread basics, genuine RuntimeMXBean identity, matched331
   native memory, then the unchanged Minecraft1.20 entry point.
4. Destroy the VM and complete its native shutdown hooks.

Report ALL PASS or the first failed/hanging row. This is **boot initialization,
not a playable menu/world**. Main receives no authentication/game arguments and
must reach its normal MissingRequiredOptionsException gate. That expected argument
refusal establishes the entry/parser path, not login, rendering, world or gameplay.
There is no game replacement class, bytecode hook, version/platform spoof or
modified original game/mod JAR. The native runtime reports its actual PS5 OS.

Local package: `dist/PPSA99878.zip` in the runtime workspace,114227889bytes,
SHA256 `05395a8cf57c59b2bf35183eb9173baafea19fff8c1dbfaa464648598069ea45`.
The [build record](validation/client-java17-bootstrap-001-build-2026-11-09.json)
identifies matching symbols, runtime/image/native groups and publisher hashes.
This local candidate includes verified original publisher inputs; it must not be
used as a public release artifact. No release or Store action is authorized here.

The exact consumer Java probe passes with a real host17 VM under-Xint/-Xcheck:jni
and UBSan, including arithmetic/UTF16/StrictMath/exceptions/registered JNI/worker
join, real management identity, original entry/parser gate and VM destruction.
Host-only mode explicitly skips PS5-specific native331 initialization; actual
17/21/25 ownership tests are separate evidence. The game and complete331 overlay/
original classes share one URLClassLoader with the matching thread context loader,
preserving genuine logging service discovery. Additional target modules include
beans/desktop Java classes, XML, logging, management and Unsafe. This does not
provide full native AWT/fonts/printing/GUI support. Original management natives
and private JVM/JMM state are linked separately by the runtime-owned helper.

Private reports: `download0/mc120-java17-bootstrap.log`,
`download0/mc120-java17-stages.log`, `download0/java17-vm-trace.log`, and fatal
`download0/java17-hs-error-%p.log`, all under this separate title's own mount.
No account/instance/world/NAS operations or inbound address/server are present.
If it crashes, reopen this same probe once to expose its retained private reports.

## Reproduction

Runtime source `f110a9d14fc12b64eecb76023d19c04f7b67a4b8` supplies the reusable extended-module/resident/package
helpers. See [the runtime guide](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/f110a9d14fc12b64eecb76023d19c04f7b67a4b8/Development/docs/java-lts-bootstrap-integration.md).
Use fresh output/work directories and matching17headers/331objects/overlay audits:

```sh
python3 tools/package_java17_bootstrap.py --runtime-workspace /path/to/runtime \
  --llvm-home /path/to/llvm --lld /path/to/ld.lld --java-home /path/to/jdk17 \
  --cache-dir /path/to/original120inputs --lwjgl331-build /path/to/matching331build \
  --ffi-core /path/to/target/ffi-core.o --image-dir /path/to/extended17/boot-image \
  --work-dir /path/to/fresh-work --offline
```

Without--offline, only pinned original publisher inputs are fetched through the
existing strict HTTPS/hash/path helper. Original release metadata and17/331
assumptions are rechecked; stale overlay/native source audits and hashes fail.
The supplemental libffi core comes from the existing pinned target builder;
343JNI output is excluded, retaining genuine331JNI and its own closure adapter.
The package records that object's exact hash. No implicit private cache fallback.
The default25 application/package and launcher version availability stay intact.
