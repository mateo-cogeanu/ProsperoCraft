#!/usr/bin/env python3
"""Build the pinned runtime-owned emutls adapter used by the resident link."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def build(runtime):
 pin=json.loads((ROOT/'client/ports/emutls-runtime.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 for name,digest in pin['source_sha256'].items():assert sha(runtime/name)==digest,name
 sdk=runtime/'.tools/native-sdk/ps5-payload-sdk';obj=runtime/'build/java25/emutls-adapter/backend.o';obj.parent.mkdir(exist_ok=True)
 subprocess.run(['/opt/homebrew/opt/llvm/bin/clang++','-target','x86_64-sie-ps5','-fvisibility-nodllstorageclass=default','-isysroot',str(sdk),'-isystem',str(sdk/'target/include/c++/v1'),'-isystem',str(sdk/'target/include'),'-std=c++20','-O2','-Wall','-Wextra','-Werror','-fno-exceptions','-fno-rtti','-fno-stack-protector','-femulated-tls','-I'+str(runtime/'.tools/java25/openjdk/src/hotspot/share'),'-c',str(runtime/'java25/probe/emutls_alloc.cpp'),'-o',str(obj)],check=True)
 symbols=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm',str(obj)],text=True)
 for name in ['ps5_emutls_enable_direct','ps5_emutls_direct_map','ps5_emutls_direct_unmap']:assert name in symbols,name
 assert '__emutls_get_address' not in symbols and '__cxa_guard' not in symbols
 return {'runtime':pin,'object_sha256':sha(obj),'console':'PendingPS5compilerTLS/nativeabort repair/startup/world/lifecycle/endurance'}
