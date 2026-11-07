# Build 263 full Controlify JNI registration capacity

Build 262's matching retained report confirms SDL 3.4.2 loads and initializes
its subsystems. Controlify then fails to register its gamepad and event native
methods because the shared 64-page closure reserve is exhausted. Native stderr
records reserve fallback followed by allocation refusal. The original SDL Java
binding declares 270 native methods across 20 classes, including 70 in SdlGamepad.

Build 263 selects 512 reserved closure pages, shared by JNA and matched333.
At the PS5 page size the bounded reserve is 8MiB. The native builder retains its
64-page default and records the explicit selection. The bootstrap reports the
selected capacity, and packaging checks that its policy matches the native
build. Independent audit checks the actual target metadata size and object hash.
The existing anonymous-first/ENOMEM-only reserve, independently prepared W-to-X
pages and failed-reset quarantine are retained.

The earlier provider test used a small direct-registration set and missed this
capacity limit. The expanded host check initializes all 20 classes from the
unchanged original libsdl4j JAR using real JNA and SDL. A controlled 64-slot
provider reproduces the original registration error. The 512-slot provider
registers all 270 native methods successfully. This controlled provider tests
the binding boundary. The actual x86-64 closure adapter separately exercises
512 real reserved pages, exhaustion/reuse, concurrent callbacks and denied mmap.

Original JNA retains its direct-registration closure pages after unregistering
methods. The expanded test records this behavior instead of claiming reclamation.
Callback-object release remains separately checked. This app replaces the process
after a verified clean game exit, so the reserve is scoped to that process.
Repeated direct registration and arbitrary additional mods can still exhaust a
bounded reserve. The existing upstream JNA bootstrap warning remains recorded.

Exact build 263 SDL discovery, DualSense controls, haptics and gameplay/save/quit
still require physical console confirmation.
