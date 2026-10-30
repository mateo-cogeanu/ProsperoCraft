/* Temporary vanilla controls through normal SDL keyboard/mouse events and state.
 * SPDX-License-Identifier: MIT
 * Included after SDL keyboard/mouse internals. No game hooks or replacements. */
#include "platform.h"
#include "ps5_bindings.h"
#include "../mesa/keyboard_layout.h"
extern int client_wsi_cursor(bool show,float x,float y,int character);
extern int client_wsi_keyboard(bool show,int selected,int lower,int symbols,const char*preview);
static struct {
    SDL_KeyboardID keyboard;
    SDL_MouseID mouse;
    Uint32 keys, blocked;
    Uint8 buttons;
    Uint64 repeat_at[30], last_pump;
    Uint32 held;float cursor_x,cursor_y;bool cursor_ready,typing,lower,mode_known,captured;int character;
    bool active,primed, devices,symbols;Uint32 keyboard_direction;Uint64 keyboard_repeat;char preview[129];unsigned preview_length;
} ps5_temp;
static unsigned short ps5_temp_keys[30];
static bool ps5_temp_bindings_ready;
static bool PS5_MappedDown(Uint32 keys,unsigned code){for(int n=0;n<30;n++)if(ps5_temp_keys[n]==code&&(keys&(1u<<n)))return true;return false;}
static Uint8 PS5_MappedMouse(Uint32 keys,Uint8 buttons){for(int n=0;n<30;n++)if((keys&(1u<<n))&&ps5_temp_keys[n]>=513)buttons|=(Uint8)(1u<<(ps5_temp_keys[n]-513));return buttons;}
static void PS5_TempKeys(Uint64 now, Uint32 keys, Uint8 buttons, SDL_Window *window)
{
    Uint8 mapped=PS5_MappedMouse(keys,buttons),old_mouse=PS5_MappedMouse(ps5_temp.keys,ps5_temp.buttons);
    for(int n=0;n<30;n++) {
        unsigned code=ps5_temp_keys[n];if(!code||code>=512)continue;
        bool seen=false;for(int j=0;j<n;j++)if(ps5_temp_keys[j]==code)seen=true;if(seen)continue;
        bool before=PS5_MappedDown(ps5_temp.keys,code),after=PS5_MappedDown(keys,code);
        if(before!=after)SDL_SendKeyboardKey(now,ps5_temp.keyboard,0,(SDL_Scancode)code,after);
    }
    for(int n=0;n<8;n++)if((keys^ps5_temp.keys)&(1u<<n))ps5_temp.repeat_at[n]=now+350000000ull;
    for(int i=0;i<3;i++)if((mapped^old_mouse)&(1u<<i))SDL_SendMouseButton(now,window,ps5_temp.mouse,(Uint8)(i==2?SDL_BUTTON_MIDDLE:i?SDL_BUTTON_RIGHT:SDL_BUTTON_LEFT),(mapped&(1u<<i))!=0);
    ps5_temp.keys=keys;ps5_temp.buttons=buttons;
}
static void PS5_TempRelease(SDL_Window *window, Uint64 now)
{
    PS5_TempKeys(now,0,0,window);
    ps5_temp.primed=false;ps5_temp.last_pump=0;ps5_temp.held=0;ps5_temp.cursor_ready=false;ps5_temp.typing=false;
    (void)client_wsi_keyboard(false,0,0,0,"");
    (void)client_wsi_cursor(false,0,0,0);
}
static bool PS5_GamepadOwned(void){
 if(!SDL_WasInit(SDL_INIT_GAMEPAD))return false;
 /* A subsystem init is not a working controller manager. Only surrender the
  * fallback once a consumer actually opens one of this port's four IDs. */
 for(int id=1;id<=4;id++)if(SDL_GetGamepadFromID((SDL_JoystickID)id))return true;
 return false;
}
static void PS5_PumpTemporaryInput(SDL_Window *window)
{
    Uint64 now=SDL_GetTicksNS();
    if(!ps5_temp_bindings_ready){for(int n=0;n<30;n++)ps5_temp_keys[n]=ps5_default_bindings[n];(void)ps5_parse_bindings(SDL_GetHint("PS5_CONTROLLER_BINDINGS"),ps5_temp_keys);ps5_temp_bindings_ready=true;}
    /* Explicit opt-in, with automatic handoff when a mod opens a gamepad.
     * Future Controlify integration must also turn this hint off explicitly. */
    if(!window || SDL_GetKeyboardFocus()!=window ||
       !SDL_GetHintBoolean("PS5_TEMPORARY_CONTROLS",false) || PS5_GamepadOwned()) {
        if(ps5_temp.active){PS5_TempRelease(window,now);ps5_temp.active=false;}
        return;
    }
    ps5_temp.active=true;
    if(!ps5_temp.devices) {
        ps5_temp.keyboard=SDL_GetNextObjectID();ps5_temp.mouse=SDL_GetNextObjectID();
        SDL_AddKeyboard(ps5_temp.keyboard,"PS5 temporary controller keys");
        SDL_AddMouse(ps5_temp.mouse,"PS5 temporary controller mouse");
        ps5_temp.devices=true;(void)pad_open();
    }
    struct pad state;pad_poll(&state);
    const struct pad_reading *readings=NULL,*last=NULL;
    int count=pad_readings(&readings);
    bool captured=SDL_GetWindowRelativeMouseMode(window);
    if(ps5_temp.mode_known&&captured!=ps5_temp.captured)PS5_TempRelease(window,now);
    ps5_temp.mode_known=true;ps5_temp.captured=captured;
    /* Buffered edges retain taps shorter than one rendered frame. */
    for(int n=0;n<count;++n) {
        const struct pad_reading *p=&readings[n];
        if(!p->connected || (p->buttons&PAD_INTERCEPTED)) {
            PS5_TempRelease(window,now);last=NULL;continue;
        }
        Uint32 held=p->buttons;
        if(p->l2>127)held|=0x10000000u;
        if(p->r2>127)held|=0x20000000u;
        if(!ps5_temp.primed) {ps5_temp.blocked=held;ps5_temp.primed=true;}
        /* Release launch-held buttons/triggers before they can activate items. */
        ps5_temp.blocked&=held;held&=~ps5_temp.blocked;
        Uint32 edge=held&~ps5_temp.held;ps5_temp.held=held;
        if(!captured&&(((held&PAD_TOUCH_PAD)&&(edge&PAD_R3))||(edge&PAD_L3))){
            ps5_temp.typing=!ps5_temp.typing;ps5_temp.keyboard_direction=0;ps5_temp.keyboard_repeat=0;
            if(ps5_temp.typing){ps5_temp.character=10;ps5_temp.lower=true;ps5_temp.preview_length=0;ps5_temp.preview[0]=0;}
        }
        Uint32 keys=0;bool layer=(held&PAD_TOUCH_PAD)!=0;
        if(held&PAD_OPTIONS)keys|=1u<<5;
        if(captured) {
            if(held&PAD_CROSS)keys|=1u<<12;
            if(held&PAD_CIRCLE)keys|=1u<<14;
            if(held&PAD_L3)keys|=1u<<15;
            if(held&PAD_TRIANGLE)keys|=1u<<13;
            if(held&PAD_SQUARE)keys|=1u<<16;
            if(held&PAD_R3)keys|=1u<<18;
            if(held&PAD_DOWN)keys|=1u<<17;
            if(held&PAD_UP)keys|=1u<<6;
            if(held&PAD_LEFT)keys|=1u<<26;
            if(held&PAD_RIGHT)keys|=1u<<27;
        } else {
            /* Game menus use the pointer; no synthetic directional focus keys. */
            if(held&PAD_CIRCLE)keys|=1u<<5;
            if(held&PAD_TRIANGLE)keys|=1u<<13;
            if(held&PAD_SQUARE)keys|=1u<<14; /* inventory quick move */
        }
        if(layer) {
            keys=0;
            if(held&PAD_UP)keys|=1u<<21; /* debug */
            if(held&PAD_LEFT)keys|=1u<<19; /* HUD */
            if(held&PAD_RIGHT)keys|=1u<<20; /* screenshot */
            if(held&PAD_DOWN)keys|=1u<<24; /* advancements */
            if(held&PAD_TRIANGLE)keys|=1u<<22; /* chat */
            if(held&PAD_SQUARE)keys|=1u<<23; /* command */
            if(held&PAD_CROSS)keys|=1u<<4; /* keyboard confirm */
            if(held&PAD_CIRCLE)keys|=1u<<7; /* backspace */
            if(held&PAD_OPTIONS)keys|=1u<<25; /* fullscreen */
        } else {
            if(captured){
                if(p->left_y<80)keys|=1u<<8;
                if(p->left_y>176)keys|=1u<<9;
                if(p->left_x<80)keys|=1u<<10;
                if(p->left_x>176)keys|=1u<<11;
            }
        }
        Uint8 buttons=0;
        if(!layer){if(captured){if(held&0x20000000u)keys|=1u<<28;if(held&0x10000000u)keys|=1u<<29;}else buttons=((held&0x20000000u)?1:0)|((held&0x10000000u)?2:0);}
        if(!captured&&!layer) {
            if(held&PAD_CROSS)buttons|=1;
            if(held&PAD_R3)buttons|=4;
        }
        if(layer&&captured&&(held&PAD_R3))buttons=4;
        if(ps5_temp.typing&&captured)ps5_temp.typing=false;
        bool was_typing=ps5_temp.typing;
        if(ps5_temp.typing&&!captured){
            Uint32 direction=held&(PAD_LEFT|PAD_RIGHT|PAD_UP|PAD_DOWN);
            if(p->left_x<80)direction|=PAD_LEFT;if(p->left_x>176)direction|=PAD_RIGHT;if(p->left_y<80)direction|=PAD_UP;if(p->left_y>176)direction|=PAD_DOWN;
            bool move=direction&&(direction!=ps5_temp.keyboard_direction||now>=ps5_temp.keyboard_repeat);
            if(move){int delta=(direction&PAD_LEFT)?-1:(direction&PAD_RIGHT)?1:(direction&PAD_UP)?-10:10;ps5_temp.character=prospero_keyboard_move(ps5_temp.character,delta);ps5_temp.keyboard_repeat=now+(direction==ps5_temp.keyboard_direction?80000000ull:300000000ull);}
            ps5_temp.keyboard_direction=direction;
            if(edge&0x20000000u)ps5_temp.lower=!ps5_temp.lower;
            if(edge&0x10000000u)ps5_temp.symbols=!ps5_temp.symbols;
            keys=0;buttons=0;char text[2]={0,0};bool back=(held&(PAD_TRIANGLE|PAD_L1))!=0;
            if(edge&(PAD_SQUARE|PAD_R1))text[0]=' ';
            if(edge&PAD_CROSS){int choice=ps5_temp.character;if(choice<50)text[0]=prospero_keyboard_character(choice,ps5_temp.lower,ps5_temp.symbols);else if(choice==50)back=true;else if(choice==51)text[0]=' ';else if(choice==52)ps5_temp.lower=!ps5_temp.lower;else if(choice==53)ps5_temp.symbols=!ps5_temp.symbols;else if(choice==54){keys|=1u<<4;ps5_temp.typing=false;ps5_temp.blocked|=PAD_CROSS;}else if(choice==55)ps5_temp.typing=false;}
            if(text[0]){SDL_SendKeyboardText(text);if(ps5_temp.preview_length<128){ps5_temp.preview[ps5_temp.preview_length++]=text[0];ps5_temp.preview[ps5_temp.preview_length]=0;}}
            if(back){keys|=1u<<7;if(!(ps5_temp.keys&(1u<<7))&&ps5_temp.preview_length)ps5_temp.preview[--ps5_temp.preview_length]=0;}
            if(held&PAD_OPTIONS){keys|=1u<<4;ps5_temp.typing=false;ps5_temp.blocked|=PAD_OPTIONS;}
            if(edge&PAD_CIRCLE)ps5_temp.typing=false;

        }
        if(was_typing&&!ps5_temp.typing)ps5_temp.blocked|=held;
        if(!was_typing&&!ps5_temp.typing&&!layer&&(edge&(PAD_L1|PAD_R1)))
            SDL_SendMouseWheel(now,window,ps5_temp.mouse,0,(edge&PAD_L1)?1.0f:-1.0f,SDL_MOUSEWHEEL_NORMAL);
        PS5_TempKeys(now,keys,buttons,window);last=p;
    }
    (void)client_wsi_keyboard(ps5_temp.typing&&!captured,ps5_temp.character,ps5_temp.lower,ps5_temp.symbols,ps5_temp.preview);
    if(!(pad_players()&1u)) {PS5_TempRelease(window,now);return;}
    /* Repeats for navigation/editing; never repeated activation or idle input. */
    for(int i=0;i<8;++i)if(i!=4 && i!=5 && (ps5_temp.keys&(1u<<i)) && now>=ps5_temp.repeat_at[i]) {
        SDL_SendKeyboardKey(now,ps5_temp.keyboard,0,ps5_temp_keys[i],true);
        if(i==7&&ps5_temp.typing&&ps5_temp.preview_length)ps5_temp.preview[--ps5_temp.preview_length]=0;
        ps5_temp.repeat_at[i]=now+100000000ull;
    }
    if(last && ps5_temp.last_pump) {
        float dt=(float)(now-ps5_temp.last_pump)/1e9f;if(dt>0.05f)dt=0.05f;
        float x=((float)last->right_x-128.0f)/127.0f,y=((float)last->right_y-128.0f)/127.0f;
        if(x>-0.16f && x<0.16f)x=0;
        if(y>-0.16f && y<0.16f)y=0;
        if(captured){
            (void)client_wsi_cursor(false,0,0,0);
            ps5_temp.cursor_ready=false;
            if(x || y)SDL_SendMouseMotion(now,window,ps5_temp.mouse,true,x*650.0f*dt,y*650.0f*dt);
        }else{
            int w=0,h=0;SDL_GetWindowSize(window,&w,&h);
            if(w>0&&h>0){
                bool initial=!ps5_temp.cursor_ready;
                if(initial){ps5_temp.cursor_x=w*0.5f;ps5_temp.cursor_y=h*0.5f;ps5_temp.cursor_ready=true;}
                ps5_temp.cursor_x=SDL_clamp(ps5_temp.cursor_x+x*(float)w*0.47f*dt,0.0f,(float)(w-1));
                ps5_temp.cursor_y=SDL_clamp(ps5_temp.cursor_y+y*(float)h*0.83f*dt,0.0f,(float)(h-1));
                if(initial||x||y)SDL_SendMouseMotion(now,window,ps5_temp.mouse,false,ps5_temp.cursor_x,ps5_temp.cursor_y);
                (void)client_wsi_cursor(!ps5_temp.typing,ps5_temp.cursor_x/(w-1),ps5_temp.cursor_y/(h-1),0);
            }
        }
    }
    ps5_temp.last_pump=now;
}
