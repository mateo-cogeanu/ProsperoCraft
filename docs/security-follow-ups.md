# Security follow-ups

## LAN log-service access policy — open, 31 October 2026

Inspection of runtime-owned `Development/java25/probe/log_share.hpp` at runtime
[`f65e1b9`](https://github.com/mateo-cogeanu/ps5-java25-homebrew/blob/f65e1b990aa1d1619be1c411aa2efae701869b63/Development/java25/probe/log_share.hpp) found
IPv4 `INADDR_ANY` binding and unauthenticated GET access to an explicit list of
reports/status endpoints. There is no per-report expiry; stop closes the listener,
but persisted current/previous logs are retained. This is an exposure concern on
untrusted LANs, not evidence of a demonstrated exploit or a security audit.

Follow-up owner: Java runtime repository for reusable listener implementation;
ProsperoCraft for launcher exposure, user controls and integration. Before code
changes, choose a compatible binding/access/authentication and expiry policy,
including support for external runtime-address helpers without preset device IPs
or client-IP filters. Review report contents and redaction, current/previous data
retention, connection limits, failure behavior and console retrieval usability.
Add host coverage for the chosen policy and exact PS5 retrieval/lifecycle checks;
update consumer integration/pins and publish each owning repository. No policy
choice or runtime repair is authorized or claimed by this documentation task.

Private security reporting is now enabled as explicitly authorized; see
[SECURITY.md](../SECURITY.md). No reporting-channel decision remains open.
