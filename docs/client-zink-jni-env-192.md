# Scoped LWJGL JNI environment ownership —192

191 crashed in exact run `client-01.000.191-1793543270-551516242`; reopened
191run is `client-01.000.191-1793543311-154537308`. The
[crash receipt](validation/client191-console-env-copy-2026-11-01.json) pins package,
run and saved local reports. Screen/context creation, drawable validation, real
VideoOut swapchain and first flip succeed. GLFW attributes refresh returns. Then
original `GlDevice` invokes `GL.createCapabilities`, and genuine LWJGL aborts:
`[LWJGL] Failed to allocate JNIEnv copy.` The startup report captures the exact
ThreadLocalUtil.setupEnvData native FatalError/VM ABORT. No previous hs-error file
exists(errno2); historical signal context elsewhere is not this failure's PC.
The upstream synchronous submission workaround advances past190's failed flush
queue, but is not full title/world acceptance.

## Concrete consumer allocation repair

Genuine pinned `org_lwjgl_system_ThreadLocalUtil.c` directly mallocs the JNI
function-table copy. Genuine `common_tools.c` callocs the owning EnvData TLS record
and frees both copy and record on pthread TLS teardown.179's allocation scoping
covers only MemoryAccessJNI/LibCStdlib, leaving these two units libc-bound.191's
fatal message identifies the env-copy malloc refusal. Exact native quota/allocator
owner remains unproven; no broad heap/GC/resource claim follows.

192 scopes allocator **imports in both units** to the same existing graphics
allocator family used by the main LWJGL memory API. It keeps allocation/free paired
for Java GL threads and native callbacks attached to the JVM. Original native
instructions, JNI table layout/function count, TLS policy, attach/detach, native
key/setter behavior and real refusal semantics stay intact. No game/mod JAR,
JNI-success stub, arbitrary loader, allocator limit or JVM/global allocator change.
Default builders/frozen native inputs remain; this is an isolated candidate.

`scope_lwjgl_env.py` accepts only the known lwjgl group, requires the complete
known graphics allocation family and both exact units, and rejects duplicate or
missing units. It compares actual executable sections before/after objcopy and
checks that only requested undefined allocator imports change. The package uses
verified179 native inputs and rebuilds the existing resident lwjgl group with
those two scoped objects. Existing MemoryAccessJNI/LibCStdlib bindings remain.
The package audit proves the scoped hashes are in the real resident manifest and
the original two hashes are absent, alongside normal symbol/constructor checks.

The explicit manual macOS/JDK25 test `test_lwjgl_env_alloc_host.py` takes a source
directory/compiler/JDK/output directory. It verifies pinned upstream files, applies
the existing PS5 native patch and compiles actual ThreadLocalUtil/common_tools with
the **PS5 TLS branch**. An old-path child JVM with unit-local libc refusal reproduces
the exact FatalError. The scoped variant exercises actual JNI table copying and
JNI dispatch on16concurrent Java threads, plus8native daemon-attach/env/detach
threads. Real pthread TLS destructors release40allocations,40frees,0live under
ASan/UBSan and Xcheck:jni. The host allocator models paired ownership, not the PS5
heap or kernel quota. No target source implementation is replaced by this fixture.
This manual source-dependent test is outside fresh-clone CI lanes.

## Exact192 PS5 test

Install complete PPSA99874 / **01.000.192**, then retry the same **Fabric26.1**
instance from the normal launcher. Report original title/world/mod behavior
separately. If it crashes, reopen and leave the launcher idle without starting
another game; if check4/black remains, leave that screen open for current reports.
Other Vanilla/Fabric26.1,26.1.1,26.1.2 remain development tests, not accepted versions.
Iris stays guarded; ordinary Microsoft ownership and upstream Fabric/Knot/Mixin
remain. Official game/mod JARs/assets are intact and not bundled.

Keep191's candidate-only upstream flushsync policy and its possible throughput
tradeoff,190's bounded stage diagnostics and189's early real mutex lease. Other
native queues/resource failures remain possible. **Quit-crash repair is still
deferred**; original startup/session/restart sources are unchanged. Retain029OSMesa,
GLFW callbacks, runtime descriptor/ZIP/ImageIO/JNA/resident aliases and allocator/
scratch/verifier/emutls/network/sync/thread-stack, SDL/RADV reserves/ownership,
shaderc/OpenAL/input/audio workarounds. Preserve all exact191/190/earlier ZIPs,
symbols/receipts and frozen history. Current published identity179 remains.

`package_zink_fabric_env.py` uses the explicit179 ZIP/relink/build inputs,
unchanged190component,runtime,JDK25,LLVM/LLD and writes isolated
`build/zink-jvm192` / `dist/candidates/zink-jvm-192`, refusing ZIP overwrite.
`test_client192_package.py` checks exact hashes/identity/classpath/resident env
imports and scoped objects, paired family, unmodified native instructions,
relocated staged constructors, one graphics copy/original JARs/signatures.
Actual192 GL capabilities/title/world/mod behavior, all Vanilla/Fabric26.1.x
world/audio/save/reopen/lifecycle,26.2/26.3/snapshot Vulkan regressions, throughput,
resource reclamation/endurance and deferred quit repair remain pending. No full
ALL PASS, release/prerelease,Store update or archive freeze is inferred.
