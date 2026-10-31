# Documentation

Start with the [project README](../README.md) for installation, current support,
controls and the release timeline. [CHANGELOG](../CHANGELOG.md) preserves build
history; a development entry does not imply a public release.

| Purpose | Guide |
| --- | --- |
| Contribute or report a reproducible bug | [CONTRIBUTING](../CONTRIBUTING.md) |
| Report a vulnerability privately | [SECURITY](../SECURITY.md) |
| Current maintainer policies | [AGENTS](../AGENTS.md) and [compatibility constraints/open work](maintainer-constraints.md) |
| Fast portable checks and optional lanes | [Host testing](host-testing.md), [inventory](host-test-inventory.md) |
| Full target preparation, ownership and archived source | [Source organization](source-organization.md) |
| Shared bootstrap, current identity and legacy package audits | [Tooling sharing](tooling-sharing.md) |
| Published 167 scope | [Release notes](releases/client-input-fabric-167.md), [console acceptance](validation/client167-console-acceptance-2026-10-30.json) |
| Local 168 candidate — console acceptance pending | [Test guide](client-shared-tooling-test-168.md) |
| Documentation migration and original maintainer narrative | [History index](documentation-history.md) |
| LAN diagnostic policy follow-up | [Open security follow-up](security-follow-ups.md) |

Detailed `client-*.md` guides retain the implementation decisions and exact-build
caveats needed for regression work. `validation/` contains preserved host, build,
publication and console records: read each record's scope. Current assets stay in
`assets/` and `docs/releases/`; obsolete launcher 075–092 previews and their original
guides are in the linked history archive. Generated previews stay under ignored
`build/`. Existing upstream toolkit documentation remains pinned with its original
source and licenses; its omitted-upstream-file links are recorded separately by
the documentation checker.
