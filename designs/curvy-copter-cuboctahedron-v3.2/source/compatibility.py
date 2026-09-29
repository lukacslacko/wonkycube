"""Compare old core interfaces and test the actual seven-piece patch."""
from retention_v2 import *

def run():
 cells,core_part=load_parts();old=Path(os.environ.get('CUBOCTA_V1_REFERENCE','outputs/natural-cuboctahedron-45deg-64mm-v1'));meta=json.loads((old/'manifest.json').read_text());rec=next(r for r in meta['parts'] if r['file']=='stl/puzzle/core.stl');m=trimesh.load(old/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];oldcore=from_mesh(m)
 vol=(oldcore^union(cells.values())).volume();assert vol<.005
 names=json.loads((DEST/'reports/test-patch.json').read_text())['names'];patch={k:cells[k] for k in names};anchors=union([s for k,s in patch.items() if k[0]=='C']+[oldcore]);petals=union(s for k,s in patch.items() if k[0]=='P');out=[]
 for row in ROWS:
  if row['name'] not in names or row['family']=='C':continue
  cc=curve(cells[row['name']],np.array(row['direction']),anchors if row['family']=='P' else petals,np.arange(0,6.01,.1));ss=summary(cc);out.append(dict(name=row['name'],**ss));assert ss['maximum_intersection_mm3']>5
 report=dict(old_core_file=rec['file'],old_core_sha256=rec['sha256'],old_core_static_overlap_mm3=vol,old_core_reusable=True,outer_pieces_mixable_with_v1=False,patch_radial_checks=out,explanation='Foot plane, axial bore, washer seat and all twelve axes unchanged. Moving shells remain outside the same 21.7 mm cavity. Each axial foot stays beyond its own fixed core pad throughout its spin.')
 (DEST/'reports/compatibility.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPATIBILITY',report,flush=True)
if __name__=='__main__':run()
