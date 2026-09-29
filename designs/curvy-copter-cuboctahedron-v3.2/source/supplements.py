"""Extra checks and clear report manifest, not physical-build certification."""
from hardware import *
import hashlib
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def run():
 meta=json.loads((DEST/'manifest.json').read_text());standrec=next(r for r in meta['parts'] if r['family']=='stand');m=trimesh.load(DEST/standrec['file'],force='mesh');T=np.array(standrec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];tool=from_mesh(m)
 cells={r['name']:load(CACHE/'printed'/(r['name']+'.npz')) for r in ROWS};c=load(CACHE/'printed-core.npz');cr=canonical('C');n=np.array(cr['direction']);fixed=union([s for k,s in cells.items() if k!=cr['name']]+[c]);worst=0
 for d in np.r_[np.linspace(0,5,21),np.linspace(6,85,41)]:worst=max(worst,(tool.translate(n*d)^fixed).volume())
 assert worst<.005
 pairs=[hardware(a) for a in AXES];hwmax=max((union(pairs[i])^union(pairs[j])).volume() for i,j in itertools.combinations(range(12),2));assert hwmax<.005
 (DEST/'reports/stand.json').write_text(json.dumps(dict(replaces=cr['name'],axial_withdrawal_mm=85,maximum_collision_mm3=worst),indent=2)+'\n')
 (DEST/'reports/hardware-pairs.json').write_text(json.dumps(dict(pairs=66,maximum_collision_mm3=hwmax),indent=2)+'\n')
 finishing=dict(edge_opening=json.loads((CACHE/'rounding.json').read_text()),radial_rounding_mm=2.,corner_neck_protection=json.loads((CACHE/'corner-neck.json').read_text()),corner_tip_trim=json.loads((CACHE/'corner-tip-trim.json').read_text()),detached_material=[])
 finishing.update(center_radial_outline_rounding=json.loads((CACHE/'flange-rounding.json').read_text()),petal_outer_fillet_reference='Unclipped cutting body at radial stations >= 35 mm; R2 continues through the exterior face.')
 for f in ORBITS:
  for label,path in [('edge opening',CACHE/(f+'-morphology-trim.json')),('radial rounding',CACHE/'ridges-2'/(f+'-tip-trimming.json'))]:
   if path.exists():finishing['detached_material'].append(dict(family=f,operation=label,details=json.loads(path.read_text())))
 (DEST/'reports/finishing.json').write_text(json.dumps(finishing,indent=2)+'\n')
 lines=['# Solved neighbors','','C = screwed center; P = petal; K = floating corner. Every copy in a family is identical. The plate names and painting map use these labels.','','| Piece | Exterior seam neighbors |','|---|---|']
 for row in sorted(ROWS,key=lambda r:r['name']):
  sig=set(row['signature']);near=[r['name'] for r in ROWS if len(sig.symmetric_difference(r['signature']))==1];lines.append('| '+row['name']+' | '+', '.join(sorted(near))+' |')
 lines+=['','| Center | Axis (proportional coordinates) |','|---|---|']
 for r in ROWS:
  if r['family']=='C':lines.append('| '+r['name']+' | '+', '.join(str(int(round(v*np.sqrt(2)))) for v in r['direction'])+' |')
 (DEST/'NEIGHBORS.md').write_text('\n'.join(lines)+'\n')
 summary=json.loads((DEST/'reports/summary.json').read_text());walk=json.loads((DEST/'reports/jumbling-walk.json').read_text());ret=json.loads((DEST/'reports/retention-spherical.json').read_text());rock=json.loads((DEST/'reports/rocking.json').read_text());assert summary['passed'] and walk['passed'] and not any(x['escape_found'] for x in rock['checks'])
 summary.update(physical_status='UNPRINTED REVISION. Print seven-piece retention test first.',finite_sampling_only=True,jumbling_walk_steps=48,jumbling_walk_minimum_petal_obstruction_mm3=min(r['maximum_intersection_mm3'] for r in walk['radial_extraction_probes'] if r['name'].startswith('P')),jumbling_walk_minimum_corner_obstruction_mm3=min(r['maximum_intersection_mm3'] for r in walk['radial_extraction_probes'] if r['name'].startswith('K')),minimum_sampled_anchor_only_petal_obstruction_mm3=min(x['maximum_intersection_mm3'] for x in ret['petal_anchor_only']),minimum_sampled_corner_obstruction_with_displaced_petals_mm3=min(x['maximum_intersection_mm3'] for x in ret['corner_to_displaced_petals']),anchor_only_petal_cases=len(ret['petal_anchor_only']),supported_corner_cases=len(ret['corner_to_displaced_petals']),limited_rocking_searches=len(rock['checks']),hardware_pairs_checked=66,mesh_sha256={r['file']:hashlib.sha256((DEST/r['file']).read_bytes()).hexdigest() for r in meta['parts']},meridian_rho_z_mm=profile(),square_face_spacing_mm=SIZE,body_gap_mm=BODY_GAP,extra_track_clearance_mm=TRACK_EXTRA,rounding_mm={'radial_dihedrals':2.,'centers':.35,'floating':.45},unchanged_interface=dict(core_radius_mm=CORE_R,core_pad_mm=CORE_PAD,foot_plane_mm=FOOT_PLANE,foot_radius_mm=FOOT_R,washer_seat_mm=SEAT,hardware='M3x20 DIN912, 9x1 mm washers, DIN985 M3 nuts'))
 summary.update(mechanism='Spherical-shell shoulders',spherical_radii_mm=[SHOULDER_R,COLLAR_OUTER_R],neck_cone_half_angle_degrees=NECK_ANGLE,assembly_validated=False,insertion_relief_applied=False,extraction_geometry='Only floating feet at radii <= 28.5 mm; outer-body collisions are not credited.',nominal_foot_capture=json.loads((DEST/'reports/nominal-foot-capture.json').read_text()),corner_tip_trim=finishing['corner_tip_trim'])
 summary.update(version=RELEASE_VERSION,physical_status='User confirmed spherical-v3 test prints work with old core. This v3.2 refinement has not yet been printed.',petal_groove_extra_width_mm=PETAL_GROOVE_WIDTH_EXTRA,petal_center_bearing_gap_mm=BODY_GAP+TRACK_EXTRA+PETAL_WALL_EXTRA,corner_petal_bearing_gap_mm=BODY_GAP+TRACK_EXTRA,rounding_mm={'radial_dihedrals':2.,'center_radial_outline_corners':CENTER_FLANGE_END_ROUNDING,'center_original_small_edges':.35,'floating_small_edges':.45},reusable_parts=['core','K floating corners','accepted v3.1 petals'])
 (DEST/'reports/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('SUPPLEMENTS COMPLETE',flush=True)
if __name__=='__main__':run()
