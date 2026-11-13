# 원본 BIN 의 ISO9660 파일을 orig/d<N>/ 로 추출 (build.py 가 읽음)
# 사용: python tools/extract.py <디스크 번호> "<원본 BIN>"
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
dn,src=sys.argv[1],sys.argv[2]
d=Disc(src); n=0
for p,lba,size,*_ in d.walk():
    out=os.path.join(W_,'orig','d'+dn,p.lstrip('/'))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'wb').write(d.read(lba,size)); n+=1
print(n,'개 파일 →',os.path.join(W_,'orig','d'+dn))
