# Minecraft 1.20 Java 17 Parker teardown test 036

PPSA99878/01.000.036 uses [runtime ddf7997](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/ddf7997)
with patch 0019. On PS5, the Java 17 Parker borrows native mutex and
relative condition objects from the existing reserves and default-clock
conditions from a separate 256-object reserve. Native initialization
remains available when a reserve is exhausted. Product builds now check
initialization and destruction, with fixed trace markers on refusal.
The JVM options, class image, original publisher inputs and worker
fault recorder are unchanged from 035.

[The 035 console evidence](client-java17-bootstrap-035-build.md) points
to teardown after a Java worker exits. It does not resolve the external
faulting instruction or prove an initialization refusal. The new
package tests whether the ownership change clears this crash.

The Java 17 target build, LTS patch replay and all 21 launcher host
checks passed. ASan/UBSan checks covered real wait/wake operations,
reserve exhaustion, native initialization refusal and concurrent reuse.
The extracted Parker constructor stopped before destruction after a
forced refusal, and 512 pooled lifecycles completed with native
initialization forced to fail.

Both signed binaries passed integrity verification. The update ZIP's
eight entries match the full archive.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `cd9894016580823c20c9bf5ee36a4d7213ee96ccf62039947a7b8b2264bfa211` |
| Update from 035 | `2451ada37b7fe2f71423bcb7f2a622633061014aa08e0246da27235392d0cdc0` |
| Matching symbol ELF | `e26172bb75bed81ee5bf3cab75456aafbae377d3ba683ad3c868ae7e70054b19` |

The maintainer reported that row 3 ran longer before crashing. All five
reports were recovered and the append-only records identify 036.
Rows 1 and 2 passed, the 256 absolute condition slots initialized,
and original Minecraft Main initialized. The earlier Parker SIGBUS
did not recur in this run. Row 3 and VM destruction recorded no
results and the game log remained empty.

The VM trace reports `OOM_MMAP_ERROR` for 16 MiB at source line 249,
which matches the failed reservation of a metaspace node in the
matching runtime. The subsequent SIGSEGV stack has candidates in
`os::get_core_path` and `os::check_core_dump_prerequisites`.
The exact native reservation refusal and the title screen remain
unverified. No Parker failure marker appeared in this run.
