/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include "console_model.hpp"
namespace prospero_hardware {
inline const char* cpu(ps5::console::Model model) {
 switch(model){case ps5::console::Model::standard:return "AMD Zen 2, 8 cores/16 threads (PlayStation 5)";case ps5::console::Model::pro:return "AMD Zen 2, 8 cores/16 threads (PlayStation 5 Pro)";default:return "AMD CPU (PlayStation 5; model unknown)";}
}
inline const char* gpu(ps5::console::Model model) {
 switch(model){case ps5::console::Model::standard:return "AMD RDNA 2, 36 CUs (PlayStation 5)";case ps5::console::Model::pro:return "AMD Radeon RDNA (PlayStation 5 Pro)";default:return "AMD Radeon RDNA (PlayStation 5; model unknown)";}
}
}
