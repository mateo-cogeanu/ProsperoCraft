# Minecraft 1.20 Java 17 test 030

PPSA99878/01.000.030 integrates [runtime 80c9c44](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/80c9c44),
including patch 0014 on OpenJDK 17 source 7d679b0486460f9f534e5e955dd192993d1ff5ef.
HotSpot now uses its existing native pthread key for the current-thread
pointer on PS5. The target VM no longer contains the emulated TLS descriptor
for that pointer. The 029 class image, heap, graphics and original game assets
carry forward.

The Java 17 target, exact HotSpot/POSIX thread storage fixtures, Java 25
fixture regression and all 21 launcher host checks passed. Exact PS5 row 3
and title-screen validation are pending.

The signed full ZIP passed integrity checks. Its eight changed entries
match the update ZIP byte for byte, and the original game asset entries
are unchanged from 029.

| Local artifact | SHA-256 |
| --- | --- |
| Signed full ZIP | `d49f1f41167058fee1e2ee919785f747c0e0c0590a8d85c8fefcb31400eaea2f` |
| Update ZIP from 029 | `fbd024ee4c07e60297481865924842e1e1d5de9b47cbf3ea80fc44070c75ebd9` |
