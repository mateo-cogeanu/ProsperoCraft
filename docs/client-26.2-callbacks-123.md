#26.2callback ABI repair — candidate123

Safari retrieved build122/session identifiers and prior startup/native-stderr/
Java exception reports on2026-10-29. Failed run1793270980-859997175 reaches
original26.2Main, then exits with-1. The Minecraft crash report identifies:

`NoSuchMethodError: Callback$Descriptor.<init>(MethodHandles$Lookup, FFICIF)`

The first failing class is original GLFWErrorCallbackI, called by GLX._initGlfw.
The GLFW3.4.1callback descriptor constructor lacks the explicit callback-interface
Class parameter now required by the resident LWJGL3.4.3core. Earlier936game-method
reference checks missed this dependency-internal call. Caught OSHI telemetry
warnings are not the fatal error. Raw reports remain local under ignored build/.

123recompiles pinned original GLFW3.4.1Java binding sources against core3.4.3.
Only source adaptation: each of26callback descriptor initializers supplies its
own interface Class. A separately packaged binding JAR precedes the original
instance GLFW JAR only for26.2GLFW receipts; a missing binding is an explicit
launch error. Original downloaded game and GLFW JARs remain unchanged/verified.
There is no game bytecode hook or replacement game class.

The new regression initializes all26real descriptors and allocates/invokes/frees
actual libffi error/key closures through generic native JNI entry points. It
checks native-to-Java argument delivery with the actual core3.4.3host library.
The custom host library's stock LWJGL hash warning is retained; it is not a
passing PS5 result.26.2publisher/loader/argument checks and existing snapshot/
startup regressions remain. The on-device missing-constructor cause is fixed
in the binding; later26.2startup/render/input/world behavior is still pending.

123also includes the user's accepted26.4snapshot labels: no Experimental tag,
supported status instead of EXPERIMENTAL and no stale testing-pending wording.
Visibility remains off by default and unlisted future snapshots remain gated.

Test a new Vanilla26.2instance onPS5: title/menu, controls/cursor/keyboard/mouse,
world, sound, save/reopen and clean return. Keep newer worlds separate.122and
public121are preserved; no new Store release/frozen pass/runtime source change.
