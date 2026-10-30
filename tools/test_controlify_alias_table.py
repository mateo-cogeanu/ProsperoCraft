#!/usr/bin/env python3
"""Read linked ELF registry tables: only SDL3's three event lookups differ."""
from pathlib import Path
import argparse,re,struct,subprocess
r=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-workspace',type=Path,required=True);a=p.parse_args()
elf=r/'build/client-startup-probe/bootstrap-01.000.164-symbols.elf';data=elf.read_bytes()
nm=subprocess.check_output(['/opt/homebrew/opt/llvm/bin/llvm-nm',str(elf)],text=True)
symbols={f[2]:int(f[0],16)for l in nm.splitlines()if len(f:=l.split())==3}
source=(a.runtime_workspace/'build/java25/builtin-libraries.cpp').read_text()
alias=re.search(r'\{"libSDL3.so", (symbols_alias_\d+),',source)[1]
def rows(name):return re.findall(r'\{"([A-Za-z_][A-Za-z0-9_]*)",',re.search(r'static const Symbol '+name+r'\[\]=\{(.*?)\n\};',source,re.S)[1])
phoff=struct.unpack_from('<Q',data,32)[0];size,num=struct.unpack_from('<HH',data,54)
segments=[struct.unpack_from('<IIQQQQQQ',data,phoff+i*size)for i in range(num)]
def read(address,n):
 for typ,flags,off,va,pa,filesz,memsz,align in segments:
  if typ==1 and va<=address and address+n<=va+filesz:return data[off+address-va:off+address-va+n]
 raise AssertionError('Address outside file-backed LOAD')
# PIE pointer initializers are carried by R_X86_64_RELATIVE addends.
shoff=struct.unpack_from('<Q',data,40)[0];shsize,shnum=struct.unpack_from('<HH',data,58)
relocations={}
for i in range(shnum):
 sh=struct.unpack_from('<IIQQQQIIQQ',data,shoff+i*shsize)
 if sh[1]==4:
  for off in range(sh[4],sh[4]+sh[5],sh[9]):
   address,info,addend=struct.unpack_from('<QQq',data,off)
   if info&0xffffffff==8:relocations[address]=addend
def pointer(address):return relocations.get(address,struct.unpack('<Q',read(address,8))[0])
def table(name):
 addr=next(v for k,v in symbols.items()if k.startswith('_ZL')and k.endswith(name));out={}
 for i,expected in enumerate(rows(name)):
  key,value=pointer(addr+i*16),pointer(addr+i*16+8);text=bytearray()
  while (b:=read(key+len(text),1))!=b'\0':text+=b
  assert text.decode()==expected
  out[expected]=value
 return out
base=table('symbols_ps5sdl');scoped=table(alias)
assert base.keys()==scoped.keys()
expected={f'SDL_{n}':f'prospero_controlify_{n}'for n in ['SetEventFilter','GetEventFilter','PollEvent']}
different={n for n in base if base[n]!=scoped[n]}
assert different==set(expected),(different,expected)
for name,replacement in expected.items():
 assert base[name]==symbols[name]
 assert scoped[name]==symbols[replacement]
print('PASS actual linked164 ELF:baseps5sdl+SDL3alias same',len(base),'exports;exactly3alias event pointers redirected to realfacade;allother/basepointersunchanged')
