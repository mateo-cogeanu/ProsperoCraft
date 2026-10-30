# Handle-specific Controlify FFM lookup, local165

The user reports continued handoff failure on164/26.3 and26.2 Fabric. Safari
retrieves the exact runs `client-01.000.164-1793386587-330541175` (26.3) and
`client-01.000.164-1793386771-762069120` (26.2). Both have scoped-event preinit
success, but no `PS5_CONTROLIFY_EVENTS scoped_filter` invocation marker.
Physical keys still log post0 and the sampled controller is neutral. Private
reports remain ignored/local.16326.2 Vanilla typing acceptance is preserved.
No release or Store submission is made.

## Missing integration in164

The compiled alias tables were verified correctly, but that check did not cover
how the real FFM backend obtained its function addresses. Its unchanged
`SdlNativeLibrary.configure()` default branch calls `System.loadLibrary("SDL3")`
and binds `SymbolLookup.loaderLookup().or(defaultLookup())`. Loader lookup
searches libraries associated with the class loader, so it can find the base
resident SDL exports instead of the SDL3 alias's scoped pointers. This explains
why the native filter facade was never entered and the global filter remained
active. OpenJDK NativeLibraries.c assigns `procHandle` to builtin JNI loads;
System.loadLibrary("SDL3") therefore uses the process registry handle here.
RawNativeLibraries path lookup uses the explicit resident alias handle instead.
Both retrieved runs log “Loaded SDL from system”, confirming the
default create/configure branch. A valid alias table alone was insufficient.

The same original backend supports system property `dev.isxander.sdl.library`.
When present, it calls configure(Path), which binds
`SymbolLookup.libraryLookup(path,Arena.global())`: one explicit library handle,
with no class-loader-wide fallback.165 sets that supported property to
`/app0/libSDL3.so` before Main. The resident loader resolves this basename to
the configured SDL3 alias; this is a resident handle, not a downloaded native
file. Raw native-library lookup takes the path directly and does not require a
placeholder file. The existing runtime loader remains restricted to known
resident groups. No alias/global ordering change, new loader or runtime patch
is added for165. The164 pinned runtime/facade remains unchanged.

The startup marker is `PS5_CONTROLIFY_LOOKUP handle_scoped=SDL3`; the native
scoped-filter marker should now follow Controlify initialization. Game/GLFW
base SDL lookup remains unchanged. Original Controlify, its FFM/API JARs, game
JARs, controller features, event data and frontend queue/filter behavior are
preserved. Only the consumer's launch configuration changes.

## Integration test

`test_controlify_ffm_lookup.py` extracts the original embedded SDL API and FFM
backend from the verified original Controlify JAR. It invokes that backend's
actual private configure() and public downcall binding under Java25/-Xverify:all,
using a real native callback/upcall and the exact native event facade.

Two separate processes prevent cached binding from concealing the result:

- Original default loaderLookup binds the real global SDL filter. The controller
  filter rejects a physical key event; the game receives none. This reproduces
  the missing164 integration through the actual backend configuration route.
- Supported explicit path binds the scoped native frontend. The physical event
  posts and the game receives it; a connection event is independently returned
  through the original backend's SDL_PollEvent downcall. The scoped-filter
  marker appears. Native code uses UBSan; original Java/API/backend classes
  remain unmodified. The host alias proxy uses normal host dynamic lookup;
  actual PS5 ELF alias tables and packaging are checked separately.

The actual launcher method is also called to verify the configured resident
path. Existing startup policy/observer/allocation/original Main checks pass.
Exact final ELF table pointer checks, package integrity/pins and normal and
replacement OpenAL relinks are recorded in the
[validation record](validation/client165-controlify-lookup.json).

## Console checks still needed

Use165/26.3 Fabric: use controller, release it, then move/click the physical
mouse and type. Confirm prompts/cursor and interactions switch naturally, then
use the controller again. Repeat26.2 Fabric and several transitions; check the
on-screen Del action, relative gameplay look and inventory clicks. Preserve
Vanilla typing and controller rumble/adaptive triggers/gyro/audio regressions.
Leave the app open at a failure so the launch/scoped-filter markers and input
trace can be correlated. Exact165 physical acceptance remains pending.

## Local artifact verification

Target build/sign, actual ELF alias-pointer tables, full package checks and both
normal/replacement OpenAL relinks pass. The relinks reproduce the exact ELF.
Matching local source/relink, symbols, package and checksums are preserved.

- Package SHA256: `23b73bbcfb3ed6b4bbe649f68aa24832e57b4b01f6f4dbdad603c01e332a40d7`
- Symbols SHA256: `0858da5123b4117f91e5071a954e90099f642a7347a9cbeea343313f69683d6b`
- Code FNV64: `7eabfcc1abc33826`

Console handoff acceptance remains pending.
