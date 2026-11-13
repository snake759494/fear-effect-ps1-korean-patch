# 타이틀 폰트(FONTTITJ) 코드표 0x20-0x7f (16x16)
R=[" !\"#$%&'()*+,-./","0123456789メモリーカド","のチェック中です・にアセスを抜か","ないくださが差れてませんフォマ_","壊ブデタありロる選択しバ開ィ違入","っDISC失敗たノルハ正____"]
T={}
for i,r in enumerate(R):
    assert len(r)==16,(i,len(r))
    for j,c in enumerate(r): T[0x20+i*16+j]=c
def dec(b): return ''.join(T.get(c,'{%02x}'%c) for c in b)
