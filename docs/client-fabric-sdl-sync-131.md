# Fabric26.2 native SDL synchronization reserve, app131

Failed130run1793281245-258448706 no longer shows the identified compiler-TLS
abort. The original Minecraft report explicitly exits during GLFW initialization:
PS5 SDL: pthread_mutex_init() failed. Checkpoints stop inside SDL video/events
initialization. The retained native trace shows Java Shutdown.halt0 and exit-1,
not the prior compiler-rt abort. The underlying SDK init return code and overall
libc/anonymous allocation pressure remain unproven.

App131 changes only the consumer SDL/native startup integration. It reserves256
recursive pthread mutex objects and128pthread condition objects after embedded
constructors and before JVM creation. Initialization failures report actual
native result codes and stop startup rather than pretending success. SDL creates
bounded leases from these ready pools with atomic ownership flags. SDL destruction
returns the lease while retaining the initialized native primitive for process
lifetime; it requires no owner/waiter, as SDL's destruction contract does. There
is no lazy SDK object initialization on subsequent SDL create calls, and no
per-frame object creation. Runtime lock/wait/timeout/signal/broadcast behavior
remains the original SDL pthread code. SDK lock/wait internals may still require
resources; this does not prove all later native allocations succeed.

The paired condition reserve avoids moving the same late-initialization problem
from SDL mutex creation into its condition variables. Pool exhaustion returns an
SDL error. This is a PS5 build patch to genuine pinned SDL; other SDL targets
and unrelated SDK synchronization are unchanged. Existing128reader/writer backend
and130compiler-TLS runtime pins remain unchanged. No game/modJAR, heap/GC, settings,
authentication or instance/world modifications.

Host ASan/UBSan compiles the actual patched SDL pthread sources against native
pthread APIs. It checks unprepared failure,256/128unique leases and exhaustion,
refused later native initialization, mutex recursion/exclusion, condition timeout,
signal/broadcast/reacquisition/protected-data visibility, NULL semantics and10000
lease/reuse cycles with exactly the original256/128native init calls. Target
build/source hashes/export/init-order and package checks are recorded separately.
This is consumer source only in ProsperoCraft, no reusable Java change.

PS5 early reservation acceptance and Fabric26.2 startup, world/render/input/audio,
save/reload, lock/condition lifecycle and endurance remain pending. Preserve130,
accepted124vanilla and Store121. No Store release/frozen milestone; raw reports
remain local. It does not establish a whole-app native-memory cure.
