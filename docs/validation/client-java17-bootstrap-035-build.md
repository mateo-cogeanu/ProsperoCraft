# Minecraft 1.20 Java 17 worker fault capture test 035

PPSA99878/01.000.035 uses [runtime ac3b595](https://github.com/mateo-cogeanu/ps5-java25-homebrew/commit/ac3b595)
with patch 0018. The probe tracks the upper 128 KiB of each registered
HotSpot worker stack using 128 atomic slots. On a fault it can sample up
to 64 aligned words from the saved stack pointer when that pointer is
inside a registered window. Only executable image offsets are emitted
from this scan. The existing main-stack scan and signal forwarding stay
in place. A stack candidate is evidence for symbol lookup and may be a
stale value rather than a return address. Unregistered threads and stack
pointers outside the windows produce no worker scan.

[Build 034](client-java17-bootstrap-034-build.md) entered original
Minecraft Main and faulted before any check result. A saved register
points to a HotSpot monitor wait routine, but the faulting instruction
is outside the probe ELF and the caller and cause are unresolved. Build
035 adds diagnostics for the next test and retains the same JVM options,
class image and verified original game inputs.

The Java 17 target build and ordered LTS patch checks passed. The
resident VM object has a weak reference to the observer and the final
ELF resolves it to the probe recorder. A host pthread fixture verified
actual stack registration, retirement, alignment and bounds, filtering
to executable offsets, and the 64-word cap under ASan/UBSan at O0 and
O2. All 21 fast and 14 native host checks passed, including signal
forwarding and restoration. Both signed binaries passed integrity
verification, and all eight update ZIP entries match the full archive.

| Local artifact | SHA-256 |
| --- | --- |
| Full signed package | `30e25ca83d308aeaa4dc5011a507c1b3b2c41ad2f81f89c450dbd29715c06eaf` |
| Update from 034 | `032d66eb18695fd56e525e2c569b3f8a3c722177101540b030488a8e0cd4ea05` |
| Matching symbol ELF | `cd028691e97312284680156e623d5cb5fbca4b6efc8397aa74288ef777dcb251` |

The maintainer reported a row 3 crash. The five retrieved reports
identify 035 and show that constructors and VM creation passed.
Original Minecraft Main initialized. Row 3 and VM destruction
produced no results, and the game log was empty.

The registered worker stack scan captured the same external SIGBUS
PC as 034. With the exact 035 symbol ELF, the closest application
return address is immediately after the call to the PlatformParker
destructor in the JavaThread destructor. The subsequent candidates
include the deleting destructor, SMR deletion and native thread entry.
Disassembly shows two native condition destroy calls and a tail jump
to the imported mutex destroy routine. This narrows the crash to the
Parker teardown path. The faulting native routine and its input state
remain unconfirmed.
