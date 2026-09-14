"""Compare specified edge extraction paths; this is not a load or 6-DOF proof."""
from mechanism_v3 import *
import argparse,time

def load_model(root):
    z=np.load(root/'reference'/'assembly_meshes.npz')
    return {k:from_mesh(trimesh.Trimesh(z[k+'_v'],z[k+'_f'],process=False)) for k in ['E12','C07','C08','core']}

def inspect(root):
    return inspect_parts(load_model(root),root.name)

def inspect_parts(p,model):
    e=p['E12']^mf.Manifold.sphere(37,144)
    a=AXES[7];b=AXES[6];d=(a+b)/np.linalg.norm(a+b)
    principal=[]
    for name,axis,other in [('C08',a,b),('C07',b,a)]:
        for lift in [0,.10,.25]:
            c=p[name].translate(axis*lift)
            for direction,vec in [('radial',d),('own_axis',axis),('other_axis',other)]:
                hits=[];peak=0
                for distance in np.arange(0,8.001,.1):
                    v=(e.translate(vec*distance)^c).volume();peak=max(peak,v)
                    if v>1e-4:hits.append(float(distance))
                principal.append({'retainer':name,'corner_lift_mm':lift,'direction':direction,'first_contact_mm':min(hits) if hits else None,'peak_intersection_mm3':peak})
    # Gentle rocking during an attempted outward pull, with the core present.
    # Rotation ramps up over the first 0.8 mm of pull. Stop at the first contact.
    rocking=[];pivot=d*28
    for lift in [0,.10,.25]:
        fixed=union([p['C08'].translate(a*lift),p['core']])
        for axis_name,rockaxis in [('toward_corners',np.cross(d,[0,0,1])),('sideways',np.array([0,0,1]))]:
            rockaxis=rockaxis/np.linalg.norm(rockaxis)
            for angle in [-10,-5,0,5,10]:
                for direction,vec in [('radial',d),('other_axis',b)]:
                    first=None
                    for distance in np.arange(0,10.001,.1):
                        rot=Rotation.from_rotvec(rockaxis*np.radians(angle)*min(distance/.8,1)).as_matrix()
                        shift=pivot-rot@pivot+vec*distance
                        v=(xform(e,rot,shift)^fixed).volume()
                        if v>1e-4:first=float(distance);break
                    rocking.append({'corner_lift_mm':lift,'rock_axis':axis_name,'final_rock_angle_deg':angle,'pull_direction':direction,'first_contact_mm':first,'collision_free_to_10_mm':first is None})
    return {'model':model,'principal_pulls':principal,'rocking_pulls':rocking,
        'principal_all_blocked':all(row['first_contact_mm'] is not None for row in principal),
        'rocking_escape_paths_found':sum(row['collision_free_to_10_mm'] for row in rocking),
        'scope':'One edge foot and one retainer; rocking paths also include the core. Other edges and corners are omitted. Contacts represent geometric obstruction, not measured force.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'outputs'/'rotated-redi-80mm-v3');ap.add_argument('--baseline',type=Path)
    args=ap.parse_args();t=time.time();report={'v3':inspect(args.out)}
    print('v3',report['v3']['principal_all_blocked'],'rocking escapes',report['v3']['rocking_escape_paths_found'],flush=True)
    if args.baseline:
        report['v2']=inspect(args.baseline)
        print('v2',report['v2']['principal_all_blocked'],'rocking escapes',report['v2']['rocking_escape_paths_found'],flush=True)
    report['seconds']=time.time()-t
    (args.out/'reference'/'retention_audit.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
