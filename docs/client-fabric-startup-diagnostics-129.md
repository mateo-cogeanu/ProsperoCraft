# Fabric26.2 unreported native exit, app129

Reproduced128run1793278503-673552755 reaches the render thread, whose Java
output ends at Setting user. The native report ends after OpenAL metadata calls.
There is no captured fatal Java exception, VM abort or hs-error. A background
publickeys DNS warning is present but is not proven to cause the exit. Initial
reports had been overwritten by a later launcher-only reopen; the reproduced
run's Java/native reports are retained locally. The cause remains unresolved.

App129 adds bounded, allocation-free startup breadcrumbs around GLFW platform
initialization, SDL video/events setup, Vulkan loader handoff, display discovery,
monitor allocation, window creation, PS5 video-driver setup and RWLock creation.
Each translation unit permits128 literal diagnostic records at most; labels
contain no credentials or instance paths. Best-effort writes append to the
already served startup history, handle partial writes/EINTR, close each descriptor,
and preserve errno. No per-frame events or normal locks are logged.

The launcher now copies at most64KiB of the preceding VM trace into explicitly
marked startup-history records before JVM creation truncates its live trace.
These are prior-run records, not evidence about the new run. The existing
startup-history retention bound still applies. This fixes loss of native trace
context on a single reopen; it does not guarantee a stack trace for every exit.

Inspection also found unchecked GLFW backend monitor and video-mode allocations.
The monitor backend now allocates/checks the native monitor before initializing
its fields, rather than calling the upstream helper which dereferences a failed
allocation. Failure tears down the SDL/Vulkan setup and returns the existing
GLFW allocation error. Video-mode allocation returns NULL/count0 on failure.
This is a concrete failure-path repair, not a proven diagnosis of128's exit.

Host ASan/UBSan uses real GLFW/SDL: forced monitor allocation refusal returns an
OOM and cleans up SDL, then three normal init/event/window/terminate cycles pass.
The actual diagnostic writer passes cap, partial-write, EINTR, open-failure,
close and errno tests; actual SDL lock regression passes. Target and package
checks are in the validation record. Reusable Java runtime129 and all policies
remain unchanged; this set belongs only in ProsperoCraft. No official JAR or
heap/GC/settings/auth/instance changes. Keep prior candidates and Store121.

PS5 cause identification and Fabric startup/world/input/audio/save/reload remain
pending. This is a diagnostic candidate, not a verified fix, Store release or
frozen milestone. After a failure, reopen once and stay in the launcher so the
new boundary records and copied native tail can be retrieved.
