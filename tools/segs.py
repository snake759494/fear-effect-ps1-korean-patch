# 스캔 결과에서 자막 구간(같은 글자 마스크가 유지되는 프레임 범위) 추출
import numpy as np,sys,json
def load(path):
    z=np.load(path); info=z['info']; M=[]
    for i in range(len(info)):
        w,h=int(info[i][2]),int(info[i][3])
        M.append(np.unpackbits(z['m%d'%i])[:w*h].reshape(h,w).astype(bool) if w else None)
    return info,M
def segments(info,M,minlen=12,minpx=25):
    n=len(M); segs=[]; cur=None
    def st(i):
        if M[i] is None: return None
        a=M[i]
        for j in (i-1,i+1):
            if 0<=j<n and M[j] is not None and M[j].shape==a.shape: a=a&M[j]
            else: return None
        return a
    for i in range(n):
        a=st(i)
        if a is None or a.sum()<minpx:
            if cur: segs.append(cur); cur=None
            continue
        if cur is not None:
            r=cur['ref']; inter=(a&r).sum(); uni=(a|r).sum()
            if inter/uni>0.45 and a.shape==r.shape:
                cur['end']=i; cur['ref']=r&a if (r&a).sum()>minpx else r; continue
            segs.append(cur)
        cur={'start':i,'end':i,'ref':a.copy()}
    if cur: segs.append(cur)
    out=[]
    for s in segs:
        if s['end']-s['start']+1<minlen: continue
        ys,xs=np.nonzero(s['ref'])
        out.append({'start':s['start'],'end':s['end'],'box':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'px':int(s['ref'].sum()),'ref':s['ref']})
    return out
