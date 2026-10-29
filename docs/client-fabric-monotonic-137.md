# Fabric26.2 timeline condition clocks, app137

Build136 failedrun1793289587-412720889 returns successfully from native shaderc
compiler initialization. The original Minecraft report then fails to create a
submit VkSemaphore with VK_ERROR_UNKNOWN. Native stderr identifies
vk_sync_timeline.c123 cnd_init failed. This path uses u_cnd_monotonic_init,
which explicitly creates condition attributes selecting CLOCK_MONOTONIC. The
prior134adapter intentionally passed non-default attributes to late SDK native
initialization, so it did not cover this timeline condition. Overall native
resource pressure/SDK return codes remain unproven.

App137 keeps128realtime conditions and additionally reserves128native monotonic
conditions before JVM startup. Native condattr initialization and setclock must
succeed there; actual failures stop startup with the existing native result log.
The RADV-only adapter now also scopes its three condition attribute operations
(init/setclock/destroy) to a64entry fixed metadata registry. Its known attributes
retain default realtime or explicit realtime/monotonic selection. Invalid clocks
return EINVAL, repeated active init EBUSY and exhausted metadata ENOMEM.
Condition creation leases from the corresponding native clock pool, never
substituting realtime for monotonic. Clock selection remains with the condition
after attribute destruction, as pthread requires. Foreign attributes and static
or unregistered native condition objects preserve their original path. Other
attribute policies are not emulated or added; only RADV's observed three APIs
are redirected. General SDK/SDL/GLFW/JVM calls remain unchanged.

Wait/timedwait/signal/broadcast continue using native objects, original caller
mutexes and original absolute deadlines. Destruction requires no active users
and returns the lease for reuse. No operation is skipped or falsely succeeds.
The condition registry is allocation-free and bounded; lock/wait internals can
still consume native resources. No blanket native-memory cure is claimed.

Host ASan/UBSan compiles actual Mesa POSIX u_cnd_monotonic routines and the actual
adapter, testing independent128/128pool limits,64attribute bounds, invalid clocks,
realtime+monotonic deadlines, signal/broadcast/mutex reacquisition/data visibility,
10000reuse cycles and no late initialization. macOS lacks native condattr_setclock,
so its native-clock fixture records selected clocks and implements monotonic
waits with native pthread_cond_timedwait_relative_np. This is host behavioral
coverage, not evidence of the PS5 clock implementation. The existing actual
Mesa C11 realtime wait/failure/static-object regression also passes. Target
native compile checks and final RADV-only nine-symbol routing/source/object
hashes plus package checks are in the matching validation record.

Consumer-only source in ProsperoCraft; no Java runtime source/pin, heap/GC,
official game/modJAR, auth/settings or instance/world change. Earlier compiler,
SDL/GLFW and allocator fixes remain. Preserve136/priorcanonicalcandidates,
accepted124vanilla and Store121. No Store release/frozen pass. PS5 early monotonic
reserve acceptance, semaphore/device/render/shader compilation/world/input/audio/
save/reload/endurance and working-version regressions remain pending. Raw logs
remain local.
