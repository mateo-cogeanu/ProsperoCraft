# Reporting a suspected vulnerability

Use GitHub's **private vulnerability reporting** for ProsperoCraft:
[Report a vulnerability privately](https://github.com/mateo-cogeanu/ProsperoCraft/security/advisories/new).
This channel was enabled with maintainer authorization and verified through the
repository API on31 October 2026. Do not open a public issue with exploit details.
No response deadline, bounty or independent security audit is promised.

Describe the affected build/commit and install source, game/loader/mod versions,
security impact, minimal reproduction and any safe mitigation. Share only the
minimum sanitized evidence. **Never publish or attach access tokens, refresh
credentials, device codes, account-store keys, private keys, personal data or raw
sensitive logs**, including in a private report; those secrets are not needed to
explain a flaw. Keep original evidence local and describe redactions. If you have
already exposed a credential, revoke/rotate it through its provider.

Ordinary compatibility failures, crashes and unsupported mods/shaders belong in
[public issue forms](https://github.com/mateo-cogeanu/ProsperoCraft/issues/new/choose)
with [sanitized reproduction details](CONTRIBUTING.md). Suspected unauthorized
access, credential disclosure or integrity bypass belongs in the private channel.

The application and LAN diagnostic services have **not been security-audited**.
The runtime HTTP log service currently binds available IPv4 interfaces and serves
allowlisted diagnostics without authentication or a per-report expiry. Logs can
contain sensitive information. Use a trusted LAN; do not expose/forward the
service to untrusted networks. Account encryption uses an app-local adjacent key,
not hardware-backed protection. The [tracked follow-up](docs/security-follow-ups.md)
records a separate design review; no binding/authentication/access policy change
is part of this documentation cleanup.
