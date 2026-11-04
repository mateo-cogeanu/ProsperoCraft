/* SPDX-License-Identifier: GPL-3.0-or-later
 * Aurora-inspired motion around the existing ProsperoCraft layout/model.
 * The original toolkit and Vulkan contributions retain their vendored notices.
 */
#pragma once
#include "ui/components/grid.hpp"
#include "ui/components/dialog.hpp"
#include "ui/motion.hpp"
namespace prospero_ui {
struct Effects {
 hui::ui::Feedback feedback;
 hui::tween::Spring switches[10];
 hui::ui::GridView grid,previous_grid;
 hui::ui::Dialog dialog;
 hui::ui::ProgressBar progress;
 hui::ui::SpringColor palette[4];
 hui::tween::Spring emphasis;
 hui::tween::Timer entrance;
 hui::ui::Pulse press;
 float clock=0,age=0,mode_age=1;
 int backdrop=5;
 int page=-1,previous_page=-1,selection=-1,model_row=-1,press_page=-1,press_row=-1;
 bool page_changed=false,ready=false;
 std::string items_key,previous_items_key;
 std::uint64_t last_press=0;
};
inline Effects* effects=nullptr;
inline hui::gfx::Color icon_color(int icon){
 constexpr std::uint32_t colors[]={0x67df9b,0x9edb78,0xb29bea,0x6bd3de,0xe68e96,0x61c9a2,0xe6cc7a,0xbedfe8};
 return hui::gfx::Color::rgb(colors[icon>=0&&icon<8?icon:0]);
}
}
