# 타이틀/스왑 화면 폰트(FONTTITJ 16x16, 코드 0x20-0x7f) 한글화 + GSHELL/SWAP.OVR 문자열
import os,sys,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image,ImageDraw,ImageFont
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
FONT=(lambda n:os.path.join(W_,'fonts',n) if os.path.exists(os.path.join(W_,'fonts',n)) else os.path.join(W_,'..',n))('NanumSquareNeo-cBd.ttf')

def load():
    L=[l.rstrip('\n').split('\t') for l in open(os.path.join(W_,'text','title_ko.tsv'),encoding='utf-8') if l.strip()]
    chars=sorted(set(c for _,_,t in L for c in t if ord(c)>0x7f))
    assert len(chars)<=0x80-0x3a
    mp={c:0x3a+i for i,c in enumerate(chars)}
    return L,mp

def enc(t,mp):
    return bytes(mp[c] if ord(c)>0x7f else ord(c) for c in t)

def patch_font(t,mp,size=15,dy=0):
    t=bytearray(t)
    cl=struct.unpack_from('<16H',t,20)
    n=struct.unpack_from('<I',t,8)[0]; o=8+n
    _,x,y,w,h=struct.unpack_from('<I4H',t,o); px=o+12; W=w*4
    lum=[((c&31)+((c>>5)&31)+((c>>10)&31))/93*255 for c in cl]
    pix=np.zeros((h,W),np.uint8)
    for yy in range(h):
        for xx in range(W):
            v=t[px+(yy*W+xx)//2]; pix[yy,xx]=(v>>4) if xx&1 else v&15
    bg=int(np.bincount(pix.ravel(),minlength=16).argmax())
    lv=sorted([i for i in range(16) if i!=bg and cl[i]],key=lambda i:lum[i])
    f=ImageFont.truetype(FONT,size*4)
    for ch,code in mp.items():
        cx=(code&15)*16; cy=((code-0x20)>>4)*16
        im=Image.new('L',(64,64),0); d=ImageDraw.Draw(im)
        bb=d.textbbox((0,0),ch,font=f)
        d.text(((64-(bb[2]-bb[0]))/2-bb[0],(64-(bb[3]-bb[1]))/2-bb[1]+dy*4),ch,font=f,fill=255)
        g=np.array(im.resize((16,16),Image.LANCZOS)).astype(float)
        for yy in range(16):
            for xx in range(16):
                a=g[yy,xx]
                if a<40: pix[cy+yy,cx+xx]=bg; continue
                best=min(lv,key=lambda i:abs(lum[i]-a)); pix[cy+yy,cx+xx]=best
    for yy in range(h):
        for xx in range(0,W,2):
            t[px+(yy*W+xx)//2]=pix[yy,xx]|(pix[yy,xx+1]<<4)
    return bytes(t)

def patch_ovr(b,name,L,mp):
    b=bytearray(b)
    for f,o,txt in L:
        if f!=name: continue
        o=int(o,16); e=b.index(b'\0',o); k=e
        while b[k]==0: k+=1
        raw=enc(txt,mp); assert len(raw)<=k-o-1
        b[o:k]=raw+bytes(k-o-len(raw))
    return bytes(b)
