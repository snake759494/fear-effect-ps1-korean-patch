import capstone,struct
def load(path,base=None,off=0x800):
    b=open(path,'rb').read()
    if base is None: base=struct.unpack_from('<I',b,0x18)[0]
    md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
    out=[]
    code=b[off:]
    for i in range(0,len(code)-3,4):
        w=code[i:i+4]; r=list(md.disasm(w,base+i))
        out.append((base+i,r[0].mnemonic,r[0].op_str) if r else (base+i,'.word',w[::-1].hex()))
    return out
