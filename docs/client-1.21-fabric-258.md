# Local build 258 · Fabric 1.21.x

The user [reported all Vanilla 1.21.x releases working on PS5 in build 257](validation/client257-vanilla-console-2026-11-07.json).
Build 258 uses normal status for Vanilla and enables 1.21 through 1.21.11
as Fabric DEV TEST entries. The candidate uses the existing Java 25, GLFW and
Zink path and verified publisher downloads.

The other project keeps LWJGL under a single class loader and declares those
JARs as system libraries so that Fabric's Knot loader delegates to their owner.
ProsperoCraft applies that same ownership boundary with its existing verified
Fabric installer and the matching LWJGL 3.3.3 PS5 overlay. The launch class
loader resolves matching 3.3.3 class resources and classes together. The launcher
still owns SDL. Fabric's pinned upstream profile for each release supplies
Loader 0.20.1, intermediary mappings and the loader's dependencies. Profile
libraries replace game libraries with the same Maven group and artifact during launch,
which prevents the duplicate ASM failure observed on 1.21.2. Mojang's original
JAR stays intact. Fabric performs its standard intermediary remapping in its own
cache. The quit audit uses Fabric's mapping resolver to find the same Minecraft
instance and running-state methods that Vanilla uses.
[Other project's class loader setup](https://github.com/tmghd272/ProsperoCraft/blob/beta/src/java/McBoot.java#L827-L860)

Test the first launch with a new Fabric instance and no mods. First launch may
take longer while Fabric builds its intermediary cache. Test world creation,
save and rejoin, and Quit Game. Then try matching Fabric API and individual
mods. Controlify auto-install is deferred for 1.21.x because these releases
use the older JNA SDL path. Built-in controller emulation remains available.
Sodium and Iris need separate PS5 validation.

See [build validation](validation/client258-fabric-1.21-2026-11-07.json) for
the exact package and host evidence.
