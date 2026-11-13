import struct
from PIL import Image
def clut(d):
    n=struct.unpack_from('<I',d,8)[0]; cx,cy,cw,ch=struct.unpack_from('<4H',d,12)
    cols=struct.unpack_from('<%dH'%(cw*ch),d,20)
    return cols,8+n,(cx,cy,cw,ch)
def rgb(c):
    return ((c&31)*255//31,((c>>5)&31)*255//31,((c>>10)&31)*255//31)
def decode(d,pal=0):
    fl=struct.unpack_from('<I',d,4)[0]; bpp=fl&3; o=8; cols=None
    if fl&8: cols,o,_=clut(d)
    n,x,y,w,h=struct.unpack_from('<I4H',d,o); px=d[o+12:o+n]
    if bpp==0:
        W=w*4; im=Image.new('RGB',(W,h)); P=im.load()
        for yy in range(h):
            for xx in range(W):
                v=px[(yy*W+xx)//2]; v=(v>>4) if xx&1 else v&15
                P[xx,yy]=rgb(cols[pal*16+v])
        return im,(x,y,w,h)
    if bpp==1:
        W=w*2; im=Image.new('RGB',(W,h)); P=im.load()
        for yy in range(h):
            for xx in range(W): P[xx,yy]=rgb(cols[pal*256+px[yy*W+xx]])
        return im,(x,y,w,h)
    if bpp==2:
        im=Image.new('RGB',(w,h)); P=im.load()
        for yy in range(h):
            for xx in range(w): P[xx,yy]=rgb(struct.unpack_from('<H',px,(yy*w+xx)*2)[0])
        return im,(x,y,w,h)
