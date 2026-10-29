# Fabric26.2 GLFW native mutex lease, app133

Build132's checkpoints complete SDL video/events setup, Vulkan loader handoff,
display enumeration, monitor creation and GLFW platform initialization. The
original Minecraft report then says GLFW0x10008 POSIX: Failed to create mutex.
This is GLFW core's separate pthread mutex creation after the platform hook,
not the previous SDL or Mesa failures. The current raw reports remain local;
exact SDK mutex failure code and overall native allocation pressure are unproven.

App133's consumer GLFW PS5 build applies a separate pinned source patch to its
POSIX mutex backend. GLFW's private mutex state now owns an SDL_Mutex pointer;
create/lock/unlock/destroy delegate to SDL's existing native mutex lease APIs.
SDL already reserves256native recursive mutexes before the JVM. No extra pool,
SDK object creation or alternate locking implementation is added here. GLFW
errors if a lease cannot be obtained; destruction returns the lease and clears
private state. Different-thread exclusion uses the existing native mutex;
recursive capability is inherited from SDL. GLFW's native TLS key code and
all other GLFW platform operations remain unchanged. This backend is selected
only for supported26.2; 26.3/26.4 use their existing SDL route.

Host ASan/UBSan compiles actual patched GLFW POSIX-thread code with the actual
reserved SDL native mutex code. It tests unprepared/exhaustion errors,256leases,
destruction zeroing,80000contended increments,10000reuse cycles and refusal of
all later native mutex initialization. Genuine GLFW/real SDL dummy window tests
still pass monitor allocation refusal, three init/window/event/termination cycles,
Unicode, keyboard, mouse and optional IME ABI. SDL native mutex/condition reserve
regressions also pass. Target/package audits require no pthread mutex imports
in GLFW and all four SDL mutex API references, plus patch/source hashes. The
matching validation record captures target, launcher and full package checks.

No Java runtime source/pin, Mesa allocator, heap/GC, official game/modJAR,
authentication/settings or instance/world changes. Retain130TLSfallback,
131SDLreserves,132Mesastringpairing and diagnostic retention. Preserve132 and
prior canonical candidates, accepted124vanilla and Store121. No Store release
or frozen pass. PS5 Fabric26.2 GLFW completion, window/render/world/input/audio,
save/reload and mutex lifecycle/endurance remain pending. Previously working
versions also need console regression checks before any public release.
