/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "libffi callbacks and real OpenAL loopback", // check_name
 "01.000.026", // version
 "Native026:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 512 MiB max heap", // vm_result
 "ClientNativeBootstrap25", // fixture
 "GPU026 %s code=%d: %s", // stage_format
 "Minecraft Native Callback/OpenAL Acceptance 01.000.026 / PPSA99874\n", // build_note
 "Client026 ready: press X once for real callbacks and OpenAL mixer checks. No sound/window expected. Keep open for logs.", // ready_note
 "Client026 controller setup failed. Existing logs remain available.", // controller_failure
 "Client026 running real Vulkan loader/libffi callbacks and OpenAL loopback mixer. No Minecraft menu or speaker output test.", // running_note
 "Client026 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: native callbacks/OpenAL mixer/JVM stop;Minecraft startup not tested.", // pass_state
 "Client026 ALL5 PASS: real callbacks/OpenAL mixer and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
