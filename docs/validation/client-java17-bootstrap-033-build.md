# Minecraft 1.20 Java 17 test 033

PPSA99878/01.000.033 uses [runtime eb2ce5a](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/eb2ce5a)
with patch 0016. A live route query can recover eligible resident network
interface query failures. The native error formatter can report short
errors using stack storage. This addresses two paths relevant to build
032's `NetworkInterface.getAll` failure.

The Java 17 target build, sanitizer route parser fixture and host JNI
formatter checks passed. Exact PS5 row 3 and title-screen validation
remain pending.

All 21 launcher host checks passed. The signed package passed integrity
verification and its 12 changed entries match the update ZIP.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `ac02e25a26fb224048e3c37e2f93f78e568ebe414cc6f33f6ce168fcd02d5142` |
| Update from 032 | `11c9791c8f92751d542ead518011aa8ddfa5298475d358251325e0ce80426578` |
