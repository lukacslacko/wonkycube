"""Regenerate the eight corrected print meshes from archived v7 meshes.
Usage: python regenerate.py /path/to/output-stls
"""
from pathlib import Path
import sys,json,hashlib
from geometry import *
from mesh_io import cleaned
from rounding_tools import tool
HERE=Path(__file__).resolve().parent
PARAMS=json.loads((HERE/'parameters.json').read_text())
RECORDS=json.loads((HERE/'ridge-sections.json').read_text())
def run(destination):
 destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
 tools={f:union(tool(r) for r in RECORDS[f]) for f in 'CF'}
 reports=[]
 for row in PARAMS['parts']:
  name=row['name'];old=load(HERE/'baseline'/(name+'.npz'));q=np.array(row['canonical_to_mechanism'])
  cut=xform(tools[row['family']],q)-mf.Manifold.sphere(32.2,192)
  result=old-cut;chunks=sorted(result.decompose(),key=lambda s:s.volume(),reverse=True)
  assert sum(abs(s.volume()) for s in chunks[1:])<.005
  m=mesh(chunks[0]);T=np.array(row['mechanism_to_print']);m.vertices=m.vertices@T[:,:3].T+T[:,3];m=cleaned(m)
  path=destination/(name+'.stl');m.export(path);re=trimesh.load(path,force='mesh')
  assert re.is_watertight and re.is_winding_consistent and len(re.split())==1
  reports.append(dict(name=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),cleanup=m.metadata.get('cleanup',{})))
  print(name,flush=True)
 (destination/'regeneration-report.json').write_text(json.dumps(reports,indent=2))
if __name__=='__main__':
 run(sys.argv[1] if len(sys.argv)>1 else HERE.parent/'regenerated-stl')
