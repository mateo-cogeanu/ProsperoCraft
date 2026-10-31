/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "Real OSMesa OpenGL contexts and readback", // check_name
 "01.000.029", // version
 "OpenGL029:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 128 MiB max heap", // vm_result
 "ClientOpenGL25", // fixture
 "GL029 %s code=%d: %s", // stage_format
 "Minecraft OpenGL Provider Acceptance 01.000.029 / PPSA99874\n", // build_note
 "Client029 ready: press X once for real software OpenGL context/readback checks. No game window expected. Keep open for logs.", // ready_note
 "Client029 controller setup failed. Existing logs remain available.", // controller_failure
 "Client029 running real OSMesa software OpenGL contexts and readback. No Minecraft menu or speaker output test.", // running_note
 "Client029 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: OpenGL contexts/readback/JVM stop;Minecraft startup not tested.", // pass_state
 "Client029 ALL5 PASS: real OpenGL contexts/readback and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
