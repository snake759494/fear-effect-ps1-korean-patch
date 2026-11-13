# 일본어 자막 구간 검출(영역 제한 + 상단 정렬 필터)
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import segs
def jsegs(npz):
    info,M=segs.load(npz)
    for i,m in enumerate(M):
        if m is not None and m.ndim==2 and m.shape[1]>=310:
            z=np.zeros_like(m); z[12:156,270:308]=m[12:156,270:308]; M[i]=z
        else: M[i]=None
    S=segs.segments(info,M,minlen=8,minpx=20)
    return info,[s for s in S if s['box'][0]>=274 and s['box'][2]<=305 and 16<=s['box'][1]<=24]
