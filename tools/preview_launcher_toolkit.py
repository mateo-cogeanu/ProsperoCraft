#!/usr/bin/env python3
"""Exercise actual Vulkan draw + native mailbox/VideoOut fixtures on lavapipe.

Run preview_launcher.py first to generate the shared controller/JNI fixture.
The VideoOut functions are host doubles; the kit, driver, shaders, queue,
render pass, uploads, synchronization and readback are real Vulkan.
"""
import argparse, os, subprocess
from pathlib import Path
from build_launcher_toolkit import ROOT, KIT, LLVM, build

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--runtime-workspace',required=True,type=Path)
p.add_argument('--motion',action='store_true')
a=p.parse_args()
work=ROOT/'build/launcher-toolkit-preview';work.mkdir(parents=True,exist_ok=True)
objects=build(work)
runtime=a.runtime_workspace.resolve()
# The host is ARM64. Only the VideoOut fixture's x86 streaming copy is
# replaced with memcpy; the target continues to compile the original SSE path.
cpu=(runtime/'native/renderer/demo_renderer.cpp').read_text().replace('#include <emmintrin.h>','')
start=cpu.index('    auto *out = static_cast<__m128i *>')
end=cpu.index('    _mm_sfence();',start)+len('    _mm_sfence();')
cpu=cpu[:start]+'    std::memcpy(destination,source,frame_bytes);'+cpu[end:]
(work/'videoout_host.cpp').write_text(cpu)
source=(ROOT/'build/launcher-preview/preview.cpp').read_text()
source=source.replace(str(runtime/'native/renderer/demo_renderer.cpp'),str(work/'videoout_host.cpp'))
source=source.replace('#include "'+str(ROOT/'client/launcher/native_menu.hpp')+'"', '#define PROSPERO_TOOLKIT 1\n#define PROSPERO_TOOLKIT_FONT_DIR "'+str(KIT/'assets/fonts')+'"\n#include "'+str(ROOT/'client/launcher/native_menu.hpp')+'"\nnamespace prospero_menu {void initialize_toolkit_graphics(){}}')
source=source.replace('output=std::string(argv[1])+"/"+scene+".ppm";prospero_menu::focus={};', 'output=std::string(argv[1])+"/"+scene+".ppm";prospero_menu::focus={};for(int settle=0;settle<60;settle++){prospero_ui::surface->list.clear();prospero_ui::Canvas canvas;prospero_menu::compose(canvas);}')
source=source.replace('snprintf(prospero_menu::fields[at+3].data(),512,"READY");', 'snprintf(prospero_menu::fields[at+3].data(),512,"%s",i==4?"COMING SOON":"READY");')
source=source.replace('snprintf(prospero_menu::fields[13].data(),512,"6");', 'snprintf(prospero_menu::fields[13].data(),512,"6");snprintf(prospero_menu::fields[30].data(),512,"OFF");snprintf(prospero_menu::fields[73].data(),512,"TEMP GAMETEST");')
source=source.replace('int main', 'static void settle_preview(){for(int i=0;i<90;i++){prospero_ui::dt=1.0f/30;prospero_ui::surface->list.clear();prospero_ui::Canvas c;prospero_menu::compose(c);}}\nint main',1)
source=source.replace('prospero_menu::focus={};assert(ps5::demo::run_ui_until', 'prospero_menu::focus={};settle_preview();assert(ps5::demo::run_ui_until')
source=source.replace('int main(int argc,char**argv){assert(argc==2);','int main(int argc,char**argv){assert(argc==2);assert(prospero_ui::open(PROSPERO_TOOLKIT_FONT_DIR));')
if a.motion:
    motion=r'''
  auto set_field=[](int at,const char* value){snprintf(prospero_menu::fields[at].data(),512,"%s",value);};
  set_field(16,"Vanilla 26.3");set_field(17,"26.3");set_field(65,"26.3 native SDL gameplay");set_field(7,"L1 / R1  Top bar     D-PAD  Navigate     X  Select     CIRCLE  Library");
  set_field(13,"6");set_field(14,"0");set_field(69,"SUPPORTED");set_field(6,"PLAY DEMO");set_field(30,"OFF");set_field(73,"DEMO BRANCH");set_field(28,"CONTENT");set_field(15,"0");
  // Force a real entrance, then replay native focus/page/background changes.
  prospero_ui::effects->page=-1;
  for(int frame=0;frame<180;frame++){
   set_field(11,frame<60?"0":frame<100?"4":frame<140?"2":frame<160?"9":"0");
   set_field(75,frame<100?"2":frame<120?"5":"6");set_field(76,frame<100?"Aurora":frame<120?"Waves":"Bokeh");
   char index[8];snprintf(index,sizeof(index),"%d",frame<60?frame/20:0);set_field(9,index);
   set_field(64,frame>=60&&frame<100?"BUSY":"IDLE");char progress[16];snprintf(progress,sizeof(progress),"%d",std::clamp((frame-60)*25,0,1000));set_field(20,progress);set_field(2,frame>=60&&frame<100?"Downloading verified publisher files...":"");
   prospero_ui::dt=1.0f/24;prospero_ui::surface->list.clear();prospero_ui::Canvas canvas;prospero_menu::compose(canvas);assert(prospero_ui::surface->render());
   auto* px=static_cast<const unsigned char*>(prospero_ui::surface->pixels);char name[64];snprintf(name,sizeof(name),"/motion-%03d.ppm",frame);
   std::ofstream f(std::string(argv[1])+name,std::ios::binary);f<<"P6\n1920 1080\n255\n";
   for(int pixel=0;pixel<1920*1080;pixel++)f.write(reinterpret_cast<const char*>(px+pixel*4),3);
  }
  set_field(11,"5");set_field(15,"2");settle_preview();
  set_field(15,"7");prospero_ui::surface->list.clear();{prospero_ui::Canvas c;prospero_menu::compose(c);}
  assert(prospero_menu::focus.x>760&&prospero_menu::focus.x<1320);
  settle_preview();assert(std::abs(prospero_menu::focus.x-1320)<1);
  prospero_menu::pressed_at=prospero_menu::now_ms();prospero_ui::surface->list.clear();{prospero_ui::Canvas c;prospero_menu::compose(c);}
  assert((*prospero_ui::buttons)[5].press.value>0);assert(prospero_ui::surface->render());
  settle_preview();assert((*prospero_ui::buttons)[5].press.value<0.001f);
  set_field(30,"ON");set_field(15,"2");prospero_ui::surface->list.clear();{prospero_ui::Canvas c;prospero_menu::compose(c);}
  assert(prospero_menu::focus.x==760&&(*prospero_ui::buttons)[2].focus.value==1&&(*prospero_ui::buttons)[5].press.value==0);
  puts("PASS instance 2x2 focus travels and settles, action press animates and settles, Reduced Motion snaps immediately");
  set_field(11,"0");set_field(9,"0");set_field(30,"ON");set_field(75,"2");settle_preview();
  assert(prospero_ui::surface->render());std::vector<unsigned char> frozen(1920*1080*4);memcpy(frozen.data(),prospero_ui::surface->pixels,frozen.size());
  for(int frame=0;frame<4;frame++){prospero_ui::surface->list.clear();prospero_ui::Canvas canvas;prospero_menu::compose(canvas);assert(prospero_ui::surface->render());assert(memcmp(frozen.data(),prospero_ui::surface->pixels,frozen.size())==0);}
  puts("PASS actual rendered Reduced Motion frames remain pixel-identical; native180frame motion tour captured through Vulkan");
  set_field(30,"OFF");
  const char* backgrounds[]={"Gradient","Aurora","Grid","Stars","Waves","Bokeh","Phosphor","Paper","Dots","Vista"};
  for(int mode=1;mode<=10;mode++){
   char value[8];snprintf(value,sizeof(value),"%d",mode);set_field(75,value);set_field(76,backgrounds[mode-1]);settle_preview();
   assert(int(prospero_ui::surface->backdrop.mode)==mode);assert(prospero_ui::surface->render());
   auto* px=static_cast<const unsigned char*>(prospero_ui::surface->pixels);std::ofstream f(std::string(argv[1])+"/background-"+backgrounds[mode-1]+".ppm",std::ios::binary);f<<"P6\n1920 1080\n255\n";
   for(int pixel=0;pixel<1920*1080;pixel++)f.write(reinterpret_cast<const char*>(px+pixel*4),3);
  }
  puts("PASS all10actual toolkit backdrop modes rendered with glass on the real single-slot Vulkan surface");

  set_field(30,"OFF");
'''
    source=source.replace(' for(failure=1;failure<=3;failure++)',motion+'\n for(failure=1;failure<=3;failure++)')
# Render each actual color palette through the production Settings paint path.
theme_preview=r'''
  snprintf(prospero_menu::fields[11].data(),512,"2");snprintf(prospero_menu::fields[15].data(),512,"6");snprintf(prospero_menu::fields[30].data(),512,"ON");
  for(int theme=0;theme<6;theme++){
   snprintf(prospero_menu::fields[104].data(),512,"%d",theme);settle_preview();assert(prospero_ui::surface->render());
   for(int bar=0;bar<7;bar++){const auto& b=(*prospero_ui::buttons)[bar];assert(b.w==1080&&b.h==86&&b.x==760&&b.y==300+96*bar);}
   auto* px=static_cast<const unsigned char*>(prospero_ui::surface->pixels);std::ofstream f(std::string(argv[1])+"/theme-"+std::to_string(theme)+".ppm",std::ios::binary);f<<"P6\n1920 1080\n255\n";
   for(int pixel=0;pixel<1920*1080;pixel++)f.write(reinterpret_cast<const char*>(px+pixel*4),3);
  }
  puts("PASS all six palettes rendered through actual Vulkan Settings controls and backdrop");
  snprintf(prospero_menu::fields[104].data(),512,"0");
'''
source=source.replace(' for(failure=1;failure<=3;failure++)',theme_preview+'\n for(failure=1;failure<=3;failure++)')
source=source.replace('static void animation_check(ps5::demo::Canvas& c) noexcept {','static void animation_check(ps5::demo::Canvas&) noexcept {prospero_ui::Canvas c;')
# The legacy discrete interpolation assertion has its own fixture. Here dt
# and the toolkit spring are exercised by the rendered controller transitions.
source=source.replace(' assert(ps5::demo::run_ui_until(animation_check,update,stop,""));','')
(work/'preview.cpp').write_text(source)
jdk=Path('/Library/Java/JavaVirtualMachines/openjdk-25.jdk/Contents/Home')
runtime=a.runtime_workspace.resolve()
subprocess.run([str(LLVM/'clang++'),'-std=c++20','-O1','-Wno-unused-function','-I'+str(KIT/'src'),'-I'+str(work),'-I'+str(ROOT/'.tools/PS5_Mesa/include'),'-I'+str(runtime/'native/renderer'),'-I'+str(runtime/'build/native'),'-I'+str(runtime/'src'),'-I'+str(jdk/'include'),'-I'+str(jdk/'include/darwin'),str(work/'preview.cpp'),*map(str,objects),'/opt/homebrew/lib/libvulkan_lvp.dylib','-o',str(work/'preview')],check=True)
subprocess.run([str(work/'preview'),str(work)],check=True,timeout=180)
from PIL import Image
for path in work.glob('*.ppm'):
    if path.name.startswith('motion-'):continue
    with Image.open(path) as picture: picture.save(path.with_suffix('.png'))
print(work/'home.png')

if a.motion:
    frames=[]
    for path in sorted(work.glob('motion-*.ppm')):
        with Image.open(path) as picture:frames.append(picture.resize((960,540)).copy())
    frames[0].save(work/'motion.webp',save_all=True,append_images=frames[1:],duration=42,loop=0,quality=78,method=4)
    print(work/'motion.webp')
