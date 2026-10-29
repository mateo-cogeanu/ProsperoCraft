# VMA lock allocation repair, app 139

Safari retrieved build 138's preserved failed run
`client-01.000.138-1793291798-491183604`. The bounded recorder reports an
unreturned mutex entry from `std::__1::__shared_mutex_base::lock()`, followed by
native `pthread_mutex_lock` returning ENOMEM (12). The original exception says
`mutex lock failed: Cannot allocate memory`. The second failed lock is the
exception allocator's fallback heap mutex, obscuring the original failure.
Addresses were resolved against the exact preserved 138 symbols with the
recorded anchor establishing a 0x400000 load adjustment. Raw reports remain local.

The retained VM trace enters `Vma.nvmaCreateBuffer` immediately before native
termination. The pinned VMA implementation uses `std::shared_mutex` in its
allocation/block/dedicated-allocation paths. App 139 uses VMA's supported
`VMA_MUTEX` and `VMA_RW_MUTEX` customization hooks to remove that late SDK mutex
allocation dependency. The upstream VMA header and generated LWJGL JNI remain
byte-identical to their artifact pins; the consumer header is force-included
when compiling the PS5 native VMA objects. Original game/mod JARs remain intact.

Each lock owns its small atomic state inside the VMA object, with no heap
allocation, SDK lazy pthread initialization or global lease limit. Ordinary
mutexes retain exclusive access. Read/write locks permit parallel readers and
exclusive writers; waiting writers block newly admitted readers while existing
readers drain. Acquire/release operations protect the original critical sections.
Locks are nonrecursive and provide no FIFO guarantee. Contention spins for 64
iterations then uses a 50 microsecond native nanosleep backoff. There is no
unconditional sleep in an uncontended operation, and no synchronization bypass.

The header and its SHA-256 are packaged with the VMA audit. Target object audits
require absence of SDK mutex and pthread references in the actual VMA object.
This change belongs to the consumer's Vulkan dependency integration; Java runtime
source/pins, process-wide allocation, heap/GC and SDK locking remain unchanged.
Previous SDL/GLFW/shaderc/RADV fixes and bounded diagnostics are retained.

Host checks exercise the exact custom hooks with the pinned VMA RAII guards:
try paths, parallel readers, exclusive writers, waiting-writer admission,
80,000 contended operations, 10,000 simultaneously live locks and repeated
address reuse under ASan/UBSan. A host build of the original pinned VMA/LWJGL
implementation with these hooks also passes real MoltenVK GPU allocation,
map/flush/invalidate/transfer/free and allocator/device cleanup, including the
PS5 enum JNI dispatch fixture. These are host checks, not console acceptance.

PS5 Fabric 26.2 startup, menu, world creation, input/audio, save/reload and
endurance remain pending. Regression checks on accepted vanilla 26.2 and working
26.3/26.4 snapshots are required before public release. Preserve exact 138 and
prior canonical candidates, accepted 124 vanilla, frozen milestones and Store 121.
No Store release or passing milestone is created by this candidate.
