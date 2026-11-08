/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <cstdint>
#include "theme_tokens.hpp"
namespace prospero_palette {
inline int selected=0;
inline constexpr std::uint32_t accent=0x81e6af;
// Recolor the launcher's green design tokens, preserving luminance structure.
// Images, warning reds, and positive Done buttons retain their own colors.
inline std::uint32_t rgb(std::uint32_t value,int theme){
 if(theme<=0||theme>5)return value;
 int r=(value>>16)&255,g=(value>>8)&255,b=value&255;
 if(g<=r||g<=b)return value;
 int low=r<b?r:b,span=g-low;

 const auto& h=prospero_theme::hues[theme];
 return ((low+span*h[0]/255)<<16)|((low+span*h[1]/255)<<8)|(low+span*h[2]/255);
}
inline std::uint32_t rgb(std::uint32_t value){return rgb(value,selected);}
inline std::uint32_t raw_ink(std::uint32_t rgb){return 0xff000000u|((rgb&255)<<16)|(rgb&0xff00)|((rgb>>16)&255);}
}
