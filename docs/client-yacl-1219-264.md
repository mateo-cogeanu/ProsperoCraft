# Build 264 YACL selection for Minecraft 1.21.9

The user reports that 1.21.11 Fabric and 1.21.10 Fabric are okay on build 263.
The 1.21.9 setup fails because YACL asks for a Fabric API version for 1.21.10.
The normal host installer reproduces the exact failure before this change.

Publisher metadata lists YACL 3.8.2 and 3.8.1 for both 1.21.9 and 1.21.10. Their
unchanged JAR manifests require Fabric API >=0.138.3+1.21.10. The newest Fabric API
published for 1.21.9 is 0.134.1+1.21.9, which does not satisfy that requirement.
YACL 3.8.0 requires >=0.133.7+1.21.9 and satisfies current Controlify's >=3.8.0 rule.

Build 264 excludes only publisher version IDs skcT0J9K and ORi1nScg for automatic
YACL selection on 1.21.9. The existing ordered version list selects UZmV6xf4
(3.8.0+1.21.9-fabric). Later publisher releases remain eligible. An exact required
pin to either incompatible release reports the conflict explicitly. This does
not alter an installed mod or bypass Fabric's own version predicates.

The full live default installer succeeds after this change, using original
Controlify 3.0.1 LTS, YACL 3.8.0 and Fabric API 0.134.1. Publisher checksums and normal
dependency validation run before publication. Deterministic content tests cover
both exclusions, compatible exact pins, explicit incompatible-pin rejection,
future-release eligibility and unchanged 1.21.10 selection.

The existing callback capacity and runtime providers are retained. Exact build 264
console download, title screen, DualSense and gameplay remain pending.

Publisher version records are available for
[3.8.2](https://api.modrinth.com/v2/version/skcT0J9K),
[3.8.1](https://api.modrinth.com/v2/version/ORi1nScg) and
[3.8.0](https://api.modrinth.com/v2/version/UZmV6xf4).

See the [exact build validation](validation/client264-yacl-1219-2026-11-07.json).
