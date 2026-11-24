# tiny-chess-01 v11: eval terms (pawn structure, rook files, outposts, king shield)
# + history heuristic cleared per move + node budget 80000. Trial Elo mean 1432.
import json,os,sys
import urllib.request as u
U=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("no env")
V=(0,100,320,330,500,900,0)
P=["","::::::::DDDDDDDD<<>@@><<;;<??<;;:::>>:::;98::89;;<<66<<;::::::::","0244442026::::624:<==<:44;=>>=;44:=>>=:44;<==<;426:;;:6202444420","688888868::::::88:;<<;:88;;<<;;88:<<<<:88<<<<<<88;::::;868888886","::::::::;<<<<<<;9::::::99::::::99::::::99::::::99::::::9:::;;:::","688998868::::::88:;;;;:89:;;;;:9::;;;;:98;;;;;:88:;::::868899886","422002244220022442200224422002246442244686666668>>::::>>>@<::<@>","02466420468::86448>@@>8448@BB@8448@BB@8448>@@>8444::::4404444440"]
KN=(33,31,18,14,-14,-18,-31,-33)
KG=(1,-1,16,-16,15,17,-15,-17)
BD=(15,17,-15,-17)
RD=(1,-1,16,-16)
CR=[15]*128
for s,v in((0,13),(7,14),(112,7),(119,11),(4,12),(116,3)):CR[s]=v
N=[0]
B=80000
KL=[0]*128
def _sm(n):
 n=(n+0x9E3779B97F4A7C15)&0xFFFFFFFFFFFFFFFF
 n=(n^(n>>30))*0xBF58476D1CE4E5B9&0xFFFFFFFFFFFFFFFF
 n=(n^(n>>27))*0x94D049BB133111EB&0xFFFFFFFFFFFFFFFF
 return n^(n>>31)
_Z=[0x243F6A8885A308D3]
for _ in range(13*128+32):_Z.append(_sm(_Z[-1]))
ZP=[_Z[i*128:(i+1)*128] for i in range(13)]
ZSIDE=_Z[13*128]
ZC=[_Z[13*128+1+i] for i in range(16)]
ZE=[_Z[13*128+17+i] for i in range(9)]
TT={}
HH=[0]*(13*128)
def fh(b,w,C,E):
 h=0
 for s in range(128):
  if s&136:continue
  p=b[s]
  if p:h^=ZP[p+6][s]
 if not w:h^=ZSIDE
 h^=ZC[C]
 if E>=0:h^=ZE[(E&7)+1]
 return h
class X(Exception):pass
def rq(p,b):
 try:
  with u.urlopen(u.Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"}))as r:return json.load(r)
 except Exception as e:sys.exit(str(e))
def ak(b,s,w):
 for d in(15,17):
  t=s-d if w else s+d
  if not t&136 and b[t]==(1 if w else -1):return 1
 for d,o in((KN,2),(KG,6)):
  for e in d:
   t=s+e
   if not t&136 and b[t]==(o if w else -o):return 1
 for d in BD+RD:
  t=s+d
  while not t&136:
   q=b[t]
   if q:
    if(d in BD and q in((3,5)if w else(-3,-5)))or(d in RD and q in((4,5)if w else(-4,-5))):return 1
    break
   t+=d
 return 0
def gn(b,w,C,E):
 ms=[]
 for s in range(128):
  if s&136:continue
  p=b[s]
  if not p or(p>0)!=w:continue
  a=abs(p)
  if a==1:
   d=16 if w else -16
   t=s+d
   pr=5 if(s>>4)==(6 if w else 1)else 0
   if not t&136 and not b[t]:
    ms.append(s|t<<7|pr<<14)
    if pr:
     for z in(2,3,4):ms.append(s|t<<7|z<<14)
    if(s>>4)==(1 if w else 6):
     t2=s+2*d
     if not b[t2]:ms.append(s|t2<<7)
   for e in(d-1,d+1):
    t=s+e
    if t&136:continue
    q=b[t]
    if(q and(q>0)!=w)or t==E:
     ms.append(s|t<<7|pr<<14)
     if pr:
      for z in(2,3,4):ms.append(s|t<<7|z<<14)
  elif a==2 or a==6:
   for e in(KN if a==2 else KG):
    t=s+e
    if t&136:continue
    q=b[t]
    if not q or(q>0)!=w:ms.append(s|t<<7)
  else:
   for e in(BD if a==3 else RD if a==4 else BD+RD):
    t=s+e
    while not t&136:
     q=b[t]
     if not q:ms.append(s|t<<7)
     else:
      if(q>0)!=w:ms.append(s|t<<7)
      break
     t+=e
 for kf,kt,rb in((4,6,1),(4,2,2),(116,118,4),(116,114,8)):
  if C&rb:
   sg=1 if kt>kf else -1
   rf=kt+1 if sg>0 else kt-2
   if b[kf]!=(6 if kf<16 else -6)or b[rf]!=(4 if kf<16 else -4):continue
   if any(b[x]for x in range(min(kf,rf)+1,max(kf,rf))):continue
   if any(ak(b,kf+i*sg,1 if kf>16 else 0)for i in range(3)):continue
   ms.append(kf|kt<<7)
 return ms
def rr(t,f):
 return(t+1 if t>f else t-2,t-1 if t>f else t+1)
def mk(b,m,w,C,E,K,H):
 f=m&127;t=m>>7&127;pr=m>>14&7
 p=b[f];cap=b[t];ep=0
 h=H^ZSIDE^ZC[C]^(ZE[(E&7)+1] if E>=0 else 0)^ZP[p+6][f]
 if abs(p)==1 and t==E and not cap:
  ep=t-16 if w else t+16;cap=b[ep];b[ep]=0
  h^=ZP[cap+6][ep]
 elif cap:
  h^=ZP[cap+6][t]
 b[t]=p;b[f]=0
 if pr:
  np=pr if w else -pr
  b[t]=np
  h^=ZP[np+6][t]
 else:
  h^=ZP[p+6][t]
 if abs(p)==6 and abs(t-f)==2:
  rf,rt=rr(t,f);b[rt]=b[rf];b[rf]=0
  h^=ZP[b[rt]+6][rf]^ZP[b[rt]+6][rt]
 kw,kb=K
 if abs(p)==6:K[0 if w else 1]=t
 C2=C&CR[f]&CR[t]
 h^=ZC[C2]
 E2=(f+16 if w else f-16)if abs(p)==1 and abs(t-f)==32 else -1
 if E2>=0:h^=ZE[(E2&7)+1]
 return(m,cap,kw,kb,ep),C2,E2,h
def un(b,x,K):
 m,cap,kw,kb,ep=x
 f=m&127;t=m>>7&127;pr=m>>14&7
 v=b[t]
 b[f]=(1 if v>0 else -1)if pr else v
 b[t]=cap if not ep else 0
 if ep:b[ep]=-1 if v>0 else 1
 if abs(v)==6 and abs(t-f)==2:
  rf,rt=rr(t,f);b[rf]=b[rt];b[rt]=0
 K[0]=kw;K[1]=kb
Q=[(ord(c)-58)*5 for s in P for c in s]
def ev(b,w):
 s=0;nb=0;nB=0;qe=0;wk=0;bk=0;wp=[];bp=[];WN=[8]*10;BX=[-1]*10;wr=[];br=[];wn=[];bn=[]
 for i in range(128):
  if i&136:continue
  p=b[i]
  if p:
   a=abs(p);r=i>>4
   if a==1:
    if p>0:
     wp.append(i)
     if r<WN[(i&7)+1]:WN[(i&7)+1]=r
    else:
     bp.append(i)
     if r>BX[(i&7)+1]:BX[(i&7)+1]=r
   if a==2:
    if p>0:wn.append(i)
    else:bn.append(i)
   if a==3:
    if p>0:nb+=1
    else:nB+=1
   if a==4:
    if p>0:wr.append(i)
    else:br.append(i)
   if a==5:qe=1
   if a==6:
    if p>0:wk=i
    else:bk=i
    continue
   v=V[a]+Q[(a-1)*64+((7-r)if p>0 else r)*8+(i&7)]
   s+=v if p>0 else -v
 for i in wp:
  r=i>>4;f=i&7
  if max(BX[f],BX[f+1],BX[f+2])<=r:s+=(r-1)*8
 for i in bp:
  r=i>>4;f=i&7
  if min(WN[f],WN[f+1],WN[f+2])>=r:s-=(6-r)*8
 for k,sg in((wk,1),(bk,-1)):
  r=k>>4;t=6 if not qe else 5
  s+=sg*Q[t*64+((7-r)if sg>0 else r)*8+(k&7)]
 if nb>1:s+=30
 if nB>1:s-=30
 FW=[0]*8;FB=[0]*8
 for i in wp:FW[i&7]+=1
 for i in bp:FB[i&7]+=1
 for f in range(8):
  if FW[f]>1:s-=8*(FW[f]-1)
  if FB[f]>1:s+=8*(FB[f]-1)
  if FW[f] and not(FW[f-1]if f else 0)and not(FW[f+1]if f<7 else 0):s-=8
  if FB[f] and not(FB[f-1]if f else 0)and not(FB[f+1]if f<7 else 0):s+=8
 for i in wr:
  f=i&7
  if not FW[f] and not FB[f]:s+=12
  elif not FW[f]:s+=6
 for i in br:
  f=i&7
  if not FW[f] and not FB[f]:s-=12
  elif not FB[f]:s-=6
 for i in wn:
  r=i>>4;f=i&7
  if r>=4:
   if r==7 or not any(b[(r+1)*16+g]==-1 for g in(f-1,f+1)if 0<=g<8):
    s+=12 if r>0 and any(b[(r-1)*16+g]==1 for g in(f-1,f+1)if 0<=g<8) else 6
 for i in bn:
  r=i>>4;f=i&7
  if r<=3:
   if r==0 or not any(b[(r-1)*16+g]==1 for g in(f-1,f+1)if 0<=g<8):
    s-=12 if r<7 and any(b[(r+1)*16+g]==-1 for g in(f-1,f+1)if 0<=g<8) else 6
 if qe:
  for k,sg in((wk,1),(bk,-1)):
   r=k>>4;f=k&7;sh=3
   if 0<=r+sg<8:
    sh=0
    for g in(f-1,f,f+1):
     if 0<=g<8 and b[(r+sg)*16+g]==(1 if sg>0 else -1):sh+=1
   s-=sg*(3-sh)*10
 return(s if w else -s)+10
def sc(b,m,w,E):
 f=m&127;t=m>>7&127;v=b[t]
 if not v:
  if abs(b[f])==1 and t==E:v=1 if w else -1
  elif not m>>14:return 0
 return 16*V[abs(v)]-V[abs(b[f])]+(900 if m>>14 else 0)
def sr(b,w,d,a,be,C,E,K,pl,z,H):
 N[0]+=1
 if N[0]>B:raise X
 a0=a
 ck=ak(b,K[0 if w else 1],not w)
 if ck and d>0:d+=1
 tt=None
 tm=0
 if tt is not None:
  td,tf,ts,tmv=tt
  if td>=d:
   if tf==0:return ts
   if tf==1 and ts>=be:return be
   if tf==2 and ts<=a:return a
  tm=tmv
 if d<=0 and not ck:
  s=ev(b,w)
  if s>=be:
   if False:TT[H]=(d,1,be,0)
   return be
  if s>a:a=s
 if d>=3 and not ck and not z and ev(b,w)>=be:
  if -sr(b,not w,d-3,-be,-be+1,C,-1,K,pl+1,1,H^ZSIDE^(ZE[(E&7)+1] if E>=0 else 0))>=be:
   if False:TT[H]=(d,1,be,0)
   return be
 if d==1:fs=ev(b,w)
 ms=gn(b,w,C,E)
 ms.sort(key=lambda m:-((1000000 if m==tm else 0)+sc(b,m,w,E)+(500 if m==KL[pl*2] else 250 if m==KL[pl*2+1] else 0)+HH[(b[m&127]+6)*128+(m>>7&127)]))
 best=-30000;bestm=0;lg=0
 for m in ms:
  t=m>>7&127
  if d<=0 and not ck and not sc(b,m,w,E):continue
  if d==1 and not ck and not sc(b,m,w,E) and fs+120<a:continue
  x,C2,E2,H2=mk(b,m,w,C,E,K,H)
  if ak(b,K[0 if w else 1],not w):
   un(b,x,K);continue
  lg+=1
  if d>=3 and lg>3 and not ck and not sc(b,m,w,E):
   s=-sr(b,not w,d-2,-be,-a,C2,E2,K,pl+1,0,H2)
   if s>a:s=-sr(b,not w,d-1,-be,-a,C2,E2,K,pl+1,0,H2)
  else:
   s=-sr(b,not w,d-1,-be,-a,C2,E2,K,pl+1,0,H2)
  un(b,x,K)
  if s>best:best=s;bestm=m
  if s>a:a=s
  if a>=be:
   if not b[t] and not m>>14:
    KL[pl*2+1]=KL[pl*2];KL[pl*2]=m
    HH[(b[m&127]+6)*128+t]+=d*d
   if False and a<28000:TT[H]=(d,1,a,bestm)
   return be
 if not lg:
  if d<=0 and not ck:
   if False:TT[H]=(d,0,a,0)
   return a
  return -29000+pl if ck else 0
 if d<=0:
  if False and a<28000:TT[H]=(d,2 if a<=a0 else 0,a,bestm)
  return a
 if False and -28000<best<28000:TT[H]=(d,2 if best<=a0 else 0,best,bestm)
 return best
def uc(m):
 f=m&127;t=m>>7&127;pr=m>>14&7
 return chr(97+(f&7))+str(1+(f>>4))+chr(97+(t&7))+str(1+(t>>4))+("  nbrq"[pr]if pr else "")
def ps(fen):
 f=fen.split();b=[0]*128;K=[4,116];r=7;c=0
 for ch in f[0]:
  if ch=="/":r-=1;c=0
  elif ch.isdigit():c+=int(ch)
  else:
   i="PNBRQKpnbrqk".index(ch);p=i+1 if i<6 else 5-i;b[r*16+c]=p
   if abs(p)==6:K[0 if p>0 else 1]=r*16+c
   c+=1
 w=f[1]=="w"
 C=("K"in f[2])|(("Q"in f[2])<<1)|(("k"in f[2])<<2)|(("q"in f[2])<<3)
 E=-1 if f[3]=="-" else(ord(f[3][0])-97)+(int(f[3][1])-1)*16
 return b,w,C,E,K
def th(b,w,C,E,K,legal):
 N[0]=0
 TT.clear()
 HH[:]=[0]*(13*128)
 H=fh(b,w,C,E)
 ms=[]
 for s in legal:
  f=(ord(s[0])-97)+(int(s[1])-1)*16
  t=(ord(s[2])-97)+(int(s[3])-1)*16
  pr="nbrq".index(s[4])+2 if len(s)==5 else 0
  ms.append(f|t<<7|pr<<14)
 ms.sort(key=lambda m:-sc(b,m,w,E))
 best=ms[0];d=1
 while d<=12:
  try:
   cur=None;ba=-30000;a=-30000
   for j,m in enumerate(ms):
    x,C2,E2,H2=mk(b,m,w,C,E,K,H)
    if j==0:
     s=-sr(b,not w,d-1,-30000,-a,C2,E2,K,1,0,H2)
    else:
     s=-sr(b,not w,d-1,-a-1,-a,C2,E2,K,1,0,H2)
     if s>a:s=-sr(b,not w,d-1,-30000,-a,C2,E2,K,1,0,H2)
    un(b,x,K)
    if s>ba:ba=s;cur=m
    if s>a:a=s
   best=cur
   if cur in ms:
    ms.remove(cur);ms.insert(0,cur)
  except X:break
  d+=1
 return best
while True:
 g=rq("/game",{})
 if g["status"]=="done":break
 while g["status"]=="your_move":
  b,w,C,E,K=ps(g["fen"])
  g=rq("/move",{"game":g["game"],"move":uc(th(b,w,C,E,K,g["legal_moves"]))})
