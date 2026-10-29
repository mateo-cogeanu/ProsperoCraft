# Fabric26.2 verifier allocation repair, app126

Build125 failed during Fabric original Main initialization with an
OutOfMemoryError for org.joml.Matrix4f, verifier site4221/errno12. Previous-run
reports1793273838-5548144 show failed24byte and26byte verifier allocations;
prior successes mapped16KiB per small allocation. No VM abort was captured.
This is a separate native allocation failure after125's temporary-buffer repair;
the root libc refusal/title memory quota remains unproven.

App126 retains125's runtime127 core temporary-buffer policy and explicitly enables
runtime128's independent verifier small reserve before JVM startup. Normal libc
allocation still comes first. Tiny verifier allocations can use16384 aligned
256byte slots (4MiB fixed BSS), returned through the existing cleanup paths.
Larger or exhausted requests retain existing anonymous-map behavior. No official
Minecraft/mod JARs, heap/GC settings, loader selection, authentication or instance
data are changed. libverify.so and its resident object are rebuilt together and
checked against the runtime pin in core-scratch-runtime-audit.json.

Reusable implementation and tests live in ps5-java25-homebrew, commit
 eb8b8ccc4e6a32a3a39a146e063a3d371c8501b1, patch0128. Host ASan/UBSan checks
reserve bounds/exhaustion/zeroing/overflow/reuse and80000 concurrent cycles;
actual legacy Matrix4f and verifier pool tests retain default-off behavior.
Target java.base native build passed. Package and launcher host checks are
recorded in the matching validation JSON. PS5 Fabric26.2 launch, world entry,
save/reload, audio/input and sustained operation remain pending. This candidate
is not a Store release or an accepted milestone. Prior125 and accepted vanilla124
are preserved; raw diagnostic reports remain local.
