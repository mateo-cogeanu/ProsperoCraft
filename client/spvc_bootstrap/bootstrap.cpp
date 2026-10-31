/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "Real SPIRV-Cross translation and reflection", // check_name
 "01.000.036", // version
 "SPVC036:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 128 MiB max heap", // vm_result
 "ClientSPVC25", // fixture
 "SPVC036 %s code=%d: %s", // stage_format
 "Minecraft SPIRV-Cross Shader Acceptance 01.000.036 / PPSA99874\n", // build_note
 "Client036 ready: press X once for real SPIRV-Cross shader checks. No game window expected. Keep open for logs.", // ready_note
 "Client036 controller setup failed. Existing logs remain available.", // controller_failure
 "Client036 running real SPIRV-Cross shader translations/reflection and guards. No Minecraft menu test.", // running_note
 "Client036 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: SPIRV-Cross translations/reflection/guards/JVM stop;Minecraft startup not tested.", // pass_state
 "Client036 ALL5 PASS: real SPIRV-Cross translations/reflection/guards and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
