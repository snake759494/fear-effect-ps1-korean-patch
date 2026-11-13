# 게임 폰트(FONTLG) 일본어 모드 코드표: '@'(0x40) 이후 바이트 c → 글리프
J={}
rows='''20 _地@下水道_入口ボイラー室東交
30 差点南西デッキ操作ウィン・チュ庭
40 @園兵舎パテトレエベタシャフ階ジ
50 分析スカブリバオゴプ安ツ@ル@ム
60 @寺院ミグ墓ギ峡谷ロドハナピクォ
70 ホノサマ基ガ爆薬庫ヴアひろう@_
80 _そ@びつかはしごセメモに中です
90 を抜ないくださがれてません空きあ
a0 @り失敗たァ上書よコ最後倒敵の数
b0 使っ弾ヒ率気付ず回時間○@進@め
c0 @新以る本当ソ自軍旗障害物移動距
d0 離ビョニザズェ格闘ユダケヘワ@_
e0 _ヤ@指紋機浄化腺血液細胞核宝車
f0 武器宿屋業部木板骨ちょ太陽月猛牛
100 @民家お金皇帝勇ポゲ原石壊ぎベネ'''
for ln in rows.split('\n'):
    a,s=ln.split(' '); a=int(a,16); assert len(s)==16,ln
    for i,ch in enumerate(s): J[a+i]=ch
def dec(b):
    out=[];jp=False
    for c in b:
        if c==0x40: jp=not jp; out.append('{@}') if False else None; continue
        if jp: out.append(J.get(c,'{%02x}'%c))
        else: out.append(chr(c) if 32<=c<127 else '{%02x}'%c)
    return ''.join(out)
# 정확한 디코드: 지속형 페이지 (`=0 @=1 ~=2 ^=3), 글리프 라벨 = c + 0x60*(page-1)
ESC={0x60:0,0x40:1,0x7e:2,0x5e:3}
def glyph(page,c):
    return None if page==0 else c+0x60*(page-1)
def dec2(b):
    out=[];p=0
    for c in b:
        if c in ESC: p=ESC[c]; continue
        if c>=0x80: out.append('{%02x}'%c); continue
        if p==0 or c==0x20: out.append(chr(c)); continue
        L=c+0x60*(p-1); out.append(J.get(L,'{p%d:%02x}'%(p,c)))
    return ''.join(out)
def valid(b):
    p=0; n=0
    for c in b:
        if c in ESC: p=ESC[c]; continue
        if c<0x20 or c>=0x7f: return False
        if p and c!=0x20:
            L=c+0x60*(p-1)
            if L not in J or J[L] in '@_': return False
            n+=1
    return n>=1
