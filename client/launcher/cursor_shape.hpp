/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <array>
namespace prospero_menu {
// Rounded silhouette traced from the user's reference: upright left edge,
// broad diagonal, rounded right nose and gently curved lower-left shoulder.
// Every change in direction is a cubic curve; there are no pointed vertices.
struct CursorShape {
 std::array<float,256> xy{};int count=0;
 void point(float x,float y){xy[count*2]=x;xy[count*2+1]=y;count++;}
 void curve(float ax,float ay,float bx,float by,float x,float y){float sx=xy[(count-1)*2],sy=xy[(count-1)*2+1];for(int i=1;i<=12;i++){float t=i/12.f,u=1-t;point(u*u*u*sx+3*u*u*t*ax+3*u*t*t*bx+t*t*t*x,u*u*u*sy+3*u*u*t*ay+3*u*t*t*by+t*t*t*y);}}
 CursorShape(){point(6,0);curve(8,0,9,1,11,3);curve(19,11,28,19,36,27);curve(40,31,37,36,32,36);curve(29,36,27,36,25,36);curve(22,36,20,37,18,39);curve(15,42,13,44,10,46);curve(5,51,0,48,0,42);curve(0,31,0,18,0,7);curve(0,3,2,0,6,0);--count;}
};
}
