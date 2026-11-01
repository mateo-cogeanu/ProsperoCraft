# Native creation checkpoints — candidate190

189 remains black in exact run `client-01.000.189-1793540376-91210473`.
The [separate console receipt](validation/client189-console-black-2026-11-01.json)
records exact package/run and first local report hashes. Session stays RUN, with
no Java exception captured. Native stderr confirms early guard init result0,
actual launcher display/device handoff and SDL window creation. Repeated Java
snapshots hold the render thread in native `glfwCreateWindow` through elapsed
129157ms. The fatal report is unavailable(errno2). This does not identify an
internal native wait, prove a GPU fault or establish title/world success.

## Diagnostic scope

190 adds fixed startup stage pairs around frontend guard acquisition, context
allocation, Zink screen creation, Mesa state-tracker context creation, drawable
validation, state-tracker binding and GLFW GL attribute refresh. Frontend output
is capped at48events with a saturating atomic counter; labels contain no runtime
paths, pointers, accounts or game arguments and preserve errno. GLFW labels reuse
the existing bounded startup boundary. No timeout, forced unlock/cleanup, ownership
relaxation, allocator/pool enlargement, driver feature or success stub is added.
This is **diagnostic**, not a claimed hang fix.

Keep189's pre-JVM real mutex lease and actual lock/error checks. Same pinned
combined Zink/RADV/GLFW path, callbacks, native API semantics and original game/mod
JARs remain. No full native stack/blocked PC was captured, so a last breadcrumb
must not be described as the exact failing instruction. It narrows the next
source interval only. Extra diagnostic output is not refresh/FPS evidence.

Install complete PPSA99874 / **01.000.190** and launch the same **Fabric26.1**
instance through the normal launcher. If black persists, leave it running for
report retrieval; report title/world behavior separately if it advances.
Vanilla/Fabric26.1/26.1.1/26.1.2 stay available as development tests; Iris stays
blocked. Accounts, downloaded originals, upstream Fabric/Knot/Mixin, saved worlds
and published179 identity are unchanged. Quit-crash repair remains explicitly
deferred; startup/session/restart sources match187/188/189.

`package_zink_fabric_trace.py` uses the explicit179 ZIP/relink/build inputs,
rebuilt pinned component, runtime,JDK25,LLVM/LLD from189; isolated outputs are
`build/zink-jvm190` and `dist/candidates/zink-jvm-190`, refusing ZIP overwrite.
`test_client190_package.py` checks exact identity/hashes/classpath, diagnostic
labels, real guard initializer in relocated staged constructors, resident groups,
single graphics copy, unchanged shutdown sources/original JARs and signatures.
Prior189 native component/host artifacts were copied locally before rebuilding;
preserve all prior ZIPs/symbols/receipts and original build validation.

Actual190 Fabric startup/title/world/mod behavior, all Vanilla/Fabric26.1.x
versions, world/audio/save/reopen/quit/relaunch,26.2/26.3/snapshot Vulkan regressions,
measured scanout/FPS/resource reclamation and endurance remain pending. Retain
029OSMesa, adapted callbacks, runtime descriptor/ZIP/ImageIO/JNA/resident aliases,
allocator/scratch/verifier/emutls/network/sync/stack and SDL/RADV/shaderc/OpenAL/
input/audio workarounds. No release/prerelease,Store action,archive freeze or full
milestone ALL PASS is inferred.

The [exact190 build record](validation/client190-zink-fabric-trace-2026-11-01.json)
pins clean source `e5c5787` and component/package/runtime hashes.
ZIP SHA-256: `38f6af3bcdd77d391e4cb4e09cab1fbfa01f66a39654550577a8cfdb7ce44f54`.
Local16fast,8native,source-only16fast, actual host GL and target/package audits
pass. Real host runs for all three releases contain ordered startup stages and
exactly48bounded frontend events.
[Ubuntu/macOS policy CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41312559066)
passes16checks on each host; completed job logs inspected. Current190native tests
are local;189hostednative verification remains separate. No190physical result or
hang repair is claimed.

Physical190 subsequently [failed creating Zink's flush queue](validation/client190-console-flush-queue-2026-11-01.json).
[191](client-zink-flushsync-191.md) tests the existing upstream synchronous
flush/present path to avoid that queue; underlying allocation/worker cause and
physical behavior remain pending. Quit repair stays deferred.
