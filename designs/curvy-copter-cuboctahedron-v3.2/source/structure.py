from hardware import *
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def structure():
 meta=json.loads((DEST/'manifest.json').read_text());rec=next(r for r in meta['parts'] if r['family']=='C');m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
 n=np.array(canonical('C')['direction']);F=frame(n);local=m.copy();local.vertices=local.vertices@F
 tri=local.triangles;rho=np.linalg.norm(tri[:,:,:2],axis=2)
 bore=np.max(abs(rho-1.8),axis=1)<.02;well=(np.max(abs(rho-4.8),axis=1)<.02)&(np.min(tri[:,:,2],axis=1)>SEAT-.02)
 seat=np.max(abs(tri[:,:,2]-SEAT),axis=1)<.02
 external=local.submesh([~(bore|well|seat)],append=True)
 t=np.arange(720)*2*np.pi/720;points=np.column_stack([4.8*np.cos(t),4.8*np.sin(t),np.full(720,SEAT-.02)])
 near,dist,idx=trimesh.proximity.closest_point(external,points);minimum=float(dist.min());assert minimum>1.5,('thin center root',minimum)
 checks=dict(center_washer_rim_minimum_external_web_mm=minimum,samples=720,foot_outer_diameter_mm=2*FOOT_R,rotating_bore_diameter_mm=3.6,foot_annular_wall_mm=FOOT_R-1.8,nut_roof_thickness_mm=CORE_PAD-NUT_ROOF,washer_seat_mm=SEAT,screw_tip_axis_coordinate_mm=SEAT+1-20,nylon_ring_exit_axis_coordinate_mm=NUT_ROOF-4,screw_projection_beyond_nut_mm=NUT_ROOF-4-(SEAT+1-20),scope='Geometric dimensions, not force or fatigue ratings.')
 assert checks['screw_projection_beyond_nut_mm']>=1
 (DEST/'reports/structure.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks,flush=True)
if __name__=='__main__':structure()
