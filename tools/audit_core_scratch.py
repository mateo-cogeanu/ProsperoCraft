#!/usr/bin/env python3
"""Audit the runtime-owned127temporary buffer integration; no duplicated runtime source."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
def audit(runtime):
 pin=json.loads((ROOT/'client/ports/core-scratch-runtime.json').read_text());patch=runtime/'java25/patches'/pin['patch'];assert hashlib.sha256(patch.read_bytes()).hexdigest()==pin['patch_sha256']
 native=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libjava';library=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libjava.so';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(native/'jni_util.o')],text=True);assert 'JNU_PS5SetDirectScratchEnabled' in names and 'JNU_PS5DirectScratchEnabled' in names
 return {'runtime':pin,'objects_sha256':{name:sha(native/name)for name in ['jni_util.o','ClassLoader.o']},'libjava_sha256':sha(library),'consumer_policy':'Explicitly enabled beforeJVM;normal allocators first;only platform-string/ClassLoader temporary buffers;64slots/8MiBperCunit,16MiBaggregate;Javaheap/GCunchanged','console':'PendingFabric26.2startup/world/nativecleanup,endurance'}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args();print(json.dumps(audit(a.runtime_workspace),indent=2))
