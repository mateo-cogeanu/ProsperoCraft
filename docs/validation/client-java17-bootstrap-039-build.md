# Minecraft 1.20 Java 17 renderer allocation test 039

PPSA99878/01.000.039 uses
[Java 17 runtime cd756dd](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/cd756dd).
[Build 038](client-java17-bootstrap-038-build.md) got past the third
metaspace reservation, then reported a failure during renderer
initialization. The original 1.20 bytecode puts the retained frame
in the branch that throws when LWJGL returns null for the 12 MiB
renderer buffer. The PS5 allocator's reason for refusing it is unknown.

The probe package reconstructs the pinned LWJGL 3.3.1 native group from
the original audited objects, redirecting only the allocator imports in
the generated MemoryAccessJNI and LibCStdlib units. Both JNI calls and
the function pointers LWJGL passes to native code now use the resident
graphics allocator's matched malloc, calloc, realloc, free and
posix_memalign functions. The graphics wrappers can fall back to libc.
The original game and LWJGL Java JARs remain intact. The 038 VM settings
and runtime are retained.

The final target ELF confirms the JNI calls and function pointers bind
to the graphics allocator. A sanitizer fixture used the two genuine
generated JNI units and host allocator stand-ins to verify a 12 MiB
allocation, realloc byte preservation, failure ownership, zeroed
allocation, and paired aligned free. Both signed binaries passed
integrity verification. All four update entries match the full archive.
All 21 fast and 14 native host checks passed.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `3b8497cd5d031d2fb9eaea0b62c7d08c0794ff81e3a9c83cb6571e8092f85aff` |
| Update from 038 | `08b4b8e204060deb5d4e17df66e42a3111fdfdb5a616b020e0060bdf0e5582c2` |
| Matching symbol ELF | `fe6db59d5660fb05a37e4be28369da63b65197679098b3d0f7241be145445bce` |

PS5 testing is pending. Run rows 1–3, check whether the title screen
appears, and confirm row 4 after quitting. If row 3 fails, reopen the
same build and leave it at the menu to preserve the reports.
