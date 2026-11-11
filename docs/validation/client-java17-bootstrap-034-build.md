# Minecraft 1.20 Java 17 test 034

PPSA99878/01.000.034 uses [runtime 48a3584](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/48a3584)
with patch 0017. Java's inflater now uses native scratch fallback on PS5
for its stream state and zlib allocations. This covers the native path
in build 033's JAR manifest failure. The PS5 target and host sanitizer
fixture with real zlib passed, including the lazy history window and
cleanup under forced allocation refusal.

The user reported a crash on PS5 row 3. The current crash report is
pending retrieval. The inflater failure and title-screen startup remain
unverified on build 034.

All 21 launcher host checks passed. The signed package passed integrity
verification and its eight changed entries match the update ZIP.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `04d6e15dd9fd458b9a24b8897cf03dc8877ec919868fca120281953888b55e70` |
| Update from 033 | `3f772008aa50073b711d2164c47e5965a122d5cd239d100b458212a4eda1de4f` |
