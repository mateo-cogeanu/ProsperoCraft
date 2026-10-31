"""Compare ELF64 relocatable code/data with local pooled-string renumbering allowed."""
import struct


def canonical_object(blob):
    if blob[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H',blob,16)[0] != 1:
        raise ValueError('Expected little-endian ELF64 relocatable')
    offset=struct.unpack_from('<Q',blob,40)[0]
    size,count,names_index=struct.unpack_from('<HHH',blob,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',blob,offset+i*size) for i in range(count)]
    def data(section):return blob[section[4]:section[4]+section[5]] if section[1]!=8 else b''
    names=data(sections[names_index])
    def string(table,start):return table[start:].split(b'\0',1)[0]
    section_names=[string(names,s[0]).decode() for s in sections]
    symbols=[];symbol_section=next(s for s in sections if s[1]==2);table=data(sections[symbol_section[6]])
    for i in range(0,symbol_section[5],symbol_section[9]):
        name,info,other,index,value,length=struct.unpack_from('<IBBHQQ',data(symbol_section),i)
        name=string(table,name)
        if name.startswith(b'.L.str'):
            name=b'string:'+string(data(sections[index]),value)
            value=0
        symbols.append((name,info,other,section_names[index] if index<count else index,value,length))
    result={}
    for i,s in enumerate(sections):
        if not s[2]&2:continue  # Compare all allocated code, data, BSS and unwind state.
        content=data(s)
        if s[2]&0x20:content=tuple(sorted(content.split(b'\0')))  # SHF_STRINGS pool order.
        relocations=[]
        for r in sections:
            if r[1]!=4 or r[7]!=i:continue
            for j in range(0,r[5],r[9]):
                address,info,addend=struct.unpack_from('<QQq',data(r),j)
                target=symbols[info>>32];kind=info&0xffffffff
                if target[1]&15==3 and target[3]=='.rodata.str1.1':
                    if kind==1:pool_offset=addend;residual=0
                    elif kind==2 and section_names[i].endswith('.rel'):pool_offset=addend-address;residual=address
                    else:raise ValueError('Unhandled pooled section relocation')
                    pool=next(data(section) for k,section in enumerate(sections) if section_names[k]=='.rodata.str1.1')
                    if not 0<=pool_offset<len(pool):raise ValueError('Invalid string relocation')
                    target=(b'pool:'+string(pool,pool_offset),);addend=residual
                relocations.append((address,kind,target,addend))
        result[section_names[i]]=(s[1],s[2],s[5],s[8],content,tuple(relocations))
    # Include symbol ABI/binding/visibility, independent of table order/local string numbers.
    return result,sorted(symbols,key=repr)
