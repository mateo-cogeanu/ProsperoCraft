/* SPDX-License-Identifier: GPL-3.0-or-later
 * Event facade for Controlify's separately loaded SDL3 frontend. Minecraft and
 * GLFW retain the real SDL queue/filter. Only joystick connection records are
 * mirrored; axes/buttons/sensors/audio still use the genuine resident SDL. */
#include <SDL3/SDL.h>
#include <stdio.h>
#define CONNECTION_CAPACITY 256
static struct {Uint32 type;Uint64 timestamp;SDL_JoystickID which;} pending[CONNECTION_CAPACITY];
static unsigned head,count;
static bool ready,overflow;
static SDL_SpinLock queue_lock;
static SDL_EventFilter local_filter;
static void *local_userdata;

static bool SDLCALL observe(void *unused,SDL_Event *event){
 (void)unused;
 if(event->type!=SDL_EVENT_JOYSTICK_ADDED&&event->type!=SDL_EVENT_JOYSTICK_REMOVED)return true;
 SDL_LockSpinlock(&queue_lock);
 if(count==CONNECTION_CAPACITY)overflow=true;
 else{unsigned slot=(head+count)%CONNECTION_CAPACITY;pending[slot].type=event->type;pending[slot].timestamp=event->common.timestamp;pending[slot].which=event->jdevice.which;count++;}
 SDL_UnlockSpinlock(&queue_lock);
 return true; /* Watch only; never rejects the game's event. */
}
int prospero_controlify_events_preinit(void){
 if(ready)return 0;
 if(!SDL_InitSubSystem(SDL_INIT_EVENTS))return -1;
 if(!SDL_AddEventWatch(observe,NULL)){SDL_QuitSubSystem(SDL_INIT_EVENTS);return -1;}
 ready=true;
 return 0; /* One process-lifetime event-subsystem reference/watch. */
}
void prospero_controlify_SetEventFilter(SDL_EventFilter filter,void *userdata){
 if(!ready||!SDL_IsMainThread()){SDL_SetError("Controlify event facade requires initialized main thread");return;}
 local_filter=filter;local_userdata=userdata;
 fprintf(stderr,"PS5_CONTROLIFY_EVENTS scoped_filter=%d shared_game_queue=preserved\n",filter!=NULL);
}
bool prospero_controlify_GetEventFilter(SDL_EventFilter *filter,void **userdata){
 if(!ready||!SDL_IsMainThread())return false;
 if(filter)*filter=local_filter;if(userdata)*userdata=local_userdata;
 return local_filter!=NULL;
}
bool prospero_controlify_PollEvent(SDL_Event *event){
 if(!ready||!SDL_IsMainThread())return SDL_SetError("Controlify event facade requires initialized main thread");
 SDL_PumpEvents(); /* Actual platform/hotplug updates; does not drain game queue. */
 for(;;){
  SDL_Event copy;SDL_zero(copy);
  SDL_LockSpinlock(&queue_lock);
  if(overflow){overflow=false;SDL_UnlockSpinlock(&queue_lock);return SDL_SetError("Controlify connection event queue overflow (256); rescan required");}
  if(!count){SDL_UnlockSpinlock(&queue_lock);return false;}
  copy.type=pending[head].type;copy.common.timestamp=pending[head].timestamp;copy.jdevice.which=pending[head].which;
  SDL_UnlockSpinlock(&queue_lock);
  bool accepted=!local_filter||local_filter(local_userdata,&copy);
  // Main-thread-only consumer: producers only append and never change head.
  if(event||!accepted){SDL_LockSpinlock(&queue_lock);head=(head+1)%CONNECTION_CAPACITY;count--;SDL_UnlockSpinlock(&queue_lock);}
  if(accepted){if(event)*event=copy;return true;}
 }
}
