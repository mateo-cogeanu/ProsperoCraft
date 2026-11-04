# Local208 — 1.21.10 Vanilla and launcher controls

Title **PPSA99874**, app **01.000.208**. The user reports1.21.11 Vanilla working
on207 and requests1.21.10 next. [The feedback record](validation/client207-console-feedback-2026-11-04.json)
preserves its scope; exact207 bytes remain unchanged.208 enables development
Vanilla1.21.10 and1.21.11 only. Earlier1.21 releases and all121 Fabric stay gated.
No release, prerelease or Store action is authorized.

## Changes

1.21.10 keeps original publisher game/libraries and the existing isolated matching
LWJGL3.3.3 native owner. Its genuine OSHI6.6.5 SystemInfo overlay uses original
interfaces and reports the existing UNKNOWN enum for PS5. Real startup CPU identity
and logical count support the original GLX CPU entry. Unsupported telemetry throws;
no desktop JNA initialization or OS/version spoofing is used for that path.

Every Zink instance reads the current launcher resolution and sets PS5_RENDER_SIZE
before GLFW initialization. SDL reports that mode initially and selects it for the
surface, even when Minecraft has an old1080p logical window. An explicit unavailable
size fails instead of silently rendering another size. The pinned VideoOut inventory
already has1080p/1440p/4K; two additional sizes cover the launcher720p/900p choices,
using existing tiled-buffer allocation/registration and refresh-rate policy. This
is a driver mode inventory, not an imposed game resolution. Non-Zink launch policy
retains its previous behavior; exact PS5 presentation for all sizes remains pending.

The launcher keyboard previously wrapped navigation over40 character cells,
excluding five action buttons. Navigation now covers45 selections with spatial
mapping to the action row. X activates the highlighted action, and native drawing
highlights it. Existing controller shortcuts and pointer actions remain. This
change does not touch the ingame keyboard.

## Evidence and console checks

Local19fast and11native checks pass. Source-only execution uses an empty explicit
dependency cache and invocation from/tmp. Additional manual checks exercise actual
SDL query/surface bodies at all five sizes, stale-window precedence, refresh/plane
controls and malformed/unavailable refusal. Publisher checks run original1.21.10
GLX CPU initialization, valid/missing identity, original desktop selection and no
PS5 JNA initialization. Original1.21.10 GlDevice construction/close and three genuine
Zink context/readback/buffer/sync cycles pass on host lavapipe. These are neither
full original Main/world nor PS5 RADV/presentation evidence.

[Validation](validation/client121-vanilla-208-2026-11-04.json) records package and
hosted checks separately. On208 test a new1.21.10 Vanilla instance, install/title,
world create/join, play, save/title/reload, Quit/library/relaunch, audio/controller
and keyboard/mouse. In the launcher keyboard, move Down to the action row and use
X on Done/Cancel/Space/Case/Backspace. Select4K in launcher settings and verify the
actual game framebuffer, then regress other sizes and existing26.x Zink instances.
Retest1.21.11, the report download path and26.x Vulkan behavior. Shader rendering,
server join, full resource budgets and endurance remain separate pending scope.
