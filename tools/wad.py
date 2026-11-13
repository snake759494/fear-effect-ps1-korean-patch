import struct,sys
def parse(b):
    hdr=struct.unpack_from('<I',b,0)[0]; ents=[];o=0
    while o+0x24<=hdr:
        nm=b[o:o+20].split(b'\0')[0]
        ok=len(nm)>2 and b'.' in nm and all(32<c<127 for c in nm)
        if ok:
            off,t,sz,sz2=struct.unpack_from('<4I',b,o+20)
            ents.append((nm.decode(),off,t,sz,sz2,o)); o+=0x24; continue
        o+=4
    return ents
if __name__=='__main__':
    b=open(sys.argv[1],'rb').read()
    for e in parse(b): print('%-16s off=%6x t=%2d sz=%6x %6x @%x'%e)
