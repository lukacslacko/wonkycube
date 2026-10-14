"""Generate and verify the full triangular-prism solving guide's algorithms."""
from pathlib import Path
import sys,itertools,json,collections,random
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from move_model import G,SIG,FAMILIES,I,compose,axis,mapped,MOVES,run
MOVES.update(R=MOVES['2'],L=MOVES['1'],B=MOVES['3'])
TOKENS=['U',"U'",'D',"D'",'R','L','B']
INV={x:(x[:-1] if x.endswith("'") else x+"'" if x in 'UD' else x) for x in TOKENS}
def inverse(s):return ' '.join(INV[x] for x in s.split()[::-1])
MAC={'M':"R U' R U",'N':"L U' R U R L D R D' R"}
LABELS={'V':['F','BR','BL'],'H':['RU','LU','BU','RD','LD','BD'],'K':['FU','BRU','BLU','FD','BRD','BLD']}
SIGNATURES={'V':[(0,1),(1,2),(0,2)],'H':[(1,3),(0,3),(2,3),(1,4),(0,4),(2,4)],'K':[(0,1,3),(1,2,3),(0,2,3),(0,1,4),(1,2,4),(0,2,4)],'Cs':[(1,),(0,),(2,)],'Cp':[(3,),(4,)]}
HOMES={fam:[FAMILIES.index(fam)*6+next(j for j,g in enumerate(G) if mapped(SIG[fam],g)==s) for s in sigs] for fam,sigs in SIGNATURES.items()}
def slot(fam,flag):return SIGNATURES[fam].index(mapped(SIG[fam],G[int(flag)%6]))
def perm(p,fam):return tuple(slot(fam,p[h]) for h in HOMES[fam])
def cycle(p,fam):
 q=perm(p,fam);m=[i for i,j in enumerate(q) if i!=j];assert len(m)==3
 a=min(m);return (a,q[a],q[q[a]])
def cyclic_same(a,b):return any(tuple(a)==tuple(b[k:]+b[:k]) for k in range(3))
def table(fam,macro,protected):
 identity=tuple(range(6));seen={identity:''};queue=collections.deque([identity]);rows={}
 while queue:
  q=queue.popleft();s=seen[q];p=run((s+' '+MAC[macro]+' '+inverse(s)).strip())
  assert np.array_equal(p[:protected],I[:protected])
  cyc=cycle(p,fam);support=tuple(sorted(cyc))
  if support not in rows:
   use=macro if cyclic_same(support,cyc) else macro+"'"
   word=MAC[macro] if use==macro else inverse(MAC[macro])
   full=' '.join(t for t in [s,word,inverse(s)] if t)
   pp=run(full);assert cyclic_same(support,cycle(pp,fam))
   rows[support]={'slots':[LABELS[fam][i] for i in support],'setup':s,'use':use,'undo':inverse(s),'full':full}
  for t in TOKENS:
   tm=perm(MOVES[t],fam);n=tuple(tm[i] for i in q)
   if n not in seen:seen[n]=(s+' '+t).strip();queue.append(n)
 assert len(rows)==20
 return [rows[k] for k in sorted(rows)],len(seen)
TABLES={};groups={}
for fam,macro,protected in [('H','M',18),('K','N',24)]:TABLES[fam],groups[fam]=table(fam,macro,protected)
FLIPS={(0,1):'L B L R',(0,2):'R B R L',(1,2):'R L R B'}
SWAPS={(0,1):'R',(0,2):'L',(1,2):'B'}
CENTER={(0,1):'R L R L R L',(0,2):'B R B R B R',(1,2):'L B L B L B'}
def execute(p,s):return run(s)[p]
def early(p):
 words=[]
 def do(s):
  nonlocal p
  p=execute(p,s);words.append(s)
 while perm(p,'V')!=(0,1,2):
  q=perm(p,'V');i=next(i for i in range(3) if q[i]!=i);do(SWAPS[tuple(sorted([i,q[i]]))])
 wrong=tuple(i for i,h in enumerate(HOMES['V']) if p[h]!=h)
 assert len(wrong) in [0,2],wrong
 if wrong:do(FLIPS[wrong])
 assert np.array_equal(p[12:18],I[12:18])
 wrong=tuple(i for i,h in enumerate(HOMES['Cs']) if p[h]!=h)
 assert len(wrong) in [0,2],wrong
 if wrong:do(CENTER[wrong])
 for token,h in zip(['U','D'],HOMES['Cp']):
  if p[h]!=h:
   s=token if execute(p,token)[h]==h else token+"'";do(s)
 assert np.array_equal(p[:18],I[:18])
 return p,words

def wanted_word(fam,cyc):
 names=[LABELS[fam][i] for i in cyc];r=next(r for r in TABLES[fam] if set(r['slots'])==set(names))
 full=r['full']
 if not cyclic_same(names,r['slots']):full=inverse(full)
 return full

def solve_perm(p,fam):
 words=[];loops=0
 while perm(p,fam)!=tuple(range(6)):
  q=perm(p,fam);inv=np.argsort(q);todo=[i for i in range(6) if q[i]!=i]
  large=next((i for i in todo if inv[inv[i]]!=i),None)
  if large is not None:
   a=large;b=int(inv[a]);cc=int(inv[b]);seqs=[(a,b,cc)]
  else:
   a=todo[0];b=int(inv[a]);cc=next(i for i in todo if i not in [a,b]);d=int(inv[cc]);seqs=[(a,b,cc),(a,d,cc)]
  for cyc in seqs:
   s=wanted_word(fam,cyc);p=execute(p,s);words.append(s)
  loops+=1;assert loops<8
 return p,words
# Exact early-phase quotient, including all side-center and V orientations.
seen={tuple(I[np.r_[0:6,12:18]]):I.copy()};queue=collections.deque([I.copy()])
while queue:
 p=queue.popleft();q,_=early(p);assert np.array_equal(q[:18],I[:18])
 for t in ['R','L','B']:
  n=execute(p,t);key=tuple(n[np.r_[0:6,12:18]])
  if key not in seen:seen[key]=n;queue.append(n)
assert len(seen)==96
# Both 360-element even permutations, exhaustive, after earlier phases.
counts={}
for fam in ['H','K']:
 count=0
 for q in itertools.permutations(range(6)):
  if sum(q[i]>q[j] for i in range(6) for j in range(i+1,6))%2:continue
  p=I.copy()
  for i,h in enumerate(HOMES[fam]):p[h]=HOMES[fam][q[i]]
  out,_=solve_perm(p,fam)
  assert perm(out,fam)==tuple(range(6))
  assert np.array_equal(out[:18 if fam=='H' else 24],I[:18 if fam=='H' else 24])
  count+=1
 counts[fam]=count
random.seed(20261014);lengths=[]
for trial in range(1000):
 p=run(' '.join(random.choice(TOKENS) for _ in range(80)))
 p,words=early(p)
 for fam in ['H','K']:
  p,ws=solve_perm(p,fam);words+=ws
 assert np.array_equal(p,I),(trial,p)
 lengths.append(sum(len(s.split()) for s in words))
# Independent check: actual CAD axis vectors, positions and 3D orientation matrices.
sys.path.insert(0,str(ROOT/'designs/triangular-prism-v1/source'))
import conical_design as cad
from scipy.spatial.transform import Rotation
cadmoves={'R':(1,180),'L':(0,180),'B':(2,180),'U':(3,-120),"U'":(3,120),'D':(4,-120),"D'":(4,120)}
lookup={tuple(sorted(r['signature'])):r for r in cad.ROWS}
def geometric(s):
 state={r['name']:(tuple(sorted(r['signature'])),np.eye(3)) for r in cad.ROWS}
 for t in s.split():
  a,ang=cadmoves[t];rot=Rotation.from_rotvec(cad.AXES[a]*np.radians(ang)).as_matrix()
  for name,(sig,ori) in list(state.items()):
   if a in sig:state[name]=(cad.mapped(sig,rot),rot@ori)
 return state
checked=0
for fam in ['H','K']:
 for rec in TABLES[fam]:
  exact=run(rec['full']);state=geometric(rec['full'])
  for row in cad.ROWS:
   f=row['orbit'];sig=tuple(row['signature']);home=SIGNATURES[f].index(sig);flag=HOMES[f][home]
   newflag=int(exact[flag]);expected_sig=mapped(SIG[f],G[newflag%6]);actual_sig,ori=state[row['name']]
   assert actual_sig==expected_sig
   # Each reference flag represents an absolute D3 frame; compare relative frame.
   def gm(g):
    return Rotation.from_euler('z',g[0]*120,degrees=True).as_matrix() @ (np.eye(3) if not g[1] else Rotation.from_euler('x',180,degrees=True).as_matrix())
   expected=gm(G[newflag%6])@gm(G[flag%6]).T
   assert np.max(abs(ori-expected))<1e-12
  checked+=1
validation={'early_phase_states':len(seen),'horizontal_permutations':counts['H'],'corner_permutations':counts['K'],'setup_entries_independently_checked_with_CAD_3D_matrices':checked,'random_scrambles_solved':1000,'scramble_length':80,'max_solution_moves_in_sample':max(lengths),'setup_search_group_sizes':groups}
OUT=Path(__file__).parent/'algorithms.json'
OUT.write_text(json.dumps({'macros':{k:{'word':v,'inverse':inverse(v)} for k,v in MAC.items()},'tables':TABLES,'validation':validation},indent=2))
print(json.dumps(validation,indent=2));print(OUT)
for fam in ['H','K']:
 print(fam)
 for r in TABLES[fam]:print(' > '.join(r['slots']),':',r['setup'] or '-', '|',r['use'],'|',r['undo'] or '-')
