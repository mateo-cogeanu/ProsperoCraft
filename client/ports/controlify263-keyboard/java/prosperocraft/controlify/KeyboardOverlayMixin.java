package prosperocraft.controlify;

import dev.isxander.controlify.screenop.compat.vanilla.EditBoxComponentProcessor.EditBoxInputTarget;
import dev.isxander.controlify.screenop.keyboard.InputTarget;
import dev.isxander.controlify.screenop.keyboard.KeyboardLayoutWithId;
import dev.isxander.controlify.screenop.keyboard.KeyboardOverlayScreen.KeyboardPositioner;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "dev.isxander.controlify.screenop.keyboard.KeyboardOverlayScreen", remap = false)
abstract class KeyboardOverlayMixin {
    @Shadow @Final private Screen backgroundScreen;
    @Unique private EditBox prosperocraft$editor;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void rememberEditor(Screen screen, KeyboardLayoutWithId layout, InputTarget target,
                                KeyboardPositioner positioner, CallbackInfo ci) {
        if (target instanceof EditBoxInputTarget input && screen.getFocused() == input.editBox()) {
            prosperocraft$editor = input.editBox();
        }
    }

    @Inject(method = "init", at = @At("RETURN"))
    private void restoreEditorFocus(CallbackInfo ci) {
        // Minecraft 26.3 clears the previous screen's focus when showing the
        // overlay. Direct text/key delivery to the EditBox needs that focus.
        if (prosperocraft$editor != null && backgroundScreen.getFocused() == null
                && backgroundScreen.children().contains(prosperocraft$editor)) {
            backgroundScreen.setFocused(prosperocraft$editor);
        }
    }
}
