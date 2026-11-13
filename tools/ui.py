# 게임 내 텍스트(FONTLG 일본어 세트) 한글화: 글자 배정, 인코딩, 폰트 그리기, EXE 렌더러 패치
import os,sys,struct,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
W_=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
ESC={0:0x60,1:0x40,2:0x7e,3:0x5e}
RESV={0x40,0x5e,0x60,0x7e,0x20}

import hashlib
def hkey(ja): return hashlib.sha1(ja.encode('utf-8')).hexdigest()[:16]
class HTr(dict):
    """키 = 일본어 원문의 SHA-1 앞 16자리 (원문을 저장소에 두지 않음)"""
    def __contains__(s,ja): return dict.__contains__(s,hkey(ja))
    def __getitem__(s,ja): return dict.__getitem__(s,hkey(ja))
def load_tsv(*names):
    d=HTr()
    for n in names:
        for l in open(os.path.join(W_,'text',n),encoding='utf-8'):
            l=l.rstrip('\n')
            if not l or l.startswith('#'): continue
            a,b=l.split('\t'); d[a]=b
    return d

def slots():
    """(page,code) 순서 목록: 1,2페이지 → 3페이지 → 확장(0x80~)"""
    out=[]
    for p in (1,2):
        out+=[(p,c) for c in range(0x21,0x80) if c not in RESV]
    out+=[(3,c) for c in range(0x21,0x50) if c not in RESV]
    out+=[(4,c) for c in range(0x80,0x80+84)]
    return out

class Enc:
    def __init__(s,texts):
        cnt=collections.Counter()
        for t in texts:
            for ch in t:
                if ord(ch)>0x7e: cnt[ch]+=1
        chars=[c for c,_ in cnt.most_common()]
        sl=slots(); assert len(chars)<=len(sl),(len(chars),len(sl))
        s.map=dict(zip(chars,sl))
    def enc(s,t):
        out=bytearray(); page=0
        for ch in t:
            if ch==' ': out.append(0x20); continue
            if ord(ch)<0x7f:
                if ch in '@^`~': raise ValueError(t)
                if page!=0: out.append(ESC[0]); page=0
                out.append(ord(ch)); continue
            p,c=s.map[ch]
            if p==4:
                out.append(c); page=0; continue
            if p!=page: out.append(ESC[p]); page=p
            out.append(c)
        return bytes(out)
    def cells(s):
        """글리프 시트 셀 위치 (x,y) → 글자"""
        res={}
        for ch,(p,c) in s.map.items():
            if p==4:
                i=c-0x80; res[(192+(i&3)*12,(i>>2)*12)]=ch
            else:
                si=c+0x60*(p-1)+0x40  # 시트 셀 번호(라벨+0x40, 0=좌상단 ASCII 0x20)
                res[((si%16)*12,(si//16)*12)]=ch
        return res

def glyph_img(ch,fontpath,size,dy=0):
    im=Image.new('L',(12,12),0); d=ImageDraw.Draw(im)
    if ch=='○':
        d.ellipse((1,1,10,10),outline=255,width=1); return np.array(im)
    f=ImageFont.truetype(fontpath,size)
    bb=d.textbbox((0,0),ch,font=f); w=bb[2]-bb[0]
    d.text(((12-w)//2-bb[0],dy),ch,font=f,fill=255)
    return np.array(im)

def patch_font_tim(tim,enc,fontpath,size=12,dy=-1):
    """FONTLG TIM(4bpp 256x256) 의 일본어 영역을 비우고 한글 글리프를 그림"""
    tim=bytearray(tim)
    n=struct.unpack_from('<I',tim,8)[0]; o=8+n
    bn,x,y,w,h=struct.unpack_from('<I4H',tim,o); px=o+12; W=w*4
    cl=struct.unpack_from('<16H',tim,20)
    lum=[((c&31)+((c>>5)&31)+((c>>10)&31)) for c in cl]
    bg=14  # 원본 배경 인덱스
    ink=sorted([i for i in range(16) if i!=bg and cl[i]!=0],key=lambda i:-lum[i])
    def put(xx,yy,v):
        k=px+(yy*W+xx)//2
        if xx&1: tim[k]=(tim[k]&0x0f)|(v<<4)
        else: tim[k]=(tim[k]&0xf0)|v
    # 일본어 영역(행 6~20 전체, 오른쪽 확장 열) 지우기
    for yy in range(72,252):
        for xx in range(0,192): put(xx,yy,bg)
    for yy in range(0,252):
        for xx in range(192,240): put(xx,yy,bg)
    for (cx,cy),ch in enc.cells().items():
        g=glyph_img(ch,fontpath,size,dy)
        for yy in range(12):
            for xx in range(12):
                v=g[yy,xx]
                if v>=96:
                    lv=ink[min(len(ink)-1,int((255-v)/256*len(ink)*0.5))]
                    put(cx+xx,cy+yy,lv)
    return bytes(tim)

# ---------- EXE 렌더러 패치 ----------
NEWADDR=0x8007b500
def exe_patch(exe):
    import keystone
    exe=bytearray(exe); base=struct.unpack_from('<I',exe,0x18)[0]
    def put(addr,code):
        ks=keystone.Ks(keystone.KS_ARCH_MIPS,keystone.KS_MODE_MIPS32+keystone.KS_MODE_LITTLE_ENDIAN)
        enc,_=ks.asm(code,addr); exe[0x800+addr-base:0x800+addr-base+len(enc)]=bytes(enc); return len(enc)
    assert exe[0x800+NEWADDR-base:0x800+NEWADDR-base+0x80]==bytes(0x80)
    # 0x8004aad0: bltz v0,skip / nop  →  j NEW / nop
    assert struct.unpack_from('<I',exe,0x800+0x8004aad0-base)[0]>>16==0x0440
    put(0x8004aad0,'j 0x%x; nop'%NEWADDR)
    asm=f'''
    bltz $v0, khi
    nop
    j 0x8004aad8
    nop
khi:
    beqz $s4, kskip
    nop
    andi $v0,$a0,0x7f
    andi $a1,$v0,3
    sll $v1,$a1,3
    sll $a1,$a1,2
    addu $a1,$a1,$v1
    addiu $a1,$a1,192
    srl $v0,$v0,2
    sll $v1,$v0,3
    sll $v0,$v0,2
    addu $a0,$v0,$v1
    move $t9,$zero
    lbu $a2,0x7ec($gp)
    j 0x8004ab70
    nop
kskip:
    j 0x8004ac1c
    nop
'''
    n=put(NEWADDR,asm.replace('\n',';'))
    assert n<=0x80,n
    return bytes(exe)
