# Shader compiler initialization mutexes, app136

Build135 captured the original C++ exception before the formatter abort:
PS5_CPP_THROW type=NSt3__112system_errorE system_error1 code12 (ENOMEM), immediately
after entering native shaderc_compiler_initialize. This establishes a native
resource system_error rather than a Java exception. The raw throw caller is
libc++'s generic system-error throw helper, not the original operation's caller;
it does not alone identify the exact failing lock. Shaderc's initialization
constructor takes first_call_mutex and glslang_mutex; glslang initialization also
uses init_lock. They use libc++ std::mutex, whose SDK native mutex can initialize
on first lock. Late native initialization failures are already proven elsewhere
in this same Fabric launch. The targeted repair follows that path; exact console
acceptance and absence of later resource failures remain pending.

PS5-only dependency patches change those initialization mutex types to
PS5ShaderInitMutex, using the existing pre-JVM reserved SDL native mutex pool.
The wrapper has constant-initialized pointer storage and atomically leases an
SDL mutex on first lock. Concurrent first users safely return redundant leases;
lock/unlock keep native mutual exclusion. The three initialization locks retain their leases for process lifetime. A
trivial destructor preserves constant static initialization without introducing
a lazy C++ destructor-registration guard. Exhaustion reports a
specific stage and retains fatal failure rather than continuing without a lock.
Shaderc's initialization/finalization/refcount logic and glslang's three init_lock
critical sections remain intact. The original deliberately retained process
mutex pointer keeps its existing lifetime. No unrelated libc++ mutex, unwind,
exception or JVM implementation is changed. Host shaderc build uses original
unpached sources; target uses pinned source exports with these separate patches.

Host ASan/UBSan compiles the actual patched shaderc GlslangInitializer bodies
against the actual reserved native SDL mutex source. Process initialization is
represented by checked lifecycle callbacks (not a host shader-compilation claim).
Tests cover8000concurrent compiler lifetimes under a seed owner,1000finalize/
reinitialize cycles, initialization refcounts/first-call serialization,80000
contended lock increments, and no native mutex-init calls after reservation.
Target audits require the patched compiler and ShaderLang objects to use SDL
mutex functions without libc++ mutex::lock calls in these objects, exact shim/
patch hashes and no unexpected automatic constructors. The staged shader compiler
constructor array drops from5to4: only ShaderLang.cpp's mutex destructor-registration
constructor disappears; the exact other four staged constructors remain. App135original-throw
recorder remains enabled to capture any later native failure.

This is consumer shader compiler dependency integration in ProsperoCraft only.
No Java runtime source/pin, game/modJAR, Javaheap/GC, auth/settings/instance/world
change. Existing SDL/GLFW/RADV reserves and Mesa allocator policy remain. Preserve
135/priorcanonicalcandidates, accepted124vanilla and Store121. No Store/frozenpass.
PS5 shaderc creation/real shader compilation/Fabric26.2 render/world/input/audio/
save/reload/endurance and working-version regression remain pending. Raw logs
stay local. No claim that all native resource pressure is resolved.
