# *E.DB 문자열 표 3종 파싱/재작성
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from jtab import dec2
def hdr(d): return struct.unpack_from('<25I',d,0)
def cstr(d,o): return d[o:d.index(b'\0',o)]
def tables(d):
    h=hdr(d); T=[]
    # 아이템: [count][u16 offs...] 기준 = 표 끝(DUMMY), 이름+8 = 표시명
    it=h[19]; n=struct.unpack_from('<I',d,it)[0]
    offs=struct.unpack_from('<%dH'%(n+2),d,it+4)
    base=it+0x12
    T.append(('item',it,base,[base+o for o in offs[2:]] ))
    # 메시지: 표 시작 기준 오프셋, 표시 문자열 직접
    ms=h[23]; first=struct.unpack_from('<H',d,ms)[0]; k=first//2
    mo=struct.unpack_from('<%dH'%k,d,ms)
    T.append(('msg',ms,ms,[ms+o for o in mo]))
    wp=h[24]; first=struct.unpack_from('<H',d,wp)[0]; k=first//2
    wo=struct.unpack_from('<%dH'%k,d,wp)
    T.append(('wpn',wp,wp,[wp+o+8 for o in wo]))
    return T
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    for name,t,base,ptrs in tables(d):
        print('==',name,hex(t),hex(base),len(ptrs))
        for p in ptrs: print('  ',hex(p),dec2(cstr(d,p)))
