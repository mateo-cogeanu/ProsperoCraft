#!/usr/bin/env python3
"""Audit runtime-owned native network scratch without copying its implementation."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def audit(runtime):
 pin=json.loads((ROOT/'client/ports/network-scratch-runtime.json').read_text());patch=runtime/'java25/patches'/pin['patch']
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha(patch)==pin['patch_sha256']
 native=runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/native/java.base/libnet'
 symbols=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','--defined-only',str(native/'net_util_md.o')],text=True)
 for name in ['JNU_PS5SetNetworkScratchEnabled','JNU_PS5NetworkScratchEnabled']:assert name in symbols
 for name in ['Inet4AddressImpl.o','Inet6AddressImpl.o','NetworkInterface.o']:
  refs=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm','-u',str(native/name)],text=True)
  assert 'JNU_PS5NetworkScratchEnabled' in refs and 'sceKernelAllocateDirectMemory' in refs,name
 return {'runtime':pin,'libnet_sha256':sha(runtime/'.tools/java25/openjdk/build/ps5-bootstrap/support/modules_libs/java.base/libnet.so'),'objects_sha256':{n:sha(native/n)for n in ['Inet4AddressImpl.o','Inet6AddressImpl.o','NetworkInterface.o','net_util_md.o']},'consumer_policy':'Enabled beforeJVM;libc/anonymous-first,independent64slot/8MiB perInet4/Inet6/NetworkInterfaceCunit,24MiBaggregate;paired release,failed cleanup retains ownership;no heap/GC/auth/DNSanswer changes','console':'Pending DNS/HTTPS/Fabric startup/world/save/endurance'}
