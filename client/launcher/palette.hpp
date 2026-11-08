/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <cstdint>
#include "theme_tokens.hpp"
namespace prospero_palette {
inline int selected=0;
inline constexpr std::uint32_t accent=0x81e6af;
// The DualSense light bar washes out the launcher's pastel accents.
// Keep distinct hues for the pad and use a dim neutral for Graphite.
inline constexpr std::uint32_t controller_rgb[]={
 0x00b418, // Forest
 0x002adc, // Ocean
 0xc0a4e6, // Amethyst
 0xeb0e41, // Rose
 0xf05500, // Amber
 0x2a2a2a, // Graphite
};
static_assert(sizeof(controller_rgb)/sizeof(controller_rgb[0])==
              sizeof(prospero_theme::hues)/sizeof(prospero_theme::hues[0]));
// Recolor the launcher's green design tokens, preserving luminance structure.
// Images, warning reds, and positive Done buttons retain their own colors.
inline std::uint32_t rgb(std::uint32_t value){
 if(selected<=0||selected>5)return value;
 int r=(value>>16)&255,g=(value>>8)&255,b=value&255;
 if(g<=r||g<=b)return value;
 int low=r<b?r:b,span=g-low;

 const auto& h=prospero_theme::hues[selected];
 return ((low+span*h[0]/255)<<16)|((low+span*h[1]/255)<<8)|(low+span*h[2]/255);
}
inline std::uint32_t raw_ink(std::uint32_t rgb){return 0xff000000u|((rgb&255)<<16)|(rgb&0xff00)|((rgb>>16)&255);}
}
