# Shaderc include mutex lifetime repair, build 160

Local development candidate **01.000.160**, title **PPSA99874**, retains the
explicit Fabric26.2 test marker. No console pass, public support, GitHub release
or Store publication is implied. Original game/mod JARs, runtime pins, budgets,
heap/GC, existing UI and frozen artifacts remain preserved.

## Exact159 evidence

The user reports another loading-screen crash after the previous159 run reached
the menu and crashed on a button. Capture v2 saves an actual **SIGSEGV/code2**,
not merely a SIGSTOP observation: report `20261030-143031-PPSA99874-128`, timestamp
2026-10-30T14:30:31Z, PID128, Render thread100651, outcome crashed. Raw registers,
stack, account/path-bearing logs and modules stay ignored/local.

The main executable's first64KiB FNV64 is `d8f875f125c39199`, matching the retained
159 ELF. That ELF's full SHA256 is
`899b93f34e0f9910707f9664776a6f244ba826190a7d62831b33496fb318f602`;
its package is `2e8d5b7523376f4231fc843e9b2e67feaefdde1655b9ff271c3907a3fc4c1686`.
The capture identifies load base0x400000. No unrelated symbols were substituted.

- PC: `libkernel.sprx+0x3d910`, fault address `0x72e6b8`.
- Caller0x18e9c67 minus0x400000 -> ELF0x14e9c67 in
  `CompileToSpecifiedOutputType`; preceding call0x14e9c62 targets PLT0x2a6b6a0.
  Its GOT0x4d27070 relocation names **pthread_mutex_destroy**.
- Next frame0x18e9584 -> ELF0x14e9584, `shaderc_compile_into_spv`.
- RDI points at the stack's native-mutex storage. Its captured eight bytes are
  `0x72e690`, equal to RBX; fault address is that value+0x28. This lies in the
  executable's code range, not a valid owned mutex. It is consistent with the
  earlier ShadowMount SYSTEM_XO_VIOLATION class. This report is stronger evidence
  than the final shader progress message alone.
- The exact target shaderc object independently retains a relocation to
  pthread_mutex_destroy in **CountingIncluder destruction**. Its constructor
  calls pthread_mutex_init but ignores its return; pthread_mutex_t storage is
  not initialized first. Include lock/unlock results are ignored too. Thus
  failed initialization permits lock/destroy of indeterminate storage. The
  console init return itself was not captured, so ENOMEM at that exact call
  remains an inference supported by the known pressure and host failure control.

## Narrow repair

The target-only private CountingIncluder header uses a per-instance in-object
nonrecursive atomic lock. It requires no SDK mutex object, allocation, lazy init
or native destruction. Acquire/release exclusion preserves serialized include
callbacks. Finite spinning yields to a50microsecond nanosleep under contention;
no FIFO guarantee is added. RAII guards release the lock on delegate exceptions.
The caller still must finish concurrent callbacks before destroying its includer.
ReleaseInclude remains independently callable, as upstream specifies.

Other platforms keep the original shaderc_util mutex; global SDK, runtime,
shaderc initializer locks, parser semantics, shader contents, compilation errors
and include callback results are unchanged. This does not suppress errors or
return fabricated shader success. No native pool/budget increase is introduced.
The existing explicit constructor staging and initialization reserves remain.

## Checks

`test_shaderc_include_mutex.py` compiles the actual pinned CountingIncluder and
actual glslang Includer interface. With pthread init forced to ENOMEM,1000
poisoned-storage original instances still call lock/destroy: the unsafe lifecycle
is reproduced. The exact patch/header then pass1000construction/delegation-error/
unwind/reuse cycles and80000includes on8threads, with exclusive delegate access,
correct counts and **zero native mutex init/lock/destroy calls**, under ASan/UBSan.

Existing actual shaderc initialization reserve tests pass8000concurrent compiler
lifetimes,1000finalize/reinitialize cycles and80000contended increments. Diagnostic
signal/ownership checks and development gate checks remain required. Target
rebuild verifies original SDK/library dependencies, exact new header/patch/object
hashes and absence of pthread mutex init/destroy references from shaderc.cc.o.
The full consumer package check verifies version, native integration, signatures,
CRC, runtime pins, original fixtures and preserved packages. Host/target checks
are not physical-console shader or gameplay acceptance.

## Next exact160 console run

Install the local160 app through the existing workflow. Keep the capture v2
payload running; it should attach to the new process. Use the disposable26.2
Fabric instance and confirm the selected version/loader in logs. Test loading,
menu button/held transitions, Controlify discovery and audible sound first.
Leave the console available at the first failure for capture and log retrieval.
If that passes, continue the full [159 lifecycle checklist](client-fabric262-development-159.md#console-test-sequence--all-pending-for-exact-159)
on160: requested physical rumble/adaptive triggers/gyro, fresh world/chunks,
recorded gameplay, marker save/reload, application restart persistence, repeated
audio/input transitions and relevant working-version regressions. None is yet
accepted for160. A menu pass alone does not complete Fabric26.2 support.

## Console follow-up

The user reports audible menu music and a visible selection change after a
button, immediately followed by a crash. Launcher logs confirm26.2/Fabric0.20.1
on160. An exact160 external stop snapshot shows SDL TLS/error recursion; it
does not carry a fatal signal. See [161 investigation](client-sdl-thread-storage-161.md).
Shaderc no longer blocks this run from reaching the menu, but this is not full
shader/gameplay acceptance. Repeated input, physical features and worlds remain
unvalidated.
