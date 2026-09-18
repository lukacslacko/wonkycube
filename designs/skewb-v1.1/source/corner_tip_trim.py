"""Remove the three perforated flange tips from each floating Skewb corner.

The clipping chords open the little holes to the flange perimeter. The broad
retaining lobes between them survive. This is subtraction only, confined to
the inner flange; the exterior and all mating parts retain the v1 geometry.
"""
from skewb_design import *

TIP_CHORD_MM=9.5
TIP_AXIAL_LIMIT_MM=22.0

def tip_cutters(row):
 assert row['family']=='K'
 n=np.asarray(row['direction']);tools=[]
 for i,j in itertools.combinations(row['signature'],2):
  radial=np.cross(AXES[i],AXES[j]);radial/=np.linalg.norm(radial)
  if radial@n<0:radial=-radial
  outward=radial-n*(radial@n);outward/=np.linalg.norm(outward)
  tool=mf.Manifold.cube([160]*3,True).trim_by_plane(outward,TIP_CHORD_MM)
  tools.append(tool.trim_by_plane(-n,-TIP_AXIAL_LIMIT_MM))
 return tools

def trim_corner_tips(s,row):
 return main(subtract(s,tip_cutters(row)))
