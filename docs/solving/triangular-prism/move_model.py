"""Exact oriented D3 action of the supplied triangular-prism design."""
import itertools
import numpy as np
N=3; G=list(itertools.product(range(N),range(2)))
SIG={'Cs':(0,),'Cp':(N,),'V':(0,1),'H':(0,N),'K':(0,1,N)}
FAMILIES=list(SIG);I=np.arange(5*2*N)
def compose(q,g):return ((q[0]+(-1)**q[1]*g[0])%N,q[1]^g[1])
def axis(g,i):return (g[0]+(-1)**g[1]*i)%N if i<N else N+((i-N)^g[1])
def mapped(sig,g):return tuple(sorted(axis(g,i) for i in sig))
def move(a,power=1):
 q=((2*a)%N,1) if a<N else ((-power if a==N else power)%N,0)
 return np.array([f*2*N+G.index(compose(q,g)) if a in mapped(SIG[family],g) else f*2*N+j for f,family in enumerate(FAMILIES) for j,g in enumerate(G)])
MOVES={**{str(i+1):move(i) for i in range(N)},'U':move(N),"U'":move(N,-1),'D':move(N+1),"D'":move(N+1,-1)}
def run(seq):
 p=I.copy()
 for t in seq.split():p=MOVES[t][p]
 return p
pairs=sorted({tuple(sorted([k,(k+1)%N])) for k in range(N)})
K={(*pair,pol):f'K{i*2+j+1:02}' for i,pair in enumerate(pairs) for j,pol in enumerate([N,N+1])}
def label(i):
 f,g=divmod(int(i),2*N);fam=FAMILIES[f];sig=mapped(SIG[fam],G[g])
 return K[sig] if fam=='K' else fam+str(sig)+str(G[g])
def cycles(p):
 used=set();out=[]
 for i in I:
  if i in used or p[i]==i:continue
  cycle=[];j=i
  while j not in used:used.add(j);cycle.append(label(j));j=p[j]
  out.append(cycle)
 return out
if __name__=='__main__':
 for a,b in itertools.permutations(['1','2','3'],2):
  seq=f'U {a} U\' {b} U {a} U\' {b}'
  p=run(seq);print(seq,cycles(p),'protected',np.array_equal(p[:24],I[:24]))
