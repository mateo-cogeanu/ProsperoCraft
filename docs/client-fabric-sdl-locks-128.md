# Fabric26.2 SDL reader/writer locks, app128

Build127 failedrun1793275520-7687009 progressed beyond the verifier. The original
Minecraft crash report says GLFW0x10008: PS5 SDL: pthread_rwlock_init() failed.
The previous verifier OOM is absent from this run's report. The underlying SDK
initialization error code was not captured, so heap pressure is a suspected
contributor, not a proven pthread failure diagnosis.

The PS5 SDL port now selects SDL_ps5rwlock.c instead of SDL's pthread RWLock
implementation. A fixed pool of256 locks needs no heap or SDK rwlock object.
Each lock uses a lock-free32bit atomic reader count (negative for writer), with
acquire/release transitions, short spinning and50microsecond kernel sleeps on
contention. Read locks can be recursive and concurrent; writers are exclusive.
Try-lock and NULL behavior match SDL_mutex.h. SDL does not promise FIFO or
writer preference; this implementation makes neither guarantee. Destruction
requires no owners/waiters, as SDL specifies. Exhaustion returns an SDL error,
and a held lock is not recycled. The pool is bounded, not an unlimited lock
allocator. Other SDL synchronization backends are unchanged.

This is a consumer SDL native dependency port, so source belongs in ProsperoCraft.
Runtime129 and its explicit verifier/core temporary-buffer integration remain
unchanged. No game/mod JARs or Java heap/GC settings change. Original SDL's
source export stays pinned; the separate PS5-only CMake patch is included in
port/audit hashes. Other platforms keep the original pthread implementation.

Host ASan/UBSan tests compile the actual port against SDL declarations and
exercise256lock exhaustion/reuse, NULL/try semantics, recursive and parallel
readers, exclusive writers, protected-data visibility and24000 contended
operations. Undefined-symbol checks exclude malloc/calloc/realloc/free and
pthread_rwlock calls from the backend. Target SDL/package audits check that
its resident object has no pthread_rwlock imports and matches new source hashes.
Target app build, launcher host and package checks are in the validation record.
PS5 Fabric26.2 initialization, world/render/save/reload, input/audio and sustained
contention remain pending. No Store release or frozen pass. Preserve127 and
accepted124vanilla; raw reports stay local.
