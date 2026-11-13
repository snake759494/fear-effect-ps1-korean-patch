# 스트림 프레임 패딩의 장면 태그(A01S 등) 추출
import re,struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
import scan
TAG=re.compile(rb'\x00\x00\x00\x00([A-I]\d\d[A-Z])\x00')
def tags(dd,lba,size):
    fr=scan.frames_index(dd,lba,size); out=[]
    for k,f in enumerate(fr):
        if None in f['secs']: continue
        data=b''.join(dd.sector(x)[24+32:24+2048] for x in f['secs'])
        used=struct.unpack_from('<I',dd.sector(f['secs'][0]),24+12)[0]
        for m in TAG.finditer(data[used:]):
            out.append((k,m.group(1).decode()))
    return fr,out
if __name__=='__main__':
    dd=Disc(sys.argv[1]); files={p:(l,s) for p,l,s,_,_ in dd.walk()}
    l,s=files[sys.argv[2]]
    fr,t=tags(dd,l,s); print(len(fr)); 
    last=None
    for k,n in t:
        if n!=last: print(k,n); last=n
