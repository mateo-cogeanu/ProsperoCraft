# Build269: compatible1.21.2 Fabric defaults

The user reports YACL requires Fabric API>=0.114.0+1.21.3 on Minecraft1.21.2.
Publisher metadata lists YACL3.7.0 through3.8.2 for1.21.2, but the unchanged
JAR manifests require the1.21.3 API. The only currently published1.21.2 API is
0.106.1+1.21.2. YACL3.6.6 requires>=0.106.0+1.21.2, so it fits.

Current Controlify3.0.1 LTS and published versions through2.4.2 require YACL>=3.8.0.
Controlify2.4.1 requires>=3.6.0 and its game range includes1.21.2.269 excludes
only the five confirmed incompatible YACL version IDs and eleven confirmed
incompatible Controlify IDs on1.21.2. Existing1.21.9 exclusions remain intact.
1.21.3 and other versions retain their selection. Future publisher IDs remain
eligible rather than permanently pinning an old version. Exact incompatible
required pins fail explicitly instead of bypassing publisher/Fabric predicates.

No official mod/game JARs or manifests are rewritten. The actual default installer
selects original Controlify qD2bMSgx(2.4.1), YACL mHeau9Ek(3.6.6) and Fabric API
UEjZZNue(0.106.1). All three publisher hashes and genuine Fabric dependency checks
pass, with an untouched world marker. This establishes dependency compatibility,
not PS5 native/controller/gameplay acceptance for the older Controlify generation.

Retry the failed fresh installation on269; verified game cache is retained.
If incompatible versions are already installed, use Installed to remove Controlify
and YACL, then add Controlify again through Mods. Keep other dependencies/worlds.
Automatic downgrade and modified-mod refusal remain unchanged. Do not delete an
instance or its cache to resolve a dependency conflict.

Deterministic selection tests cover each exact exclusion, unchanged1.21.3 pins,
compatible automatic selection, all-excluded refusal and future release eligibility.
The live check uses original publisher files and the actual installer/checker;
raw downloads and reports remain local. Existing cache-recovery and diagnostic
policies are retained. Exact269 download/controller/world/shader/quit and endurance
remain pending; no release or Store update authorized.

Publisher records: [YACL3.6.6](https://api.modrinth.com/v2/version/mHeau9Ek),
[Controlify2.4.1](https://api.modrinth.com/v2/version/qD2bMSgx),
[Fabric API](https://api.modrinth.com/v2/version/UEjZZNue).
