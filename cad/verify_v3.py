"""Audit saved prototype meshes, hardware access, assembly and turn paths."""
from mechanism_v3 import *
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import argparse,zipfile,xml.etree.ElementTree as ET,time

def check_stand(p,out):
    m=trimesh.load(out/'calibration'/'assembly_stand.stl',force='mesh',process=True)
    a=m.face_adjacency;g=coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(m.faces),len(m.faces))).tocsr()
    count,_=connected_components(g,directed=False)
    mesh_ok=bool(m.is_watertight and m.is_winding_consistent and count==1 and m.volume>0)
    stand=xform(p['stand'],frame(-AXES[0]),AXES[0]*(CORE_PAD+70))
    static=union([p['core']]+[p[f'C{i:02}'] for i in range(2,9)]+[p[f'E{i:02}'] for i in range(1,13)]+[s for n in AXES[1:] for s in hardware(n)])
    raw=(stand^static).volume();withdrawal=0
    for offset in np.r_[np.arange(.005,5.1,.25),np.arange(6,121,2)]:
        withdrawal=max(withdrawal,(stand.translate(AXES[0]*offset)^static).volume())
    row={'file':'calibration/assembly_stand.stl','watertight':bool(m.is_watertight),'connected_components':int(count),'volume_mm3':float(m.volume),'minimum_print_z_mm':float(m.bounds[0,2]),'passed':mesh_ok}
    result={'type':'gravity-supported, integral 2.2 mm peg','initial_contact_overlap_mm3':raw,'withdrawal_maximum_overlap_mm3':withdrawal,'saved_stl':row,'passed':bool(mesh_ok and raw<.01 and withdrawal<1e-5)}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'outputs'/'rotated-redi-80mm-v3')
    ap.add_argument('--stand-only',action='store_true',help='Update only the changed stand check in an existing report')
    args=ap.parse_args();out=args.out;start=time.time();report={};failures=[]
    z=np.load(out/'reference'/'assembly_meshes.npz')
    p={k[:-2]:from_mesh(trimesh.Trimesh(z[k],z[k[:-2]+'_f'],process=False)) for k in z.files if k.endswith('_v')}
    if args.stand_only:
        report=json.loads((out/'reference'/'verification.json').read_text())
        result=check_stand(p,out);report['assembly_stand']=result
        report.pop('assembly_stand_overlap_mm3',None)
        report['saved_stl_checks']=[result['saved_stl'] if row['file']=='calibration/assembly_stand.stl' else row for row in report['saved_stl_checks']]
        report['stand_revision_check_seconds']=time.time()-start
        if not result['passed']:report['failures'].append('revised stand')
        report['passed']=not report['failures']
        (out/'reference'/'verification.json').write_text(json.dumps(report,indent=2))
        print('STAND',result,flush=True)
        return
    checks=[]
    for f in sorted(list((out/'parts').glob('*.stl'))+list((out/'calibration').glob('*.stl'))):
        m=trimesh.load(f,force='mesh',process=True)
        a=m.face_adjacency;g=coo_matrix((np.ones(len(a)),(a[:,0],a[:,1])),shape=(len(m.faces),len(m.faces))).tocsr()
        count,_=connected_components(g,directed=False)
        ok=bool(m.is_watertight and m.is_winding_consistent and count==1 and m.volume>0 and np.isfinite(m.vertices).all())
        checks.append({'file':str(f.relative_to(out)),'watertight':bool(m.is_watertight),'connected_components':int(count),'volume_mm3':float(m.volume),'minimum_print_z_mm':float(m.bounds[0,2]),'passed':ok})
        if not ok:failures.append('mesh '+f.name)
    report['saved_stl_checks']=checks
    print('STL',len(checks),'failures',len(failures),flush=True)
    cs=[p[f'C{i:02}'] for i in range(1,9)];es=[p[f'E{i:02}'] for i in range(1,13)];cr=p['core'];bodies=cs+es
    screws=[];washers=[]
    for n in AXES:
        s,w=hardware(n);screws.append(s);washers.append(w)
    # The nominal screw envelope intentionally penetrates the pilot wall to
    # form threads. Check screw/core engagement separately from body collisions.
    fixed_hardware=union([cr]+screws+washers)
    # Flat bearing faces intentionally contact. Quantized mesh coplanarity can
    # create tiny signed overlap. Record raw values and require that translating
    # the corner just 0.005 mm outward eliminates any core overlap.
    contact=[]
    for c,n in zip(cs,AXES):
        raw=(c^cr).volume();lift=(c.translate(n*.005)^cr).volume()
        contact.append({'raw_core_contact_overlap_mm3':raw,'overlap_after_0p005_mm_lift_mm3':lift})
        if raw>.01 or lift>1e-5:failures.append('bearing contact exceeds numerical tolerance')
    report['flat_bearing_contacts']=contact
    maximum=max((a^b).volume() for a,b in itertools.combinations(bodies,2))
    hardware_overlap=max((b^union(screws+washers)).volume() for b in bodies)
    if maximum>1e-5:failures.append('solved outer overlap')
    if hardware_overlap>1e-5:failures.append('screw or washer overlaps a rotating part')
    report['solved']={'maximum_outer_overlap_mm3':maximum,'maximum_screw_washer_overlap_mm3':hardware_overlap}
    print('solved',report['solved'],'core contact',max(q['raw_core_contact_overlap_mm3'] for q in contact),flush=True)
    turns=[]
    for a,n in enumerate(AXES):
        moving=union([cs[a]]+[e for pair,e in zip(EDGES,es) if a in pair])
        static_outer=union([c for i,c in enumerate(cs) if i!=a]+[e for pair,e in zip(EDGES,es) if a not in pair])
        static=union([static_outer,fixed_hardware]);vmax=0;gap=1;lifted_core=0
        for angle in range(0,121,5):
            rot=Rotation.from_rotvec(n*np.radians(angle)).as_matrix();m=xform(moving,rot)
            vmax=max(vmax,(m^static).volume());gap=min(gap,m.min_gap(static_outer,1))
            lifted_core=max(lifted_core,(xform(cs[a],rot).translate(n*.005)^cr).volume())
        turns.append({'corner':a+1,'samples':25,'maximum_raw_overlap_mm3':vmax,'minimum_outer_gap_mm':gap,'core_overlap_after_0p005_mm_lift':lifted_core})
        if vmax>.01 or lifted_core>1e-5:failures.append('turn '+str(a+1))
        # Independently forbid outer/hardware overlaps; their allowed threshold
        # must not be relaxed to accommodate the intentional core contact.
        for angle in range(0,121,5):
            m=xform(moving,Rotation.from_rotvec(n*np.radians(angle)).as_matrix())
            if (m^union([static_outer]+screws+washers)).volume()>1e-5:failures.append('turn outer or hardware '+str(a+1));break
        print('turn',turns[-1],flush=True)
    report['all_axis_turn_sweeps']=turns
    insertions=[]
    for a,n in enumerate(AXES):
        static=union([b for i,b in enumerate(bodies) if i!=a]+[cr]);vmax=0
        for offset in np.r_[np.arange(.005,20.01,.25),np.arange(21,121,1)]:
            vmax=max(vmax,(cs[a].translate(n*offset)^static).volume())
        insertions.append({'corner':a+1,'maximum_overlap_mm3':vmax})
        if vmax>1e-5:failures.append('corner insertion '+str(a+1))
    report['corner_insertion']=insertions
    edge_insertions=[]
    for k,e in enumerate(es):
        d=AXES[EDGES[k][0]]+AXES[EDGES[k][1]];d/=np.linalg.norm(d)
        static=union([v for j,v in enumerate(es) if j!=k]+[cr]);vmax=0
        for offset in np.r_[np.arange(0,12.01,.5),np.arange(14,121,2)]:vmax=max(vmax,(e.translate(d*offset)^static).volume())
        edge_insertions.append({'edge':k+1,'maximum_overlap_mm3':vmax})
        if vmax>1e-5:failures.append('edge insertion '+str(k+1))
    report['edge_insertion']=edge_insertions
    print('insertion corner max',max(r['maximum_overlap_mm3'] for r in insertions),'edge max',max(r['maximum_overlap_mm3'] for r in edge_insertions),flush=True)
    # Cylindrical 12 mm bit-holder envelope has a conservative flat front at
    # the washer top. It can surround the head while a bit reaches the recess.
    access=[]
    for a,n in enumerate(AXES):
        holder=xform(mf.Manifold.cylinder(120,6,6,192),frame(n),n*SCREW_TOP)
        vmax=(holder^union(bodies)).volume();washer_v=0
        for offset in np.r_[np.arange(0,20.1,1),np.arange(25,121,5)]:
            washer_v=max(washer_v,(washers[a].translate(n*offset)^union(bodies)).volume())
        access.append({'corner':a+1,'holder_diameter_mm':12,'holder_body_overlap_mm3':vmax,'washer_insertion_overlap_mm3':washer_v})
        if vmax>1e-5 or washer_v>1e-5:failures.append('hardware access '+str(a+1))
    report['driver_and_washer_access']=access
    report['assembly_stand']=check_stand(p,out)
    if not report['assembly_stand']['passed']:failures.append('stand')
    retention=[]
    for k,(a,b) in enumerate(EDGES):
        d=AXES[a]+AXES[b];d/=np.linalg.norm(d);hits=[]
        for c in [cs[a],cs[b]]:
            hit=[float(t) for t in np.arange(0,6.01,.1) if (es[k].translate(d*t)^c).volume()>1e-4]
            hits.append(min(hit) if hit else None)
        retention.append({'edge':k+1,'first_radial_obstruction_by_each_corner_mm':hits})
        if None in hits:failures.append('edge retention '+str(k+1))
    report['radial_pullout_retention']=retention
    fixture=p['test_fixture'];testmoving=union([p['test_rotor']]+[p[f'test_edge_{i}'] for i in range(1,4)])
    vmax=0
    for angle in range(0,361,5):
        m=xform(testmoving,Rotation.from_rotvec(AXES[7]*np.radians(angle)).as_matrix())
        vmax=max(vmax,(m^fixture).volume())
    report['one_axis_fixture']={'angle_samples':73,'maximum_contact_overlap_mm3':vmax}
    if vmax>.01:failures.append('fixture motion')
    # Verify positive annular landing area in the actual corner, and a
    # continuous >=2 mm collar around the large washer access at its seat.
    seat_wall=[]
    for a,c in enumerate(cs):
        local=xform(c,frame(AXES[a]).T)
        for zheight in [CORE_PAD+.01,POC_SEAT-.01]:
            target=mf.CrossSection.circle(FOOT_R-.01 if zheight<23 else WASHER_OD/2,192)-mf.CrossSection.circle(SCREW_BORE_D/2+.01,128)
            if (target-local.slice(zheight)).area()>.02:failures.append('incomplete annular bearing or washer seat '+str(a+1))
        collar=mf.Manifold.cylinder(.5,ACCESS_D/2+2,ACCESS_D/2+2,192).translate([0,0,POC_SEAT+.01])-mf.Manifold.cylinder(.6,ACCESS_D/2+.01,ACCESS_D/2+.01,192).translate([0,0,POC_SEAT])
        missing=(collar-local).volume()
        seat_wall.append({'corner':a+1,'missing_volume_from_2_mm_collar_mm3':missing})
        if missing>.01:failures.append('thin washer-well collar '+str(a+1))
    report['bearing_and_washer_support']=seat_wall
    screw_checks=[]
    for length in [20,25]:
        ss=[hardware(n,length=length)[0] for n in AXES]
        collision=max((a^b).volume() for a,b in itertools.combinations(ss,2))
        screw_checks.append({'length_mm':length,'nominal_core_engagement_mm':CORE_PAD-(SCREW_TOP-length),'maximum_screw_pair_overlap_mm3':collision})
        if collision>1e-5:failures.append('screw pair '+str(length))
    report['screw_lengths']=screw_checks
    plates=[]
    for f in sorted((out/'plates').glob('*.3mf')):
        with zipfile.ZipFile(f) as zf:
            root=ET.fromstring(zf.read('3D/3dmodel.model'));ns={'m':root.tag.split('}')[0][1:]}
            objects={o.attrib['id']:o for o in root.findall('m:resources/m:object',ns)};ok=True
            for item in root.findall('m:build/m:item',ns):
                obj=objects[item.attrib['objectid']]
                v=np.array([[float(v.attrib[k]) for k in 'xyz'] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
                T=np.array(list(map(float,item.attrib['transform'].split()))).reshape(4,3);v=v@T[:3]+T[3]
                ok=ok and bool(v.min()>=-1e-4 and v.max()<=256)
            plates.append({'file':f.name,'objects':len(objects),'within_256_mm_volume':ok})
            if not ok:failures.append('plate '+f.name)
    report['print_plates']=plates
    report['limitations']=['Not physically printed or tested for thread grip, turning torque, deformation or wear.',
        'Screw adjustment must leave approximately 0.08–0.15 mm axial freedom; over-tightening clamps the rotating corner.',
        'Perfectly aligned rigid geometry is checked. Wobble and roughness require the physical fixture test.',
        'Direct PLA threads have no independently validated holding load and may loosen with use.',
        'Turn/insertion sampling is backed by the unchanged rotational cut family and explicit axisymmetric inner bearing foot and square retaining rails; sampling alone is not a continuous-motion proof.',
        'The screw envelope assumes a flat-underhead machine screw with head diameter <=6 mm and height <=3 mm; the open well also accommodates larger heads below 13 mm diameter.',
        'Flat contact overlap <=0.01 mm3 is accepted only with separate contact-lift, outer collision and hardware checks; strict threshold elsewhere is 1e-5 mm3.']
    report['failures']=failures;report['passed']=not failures;report['seconds']=time.time()-start
    (out/'reference'/'verification.json').write_text(json.dumps(report,indent=2))
    print('DONE',report['passed'],'seconds',time.time()-start,'failures',failures,flush=True)

if __name__=='__main__':main()
