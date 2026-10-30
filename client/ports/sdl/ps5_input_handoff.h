/* SPDX-License-Identifier: GPL-3.0-or-later
 * Bounded read-only snapshots after physical input. No game/mod mode policy. */
#pragma once
static unsigned ps5_handoff_pending,ps5_handoff_budget;
static Uint64 ps5_handoff_next;
static void PS5_TracePhysicalInput(unsigned source){ps5_handoff_pending|=source;}
static void PS5_TraceInputHandoff(SDL_Window *window){
 if(!ps5_handoff_pending||ps5_handoff_budget>=16)return;
 Uint64 now=SDL_GetTicksNS();if(now<ps5_handoff_next)return;
 unsigned source=ps5_handoff_pending;ps5_handoff_pending=0;ps5_handoff_next=now+1000000000ull;ps5_handoff_budget++;
 fprintf(stderr,"PS5_HANDOFF physical=%u focus=%d cursor_visible=%d relative=%d",source,window!=NULL,SDL_CursorVisible(),window?SDL_GetWindowRelativeMouseMode(window):0);
 unsigned open=0;
 for(SDL_JoystickID id=1;id<=4;id++){
  SDL_Gamepad *pad=SDL_GetGamepadFromID(id);if(!pad)continue;open++;
  unsigned buttons=0;for(int b=0;b<SDL_GAMEPAD_BUTTON_COUNT;b++)if(SDL_GetGamepadButton(pad,(SDL_GamepadButton)b))buttons++;
  Sint16 axis[6];for(int a=0;a<6;a++)axis[a]=SDL_GetGamepadAxis(pad,(SDL_GamepadAxis)a);
  fprintf(stderr," pad%u_buttons=%u axes=%d,%d,%d,%d,%d,%d",id,buttons,axis[0],axis[1],axis[2],axis[3],axis[4],axis[5]);
 }
 fprintf(stderr," opened=%u\n",open);
}
