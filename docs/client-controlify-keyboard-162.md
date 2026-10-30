# Controlify26.3 keyboard deletion, local build162

The user reports **all requested functionality working on exact161**, including
Fabric26.2 keyboard deletion. This is physical-console user acceptance, not a
new measured endurance result: no duration, coordinates or individual feature
measurements were supplied. The retained161 package is
`a34f95fd19f08a6d51485eeac7117172da95e9ea7ed4b9022abe6e0780d2e59f`;
its symbols and corresponding source/relink remain preserved. Latest retrieved
build/session identify161 and26.2/Fabric0.20.1/Controlify3.5.3+mc26.2.

The user separately reports that Controlify’s keyboard delete does nothing
on26.3 and requests that repair **before** any GitHub/ProsperoStore release.
This work creates local162 only. The public158 download and its support gate
remain unchanged. No release or Store submission is authorized here.

## Cause in original artifacts

The original verified Controlify3.5.3+mc26.3 Fabric JAR SHA256 is
`bc759f557d122079bb9078741065935bf3aa9bfd5e60b414e242633c0dded86a`
(Modrinth versionfo76vL20, retained from the publisher-verified trigger fixture).
`KeyWidget.onPress` passes `(42,0,0)` to `InputTarget.acceptKeyCode` for the
Backspace special action. `EditBoxInputTarget` constructs the original
Minecraft `KeyEvent` with those three integers. In26.3, its first field is the
key position and its second is the key value/shortcut. The original EditBox
switches on `shortcutKey()` and expects **8** for backspace; zero is ignored.
This is a Java-level mod/game input mismatch, upstream of SDL/native events.
Changing physical key delivery cannot repair this direct synthetic event.

The host fixture reproduces the no-op on an actual original26.3 EditBox.
Supplying `(42,8,0)` through the actual original Controlify input target deletes
correctly. No game class, mod class, bytecode hook or downloaded JAR is changed.

## Supported resource configuration

`ProsperoControlifyKeyboard` runs before Main, after preparing the selected
instance. Only26.3/Fabric with the exact known mod SHA gets an override. The
helper reads the three existing full/simple/server-IP keyboard layouts from the
installed original JAR. It changes only each Backspace function to the supported
`CodeFunc`, with codec fields `keycode:42`, `scancode:8` (historical mod field
names) and default modifier0. The shortcut, dimensions, other keys and localized
`controlify.keyboard.special.backspace` label stay intact.

The generated normal resource pack contains those JSON layouts, compatible
97.1 pack metadata, an ownership marker, upstream LGPL3 license and provenance.
It contains no classes or game assets. Original game/mod JARs are read only.
The pack is appended once to the selected resource packs, preserving existing
order and unrelated options; exact original options are backed up before change.
Subsequent launches do not rewrite/re-enable it after the user disables it.
A changed/removed/duplicate Controlify mod removes only the owned override and
its selection, so a future fixed mod does not retain a stale layout override.
An unrelated colliding filename or malformed options are left intact. Startup
logs only a bounded status, without paths/account information; optional failure
does not prevent Main. The repair does not apply to26.2, Vanilla or snapshots.
Existing custom packs can be ordered above this normal override or it can be
disabled through Minecraft’s resource-pack settings.

## Checks

`test_controlify_keyboard.py` uses the actual original mod’s layout codec,
original Minecraft pack-metadata codec and original Minecraft EditBox through
Controlify’s original input target. It checks all three layouts, reproduces the
old no-op, then verifies end/middle/selection/Unicode deletion, repeated deletion
and empty input. The fixture changes focus only through reflection to avoid a
running graphical Minecraft singleton; no replacement game classes are used.

Installation controls verify unchanged original mod bytes,26.2/Vanilla exclusion,
retained pack order/unrelated options/exact backup, idempotency, explicit user
disablement, cleanup after a mod update/removal, malformed options and unowned
filename collision. Actual startup policy/observer/native-allocation checks,
launcher development-gate checks and target/package/relink results are recorded
in the [validation record](validation/client162-controlify-keyboard.json).

## Exact162 console check

Open26.3 Fabric and test both the highlighted Del key and its controller shortcut
in the Controlify keyboard. Check single and held deletion, selected text,
server address/chat fields, and close/reopen the keyboard. Confirm typing and
other keyboard actions remain as before. Then make a quick26.2 Fabric keyboard
and gameplay regression check;161’s prior acceptance is preserved.162 is a
local development candidate until this exact-build console check succeeds.
No new GitHub/Store release is created by this work.

## Issue11: physical USB keyboard and Controlify pointer

[Issue11](https://github.com/mateo-cogeanu/ProsperoCraft/issues/11) reports no
physical keyboard input on117/26.3 Vanilla and a flickering, unclickable mouse
with Controlify. It has no logs or follow-up comments.117 uses the same native
HID packet layout/discovery and input adapters as161; a newer app alone does
not establish a fix. The pinned [device-tested ABI reference](https://github.com/ZiZc3/Ruffle-Flash-PS5/blob/1265f473e7479d6c0fcfb78cc160a0eea446bb08/src/hid.rs)
agrees with the current96-byte keyboard and40-byte mouse record definitions.
No speculative ABI or service-privilege change is made.

There is a concrete cursor ownership conflict: while a gamepad consumer owns
the controller, every fallback pump calls TempRelease and hides the shared
hardware cursor. Physical mouse reports then show it again, regardless of SDL
cursor visibility.162 releases fallback ownership once per handoff, preserves
physical event routing, and respects SDL visibility/relative capture. It updates
the retained pointer after visibility changes even without a new HID packet.
No idle motion/button event is invented; the game/mod retain input-mode policy.
The actual117 header reproduces repeated hide/show churn in the combined host
fixture; both patched adapters pass100stationary-report/idle/click/handoff/
focus/capture/visibility cases under ASan/UBSan. This fixes that demonstrated
conflict; physical acceptance and any remaining Controlify click/mode issue
still need the console test.

The physical keyboard's root cause is **unproven**.162 logs first read result,
bounded connect/interception transitions, record length, presence/count of
valid key slots and whether SDL posted a key event. It never records key codes
or typed text. The per-port record budget is12 plus one first-read and one
entry per event-post result; error retries share the record budget. SDK user/
module/open diagnostics remain local. Existing sanitizer tests cover normal
key/text/modifier/repeat/focus/interception/read-error routing, native import/
lookup/index handling, and bounded diagnostics. Host fixtures cannot prove the
reporter's device delivers packets.

The user has a keyboard and mouse and agrees to test. Connect both before162;
first test26.3 Vanilla WASD/text/backspace, then26.3 Fabric Controlify movement/
clicks/virtual-keyboard deletion, and leave the app/log server available. The
physical keyboard report remains open until those diagnostics identify the
actual failing boundary and physical input is confirmed. No issue comment is
posted and no issue is closed by this work.

## Local artifact verification

Build162 compiles, links and signs successfully. Full package integrity,
version/development marker, paired launcher/startup/helper classes, final SDL
source hashes, runtime pins and preserved artifact checks pass. Both ordinary
and replacement-object OpenAL relinks reproduce the exact executable.

- Package SHA256: `50ef004e14551cf46e2f9b83d5349dd78eddeb2ba1370a740089f1e9bf55961e`
- Symbols SHA256: `654b4de6823bc8ccfd5a8fdc4ec0c047c74ba4f1eb2c7337dd0df31b645cf977`
- First64KiB code FNV64: `ee6ebfa9d2af4b43`

Matching package, symbols, OpenAL source/relink and checksums are retained in
the ignored local candidate directory. Console results remain pending.
