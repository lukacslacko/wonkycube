"""Copy a complete v7.1 package and rebuild its plates from its manifest/STLs."""
from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np,trimesh
from print_3mf import save_3mf

def run(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination==source or source in destination.parents:raise ValueError('Use a new destination outside the source package.')
 shutil.copytree(source,destination,ignore=shutil.ignore_patterns('__pycache__','*.pyc','build','.venv'))
 meta=json.loads((destination/'manifest.json').read_text());R=np.array(json.loads((destination/'reference/cube-to-mechanism.json').read_text()));assembly=[]
 for plate in meta['plates']:
  x=y=14.;height=0.;items=[];rects=[]
  rows=[next(r for r in meta['parts'] if r['name']==n) for n in plate['objects']]
  for row in rows:
   path=destination/row['file'];m=trimesh.load(path,force='mesh')
   assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
   row.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),volume_mm3=float(m.volume),triangles=len(m.faces),dimensions_mm=np.ptp(m.vertices,axis=0).tolist())
   w,h=np.ptp(m.vertices,axis=0)[:2]
   if x+w>242:x=14.;y+=height+10;height=0.
   assert y+h<242
   offset=[x-m.bounds[0,0],y-m.bounds[0,1],0.];items.append((row['name'],m,offset));rects.append((row['name'],x,y,w,h));x+=w+10;height=max(height,h)
   T=np.array(row['mechanism_to_print']);solved=m.copy();solved.vertices=((m.vertices-T[:,3])@T[:,:3])@R;assembly.append((row['name'],solved,[0,0,0]))
  save_3mf(destination/plate['file'],items)
  svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="#fafaf8"/>']
  for n,x,y,w,h in rects:svg.append(f'<rect x="{x}" y="{256-y-h}" width="{w}" height="{h}" fill="#dceaf1" stroke="#597383"/><text x="{x+w/2}" y="{256-y-h/2}" text-anchor="middle" font-size="4">{n}</text>')
  (destination/'plates'/(plate['name']+'-map.svg')).write_text(''.join(svg)+'</svg>')
 save_3mf(destination/'reference/DO-NOT-PRINT-solved.3mf',assembly)
 (destination/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
 # Rebuilt geometry must receive its own validation; old reports retain their
 # recorded hashes and are reference evidence, not results of this repacking.
 for name in ['SHA256SUMS.txt','publication.json']:
  p=destination/name
  if p.exists():p.unlink()
 (destination/'REPACKED.txt').write_text('Plates rebuilt from this package. Rerun geometry and publication checks before distribution. Archived reports retain their original scope and hashes.\n')
 files=sorted(p for p in destination.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 (destination/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(destination).as_posix()+'\n' for p in files))
 print(destination)
if __name__=='__main__':run(sys.argv[1],sys.argv[2])
