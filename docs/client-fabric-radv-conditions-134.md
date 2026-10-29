# Fabric26.2 RADV queue native conditions, app134

Current133run's original Minecraft output fails Vulkan device creation with
VK_ERROR_UNKNOWN. Native stderr identifies the actual driver reason:
vulkan/runtime/vk_queue.c83 cnd_init failed. GLFW/window/display/surface creation
succeeded. The launcher correctly rejects original Main returning without clean
shutdown; that check is retained, rather than treating this failed launch as
success. The underlying native initialization return code/resource pressure
remains unproven.

App134 reserves128native pthread condition objects after embedded constructors,
before SDL reserve initialization and JVM creation. Failure reports its native
result and stops initialization. RADV-only bindings redirect pthread condition
init/destroy/signal/broadcast/wait/timedwait to consumer-owned adapters. Mesa's
original C11 implementation and its status/error mapping remain unchanged.

Default-attribute init leases a reserved native condition and records the
caller's opaque condition-object address in a fixed registry. Waits use that
native condition and the caller's original native mutex; timed waits retain
the original absolute time. Destroy returns the lease while retaining the
initialized native object for process lifetime. Callers must have no active
waiters/operations at destruction, as pthread requires. Duplicate active init
returns EBUSY; unavailable/exhausted pools return ENOMEM. Non-default attributes
and unregistered objects, including static initializers, retain their ordinary
native path. Registry synchronization uses allocation-free atomics. No native
condition object is copied, no wait is skipped and no success is fabricated.
SDK platform internals, SDL, GLFW, software OSMesa and general JVM/libc condition
calls keep their existing bindings. Native lock/wait internals may still need
resources; no whole-app memory cure is claimed.

Host ASan/UBSan compiles actual Mesa C11 pthread/time implementations with the
actual adapter. Tests cover failed early reservation,128lease bounds, duplicate
init rejection, refused later native init, timedwait/signal/broadcast/native
mutex reacquisition/protected-data visibility,10000reuse cycles and ordinary
static-condition fallback. Target/package audits require six RADV bindings,
exports and source/object hashes while ensuring they are absent from the shared
graphics binding map. Existing launcher and full-package checks are recorded
in the validation JSON.

This set is consumer graphics/native integration in ProsperoCraft. Java runtime
source/pins, earlier SDL/GLFW reserves, Mesa strings, heap/GC and official game/
modJARs remain unchanged. Instances/worlds/auth/settings are not edited. Preserve
133/priorcanonicalcandidates, accepted124vanilla and Store121. No Store release
or frozen milestone. PS5 Vulkan device creation, Fabric26.2 render/world/input/
audio/save/reload, native queue lifecycle/endurance and working-version regression
remain pending. Raw reports stay local.
