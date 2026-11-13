# 스트림 전체 디코드 → 프레임별 흰 글자 마스크(압축) 저장
# python scan.py <disc> <file> <out.npz>
import sys,os,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
import fmv
def frames_index(dd,lba,size):
    n=size//2048; fr={}; order=[]
    for i in range(n):
        s=dd.sector(lba+i)
        if s[18]&0x08 and s[24:26]==b'\x60\x01':
            ci,cc,fn,fs,w,h=struct.unpack_from('<HHIIHH',s,24+4)
            key=(fn,)
            if ci==0:
                order.append({'num':fn,'w':w,'h':h,'cc':cc,'size':fs,'secs':[None]*cc})
            if order and order[-1]['num']==fn and ci<len(order[-1]['secs']): order[-1]['secs'][ci]=lba+i
    return order
def mask(img):
    f=img.astype(int); mn=f.min(2); mx=f.max(2)
    return (mn>170)&(mx-mn<60)
if __name__=='__main__':
    disc,path,out=sys.argv[1:4]
    dd=Disc(disc); files={p:(l,s) for p,l,s,_,_ in dd.walk()}
    lba,size=files[path]
    fr=frames_index(dd,lba,size)
    M=[];info=[]
    for k,f in enumerate(fr):
        if None in f['secs']: info.append((f['secs'][0] or 0,f['num'],0,0)); M.append(np.zeros(1,np.uint8)); continue
        data=b''.join(dd.sector(x)[24+32:24+2048] for x in f['secs'])
        try:
            q,c,pos=fmv.decode(data,f['w'],f['h']); img=fmv.to_rgb(c,f['w'],f['h'])
            m=mask(img)
        except Exception as e:
            m=np.zeros((f['h'],f['w']),bool)
        M.append(np.packbits(m)); info.append((f['secs'][0],f['num'],f['w'],f['h']))
    np.savez_compressed(out,info=np.array(info),**{'m%d'%i:x for i,x in enumerate(M)})
    print(path,len(fr))
