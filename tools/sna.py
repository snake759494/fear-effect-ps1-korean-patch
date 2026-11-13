# SNAME?.SNA 장면 이름: 헤더 [n][그룹오프셋 n개], 그룹 [cnt][(id,문자열오프셋)*cnt], 문자열 영역(기준=첫 문자열)
import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from jtab import dec2
def patch(d,tr,enc,log=print):
    d=bytearray(d)
    n=struct.unpack_from('<I',d,0)[0]; go=struct.unpack_from('<%dI'%n,d,4)
    refs=[]
    for g in go:
        c=struct.unpack_from('<I',d,g)[0]
        for i in range(c): refs.append(g+4+i*8+4)
    base=max(g+4+struct.unpack_from('<I',d,g)[0]*8 for g in go)
    offs=sorted(set(struct.unpack_from('<I',d,r)[0] for r in refs))
    end=d.find(b'\xab',base)
    if end<0: end=len(d)
    new=bytearray(); mp={}
    for o in offs:
        e=d.index(b'\0',base+o); raw=bytes(d[base+o:e]); ja=dec2(raw)
        if ja in tr: raw=enc.enc(tr[ja])
        elif any(ord(c)>0x3000 for c in ja): log('SNA 미번역 '+ja)
        mp[o]=len(new); new+=raw+b'\0'
    last=max(d.index(b'\0',base+o) for o in offs)+1
    assert base+len(new)<=end,('SNA 초과',base+len(new),end)
    d[base:last]=bytes(last-base)
    d[base:base+len(new)]=new
    for r in refs: struct.pack_into('<I',d,r,mp[struct.unpack_from('<I',d,r)[0]])
    return bytes(d)
