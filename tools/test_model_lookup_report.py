#!/usr/bin/env python3
"""Exercise the actual launcher snapshot, shared display labels and short report."""
from pathlib import Path
import argparse,subprocess,tempfile
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args()
s=(r/'client/startup/bootstrap.cpp').read_text();start=s.index(' char model_status[320];');end=s.index('\n\n sceUserServiceInitialize',start);actual=s[start:end]
code=r'''
#include <cassert>
#include <cstdio>
#include <cstring>
#include "client/launcher/hardware_identity.hpp"
#include "client/ports/oshi/hardware_labels.hpp"
#define PROSPERO_APP_VERSION "01.000.158"
static char captured[512];static unsigned calls=0;static unsigned long long answer=0x840fd0;
extern "C" unsigned long long sceKernelGetMainSocId(){calls++;return answer;}
namespace ps5::log_share {static void write_note(const char*,const char* p){assert(std::strlen(p)<sizeof(captured));std::strcpy(captured,p);}}
int main(){
 prospero_menu::hardware::initialize();answer=0;prospero_menu::hardware::initialize();assert(calls==1);
 assert(prospero_menu::hardware::identity().model==ps5::console::Model::pro);
 assert(!std::strcmp(prospero_hardware::cpu(prospero_menu::hardware::identity().model),"AMD Zen 2, 8C16T (PS5 Pro)"));
 assert(!std::strcmp(prospero_hardware::gpu(prospero_menu::hardware::identity().model),"AMD RDNA 2.x, 60 CUs (PS5 Pro)"));
'''+actual+r'''
 assert(std::strstr(captured,"source=launcher_soc soc_id=0x840fd0"));assert(std::strlen(captured)<320);
 prospero_menu::hardware::Identity base;answer=0x840f00;base.initialize(sceKernelGetMainSocId);assert(base.value().model==ps5::console::Model::standard);
 assert(!std::strcmp(prospero_hardware::gpu(base.value().model),"AMD RDNA 2, 36 CUs (PS5)"));
 prospero_menu::hardware::Identity error;answer=0x80020003;error.initialize(sceKernelGetMainSocId);assert(error.value().model==ps5::console::Model::unknown);
 puts("PASS actual launcher snapshot:query once,cached Pro/base/error models,unchanged labels,real report fits512-byte writer");
}
'''
with tempfile.TemporaryDirectory(prefix='model-launcher-')as t:
 w=Path(t);(w/'check.cpp').write_text(code)
 subprocess.run(['clang++','-std=c++20','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(r),'-I'+str(a.runtime_workspace/'java25/platform'),str(w/'check.cpp'),'-o',str(w/'check')],check=True)
 subprocess.run([str(w/'check')],check=True)
