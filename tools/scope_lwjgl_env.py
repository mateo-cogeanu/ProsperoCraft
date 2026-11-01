"""Candidate-only allocator import scoping for genuine LWJGL JNI env/TLS units."""
import hashlib,struct,subprocess
from pathlib import Path

UNITS=('common_tools.c.o','org_lwjgl_system_ThreadLocalUtil.c.o')
FAMILY=('malloc','calloc','realloc','free','posix_memalign','aligned_alloc')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def code_sections(path):
 data=Path(path).read_bytes();assert data[:6]==b'\x7fELF\x02\x01','ELF64 little-endian object required'
 offset=struct.unpack_from('<Q',data,40)[0];size,count,strings=struct.unpack_from('<HHH',data,58)
 sections=[struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size)for i in range(count)];table=sections[strings];names=data[table[4]:table[4]+table[5]]
 return {names[s[0]:].split(b'\0',1)[0].decode():data[s[4]:s[4]+s[5]]for s in sections if s[2]&4 and s[5]}
def undefined(nm,path):
 text=subprocess.check_output([str(nm),'-u',str(path)],text=True)
 return {line.split()[-1]for line in text.splitlines()if line.split()}
def scope(group,bindings,output,llvm):
 if group['name']!='lwjgl':raise ValueError('Only known LWJGL group may be scoped')
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 if not all(name in bindings and bindings[name].startswith('clientgpu_')for name in FAMILY):raise ValueError('Complete known graphics allocator family required')
 mapping={name:bindings[name]for name in FAMILY};rename=output/'lwjgl-env-bindings.txt';rename.write_text(''.join(k+' '+v+'\n'for k,v in sorted(mapping.items())))
 records={};updated=[]
 for item in group['objects']:
  source=Path(item)
  if source.name not in UNITS:updated.append(item);continue
  if source.name in records:raise ValueError('Duplicate env native unit')
  before=undefined(Path(llvm)/'llvm-nm',source);target=output/('scoped-env-'+source.name)
  subprocess.run([str(Path(llvm)/'llvm-objcopy'),'--redefine-syms='+str(rename),str(source),str(target)],check=True)
  after=undefined(Path(llvm)/'llvm-nm',target)
  if after!={mapping.get(n,n)for n in before}:raise ValueError('Unexpected native import changes')
  if code_sections(source)!=code_sections(target):raise ValueError('Scoping altered actual machine instructions')
  records[source.name]={'input_sha256':sha(source),'output_sha256':sha(target),'allocator_imports':{name:mapping[name]for name in FAMILY if name in before},'code_sections_unchanged':True};updated.append(str(target))
 if set(records)!=set(UNITS):raise ValueError('Both env-copy and owning TLS/free units are required')
 group['objects']=updated
 return {'scope':'Only genuine LWJGL ThreadLocalUtil env-copy and common_tools TLS record allocation/free; existing scoped graphics allocator family, no JVM/global changes','bindings':mapping,'objects':records,'console':'PENDING PS5 GL capabilities/native-thread lifecycle'}
