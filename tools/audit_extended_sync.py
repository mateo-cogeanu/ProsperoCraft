#!/usr/bin/env python3
"""Audit pinned reusable HotSpot extended reserve and matching target artifacts."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
def audit(runtime):
 pin=json.loads((ROOT/'client/ports/extended-sync-runtime.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert pin['commit']!='PENDING_RUNTIME_SOURCE_PUBLICATION'
 patch=runtime/'java25/patches'/pin['patch'];assert sha(patch)==pin['patch_sha256']
 obj=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/hotspot/variant-server/libjvm/objs/os_posix.o'
 names=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(obj)],text=True)
 assert 'JVM_PS5SetExtendedSyncReserveEnabled' in names
 lib=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/server/libjvm.so'
 return {'runtime':pin,'os_posix_object_sha256':sha(obj),'libjvm_sha256':sha(lib),'consumer_policy':'BeforeJVM requests8192mutex/8192relative/2048absolute,checks setter result;actual native initialized counts remain authoritative;no heap/GC change','console':'Pending actual prime capacity/late FFM class creation/Fabric startup/world/regression'}
