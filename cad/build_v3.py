"""Build the complete 80 mm rounded prototype with square retaining shoulders print set.

Usage: python build_v3.py [--out PATH] [--pilot 2.6]
"""
from mechanism_v3 import *
from v3_io import clean_mesh, write_stl, print_orient, save_3mf, label_shape
import argparse, shutil, time, hashlib

HERE=Path(__file__).resolve().parent

def v3_stand():
    # A gravity-supported assembly jig avoids a deeply recessed screw that
    # would need a long bare bit. The peg enters the vacant C01 pilot hole.
    base=mf.Manifold.cylinder(4,32,32,128)
    body=mf.Manifold.cylinder(32,8,8,96)
    taper=mf.Manifold.cylinder(4,8,3.4,96).translate([0,0,32])
    neck=mf.Manifold.cylinder(34,3.4,3.4,96).translate([0,0,36])
    peg=union([mf.Manifold.cylinder(2.7,1.1,1.1,96),mf.Manifold.cylinder(.3,1.1,.8,96).translate([0,0,2.7])]).translate([0,0,70])
    return union([base,body,taper,neck,peg])

def coupon():
    s=mf.Manifold.cube([90,51,12])
    n=np.array([0,np.sqrt(2),1])/np.sqrt(3)
    for i,d in enumerate([2.4,2.5,2.6,2.7,2.8]):
        x=12+16*i
        bore=mf.Manifold.cylinder(80,d/2,d/2,96).translate([0,0,-40])
        s-=xform(bore,frame(n),[x,30,12])
        s-=label_shape(f'{d:.1f}').translate([x-3,41,11.5])
    for i,d in enumerate([3.2,3.3,3.4]):
        x=12+18*i
        s-=mf.Manifold.cylinder(14,d/2,d/2,96).translate([x,12,-1])
        s-=label_shape(f'{d:.1f}').translate([x-3,3,11.5])
    s-=mf.Manifold.cylinder(2,ACCESS_D/2,ACCESS_D/2,192).translate([75,12,10.5])
    s-=mf.Manifold.cylinder(14,SCREW_BORE_D/2,SCREW_BORE_D/2,96).translate([75,12,-1])
    s-=label_shape('13.8').translate([70,3,11.5])
    return s

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE.parent/'outputs'/'rotated-redi-80mm-v3p1')
    parser.add_argument('--pilot',type=float,default=PILOT_D)
    args=parser.parse_args();out=args.out.resolve();start=time.time()
    if not 2.3<=args.pilot<=2.9: raise ValueError('Pilot must be between 2.3 and 2.9 mm')
    for sub in ['parts','calibration','plates','reference','source']:(out/sub).mkdir(parents=True,exist_ok=True)
    data=json.loads((HERE/'chosen_rotation.json').read_text());R=np.array(data['cube_to_mechanism_matrix'])
    cube,cs,es=build_cells_v3(R,192)
    cs,removed=assembly_relief_v3(cs,es,192)
    cs=finish_corners_v3(cs)
    cr=poc_core(args.pilot,288,print_flat=False)
    parts={};kinds={}
    for prefix,kind,ss in [('C','corner',cs),('E','edge',es)]:
        for i,s in enumerate(ss):
            name=f'{prefix}{i+1:02}'
            parts[name]=s.simplify(.008);kinds[name]=kind
    # Opposite pieces are exact inversion partners. Round each pair once.
    for prefix,count in [('C',8),('E',12)]:
        for i in range(count//2):
            name=f'{prefix}{i+1:02}'
            print('rounding',name,flush=True)
            original=parts[name]
            m0=mesh(original)
            fingerprint=hashlib.sha256(m0.vertices.tobytes()+m0.faces.tobytes()+(HERE/'mechanism_v3.py').read_bytes()).hexdigest()[:20]
            cache=HERE/'v3_round_cache';cache.mkdir(exist_ok=True)
            cachefile=cache/f'{name}-{fingerprint}.npz'
            if cachefile.exists():
                with np.load(cachefile) as z:rounded=from_mesh(trimesh.Trimesh(z['v'],z['f'],process=False))
            else:
                rounded=round_exterior(original)
                mm=mesh(rounded);np.savez_compressed(cachefile,v=mm.vertices,f=mm.faces)
            parts[name]=rounded
            parts[f'{prefix}{count-i:02}']=xform(rounded,-np.eye(3))
    cs=[parts[f'C{i:02}'] for i in range(1,9)]
    es=[parts[f'E{i:02}'] for i in range(1,13)]
    parts['core']=cr.simplify(.008);kinds['core']='core'
    packed={};records=[];printed={};display=[]
    def pack(name,s):
        m=clean_mesh(mesh(s));packed[name+'_v']=m.vertices;packed[name+'_f']=m.faces
        return m
    for name,s in parts.items():
        assert len(s.decompose())==1,(name,'disconnected')
        m=pack(name,s);pm,T=print_orient(s,kinds[name],R)
        pm.export(out/'parts'/f'{name}.stl');printed[name]=pm
        records.append({'name':name,'kind':kinds[name],'quantity':1,'volume_mm3':float(m.volume),
            'triangles':len(m.faces),'mechanism_to_print_matrix_3x4':T,'print_bounds_mm':pm.bounds.tolist()})
        display.append((name,m,(0,0,0)))
        print(name,'faces',len(m.faces),'volume',round(m.volume),flush=True)
    save_3mf(out/'reference'/'assembled_reference_DO_NOT_PRINT.3mf',display)
    for plate,names in [('edges_01_to_06',[f'E{i:02}' for i in range(1,7)]),('edges_07_to_12',[f'E{i:02}' for i in range(7,13)]),('corners_01_to_04',[f'C{i:02}' for i in range(1,5)]),('corners_05_to_08',[f'C{i:02}' for i in range(5,9)])]:
        objects=[]
        for i,name in enumerate(names):
            pm=printed[name]
            limit=np.array([112,72] if plate.startswith('edges') else [112,112])
            assert (pm.extents[:2]<limit).all(),(name,pm.extents)
            y=44+84*(i//2) if plate.startswith('edges') else 64+128*(i//2)
            objects.append((name,pm,(64+128*(i%2),y,0)))
        save_3mf(out/'plates'/f'{plate}.3mf',objects)
    save_3mf(out/'plates'/'core.3mf',[('core',printed['core'],(128,128,0))])
    st=v3_stand();write_stl(st,out/'calibration'/'assembly_stand.stl');pack('stand',st)
    write_stl(coupon(),out/'calibration'/'fit_coupon.stl')
    # The fixture is the same true mechanism with a smaller spherical exterior.
    n=AXES[7];F=frame(n);ball=mf.Manifold.sphere(42,288)
    large=xform(cut_solid_v3(GAP/2,192),F)
    fixture=union([ball-large,cr]).trim_by_plane(n,-16)
    test={'test_fixture':fixture,'test_rotor':cs[7]^ball}
    for pair,e in zip(EDGES,es):
        if 7 in pair:test['test_edge_'+str(sum(k.startswith('test_edge') for k in test)+1)]=e^ball
    test_records=[]
    for name,s in test.items():
        assert len(s.decompose())==1,name
        m=pack(name,s.simplify(.008))
        if name in ['test_fixture','test_rotor']:T=F.T
        else:
            center=np.array(s.bounding_box()).reshape(2,3).mean(axis=0)
            T=Rotation.align_vectors([[0,0,1]],[center/np.linalg.norm(center)])[0].as_matrix()
        v=m.vertices@T.T;v[:,2]-=v[:,2].min();pm=m.copy();pm.vertices=v
        clean_mesh(pm).export(out/'calibration'/f'{name}.stl')
        test_records.append({'name':name,'print_bounds_mm':pm.bounds.tolist()})
    np.savez_compressed(out/'reference'/'assembly_meshes.npz',**packed)
    metadata={'design':'Rotated Redi 80 — spherical core revision v3.1','units':'mm','rotation':data,
        'parameters':{'side':SIDE,'exterior_round_radius':EXTERIOR_ROUND,'protected_inner_radius':PROTECTED_RADIUS,'rail_radius':RAIL_RADIUS,'rail_top_axis_coordinate':17.0,'gap_total':GAP,'core_radius':CORE_R,'shell_inner_radius':INNER_R,
            'core_pad_radius':CORE_PAD,'core_extra_print_flat':False,'core_print_bed_axis':'C01','pilot_diameter':args.pilot,'through_hole_axes':4,
            'screw_bore_diameter':SCREW_BORE_D,'flat_bearing_foot_diameter':2*FOOT_R,
            'flat_bearing_area_mm2':np.pi*(FOOT_R**2-(SCREW_BORE_D/2)**2),
            'washer_seat_radius':POC_SEAT,'access_well_diameter':ACCESS_D,
            'washer_OD_thickness':[WASHER_OD,WASHER_T],
            'nominal_axial_play':AXIAL_PLAY,'screw_length':SCREW_LENGTH,
            'screw_tip_radius':SCREW_TIP,'nominal_engagement':CORE_PAD-SCREW_TIP,
            'assembly_relief_side_clearance':ASSEMBLY_RELIEF_SIDE_CLEARANCE,'segments':192},'parts':records,'calibration_parts':test_records,
        'corner_assembly_relief_volume_mm3':removed,'generation_seconds':time.time()-start}
    (out/'reference'/'design.json').write_text(json.dumps(metadata,indent=2))
    for name in ['mechanism.py','poc_mechanism.py','mechanism_v3.py','exact_assembly_sweep.py','v3_io.py','build_v3.py','chosen_rotation.json','optimize_rotation.py']:
        shutil.copy(HERE/name,out/'source'/name)
    (out/'source'/'requirements.txt').write_text('numpy==2.4.6\nscipy==1.17.1\nmanifold3d==3.5.2\ntrimesh==5.1.0\nmatplotlib==3.11.1\nshapely==2.1.2\nrtree==1.4.1\npillow==12.3.0\n')
    print('DONE',out,'seconds',time.time()-start,flush=True)

if __name__=='__main__': main()
