# FMV 자막 교체: 일본어 세로 자막 지우기 + 한글 세로 자막 그리기 + 영역 MB 재인코딩
import os,sys,struct,numpy as np,cv2
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fmv, mdec as M
from PIL import Image,ImageDraw,ImageFont
W_=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
ZX0,ZX1,ZY0,ZY1=262,310,12,156      # 자막 영역
MBC=(16,17,18,19)                   # 재인코딩할 MB 열 (x 256..319)
FONTS={}
def font(name,size):
    k=(name,size)
    if k not in FONTS:
        p=os.path.join(W_,'fonts',name) if os.path.exists(os.path.join(W_,'fonts',name)) else os.path.join(W_,'..',name)
        FONTS[k]=ImageFont.truetype(p,size)
    return FONTS[k]

def text_mask(imgs):
    """구간 프레임들 → 자막 글자 마스크 (영역 내, 안정적으로 밝은 픽셀)"""
    acc=np.zeros(imgs[0].shape[:2],float)
    for im in imgs:
        f=im.astype(int); mx=f.max(2); mn=f.min(2)
        white=(mn>150)&(mx-mn<70)
        color=(mx>200)                     # 주황 강조 글자 등
        acc+=white|color
    st=acc/len(imgs)>=0.6
    m=np.zeros_like(st); m[ZY0:ZY1,ZX0:ZX1]=st[ZY0:ZY1,ZX0:ZX1]
    return m

def erase(img,mask,grow=2):
    k=np.ones((3,3),np.uint8)
    mk=cv2.dilate(mask.astype(np.uint8)*255,k,iterations=grow)
    return cv2.inpaint(img,mk,4,cv2.INPAINT_TELEA)

def layout(text,top=19,right=296,pitch=12,maxrows=11):
    """한글 세로쓰기 배치: '/'는 강제 열바꿈, <..>는 노란 강조. 반환 [(x중심,y위,글자,강조)]"""
    cols=[]; hl=False
    for part in text.split('/'):
        cur=[]
        for ch in part.strip():
            if ch=='<': hl=True; continue
            if ch=='>': hl=False; continue
            if ch==' ':
                if cur and cur[-1][0]!=' ': cur.append((' ',hl))
                continue
            cur.append((ch,hl))
        col=[];h=0
        for ch,f in cur:
            u=0.5 if ch==' ' else 1
            if h+u>maxrows and ch!=' ':
                while col and col[-1][0]==' ': col.pop()
                cols.append(col); col=[];h=0
            if ch==' ' and not col: continue
            col.append((ch,f)); h+=u
        while col and col[-1][0]==' ': col.pop()
        if col: cols.append(col)
    out=[]
    for ci,col in enumerate(cols):
        x=right-ci*pitch; y=top
        for ch,f in col:
            if ch==' ': y+=pitch//2; continue
            out.append((x,y,ch,f)); y+=pitch
    return out,len(cols)

YEL=np.array([255,214,40],float); WHT=np.array([235,235,235],float)
_RC={}
def render(img,text,fname='NanumSquareNeo-dEb.ttf',size=11,pitch=12,**kw):
    H,W=img.shape[:2]; key=(text,H,W,fname,size,pitch)
    if key not in _RC:
        if len(_RC)>8: _RC.clear()
        _RC[key]=_overlay(text,H,W,fname,size,pitch,**kw)
    a,ay,sh,nc=_RC[key]
    out=img.astype(float)
    out=out*(1-0.75*sh[...,None])
    col=WHT[None,None,:]*(1-ay[...,None])+YEL[None,None,:]*ay[...,None]
    out=out*(1-a[...,None])+col*a[...,None]
    return np.clip(out,0,255).astype(np.uint8),nc
def _overlay(text,H,W,fname,size,pitch,**kw):
    pl,nc=layout(text,pitch=pitch,**kw)
    fg=Image.new('L',(W*4,H*4),0); fy=Image.new('L',(W*4,H*4),0)
    d=ImageDraw.Draw(fg); dy=ImageDraw.Draw(fy); f=font(fname,size*4)
    for x,y,ch,hl in pl:
        bb=d.textbbox((0,0),ch,font=f); w=bb[2]-bb[0]; h=bb[3]-bb[1]
        pos=(x*4-w/2-bb[0],y*4+(pitch*4-h)/2-bb[1])
        d.text(pos,ch,font=f,fill=255)
        if hl: dy.text(pos,ch,font=f,fill=255)
    a=np.array(fg.resize((W,H),Image.LANCZOS),float)/255
    ay=np.array(fy.resize((W,H),Image.LANCZOS),float)/255
    sh=cv2.dilate((a*255).astype(np.uint8),np.ones((3,3),np.uint8)).astype(float)/255
    sh=cv2.GaussianBlur(sh,(3,3),0.6)
    return a,ay,sh,nc

def encode_frame(data,w,h,newimg,cap,oldimg=None):
    q,coef,pos=fmv.decode(data,w,h); nac=fmv.decode.nac.copy()
    rows=(h+15)//16
    if oldimg is None: oldimg=fmv.to_rgb(coef,w,h)
    diff=np.abs(newimg.astype(int)-oldimg.astype(int)).max(2)>0
    sel=set()
    for mx in range((w+15)//16):
        for my in range(rows):
            if diff[my*16:my*16+16,mx*16:mx*16+16].any(): sel.add(mx*rows+my)
    if not sel: return data,None
    for maxac in (63,40,28,20,14,10,6):
        nm=M.from_rgb(np.ascontiguousarray(newimg),q,sel,maxac)
        out=fmv.reencode(data,w,h,q,pos,nac,nm,cap)
        if out is not None: return out,maxac
    return None,None
