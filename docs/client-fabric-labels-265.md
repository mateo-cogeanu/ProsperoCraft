# Build 265 Fabric release labels

The user requests publication with normal Fabric status for 1.21.7, 1.21.8,
1.21.9, 1.21.10 and 1.21.11. Fabric 1.21 through 1.21.6 is Experimental.
Cards have no normal READY badge. The detail Play action uses Experimental
instead of DEV TEST for the remaining implemented Fabric versions.

The new v6 resource policy carries these labels. Historical resource policies
retain their earlier decisions. Existing Vanilla support and the separate
26.1 Fabric Experimental flag remain. Future unsupported releases stay blocked.
The YACL correction and 512-page callback reserve are included.

Host assertions check all twelve versions, actual card fields and detail Play
labels with a synthetic session. This establishes the requested UI policy.
The user's earlier positive reports cover build263 1.21.11 and 1.21.10 Fabric;
they do not validate the exact new 265 package.

The release notes are prepared locally. AGENTS.md requires physical-console
confirmation for the exact build before creating a GitHub release or prerelease.
The user confirmed build 265 passes both the label and shader-world checks on
2026-11-07 and authorized publication. Exact package bytes are retained.

See the [exact build validation](validation/client265-fabric-labels-2026-11-07.json).
