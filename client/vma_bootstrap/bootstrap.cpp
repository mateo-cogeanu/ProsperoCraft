/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "Real VMA allocation and GPU transfer controls", // check_name
 "01.000.035", // version
 "VMA035:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 128 MiB max heap", // vm_result
 "ClientVMA25", // fixture
 "VMA035 %s code=%d: %s", // stage_format
 "Minecraft VMA Allocator Acceptance 01.000.035 / PPSA99874\n", // build_note
 "Client035 ready: press X once for real VMA allocation/GPU transfer checks. No game window expected. Keep open for logs.", // ready_note
 "Client035 controller setup failed. Existing logs remain available.", // controller_failure
 "Client035 running real VMA allocation/GPU transfers and guards. No Minecraft menu or speaker output test.", // running_note
 "Client035 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: VMA allocation/GPU transfers/guards/JVM stop;Minecraft startup not tested.", // pass_state
 "Client035 ALL5 PASS: real VMA allocation/GPU transfers/guards and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
