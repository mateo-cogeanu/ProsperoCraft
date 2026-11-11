# Minecraft 1.20 Java 17 reservation size test 038

PPSA99878/01.000.038 uses the same
[Java 17 runtime cd756dd](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/cd756dd)
as [build 037](client-java17-bootstrap-037-build.md). It sets the
interpreter code cache reservation to 8 MiB and compressed class space
to 16 MiB. That lowers the combined requested reservations by 56 MiB.
The probe still runs with `-Xint` and a 192 MiB maximum Java heap.

Build 037's fatal report showed about 717 KiB of code cache in use and
5.13 MiB of class space committed before its third aligned 16 MiB
non-class metaspace reservation returned `ENOMEM`. The new settings test
whether reducing unused reservations helps this workload. The kernel
resource that returned `ENOMEM` remains unknown.

The Java 17 host VM accepted the options and loaded 8,000 generated
classes, with an 8 MiB code cache and a 16 MiB compressed class space.
The PS5 target audit and both signed binary integrity checks passed.
The four entries in the update ZIP match the full archive.

The full launcher host lane stopped twice at the instance worker's
five-second timeout. That check passed in isolation on both the 037
source snapshot and the 038 working tree. The remaining checks passed
when run separately, so all 21 checks passed across the split runs.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `38c7340e410142c03c6b948bbf685c3cf71807d0e80ec8e7748e922d79fd87c7` |
| Update from 037 | `1a63961777f822391973101cffd8b453d70cac31540651fd633cfc7a9fc071f8` |
| Matching symbol ELF | `38a6ba70567da231864be46f7261f8958712fd48eff931d368976c0f105d15f1` |

Physical console validation is pending. Run rows 1–3. If the title screen
opens, quit normally and check row 4. If it crashes, reopen the same
build and leave it at the menu to preserve the reports.
