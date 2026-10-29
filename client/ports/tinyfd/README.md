# Explicit unavailable-desktop-dialog JNI adapter

Minecraft26.2eagerly loads original LWJGL tinyfd. PS5 has no supported desktop
file-dialog service. This consumer adapter provides the original JNI signatures,
identifies itself honestly and returns cancellation/unavailable results. No
upstream TinyFD implementation/version, GUI, shell execution, accepted answer or
file path is fabricated. Minecraft/launcher in-game menus are separate.

See docs/client-26.2-glfw-122.md. Do not advertise desktop dialog support.
