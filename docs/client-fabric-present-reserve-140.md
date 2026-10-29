# Native presentation reserves, app 140

Safari retrieved the preserved build139 failure after reopening. Run
`client-01.000.139-1793292744-490193153` gets past VMA buffer creation, compiles
shaders and creates three imported VideoOut swapchain images. It then reports
`WSI flip thread create result2`. The original Minecraft26.2/Fabric crash report
identifies `VK_ERROR_OUT_OF_HOST_MEMORY: Failed to present image`, during the
first resource reload/render frames. This is later than138's VMA mutex failure;
it is not evidence of a world/gameplay pass. Raw reports remain local.

The native trace also records repeated RADV C11 `mtx_lock` calls returning
ENOMEM, resolved using the exact139 symbols. Mesa's POSIX `mtx_init` implementation
ignores the underlying init result, so a failed late native allocation can leave
those locks unusable. Separate C++ exceptions originate in OpenAL diagnostic
logging; this candidate does not claim their cause is repaired or establish
working audio. Java thread creation failures appear during error-reporting exit.

App140 reserves one actual native presentation worker before JVM creation.
The worker waits for assignment without initializing graphics or touching WSI.
The private WSI source patch replaces only the flip thread's `thrd_create` call
with a single assignment to that existing worker. It invokes the original
`videoout_flip_thread` with its unchanged argument; original fences, queue,
mutex/condition operations, flip ordering and VideoOut calls remain in place.
The WSI routine already lives for the process lifetime and remains shared across
swapchain lifecycles. No second presentation routine, synchronous presentation
fallback or fabricated success is introduced. Precreation failure fails startup
explicitly. A duplicate or invalid assignment returns Mesa `thrd_error`.

RADV's six pthread mutex calls alone route through a bounded native reserve:
256 ordinary mutexes and64 recursive mutexes initialized before the JVM.
Initialization leases an unused native object by caller address; lock/unlock,
try/timed lock and condition waits retain native pthread operations. Condition
waits resolve both the leased condition and the leased caller mutex, preserving
atomic unlock/wait/reacquisition. Destroy returns an unused lease; concurrent
use/destruction remains outside the POSIX lifetime contract. Unsupported foreign
attributes keep their native path. The internal recursive attributes produced
by Mesa use the recursive pool. Pools retain their native objects until process
exit. Exhaustion returns ENOMEM. No arbitrary/default global pthread interposition,
Java runtime policy, heap/GC or game/mod JAR changes are introduced.

The WSI patch applies only to a private archive rebuilt from pristine pinned
Mesa sources; original sources/archive remain unchanged. The new source/patch,
object and packaged audit hashes are checked. Existing VMA hooks, runtime fixes,
SDL/GLFW/compiler reserves, clock semantics and bounded diagnostics are retained.

Host ASan/UBSan checks exercise actual native worker creation failure/retry,
idempotence, no callback before assignment, single assignment, invalid requests,
late creation refusal and exact original thread identity/argument/result. Actual
Mesa C11 plus native mutex/condition adapters validate normal/recursive locks,
320-slot exhaustion and return,80,000 contended operations,10,000 mutex/condition
reuse cycles, try/timed operations, locked-destroy rejection, signal/broadcast,
data visibility and condition-mutex reacquisition with late native init refused.
Existing realtime/monotonic condition and launcher checks remain required. On
macOS only, the missing native timed-mutex API is supplied by an explicitly host
fixture using native trylock and absolute deadlines; PS5 uses its native API.

PS5 exact140 startup/presentation and Fabric26.2 menu/world/input/audio/save/reload/
endurance remain pending. Recheck accepted vanilla26.2 and working26.3/26.4
snapshots before a public release. Preserve exact139/138 and prior canonical
packages/symbols, accepted124, frozen milestones and Store121. No Store release
or new passing milestone is established by this build.
