/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "Real FreeType font rasterization and controls", // check_name
 "01.000.033", // version
 "FONT033:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 128 MiB max heap", // vm_result
 "ClientFreeType25", // fixture
 "FONT033 %s code=%d: %s", // stage_format
 "Minecraft FreeType Font Acceptance 01.000.033 / PPSA99874\n", // build_note
 "Client033 ready: press X once for real FreeType font rasterization checks. No game window expected. Keep open for logs.", // ready_note
 "Client033 controller setup failed. Existing logs remain available.", // controller_failure
 "Client033 running real FreeType glyph rasterization and font controls. No Minecraft menu or speaker output test.", // running_note
 "Client033 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: FreeType glyphs/guards/JVM stop;Minecraft startup not tested.", // pass_state
 "Client033 ALL5 PASS: real FreeType glyphs/guards and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
