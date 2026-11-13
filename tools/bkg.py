# 메뉴 BKG(TIM) 일본어 글자 이미지를 한글로 다시 그림
import os,sys,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image,ImageDraw,ImageFont
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
FONT=(lambda n:os.path.join(W_,'fonts',n) if os.path.exists(os.path.join(W_,'fonts',n)) else os.path.join(W_,'..',n))('NanumSquareNeo-dEb.ttf')
KO={'BEACON':'세이브 비컨','CONTTYPE':'타입','CLASSIC':'클래식','BACK':'돌아가기','SELECT':'결정',
    'RETROHLX':'헬릭스 피어 이펙트','ARTGALRY':'아트 갤러리','CROUCH':'웅크리기','INVF':'아이템 전환 앞',
    'EVADE':'피하기','RUN':'달리기','VIB':'진동','ON2':'온','OFF2':'오프','EXIT':'돌아가기',
    'RESET':'기본 설정으로 복원','FIRE':'공격/퀵 드로','ACTION':'액션/무기 선택','INVB':'아이템 전환 뒤',
    'T180':'퀵 턴','STEREO':'스테레오','MONO':'모노럴','ON':'온','OFF':'오프','MASTERV':'볼륨',
    'NORMAL':'노멀','HARD':'하드','DIFFCLTY':'난이도','START':'START 버튼을 누르세요','AUTODRAW':'오토 리로드'}
# 아이콘 보존: 글자가 들어갈 x 범위 (원본 픽셀)
XR={'BACK':(0,60),'SELECT':(26,96)}

def _parse(t):
    fl=struct.unpack_from('<I',t,4)[0]; bpp=fl&3
    n=struct.unpack_from('<I',t,8)[0]; cw,ch=struct.unpack_from('<2H',t,16)
    cols=struct.unpack_from('<%dH'%(cw*ch),t,20); o=8+n
    bn,x,y,w,h=struct.unpack_from('<I4H',t,o); px=o+12
    W=w*4 if bpp==0 else w*2
    raw=np.frombuffer(t,np.uint8,bn-12,px)
    if bpp==0:
        idx=np.empty(W*h,np.uint8); idx[0::2]=raw&15; idx[1::2]=raw>>4
    else: idx=raw.copy()
    return bpp,cols,px,idx.reshape(h,W)

def patch(t,name):
    text=KO[name]; t=bytearray(t)
    bpp,cols,px,idx=_parse(bytes(t)); h,W=idx.shape
    ncol=16 if bpp==0 else 256
    lum=np.array([((c&31)+((c>>5)&31)+((c>>10)&31))/93*255 for c in cols[:ncol]])
    r=np.array([c&31 for c in cols[:ncol]]); g=np.array([(c>>5)&31 for c in cols[:ncol]]); b=np.array([(c>>10)&31 for c in cols[:ncol]])
    sat=np.maximum(np.maximum(r,g),b)-np.minimum(np.minimum(r,g),b)
    gray=(sat[idx]<=2)
    bright=(lum[idx]>60)&gray
    x0,x1=XR.get(name,(0,W))
    reg=np.zeros_like(bright); reg[:,x0:x1]=True
    ys,xs=np.nonzero(bright&reg)
    bx0,bx1,by0,by1=xs.min(),xs.max(),ys.min(),ys.max()
    bg=int(idx[0,0])
    # 글자 영역 지우기
    clr=reg&gray; idx=idx.copy(); idx[clr]=bg
    # 렌더(4배)
    th=by1-by0+1; S=4
    size=int(th*1.05)
    while True:
        f=ImageFont.truetype(FONT,size*S)
        d0=ImageDraw.Draw(Image.new('L',(1,1)))
        bb=d0.textbbox((0,0),text,font=f); tw=(bb[2]-bb[0])/S
        avail=(x1-2)-bx0 if name not in ('MASTERV','DIFFCLTY','START','AUTODRAW','NORMAL') else (x1-2)-max(2,x0)
        if tw<=avail or size<=8: break
        size-=1
    im=Image.new('L',(W*S,h*S),0); d=ImageDraw.Draw(im)
    if name in ('MASTERV','DIFFCLTY','START','AUTODRAW'):
        cx=(bx0+bx1+1)/2; X=cx*S-(bb[2]-bb[0])/2-bb[0]
        if X<2*S: X=2*S-bb[0]
    else: X=bx0*S-bb[0]
    Y=((by0+by1+1)/2)*S-(bb[3]+bb[1])/2
    d.text((X,Y),text,font=f,fill=255)
    a=np.array(im.resize((W,h),Image.LANCZOS)).astype(float)
    # 회색 팔레트 중 가장 가까운 밝기
    gi=[i for i in range(ncol) if sat[i]<=2]
    gl=lum[gi]
    for yy,xx in zip(*np.nonzero(a>24)):
        if not reg[yy,xx]: continue
        v=a[yy,xx]; k=gi[int(np.argmin(np.abs(gl-v)))]; idx[yy,xx]=k
    # 다시 쓰기
    flat=idx.ravel()
    if bpp==0: data=(flat[0::2]|(flat[1::2]<<4)).astype(np.uint8).tobytes()
    else: data=flat.astype(np.uint8).tobytes()
    t[px:px+len(data)]=data
    return bytes(t)
