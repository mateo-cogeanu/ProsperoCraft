# Controlify keyboard on Minecraft 26.3 Fabric

Minecraft 26.3 clears the previous screen's focus when switching screens.
Controlify 3.5.3 opens its keyboard overlay with a direct reference to the
previous screen's text box. That box rejects typed characters and editing keys
after losing focus. Separately, Controlify's built-in Backspace sends scan
position 42 and shortcut value 0. Minecraft's text fields expect value 8.
The earlier resource pack corrects Backspace for its three layouts, while the
new fix also covers the built-in fallback and other layouts using that action.

In PPSA99874/01.000.281, a [small client companion mod](../client/ports/controlify263-keyboard/fabric.mod.json)
uses Fabric's existing Mixin mechanism on the two Controlify classes. It
captures the focused text box as the overlay is constructed and returns focus
after initialization if the same field still belongs to the background screen
and that screen has acquired no other focus. It also fills in the missing
Backspace shortcut while preserving already-correct keys. The launcher adds
the companion through Fabric's `fabric.addMods` only for 26.3 Fabric with
exactly one installed Controlify JAR matching the original 3.5.3 hash.
Minecraft and Controlify load from their original publisher JARs. The previous
resource pack can still be used, and the Java HTTP module from build 280 is
included.

The [packager](../tools/package_client_121.py) builds the companion from source
with checked inputs supplied as `--controlify-jar`, `--mixin-jar` and
`--minecraft-263-jar`. The [package auditor](../tools/audit_client_121.py)
verifies the companion entries and launcher integration. Host tests used real
Knot, Controlify and Minecraft classes. A headless screen fixture reproduced
loss of typing after focus was cleared, then verified restored typing and
Backspace with the companion. The fixture also checked ordinary chat input
and reproduced the original zero-code Backspace failure.

On PS5, open the keyboard in the same field that failed. Type a lowercase
letter, a shifted letter and a space. Test both selecting Del and pressing the
controller's Backspace shortcut, then close and reopen the keyboard. Check chat
and a separate field such as server address. World, save and shader
confirmation remain pending for this exact build.
