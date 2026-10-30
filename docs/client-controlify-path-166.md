# Controlify existing library path, local166

The user reports165 no longer detects the controller. Safari retrieves the
exact165 native/game reports; the game log records
`PS5_CONTROLIFY_LOOKUP handle_scoped=SDL3`, followed by Controlify's
`Failed to initialize controller manager` with
`IllegalArgumentException: Cannot open library: /app0/libSDL3.so`. The failure
occurs in the original FFM backend configure(Path) before native manager/filter
creation. Raw reports stay local.165 is failed, not accepted.

## Missed canonicalization prerequisite

The original OpenJDK RawNativeLibraries.load(Path) first calls
`path.toRealPath().toString()`. On IOException it returns null.165 configured
a non-existent path, so the resident loader never received the request. Its
host positive test used an existing native file and did not cover that target
package prerequisite. The supported handle-specific route itself remains
appropriate for isolating the shared SDL alias from process lookup.

166 configures `/app0/assets/java25/lib/libSDL3.so`. Packaging now generates
that genuine ET_DYN SDL ELF from the exact scoped resident-sdl.o with libSDL3.so
SONAME and records both hashes in the SDL audit. The file supplies a real path
for canonicalization. Raw native loading then resolves its basename through
the existing known-resident registry to the SDL3 alias. No sidecar machine code
is dynamically loaded or executed, and no arbitrary native loader is enabled.
The sidecar retains real SDL symbols/code; it is not an empty placeholder or a
new standalone SDL support claim. Existing source, licenses and resident object
materials remain available. Original game/mod/backend JARs are unchanged.

Before Main, a target-side preflight performs the actual path-based lookup and
checks that all three SDL event addresses equal their scoped facade exports.
Success logs `verified_events=3`; missing or unscoped lookups fail explicitly
before game startup instead of reaching a broken controller manager. The check
closes its temporary arena; the real native groups remain resident.

No runtime code, alias tables, event facade, controller/audio state, heap/GC,
public support gate or game policy changes in166. The original FFM backend's
property remains the integration point; the path and matching package contents
are corrected. Prior candidates and accepted161/163Vanilla results are retained.
GitHub/Store releases remain on hold.

## Checks

The actual original FFM backend test now runs three fresh-process cases:
loaderLookup reproduces dropped physical input, a nonexistent explicit path
reproduces Cannot open library before binding, and the existing scoped-library
path preserves game keyboard delivery and mod connection events through real
FFM downcalls/upcall and the unchanged native facade. It calls the actual
launcher setup method to verify the configured target path, rejects an unscoped
base SDL lookup, and passes the actual preflight against exact host symbol aliases
matching the resident table mapping. Java25/-Xverify:all
and native UBSan remain enabled.

Target package gates require the sidecar to exist at that exact asset path,
verify its ET_DYN ELF format/real SDL and facade exports, and match its recorded
SHA256 and resident object hash. The existing actual ELF alias-pointer checks,
startup host policy/native allocation/observer/original Main checks, package
integrity/pins and exact OpenAL relinks are recorded in the
[validation record](validation/client166-controlify-path.json).

## Console validation pending

Use166 with26.3 Fabric first: confirm Controlify detects the controller and
controller input works. Then test controller to keyboard/mouse and back,
including typing/clicks. Repeat26.2 Fabric, several transitions, on-screen Del,
relative gameplay mouse look and inventory clicks. Check rumble/adaptive
triggers/gyro/audio and preserved Vanilla typing. Leave the app open if detection
or handoff fails. No physical acceptance follows from the host/path/package checks.

## Local artifact verification

Target build/sign, exact ELF alias tables, complete package checks (including
the configured file and sidecar audit) and both OpenAL relinks pass. Matching
local package, symbols and corresponding source/relink/checksums are retained.
An initial local disk-full interruption was resolved by removing duplicate
temporary relink outputs and verified compressed kits' expanded copies only;
canonical artifacts remain preserved. Interrupted checks were retried and pass.

- Package SHA256: `695f534ad545799acb3236cc30cd6a470d8a9669b591fac559c9b02f27fbef3e`
- Symbols SHA256: `5fa0e00ac8d4680117dfc6a6322241788a508236e71b9e5a5d82dd2a256b50ae`
- Code FNV64: `430d63147b87210f`

Exact166 controller detection and handoff remain console-pending.
