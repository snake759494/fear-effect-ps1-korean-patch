# *E.DB 표시 문자열 교체 (표별 재배치 + 오프셋 갱신)
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import db
from jtab import dec2

def rebuild(d,tr,enc,log=None):
    """d: DB bytes, tr: 일본어→한국어 dict, enc: ui.Enc. 반환 새 bytes"""
    d=bytearray(d); h=db.hdr(d)
    secs=sorted(set(x for x in h if 0<x<len(d)))
    for name,t,base,ptrs in db.tables(bytes(d)):
        # 표 오프셋 위치(u16 배열)
        if name=='item': tab=t+8; delta=0
        else: tab=t; delta=8 if name=='wpn' else 0
        # 영역: 첫 표시 문자열 앞(내부명 포함)부터 마지막 문자열 끝까지
        pre=8 if name!='msg' else 0
        start=ptrs[0]-pre
        ends=[d.index(b'\0',p)+1 for p in ptrs]
        stop=max(ends)
        limit=min([s for s in secs if s>stop]+[len(d)])
        # 끝 이후 여유(0/0xcd 패딩) 포함 한계
        new=bytearray(); newp=[]
        order=sorted(range(len(ptrs)),key=lambda i:ptrs[i])
        cur=start
        for k,i in enumerate(order):
            p=ptrs[i]
            if k>0 and p==ptrs[order[k-1]]:   # 같은 문자열 공유
                newp.append((i,newp[-1][1])); continue
            new+=d[cur:p]                       # 앞 부분(내부명/글루) 그대로
            ja=dec2(bytes(d[p:ends[i]-1]))
            raw=bytes(d[p:ends[i]-1])
            if ja in tr: raw=enc.enc(tr[ja])
            elif any(ord(c)>0x3000 for c in ja) and log: log(f'미번역 {name} {ja}')
            newp.append((i,start+len(new))); new+=raw+b'\0'
            cur=ends[i]
        tail=stop
        if start+len(new)>limit:
            raise ValueError(f'{name} 영역 초과 {start+len(new):x}>{limit:x}')
        d[start:start+len(new)]=new
        # 남는 부분 0 채움 (원래 끝까지)
        if start+len(new)<stop: d[start+len(new):stop]=bytes(stop-start-len(new))
        # 오프셋 갱신
        bb=base
        for i,np_ in newp:
            v=np_-bb-delta
            assert 0<=v<0x10000
            struct.pack_into('<H',d,tab+i*2,v)
    return bytes(d)
