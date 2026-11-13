import os,re,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from jtab import dec2,valid
pat=re.compile(rb'[\x20-\x7f]{2,}(?=\x00)')
for d in ['d1','d2','d3','d4']:
  for root,_,fs in os.walk('orig/'+d):
    for f in fs:
      if f.endswith('.BS') or 'CHAR' in root or 'NPC' in root or 'MIDI' in f: continue
      b=open(os.path.join(root,f),'rb').read()
      for m in pat.finditer(b):
        s=m.group()
        if any(e in s for e in b'@~^') and valid(s):
          print(d,os.path.join(root[7:],f).replace(os.sep,'/'),hex(m.start()),dec2(s),sep='\t')
