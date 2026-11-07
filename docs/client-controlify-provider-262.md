# Build 262 JNA allocation and Controlify discovery

Build 261's current-run report reaches Controlify initialization. Its original
SDL loader then fails inside JNA Native.open with OutOfMemoryError while allocating
the native library path string. Controlify reports no controllers after this
failure. The optional HID-library failure is caught earlier by the original mod.

Build 262 explicitly maps the runtime-built JNA object's malloc, calloc, strdup
and free imports to the existing consumer native provider as a pair. The builder
checks the exact original object, approved provider symbols and resulting object
hash. It also binds JNA closure allocation, preparation and free to the existing
333 W-to-X closure adapter with its existing 64-page pre-JVM reserve. JNA and 333
use byte-identical target ffi.h inputs. Default runtime JNA output and original
Java/mod/game downloads stay in place.

The package audit requires all seven provider imports and rejects the former raw
imports. It checks the exact resident-group hash and retains build261's scoped
JNI handle policy. Sharing the bounded closure reserve does not establish unlimited
callbacks or remove native allocation pressure.

The explicit host check requires the runtime's audited pinned JNA host source,
the original 1.21.11 JNA JAR, and actual SDL/libffi host libraries.

`tools/test_jna_provider_host.py` reproduces C-string refusal, then exercises
the provider boundary through original JNA Native.open and direct SDL registration,
1000 paired native memory/string buffers, and a real libffi callback with paired
release. A refused-provider control still reports OutOfMemoryError. Its controlled
host provider does not execute the PS5 allocator implementation. Xcheck:jni reports
the existing upstream JNI bootstrap unchecked-exception warning during JNA loading;
the subsequent assertions pass. The actual PS5 closure adapter is separately
checked with denied anonymous mmap and its bounded reserve.

Physical 262 SDL load, DualSense enumeration, Controlify handoff, gameplay,
rumble/triggers and save/quit remain pending.

See the [exact build validation](validation/client262-controlify-provider-2026-11-07.json).
