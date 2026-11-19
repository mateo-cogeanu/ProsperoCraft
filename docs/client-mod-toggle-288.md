# Enable and disable installed mods

Local candidate 01.000.288 adds an X-button toggle to each mod in Instance
Settings → Mods → Installed. Rows show Enabled or Disabled. RIGHT still opens
the existing uninstall confirmation. Resource packs and shader packs retain their
existing controls.

Disabling renames `mods/name.jar` to `mods/name.jar.disabled`; enabling reverses
the rename. File bytes and the content receipt stay unchanged. Both managed and
manually added mods appear after reopening the launcher. Existing destination
files and symlinks are rejected rather than overwritten. A disabled mod can also
be uninstalled through the existing receipt transaction.

Launch checks and dependency repair inspect active mods only. If an enabled mod
requires a disabled provider, repair explains which dependency to enable instead
of reinstalling it. Fabric nested module IDs and provided aliases are included.
Modrinth selections and browser uploads also respect disabled files. Automatic
Controlify installation respects a disabled Controlify. Disabling Controlify
removes its in-game controller support until enabled again.

The 21 launcher checks and 14 native checks pass. The actual launcher selection
handler, file preservation, reopen, collision/path refusal, uninstall, disabled
nested Fabric dependency and Controlify default policy are exercised on the host.
The signed package passes its independent audit. These checks do not establish
physical PS5 UI or game acceptance.

On 288, check controller navigation and both toggle states, reopen the launcher,
launch with an optional mod disabled, enable it again, and verify a disabled
required dependency produces the expected explanation. Check save/reload and
shader rendering before release approval. Public release 287 remains unchanged.

[Build validation](validation/client288-mod-toggle-2026-11-19.json)
