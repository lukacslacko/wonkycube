"""Audit a local, subtract-only ridge revision against v4.1."""
from mechanism_v4p2 import *
from build_v4 import load_parts
from audit_retention_v3 import inspect_parts
from scipy.spatial import cKDTree
import argparse,time

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.time();old=load_parts(args.base);new=load_parts(args.out)
    meta=json.loads((args.out/'reference/design.json').read_text());oldmeta=json.loads((args.base/'reference/design.json').read_text())
    records={r['name']:r for r in meta['parts']};oldrecords={r['name']:r for r in oldmeta['parts']}
    cut,sections=ridge_cutter(old['E12']);ball=mf.Manifold.sphere(33.49,192);rows=[];fail=[]
    for change in meta['radial_ridge_changes']:
        name=change['name'];a=old[name];b=new[name];Q=np.array(change['cutter_rotation'])
        exact=round_radial_ridges(a,Q,cut)
        aa=a^ball;bb=b^ball
        foot_difference=(aa-bb).volume()+(bb-aa).volume()
        error=float(cKDTree(mesh(exact).vertices).query(mesh(b).vertices)[0].max())
        same_transform=records[name]['mechanism_to_print_matrix_3x4']==oldrecords[name]['mechanism_to_print_matrix_3x4']
        pm=trimesh.load(args.out/'parts'/f'{name}.stl',force='mesh',process=True);T=np.array(records[name]['mechanism_to_print_matrix_3x4'])
        transformed=(pm.vertices-T[:,3])@T[:,:3]
        print_error=float(cKDTree(mesh(b).vertices).query(transformed)[0].max())
        row={'edge':name,'changed_volume_in_inner_track_region_mm3':foot_difference,
            'maximum_saved_vertex_distance_to_exact_subtractive_CAD_vertex_mm':error,
            'maximum_print_vertex_distance_to_reference_vertex_mm':print_error,
            'same_print_transform':same_transform,'removed_volume_mm3':change['removed_volume_mm3']}
        row['passed']=bool(error<.005 and print_error<.005 and same_transform)
        if not row['passed']:fail.append('edge '+name)
        rows.append(row);print(row,flush=True)
    unchanged={name:(args.base/'parts'/f'{name}.stl').read_bytes()==(args.out/'parts'/f'{name}.stl').read_bytes() for name in ['core']+[f'C{i:02}' for i in range(1,9)]}
    if not all(unchanged.values()):fail.append('core/corner changed')
    # One replaced edge among old pieces, testing every turn axis.
    p=old.copy();p['E12']=new['E12'];mix=[]
    for a,n in enumerate(AXES):
        moving_names=[f'C{a+1:02}']+[f'E{k+1:02}' for k,pair in enumerate(EDGES) if a in pair]
        names=[f'C{k:02}' for k in range(1,9)]+[f'E{k:02}' for k in range(1,13)]
        moving=union([p[k] for k in moving_names]);fixed=union([p[k] for k in names if k not in moving_names]);peak=0
        for angle in range(0,121,10):peak=max(peak,(xform(moving,Rotation.from_rotvec(n*np.radians(angle)).as_matrix())^fixed).volume())
        mix.append({'corner':a+1,'angle_samples':13,'maximum_outer_overlap_mm3':peak})
        if peak>1e-5:fail.append('single-edge replacement turn '+str(a+1))
    retention=inspect_parts({k:new[k] for k in ['E12','C07','C08','core']},'v4.2 edge with unchanged v4.1 retainers')
    if not retention['principal_all_blocked'] or retention['rocking_escape_paths_found']:fail.append('retention')
    # A small rigid residual-turn probe. Hold C07 at beta and carry the
    # shared E12 with C08 during alpha; no elasticity or cam-driven motion.
    probes=[];names=[f'C{k:02}' for k in range(1,9)]+[f'E{k:02}' for k in range(1,13)]
    active=set(['C08','E08','E11','E12']);previous=set(['C07','E07','E10','E12'])
    for beta in [-2,-1,-.5,.5,1,2]:
        B=Rotation.from_rotvec(AXES[6]*np.radians(beta)).as_matrix()
        for alpha in [-2,-1,-.5,.5,1,2]:
            A=Rotation.from_rotvec(AXES[7]*np.radians(alpha)).as_matrix();values=[]
            for model in [old,new]:
                bodies={k:xform(model[k],(A if k in active else np.eye(3))@(B if k in previous else np.eye(3))) for k in names}
                values.append((union([bodies[k] for k in active])^union([bodies[k] for k in names if k not in active])).volume())
            probes.append({'residual_C07_deg':beta,'C08_motion_deg':alpha,'baseline_overlap_mm3':values[0],'revision_overlap_mm3':values[1]})
            if values[1]>values[0]+.005:fail.append('misalignment collision increased')
    report={'revision':'v4.2','unchanged_part_stl_bytes':unchanged,'edge_changes':rows,'single_edge_mixed_turns':mix,
        'retention':retention,'misalignment_probe':probes,
        'limits':['The radial-ridge fillet is a constant 3 mm circular arc in transverse sections, including the inner track region; no radius taper is used.',
        'The CAD only removes material. Export coordinates are checked within 0.005 mm, far below the fit clearances.',
        'The held-residual-turn probe compares geometric intersection only. It does not predict hand torque or a physical corner-cutting angle.',
        'Retention checks cover specified translations and rocking paths, not every possible escape or deformation.'],
        'passed':not fail,'failures':fail,'seconds':time.time()-start}
    (args.out/'reference/ridge_revision_check.json').write_text(json.dumps(report,indent=2))
    print('DONE',report['passed'],fail,time.time()-start,flush=True)

if __name__=='__main__':main()
