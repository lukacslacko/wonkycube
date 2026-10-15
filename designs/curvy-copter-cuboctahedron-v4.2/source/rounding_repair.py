"""Complete both halves of the saved radial circular fillets."""
from design import *
def tool(rec):
 rings=[];fixed=0
 for row in rec['sections']:
  x=row['station_mm'];cy,cz=row['center'];lo,hi=row['angles'];r=row['radius_mm']
  assert abs(cz)<1e-8
  a=max(abs(lo),abs(hi));fixed+=abs(lo+hi)>1e-3
  theta=np.linspace(-a,a,65)
  arc=np.column_stack([cy-r*np.cos(theta),cz+r*np.sin(theta)])
  yz=np.vstack([[-100,cz],[-100,arc[0,1]],arc,[-100,arc[-1,1]]])
  rings.append(np.column_stack([yz,np.full(len(yz),x)]))
 n=len(rings[0]);faces=[]
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;faces.extend([[a,b,a+n],[b,b+n,a+n]])
 for j in range(1,n-1):
  faces.append([0,j+1,j]);a=(len(rings)-1)*n;faces.append([a,a+j,a+j+1])
 m=trimesh.Trimesh(np.vstack(rings),np.array(faces),process=True)
 if m.volume<0:m.invert()
 assert m.is_watertight and m.is_winding_consistent
 return xform(from_mesh(m),np.array(rec['frame']).T),fixed
def repair(s,f):
 records=json.loads((HERE/'rounding-reference'/(f+'-sections.json')).read_text());tools=[];stats=[]
 for rec in records:
  # The center's four mixed-side corners are shifted by the neck profile
  # and have their own complete R1.2 outline fillets. They are not symmetric
  # R2 edges; do not apply this symmetry repair to those different corners.
  if f=='C' and canonical('C')['signature'][0] in rec['axes']:continue
  t,count=tool(rec);tools.append(t.as_original().simplify(.001));stats.append(dict(axes=rec['axes'],corrected_sections=count))
 raw=subtract(s,tools);cs=sorted(raw.decompose(),key=lambda c:c.volume(),reverse=True);assert sum(abs(c.volume()) for c in cs[1:])<.1
 fixed=cs[0];removed=s-fixed;save(removed,CACHE/f'rounding-removed-{f}.npz')
 save(fixed,CACHE/f'rounded-{f}.npz')
 print('ROUND REPAIR',f,'removed',removed.volume(),'dust',[c.volume() for c in cs[1:]],flush=True)
 save(union(tools),CACHE/f'rounding-tool-{f}.npz')
 return fixed,dict(family=f,removed_volume_mm3=removed.volume(),corrected_edges=stats)
if __name__=='__main__':
 from prepare import prepare
 prepare()
