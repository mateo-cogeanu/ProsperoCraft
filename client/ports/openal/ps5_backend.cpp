/* SPDX-License-Identifier: LGPL-2.0-or-later
 * OpenAL Soft playback backend for PS5's paced AudioOut API.
 * ABI/configuration follows the project's native/menu_audio.hpp baseline.
 * Game audio is rendered by OpenAL itself; no loopback diversion or fake sink.
 */
#include "config.h"
#include "ps5_backend.h"
#include "ps5_port_pool.hpp"
#include "ps5_capture.hpp"
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include "ps5_audio_mutex.hpp"
#include "ps5_mixer_workers.hpp"
#include "althrd_setname.h"
#include "core/device.h"
#include "core/helpers.h"
extern "C" {
int sceUserServiceGetInitialUser(int*);
int sceAudioInInit();int sceAudioInOpen(int,unsigned,unsigned,unsigned,unsigned,unsigned);
int sceAudioInInput(int,void*);int sceAudioInClose(int);int sceAudioInGetSilentState(int);int sceAudioInGetRerouteCount(int);
int sceAudioOutInit();
int sceAudioOutOpen(int,int,int,unsigned,unsigned,unsigned);
int sceAudioOutOutput(int,const void*);
int sceAudioOutClose(int);
int sceKernelUsleep(unsigned);
extern int client_ps5_audio_early_init_result;
extern int client_ps5_audio_early_port;
extern int client_ps5_audio_secondary_port;
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
ps5audio::MixerWorkers mixerWorkers;
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
    ps5audio::MixerWorkers::Slot* worker=nullptr;
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
         else if(client_ps5_audio_secondary_port>=0){port=client_ps5_audio_secondary_port;client_ps5_audio_secondary_port=-1;state.ready=true;report("adopt pre-JVM secondary port",port);}
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
        if(worker)stop();
        kill.store(false,std::memory_order_release);
        worker=mixerWorkers.assign([](void* context){static_cast<Ps5Backend*>(context)->mix();},this);
        if(!worker) {
            kill.store(true,std::memory_order_release);
            throw al::backend_exception{al::backend_error::DeviceError,"PS5 reserved mixer worker unavailable"};
        }
    }
    void stop() override {
        kill.store(true,std::memory_order_release);
        mixerWorkers.wait_release(worker);worker=nullptr;
    }
};
}
namespace {
constexpr auto CaptureName="PS5 system microphone (select DualSense in PS5 settings)";
std::atomic<bool> captureEnabled{false},captureLeased{false};
ps5audio::Capture capture;
// Both core and producer state outlive every logical OpenAL device. A failed
// join pins this state/port; it must not retain the destroyed backend or device.
ps5audio::CaptureWorkerLifetime captureWorkerLifetime;
std::atomic<bool> captureWorkerPinned{false};
ps5audio::CaptureApi captureApi(){return {sceUserServiceGetInitialUser,sceAudioInInit,sceAudioInOpen,sceAudioInInput,sceAudioInGetSilentState,sceAudioInGetRerouteCount,sceAudioInClose};}
struct CaptureLease {
 bool owned=false;
 bool acquire(){bool expected=false;owned=captureLeased.compare_exchange_strong(expected,true,std::memory_order_acq_rel);return owned;}
 void release(){if(owned&&capture.close()){captureLeased.store(false,std::memory_order_release);owned=false;}}
 ~CaptureLease(){release();} // Failed close pins ownership; do not orphan a live port.
};
struct Ps5Capture final : BackendBase {
 explicit Ps5Capture(gsl::not_null<DeviceBase*> device) noexcept:BackendBase{device}{}
 CaptureLease lease;pthread_t thread{};ps5audio::WorkerOwnership worker;
 // Unjoined producer may still use the port: keep the lease pinned, never close.
 // Dropping only this object's claim leaves the global lease held (pinned).
 ~Ps5Capture() override {if(stopWorker())lease.release();else lease.owned=false;}
 void open(std::string_view name) override {
  if(!captureEnabled.load(std::memory_order_acquire)||(!name.empty()&&name!=CaptureName))throw al::backend_exception{al::backend_error::NoDevice,"PS5 microphone capture disabled or unavailable"};
  if(mDevice->mSampleRate!=48000||mDevice->FmtChans!=DevFmtMono||(mDevice->FmtType!=DevFmtFloat&&mDevice->FmtType!=DevFmtShort))throw al::backend_exception{al::backend_error::DeviceError,"PS5 capture requires 48kHz mono float32 or S16"};
  if(!lease.acquire())throw al::backend_exception{al::backend_error::DeviceError,"PS5 microphone is in use or cleanup is pending"};
  if(!capture.open(captureApi())){std::fprintf(stderr,"PS5 AudioIn stage=%s result=0x%x\n",capture.errorStage,unsigned(capture.error));std::fflush(stderr);lease.release();throw al::backend_exception{al::backend_error::NoDevice,"PS5 microphone {} failed: 0x{:x}",capture.errorStage,unsigned(capture.error)};}
  mDeviceName=CaptureName;mDevice->mBufferSize=ps5audio::Capture::Capacity;
 }
 static void disconnect(void* device,const char* message){static_cast<DeviceBase*>(device)->handleDisconnect("{}",message);}
 static void* run(void*) noexcept {
  while(!captureWorkerLifetime.kill.load(std::memory_order_acquire)){
   if(!captureEnabled.load(std::memory_order_acquire)){capture.clear();std::fprintf(stderr,"PS5 AudioIn stage=disabled-during-capture\n");std::fflush(stderr);captureWorkerLifetime.disconnect("PS5 microphone capture disabled");break;}
   if(!capture.pump()){std::fprintf(stderr,"PS5 AudioIn stage=%s result=0x%x\n",capture.errorStage,unsigned(capture.error));std::fflush(stderr);captureWorkerLifetime.disconnect("PS5 microphone capture failed");break;}
  }
  return nullptr;
 }
 void start() override {
  if(worker.started)return;if(worker.uncertain||!lease.owned||!captureEnabled.load(std::memory_order_acquire))throw al::backend_exception{al::backend_error::DeviceError,"PS5 microphone disabled"};
  capture.clear();captureWorkerLifetime.attach(mDevice.get(),disconnect);pthread_attr_t attr;int rc=pthread_attr_init(&attr);
  if(!rc){rc=pthread_attr_setstacksize(&attr,128*1024);if(!rc)rc=pthread_create(&thread,&attr,run,nullptr);pthread_attr_destroy(&attr);}
  if(rc){captureWorkerLifetime.detach();std::fprintf(stderr,"PS5 AudioIn stage=worker-create result=0x%x\n",unsigned(rc));std::fflush(stderr);throw al::backend_exception{al::backend_error::DeviceError,"PS5 microphone worker unavailable"};}worker.started=true;
 }
 bool stopWorker(){
  if(!lease.owned)return true; // A refused competing open must not stop the owner.
  captureWorkerLifetime.kill.store(true,std::memory_order_release);const bool was_uncertain=worker.uncertain;
  if(!worker.stop([this]{return pthread_join(thread,nullptr);})){captureWorkerPinned.store(true,std::memory_order_release);captureWorkerLifetime.detach();if(!was_uncertain){std::fprintf(stderr,"PS5 AudioIn stage=worker-join result=0x%x; microphone pinned until restart\n",unsigned(worker.join_error));std::fflush(stderr);}return false;}
  captureWorkerLifetime.detach();capture.clear();return true;
 }
 void stop() override {stopWorker();}
 auto availableSamples()->std::size_t override{return captureWorkerPinned.load(std::memory_order_acquire)?0:capture.available();}
 void captureSamples(std::span<std::byte> out) override {
  if(captureWorkerPinned.load(std::memory_order_acquire))throw al::backend_exception{al::backend_error::DeviceError,"PS5 microphone worker cleanup uncertain"};
  unsigned frame=mDevice->FmtType==DevFmtFloat?sizeof(float):sizeof(std::int16_t);
  if(out.size()%frame||!capture.take(out.data(),unsigned(out.size()/frame),mDevice->FmtType==DevFmtFloat))throw al::backend_exception{al::backend_error::DeviceError,"Not enough PS5 microphone samples"};
 }
};
}
extern "C" __attribute__((visibility("default"))) int client_ps5_capture_service_preinit(){
 const bool ready=capture.initialize(captureApi());const int rc=ready?0:capture.error;
 std::fprintf(stderr,"PS5 AudioIn pre-JVM service init result=0x%x; no port opened or input read\n",unsigned(rc));std::fflush(stderr);return rc;
}
extern "C" __attribute__((visibility("default"))) void client_ps5_capture_enable(int enabled){captureEnabled.store(enabled!=0,std::memory_order_release);}
extern "C" __attribute__((visibility("default"))) void client_ps5_capture_probe(char* result,unsigned size){
 if(!result||!size)return;CaptureLease lease;
 if(!lease.acquire()){std::snprintf(result,size,"Microphone busy or previous cleanup failed. Restart the app.");return;}
 if(!capture.open(captureApi())){std::snprintf(result,size,"AudioIn %s failed (0x%x). Select your microphone in PS5 settings; capture remains unvalidated.",capture.errorStage,unsigned(capture.error));return;}
 bool good=true;for(unsigned n=0;n<313;n++)if(!capture.pump()){good=false;break;}
 std::snprintf(result,size,"%s: blocks=%llu nonzero=%llu peak=%d silent-blocks=%llu. System-selected route; DualSense identity and mute need console confirmation. No recording saved.",good?"Input reads completed":"Capture failed",(unsigned long long)capture.blocks,(unsigned long long)capture.nonzero,capture.peak,(unsigned long long)capture.silent_blocks);
 if(!capture.close())std::snprintf(result,size,"Microphone close failed (0x%x). Ownership retained; restart the app.",unsigned(capture.error));
}

extern "C" __attribute__((visibility("default"))) int client_ps5_audio_worker_preinit() {return mixerWorkers.preinit();}
auto Ps5BackendFactory::init() -> bool {return true;}
auto Ps5BackendFactory::querySupport(BackendType type) -> bool {return type==BackendType::Playback||type==BackendType::Capture;}
auto Ps5BackendFactory::enumerate(BackendType type) -> std::vector<std::string> {
    if(type==BackendType::Playback)return {DeviceName};
    if(type==BackendType::Capture&&captureEnabled.load(std::memory_order_acquire)){
        CaptureLease probe;if(probe.acquire()){
            if(capture.open(captureApi())&&capture.pump()){probe.release();if(!probe.owned)return {CaptureName};}
            std::fprintf(stderr,"PS5 AudioIn enumeration stage=%s result=0x%x\n",capture.errorStage,unsigned(capture.error));std::fflush(stderr);
        }
        // A live healthy owner proves the device; listing it must not disturb that capture.
        else if(!captureWorkerPinned.load(std::memory_order_acquire)&&capture.active())return {CaptureName};
        else {std::fprintf(stderr,"PS5 AudioIn enumeration stage=lease-unavailable\n");std::fflush(stderr);}
    }
    return {};
}
auto Ps5BackendFactory::createBackend(gsl::not_null<DeviceBase*> device,BackendType type) -> BackendPtr {
    if(type==BackendType::Playback)return BackendPtr{new Ps5Backend{device}};
    if(type==BackendType::Capture)return BackendPtr{new Ps5Capture{device}};
    return nullptr;
}
auto Ps5BackendFactory::getFactory() -> BackendFactory& {static Ps5BackendFactory factory;return factory;}
