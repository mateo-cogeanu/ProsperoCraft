# Scoped Controlify event delivery, local164

The user accepts16326.2 Vanilla typing but reports automatic keyboard/mouse
handoff still broken with Controlify on26.3 and26.2 Fabric. The user leaves
the app open for retrieval. No release/ProsperoStore submission is made.

## Exact live evidence

Safari retrieved163 session `client-01.000.163-1793385726-499143452`, current
native stderr/game log and startup identity26.3/Fabric0.20.1, with original
Controlify3.5.3+mc26.3. Raw logs remain ignored/local. All16physical-input trace
samples have opened gamepad1, **zero buttons and six zero axes**. The cursor
stays hidden; capture changes from menu to relative gameplay mode. Keyboard
packets are connected, unintercepted, contain valid slots, but
`key_event_posted=0`. These observations do not support a persistent controller
axis/button as the cause of this run's failure.

The exact unchanged Controlify JAR SHA256 is
`bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a`.
Its SDLControllerManager constructor installs SDL_SetEventFilter; its
EventFilter returns true only for SDL_EVENT_JOYSTICK_ADDED1541 and REMOVED1542.
The manager polls SDL_PollEvent for those notifications. SDL's real global
filter rejects all keyboard/text/mouse events and can discard pending events.
The manager assumes ownership of its SDL event stream; separate SDL instances
would isolate these clients. This consumer's resident SDL3 alias shares the
game's SDL, so the mod changes the game's filter
and can drain its queue. The physical events never reach Minecraft/Controlify's
normal keyboard/mouse mode-switch callbacks. Both original filter invocation
and native queue behavior are reproduced in the host test.

## Explicit frontend separation

Reusable runtime [alias symbol lookup](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/abccf72189bc5547e08aab28a923e6d55d13fc33)
is pinned/hash-checked separately. Only three **SDL3 alias** lookups are changed:
SDL_SetEventFilter, SDL_GetEventFilter and SDL_PollEvent resolve to consumer-owned
facade exports in the same ps5sdl group. Base ps5sdl lookups used by Minecraft
and real GLFW/native SDL calls remain the genuine functions. Default runtime
lookup, other aliases, initializer/object lifetime and native implementations
stay unchanged; no arbitrary loader, new platform identity or Java hooks exist.

The frontend retains Controlify's actual filter callback/userdata locally.
It never sets or clears the game's filter. Before JVM startup, it initializes
one process-lifetime SDL events reference and registers an event watch. Failure
aborts startup explicitly. The watch copies only joystick added/removed
records (type,timestamp,ID) into256fixed slots under a spinlock, never rejects
the original event and does not allocate on a push. No pointer-bearing keyboard/
text/audio events enter this queue. Game and mod can consume their independent
connection copies in either order. Poll still pumps the real platform, applies
the mod's filter to its copy and leaves all game events alone. Null polling
peeks. Filter and poll use SDL's main-thread contract; foreign polling fails.
No connection/axis/button/sensor/audio results are fabricated or neutralized.

The queue is bounded, not lossless under unlimited hotplug bursts: overflow
returns an explicit SDL error requiring rescan, without overwriting owned
records. The known manager's main-thread filter/poll behavior is supported;
this is not a full independent SDL instance or a general event-API sandbox.
Game global filters, additional mod event APIs, reentrant filters and repeated
full SDL_Quit/reinitialization in one process need separate design/validation.
The app currently runs one selected game per process. The process-lifetime
watch/queue contains no per-game heap ownership and is reclaimed on app exit.

## Checks and console acceptance

The test invokes the exact original mod EventFilter using its embedded SDL API,
verifying keyboard/text/mouse rejection and connection acceptance. The native
fixture uses real host SDL: original global filter drops physical events;
facade preserves the game filter,5physical event categories, independent
connection copies, order/peek, local filter changes, foreign-thread rejection,
256slot bounds/explicit overflow and1000connection lifecycles under ASan/UBSan.
Existing USB/cursor/trace, launcher and repeat regression checks remain required.
Target source/pins/actual alias tables, full package and exact OpenAL relinks
are recorded in the [validation record](validation/client164-event-isolation.json).

Use exact164 with26.3 Fabric: use controller, release it, then physical mouse
movement/clicks and keyboard typing. Confirm controller prompts/cursor behavior
switches naturally; then use the controller again. Check repeated transitions,
the on-screen Del key/shortcut, gameplay relative mouse look and inventory clicks.
Repeat26.2 Fabric and preserve working Vanilla typing. Check rumble/adaptive
triggers/gyro and controller connect/disconnect after the event change. Leave
the app open at a failure. Exact164 physical acceptance remains pending.

## Local artifact verification

Target compile/link/sign, full package checks and both OpenAL relinks pass.
Actual ELF table inspection resolves relative pointer relocations and verifies
1942exports on each table: exactly3SDL3alias entries point to the real facade,
while the base table and every other alias entry stay unchanged.

- Package SHA256: `1ac6b09c1a812a60b375466debc20dca616aac7d00e66cd52b5611040b52159a`
- Symbols SHA256: `682da77ccf8e5fab89bc7039c633d13bb1eb72656a0066ca642a3496b2a71170`
- Code FNV64: `bffa0b6cb9da5616`

Matching local package/symbols/corresponding-source/relink/checksums are retained.
Console acceptance remains pending; no release or Store publication follows.
