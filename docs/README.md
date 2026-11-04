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
| NeoForge client research; implementation decisions pending | [Phase A plan](client-neoforge-plan.md), [inspection and validation](validation/client-neoforge-phase-a-2026-11-03.json) |
| Launcher212 — in-place selectors, live theme preview and full icon grid | [Guide](client-launcher-selectors-212.md), [validation](validation/client212-launcher-selectors-2026-11-04.json) |
| Launcher211 — whole-launcher120 target, moderate menus and symmetric cards | [Guide](client-launcher-120-211.md), [validation](validation/client211-launcher-120-2026-11-04.json) |
| Launcher210 — full controls, focused automatic login and expanding instance cards | [Guide](client-launcher-refinements-210.md), [validation](validation/client210-launcher-refinements-2026-11-04.json) |
| Launcher209 — horizontal page turns, L2/R2, theme arrows and continuous lists | [Guide](client-launcher-motion-209.md), [validation](validation/client209-launcher-motion-2026-11-04.json) |
| 1.21.x Vanilla first;207 user reports1.21.11 working;208 tests1.21.10, selected resolution and launcher keyboard | [Local208](client-1.21-208.md), [Local207](client-1.21-207.md), [Local206](client-1.21-206.md), [Local205](client-1.21-205.md), [Phase A draft](client-1.21-plan.md), [publisher lock](../client/1.21.lock.json), [inspection and validation](validation/client121-phase-a-2026-11-03.json) |
| Published 167 scope | [Release notes](releases/client-input-fabric-167.md), [console acceptance](validation/client167-console-acceptance-2026-10-30.json) |
| Microphone feature handoff for another model | [Start here](handoffs/microphone-174/00-START-HERE.md), [continuation prompt](handoffs/microphone-174/03-CONTINUATION-PROMPT.md) |
| Released179 — automatic microphone, no launcher mic menu | [Release notes](releases/client-microphone-default-179.md), [console acceptance](validation/client179-console-acceptance-2026-10-31.json), [publication/Store submission](validation/client179-store-publication-2026-10-31.json) |
| Local178 — opt-in input-port preparation/reuse | [Evidence/test guide](client-audioin-port-178.md) |
| Local192 — paired LWJGL JNI env/TLS allocator scoping; PS5 pending | [Evidence/test guide](client-zink-jni-env-192.md) |
| Local191 — upstream synchronous Zink flush/present workaround; PS5 pending | [Evidence/test guide](client-zink-flushsync-191.md) |
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

- [193 clean System.exit handoff and screen wait diagnostics](client-zink-lifecycle-193.md)

- [194 early genuine Zink screen/queue preparation](client-zink-prewarm-194.md)

- [195 early Zink screen and instance-refusal cleanup](client-zink-early-screen-195.md)

- [196 prepared ownership and upstream direct context](client-zink-direct-context-196.md)

- [197 Iris testing, queue shutdown and observation cost](client-zink-iris-197.md)
- [198 experimental Sodium LWJGL version-check configuration](client-zink-sodium-198.md)
- [199 default fullscreen hint and genuine no-error contexts](client-zink-hints-199.md)
- [200 genuine management API for Iris shadow initialization](client-zink-management-200.md)
- [201 packaged binding ownership and concurrent shutdown audit](client-zink-ownership-201.md)
- [202 native small flag queries and final SDL lifecycle](client-zink-final-202.md)
- [203 normal26.1.x launcher labels and202shader/quit results](client-zink-ready-203.md)
- [204 save descriptor headroom and extended handle diagnostics](client-save-headroom-204.md)

Release212: [notes](releases/client-launcher-vanilla-212.md) and [console acceptance](validation/client212-console-acceptance-2026-11-04.json).

[Release212 publication and Store submission](validation/client212-store-publication-2026-11-04.json).
