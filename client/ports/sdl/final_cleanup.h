/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef PROSPERO_FINAL_SDL_CLEANUP_H
#define PROSPERO_FINAL_SDL_CLEANUP_H
#include <SDL3/SDL.h>
/* After GLFW destroys its windows and releases VIDEO, on SDL's real main thread.
 * Explicit caller policy only: default behavior retains its existing references. */
static inline bool prospero_sdl_finalize(void){
 Uint32 live=SDL_WasInit(0);
 if(!live)return true;
 if((live&~0x6210u)||!SDL_IsMainThread())return false;
 SDL_Quit();
 return SDL_WasInit(0)==0;
}
#endif
