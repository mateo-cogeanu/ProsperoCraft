#Fabric26.2native scratch pressure — candidate125

User confirms Vanilla26.2working on124; Fabric26.2fails. Current124run
1793272719-47498832loads Fabric0.20.1,Controlify3.5.3andFabricAPI0.161.0, then
fails with native platform-string allocation OOM during RandomAccessFile.open0
while bounded ZipFile handles reopen an archive. Native log shows157byte filename
malloc failure and16KiBanonymous mapping ENOMEM. Nearby large ClassLoader buffers
also fall back to anonymous pages. LastG1sample has~210MiBused/~1176MiBcommitted;
this is not a Javaheap-exhaustion diagnosis.132open descriptors,without EMFILE.
Existing native direct-budget reports show no syscall failure/policy rejection.
Exact anonymous quota and allocation-owner/peak/leak behavior remain unproven.
Raw reports remain local.

Runtime127provides a default-off final fallback for the existing platform-string
and class-loading native temporary buffers. Consumer125explicitly enables it
beforeJVMstartup. Normal malloc, existing reusable classloader leases and
anonymous pages retain precedence. EachCunit has64slots/8MiB(16MiBaggregate).
Direct mappings and physical backing have tracked matching ownership; failed
cleanup retains budget/backing rather than freeing uncertain live memory.
No orphan recovery is claimed. Heap size, G1 and graphics-memory policy stay
unchanged. Reusable source lives only in the Java repository; this consumer
pins the runtime commit/patch and packages its rebuilt libjava with an audit.

Host checks exercise default-off/anonymous-first/direct paths,filled buffers,
size/slot/budget limits,800concurrent allocations/releases,map rollback and
retained ownership on unmap/release failure underASan/UBSan. Actual JNI string
encodings/ClassLoader definitions and scratch lease concurrency remain passing
with the opt-in disabled. Target java.base-libs rebuild and consumer native
symbol/package/source audits pass. Syscalls onhost are fixtures;physicalPS5
mapping/release and Fabricstartup/render/world/audio/save/cleanup/endurance
remain pending. This addresses the observed buffer allocation failure and does
not prove every later Fabric/mod allocation will fit.

Vanilla124feedback is recorded; no formal ALL PASS or new frozen milestone is
inferred.125retains the26.2GLFWcallback/Vulkanownership fixes,accepted snapshot
labels and defaults,themes/cursor/auth and existing world/data behavior.
Public121/older candidates preserved. No Store release is requested.
