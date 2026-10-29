/* SPDX-License-Identifier: LGPL-2.0-or-later
 * OpenAL Soft playback backend for PS5's paced AudioOut API.
 * ABI/configuration follows the project's native/menu_audio.hpp baseline.
 * Game audio is rendered by OpenAL itself; no loopback diversion or fake sink.
 */
#include "config.h"
#include "ps5_backend.h"
#include "ps5_port_pool.hpp"
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include "ps5_audio_mutex.hpp"
#include <thread>
#include "althrd_setname.h"
#include "core/device.h"
#include "core/helpers.h"
extern "C" {
int sceAudioOutInit();
int sceAudioOutOpen(int,int,int,unsigned,unsigned,unsigned);
int sceAudioOutOutput(int,const void*);
int sceAudioOutClose(int);
int sceKernelUsleep(unsigned);
extern int client_ps5_audio_early_init_result;
extern int client_ps5_audio_early_port;
}
namespace {
constexpr auto DeviceName="PS5 Speakers";
constexpr unsigned Frames=256,Channels=2,Rate=48000;
void report(const char* stage,int result)
{
    std::fprintf(stderr,"PS5 OpenAL AudioOut %s result=%d\n",stage,result);
    std::fflush(stderr);
}
constexpr std::uint32_t AudioBusy=0x80260002u,AudioAlreadyInit=0x8026000eu,AudioNotInit=0x8026000fu;
struct AudioState {ps5audio::Mutex mutex;bool ready=false;};
AudioState& audioState(){static AudioState state;return state;}
int initialize()
{
    auto& state=audioState();const auto lock=std::lock_guard{state.mutex};
    if(state.ready)return 0;
    const int early=client_ps5_audio_early_init_result;
    if(early>=0 || static_cast<std::uint32_t>(early)==AudioAlreadyInit) {
        report("using successful pre-JVM initialization",early);state.ready=true;return 0;
    }
    const int result=sceAudioOutInit();report("init",result);
    if(result>=0 || static_cast<std::uint32_t>(result)==AudioAlreadyInit)state.ready=true;
    return result;
}
ps5audio::PortPool& ports(){static ps5audio::PortPool pool;return pool;}
void confirmedOpen()
{
    auto& state=audioState();const auto lock=std::lock_guard{state.mutex};state.ready=true;
}
struct Ps5Backend final : BackendBase {
    explicit Ps5Backend(gsl::not_null<DeviceBase*> device) noexcept : BackendBase{device}{}
    ~Ps5Backend() override {stop();close();}
    int port=-1;bool healthy=true;
    std::atomic<bool> kill{true};
    std::thread thread;
    alignas(64) std::array<std::int16_t,Frames*Channels> pcm{};
    void close() noexcept {
        if(port<0)return;
        const int handle=port;port=-1;
        const int drained=sceAudioOutOutput(handle,nullptr);report("drain",drained);
        if(healthy&&drained>=0&&ports().keep(handle))report("retain silent port for reload",handle);
        else report("close",sceAudioOutClose(handle));
    }
    void open(std::string_view name) override {
        if(!name.empty() && name!=DeviceName)
            throw al::backend_exception{al::backend_error::NoDevice,"Unknown PS5 audio device {}",name};
        {auto& state=audioState();const auto lock=std::lock_guard{state.mutex};
         if(client_ps5_audio_early_port>=0){port=client_ps5_audio_early_port;client_ps5_audio_early_port=-1;state.ready=true;report("adopt pre-JVM port",port);}
        }
        if(port<0){port=ports().take();if(port>=0)report("reuse retained port",port);}
        if(port>=0){mDeviceName=DeviceName;return;}
        // A busy init is not success. Probe the real port: it must actually open.
        // Retry only explicit busy/not-initialized recovery, at most450ms total.
        for(unsigned attempt=0;attempt<10;++attempt) {
            const int init=initialize();const auto code=static_cast<std::uint32_t>(init);
            if(init<0 && code!=AudioBusy && code!=AudioAlreadyInit)
                throw al::backend_exception{al::backend_error::DeviceError,"PS5 AudioOut initialization failed: {}",init};
            if(code==AudioBusy)report("init busy; real port probe",init);
            // SYSTEM user,MAIN output,256frames/48kHz/stereoS16.
            port=sceAudioOutOpen(0xff,0,0,Frames,Rate,1);report("open",port);
            if(port>=0) {
                confirmedOpen();
                if(code==AudioBusy)report("busy recovery confirmed by actual port",port);
                break;
            }
            const auto error=static_cast<std::uint32_t>(port);
            if(code!=AudioBusy || (error!=AudioBusy && error!=AudioNotInit) || attempt==9)
                throw al::backend_exception{al::backend_error::DeviceError,"PS5 AudioOut open failed: {}",port};
            report("busy recovery retry",attempt+1);
            const int wait=sceKernelUsleep(50000);
            if(wait<0)throw al::backend_exception{al::backend_error::DeviceError,"PS5 AudioOut retry wait failed: {}",wait};
        }
        mDeviceName=DeviceName;
    }
    auto reset() -> bool override {
        mDevice->FmtChans=DevFmtStereo;mDevice->FmtType=DevFmtShort;
        mDevice->mSampleRate=Rate;mDevice->mUpdateSize=Frames;mDevice->mBufferSize=Frames*2;
        mDevice->mAmbiOrder=0;setDefaultWFXChannelOrder();
        return port>=0;
    }
    void mix() noexcept {
        althrd_setname(GetMixerThreadName());
        unsigned blocks=0;
        try {
            while(!kill.load(std::memory_order_acquire) && mDevice->Connected.load(std::memory_order_acquire)) {
                mDevice->renderSamples(pcm.data(),Frames,Channels);
                // AudioOut consumes/blocks on this buffer; keep storage alive until stop joins.
                const int result=sceAudioOutOutput(port,pcm.data());
                if(result<0) {
                    healthy=false;report("output failure",result);
                    mDevice->handleDisconnect("PS5 AudioOut failed: {}",result);break;
                }
                if(++blocks==1)report("first PCM block submitted",result);
            }
        } catch(const std::exception& error) {
            healthy=false;std::fprintf(stderr,"PS5 OpenAL mixer exception: %s\n",error.what());std::fflush(stderr);
            mDevice->handleDisconnect("PS5 mixer exception");
        } catch(...) {
            healthy=false;report("unknown mixer exception",-1);mDevice->handleDisconnect("PS5 mixer exception");
        }
        kill.store(true,std::memory_order_release);
    }
    void start() override {
        if(port<0)throw al::backend_exception{al::backend_error::DeviceError,"PS5 audio port closed"};
        if(thread.joinable())stop();
        kill.store(false,std::memory_order_release);
        try {thread=std::thread{&Ps5Backend::mix,this};}
        catch(const std::exception& error) {
            kill.store(true,std::memory_order_release);
            throw al::backend_exception{al::backend_error::DeviceError,"PS5 mixer thread failed: {}",error.what()};
        }
    }
    void stop() override {
        kill.store(true,std::memory_order_release);
        if(thread.joinable())thread.join();
    }
};
}
auto Ps5BackendFactory::init() -> bool {return true;}
auto Ps5BackendFactory::querySupport(BackendType type) -> bool {return type==BackendType::Playback;}
auto Ps5BackendFactory::enumerate(BackendType type) -> std::vector<std::string> {
    if(type==BackendType::Playback)return {DeviceName};
    return {};
}
auto Ps5BackendFactory::createBackend(gsl::not_null<DeviceBase*> device,BackendType type) -> BackendPtr {
    if(type==BackendType::Playback)return BackendPtr{new Ps5Backend{device}};
    return nullptr;
}
auto Ps5BackendFactory::getFactory() -> BackendFactory& {static Ps5BackendFactory factory;return factory;}
