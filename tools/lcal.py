import struct
def parse(d):
    n=struct.unpack_from('<I',d,0)[0]; out={}
    for i in range(n):
        name=d[4+i*8:8+i*8].decode(); o=struct.unpack_from('<I',d,8+i*8)[0]
        ev=[]
        while True:
            f,t=struct.unpack_from('<ii',d,o); o+=8
            if f==-1: break
            ev.append((f,None if t==-1 else d[t:d.index(b'\0',t)].decode('latin1')))
        out[name]=ev
    return out
def lines(ev):
    """(start,end,text) 목록: 같은 프레임 동시 표시는 ' / '로 합침"""
    res=[];cur=[];st=None
    for f,t in ev:
        if t is None:
            if cur: res.append((st,f,' / '.join(cur))); cur=[]; st=None
        else:
            if st is not None and f!=st and cur: res.append((st,f,' / '.join(cur))); cur=[]
            if not cur: st=f
            cur.append(t)
    if cur: res.append((st,None,' / '.join(cur)))
    return res
