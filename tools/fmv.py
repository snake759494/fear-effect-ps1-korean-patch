# PSX STR v2 고속 디코더(numba) + 매크로블록 단위 재인코딩
import numpy as np, math, struct
from numba import njit
import mdec as M

# VLC 디코드 표: 17비트 이하 코드 → (길이, run, level) ; 2비트 '10'=EOB, '000001'=ESC
_tab_len=np.zeros(1<<17,np.int32); _tab_run=np.zeros(1<<17,np.int32); _tab_lev=np.zeros(1<<17,np.int32)
def _put(code,ln,r,l):
    sh=17-ln; base=int(code,2)<<sh
    _tab_len[base:base+(1<<sh)]=ln; _tab_run[base:base+(1<<sh)]=r; _tab_lev[base:base+(1<<sh)]=l
for c,(r,l) in M.DEC.items():
    if c=='11': continue  # 첫 계수 아닌 경우 '11'은 0/1 ; 아래에서 별도
    _put(c,len(c),r,l)
_put('11',2,0,1)
_put('10',2,-1,0)      # EOB
_put('000001',6,-2,0)  # ESC
ZZ=np.array(M.ZZ,np.int32); QT=np.array(M.QT,np.float64)

@njit(cache=True)
def _decode(words,nmb,TL,TR,TV,ZZ,QT,q,coef,mbpos,nac):
    # words: uint16 배열. 비트는 각 16비트 워드 MSB부터
    p=np.int64(0); buf=np.uint64(0); n=np.int64(0)
    nw=len(words)
    for mb in range(nmb):
        # 현재 비트 위치 기록
        mbpos[mb]=p*16-n
        for b in range(6):
            while n<32:
                w=np.uint64(words[p]) if p<nw else np.uint64(0)
                buf=(buf<<np.uint64(16))|w; p+=1; n+=16
            dc=int((buf>>np.uint64(n-10))&np.uint64(0x3ff)); n-=10
            if dc>=512: dc-=1024
            for k in range(64): coef[mb,b,k]=0.0
            coef[mb,b,0]=dc*QT[0]
            i=np.int64(0)
            while True:
                while n<32:
                    w=np.uint64(words[p]) if p<nw else np.uint64(0)
                    buf=(buf<<np.uint64(16))|w; p+=1; n+=16
                idx=int((buf>>np.uint64(n-17))&np.uint64(0x1ffff))
                ln=np.int64(TL[idx]); r=np.int64(TR[idx])
                if ln==0: return -1
                n-=ln
                if r==-1: break
                if r==-2:
                    while n<32:
                        w=np.uint64(words[p]) if p<nw else np.uint64(0)
                        buf=(buf<<np.uint64(16))|w; p+=1; n+=16
                    r=int((buf>>np.uint64(n-6))&np.uint64(0x3f)); n-=6
                    l=int((buf>>np.uint64(n-10))&np.uint64(0x3ff)); n-=10
                    if l>=512: l-=1024
                else:
                    l=np.int64(TV[idx])
                    s=int((buf>>np.uint64(n-1))&np.uint64(1)); n-=1
                    if s: l=-l
                nac[mb]+=1
                i=np.int64(i+r+1)
                if i>63: break
                z=ZZ[i]; coef[mb,b,z]=l*QT[z]*q/8.0
    mbpos[nmb]=p*16-n
    return 0

_C=np.array([[ (math.sqrt(0.125) if u==0 else 0.5)*math.cos((2*x+1)*u*math.pi/16) for x in range(8)] for u in range(8)])

def decode(data,w,h):
    q=data[4]|data[5]<<8; ver=data[6]|data[7]<<8
    if ver!=2: raise ValueError('ver %d'%ver)
    body=data[8:]
    words=np.frombuffer(body[:len(body)//2*2],'<u2')
    W=(w+15)//16; H=(h+15)//16; nmb=W*H
    coef=np.zeros((nmb,6,64)); pos=np.zeros(nmb+1,np.int64); nac=np.zeros(nmb,np.int64)
    r=_decode(words,nmb,_tab_len,_tab_run,_tab_lev,ZZ,QT,q,coef,pos,nac)
    if r<0: raise ValueError('vlc')
    decode.nac=nac
    return q,coef,pos

def to_rgb(coef,w,h):
    W=(w+15)//16*16; H=(h+15)//16*16; rows=H//16; nmb=coef.shape[0]
    B=coef.reshape(nmb,6,8,8)
    px=np.einsum('vy,mbvu,ux->mbyx',_C,B,_C)
    Y=np.zeros((H,W)); Cb=np.zeros((H//2,W//2)); Cr=np.zeros((H//2,W//2))
    for i in range(nmb):
        mx=i//rows; my=i%rows
        Cr[my*8:my*8+8,mx*8:mx*8+8]=px[i,0]; Cb[my*8:my*8+8,mx*8:mx*8+8]=px[i,1]
        Y[my*16:my*16+8,mx*16:mx*16+8]=px[i,2]; Y[my*16:my*16+8,mx*16+8:mx*16+16]=px[i,3]
        Y[my*16+8:my*16+16,mx*16:mx*16+8]=px[i,4]; Y[my*16+8:my*16+16,mx*16+8:mx*16+16]=px[i,5]
    Y=Y+128; cr=Cr.repeat(2,0).repeat(2,1); cb=Cb.repeat(2,0).repeat(2,1)
    R=Y+1.402*cr; G=Y-0.344*cb-0.714*cr; Bb=Y+1.772*cb
    return np.clip(np.stack([R,G,Bb],-1),0,255).astype(np.uint8)[:h,:w]

_BC={}
def _allbits(data):
    k=id(data)
    if _BC.get('k')==k and _BC.get('d') is data: return _BC['s']
    body=np.frombuffer(data[8:8+(len(data)-8)//2*2],np.uint8).reshape(-1,2)[:,::-1].copy()
    st=(np.unpackbits(body.ravel())+48).tobytes().decode()
    _BC.update(k=k,d=data,s=st); return st
def bits_of(data,a,b):
    """원본 비트스트림의 [a,b) 비트를 '0/1' 문자열로"""
    return _allbits(data)[a:b]

def reencode(data,w,h,q,pos,nac,newmbs,cap):
    """newmbs: {mb: [[dc,[(r,l)..]]x6]} 나머지 MB는 원본 비트 복사. 반환 프레임 데이터(헤더 포함) 또는 None"""
    W=(w+15)//16; H=(h+15)//16; nmb=W*H
    bits=[]; ncode=0; nblk=nmb*6
    for i in range(nmb):
        if i in newmbs:
            s=[]
            for dc,ac in newmbs[i]:
                s.append(format(dc&0x3ff,'010b'))
                for r,l in ac:
                    k=(r,abs(l))
                    if k in M.ENC: s.append(M.ENC[k]+('1' if l<0 else '0'))
                    else: s.append('000001'+format(r,'06b')+format(l&0x3ff,'010b'))
                    ncode+=1
                s.append('10')
            bits.append(''.join(s))
        else:
            ncode+=int(nac[i])
            bits.append(bits_of(data,int(pos[i]),int(pos[i+1])))
    allb=''.join(bits)+'0111111111'
    allb+='0'*((-len(allb))%16)
    body=bytearray()
    bb=np.frombuffer(allb.encode(),np.uint8)-48
    body=np.packbits(bb).reshape(-1,2)[:,::-1].tobytes()
    # 원본 헤더의 첫 필드(MDEC 코드 수 관련)는 원본 비율 유지: 다시 계산
    hdr=struct.pack('<HHHH',((ncode+nblk*2+1)//2+31)//32*32,0x3800,q,2)
    out=bytes(hdr)+bytes(body)
    return out if len(out)<=cap else None
