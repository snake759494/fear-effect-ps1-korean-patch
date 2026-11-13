# 자막 구간 목록 저장 + 일본어 자막 크롭 시트 생성
# python sheet.py <disc> <path> <tag>
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image,ImageDraw
from iso import Disc
import fmv,scan,jseg
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
G_=os.path.dirname(W_)
def frame(dd,f):
    data=b''.join(dd.sector(x)[24+32:24+2048] for x in f['secs'])
    q,c,pos=fmv.decode(data,f['w'],f['h']); return fmv.to_rgb(c,f['w'],f['h'])
def main(disc,path,tag):
    dd=Disc(os.path.join(G_,'Helix - Fear Effect (Japan) (Disc %s).bin'%disc))
    files={p:(l,s) for p,l,s,_,_ in dd.walk()}
    fr=scan.frames_index(dd,*files[path])
    info,S=jseg.jsegs(os.path.join(W_,'scan','d%s_%s.npz'%(disc,tag)))
    out=[]; crops=[]
    for k,s in enumerate(S):
        out.append({'k':k,'start':s['start'],'end':s['end'],'box':s['box']})
        img=frame(dd,fr[(s['start']+s['end'])//2])
        cr=Image.fromarray(img[14:150,268:308]).resize((80,272),Image.NEAREST)
        crops.append(cr)
    json.dump(out,open(os.path.join(W_,'text','fmv','%s.json'%tag),'w'),indent=0)
    per=24
    for p in range(0,len(crops),per):
        sh=Image.new('RGB',(per//2*90,2*300),(40,40,40)); d=ImageDraw.Draw(sh)
        for i,cr in enumerate(crops[p:p+per]):
            x=(i%(per//2))*90; y=(i//(per//2))*300
            # 오른쪽 열이 먼저 오도록 그대로 배치
            sh.paste(cr,(x+5,y+22)); d.text((x+5,y+4),str(p+i),fill=(255,255,0))
        sh.save(os.path.join(W_,'ex','sh_%s_%02d.png'%(tag,p//per)))
    print(tag,len(S))
if __name__=='__main__': main(*sys.argv[1:4])
