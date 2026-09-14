"""Build interchangeable v4 outer parts from the supplied v3.1 baseline."""
from mechanism_v4 import *
from v3_io import clean_mesh,save_3mf,write_stl
import argparse,hashlib,shutil,time

HERE=Path(__file__).resolve().parent

def load_parts(root):
    z=np.load(root/'reference/assembly_meshes.npz')
    return {k[:-2]:from_mesh(trimesh.Trimesh(z[k],z[k[:-2]+'_f'],process=False)) for k in z.files if k.endswith('_v')}

def fingerprint(parts):
    h=hashlib.sha256((HERE/'mechanism_v4.py').read_bytes())
    for name in ['C08','E08','E11','E12']:
        m=mesh(parts[name]);h.update(m.vertices.tobytes());h.update(m.faces.tobytes())
    return h.hexdigest()

def canonical(parts):
    key=fingerprint(parts);cache=HERE/'v4-canonical-cache.npz'
    if cache.exists():
        z=np.load(cache)
        if str(z['fingerprint'])==key:
            return {name:from_mesh(trimesh.Trimesh(z[name+'_v'],z[name+'_f'],process=False)) for name in ['C08','E12']}
    ball=mf.Manifold.sphere(INNER_LIMIT,192);cutters=[]
    for name in ['E08','E11','E12']:
        print('sweeping unrounded flange',name,flush=True)
        a,b=EDGES[int(name[1:])-1];other=a if b==7 else b
        cut,_=track_cutter(parts[name]^ball,AXES[other]);cutters.append(cut)
    print('rounding corner',flush=True)
    c=round_inner(widen_corner(parts['C08'],AXES[7],cutters),CORNER_INNER_ROUND,AXES[7])
    print('rounding edge',flush=True)
    e=round_inner(parts['E12'],EDGE_INNER_ROUND)
    data={'fingerprint':key}
    for name,s in [('C08',c),('E12',e)]:
        m=mesh(s);data[name+'_v']=m.vertices;data[name+'_f']=m.faces
    np.savez_compressed(cache,**data)
    return {'C08':c,'E12':e}

def cube_group():
    result=[]
    for p in itertools.permutations(range(3)):
        for signs in itertools.product([-1,1],repeat=3):
            Q=np.eye(3)[list(p)]*np.array(signs)[:,None]
            if np.linalg.det(Q)>.9:result.append(Q)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,default=HERE/'baseline');ap.add_argument('--out',type=Path,default=HERE.parent/'outputs/rotated-redi-80mm-v4')
    args=ap.parse_args();out=args.out.resolve();start=time.time()
    for sub in ['parts','plates','reference','source','calibration']:(out/sub).mkdir(parents=True,exist_ok=True)
    base=load_parts(args.base);canon=canonical(base);parts={};maps=[];group=cube_group()
    ball=mf.Manifold.sphere(INNER_LIMIT,192);compareball=mf.Manifold.sphere(34.5,144)
    for prefix,count,refname in [('C',8,'C08'),('E',12,'E12')]:
        ref=base[refname]^compareball
        for i in range(count):
            name=f'{prefix}{i+1:02}';s=base[name];small=s^compareball
            if prefix=='C':candidates=[Q for Q in group if np.linalg.norm(Q@AXES[7]-AXES[i])<1e-7]
            else:
                a,b=EDGES[i];targets=[AXES[a],AXES[b]]
                candidates=[Q for Q in group if all(min(np.linalg.norm(Q@n-t) for t in targets)<1e-7 for n in [AXES[6],AXES[7]])]
            scores=[]
            for Q in candidates:
                mapped=xform(ref,Q);scores.append((small-mapped).volume()+(mapped-small).volume())
            Q=candidates[int(np.argmin(scores))]
            if min(scores)>1:raise ValueError((name,'unexpected baseline inner asymmetry',min(scores)))
            removable=ball-xform(canon[refname],Q)
            if prefix=='C':removable-=protected_axle(AXES[i])
            parts[name]=main_component(s-removable)
            maps.append({'name':name,'canonical_rotation':Q.tolist(),'baseline_inner_symmetric_difference_mm3':min(scores),'material_removed_mm3':s.volume()-parts[name].volume()})
            print(name,'removed',maps[-1]['material_removed_mm3'],flush=True)
    parts['core']=base['core'];parts['stand']=base['stand']
    meta=json.loads((args.base/'reference/design.json').read_text());records={r['name']:r for r in meta['parts']};packed={};printed={}
    for name,s in parts.items():
        m=clean_mesh(mesh(s));packed[name+'_v']=m.vertices;packed[name+'_f']=m.faces
        if name=='stand':continue
        row=records[name];T=np.array(row['mechanism_to_print_matrix_3x4']);pm=m.copy();pm.vertices=m.vertices@T[:,:3].T+T[:,3]
        pm=clean_mesh(pm);pm.export(out/'parts'/f'{name}.stl');printed[name]=pm
        row.update(volume_mm3=float(m.volume),triangles=len(m.faces),print_bounds_mm=pm.bounds.tolist())
    # Keep the original print orientations, translations and unchanged parts.
    for name in ['core.stl']:
        source=args.base/'parts'/name
        if source.exists():shutil.copy(source,out/'parts'/name)
    for name in ['fit_coupon.stl','assembly_stand.stl']:
        shutil.copy(args.base/'calibration'/name,out/'calibration'/name)
    for plate,names in [('edges_01_to_06',[f'E{i:02}' for i in range(1,7)]),('edges_07_to_12',[f'E{i:02}' for i in range(7,13)]),('corners_01_to_04',[f'C{i:02}' for i in range(1,5)]),('corners_05_to_08',[f'C{i:02}' for i in range(5,9)]),('core',['core'])]:
        objects=[]
        for i,name in enumerate(names):
            y=44+84*(i//2) if plate.startswith('edges') else 64+128*(i//2)
            pos=(128,128,0) if name=='core' else (64+128*(i%2),y,0)
            objects.append((name,printed[name],pos))
        save_3mf(out/'plates'/f'{plate}.3mf',objects)
    save_3mf(out/'plates'/'comparison_C08_E12.3mf',[('C08_v4',printed['C08'],(65,128,0)),('E12_v4',printed['E12'],(190,128,0))])
    save_3mf(out/'reference'/'assembled_reference_DO_NOT_PRINT.3mf',[(name,trimesh.Trimesh(packed[name+'_v'],packed[name+'_f'],process=False),(0,0,0)) for name in records])
    # Rebuild the fixed one-axis bowl with the same widened swept track.
    n=AXES[7];F=frame(n);shell=mf.Manifold.sphere(42,288)
    fixture=(shell-xform(cut_solid_v3(GAP/2,192),F))+parts['core']
    orbit,_=track_cutter(base['E12']^ball,n)
    # The stationary bowl is axisymmetric and has no crossing corner lead-in.
    # Widen its track; the rotor and edge feet use the fully rounded puzzle
    # geometry. Preserve the integral core without a coincident re-union.
    fixture=widen_corner(fixture,n,[orbit])
    fixture=fixture.trim_by_plane(n,-16)
    test={'test_fixture':fixture,'test_rotor':parts['C08']^shell,'test_edge_1':parts['E08']^shell,'test_edge_2':parts['E11']^shell,'test_edge_3':parts['E12']^shell}
    test_records=[]
    for name,s in test.items():
        s=main_component(s);m=clean_mesh(mesh(s));packed[name+'_v']=m.vertices;packed[name+'_f']=m.faces
        oldrow=next(r for r in meta['calibration_parts'] if r['name']==name)
        if name in ['test_fixture','test_rotor']:T=F.T
        else:
            center=np.array(s.bounding_box()).reshape(2,3).mean(axis=0);T=Rotation.align_vectors([[0,0,1]],[center/np.linalg.norm(center)])[0].as_matrix()
        pm=m.copy();v=m.vertices@T.T;v[:,2]-=v[:,2].min();pm.vertices=v;pm=clean_mesh(pm);pm.export(out/'calibration'/f'{name}.stl')
        test_records.append({'name':name,'print_bounds_mm':pm.bounds.tolist()})
    np.savez_compressed(out/'reference/assembly_meshes.npz',**packed)
    meta['design']='Rotated Redi 80 — interchangeable internal rounding and wider tracks v4'
    meta['parameters'].update(side=SIDE,gap_total=GAP,edge_internal_round=EDGE_INNER_ROUND,corner_internal_round=CORNER_INNER_ROUND,track_extra_clearance=TRACK_EXTRA_CLEARANCE,track_total_clearance_from_unrounded_flange=GAP+TRACK_EXTRA_CLEARANCE,internal_edit_limit_radius=INNER_LIMIT)
    meta['parts']=list(records.values());meta['calibration_parts']=test_records;meta['internal_modifications']=maps;meta['generation_seconds']=time.time()-start
    meta['compatibility']='Every revised outer piece is formed by removing material from its v3.1 baseline. Exterior beyond radius 35.5, bearing foot, central stem and washer seat/collar are protected using the corresponding original part.'
    (out/'reference/design.json').write_text(json.dumps(meta,indent=2))
    print('DONE',time.time()-start,flush=True)

if __name__=='__main__':main()
