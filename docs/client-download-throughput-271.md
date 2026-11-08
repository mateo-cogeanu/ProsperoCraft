# Build271: download connection reuse and streamed progress

User reports1.21.1Fabric taking a long time at465/870MB, then advancing to468MB.
That establishes progress, not a measured network bottleneck. Cyberduck cannot
list the selected shared-cache directory (FTP550), so current partial-file growth
and exact transfer rate are unobserved. No network/server/storage cause is proven.

Two concrete installer behaviors are repaired:

* Publisher and Modrinth/Fabric GETs previously called disconnect after every
  successful body.271 closes fully consumed responses normally, allowing the
  genuine JDK keep-alive pool to reuse connections. Refused HTTP status, early
  cancellation, read failure, truncated declared body or close failure explicitly
  disconnects. No custom pool, HTTP stack, DNS bypass, redirect or certificate
  policy change. Default JDK pooling limits and user-selected1–6workers remain.
  Microsoft/account transports are unchanged.
* Full-install progress previously advanced only at file completion.271 reports
  staged byte deltas during64KiB streaming with serialized100ms UI throttling.
  One byte per file remains uncounted until checksum verification and publication.
  Cache hits count after hash verification, with no new network request. The
  counter includes reused verified bytes and bytes in active staging files; it
  is not a downloaded-byte/speed measurement or proof of verified readiness.
  Failure never publishes a receipt; next retry verifies/reuses completed files.
  Quick refresh retains its file/check-based progress. The phase now says
  Preparing Minecraft instead of implying a fresh install is repairing itself.

JDK documentation distinguishes closing a response (persistent connections may
remain shared) from disconnecting an idle socket:
[HttpURLConnection](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/HttpURLConnection.html).
A local real TLS test performs four sequential requests through the production
publisher/mod helpers and observes one server-side client port. Injected complete,
partial,truncated and read-refusal bodies verify disconnect ownership; existing
HTTPS status/redirect/TLS verification controls remain. A small chunked fixture
asserts progress becomes visible before EOF while final hashes still pass.

This reduces avoidable connection churn but provides no numeric PS5 speed claim.
Large assets can still be limited by CDN/network/storage. No cache purge, world
migration, global worker override, resume-Range protocol or game/JAR/GC change.
Exact271download rate/progress,cancellation/retry,offline/normal launch,existing
freeze sampler,shader and endurance remain physical tests. Preserve released267
and prior candidates. No release or Store update is authorized.
