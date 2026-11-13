# 범위 표기(a-b<TAB>텍스트) → 구간별 tsv
import sys
src,dst=sys.argv[1:3]; out=[]
for l in open(src,encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    k,t=l.split('\t',1); a,b=(k.split('-')+[k])[:2]
    for i in range(int(a),int(b)+1): out.append(f'{i}\t{t}')
open(dst,'w',encoding='utf-8').write('\n'.join(out)+'\n'); print(dst,len(out))
