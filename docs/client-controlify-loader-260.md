# Local build 260 Controlify native loader failures

Build 259 still crashes on the user's 1.21.11 Fabric instance. Its retained
startup report confirms all three JNA checkpoints, a real SDL version of
3.4.2 and the three scoped event symbols. The Java log ends during Controlify
pre-initialization. The retained native trace records allocation refusals and
ends in a native null-pointer fault. The fault has a null destination pointer. Its source pointer resolves, using
the retained exact-build symbols and verified image adjustment, to the resident
loader's missing-library error string. It does not establish a complete Java
stack for the fault.

Pinned JNA's Unix loader-error helper calls malloc then strcpy without testing
the result. The original optional HID4Java service attempts a native library
that this runtime does not provide during Controlify pre-initialization.
Host fault injection reproduces a native crash when the error-buffer allocation
is refused. This identifies a concrete unsafe failure path consistent with the
console evidence. Its responsibility for the reported console crash remains
to be validated.

Build 260 explicitly integrates the runtime's checked JNA loader errors.
The actual open, close and symbol lookup entrypoints retain Java errors when
error-buffer allocation fails or loader error text is unavailable.
The original JNA Java, HID4Java, Controlify and game downloads stay intact.
The native implementation, patch and build tooling live in the Java repository.
The consumer pins both the original target object and its resident group.

The runtime's original-source negative control faults under ASan. The patched
JNI operations pass the text/missing-text/allocation-refusal matrix under
ASan/UBSan. Genuine rebuilt host dispatch passes JNA initialization, native
sizes, error state, memory/string operations and real libffi calls.
Physical title-screen startup, controller handoff, world play and quit on this
exact candidate remain pending. An underlying allocation-pressure cause also
remains unresolved.

See the [exact candidate record](validation/client260-controlify-loader-2026-11-07.json).
