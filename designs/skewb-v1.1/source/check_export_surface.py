"""Export fidelity after regularization; record CAD regularization separately."""
from skewb_design import *
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
META=json.loads((DEST/'manifest.json').read_text());out=[]
for row in META['parts']:
 name=row['name']
 if name not in [r['name'] for r in ROWS]:continue
 m=trimesh.load(DEST/row['file'],force='mesh');t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 raw=load(CACHE/'final'/(name+'.npz'));regular=raw.simplify(.001);original=mesh(regular)
 removed=float((raw-regular).volume());added=float((regular-raw).volume())
 # The documented normal-error simplification removes nearly zero-thickness
 # CSG whiskers. Their tips can move farther than the normal tolerance.
 # Report that operation separately from STL conversion; do not interpret
 # .001 mm as a bound on every vertex's movement. Final mesh motion,
 # retention and circle profiles are checked independently.
 assert removed<.25 and added<.25,(name,removed,added)
 measurements=[]
 for source,target in [(original,m),(m,original)]:
  points=np.vstack([source.vertices[np.linspace(0,len(source.vertices)-1,min(5000,len(source.vertices))).astype(int)],source.triangles_center[np.linspace(0,len(source.faces)-1,min(3000,len(source.faces))).astype(int)]])
  distances=[]
  for start in range(0,len(points),500):distances.extend(trimesh.proximity.closest_point(target,points[start:start+500])[1])
  d=np.array(distances);assert d.max()<.015,(name,d.max())
  measurements.append(dict(samples=len(d),maximum_mm=float(d.max()),rms_mm=float(np.sqrt(np.mean(d*d)))))
 out.append(dict(name=name,regularization_removed_mm3=removed,regularization_added_mm3=added,regularized_cad_to_print=measurements[0],print_to_regularized_cad=measurements[1]));print(name,measurements,flush=True)
(DEST/'reports/export-surface.json').write_text(json.dumps(dict(passed=True,parts=out,scope='Bidirectional vertex and face-center samples against the .001 mm normal-error regularized export input, not an exact Hausdorff bound or a vertex-movement bound on CAD regularization. Original-CAD versus print ridge profiles are checked separately.'),indent=2))
