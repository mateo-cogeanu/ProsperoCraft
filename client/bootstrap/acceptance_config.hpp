/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
namespace prospero_acceptance {
// Constant-initialized aggregate: no constructors, allocation or policy changes.
struct Config {
 const char* check_name;
 const char* version;
 const char* notification_prefix;
 const char* vm_result;
 const char* fixture;
 const char* stage_format;
 const char* build_note;
 const char* ready_note;
 const char* controller_failure;
 const char* running_note;
 const char* failure_format;
 const char* pass_state;
 const char* pass_note;
 };
}
