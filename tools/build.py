# 한글 패치 빌드: 원본 bin 복사 → 파일 교체 → [KR].bin/.cue
import os,sys,struct,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import wad,ui,dbw,sna,title,bkg
from disc import Writer
W_=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
G_=os.path.dirname(W_)
NAME='Helix - Fear Effect (Japan) (Disc %d)'
LOG=[]
def log(s):
    if s not in LOG: LOG.append(s); print(s)

def get_enc():
    tr=ui.load_tsv('ui_ko.tsv','sna_ko.tsv')
    return tr,ui.Enc(sorted(set(tr.values())))

def wad_put(b,idx_pred,fn):
    """WAD 안 조건에 맞는 항목들을 fn(bytes)->bytes(같은 크기) 로 교체"""
    b=bytearray(b); k=0
    for i,e in enumerate(wad.parse(bytes(b))):
        nm,off,t,sz=e[:4]
        if idx_pred(i,nm):
            new=fn(bytes(b[off:off+sz])); assert len(new)==sz,(nm,len(new),sz)
            b[off:off+sz]=new; k+=1
    assert k,'항목 없음'
    return bytes(b)

def ingame_files(dn,tr,enc,fontimg):
    out={}
    o=lambda p:open(os.path.join(W_,'orig','d%d'%dn,p.lstrip('/')),'rb').read()
    # EXE
    exe=[f for f in os.listdir(os.path.join(W_,'orig','d%d'%dn)) if f.startswith('SLPS')][0]
    out['/'+exe]=ui.exe_patch(o(exe))
    # 폰트 (첫 FONTLG = 일본어)
    first=[None]
    def fl(i,nm):
        if nm=='FONTLG.FNT' and first[0] is None: first[0]=i
        return i==first[0]
    out['/FONT2.WAD']=wad_put(o('FONT2.WAD'),fl,lambda x:fontimg)
    # DB / SNA
    env=os.path.join(W_,'orig','d%d'%dn,'ENV')
    for f in sorted(os.listdir(env)):
        if f.endswith('E.DB') and len(f)==4:
            out['/ENV/'+f]=dbw.rebuild(o('ENV/'+f),tr,enc,log)
        if f.endswith('ENV.WAD'):
            ents=wad.parse(o('ENV/'+f)); fdb=[i for i,e in enumerate(ents) if e[0].endswith('.DB')][0]
            b=wad_put(o('ENV/'+f),lambda i,nm:i==fdb,lambda x:dbw.rebuild(x,tr,enc,log))
            b=wad_put(b,lambda i,nm:nm=='SNAMEE.SNA',lambda x:sna.patch(x,tr,enc,log))
            out['/ENV/'+f]=b
    for p in ('IFACE/TITLEE.WAD','IFACE/LEVSEL.WAD'):
        out['/'+p]=wad_put(out.get('/'+p) or o(p),lambda i,nm:nm=='SNAMEE.SNA',lambda x:sna.patch(x,tr,enc,log))
    # 타이틀/스왑 화면 폰트와 문자열
    L,mp=title.load()
    for p in ('IFACE/TITLEE.WAD','IFACE/SWAPE.WAD'):
        out['/'+p]=wad_put(out.get('/'+p) or o(p),lambda i,nm:nm=='FONTTITJ.FNT',lambda x:title.patch_font(x,mp))
    # 메뉴 이미지
    b=bytearray(out['/IFACE/TITLEE.WAD'])
    for e in wad.parse(bytes(b)):
        nm=e[0][:-4]
        if e[0].endswith('.BKG') and nm in bkg.KO:
            b[e[1]:e[1]+e[3]]=bkg.patch(bytes(b[e[1]:e[1]+e[3]]),nm)
    out['/IFACE/TITLEE.WAD']=bytes(b)
    for f in ('GSHELL.OVR','SWAP.OVR'):
        out['/OVERLAY/'+f]=title.patch_ovr(o('OVERLAY/'+f),f,L,mp)
    return out

def build(dn,extra=None,copy=True):
    src=os.path.join(G_,NAME%dn+'.bin'); dst=os.path.join(G_,NAME%dn+' [KR].bin')
    if copy: shutil.copyfile(src,dst)
    cue=open(os.path.join(G_,NAME%dn+'.cue'),encoding='latin1').read()
    open(os.path.join(G_,NAME%dn+' [KR].cue'),'w',encoding='latin1').write(cue.replace(NAME%dn+'.bin',NAME%dn+' [KR].bin'))
    tr,enc=get_enc()
    fontlg=wad.parse(open(os.path.join(W_,'orig','d1','FONT2.WAD'),'rb').read())
    b=open(os.path.join(W_,'orig','d1','FONT2.WAD'),'rb').read()
    e=[x for x in fontlg if x[0]=='FONTLG.FNT'][0]
    fontimg=ui.patch_font_tim(b[e[1]:e[1]+e[3]],enc,os.path.join(W_,'fonts','Galmuri11.ttf'),12,-1)
    files=ingame_files(dn,tr,enc,fontimg)
    if extra: files.update(extra(dn,files))
    w=Writer(dst)
    for p,data in files.items():
        w.replace(p,data,allow_move=False)
    w.f.close()
    print('완료',dst)

if __name__=='__main__':
    nc='--nocopy' in sys.argv
    for a in sys.argv[1:]:
        if a.isdigit(): build(int(a),copy=not nc)
