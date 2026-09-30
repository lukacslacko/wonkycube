"""Replacement original double-Ivy core: current tapered DIN985 nut seats."""
from pathlib import Path
import os,json,hashlib
import numpy as np
import manifold3d as mf
import trimesh
from scipy.spatial.transform import Rotation
from print_3mf import save_3mf
HERE=Path(__file__).resolve().parent
DEST=Path(os.environ.get('IVY_CORE_RELEASE',HERE.parent/'release'))
SEG=192
CORE_R=19.2; CORE_PAD=17.6; NUT_ROOF=15.65; ENTRY_AF=5.85
AXES=np.array([[-1,-1,1],[-1,1,-1],[1,-1,-1],[1,1,1]],float)/np.sqrt(3)
def frame(n):
 seed=np.array([0.,0.,1.]);u=np.cross(seed,n);u/=np.linalg.norm(u)
 return np.column_stack([u,np.cross(n,u),n])
def xform(s,q,t=(0,0,0)):return s.transform(np.column_stack([q,t]))
def union(ss):return mf.Manifold.batch_boolean(list(ss),mf.OpType.Add)
def hexagon(af):return mf.CrossSection([[[af/np.sqrt(3)*np.cos(a),af/np.sqrt(3)*np.sin(a)] for a in np.arange(6)*np.pi/3]])
def slot(af):
 h=af/2;e=ENTRY_AF/2
 channel=mf.CrossSection([[[0,-h],[3,-h],[6,-e],[35,-e],[35,e],[6,e],[3,h],[0,h]]])
 return (hexagon(af)+channel).extrude(4.25).translate([0,0,NUT_ROOF-4.25])
def bore():return mf.Manifold.cylinder(80,1.7,1.7,96).translate([0,0,-40])
def envelope():
 s=mf.Manifold.sphere(CORE_R,SEG)
 for n in AXES:s=s.trim_by_plane(-n,-CORE_PAD)
 return s

def core(af):return envelope()-union(xform(slot(af)+bore(),frame(n)) for n in AXES)
def coupon(af):
 return mf.Manifold.cube([24,18,10]).translate([-12,-9,CORE_PAD-10])-slot(af)-bore()
def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
def solid(m):return mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
def write(s,relative,q):
 m=mesh(s);v=m.vertices@q.T;shift=-np.r_[((v.max(0)+v.min(0))/2)[:2],v[:,2].min()];m.vertices=v+shift
 # Only normal float32 STL quantization; reject disconnected exports.
 m.vertices=m.vertices.astype(np.float32).astype(float);m.merge_vertices(digits_vertex=8);m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices()
 p=DEST/relative;p.parent.mkdir(parents=True,exist_ok=True);m.export(p)
 m=trimesh.load(p,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and m.volume>0,relative
 assert abs(m.bounds[0,2])<.005
 return m,dict(file=relative,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mechanism_to_print=np.column_stack([q,shift]).tolist(),dimensions_mm=np.ptp(m.vertices,axis=0).tolist(),volume_mm3=float(m.volume),watertight=True,components=1)
def run():
 (DEST/'plates').mkdir(parents=True,exist_ok=True);(DEST/'reports').mkdir(exist_ok=True)
 records=[];coupons=[]
 q=Rotation.align_vectors([[0,0,-1]],[AXES[0]])[0].as_matrix()
 for af in [5.25,5.20]:
  m,r=write(core(af),f'stl/core-nut-seat-{af:.2f}.stl',q);r.update(kind='core',nut_seat_af_mm=af,recommended=af==5.25);records.append(r)
  save_3mf(DEST/'plates'/f'core-nut-seat-{af:.2f}.3mf',[(f'core-{af:.2f}',m,[128,128,0])])
  m,r=write(coupon(af),f'stl/nut-fit-{af:.2f}.stl',np.eye(3));r.update(kind='coupon',nut_seat_af_mm=af);records.append(r);coupons.append((f'nut-fit-{af:.2f}',m,[108+len(coupons)*40,128,0]))
 save_3mf(DEST/'plates/nut-fit-coupons.3mf',coupons)
 manifest=dict(version='double-ivy-original-core-current-nut-seats-v1',units='millimeter',recommended='stl/core-nut-seat-5.25.stl',core_radius_mm=CORE_R,axle_pad_distance_mm=CORE_PAD,nut_roof_mm=NUT_ROOF,nut_slot_height_mm=4.25,nut_entry_af_mm=ENTRY_AF,tight_channel_length_mm=3.,lead_in_length_mm=3.,screw_bore_diameter_mm=3.4,axes=AXES.tolist(),compatible_outer_packages=['double-Ivy original one-piece-core versions','spherical v6 64 mm','layered spherical v7 72 mm'],hardware='4 DIN912 M3x20, 4 DIN985 M3, 4 washers 9 mm OD x 1 mm',parts=records)
 (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('EXPORT COMPLETE',json.dumps(records),flush=True)
if __name__=='__main__':run()
