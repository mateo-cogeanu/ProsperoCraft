/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "../bootstrap/acceptance_config.hpp"
namespace {
constexpr prospero_acceptance::Config acceptance{
 "Real STB PNG readback and codec controls", // check_name
 "01.000.031", // version
 "STB031:", // notification_prefix
 "Real JNI_CreateJavaVM, -Xint, 128 MiB max heap", // vm_result
 "ClientSTB25", // fixture
 "STB031 %s code=%d: %s", // stage_format
 "Minecraft STB Codec Acceptance 01.000.031 / PPSA99874\n", // build_note
 "Client031 ready: press X once for real STB image/codecs checks. No game window expected. Keep open for logs.", // ready_note
 "Client031 controller setup failed. Existing logs remain available.", // controller_failure
 "Client031 running real STB PNG roundtrip and codec controls. No Minecraft menu or speaker output test.", // running_note
 "Client031 failed check%d: %.160s. Keep open for logs; close/reopen to retry.", // failure_format
 "ALL5 PASS: STB PNG/codecs/JVM stop;Minecraft startup not tested.", // pass_state
 "Client031 ALL5 PASS: real STB PNG/codecs and JVM shutdown. Minecraft startup and speaker output remain untested.", // pass_note
};
}
#include "../bootstrap/acceptance_impl.hpp"
