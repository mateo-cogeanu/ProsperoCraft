# Minecraft 1.20 Java 17 test 029

PPSA99878/01.000.029 integrates [runtime 98953f6](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/98953f6),
including patch 0013 on OpenJDK 17 source 7d679b0486460f9f534e5e955dd192993d1ff5ef.
Non-strong hidden-class loaders now share 32 metaspace locks. The 028
interpreter, heap, synchronization pool sizes, class image, original
Minecraft inputs and graphics configuration carry forward.

The PS5 Java 17 target built successfully. The local signed containers and
full ZIP passed integrity checks. All eight entries in the update ZIP were
compared with the full package, and the 028 and 029 game asset entries match.

| Local artifact | SHA-256 |
| --- | --- |
| Signed full ZIP | `863531dcb47d8f92113e9b5270f62df6f3c00f9938319378259b35ec6820eca2` |
| Update ZIP from 028 | `77abe02bd68597fb512c8aa3e0f18c8f10364883f642cd009bb16428410833e0` |

Build 028's retained reports show a native abort after entering the original
Minecraft Main. The abort caller is unresolved. Exact 029 hardware validation
is pending, starting with probe row 3 and the title screen. Play, shader
rendering, stability and performance have not been validated.
