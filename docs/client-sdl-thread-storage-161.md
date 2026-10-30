# SDL thread-storage failure repair, build161

Local development **01.000.161**, PPSA99874, retains the explicit Fabric26.2
package marker. Public release158 and its Fabric26.2 hold remain unchanged.
No release, Store submission or console pass is implied.

## Exact160 evidence

The user heard music in the menu and saw a button change the selected option,
then the app crashed. Retrieved launcher logs identify **26.2 / Fabric0.20.1**
on160; run client-01.000.160-1793377739-75158716 precedes the reopened app.
This confirms audible menu output and one visible input response, not controller
feature acceptance or sustained stability.

External capture20261030-162943-PPSA99874-92 has outcome **stop-observed**,
SIGSTOP17/code0, Download-4 thread101939, SP0x1066240000. It is a snapshot
before detach, not proof that SIGSTOP killed the title. Render-thread and audio
stacks are observations rather than fatal callers. Raw reports remain local.

The independently calculated first64KiB FNV64 **b2ffd59b34da92ea** matches the
retained160 executable (SHA256
bec7f3d20a2be1f4b477ee58a19773260ff39303fbf94547096da7a4287f7347).
Its package SHA256 is
cb7e730ad7ef5d71cfad24892b3d6698069d2e69cbf51da88017d87ad06f6cb6.
Exact symbolized frames repeatedly cycle through:

- SDL_SetTLS+0x133 (ELF0xf4a283), following SDL_SYS_SetTLSData;
- SDL_GetErrBuf (0xf4a691), creating the error buffer;
- SDL_SetError (0xee4d7d), attempting to report the TLS failure.

Disassembly of SDL_SYS_SetTLSData at0xfdb940 shows pthread_setspecific's
nonzero result tail-calling SDL_SetError at0xfdb971. Source confirms that error
creation then calls SDL_SetTLS again before an error buffer is installed. The
recursion is concrete; the SDK return value and underlying allocation owner
were not captured. Button timing does not establish that the button itself
caused this failure on Download-4.

## Repair and ownership

Only the private pinned SDL export changes. PS5 uses upstream SDL's existing
generic thread-ID keyed storage, avoiding SDK pthread key/set/get calls on
foreign JVM threads. Bootstrap explicitly creates its one recursive mutex from
the existing256-object SDL reserve before JVM startup; failure aborts launch.
Access before bootstrap fails closed. That mutex lease is retained across SDL
quit/reinit, so reinitialization needs no late SDK allocation. Other platforms
keep their pthread backend. There is no new global allocator or TLS interposer.

Thread-ID lookup, exclusion, per-slot destructors and cleanup remain. Only TLS
store/list-node allocation uses non-reporting private helpers; these keep the
configured SDL allocator, allocation counters and SDL_free pairing. Ordinary
SDL_malloc/realloc still report OOM normally. This distinction matters because
those ordinary wrappers themselves call SDL_OutOfMemory on refusal, which would
otherwise reenter error creation during bootstrap. Foreign threads still require SDL_CleanupTLS; automatic cleanup
of foreign JVM threads is not added. Generic lookup is linear in active stores,
so console endurance and foreign-thread retention need measurement.

If allocating an error buffer, TLS store or list entry fails, the uninstalled
buffer is freed and error creation returns NULL. SDL_SetErrorV then returns
false without recursion or shared writable fallback. A refused message-string
allocation leaves SDL_GetError returning an empty string, never NULL. Existing
errors remain per-thread. Allocation counters count live stores, not resizes,
so a grown store can still be fully cleaned up at quit. Native API failures
are not changed into success. Heap/GC, Java runtime pins, synchronization
capacities, game/mod JARs and input/audio behavior are unchanged.

## Validation

`test_sdl_thread_storage.py` compiles the actual exported TLS routines,
pthread-backend selection, error routines and actual allocator wrappers/helpers,
with upstream TLS/error structs. A forced SDK refusal in the pinned original
reproduces32recursive error-creation attempts before the fixture stops it.
ASan/UBSan cover four refused allocation sites, cleanup of partially installed
state, retained existing storage on failed growth,8threads/8000lifetimes,
160000slot destructors, error isolation, resizing, and quit/reinit. Existing
SDL native sync and RWLock controls also pass. Target package checks pass and require
preinit export, exact patch hash and no pthread/error references from the
actual SDL_systls object. The complete target build, package integrity/pin/frozen-artifact checks and both
normal/replacement OpenAL relinks pass. Both relinks reproduce exact ELF SHA256
f768a4dccfb42e0f4a882a224d4d0b210de7f8d98320847490761dce6a7575b8.
The local161 package SHA256 is
a34f95fd19f08a6d51485eeac7117172da95e9ea7ed4b9022abe6e0780d2e59f.
See [validation record](validation/client161-sdl-thread-storage.json).

## Console checks still required

Use exact161 and the disposable26.2 Fabric instance, with capture v2 running.
First test loading, audible music, repeated/held menu buttons and transitions.
If stable, continue Controlify rumble, adaptive triggers, gyro, a fresh world,
chunk movement, save/reload with a marker, app-restart persistence, audio/input
transitions and recorded endurance. Check existing Vanilla26.2/26.3 and supported
26.4 regressions. Leave the app available at the first failure for retrieval.
No world or physical-controller feature pass follows from the160 menu report.

## Physical-console feedback

The user reports exact161: “all works! everything i mean!!”, including deletion
on26.2. This is user acceptance of the requested Fabric26.2 functionality. No
session duration, marker coordinates or per-feature measurements were supplied,
so no measured endurance claim is added. The user requests fixing a separate
26.3 Controlify keyboard delete regression before any GitHub/Store release.
Candidate161, its symbols and corresponding source/relink are preserved.
