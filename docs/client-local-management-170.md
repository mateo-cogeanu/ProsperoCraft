# Local candidate 01.000.170: launcher editing and local content manager

This is a **local physical-console test candidate**, not a release or Store update.
Input switching and web management have host coverage; exact PS5 acceptance remains
pending separately for each. An opt-in PS5 AudioIn/OpenAL capture path and local meter test are implemented;
DualSense speech, hardware mute and full voice chat remain **console-pending**. See [microphone investigation](controller-microphone-investigation.md).
The existing Minecraft version/loader policy and original publisher JARs are unchanged.
No runtime source change is required for these two launcher features.

## Editing and input ownership

The existing launcher edit screen retains its text buffer, original cancel value,
field purpose and return screen when devices change. It remains append/backspace
editing; there is no new caret/selection facility. Physical typing, keyboard
navigation, mouse clicks and wheel activity select physical editing and hide the
character grid. Enter confirms; Esc/right click cancels. Name validation and the
40-character limit remain. Instance creation, rename and content-search flows
share this policy. Controller button edges or meaningful left-stick navigation
restore the character grid. The existing stick threshold56/release28 policy stays;
gyro and mouse movement never select an editing mode. Held stick repeats cannot
restore the keyboard while physical mode is active. Last-keyboard disconnect or
interception restores controller editing; release/rearm prevents held-on-connect
characters. Each text character still travels through one HID text-command path.
Launcher HID ownership still ends before Minecraft starts. In-game editing and
Controlify arbitration are unchanged.

## Opening and pairing

Open **Instance Settings → Manage from phone / browser**. Keep this screen open.
After the listener is bound and discovery succeeds, the launcher shows the selected
instance's QR URL, the identical readable URL, a random32-hex-character pairing
code and actual service status. Type that URL in a browser or scan the QR; enter
the code on the browser pairing screen. The home page lists all instance IDs/names,
versions/loaders; direct `/instance/<stable UUID>` pages retain home navigation.
Left/right on the console cycles available addresses rather than choosing an
arbitrary first interface. Circle/Esc/right click stops the service and revokes
access. Return to this screen to restart and generate a new code. Port8092 is the
default; `ps5.launcher.web.port` permits a configured port (0 requests an available
port). The displayed port always comes from the bound socket.

`NetworkInterface` uses the existing runtime libnet interface enumeration, backed
by native `getifaddrs` and its existing route/flags fallback patches0076/0081.
Only up, non-loopback interfaces with RFC1918 IPv4 addresses are advertised;
link-local/public IPv4 and IPv6-only networks are currently unsupported. Multiple
addresses are sorted and explicitly selectable. Discovery refreshes every3seconds
between requests, removes stale URLs and revokes sessions on address changes or
query failure. During a bounded upload it refreshes after that request. A bound
listener and interface address do not prove reachability from a phone: Wi-Fi
isolation, firewalls and actual PS5 networking remain physical-console checks.

The service uses a separate listener and one daemon worker, one accepted socket,
backlog4, header timeout5seconds and bounded body/cleanup time. It is available
only on this launcher screen, never while Minecraft is starting/running or the
app is closed. Entering the screen requires idle launcher workers. Browser
mutations lease launcher ownership; other launcher actions wait until cleanup
finishes. Closing the screen closes listener/active socket and cancels pending
streaming work. A file already committed before cancellation remains installed.
Repeated service restarts and stop/join are tested on the host. Console resource
quotas and endurance are unmeasured.

## Content scope

| Destination | Accepted transport formats | Consumer requirement |
| --- | --- | --- |
| `mods/` | `.jar` with a readable ZIP directory and `fabric.mod.json` | Fabric instance; exact game/mod/dependency compatibility still required |
| `resourcepacks/` | `.zip` with `pack.mcmeta` | Matching resource-pack schema/version; select in Minecraft |
| `shaderpacks/` | `.zip` containing `shaders/` | Fabric with compatible Vitrail; upload does not install Vitrail or activate a pack |
| `schematics/` | `.litematic`, compound NBT/gzip signature | Matching Litematica and dependencies, using its default directory |
| `config/worldedit/schematics/` | `.schem` or legacy `.schematic`, compound NBT/gzip signature | Matching Fabric WorldEdit, default schematic directory and required world permissions |

These are **explicit transport destinations**, not a claim that Litematica or
WorldEdit has passed on PS5. Neither is auto-installed. Schematic NBT schema,
data-version migration, legacy block conversion and permissions are checked by
the consuming mod, not this uploader. Custom schematic directories are not
followed. Create `.nbt`, arbitrary directories, worlds and save deletion are
outside scope. Litematica's default is documented in its [upstream README](https://github.com/maruohon/litematica#schematics).
WorldEdit documents [config locations](https://worldedit.enginehub.org/en/latest/config/)
and [schematic formats/directory configuration](https://worldedit.enginehub.org/en/latest/usage/clipboard/).

The browser lists filenames/sizes, uploads multiple files sequentially with
progress/cancel, refreshes lists and confirms removal of user content. Existing
filenames return409; there is no silent overwrite. Modrinth-managed files must
use the launcher's receipt-aware uninstall operation. Uploaded files get no
fabricated project identity/dependency receipt. Rename/duplicate and content
enable/disable remain in the native launcher where supported; this service does
not expose arbitrary filesystem operations. Reopening the native Installed view
reads the real folders after browser changes.

The original170 upload is limited to128MiB (superseded in [213](client-browser-uploads-213.md)) and streams through a64KiB buffer into an owned
`.prospero-upload-*.part` in the destination. Same-directory move publishes the
complete file without a replacement flag; filesystem atomicity remains platform
specific. Failure, disconnect, quota/full-volume error and cancellation remove
staging; stale owned staging files are reclaimed on the next mutation after a
crash. Filenames are bounded to120 simple ASCII characters. All ancestors are
checked for links, destination traversal is rejected, archive paths are inspected
without extraction, ZIP directory count/size is bounded before `ZipFile` allocation
(8192entries/4MiB; no ZIP64/split archives). No upload is executed by the service.
The PS5 capacity API is presently unsupported, so no free-space number or
pre-reservation is invented: real ENOSPC/quota write failures are authoritative
and tested with injected full-volume errors. Budget conservatively when uploading.

## Access and theme model

The listener binds available interfaces without a client-IP filter. Host validation
accepts only current advertised addresses; origin/custom-header checks protect
mutations, cookies are HttpOnly/SameSite Strict, and no cross-origin permission
headers are sent. Pairing allows5attempts/minute. One paired browser session expires
15minutes after pairing; pairing another browser replaces it. Disconnect browser,
closing the console screen, service restart and network changes revoke it. Codes
are never placed in URLs/access logs. Only public instance metadata and generated
theme colors enter `/api`; account/refresh/key files have no routes. Invalid HTTP
framing, duplicate headers and oversized requests are refused. This is a scoped
implementation with host tests, not an independent security audit.

**Local HTTP is unencrypted.** Use a trusted network: peers capable of observing
traffic can steal codes/cookies/files. Binding all interfaces does not guarantee
LAN-only exposure. No certificate, router/port-forwarding or system setting is
installed/changed. The existing runtime-owned read-only log service remains
separate and unchanged, including its [open security follow-up](security-follow-ups.md).

`client/launcher/theme-tokens.json` maintains the native hue table and browser
base tokens. `tools/generate_theme_tokens.py` generates the C++ and Java versions
with the same recoloring formula. Browser `/api` polling every5seconds learns
current theme tokens. Changing the theme through the launcher requires leaving
this screen, which revokes the current browser; reopening/pairing uses the new
theme. Home uses the exact native launcher instance-icon pixels, themed instance cards,
and the same hue tokens. An instance opens four content-category buttons, with an
explicit Litematica/WorldEdit choice under Schematics, then file selection/upload.
Compatibility and connection detail is tucked into expandable help. Browser assets,
fonts (system stack) and scripts require no CDN. Nayuki QR
source is MIT-licensed, pinned with original file hashes in `qr-source.json`; its
license is included in the application and the complete source is in this repo.

## Exact PS5 test plan

1. Install the matching170package after preserving your existing app data. Use a
   disposable instance for upload/removal and schematic/mod compatibility tests.
2. Exercise controller-started creation/rename/search edits; unfinished text across
   repeated keyboard/controller switches; Enter/Square confirmation, Circle/Esc
   cancellation, backspace,40-character validation, last-keyboard disconnect and
   controller-only operation. Check for duplicate characters and drift flicker.
3. Open web management. Verify detected address/QR on phone and desktop; manual URL
   and pairing; multi-address choice, network loss/change, binding failure/retry,
   expiry/revocation and repeated restarts. Keep the management screen open.
4. Upload valid content for each destination, check duplicate/error/progress/cancel
   and interruption cleanup; remove disposable user files and refresh native lists.
   Confirm existing worlds, receipts/accounts and original game/mod JARs remain.
   Check full storage failure without damaging valuable data. Install only trusted,
   compatible mod versions; actual schema/render behavior is a separate test.
5. Close management while an upload runs, then launch Minecraft only after cleanup.
   Verify service unavailable during play and after app exit; game audio, input,
   rumble/gyro/triggers, save/reload and repeated transitions remain intact. Record
   session duration and resource/FD behavior, not just successful startup.

Host checks, candidate checksum/symbols and remaining boundaries are recorded in
[validation](validation/client170-local-management-2026-10-31.json). For microphone testing, use Instance Settings → Microphone and the separate
[AudioIn/voice-chat plan](controller-microphone-investigation.md). Do not substitute
phone/headset audio or record anyone without consent.
