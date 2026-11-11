# Minecraft 1.20 Java 17 test 031

PPSA99878/01.000.031 integrates [runtime 107e363](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/107e363)
by explicitly enabling its compiler-TLS adapter. The scoped SDK object
uses the Java 17 mapped-slab fallback for compiler TLS allocations and
a bounded registry for refused native key updates. The 030 HotSpot
binary, image, heap and original Minecraft and graphics inputs carry forward.

The target link and host fixtures passed. Disassembly verifies the
SDK calls into the scoped backend. The host fixtures covered the 128-byte
allocation, refusal and growth ownership, and thread lifecycle. All 21
launcher host checks passed. The signed containers and full ZIP passed
integrity checks and the seven changed entries match the update byte
for byte.

| Local artifact | SHA-256 |
| --- | --- |
| Signed full ZIP | `1b332019ad9acb808fc8c7fa5b52aa1d4a810c44b32c7cc288f5bbe4a3f94dbb` |
| Update ZIP from 030 | `8221d3cc7178e39d2c3312da58f5b9913d742d30d1a6b425605679de3a1949f5` |

Exact PS5 row 3 and title-screen validation remain pending. The underlying
native allocation pressure and longer-running gameplay remain unverified.
