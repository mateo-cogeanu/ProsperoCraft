# Zink JVM effective classpath repair — candidate185

The user reports184 failed check4. Read-only Safari reports identify
PPSA99874 /01.000.184, run `client-01.000.184-1793525304-161693377`, state
FAIL/codeFFFFFAE5. The current probe exception is
`NoClassDefFoundError: org/lwjgl/glfw/GLFW`. Startup records actual JVM creation
and **native launcher display/device closure and UI-thread join** before the
exception. There is no successful GL workload, DestroyJavaVM or return checkpoint.
Separate thrown-exceptions/hs-error reports are unavailable (errno2). Native/JVM
trace ends with the fixture exception; no new fatal signal is established.
First startup/native downloads remain local. Direct tool HTTP failed with no route
to host; Safari accessed the same read-only service.

The [184 failure receipt](validation/client184-console-classpath-2026-11-01.json)
records the exact package/run and saved-report hashes.

## Concrete packaging cause

184 included the genuine adapted `lwjgl-glfw-3.4.1-ps5-callback343.jar` under
`assets/java25/ports`, but inherited179's JVM classpath omitted that JAR.179 loads
GLFW through later per-instance game classloaders; the diagnostic directly uses
GLFW in its system-loaded harness. Shipping a JAR alone does not make it reachable.
184's host test constructed its own classpath including the binding, and its
package audit checked file presence rather than effective JVM reachability. That
verification gap missed this packaging error. No game/native driver failure or
new runtime allocator cause follows from this check4 failure.

185 adds the adapted binding **first in the effective JVM classpath**. Its
`zink_jvm_classpath.py` helper validates every classpath entry against the explicit
package root, identifies the first JAR defining each required diagnostic/GLFW/GL/
PS5Library/memory class, and requires the adapted GLFW provider. A real JDK25
URLClassLoader performs non-initializing resolution with full verification;
this runs no graphics or game/native initialization. The helper searches no
private/game cache and downloads nothing.

`test_zink_jvm_classpath.py` checks the actual184package/header: the old missing
entry fails despite the JAR's presence; the corrected entry order resolves all
required classes. Header construction is idempotent.185's independent package
audit also matches exact JAR digests and requires the complete classpath option
as a NUL-terminated string in the **exact symbols ELF**, so metadata alone cannot
claim a path that the executable never received.

## Exact185 test

Install complete PPSA99874 /**01.000.185**. Wait for the actual native launcher
**Run Zink handoff** card, then press **X once**. Expect the same six-second JVM
RGB/moving-white-bar sequence, real GL/GLFW/SDL cleanup, diagnostic-only successful
DestroyJavaVM, then the existing LoadExec barrier to a fresh launcher/JVM page
showing **Stage2b PASS**. Confirm visible motion and the returned page separately.
If it fails/crashes, reopen **without X** and leave it open for current/previous
reports on read-only port8765. No preset IP or client filter is added.

185 retains184's real launcher, resident resolver, scoped combined Zink/RADV,
constructor staging, runtime fallback policies and restart guards. Its own harness
labels/identity advance to185; shared diagnostic JVM-shutdown log labels are now
version-neutral to avoid misidentifying subsequent candidates. Production179
policy is unchanged. The [184 guide](client-zink-jvm-handoff-184.md) describes this
actual native UI/JVM seam and the host/native ownership boundaries.

This is still a diagnostic Java mailbox page, **not ordinary account/instance/
download/original-Main behavior**. Original26.1/26.1.1/26.1.2 title/world/audio/
save/reopen/exit/relaunch, Vulkan-version regressions, measured refresh/FPS and
endurance remain pending. Preserve accepted183, failed184 and older packages,
symbols, original validation,029 OSMesa, adapted callbacks, runtime allocator/TLS/
sync/stack workarounds, official JARs and frozen history. No release/prerelease or
Store action; current game/root identity remains179 and26.1 production stays blocked.

Build185 with `package_zink_jvm_classpath.py` using the same explicit179 package,
relink/build inputs, component, runtime, JDK25, LLVM/LLD as184. Output is
`dist/candidates/zink-jvm-185`; existing candidate ZIPs are never overwritten.
`test_client185_package.py` audits the result. The shared host GL harness accepts
an explicit `--fixture client/zink_handoff_classpath/ClientStartup25.java` and an
isolated output directory; actual Java rendering runs on lavapipe, while its
launcher barrier is modeled and no native UI/VideoOut/LoadExec is established.
The [185 validation record](validation/client185-zink-classpath-2026-11-01.json)
records clean build source7ae62cb and exact package/symbol/classpath hashes. ZIP SHA-256:
`e541f4638ab5034e9addbf280a34f3220276cc0fca04ef70edc5ca0e13be3f7f`.
The host workload also passes using **the actual185packaged JAR list/order and
packaged fixture**, with no shadowing fixture class or extra parent JAR entries.
Supply `--app` and `--classpath-audit` with a clean host output directory to use
this stricter mode. It still models only the launcher barrier, never PS5 VideoOut.

Local16fast,7native and source-only outside-root16fast checks pass.
[Build-source Ubuntu/macOS CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41293415195)
and [effective-host-tool CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41293624975)
both pass16fast checks; completed jobs/logs were inspected. Hosted CI executes
no graphics, native launcher, VideoOut or PS5 process replacement.

Physical185 subsequently failed check4 with a bare resident-library name. See the
[185 failure receipt](validation/client185-console-resident-2026-11-01.json) and
[186 repair](client-zink-resident-186.md). No185 GL/handoff pass is claimed.
