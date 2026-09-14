"""Build v4.2 radial-ridge replacement edges, retaining all other v4 parts."""
from mechanism_v4p2 import *
from v3_io import clean_mesh,save_3mf
from build_v4 import load_parts,cube_group
import argparse,shutil,time

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();t=time.time();out=args.out
    for sub in ['parts','plates','calibration','reference','source']:(out/sub).mkdir(parents=True,exist_ok=True)
    base=load_parts(args.base);parts=base.copy();cut,sections=ridge_cutter(base['E12']);group=cube_group()
    meta=json.loads((args.base/'reference/design.json').read_text());records={r['name']:r for r in meta['parts']};changes=[]
    for i,pair in enumerate(EDGES):
        name=f'E{i+1:02}';targets=[AXES[a] for a in pair]
        candidates=[Q for Q in group if all(min(np.linalg.norm(Q@n-v) for v in targets)<1e-7 for n in [AXES[6],AXES[7]])]
        Q=candidates[0];result=round_radial_ridges(base[name],Q,cut)
        m=clean_mesh(mesh(result))
        parts[name]=from_mesh(m)
        row=records[name];T=np.array(row['mechanism_to_print_matrix_3x4']);pm=m.copy();pm.vertices=m.vertices@T[:,:3].T+T[:,3]
        pm=clean_mesh(pm);pm.export(out/'parts'/f'{name}.stl')
        row.update(volume_mm3=float(m.volume),triangles=len(m.faces),print_bounds_mm=pm.bounds.tolist())
        changes.append({'name':name,'cutter_rotation':Q.tolist(),'removed_volume_mm3':base[name].volume()-result.volume()})
        print(name,changes[-1]['removed_volume_mm3'],flush=True)
    for name in ['core']+[f'C{i:02}' for i in range(1,9)]:shutil.copy(args.base/'parts'/f'{name}.stl',out/'parts'/f'{name}.stl')
    for source in (args.base/'calibration').glob('*.stl'):shutil.copy(source,out/'calibration'/source.name)
    for i,edge in enumerate(['E08','E11','E12'],1):
        name=f'test_edge_{i}';s=main_component(parts[edge]^mf.Manifold.sphere(42,288));m=clean_mesh(mesh(s));parts[name]=from_mesh(m)
        center=np.array(s.bounding_box()).reshape(2,3).mean(axis=0);R=Rotation.align_vectors([[0,0,1]],[center/np.linalg.norm(center)])[0].as_matrix()
        pm=m.copy();v=m.vertices@R.T;v[:,2]-=v[:,2].min();pm.vertices=v;pm=clean_mesh(pm);pm.export(out/'calibration'/f'{name}.stl')
        next(r for r in meta['calibration_parts'] if r['name']==name)['print_bounds_mm']=pm.bounds.tolist()
    printed={name:trimesh.load(out/'parts'/f'{name}.stl',force='mesh',process=True) for name in records}
    for start in [1,7]:
        names=[f'E{i:02}' for i in range(start,start+6)]
        save_3mf(out/'plates'/f'edges_{start:02}_to_{start+5:02}.3mf',[(n,printed[n],(64+128*(i%2),44+84*(i//2),0)) for i,n in enumerate(names)])
    save_3mf(out/'plates/comparison_E12.3mf',[('E12_v4p2',printed['E12'],(128,128,0))])
    for start in [1,5]:
        names=[f'C{i:02}' for i in range(start,start+4)]
        save_3mf(out/'plates'/f'corners_{start:02}_to_{start+3:02}.3mf',[(n,printed[n],(64+128*(i%2),64+128*(i//2),0)) for i,n in enumerate(names)])
    save_3mf(out/'plates/core.3mf',[('core',printed['core'],(128,128,0))])
    save_3mf(out/'reference/assembled_reference_DO_NOT_PRINT.3mf',[(name,mesh(parts[name]),(0,0,0)) for name in records])
    data={}
    for name,s in parts.items():
        m=mesh(s);data[name+'_v']=m.vertices;data[name+'_f']=m.faces
    np.savez_compressed(out/'reference/assembly_meshes.npz',**data)
    meta['design']='Wonkycube 80 — v4.2.1 publication export, constant 3 mm radial ridge rounding through the tracks'
    meta['release']='v4.2.1'
    meta['parameters'].pop('radial_ridge_blend_start',None)
    meta['parameters'].pop('radial_ridge_full_round_start',None)
    meta['parameters'].update(radial_ridge_round=RADIAL_RIDGE_ROUND,round_through_track_region=True,radial_radius_taper=False)
    (out/'reference/ridge_sections.json').write_text(json.dumps(sections,indent=2))
    meta['parts']=list(records.values());meta['radial_ridge_changes']=changes
    meta['compatibility']='Only edge-piece radial ridges are cut, including the inner stepped track region. The v4.1 core, corners and hardware remain unchanged. Main exterior face planes and print transforms are retained; there is no protected small-radius band.'
    meta['generation_seconds']=time.time()-t
    (out/'reference/design.json').write_text(json.dumps(meta,indent=2))
    print('DONE',time.time()-t,flush=True)

if __name__=='__main__':main()
