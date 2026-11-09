# Java17 / original1.20 bootstrap002 diagnostics

Standalone PPSA99878 version01.000.002 follows the [001crash record](validation/client-java17-bootstrap-001-crash-2026-11-09.json).
The retained run entered JNI_CreateJavaVM and completed the extended JIMAGE
allocation/read/read-only setup, then stopped without a PC. Original Minecraft
was not reached. The cause is unproven; no crash fix is claimed from these logs.

002 keeps the exact VM settings and class image, adding runtime17 fixed phase
markers and the existing scoped native fault recorder around VM creation. The
recorder logs a binary anchor and bounded signal context and forwards prior
handlers without recovery or context rewriting. Scope exit leaves newly installed
VM handlers alone. On startup/reopen, the probe precreates/chmods only its three
unauthenticated diagnostic files0644 without truncating previous bytes, allowing
FTP retrieval. Other title/account/instance files and folder permissions stay.
The001trace was downloaded after explicit FTP SITE CHMOD644 succeeded; no raw
reports are published. Runtime changes are pinned at`3c1ac7426072e90eec7171e67b4df23839e70f45`.

Install the new separate002title and run rows1then2. If2passes, finish3and4.
If it crashes, reopen002once and leave it at the probe screen; do not reinstall001
or rerun the crashing row before retrieval. Report which row passed/failed.
This remains original entry/JNI testing; no playable menu/world or shader/C2 pass.

Local ZIP:`dist/PPSA99878.zip` in the runtime workspace,
SHA256`879b00a744efa59530533b5d55c37c4b9bf756e4eb5473bb30e7a65049bd10ce`. See the
[exact build record](validation/client-java17-bootstrap-002-build-2026-11-09.json).
Failed001ZIP/title/symbols are preserved under local-tests/source history. The
working Java25 launcher and frozen17/21startup packages stay unchanged. Physical
002VM/fault/phase results are pending. No public binary release or Store update.

Reports in this title's own download0:

- `mc120-java17-bootstrap.log`: scope installation, image anchor and check status.
- `java17-vm-trace.log`: runtime phases and JIMAGE progress.
- `mc120-java17-fault.log`: existing scoped native signal/frame capture.

Cyberduck can access the active reports at`/mnt/sandbox/download/PPSA99878`.
The title sandbox's download0alias was inaccessible to FTP even while the direct
active download mount was listed. Use the fresh listing and default Download;
keep the first retrieval locally. Raw logs remain local. Reproduction uses the
same explicit [package helper](../tools/package_java17_bootstrap.py) and reviewed
original inputs as001; the helper additionally compiles the existing diagnostic
Csource with this probe's dedicated path. It does not link a Java25VM or343JNI.
