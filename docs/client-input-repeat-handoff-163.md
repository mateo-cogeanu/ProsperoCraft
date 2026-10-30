# Held-key repeat crash and Controlify handoff, local163

The user tested exact162 and reports26.3 Vanilla keyboard/mouse working
flawlessly. Both26.3 and26.2 Fabric with Controlify fail to hand control back to
physical keyboard/mouse.26.2 Vanilla crashes when typing; the user reopens the
app. This narrows issue11: physical HID works on this user's26.3 Vanilla run,
but does not establish universal keyboard hardware support or Controlify
compatibility. The existing161 acceptance remains a distinct earlier report;
these later regression failures block a new release. No GitHub release or
ProsperoStore submission is made.

## Crash identity

Safari retrieved previous-run native/game reports and startup history. The
failed run is client-01.000.162-1793384836-508511676; its launch identity is
26.2/Vanilla/GLFW. Its VM abort status says no fresh VM abort; the downloaded
previous hs_err is dated October29 and is unrelated to this typing crash.
Private logs remain ignored/local.

FTP capture20261030-182800-PPSA99874-103 is an actual **SIGABRT6**, code65543,
Render thread100658,44seconds uptime. The title module base is0x400000 and
text FNV64 **ee6ebfa9d2af4b43**, independently matching retained162 symbols
SHA256 `654b4de6823bc8ccfd5a8fdc4ec0c047c74ba4f1eb2c7337dd0df31b645cf977`.
Exact frames resolve to:

- `__wrap_abort` at ELF0x2beac;
- `clientgpu_ps5___assert` at0x29c351c;
- `_glfwInputKey` at0xfe3208;
- the PS5 platform event `poll` at0xfef958.

Disassembly immediately before0xfe3208 calls the assertion function with
source line277. The pinned upstream input.c line277 asserts that incoming
internal action is PRESS or RELEASE. Our adapter passed GLFW_REPEAT for an
SDL key-down marked repeat. This is invalid for GLFW's internal input API:
that API derives a repeat callback from PRESS while the key is already down.
Other retrieved captures182024 and182712 are stop-observed SIGSTOP snapshots,
not fatal-signal proof.

## Narrow repeat repair

The consumer GLFW adapter sends internal PRESS for every SDL key-down,
including SDL repeat, and RELEASE for key-up. The unchanged original GLFW core
owns key-state updates, duplicate-release handling and public REPEAT callback
classification. No assertions are disabled. Unicode/text routing, modifier
conversion, keyboard layout, original game/mod JARs and Java runtime remain
unchanged. The existing host fixture now passes50held repeats on each of3
real GLFW/SDL window lifecycles (150total), checking callback count and held
state before release, under ASan/UBSan. Full existing window/input/allocator/
IME/Unicode/mouse/close checks also pass.

## Controlify handoff remains unresolved

Original Controlify26.3 SDLEventHandler mixins request KEYBOARD_MOUSE on physical
keyboard/mouse handling unless configured for mixed mode. Its controller tick
can request controller mode again when the current controller reports input.
The exact failing Fabric run's controller state was not captured. We do not
assume stick drift, a stuck button, bad mapping, a configuration problem or
launcher ownership as the proven cause. The162 cursor release conflict was
real but fixing it alone did not establish automatic input-mode handoff.

163 adds read-only snapshots after actual physical key/mouse input: SDL cursor
visibility, relative mode, open gamepad count, number of pressed buttons and
six SDL gamepad axis values. Source requests coalesce, at most one snapshot per
second,16total. No physical key codes or typed text are recorded. No controller
mode is forced; no input values are changed and no synthetic activity is added.
The trace reads existing opened gamepads; it does not open or disconnect them.
Host sanitizer controls check idle silence, source coalescing, throttle, cap,
null focus and absence of mode/input writes. Existing native HID/USB/fallback/
cursor controls remain relevant and are rerun for the changed integration.

## Exact163 console sequence

First26.2 Vanilla: hold a letter and Backspace in a disposable text field long
enough for repeat, then release; confirm typing remains stable. Then test
26.3 Fabric with Controlify: use the controller, release its controls, use
physical mouse movement/clicks and keyboard typing, and leave the app available
while that failure is present. Retrieve the handoff trace before further
restarts overwrite the run. Continue26.2 Fabric handoff after that evidence is
collected. Confirm the162 on-screen Del fix separately once physical handoff
permits normal use. No full input acceptance is claimed yet.

## Build verification

Target compile/link/sign, complete package integrity/version/marker/paired-class/
native-source-hash/runtime-pin/frozen-artifact checks and both ordinary and
replacement-object OpenAL relinks pass. Both relinks reproduce the exact ELF.
Matching source/relink, symbols, package and checksums remain local.

- Package SHA256: `0d7f8f80fd3acc29a2a451494ca8370dc163508bf295938e7e45213c317bdeba`
- Symbols SHA256: `dcda387c4af7a82542db11cdb69e631eb66845040780554f5654c8a65550bd5a`
- Code FNV64: `7b12ef210f5728fd`

[Validation record](validation/client163-input-repeat-handoff.json).
