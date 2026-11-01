# Early screen preparation and instance-refusal cleanup —195

[193 current-run evidence](validation/client193-console-shader-queue-2026-11-01.json)
identifies failed initialization of the required initial Zink shader queue, after
real Vulkan instance/device creation succeeds.195 retains [194 early preparation](client-zink-prewarm-194.md):
create the same genuine screen/cache/initial worker before JVM pressure, then reuse
it for the first original GL context. Native budgets, queue/fence/compiler behavior,
last-context cleanup, full launcher, original JARs and193 quit candidate fix remain.
Exact cause of the native refusal and PS5 mitigation success remain unproven.

194 passes actual host preparation/rendering and exact target/package checks.
An extra negative probe enables validation on a host without a validation layer:
Zink refuses, but partial-screen teardown calls an unloaded instance dispatch
function. ASan records a null PC in original zink_internal_create_screen; a native-
only run also reproduces it, so this is not a JVM-constructor injection artifact.
The [194 local record](validation/client194-local-preparation-2026-11-01.json)
preserves its unvalidated package and the failure;194 was not sent for console
acceptance and is not a passing milestone.

`0005-instance-dispatch-before-refusal.patch` loads the genuine instance and
physical-device dispatch tables immediately after the real instance is retained,
before validation-layer refusal can enter teardown. Existing Vulkan instance,
reference counts, destructor and all success/error decisions remain. No fake
function, skipped destruction, extra object, loader or broad recovery policy.
This is a concrete error-path ordering fix in the optional consumer Zink component;
the Java runtime/default graphics builder and archived artifacts remain unchanged.
Other partial initialization or allocation failures are not universally validated.

The host missing-provider control runs before inserting the genuine preparation
provider. Positive tests then inject the explicit native constructor before real
Java launcher/JVM startup. Loading that provider for a missing-provider test had
invalidated its premise; the corrected separate-child control is preserved. No
PS5 compatibility behavior was changed to satisfy that test.

## Checks and console work

`package_zink_early_screen.py` / `test_client195_package.py` produce isolated195,
with verified179 package/relink inputs, new exact combined component, required
scoped prepare export, original Main/26.1.x Vanilla/Fabric gates, retained canonical
classpath/JAR hashes and staged constructors. No prior ZIP overwrite or current179
identity change. Normal native launcher Vulkan coexistence/resource cost remains
an explicit physical check; early preparation retains an extra real Zink device
and initial workers while account/download work runs, even for another renderer.

Host checks cover real concurrent/idempotent preparation, GL clear/draw/readback,
refused surface, context ownership/transfer/resize/destruction, original26.1/
26.1.1/26.1.2 capabilities and real pre-JVM preparation. The missing-validation-
layer negative test (`--prepare-screen --check-preparation-refusal`, requiring
a layerless host provider) must return an honest preparation failure before host JVM
entry; it is separate from successful GL and PS5 startup checks. No full-game,
save, native quota/resource recovery or console success is inferred.

Install complete PPSA99874 / **01.000.195**, and retry the same Fabric26.1
instance. Leave a failure/black screen open for current logs. Report title/world/
mods separately. Then test Vanilla26.1 title/world/save, Quit Game, normal launcher
library and launch again.193's quit handoff remains a candidate until physically
confirmed.26.1 patch releases, Fabric shutdown,26.2+ Vulkan/input/audio, resource
reclamation and endurance remain pending. No release/prerelease/Store/archive action.

[Exact195 build/validation](validation/client195-zink-early-screen-2026-11-01.json)
pins clean source `5b75968` and all package/runtime/native hashes.
ZIP SHA-256: `d863ac675d645a159e42ac3507326c1c5ec2a511d40d2dcbbe492f0936e60be0`.
Source-only outside-root17fast/11native, real host pre-JVM preparation/reuse,
concurrent/native rendering and26.1/26.1.1/26.1.2 GL capability checks,
missing-provider control, early validation-refusal/instance cleanup and exact
target/package audits pass. [Policy CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41328466574)
passes17checks and [native CI](https://github.com/mateo-cogeanu/ProsperoCraft/actions/runs/41328477750)
passes11checks on each Ubuntu/macOS host; actual completed jobs/logs inspected.
These are host/build results; physical195 startup and quit/relaunch remain pending.
