/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <cstdint>
namespace prospero_palette {
inline int selected=0;
// Recolor the launcher's green design tokens, preserving luminance structure.
// Images, warning reds, and positive Done buttons retain their own colors.
inline std::uint32_t rgb(std::uint32_t value){
 if(selected<=0||selected>5)return value;
 int r=(value>>16)&255,g=(value>>8)&255,b=value&255;
 if(g<=r||g<=b)return value;
 int low=r<b?r:b,span=g-low;
 static constexpr int hues[6][3]={{0,255,100},{0,150,255},{160,90,255},{255,80,160},{255,170,40},{150,150,150}};
 const auto& h=hues[selected];
 return ((low+span*h[0]/255)<<16)|((low+span*h[1]/255)<<8)|(low+span*h[2]/255);
}
inline std::uint32_t raw_ink(std::uint32_t rgb){return 0xff000000u|((rgb&255)<<16)|(rgb&0xff00)|((rgb>>16)&255);}
}
