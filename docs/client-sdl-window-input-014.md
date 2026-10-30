# Client SDL Window/Input 01.000.014 — pad initialization and discovery

Client013 passed the earlier Vulkan/compute rows and explicit companion loads,
then failed SDL check11 with `No SDL gamepad`. Session
`client-01.000.013-1792838974-537697485` was retrieved on2026-10-24.
SDL video and fullscreen window creation returned successfully before enumeration;
no controller-input or SDL-surface pass is established by that alone.

The input adapter called scePadInit after the bootstrap had already initialized
UserService/Pad and closed its start-button handle. A negative repeated-init
return would reject the adapter before actual pad discovery; no native error
number was captured in013, so this remains a suspected cause.014 reuses that
explicit bootstrap-owned service lifetime while still requiring actual initial
user retrieval and successful scePadOpen (or a real existing handle).

014 also pumps real SDL events/joystick updates and retries gamepad discovery
for up to10seconds rather than accepting an empty initial snapshot as final.
If discovery fails, it reports joystick inventory separately from mapped gamepads.
Native adapter diagnostics now route directly into persistent probe checkpoints.
No controller is synthesized on PS5 and no empty inventory is treated as success.

Host ASan/UBSan tests compile the actual platform-input.c with explicit host OS
call fixtures: a repeated scePadInit is configured to fail and verified never
called; actual adapter open/read/button/axis/release/disconnect paths pass.
That test does not validate PS5 hardware. Existing real-SDL host virtual-input
state/event/ABI tests remain separate evidence. Target package checks and exact
hash are recorded in client/sdl/status.json. Frozen milestones and failed013's
exact package/symbols are preserved. JVM/SDK and original game/SDL/Vulkan JARs
are unchanged; the consumer native input adapter and Java discovery loop change.

Install **PPSA99874 01.000.014** from `dist/client-sdl/PPSA99874.zip`, also at the
runtime workspace's current `dist/PPSA99874.zip`. Wait for Client014 ready,
release and press X once. At Input ready, supply X, Circle, D-pad Left and a
strong left-stick movement. Confirm automatic PASS and the full-screen pattern.
Keep it open for reports; after a crash reopen without pressing X.

All twelve014 PS5 checks and input/visual confirmation remain pending. SDL/GPU
resources stay retained through JVM shutdown; teardown/resize/reconnect/focus/
recovery/audio/callbacks/gameplay and server two-hour endurance remain unvalidated.

## Console acceptance

The user confirms “tiles nice, inputs all accepted” on2026-10-24. Retrieved session ALL12 PASS and logs verify eventMask15/stateMask15,537 graphics/sample/guard/FIFO frames and DestroyJavaVM complete. Exact tested source/package and evidence are frozen in [Client_SDL_Window_Input](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_SDL_Window_Input/README.md).
