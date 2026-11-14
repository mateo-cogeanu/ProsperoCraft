package prosperocraft.controlify;

import dev.isxander.controlify.screenop.keyboard.InputTarget;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Mixin(targets = "dev.isxander.controlify.screenop.keyboard.KeyWidget", remap = false)
abstract class KeyWidgetMixin {
    @Redirect(method = "onPress",
              at = @At(value = "INVOKE", target =
                      "Ldev/isxander/controlify/screenop/keyboard/InputTarget;acceptKeyCode(III)Z"))
    private boolean forwardSpecialKey(InputTarget target, int scanCode, int keyCode, int modifiers) {
        // The built-in/fallback layout passes zero for Backspace's shortcut.
        return target.acceptKeyCode(scanCode, scanCode == 42 && keyCode == 0 ? 8 : keyCode, modifiers);
    }
}
