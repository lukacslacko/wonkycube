"""Check the localized corner trim and line-width-aware layer connectivity."""
from skewb_design import *
from section_connectivity import check
from finish_skewb import outer_rounded
import sys,zipfile,xml.etree.ElementTree as ET,hashlib
NEW=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
OLD=Path(sys.argv[2]) if len(sys.argv)>2 else None
newmeta=json.loads((NEW/'manifest.json').read_text());b={r['name']:r for r in newmeta['parts']}
a={r['name']:r for r in json.loads((OLD/'manifest.json').read_text())['parts']} if OLD else {}

def read(folder,row):
 m=trimesh.load(folder/row['file'],force='mesh');t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3];return from_mesh(m)
def untrimmed(row):
 base=next(r for r in ROWS if r['family']=='K');q=mapping(base['signature'],row['signature'])
 before=xform(load(CACHE/'ridges-3/K.npz'),q)^xform(mf.Manifold.cube([SIDE]*3,True),R)
 return main(before^(outer_rounded(row)+mf.Manifold.sphere(30,SEG)))

changed=[name for name in a if a[name]['sha256']!=b[name]['sha256']] if OLD else None
if OLD:assert changed==['K01','K02','K03','K04']
report=dict(changed_parts=changed,baseline='previous-release-STL' if OLD else 'untrimmed-CAD',geometry=[],layers=[],scope='Fixed-linewidth geometric opening of layer sections and overlap graph between successive layers; not Bambu G-code or support generation. Layer islands that join the main body higher up remain legitimate supported overhangs.')
for row in (r for r in ROWS if r['family']=='K'):
 name=row['name'];before=untrimmed(row);old=read(OLD,a[name]) if OLD else before;new=read(NEW,b[name]);removed=old-new;added=new-old
 # Check exact locality on pre-export CAD. Two STL exports have slightly
 # different normal-error regularization/quantization along shared surfaces;
 # their tiny difference ribbons are not the intended trimming region.
 after=load(CACHE/'final'/(name+'.npz'));cad_removed=before-after
 assert (after-before).volume()<1e-6
 v=mesh(cad_removed).vertices;n=np.array(row['direction']);rr=np.linalg.norm(v,axis=1)
 assert added.volume()<(.03 if OLD else .25),(name,'added export volume',added.volume())
 assert rr.max()<28 and (v@n).max()<22.001
 report['geometry'].append(dict(name=name,removed_mm3=float(removed.volume()),cad_removed_mm3=float(cad_removed.volume()),added_export_difference_mm3=float(added.volume()),cad_removed_max_radius_mm=float(rr.max()),cad_removed_max_axis_mm=float((v@n).max()),watertight=True,components=1))
 record=b[name];t=np.array(record['mechanism_to_print']);orientations=[('inward-down',xform(new,t[:,:3],t[:,3]))]
 other=next(o for o in newmeta['orientation_options'] if o['name']==name);t=np.array(other['mechanism_to_print']);orientations.append(('face-down',xform(new,t[:,:3],t[:,3])))
 for orientation,s in orientations:
  for layer,width in [(.12,.42),(.16,.40),(.16,.42),(.16,.48),(.20,.42)]:
   groups=check(s,layer,width)
   # Numerically tiny isolated contours are recorded too, not silently dropped.
   detached=sum(g['volume_mm3'] for g in groups[1:]);assert detached<.005,(name,orientation,layer,width,groups)
   item=dict(name=name,orientation=orientation,layer_height_mm=layer,line_width_mm=width,components=groups,detached_volume_mm3=detached)
   report['layers'].append(item);print('LAYER',name,orientation,layer,width,'components',len(groups),'detached',detached,flush=True)
old=read(OLD,a['K01']) if OLD else untrimmed(next(r for r in ROWS if r['name']=='K01'))
t=np.array((a if OLD else b)['K01']['mechanism_to_print']);baseline=check(xform(old,t[:,:3],t[:,3]),.16,.42)
assert len(baseline)>1 and sum(g['volume_mm3'] for g in baseline[1:])>.1
report['old_K01_inward_down_0_16_0_42']=baseline;report['passed']=True
(NEW/'reports/tip-revision.json').write_text(json.dumps(report,indent=2));print('TIP REVISION PASS',flush=True)
