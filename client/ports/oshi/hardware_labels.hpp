/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include "console_model.hpp"
namespace prospero_hardware {
inline const char* cpu(ps5::console::Model model) {
 switch(model){case ps5::console::Model::standard:return "AMD Zen 2, 8C16T (PS5)";case ps5::console::Model::pro:return "AMD Zen 2, 8C16T (PS5 Pro)";default:return "AMD CPU (PS5; model unknown)";}
}
inline const char* gpu(ps5::console::Model model) {
 switch(model){case ps5::console::Model::standard:return "AMD RDNA 2, 36 CUs (PS5)";case ps5::console::Model::pro:return "AMD RDNA 2.x, 60 CUs (PS5 Pro)";default:return "AMD RDNA (PS5; model unknown)";}
}
}
