# Experimental PS5 microphone capture — local170, console pending

A real **default-off AudioIn → OpenAL capture path is implemented**. This supersedes
169's investigation-only state. It has host core/lifecycle coverage and a target
build; it does **not** establish captured DualSense speech or working multiplayer
voice chat. No recordings are saved by the local meter test.

## Console test and user control

Open **Instance Settings → Microphone** (left panel; from the bottom management
button press left). Select **Test input – 5 seconds** deliberately, speak only your
own consented test phrase, and read the reported blocks/nonzero sample count/peak/
silent blocks. First select **Wireless Controller / DualSense microphone** in PS5
system microphone settings and disconnect headsets/Remote Play for this test.
Repeat while the controller is muted, then unmuted, and compare. The test does not
unmute, set gain, change system routing or save a WAV. Counts alone are not formal
success: speech correlation and mute behavior must be observed on this exact build.

**Voice capture: ON** enables OpenAL capture for a matching mod; OFF is the saved
default. Enabling itself captures nothing. Enumeration probes one native block
only when opted in; opening/starting a mod's microphone begins actual capture.
The native selector is honestly named **PS5 system microphone (select DualSense in
PS5 settings)**. This API profile opens the initial user's system-selected route,
so attaching a headset can change it. Automatic built-in/headset identity remains
unimplemented: do not describe a headset route as the controller microphone.

## Native implementation and evidence boundary

`ps5_capture.hpp` owns one256-frame S16/16kHz block and a fixed16384-frame float
ring. A single exclusive lease owns at most one AudioIn handle. OpenAL uses one
128KiB-stack worker while recording; stop joins before close, failure disconnects
the OpenAL device, and close failure retains ownership until app restart. There
are no added always-running capture threads. Repeated start/stop and producer/
consumer bounds are tested with OS doubles. Actual PS5 blocking-read behavior,
thread creation under native pressure and resource release remain console checks.

Input is converted to48kHz mono with an exact3:1 linear interpolation and bounded
previous-sample history; OpenAL accepts mono float32 or S16. The 16kHz source caps
voice bandwidth at8kHz; this does not promise a48kHz microphone's fidelity. Overflow
drops oldest samples to bound latency/memory. Silence state is checked before and
after every input; any nonzero state or route-count change discards the block and
clears queued/history samples. Negative state/read errors disconnect capture.
No mute, focus or routing setter is called. Hardware/system privacy behavior still
needs independent physical observation.

The profile is initial user, General purpose1, index0,256frames,16000Hz,param1.
This is **PS5-specific declaration evidence, not verified local hardware ABI**:
[AudioIn declarations](https://github.com/boykopovar/AnyPS5/blob/b8f0a6b2025605b78eb70646bda79f458a577c82/core/libs/prx/libSceAudioIn/include/AudioIn.hpp)
and [format/read implementation](https://github.com/boykopovar/AnyPS5/blob/b8f0a6b2025605b78eb70646bda79f458a577c82/core/libs/prx/libSceAudioIn/Export.cpp)
provide the calling signatures/profile. PS4 sources differ in format constants;
no PS4-format fallback or guessed buffer layout is silently attempted. The PS5
3.20 [export reference](https://github.com/DNNDHH/PS5-3.20_Libs/blob/main/libSceAudioIn.c)
confirms the six resident import names/NIDs. Link-time declarations load the real
system library; declaration bodies are **never linked into the application** and
no Sony module is shipped. The optional module dependency itself needs a170console
startup check, even with capture OFF. A cached external microphone-probe report
was found, but its repository now returns404, so its implementation was not used
as verified source. URL hashes and consumer evidence are in the
[investigation pin](../client/ports/voicechat-investigation.json).

The PS5 native adapter, OpenAL backend and launcher settings are consumer code in
ProsperoCraft. Existing Java registry/JNA mechanisms are reused without runtime
changes, arbitrary loading, platform spoofing, game hooks or modified mod JARs.

## Verified consumer path

Publisher Modrinth metadata lists original Fabric **2.6.27+26.3** (`x9jLR94Q`) and
**2.6.27+26.2** (`ul3tRpKz`), published28October2026. Their original JAR SHA512
hashes were checked locally and their `fabric.mod.json` dependencies inspected;
[pins and dependency declarations](../client/ports/voicechat-investigation.json)
record this investigation without shipping or modifying those JARs. No game
support restriction or approved mod list is extended by this metadata.

The upstream26.3 source inspection is pinned to
[`2e56198016e02fd99139d37f382b7155c5bd63f5`](https://github.com/henkelmax/simple-voice-chat/tree/2e56198016e02fd99139d37f382b7155c5bd63f5),
a **2.6.28 development** source snapshot, not an assertion of byte equivalence with
publisher2.6.27. Its `MicrophoneManager` chooses OpenAL unless the platform/config
selects Java sound, and falls back to `JavaxMicrophone` after OpenAL failure.
`ALMicrophone` opens `alcCaptureOpenDevice`, starts/stops capture, checks available
samples, reads them and closes the device. `AudioUtils` specifies **48kHz and960
frames/20ms**; OpenAL capture requests mono float32 (stereo only when configured).
A PS5 S16 hardware source would therefore need a real sample/format conversion
path through OpenAL's capture conversion, with bounded buffering and lifecycle.
The Java sound fallback currently has no PS5 capture provider either.

Upstream uses JNA platform detection, LWJGL OpenAL, native Opus validation through
`opus4j`, optional `rnnoise4j`/`speex4j` and recording through `lame4j`. Its Opus
manager offers a genuine Java Concentus fallback. Existing resident JNA support
and playback do not establish any of these native bindings or their full-game
initialization on PS5. Native Opus/denoiser/recording ports would need their own
source/ABI/license validation if enabled. Controlify's SDL audio endpoint is
explicitly **output-only haptics**, not microphone capture. No JAR hooks, fake
capture, platform spoofing or browser microphone substitution was introduced.

The upstream [client configuration](https://dev.modrepo.de/minecraft/voicechat/wiki/client_config)
documents microphone selection, PTT/VOICE activation and the Java capture option.
A matching server-side voice-chat installation and reachable voice transport are
separate requirements; the local management HTTP server carries no voice data.

## Exact-build acceptance still required

Use original Fabric Simple Voice Chat2.6.27 matching26.3/26.2, with its declared
Fabric dependencies and a compatible voice-chat server. Leave the upstream Java
microphone option OFF to try OpenAL. Upstream native Opus validation may fail on
PS5; the genuine Java Concentus fallback is available in the inspected source,
but its real startup/codec path still needs console validation. Optional native
noise suppression/recording libraries are not ported or claimed. No voice mod is
auto-installed or configured over existing user choices.

After the local test establishes real speech and mute behavior, enable capture
and select the PS5 system microphone in Simple Voice Chat. With a consenting
participant verify PTT and/or voice activation, the participant hearing the PS5
user, PS5 receiving voice playback, muted silence, headset route distinction,
repeated microphone restarts and world/server transitions. Check playback,
controller input, rumble/gyro/triggers and native resource counts during a
recorded-duration endurance session. Do not record/publish anyone's speech.

No physical speech, hardware mute, actual mod codec/capture, remote participant,
route identity, playback/input regression or endurance result is claimed for170.
If the initial profile fails, preserve its code/result and repair against verified
API evidence before changing constants. A successful host mock or open call does
not establish microphone compatibility.

## Local174 follow-up

The173 actual mono capture open fails; its missing stage/code prevents a root-cause
claim.174 retains confirmed process-lifetime AudioIn initialization across probes
and opens, retries genuine failed initialization and reports native failure stage/
code. Native profile constants are unchanged. See [174 evidence and console checks](client-mic-disconnect-174.md).
Speech, mute, route identity and two-way SVC remain pending.

## Local177 service preparation

176 current-run SVC reports AudioIn init0x80260108 before microphone port open.
177 prepares the service before JVM/game pressure, without user lookup, port open
or input read. Capture stays default-off. See [177 evidence/test guide](client-audioin-service-177.md).
The earlier173 nonzero launcher counts remain separate evidence; no177 speech or
whole-build acceptance is implied.
