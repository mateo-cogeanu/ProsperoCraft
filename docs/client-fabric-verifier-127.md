# Fabric26.2 variable-sized verifier reserve, app127

Failed126run1793274682-683235147 still initializes original Matrix4f, but fails
at verifier3560 (CCinit) with errno12. Native reports show failed2048,1006and2016
byte buffers; a226byte request also exceeds128's256byte slot with its header.
The small-slot mitigation did not cover the full verifier workload. The underlying
libc refusal and PS5 anonymous mapping capacity remain unproven.

App127 retains126's explicit reserve enablement and runtime127 core-buffer policy,
but integrates runtime129 contiguous-unit allocation in the same4MiB verifier
arena. Requests can span multiple256byte units, and cleanup returns entire runs.
Bounds and native verification decisions stay intact. Normal malloc comes first;
reserve exhaustion or oversize requests retain anonymous fallback and OOM.
No new Java heap/GC settings or game/mod JAR transformations are introduced.

Reusable runtime source is published as fea0390a02e093317d2bbac457802ef0efbe7d29.
The actual legacy verifier verifies original publisher JOML1.10.8 Matrix4f,
Matrix4d, Matrix3f, Quaternionf andVector3f with both libc and anonymous mappings
denied and the reserve enabled. Existing disabled-mode success/OOM cases still
pass. ASan/UBSan covers full arena reuse, multi-unit allocations, zeroing,
overflow, bounded exhaustion and80000 concurrent cycles. Target native build
passed. Consumer package audits compare the rebuilt libverify and resident
object hashes to pinned runtime patches, including the128 prerequisite.

PS5 Fabric26.2 launch, world entry, save/reload, audio/input and sustained usage
remain pending. Prior126/125 and accepted124 vanilla are preserved. This is a
test candidate; no Store release or frozen milestone is created. Raw reports
and downloaded JARs stay local.
