# Minecraft 1.20 native allocation test 015

Build 014 created the Java VM, completed the LWJGL native memory check,
and entered the original Minecraft 1.20 Main. The VM trace then recorded
a fatal HotSpot malloc failure for 9,232 bytes at the AllocateHeap
error path. The game log was empty. The underlying native allocator
refusal and the exact allocation caller remain unconfirmed.

Build 015 uses the Java 17 port's native heap fallback from runtime
source commit 4a9d80f. HotSpot can attempt an anonymous mapping after
malloc refusal, with paired allocation and cleanup. The Java heap
limit stays at 128 MiB and the original client and assets are preserved.
The runtime target build and a host forced-refusal check passed.

Install PPSA99878 version 01.000.015. For a complete 014 installation,
merge the local update ZIP into the existing title directory.
Run rows 1 through 3. If the app crashes, reopen the probe once to
expose the VM trace. The fallback and title screen need PS5 validation.

Signed full ZIP SHA-256 `02eec0fb5fae83b0b51d1cd39960552acf10336728f3cae7871e1f88039a0cf0`.
