"""Seven actual puzzle pieces on one plate, for testing on the old core."""
from hardware import *
from print_3mf import save_3mf
import mesh_render as mr
from PIL import Image,ImageDraw
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def run():
 meta=json.loads((DEST/'manifest.json').read_text());base={};printed={}
 for r in meta['parts']:
  if '/puzzle/' not in r['file']:continue
  m=trimesh.load(DEST/r['file'],force='mesh');printed[r['family']]=m.copy();T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];base[r['family']]=m
 kr=canonical('K');sig=set(kr['signature']);selected=[r for r in ROWS if set(r['signature'])<=sig];assert len(selected)==7
 (DEST/'start-here').mkdir(exist_ok=True);objects=[];x=18.;y=16.;height=0
 for row in sorted(selected,key=lambda r:r['family']):
  m=printed[row['family']];w,h=np.ptp(m.vertices,axis=0)[:2]
  if x+w>240:x=18.;y+=height+14;height=0
  assert y+h<240
  objects.append((row['name'],m,[x+w/2,y+h/2,0]));x+=w+14;height=max(height,h)
 save_3mf(DEST/'start-here/retention-test-7-pieces.3mf',objects)
 save_3mf(DEST/'start-here/upgrade-test-6-pieces.3mf',[o for o in objects if not o[0].startswith('K')])
 save_3mf(DEST/'start-here/centers-only-test-3-pieces.3mf',[o for o in objects if o[0].startswith('C')])
 objects_c=[];x=18.;y=16.;height=0
 for row in [r for r in ROWS if r['family']=='C']:
  m=printed['C'];w,h=np.ptp(m.vertices,axis=0)[:2]
  if x+w>240:x=18.;y+=height+14;height=0
  assert y+h<240
  objects_c.append((row['name'],m,[x+w/2,y+h/2,0]));x+=w+14;height=max(height,h)
 save_3mf(DEST/'start-here/centers-only-full-12-pieces.3mf',objects_c)
 mr.meshes['core']=base['core'];draw=[('core',np.eye(3),np.zeros(3),'#84939d')];assembly=[('core',base['core'],[0,0,0])];colors={'C':'#72ad9a','P':'#70a5d1','K':'#e7b75e'}
 for row in selected:
  m=base[row['family']].copy();q=mapping(canonical(row['family'])['signature'],row['signature']);m.vertices=m.vertices@q.T;mr.meshes[row['name']]=m;draw.append((row['name'],np.eye(3),np.zeros(3),colors[row['family']]));assembly.append((row['name'],m,[0,0,0]))
 save_3mf(DEST/'start-here/DO-NOT-PRINT-test-assembly.3mf',assembly)
 n=np.array(kr['direction']);el=np.degrees(np.arcsin(n[2]));az=np.degrees(np.arctan2(n[1],n[0]));im=mr.render(draw,size=850,extent=44,elev=el+12,az=az+15);im.save(DEST/'images/retention-test-patch.png')
 text=['# Start with this retention patch','',
 'Print `retention-test-7-pieces.3mf`: three centers, three petals and one corner. These are the exact full-puzzle STLs, so they count toward the complete print if the test succeeds. The file contains geometry and placement, not Bambu slicing settings.','',
 'Reuse the **old 64 mm vertex-turning cuboctahedron core**, three M3×20 DIN912 screws, three 9×1 mm washers and three installed DIN985 nuts. The new body is 72 mm, but its core mounts are unchanged. Reuse spherical-v3 or v3.1 floating corners freely. Petals should be the accepted v3.1 design; previous cylindrical-retention parts are not compatible.','',
 'The reference assembly is for viewing, not printing. The other named print plates are also printable; never print the assembled reference.','',
 '| Family | Actual locations |','|---|---|']
 for f in ['C','P','K']:text.append('| '+f+' | '+', '.join(r['name'] for r in selected if r['family']==f)+' |')
 text+=['','1. Use the reference to position the corner, petals and centers. Keep centers absent or loose while manipulating the floating pieces. The complete spherical shoulders were not trimmed for straight insertion, and the insertion sequence is unverified by agreement with the user.','2. Once interlocked, install the three screws and washers. Seat gently; do not use the screws to force a blocked part past a shoulder.','3. Remove the temporary tape. With the centers seated, the three petals and the corner should stay captured when the patch is lifted or turned over. Gently tug each outward and rock it a little.','4. Back the center screws off only enough for the parts to move without binding. Confirm the loose parts remain captured with that setting.','5. If a petal or corner still comes out readily, stop before printing the rest and report which part and direction. This is a physical test of the new geometry, not a promise of pop resistance.','',
 'This open patch is a **retention fixture**, not a complete turning puzzle. Do not try full turns on it: missing neighboring sectors do not provide the normal transfer of support. No destructive pull force is prescribed.','',
 'After a satisfactory test, print the remaining **9 centers, 21 petals and 7 corners**. The three full-set plates include the test pieces again; remove those copies if you use the plates.']
 text+=['','## Reusing your spherical-v3 test pieces','','`upgrade-test-6-pieces.3mf` contains the three revised centers and three revised petals only. Reuse the old core and the previously printed K01 corner. The corner and core STLs are unchanged; the revised centers/petals work with them. For a full upgrade, replace all twelve centers and twenty-four petals.']
 text+=['','## Center-only correction from v3.1','','`centers-only-test-3-pieces.3mf` contains the three corrected centers for the existing patch. `centers-only-full-12-pieces.3mf` contains all twelve centers without a core or floating pieces. v3.1 petals, floating corners and core are unchanged byte for byte. Only the center files changed in v3.2.']
 (DEST/'start-here/README.md').write_text('\n'.join(text)+'\n')
 (DEST/'reports/test-patch.json').write_text(json.dumps(dict(names=[r['name'] for r in selected],actual_puzzle_parts=True,reuses_old_core=True,quantity=7,bed_inside_256mm=True),indent=2)+'\n')
 print('TEST PATCH', [r['name'] for r in selected],flush=True)
if __name__=='__main__':run()
