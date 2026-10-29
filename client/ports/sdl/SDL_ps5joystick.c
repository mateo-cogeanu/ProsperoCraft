/*
 * Dusklight for the PlayStation 5 - SDL3's joystick driver for the console.
 *
 * Up to four controllers, one per signed-in user, read through the title's
 * platform layer (ps5/src/platform.h). Each is a gamepad with a mapping of its
 * own, and reports itself as a DualSense so a title shows the right glyphs.
 *
 * SPDX-License-Identifier: Zlib
 */
/* Consumer changes: native gyro,rumble and translated DualSense trigger effects. */
#include "SDL_internal.h"

#ifdef SDL_JOYSTICK_PS5

#include "joystick/SDL_sysjoystick.h"
#include "joystick/SDL_joystick_c.h"

#include "platform.h"

/* Joystick buttons, in this order */
static const uint32_t ps5_buttons[] = {
    PAD_CROSS, PAD_CIRCLE, PAD_SQUARE, PAD_TRIANGLE,
    PAD_L1, PAD_R1, PAD_L3, PAD_R3,
    PAD_OPTIONS, PAD_TOUCH_PAD,
    PAD_UP, PAD_DOWN, PAD_LEFT, PAD_RIGHT,
};
#define PS5_BUTTONS ((int)SDL_arraysize(ps5_buttons))
#define PS5_AXES    6 // left x, left y, right x, right y, L2, R2

static bool ps5_pad_opened;
static uint32_t ps5_connected;              // a bit a player, as SDL knows them
static int ps5_device_player[PAD_PLAYERS];  // device index -> player
static int ps5_devices;

static SDL_JoystickID PS5_InstanceID(int player)
{
    return (SDL_JoystickID)(player + 1);
}

static void PS5_ListDevices(void)
{
    ps5_devices = 0;
    for (int player = 0; player < PAD_PLAYERS; player++) {
        if (ps5_connected & (1u << player)) {
            ps5_device_player[ps5_devices++] = player;
        }
    }
}

static void PS5_JoystickDetect(void)
{
    struct pad pad;
    uint32_t now;

    if (!ps5_pad_opened) {
        return;
    }
    pad_poll(&pad);
    now = pad_players();
    for (int player = 0; player < PAD_PLAYERS; player++) {
        const uint32_t bit = 1u << player;
        if ((now & bit) && !(ps5_connected & bit)) {
            ps5_connected |= bit;
            PS5_ListDevices();
            SDL_PrivateJoystickAdded(PS5_InstanceID(player));
        } else if (!(now & bit) && (ps5_connected & bit)) {
            ps5_connected &= ~bit;
            PS5_ListDevices();
            SDL_PrivateJoystickRemoved(PS5_InstanceID(player));
        }
    }
}

static bool PS5_JoystickInit(void)
{
    ps5_pad_opened = pad_open();
    PS5_JoystickDetect();
    return true;
}

static int PS5_JoystickGetCount(void)
{
    return ps5_devices;
}

static bool PS5_JoystickIsDevicePresent(Uint16 vendor_id, Uint16 product_id, Uint16 version, const char *name)
{
    return false;
}

static const char *PS5_JoystickGetDeviceName(int device_index)
{
    return "DualSense Wireless Controller";
}

static const char *PS5_JoystickGetDevicePath(int device_index)
{
    return NULL;
}

static int PS5_JoystickGetDeviceSteamVirtualGamepadSlot(int device_index)
{
    return -1;
}

static int PS5_JoystickGetDevicePlayerIndex(int device_index)
{
    return ps5_device_player[device_index];
}

static void PS5_JoystickSetDevicePlayerIndex(int device_index, int player_index)
{
}

static SDL_GUID PS5_JoystickGetDeviceGUID(int device_index)
{
    /* Sony's DualSense, with a driver signature no mapping database entry has:
     * the mapping is this driver's */
    return SDL_CreateJoystickGUID(SDL_HARDWARE_BUS_BLUETOOTH, 0x054c, 0x0ce6, 0, NULL,
                                  PS5_JoystickGetDeviceName(device_index), 'p', 0);
}

static SDL_JoystickID PS5_JoystickGetDeviceInstanceID(int device_index)
{
    return PS5_InstanceID(ps5_device_player[device_index]);
}

static bool PS5_JoystickOpen(SDL_Joystick *joystick, int device_index)
{
    joystick->nbuttons = PS5_BUTTONS;
    joystick->naxes = PS5_AXES;
    joystick->nhats = 0;
    if(pad_player_has_gyro(ps5_device_player[device_index]))SDL_PrivateJoystickAddSensor(joystick,SDL_SENSOR_GYRO,0.0f);
    SDL_SetBooleanProperty(SDL_GetJoystickProperties(joystick), SDL_PROP_JOYSTICK_CAP_RUMBLE_BOOLEAN, pad_player_has_rumble(ps5_device_player[device_index]));
    SDL_SetBooleanProperty(SDL_GetJoystickProperties(joystick), SDL_PROP_JOYSTICK_CAP_RGB_LED_BOOLEAN, false);
    return true;
}

static bool PS5_JoystickRumble(SDL_Joystick *joystick, Uint16 low_frequency_rumble, Uint16 high_frequency_rumble)
{
    return pad_player_rumble((int)joystick->instance_id-1,low_frequency_rumble,high_frequency_rumble)?true:SDL_SetError("PS5 compatible rumble failed");
}

static bool PS5_JoystickRumbleTriggers(SDL_Joystick *joystick, Uint16 left, Uint16 right)
{
    return SDL_Unsupported();
}

static bool PS5_JoystickSetLED(SDL_Joystick *joystick, Uint8 red, Uint8 green, Uint8 blue)
{
    return SDL_Unsupported();
}

static bool PS5_JoystickSendEffect(SDL_Joystick *joystick, const void *data, int size)
{
    return pad_player_send_effect((int)joystick->instance_id-1,data,size)?true:SDL_SetError("PS5 trigger effect unavailable,unsupported or failed");
}

static bool PS5_JoystickSetSensorsEnabled(SDL_Joystick *joystick, bool enabled)
{
    if(!pad_player_set_motion((int)joystick->instance_id-1,enabled))return SDL_SetError("PS5 motion sensor could not change state");
    return true;
}

static Sint16 PS5_Stick(float value)
{
    value = SDL_clamp(value, -1.0f, 1.0f);
    return (Sint16)(value * 32767.0f);
}

static Sint16 PS5_Trigger(float value)
{
    value = SDL_clamp(value, 0.0f, 1.0f);
    return (Sint16)(value * 65535.0f - 32768.0f);
}

extern void client_input_change(unsigned) __attribute__((weak));
static void PS5_JoystickUpdate(SDL_Joystick *joystick)
{
    const Uint64 timestamp = SDL_GetTicksNS();
    struct pad pad;

    /* PS5_JoystickDetect polled the pads just before */
    if (!pad_player((int)joystick->instance_id - 1, &pad) || (pad.held & PAD_INTERCEPTED)) {
        return;
    }
    if(client_input_change)client_input_change(pad.held);
    for (int i = 0; i < PS5_BUTTONS; i++) {
        SDL_SendJoystickButton(timestamp, joystick, (Uint8)i, (pad.held & ps5_buttons[i]) != 0);
    }
    SDL_SendJoystickAxis(timestamp, joystick, 0, PS5_Stick(pad.left_x));
    SDL_SendJoystickAxis(timestamp, joystick, 1, PS5_Stick(pad.left_y));
    SDL_SendJoystickAxis(timestamp, joystick, 2, PS5_Stick(pad.right_x));
    SDL_SendJoystickAxis(timestamp, joystick, 3, PS5_Stick(pad.right_y));
    SDL_SendJoystickAxis(timestamp, joystick, 4, PS5_Trigger(pad.l2));
    SDL_SendJoystickAxis(timestamp, joystick, 5, PS5_Trigger(pad.r2));
    int player=(int)joystick->instance_id-1;
    if(pad_player_motion_enabled(player)){
        const struct pad_reading *samples=NULL;int count=pad_player_readings(player,&samples);
        for(int i=0;i<count;i++){
            const struct pad_reading *s=&samples[i];
            if(!s->connected||(s->buttons&PAD_INTERCEPTED))continue;
            if(!__builtin_isfinite(s->angular_velocity[0])||!__builtin_isfinite(s->angular_velocity[1])||!__builtin_isfinite(s->angular_velocity[2]))continue;
            if(s->timestamp_us>UINT64_MAX/1000)continue;
            SDL_SendJoystickSensor(timestamp,joystick,SDL_SENSOR_GYRO,s->timestamp_us*1000,s->angular_velocity,3);
        }
    }
}

static void PS5_JoystickClose(SDL_Joystick *joystick)
{
    (void)pad_player_reset_triggers((int)joystick->instance_id-1);
    if(pad_player_has_rumble((int)joystick->instance_id-1))(void)pad_player_rumble((int)joystick->instance_id-1,0,0);
    if(pad_player_motion_enabled((int)joystick->instance_id-1))(void)pad_player_set_motion((int)joystick->instance_id-1,false);
}

static void PS5_JoystickQuit(void)
{
}

static bool PS5_JoystickGetGamepadMapping(int device_index, SDL_GamepadMapping *out)
{
    *out = (SDL_GamepadMapping){
        .a = { EMappingKind_Button, 0 },
        .b = { EMappingKind_Button, 1 },
        .x = { EMappingKind_Button, 2 },
        .y = { EMappingKind_Button, 3 },
        .leftshoulder = { EMappingKind_Button, 4 },
        .rightshoulder = { EMappingKind_Button, 5 },
        .leftstick = { EMappingKind_Button, 6 },
        .rightstick = { EMappingKind_Button, 7 },
        .start = { EMappingKind_Button, 8 },
        /* the pad's CREATE button is the shell's: the touch pad's click is "back" */
        .back = { EMappingKind_Button, 9 },
        .dpup = { EMappingKind_Button, 10 },
        .dpdown = { EMappingKind_Button, 11 },
        .dpleft = { EMappingKind_Button, 12 },
        .dpright = { EMappingKind_Button, 13 },
        .leftx = { EMappingKind_Axis, 0 },
        .lefty = { EMappingKind_Axis, 1 },
        .rightx = { EMappingKind_Axis, 2 },
        .righty = { EMappingKind_Axis, 3 },
        .lefttrigger = { EMappingKind_Axis, 4 },
        .righttrigger = { EMappingKind_Axis, 5 },
    };
    return true;
}

SDL_JoystickDriver SDL_PS5_JoystickDriver = {
    PS5_JoystickInit,
    PS5_JoystickGetCount,
    PS5_JoystickDetect,
    PS5_JoystickIsDevicePresent,
    PS5_JoystickGetDeviceName,
    PS5_JoystickGetDevicePath,
    PS5_JoystickGetDeviceSteamVirtualGamepadSlot,
    PS5_JoystickGetDevicePlayerIndex,
    PS5_JoystickSetDevicePlayerIndex,
    PS5_JoystickGetDeviceGUID,
    PS5_JoystickGetDeviceInstanceID,
    PS5_JoystickOpen,
    PS5_JoystickRumble,
    PS5_JoystickRumbleTriggers,
    PS5_JoystickSetLED,
    PS5_JoystickSendEffect,
    PS5_JoystickSetSensorsEnabled,
    PS5_JoystickUpdate,
    PS5_JoystickClose,
    PS5_JoystickQuit,
    PS5_JoystickGetGamepadMapping,
};

#endif // SDL_JOYSTICK_PS5
