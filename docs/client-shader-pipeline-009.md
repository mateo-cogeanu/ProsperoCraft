# Client Shader Pipeline 01.000.009

Client009 adds a real compute-shader canary after the frozen008 Vulkan command
baseline. It uses the original LWJGL Vulkan3.4.3 JAR and actual RADV device:
validated SPIR-V module, storage-buffer descriptor, pipeline layout, push
constants, vkCreateComputePipelines, vkCmdBindPipeline/BindDescriptorSets,
vkCmdPushConstants and vkCmdDispatch. No native shortcut computes the result.

The consumer GLSL source is compiled offline with glslang for Vulkan1.1 and
validated using spirv-val. The build records compiler output/version and source/
SPIR-V SHA256 hashes. Generated Java fixture data and packaged SPIR-V derive
from the same bytes. On PS5, RADV compiles that SPIR-V into GPU machine code
when creating the compute pipeline. This does not exercise shaderc or compile
GLSL at runtime.

Each invocation transforms a distinct buffer word using uint32 arithmetic and
per-dispatch push constants. Java checks all output words and every remaining
word of the64KiB allocation against guard values. Counts1,63,64,65,1024,4096
exercise one invocation, partial and exact64-thread workgroups and larger
workloads. Three complete shader/device sessions produce18 submissions, each
with explicit host/compute barriers, flush/invalidate and a five-second fence
wait. Incomplete submissions retain their resources and require relaunch rather
than freeing memory the GPU could still use.

The pinned dependencies do not yet include a PS5 SDL window backend. This is an
offscreen shader check before window/display integration, not SDL integration,
a visible triangle, a graphics/fragment pipeline, Java presentation or Minecraft
startup. The screen stays on the CPU probe menu. Frozen000–004 and008 source/
packages remain unchanged; server two-hour endurance stays deferred.

## Run on PS5

Install **PPSA99874 01.000.009** from `dist/client-shader/PPSA99874.zip`, also
copied to the runtime workspace's current `dist/PPSA99874.zip`. Same shared app
identity: installation replaces the previous server/client app.

Run **all eleven rows in order**. Row9 repeats the passing standard Vulkan
transfer fixture, row10 is the new compute shader/readback test and row11 is
DestroyJavaVM. Report the failing row if any; keep the app open for logs. If a
row stalls for about a minute, record its stage and reopen without running rows
so saved reports can be retrieved. First pipeline compilation is new on PS5;
its completion time is not established.

## Reproduce/check

Use the same JDK/runtime arguments as008, adding `--shader`:

```sh
python3 tools/package_client_vulkan.py --shader --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25 --offline
python3 tools/test_client_vulkan_host.py --shader --runtime-workspace /path/to/PS5_Homebrew --java-home /path/to/jdk25
python3 tools/test_client_vulkan_package.py --shader --runtime-workspace /path/to/PS5_Homebrew
```

The real Mac MoltenVK GPU passes18 dispatches/all output+guard checks/three
pipeline lifecycles with Java25 Xint/XcheckJNI/verification and actual LWJGL
core UBSan. Host success does not establish PS5 shader execution. Target package
checks, exact package hash and pending console results are recorded in
`client/shader/status.json`. Official game/Vulkan JARs, the Java runtime
implementation and SDK are unchanged. No new milestone/release is created
until this exact build passes on PS5.

## Console acceptance

All eleven009 rows pass on2026-10-24, confirmed by the user and retrieved current-run reports. Logs verify18 shader dispatches, full output/guard checks,3 lifecycles and DestroyJavaVM. Exact tested bytes are frozen in [Client_Shader_Pipeline](https://github.com/mateo-cogeanu/ps5-homebrew-history/tree/aa7db35ee9aa5cc6515f49b23ebda6d1ecfcf91d/prosperocraft/Client_Shader_Pipeline/README.md).
