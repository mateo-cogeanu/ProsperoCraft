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
| Microphone feature handoff for another model | [Start here](handoffs/microphone-174/00-START-HERE.md), [continuation prompt](handoffs/microphone-174/03-CONTINUATION-PROMPT.md) |
| Released179 — automatic microphone, no launcher mic menu | [Release notes](releases/client-microphone-default-179.md), [console acceptance](validation/client179-console-acceptance-2026-10-31.json), [publication/Store submission](validation/client179-store-publication-2026-10-31.json) |
| Local178 — opt-in input-port preparation/reuse | [Evidence/test guide](client-audioin-port-178.md) |
| Local190 — bounded native create-window checkpoints; Fabric black-screen cause pending | [Test guide](client-zink-fabric-trace-190.md) |
| Local189 — early Zink frontend mutex lease; Fabric PS5 retest pending | [Evidence/test guide](client-zink-fabric-guard-189.md) |
| Local188 — Vanilla/Fabric26.1.x development tests; quit crash retained | [Test guide](client-zink-fabric-188.md) |
| Local187 — normal launcher; Vanilla26.1 Zink development title test pending | [Test guide](client-zink-launcher-187.md) |
| Local186 — user-reported JVM/launcher Stage2b PASS | [Evidence/test guide](client-zink-resident-186.md) |
| Local185 — GLFW reachable; check4 resident-name failure | [Evidence/test guide](client-zink-classpath-185.md) |
| Local184 — check4 failed after native UI closed; GLFW classpath omission | [Test guide](client-zink-jvm-handoff-184.md) |
| Local183 — user-reported native Stage2a PASS | [Evidence/test guide](client-zink-present-flush-183.md) |
| Local182 — captured null semaphore fault during queued presentation | [Evidence/test guide](client-zink-first-frame-182.md) |
| Local181 — crashed before first-frame completion | [Test guide](client-26.1-zink-present-181.md) |
| Local180 — user-reported native context Stage1 PASS | [Implementation and test guide](client-26.1-zink-native-180.md), [Phase A plan](client-26.1-zink-plan.md) |
| Local177 — prepare AudioIn service before JVM/game | [Evidence/test guide](client-audioin-service-177.md) |
| Local176 — primary review of microphone specialist work | [Review/test guide](client-microphone-review-176.md) |
| Local174 — microphone diagnostics and SVC disconnect repair; console pending | [Evidence/test guide](client-mic-disconnect-174.md) |
| Local173 — voice speaker/context repair; console pending | [Evidence/test guide](client-voice-speaker-173.md) |
| Local172 — terrain stack budget; console pending | [Evidence/test plan](client-terrain-thread-budget-172.md) |
| Local171 — pairing/layout/voice-thread repair; console pending | [Test guide](client-local-management-171.md) |
| Local 170 — input/web/microphone console checks pending | [Test guide](client-local-management-170.md), [capture investigation](controller-microphone-investigation.md) |
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

[Local build storage cleanup](local-build-storage.md)
