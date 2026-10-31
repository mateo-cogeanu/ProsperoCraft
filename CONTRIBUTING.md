# Contributing

ProsperoCraft integrates Minecraft with the native PS5 Java25 runtime. Start with
[README](README.md), [documentation index](docs/README.md) and the current
[maintainer instructions](AGENTS.md).

## Layout and ownership

`client/` contains the launcher, bootstrap and consumer native ports; `server/`
contains server harness/configuration; `tools/` contains consumer build/audit/test
entry points. Pins and source patches stay with their owning implementation;
`tests/` and `docs/validation/` preserve fixtures and scoped results. Reusable JVM,
core-library and runtime packaging fixes belong in
[ps5-java25-homebrew](https://github.com/mateo-cogeanu/ps5-java25-homebrew), with
matching runtime integration/pins here. Frozen source belongs in the existing
[history archive](https://github.com/mateo-cogeanu/ps5-homebrew-history).

## Setup and checks

Fast host checks support macOS/Linux ARM64 or x86_64, Python 3.10+ without `-O`,
and a complete JDK 25. They need no PS5 SDK, Microsoft account or game download.
Follow [host testing](docs/host-testing.md) for portable tool discovery, explicit
options and the small hash-pinned host dependencies:

```sh
python3 tools/run_host_tests.py --fetch-deps
# After provisioning, routine assertions work offline.
python3 tools/run_host_tests.py
# For affected scoped native code, with compatible Clang/Clang++ and sanitizers:
python3 tools/run_host_tests.py --lane native --fetch-deps
# Documentation changes:
python3 tools/check_documentation.py
git diff --check
```

Use the [test inventory](docs/host-test-inventory.md) for optional SDL/OpenAL/GPU,
SDK/package and publisher-input prerequisites, and [source organization](docs/source-organization.md)
for full preparation/build entry points. Full target packaging has separate SDK,
runtime and native inputs; these are not private prerequisites for the fast lane.
Do not substitute a personal game cache for missing pinned test dependencies.
Host compilation, a package audit and a different host GPU backend cannot validate
PS5 startup, GPU, controllers, audio, world saves, lifecycle or endurance. Report
those separately; exact-build physical-console confirmation gates every new
release/prerelease, with explicit maintainer release/Store authorization.

## Reporting a reproducible problem

Use the existing [bug/mod/shader issue forms](https://github.com/mateo-cogeanu/ProsperoCraft/issues/new/choose).
Give the launcher build and install source, console firmware, game version,
Vanilla/loader version, exact mod/shader/resource-pack versions, steps, expected
and actual behavior, frequency, and whether a fresh disposable instance reproduces
it. For source builds include the commit, runtime pin, toolchain and relevant
command. Keep known-good originals and worlds backed up before a reproduction.
Do not infer a cause from the final log line.

Collect matching build/session/current-run reports promptly, then review them
locally before sharing a **minimal sanitized excerpt**. Redact access/refresh
credentials, device codes, authorization headers, account-store keys, session/
profile identifiers, personal paths, IPs/hostnames and chat/world/server personal
data as appropriate. Do not upload account files, private keys, complete caches,
raw report bundles or game/mod JARs. Keep run/version markers needed to correlate
the excerpt; describe each redaction. The issue form lists the current LAN/FTP
retrieval paths; those services do not sanitize content for you. Use a trusted LAN
and avoid forwarding their ports. Suspected vulnerabilities use [private reporting](SECURITY.md),
not public crash/compatibility issues.

## Changes and review

Keep changes scoped, explain behavior and run affected checks. Include local,
hosted and console evidence with explicit limitations. Preserve original game/mod
JARs, publisher hashes, existing compatibility/failure behavior, saved user choices,
fixtures, frozen validation and exact released bytes. New compatibility belongs
in runtime or supported harness/configuration, not game-JAR rewrites. Retain
upstream licenses/credits and matching OpenAL source/relink support. Never commit
SDK/cache/build outputs, downloaded game files, secrets or personal logs. Ordinary
GitHub pull requests can describe a proposed change; there is no mandatory private
contribution service or claim that CI establishes console acceptance.
