# FMV 자막 적용: [KR].bin 의 스트림 프레임을 제자리 교체
# python fmvapply.py <disc> <path> <tag> [미리보기만:k목록]
import sys,os,json,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from disc import Writer
from iso import Disc
import fmv,scan,sub
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
G_=os.path.dirname(W_)
PAD=2
def load_tr(tag):
    tr={}
    for l in open(os.path.join(W_,'text','fmv',tag+'_ko.tsv'),encoding='utf-8'):
        l=l.rstrip('\n')
        if l and not l.startswith('#'):
            k,t=l.split('\t',1); tr[int(k)]=t
    return tr
def apply(disc,path,tag,preview=None,binpath=None):
    binpath=binpath or os.path.join(G_,'Helix - Fear Effect (Japan) (Disc %s) [KR].bin'%disc)
    w=Writer(binpath); src=Disc(os.path.join(G_,'Helix - Fear Effect (Japan) (Disc %s).bin'%disc))
    fr=scan.frames_index(src,*w.files[path][1:3])
    S=json.load(open(os.path.join(W_,'text','fmv',tag+'.json'))); tr=load_tr(tag)
    stat={'ok':0,'fail':0,'lowq':0}; pend={}
    only=os.environ.get('FMV_ONLY_FROM')
    if only: S=[x for x in S if x['k']>=int(only)]
    for s in S:
        k=s['k']
        if k%25==0: print(tag,k,len(S),flush=True)
        if preview is not None and k not in preview: continue
        txt=tr.get(k)
        if txt is None: print('미번역',tag,k); continue
        a=max(0,s['start']-PAD); b=min(len(fr)-1,s['end']+PAD)
        frames=[]
        for i in range(a,b+1):
            f=fr[i]
            if None in f['secs']: frames.append(None); continue
            data=b''.join(src.sector(x)[24+32:24+2048] for x in f['secs'])
            q,c,pos=fmv.decode(data,f['w'],f['h']); frames.append((f,data,fmv.to_rgb(c,f['w'],f['h'])))
        core=[x[2] for x in frames[s['start']-a:s['end']-a+1] if x]
        step=max(1,len(core)//15)
        m=sub.text_mask(core[::step])
        x0,y0,x1,y1=s['box']; bm=np.zeros_like(m); bm[max(0,y0-3):y1+4,max(0,x0-3):x1+4]=True; m&=bm
        if k>=1000 and m.sum()>0:
            def dec(i):
                f=fr[i]
                if None in f['secs']: return None
                data=b''.join(src.sector(x)[24+32:24+2048] for x in f['secs'])
                q,c,pos=fmv.decode(data,f['w'],f['h']); return (f,data,fmv.to_rgb(c,f['w'],f['h']))
            from scipy.ndimage import binary_dilation
            ring=binary_dilation(m,iterations=2)&~m
            busy=np.zeros(len(fr),bool)
            for o in S:
                if o['k']!=k: busy[max(0,o['start']-PAD):o['end']+PAD+1]=True
            def has(x):
                if x is None or x[2].shape[:2]!=m.shape: return False
                g=x[2].astype(int); w_=(g.min(2)>90)&(g.max(2)-g.min(2)<80)
                if (w_&m).sum()/m.sum()<=0.6: return False
                l=g.mean(2); return l[m].mean()-l[ring].mean()>45
            i=a-1
            while i>=0 and i>=s['start']-200 and not busy[i]:
                x=dec(i)
                if not has(x): break
                frames.insert(0,x); i-=1
            i=b+1
            while i<len(fr) and i<=s['end']+200 and not busy[i]:
                x=dec(i)
                if not has(x): break
                frames.append(x); i+=1
        for j,x in enumerate(frames):
            if x is None: continue
            f,data,img=x
            new=sub.erase(img,m); new,_=sub.render(new,txt)
            cap=f['cc']*2016
            out,mq=sub.encode_frame(data,f['w'],f['h'],new,cap,img)
            if preview is not None and j==(len(frames)//2):
                Image.fromarray(np.concatenate([img,new],1)).resize((1280,320)).save(os.path.join(W_,'shots','pv_%s_%d.png'%(tag,k)))
            if out is None: stat['fail']+=1; continue
            stat['ok']+=1; stat['lowq']+=(mq is not None and mq<20)
            if preview is not None: continue
            fs=(len(out)+3)//4*4; out=out+bytes(cap-len(out))
            for ci,lba in enumerate(f['secs']):
                sec=src.sector(lba); hd=bytearray(sec[24:24+32])
                struct.pack_into('<I',hd,12,fs)   # 프레임 데이터 크기
                pend[lba]=bytes(hd)+out[ci*2016:(ci+1)*2016]
    for lba in sorted(pend): w.wsec(lba,pend[lba],keep_sub=True)
    w.f.close(); print(tag,stat,flush=True)
if __name__=='__main__':
    pv=[int(x) for x in sys.argv[4].split(',')] if len(sys.argv)>4 else None
    apply(sys.argv[1],sys.argv[2],sys.argv[3],pv)
