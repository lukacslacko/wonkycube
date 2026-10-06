"""Small keyed press-fit samples with the same flats, clearance and ribs."""
from caps import *
from mesh_io import cleaned
from print_3mf import save_3mf
import hashlib

def export_coupons():
 folder=DEST/'stl/fit-coupons';folder.mkdir(parents=True,exist_ok=True)
 records=[];plate=[]
 for j,f in enumerate(['T','S']):
  female,male,directions=keys(f)
  floor=1.4;depth=1.8
  socket=cross(female.buffer(2.0,quad_segs=12)).extrude(floor+depth)-cross(female).extrude(10).translate([0,0,floor])
  plain=cross(male).extrude(7.)
  rib=xform(ribs(f,directions),frame(canonical(f)['direction']).T).translate([0,0,-KEY_BOTTOM[f]])
  peg=plain+rib
  rigid=(plain.translate([0,0,floor])^socket).volume();crush=(peg.translate([0,0,floor])^socket).volume()
  assert rigid<.001 and .025<crush<.10,(f,rigid,crush)
  for role,s in [('socket',socket),('peg',peg)]:
   label=('threefold' if f=='T' else 'fourfold')+'-key-'+role
   m=cleaned(mesh(s));path=folder/(label+'.stl');m.export(path)
   check=trimesh.load(path,force='mesh');assert check.is_watertight and len(check.split())==1 and check.volume>0
   plate.append((label,check,[30+40*j,30+(0 if role=='socket' else 30),0]))
   records.append(dict(file=path.relative_to(DEST).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),family=f,role=role,quantity=1))
 save_3mf(folder/'cap-key-fit-tests.3mf',plate)
 (DEST/'reports/cap-key-coupons.json').write_text(json.dumps(dict(passed=True,rigid_clearance_per_side_mm=KEY_GAP,rib_interference_mm=RIB_INTERFERENCE,receiver_depth_mm=depth,files=records,notes='Print without supports at final layer height. Push the ribbed end of each 7 mm peg into its matching socket. A small hand force should seat it; it should resist falling out and remain removable. This tests the local key fit, not the complete plug fit or gripping force.'),indent=2)+'\n')
 print('CAP FIT COUPONS',len(records),'STLs',flush=True)

if __name__=='__main__':export_coupons()
