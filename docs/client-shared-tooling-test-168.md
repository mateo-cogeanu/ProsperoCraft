# Local168 shared-tooling regression candidate

PPSA99874 /01.000.168 is a local test candidate built from clean source commit
`8d9874ddda9a3c468d8f2dc5b1a64147b76a26f0`. It contains the shared-tooling refactor
and reproducible Java identity from [the refactor](tooling-sharing.md), plus a
version increment to distinguish it from accepted167. It changes no runtime pin,
game/mod JAR, native performance policy or OAuth client/endpoint/scope/token flow.
It is not a GitHub/Store release and has no new physical-console acceptance.

Full current-client SDK build and specialized package audit pass. Native and both
Java identity resources agree on168. Both exact OpenAL relink paths pass and its
kit includes the shared consumer headers. The native launcher object is equivalent
to167 after version-string normalization. Only the three User-Agent Java classes
change; ProsperoBuild.class and its resource are added. Original167 checksums,
release audit, snapshots, symbols and recovery baseline are preserved.

Local artifacts are retained under ignored
`dist/candidates/ProsperoCraft-Refactor-01.000.168/` in the consumer workspace:
package, symbols, build-status, validation, corresponding-source/relink ZIP and
SHA256SUMS. A convenient delivery copy is the runtime workspace's
`dist/ProsperoCraft-01.000.168-test.zip`. Nothing compiled is committed here.

Package SHA-256:
`f069b642d326624a839b6ea5521e8042eec3d876fd4ceb089abba4af455c41d8`.

Install the complete PPSA99874 folder using the existing homebrew workflow.
Check the168 launcher label, retained account/instances and controller/keyboard/
mouse navigation. Check network listings and a download, with saved-login refresh
if needed. Start Vanilla26.2 and Fabric26.2; check controller/input handoff, mouse/
keyboard and audio, then save/quit/reopen. Report which build and steps passed or
failed. Keep credentials and raw console reports local. No ALL PASS, endurance
result or release authorization is inferred until the user tests these exact bytes.

See [measured validation](validation/client168-refactor-build-2026-10-31.json).
This completes the previously storage-blocked full SDK/package verification;
the earlier refactor record remains an accurate record of its original test scope.
