"""Recesses and 1:1 foam outlines, derived from the finished printable solids.

All dimensions are millimetres. Pocket walls grip compressible 2 mm foam;
there is no rigid snap undercut. A thin glue layer is permitted by the depth.
"""
from design import *
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
import shapely

THICKNESS=2.0
DEPTH=2.1
RIM=1.0
FLOOR_WEB=1.2
WALL=.8
FOAM_GROWTH=.04
CORNER_RADIUS=.45
BETWEEN_POCKETS=1.6

def polygons(p):
 if p.is_empty:return []
 if isinstance(p,Polygon):return [p]
 return [a for g in p.geoms for a in polygons(g)]

def region(section):
 out=GeometryCollection()
 for pts in section.to_polygons():
  if len(pts)>=3:out=out.symmetric_difference(Polygon(pts).buffer(0))
 return out

def cross(p):
 contours=[]
 for g in polygons(p):
  contours.append(np.array(g.exterior.coords)[:-1])
  contours.extend(np.array(a.coords)[:-1] for a in g.interiors)
 return mf.CrossSection(contours,mf.FillRule.EvenOdd)

def coords(p):
 return dict(outer=np.array(p.exterior.coords)[:-1].tolist(),holes=[np.array(a.coords)[:-1].tolist() for a in p.interiors])

def polygon(rec):return Polygon(rec['outer'],rec.get('holes',[]))

def fitted(rec):
 """Compressed seated foam envelope; 0.1 mm below plastic before glue."""
 p=polygon(rec['pocket']).buffer(-.005)
 return xform(cross(p).extrude(THICKNESS).translate([0,0,FACE_HEIGHT-DEPTH]),np.array(rec['frame']))

def pockets():
 records=[];stats=[]
 for family in ORBITS:
  basepath=CACHE/f'bare-{family}.npz'
  if not basepath.exists():save(load(CACHE/f'final-{family}.npz'),basepath)
  base=load(basepath);cuts=[];tests=[];webs=[];voids=[]
  # Triangulated fillets have tiny directional differences. Intersect the
  # rotational stabilizer copies, then make the pockets from one repeated
  # template so a center's complete geometry has exact turn symmetry.
  stabilizer=[q for q in GROUP if mapped(canonical(family)['signature'],q)==tuple(canonical(family)['signature'])]
  if family!='P':
   base=mf.Manifold.batch_boolean([xform(base,q) for q in stabilizer],mf.OpType.Intersect)
  seed=None
  for n,h,label in FACES:
   F=frame(n);local=xform(base,F.T)
   top=region(local.slice(h-.005))
   if top.area<10:continue
   candidate=top.buffer(-RIM,quad_segs=12)
   # Leave a continuous floor and a lateral web throughout the pocket depth.
   # Slices are supplemented by an exact solid containment test below.
   for z in np.linspace(h-.04,h-DEPTH-FLOOR_WEB,18):
    candidate=candidate.intersection(region(local.slice(z)).buffer(-WALL,quad_segs=12))
   # Keep each recess on its own side of every exterior-face bisector.
   # At full depth, facing pockets then leave a continuous plastic spine.
   for other,_,_ in FACES:
    delta=n-other;length=np.linalg.norm(delta)
    if length<1e-7:continue
    a=F[:,:2].T@delta;aa=np.linalg.norm(a)
    if aa<1e-7:continue
    rhs=BETWEEN_POCKETS/2*length-(h-DEPTH)*(delta@n)
    u=a/aa;v=np.array([-u[1],u[0]]);anchor=u*(rhs/aa)
    halfplane=Polygon([anchor-v*200,anchor+v*200,anchor+v*200+u*400,anchor-v*200+u*400])
    candidate=candidate.intersection(halfplane)
   candidate=candidate.buffer(-CORNER_RADIUS,quad_segs=12).buffer(CORNER_RADIUS,quad_segs=12).simplify(.008,preserve_topology=True)
   if family!='P':
    if seed is None:seed=(F,candidate)
    else:
     initial,pg=seed;q=next(q for q in stabilizer if np.linalg.norm(q@initial[:,2]-n)<1e-7)
     transform=F[:,:2].T@q@initial[:,:2]
     candidate=unary_union([Polygon(np.array(p.exterior.coords)@transform.T,[np.array(a.coords)@transform.T for a in p.interiors]) for p in polygons(pg)])
   for j,p in enumerate(polygons(candidate)):
    if p.area<15:continue
    assert not p.interiors,('inlay has a hole',family,label)
    # The complete floor-and-side-web envelope must fit, not just sample slices.
    web=cross(p.buffer(WALL-.025,quad_segs=12)).extrude(DEPTH+FLOOR_WEB-.05).translate([0,0,h-DEPTH-FLOOR_WEB])
    missing=(web-local).volume()
    assert missing<.003,('floor/wall envelope escapes solid',family,label,missing)
    cutter=cross(p).extrude(DEPTH+1).translate([0,0,h-DEPTH])
    webs.append(xform(web,F))
    voids.append(xform(cross(p).extrude(DEPTH).translate([0,0,h-DEPTH]),F))
    cuts.append(xform(cutter,F));key=f'{family}-{label}'+(f'-{j+1}' if j else '')
    foam=p.buffer(FOAM_GROWTH,quad_segs=12).simplify(.008,preserve_topology=True)
    records.append(dict(id=key,family=family,canonical_face=label,frame=F.tolist(),pocket=coords(p),cut=coords(foam),quantity=sum(r['family']==family for r in ROWS),area_mm2=p.area))
    tests.append(dict(id=key,area_mm2=p.area,minimum_floor_web_design_mm=FLOOR_WEB,minimum_lateral_web_design_mm=WALL-.025,containment_error_mm3=missing))
  assert len(cuts)=={'T':3,'S':4,'P':2}[family],('missing inlay pockets',family,len(cuts))
  gaps=[]
  for i,web in enumerate(webs):
   intrusion=(web^union([c for j,c in enumerate(cuts) if i!=j])).volume()
   assert intrusion<.003,('another pocket cuts a floor or wall envelope',family,i,intrusion)
   tests[i]['other_pockets_in_web_mm3']=intrusion
  for i,j in itertools.combinations(range(len(voids)),2):
   gap=voids[i].min_gap(voids[j],5.)
   assert gap>BETWEEN_POCKETS-.02,('thin plastic between adjacent inlays',family,i,j,gap)
   gaps.append(dict(pockets=[tests[i]['id'],tests[j]['id']],minimum_gap_mm=gap,search_limit_mm=5.))
  carved=subtract(base,cuts)
  fragments=sorted(carved.decompose(),key=lambda c:c.volume(),reverse=True)
  tiny=sum(abs(c.volume()) for c in fragments[1:])
  assert tiny<.01,('detached pocket material',family,tiny)
  final=fragments[0]
  assert final.volume()>.7*base.volume()
  save(final,CACHE/f'final-{family}.npz')
  save(final,CACHE/f'pocketed-{family}.npz')
  stats.append(dict(family=family,recesses=len(cuts),removed_volume_mm3=base.volume()-final.volume(),discarded_boolean_dust_mm3=tiny,checks=tests,between_pockets=gaps))
  print('INLAYS',family,len(cuts),'removed',round(base.volume()-final.volume(),2),flush=True)
 (CACHE/'inlays.json').write_text(json.dumps(dict(thickness_mm=THICKNESS,recess_depth_mm=DEPTH,nominal_rim_mm=RIM,minimum_between_pockets_mm=BETWEEN_POCKETS,foam_compression_per_side_mm=FOAM_GROWTH,records=records,checks=stats),indent=2)+'\n')

if __name__=='__main__':pockets()
