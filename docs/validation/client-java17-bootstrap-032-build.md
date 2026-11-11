# Minecraft 1.20 Java 17 test 032

PPSA99878/01.000.032 integrates [runtime 4ce4789](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/4ce4789).
Java 17 now routes its native network interface allocations through the
paired scratch allocator on PS5. Build 031 reported an out-of-memory
exception in that code during Minecraft startup. The target build and
host sanitizer fixture passed, including IPv4, IPv6 and partial allocation
cleanup under forced native memory refusal.

Exact PS5 row 3 and title-screen validation remain pending.

All 21 launcher host checks passed. The signed full package passed
integrity verification. Its nine changed entries match the update ZIP.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `f8c4a8ce81d8fb066377090d82d746b53d3f4422e4417fda9cab1097a2eb6aba` |
| Update from 031 | `d1796544ba492ac2646be0387dc461bb70d19cc778305f8997c5bc9981d6772a` |
